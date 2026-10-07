"""
Core Address Standardizer & Entity Resolution Engine.
=====================================================
Standardizes US and International addresses to USPS Publication 28 and ISO standards:
  - Tier 1: Sub-0.015ms Fast-path regex and structured trie parser.
  - Tier 2: Deterministic rule matrix with right-to-left reverse anchor scanning,
            positional directional grammar, rural route mapping, Queens hyphenation,
            and Levenshtein <= 1 closed-vocabulary typo recovery.
  - Tier 3: Statistical CRF fallback (usaddress) with tag post-processing.
  - Two-tier matching keys: suite-level (normalized_address_key) and building-level (building_key).
  - Hybrid collision-free phonetic blocking keys.
  - Commercial formation / registered agent hub detection.
"""

import copy
import unicodedata
import logging
import re
from typing import Optional, Tuple, List, Dict, Any

try:
    import usaddress
except ImportError:
    usaddress = None

from address_standardizer.models import StandardizedAddress, LocalityOnlyStatus
from address_standardizer.confidence import (
    RoutingTier,
    compute_confidence_score,
)
from address_standardizer.audit import get_audit_ledger
from address_standardizer.cache import (
    get_default_cache,
    make_cache_key,
)
from address_standardizer.tables import (
    DIRECTIONALS,
    STREET_SUFFIXES,
    SECONDARY_UNITS,
    US_STATES,
    COUNTRY_MAP,
    CANADIAN_PROVINCES,
    WORD_ORDINALS,
    COMPOUND_ORDINALS,
    ZIP3_TO_STATE,
    GLOBAL_METRO_TO_COUNTRY,
    LANDMARK_CAMPUS_KEYWORDS,
    CATALOGED_COMMERCIAL_HUBS,
)
from address_standardizer._patterns import (
    RE_CLEAN_TOKEN,
    RE_WHITESPACE,
    RE_NON_ALPHANUMERIC,
    RE_NON_DIGITS,
    RE_STATE_ZIP,
    RE_PO_BOX,
    RE_SEC_UNIT,
    RE_PMB,
    RE_QUEENS_BOROUGH,
    RE_URBANIZATION,
    RE_UK_POSTCODE,
    RE_CAN_POSTCODE,
    RE_NUMBERED_STREET,
    RE_GLUED_HASH,
    RE_GLUED_UNIT,
    RE_GLUED_HOUSE_NUM,
    RE_MILITARY_UNIT_BOX,
    RE_RURAL_ROUTE,
    RE_TERMINAL_COUNTRY,
    RE_LEGACY_CORRUPTIONS,
    clean_redundant_street_tail,
    clean_repetitive_cycles,
    parse_intersection_address,
    is_city_noise_in_street1,
    clean_rooftop_address,
    is_invalid_thoroughfare,
    RE_HIGHWAY_CONTRACT,
    RE_ATTACHED_SUFFIX_EXPLICIT_UNIT,
    RE_ATTACHED_SUFFIX_BARE_UNIT,
    RE_SAINT_HYPHEN,
    RE_PRIVATE_MAILBOX,
    RE_HYPHENATED_UNIT,
    RE_COMMA_DOT,
    RE_DIGITS,
    RE_PHYSICAL_STREET_INDICATOR,
    RE_OCCUPANCY_VAL_CLEAN,
    RE_IDENTIFIER_TOKEN,
    RE_INTL_FLAT,
    RE_INTL_SEC_INLINE,
    RE_INTL_SEC_START,
    RE_NUMBER_HYPHEN_NUMBER,
    RE_CARE_OF,
    RE_PR_HIGHWAY,
    FROZEN_DIRECTIONAL_VALUES,
    FROZEN_US_STATE_CODES,
    ROUTE_PREFIXES,
    MULTI_WORD_CITIES,
    STANDALONE_SEC_UNITS,
    get_fuzzy_suffix,
    get_fuzzy_directional,
)
from address_standardizer.phonetics import (
    generate_phonetic_address_key,
)
from address_standardizer.fast_path import fast_path_parse
from address_standardizer.international import (
    CountryGrammarRegistry,
    fold_to_ascii_key,
)

logger = logging.getLogger(__name__)


def num_to_ordinal(n: int) -> str:
    """Converts integer into ordinal representation (1 -> 1ST, 2 -> 2ND, 3 -> 3RD, 4 -> 4TH)."""
    if 11 <= (n % 100) <= 13:
        suffix = 'TH'
    else:
        suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(n % 10, 'TH')
    return f"{n}{suffix}"


def get_state_from_zip3(zip5: Optional[str]) -> Optional[str]:
    """Resolves US state code from first 3 digits of a 5-digit ZIP code."""
    if not zip5 or len(zip5) < 3 or not zip5[:3].isdigit():
        return None
    return ZIP3_TO_STATE.get(zip5[:3])


def _clean_token(t: str) -> str:
    """Strip leading/trailing punctuation and whitespace."""
    return RE_CLEAN_TOKEN.sub("", t.strip())


def normalize_country_code(
    country_raw: Optional[str],
    state_raw: Optional[str] = None,
    postal_raw: Optional[str] = None,
    raw_street: Optional[str] = None,
    city_raw: Optional[str] = None,
) -> str:
    """Resolve country to ISO-3166-1 alpha-3 code, defaulting to USA if state is a US state or CAN if Canadian province."""
    country_cand = ""
    if country_raw:
        c_clean = country_raw.strip().upper()
        c_clean_alphanumeric = RE_NON_ALPHANUMERIC.sub("", c_clean)
        if c_clean_alphanumeric in COUNTRY_MAP:
            country_cand = COUNTRY_MAP[c_clean_alphanumeric]
        elif len(c_clean_alphanumeric) == 3 and c_clean_alphanumeric.isascii() and c_clean_alphanumeric.isalpha():
            country_cand = c_clean_alphanumeric
        else:
            from address_standardizer.international.countries import CountryRegistry

            info = CountryRegistry.get(country_raw)
            if info:
                country_cand = info.alpha3

    # If country is explicitly non-US, return it immediately
    if country_cand and country_cand not in ("USA", "PRI", "GUM", "VIR", "MNP", "ASM", ""):
        return country_cand

    # Check state indicator
    is_valid_us_state = False
    if state_raw:
        s_clean = RE_NON_ALPHANUMERIC.sub("", state_raw.strip().upper())
        if s_clean in CANADIAN_PROVINCES:
            return "CAN"
        if s_clean in US_STATES:
            is_valid_us_state = True

    # If state is explicitly a US state, then country is USA
    if is_valid_us_state:
        return "USA"

    if country_cand in ("PRI", "GUM", "VIR", "MNP", "ASM"):
        return country_cand

    # Cross-Border Foreign Operating Bank Branches / Metadata check:
    # When state is absent or not a US state (e.g. 'US' or empty), or dummy '00000' zip,
    # or raw_street indicates foreign branch, check city against global metros.
    is_foreign_indicator = (
        state_raw in ("US", "USA", "", None)
        or postal_raw in ("00000", "", None)
        or (raw_street and any(ind in raw_street.upper() for ind in ("(FRGN)", "(FOREIGN)", " FRGN", " OVERSEAS")))
    )

    # International metro check: When state is absent or not a US state,
    # check city against global metros to prevent erroneous USA defaulting
    if city_raw:
        c_clean = RE_NON_ALPHANUMERIC.sub(" ", city_raw).strip().upper()
        c_clean = " ".join(c_clean.split())
        candidates = [c_clean]
        c_no_num = re.sub(r"\s+\d+.*$", "", c_clean).strip()
        if c_no_num and c_no_num != c_clean:
            candidates.append(c_no_num)
        c_no_lead = re.sub(r"^\d+\s+", "", c_clean).strip()
        if c_no_lead and c_no_lead != c_clean:
            candidates.append(c_no_lead)
        if "," in city_raw:
            for part in city_raw.split(","):
                p_c = RE_NON_ALPHANUMERIC.sub(" ", part).strip().upper()
                p_c = " ".join(p_c.split())
                if p_c:
                    candidates.append(p_c)

        for cand in candidates:
            if cand in GLOBAL_METRO_TO_COUNTRY:
                if not is_valid_us_state or is_foreign_indicator:
                    return GLOBAL_METRO_TO_COUNTRY[cand]
            cand_unaccent = unicodedata.normalize("NFKD", cand).encode("ASCII", "ignore").decode("utf-8")
            if cand_unaccent in GLOBAL_METRO_TO_COUNTRY:
                if not is_valid_us_state or is_foreign_indicator:
                    return GLOBAL_METRO_TO_COUNTRY[cand_unaccent]

    if postal_raw:
        p_clean = postal_raw.strip().upper()
        if RE_CAN_POSTCODE.match(p_clean):
            return "CAN"
        if RE_UK_POSTCODE.match(p_clean):
            return "GBR"

    # Scan raw single string for international indicators
    if raw_street:
        st_clean = raw_street.upper()
        if "CAYMAN" in st_clean:
            return "CYM"
        if RE_UK_POSTCODE.search(st_clean) or st_clean.endswith(", UK") or st_clean.endswith(" UK") or "UNITED KINGDOM" in st_clean:
            return "GBR"
        if RE_CAN_POSTCODE.search(st_clean) or st_clean.endswith(", CANADA") or st_clean.endswith(" CANADA"):
            return "CAN"
        m_sz = RE_STATE_ZIP.search(st_clean)
        if m_sz and m_sz.group(1).upper() in FROZEN_US_STATE_CODES:
            return "USA"

        # Check if address ends with a US state code/name (or US state before country)
        # BEFORE scanning raw components against COUNTRY_MAP to prevent domestic namesake cities
        # (e.g. Lebanon NH, Mexico ME, Brazil IN, Paris TX, London OH, Berlin CT)
        # from being hijacked by sovereign country names.
        raw_parts = [p.strip() for p in raw_street.split(",") if p.strip()]
        if raw_parts:
            last_clean = RE_NON_ALPHANUMERIC.sub("", raw_parts[-1]).strip().upper()
            if last_clean in ("USA", "US", "UNITED STATES", "UNITED STATES OF AMERICA"):
                if len(raw_parts) >= 2:
                    prev_clean = RE_NON_ALPHANUMERIC.sub("", raw_parts[-2]).strip().upper()
                    if prev_clean in FROZEN_US_STATE_CODES or prev_clean in US_STATES:
                        return "USA"
            elif last_clean in FROZEN_US_STATE_CODES or last_clean in US_STATES:
                return "USA"
            else:
                subwords = raw_parts[-1].split()
                if subwords:
                    sub_last = RE_NON_ALPHANUMERIC.sub("", subwords[-1]).strip().upper()
                    if sub_last in FROZEN_US_STATE_CODES or sub_last in US_STATES:
                        return "USA"

        # Check country map in raw street components (ignoring US state abbreviations and numbers)
        for part in raw_street.split(","):
            p_clean = RE_NON_ALPHANUMERIC.sub(" ", part).strip().upper()
            p_clean = " ".join(p_clean.split())
            p_alphanumeric = RE_NON_ALPHANUMERIC.sub("", part).strip().upper()
            if p_alphanumeric in FROZEN_US_STATE_CODES or p_alphanumeric.isdigit():
                continue
            if p_alphanumeric in STREET_SUFFIXES or p_alphanumeric in STREET_SUFFIXES.values():
                continue
            if p_clean in COUNTRY_MAP and COUNTRY_MAP[p_clean] != "USA":
                return COUNTRY_MAP[p_clean]
            if p_alphanumeric in COUNTRY_MAP and COUNTRY_MAP[p_alphanumeric] != "USA":
                return COUNTRY_MAP[p_alphanumeric]

        raw_words = RE_NON_ALPHANUMERIC.sub(" ", raw_street).strip().upper().split()
        if len(raw_words) >= 2:
            two_w = f"{raw_words[-2]} {raw_words[-1]}"
            if two_w in COUNTRY_MAP and COUNTRY_MAP[two_w] != "USA":
                return COUNTRY_MAP[two_w]
        if raw_words and raw_words[-1] in COUNTRY_MAP and COUNTRY_MAP[raw_words[-1]] != "USA":
            if (
                (len(raw_words[-1]) > 2 or raw_words[-1] not in FROZEN_US_STATE_CODES)
                and not raw_words[-1].isdigit()
                and raw_words[-1] not in STREET_SUFFIXES
                and raw_words[-1] not in STREET_SUFFIXES.values()
            ):
                return COUNTRY_MAP[raw_words[-1]]
        elif len(raw_words) >= 2 and raw_words[-1].isdigit():
            prev_w = raw_words[-2]
            if (
                prev_w in COUNTRY_MAP
                and COUNTRY_MAP[prev_w] != "USA"
                and (len(prev_w) > 2 or prev_w not in FROZEN_US_STATE_CODES)
                and prev_w not in STREET_SUFFIXES
                and prev_w not in STREET_SUFFIXES.values()
            ):
                return COUNTRY_MAP[prev_w]

        # Check global metros in raw street SECOND
        for part in raw_street.split(","):
            p_clean = RE_NON_ALPHANUMERIC.sub(" ", part).strip().upper()
            p_clean = " ".join(p_clean.split())
            if p_clean in GLOBAL_METRO_TO_COUNTRY:
                return GLOBAL_METRO_TO_COUNTRY[p_clean]
            c_unaccent = unicodedata.normalize("NFKD", p_clean).encode("ASCII", "ignore").decode("utf-8")
            if c_unaccent in GLOBAL_METRO_TO_COUNTRY:
                return GLOBAL_METRO_TO_COUNTRY[c_unaccent]
            p_no_num = re.sub(r"\s+\d+.*$", "", p_clean).strip()
            if p_no_num and p_no_num != p_clean:
                if p_no_num in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[p_no_num]
                if p_no_num in COUNTRY_MAP and COUNTRY_MAP[p_no_num] != "USA":
                    return COUNTRY_MAP[p_no_num]
            p_no_lead = re.sub(r"^\d+\s+", "", p_clean).strip()
            if p_no_lead and p_no_lead != p_clean:
                if p_no_lead in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[p_no_lead]
                p_lead_unaccent = unicodedata.normalize("NFKD", p_no_lead).encode("ASCII", "ignore").decode("utf-8")
                if p_lead_unaccent in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[p_lead_unaccent]
                if p_no_lead in COUNTRY_MAP and COUNTRY_MAP[p_no_lead] != "USA":
                    return COUNTRY_MAP[p_no_lead]

    return "USA"


normalize_country = normalize_country_code


def normalize_us_state(state_raw: Optional[str], zip5: Optional[str] = None) -> str:
    """Normalize US state string or full name to standard 2-letter postal code, with ZIP3 auto-healing."""
    res = ""
    if state_raw:
        s_raw = state_raw.strip()
        if s_raw.upper().startswith("USA-"):
            s_raw = s_raw[4:].strip()
        elif s_raw.upper().startswith("US-"):
            s_raw = s_raw[3:].strip()
        s_clean = RE_NON_ALPHANUMERIC.sub("", s_raw.upper())
        res = US_STATES.get(s_clean, s_clean[:2] if len(s_clean) == 2 else s_clean)
    if (not res or res not in FROZEN_US_STATE_CODES) and zip5:
        zip3_st = get_state_from_zip3(zip5)
        if zip3_st:
            res = zip3_st
    return res


def normalize_us_postal_code(postal_raw: Optional[str]) -> Tuple[str, str]:
    """Returns (formatted_postal_code, zip5)."""
    if not postal_raw:
        return "", ""
    digits = RE_NON_DIGITS.sub("", postal_raw.strip())
    if len(digits) == 4:
        digits = f"0{digits}"
    if len(digits) >= 9:
        return f"{digits[:5]}-{digits[5:9]}", digits[:5]
    elif len(digits) >= 5:
        return digits[:5], digits[:5]
    clean = postal_raw.strip().upper()
    return clean, clean[:5]


def is_registered_agent_hub_address(
    street1: str,
    street2: str = "",
    city: str = "",
    state: str = "",
    postal_code: str = "",
    country: str = "USA",
    raw_street: str = ""
) -> bool:
    """Detects whether an address corresponds to a known corporate service or formation hub."""
    from address_standardizer.registry import is_registered_agent_hub_address as _reg_is_hub
    return _reg_is_hub(
        street1=street1,
        street2=street2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        raw_street=raw_street,
    )


def _pre_normalize_address_string(text: str) -> str:
    """Pre-normalizes glued punctuation, symbols, formatting, and repetitive cycles."""
    text = clean_repetitive_cycles(text)
    # Split glued house numbers: '3340PEACHTREE ROAD' -> '3340 PEACHTREE ROAD'
    text = RE_GLUED_HOUSE_NUM.sub(r"\1 \2", text.strip())
    # Split glued hashtags: 'Main St#101' -> 'Main St # 101'
    text = RE_GLUED_HASH.sub(" # ", text)
    # Split glued unit prefixes: 'Apt.4B' -> 'Apt 4B'
    text = RE_GLUED_UNIT.sub(r"\1 ", text)
    # Normalize Saint hyphenation e.g. 'St-Charles' -> 'St Charles', 'Saint-Gaudens' -> 'Saint Gaudens'
    text = RE_SAINT_HYPHEN.sub(r"\1 \2", text)
    # Suffix-attached unit: 'Main St-Ste 200' -> 'Main St STE 200', 'Main St-4B' -> 'Main St APT 4B'
    text = RE_ATTACHED_SUFFIX_EXPLICIT_UNIT.sub(r"\1 \2 \3", text)
    text = RE_ATTACHED_SUFFIX_BARE_UNIT.sub(r"\1 APT \2", text)
    # Normalize Private Mailbox to PMB
    text = RE_PRIVATE_MAILBOX.sub("PMB", text)
    # Normalize STE-400 -> STE 400
    text = RE_HYPHENATED_UNIT.sub(r"\1 \2", text)
    return text


def _standardize_secondary_unit(sec: str) -> str:
    """Standardizes secondary units according to USPS Pub 28, deduplicates repeated tokens, and enforces FL <num>."""
    if not sec:
        return ""
    # Strip any leading STE or SUITE if followed by other unit types (FL, APT, UNIT, DEPT, PH, SUITE, STE) or ordinal floor
    s = re.sub(
        r"^(?:STE|SUITE)\s+(?=(?:\d+(?:ST|ND|RD|TH)\s+)?(?:FL|FLOOR|FLR|APT|APARTMENT|UNIT|DEPT|DEPARTMENT|PH|PENTHOUSE|SUITE|STE)\b)",
        "",
        sec.strip().upper(),
        flags=re.IGNORECASE,
    )
    # Clean separator punctuation between tokens, preserving hyphens in unit identifiers like 4-B or PH-A
    s = re.sub(r"[,;]+", " ", s)
    s = re.sub(r"\s+[\-–—\/]\s+", " ", s)
    raw_tokens = s.split()
    if not raw_tokens:
        return ""

    tokens = []
    for t in raw_tokens:
        if t in ("SUITE", "SUIT"):
            tokens.append("STE")
        elif t in ("FLOOR", "FLR"):
            tokens.append("FL")
        elif t in ("APARTMENT", "APPT"):
            tokens.append("APT")
        else:
            tokens.append(t)

    # Token-level repeat deduplication
    for rlen in range(1, len(tokens) // 2 + 1):
        if len(tokens) % rlen == 0:
            chunk = tokens[:rlen]
            if chunk * (len(tokens) // rlen) == tokens:
                tokens = chunk
                break

    # Floor normalization: Pub 28 strict format FL <num>
    if len(tokens) == 2 and tokens[1] in ("FL", "FLOOR", "FLR"):
        m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[0])
        if m:
            tokens = ["FL", m.group(1)]
    elif len(tokens) == 2 and tokens[0] in ("FL", "FLOOR", "FLR"):
        m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[1])
        if m:
            tokens = ["FL", m.group(1)]
    else:
        new_toks = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and tokens[i+1] in ("FL", "FLOOR", "FLR"):
                is_preceded_by_unit = (i > 0 and tokens[i-1] in ("STE", "APT", "UNIT", "DEPT", "RM", "ROOM", "BLDG", "PH"))
                is_ordinal = bool(re.search(r"(?:ST|ND|RD|TH)$", tokens[i]))
                m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[i])
                if m and (not is_preceded_by_unit or is_ordinal):
                    new_toks.extend(["FL", m.group(1)])
                    i += 2
                    continue
            if tokens[i] in ("FL", "FLOOR", "FLR") and i + 1 < len(tokens):
                m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[i+1])
                if m:
                    new_toks.extend(["FL", m.group(1)])
                    i += 2
                    continue
            new_toks.append(tokens[i])
            i += 1
        tokens = new_toks

    # Final repeat check after normalization
    for rlen in range(1, len(tokens) // 2 + 1):
        if len(tokens) % rlen == 0:
            chunk = tokens[:rlen]
            if chunk * (len(tokens) // rlen) == tokens:
                tokens = chunk
                break

    res = " ".join(tokens)
    # Strip any STE or SUITE prepended to FL, APT, UNIT, DEPT, PH
    res = re.sub(r"^(?:STE|SUITE)\s+(FL|APT|UNIT|DEPT|PH)\b", r"\1", res)
    return res


def _rule_based_us_street_parse(address_str: str, enable_fuzzy: bool = True) -> Tuple[str, str, bool]:
    """
    Tier 2 Deterministic Rule Matrix:
    Standardizes US streets according to USPS Pub 28 using positional grammar,
    Rural Route handling, Queens hyphenation, and typo recovery.
    """
    clean_addr = _pre_normalize_address_string(address_str)

    # Check for Rural Route / Highway Contract
    m_rr = RE_RURAL_ROUTE.search(clean_addr)
    if m_rr:
        prefix_before = clean_addr[:m_rr.start()].strip()
        if not any(c.isdigit() for c in prefix_before):
            rr_num = m_rr.group(2)
            box_id = m_rr.group(3)
            st1_rr = f"RR {rr_num} BOX {box_id}".strip() if box_id else f"RR {rr_num}"
            return st1_rr, "", True

    m_hc = RE_HIGHWAY_CONTRACT.search(clean_addr)
    if m_hc:
        prefix_before = clean_addr[:m_hc.start()].strip()
        if not any(c.isdigit() for c in prefix_before):
            hc_num = m_hc.group(2)
            box_id = m_hc.group(3)
            st1_hc = f"HC {hc_num} BOX {box_id}".strip() if box_id else f"HC {hc_num}"
            return st1_hc, "", True

    # Check for Military Unit Box
    m_mil = RE_MILITARY_UNIT_BOX.search(clean_addr)
    if m_mil and not RE_PHYSICAL_STREET_INDICATOR.search(clean_addr):
        prefix_before = clean_addr[:m_mil.start()].strip()
        if not any(c.isdigit() for c in prefix_before):
            st1_mil = f"{' '.join(m_mil.group(1).upper().split())} {' '.join(m_mil.group(2).upper().split())}"
            return st1_mil, "", True

    # Check for PO Box
    m_po = RE_PO_BOX.search(clean_addr)
    if m_po:
        pob_num = m_po.group(1).upper()
        rem = clean_addr[:m_po.start()] + clean_addr[m_po.end():]
        rem = rem.strip(" ,.-")
        if rem:
            st1_sub, sec_sub, _ = _rule_based_us_street_parse(rem)
            sec_out = f"{sec_sub} PO BOX {pob_num}".strip() if sec_sub else f"PO BOX {pob_num}"
            return (st1_sub or f"PO BOX {pob_num}"), (sec_out if st1_sub else sec_sub), True
        return f"PO BOX {pob_num}", "", True

    # PMB / Private Mailbox extraction
    sec_unit = ""
    m_pmb = RE_PMB.search(clean_addr)
    if m_pmb:
        sec_unit = f"PMB {m_pmb.group(1).upper()}"
        clean_addr = clean_addr[:m_pmb.start()] + clean_addr[m_pmb.end():]

    # Secondary unit extraction (multi-tier support)
    sec_parts = []
    matches = list(RE_SEC_UNIT.finditer(clean_addr))
    if matches:
        for m_sec in matches:
            if m_sec.group(1):
                sec_type = SECONDARY_UNITS.get(m_sec.group(1).upper(), m_sec.group(1).upper())
                sec_val = m_sec.group(2).lstrip("#-").upper()
                sec_parts.append(f"{sec_type} {sec_val}")
            elif m_sec.group(3):
                sec_parts.append(f"STE {m_sec.group(3).lstrip('#-').upper()}")
            elif m_sec.group(4):
                sec_type = SECONDARY_UNITS.get(m_sec.group(4).upper(), m_sec.group(4).upper())
                sec_val = m_sec.group(5).lstrip("#-").upper() if m_sec.group(5) else ""
                sec_parts.append(f"{sec_type} {sec_val}".strip())
        clean_addr = RE_SEC_UNIT.sub(" ", clean_addr).strip()
    if sec_parts:
        extracted_sec = " ".join(sec_parts).strip()
        sec_unit = f"{sec_unit} {extracted_sec}".strip() if sec_unit else extracted_sec
    if sec_unit:
        sec_unit = _standardize_secondary_unit(sec_unit)

    clean_addr = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", clean_addr)).strip().upper()
    if not clean_addr:
        return "", sec_unit, bool(sec_unit)

    tokens = clean_addr.split()

    # Determine House Number vs Words
    house_num_tokens = []
    i = 0
    # Check for fractional house number: "100 1/2 Main St"
    if len(tokens) > 1 and tokens[0].isdigit() and tokens[1] in ("1/2", "1/4", "3/4"):
        house_num_tokens = [tokens[0], tokens[1]]
        i = 2
    # Queens hyphenated or address range: "123-45 82nd Ave" or "100-102 Main St"
    elif RE_QUEENS_BOROUGH.match(tokens[0]) or RE_NUMBER_HYPHEN_NUMBER.match(tokens[0]):
        house_num_tokens = [tokens[0]]
        i = 1
    elif any(c.isdigit() for c in tokens[0]):
        house_num_tokens = [tokens[0]]
        i = 1

    rem_tokens = tokens[i:]
    norm_tokens = list(house_num_tokens)

    # Positional Directional Grammar:
    # If remaining tokens (excluding house number) is [DIRECTIONAL, SUFFIX] e.g. ['SOUTH', 'ST']
    # 'SOUTH' is the street name itself, NOT a pre-directional!
    is_named_directional = False
    if len(rem_tokens) == 2:
        tok0 = rem_tokens[0]
        tok1 = rem_tokens[1]
        f_suf = get_fuzzy_suffix(tok1)
        if (tok0 in DIRECTIONALS or tok0 in FROZEN_DIRECTIONAL_VALUES) and (tok1 in STREET_SUFFIXES or f_suf):
            is_named_directional = True

    # Compound directional street name e.g. ['NORTH', 'EAST', 'ST']
    is_compound_directional = False
    if len(rem_tokens) == 3:
        comp_dir = f"{rem_tokens[0]} {rem_tokens[1]}"
        tok2 = rem_tokens[2]
        f_suf = get_fuzzy_suffix(tok2)
        if comp_dir in ("NORTH EAST", "NORTH WEST", "SOUTH EAST", "SOUTH WEST") and (tok2 in STREET_SUFFIXES or f_suf):
            is_compound_directional = True

    j = 0
    while j < len(rem_tokens):
        t = rem_tokens[j]

        # Named directional bypass: preserve full word
        if is_named_directional and j == 0:
            norm_tokens.append(t)
            j += 1
            continue

        if is_compound_directional and j == 0:
            norm_tokens.append(t)
            norm_tokens.append(rem_tokens[1])
            j += 2
            continue

        # Check for 2-token compound ordinals
        if j + 1 < len(rem_tokens):
            compound_candidate = f"{t} {rem_tokens[j+1]}"
            if compound_candidate in COMPOUND_ORDINALS:
                norm_tokens.append(COMPOUND_ORDINALS[compound_candidate])
                j += 2
                continue

        if t in COMPOUND_ORDINALS:
            norm_tokens.append(COMPOUND_ORDINALS[t])
        elif t in WORD_ORDINALS:
            norm_tokens.append(WORD_ORDINALS[t])
        elif t in DIRECTIONALS:
            norm_tokens.append(DIRECTIONALS[t])
        elif t in STREET_SUFFIXES:
            norm_tokens.append(STREET_SUFFIXES[t])
        elif norm_tokens and norm_tokens[-1] in ("&", "AND", "/", "-", "TO"):
            norm_tokens.append(t)
        elif t.isdigit() and 1 <= int(t) <= 999:
            # Check route prefix exclusion
            prev = norm_tokens[-1] if norm_tokens else ""
            prev2 = f"{norm_tokens[-2]} {prev}" if len(norm_tokens) >= 2 else ""
            if prev not in ROUTE_PREFIXES and prev2 not in ROUTE_PREFIXES and j + 1 < len(rem_tokens) and (rem_tokens[j+1] in STREET_SUFFIXES or get_fuzzy_suffix(rem_tokens[j+1])):
                norm_tokens.append(num_to_ordinal(int(t)))
            else:
                norm_tokens.append(t)
        else:
            m_ord = RE_NUMBERED_STREET.match(t)
            is_suffix_pos = (len(rem_tokens) > 1 and j == len(rem_tokens) - 1) or (
                len(rem_tokens) > 2 and j == len(rem_tokens) - 2 and (rem_tokens[-1] in DIRECTIONALS or rem_tokens[-1] in FROZEN_DIRECTIONAL_VALUES)
            )
            is_dir_pos = (j == 0 and len(rem_tokens) > 2) or (j == len(rem_tokens) - 1)

            f_suf = (get_fuzzy_suffix(t) if is_suffix_pos else None) if enable_fuzzy else None
            f_dir = (get_fuzzy_directional(t) if is_dir_pos else None) if enable_fuzzy else None

            if m_ord:
                norm_tokens.append(num_to_ordinal(int(m_ord.group(1))))
            elif f_suf:
                norm_tokens.append(f_suf)
            elif f_dir:
                norm_tokens.append(f_dir)
            elif enable_fuzzy:
                from address_standardizer.fuzzy import heal_street_name
                h_name = heal_street_name(t)
                norm_tokens.append(h_name if h_name else t)
            else:
                norm_tokens.append(t)
        j += 1

    st1 = " ".join(norm_tokens).strip()
    st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
    sec_unit = _standardize_secondary_unit(sec_unit)
    return st1, sec_unit, bool(st1)


def _parse_us_street_tokens(address_str: str, enable_fuzzy: bool = True, city_raw: str = "") -> Tuple[str, str, bool, str, str, str]:
    """Parse address string using usaddress with rule-based fallback and USPS Pub 28 mapping."""
    clean_input = _pre_normalize_address_string(address_str)

    # Check for Puerto Rico Urbanization prefix
    urb_prefix = ""
    m_urb = RE_URBANIZATION.search(clean_input)
    if m_urb:
        urb_prefix = f"URB {m_urb.group(1).strip().upper()}"
        clean_input = clean_input[:m_urb.start()] + clean_input[m_urb.end():]

    # Check for Rural Route in single string before usaddress
    m_rr = RE_RURAL_ROUTE.search(clean_input)
    if m_rr and not RE_PHYSICAL_STREET_INDICATOR.search(clean_input):
        prefix_before = clean_input[:m_rr.start()].strip()
        if not any(c.isdigit() for c in prefix_before):
            rr_num = m_rr.group(2)
            box_id = m_rr.group(3)
            st1_rr = f"RR {rr_num} BOX {box_id}".strip() if box_id else f"RR {rr_num}"
            # Extract city state zip
            m_sz = RE_STATE_ZIP.search(clean_input.upper())
            p_st = m_sz.group(1) if m_sz else ""
            p_zp = m_sz.group(2) if m_sz else ""
            p_city = ""
            if m_sz:
                before_sz = clean_input[:m_sz.start()].rstrip(" ,")
                after_rr = before_sz[m_rr.end():].strip(" ,")
                p_city = after_rr
            return st1_rr, "", True, p_city, p_st, p_zp

    m_hc = RE_HIGHWAY_CONTRACT.search(clean_input)
    if m_hc and not RE_PHYSICAL_STREET_INDICATOR.search(clean_input):
        prefix_before = clean_input[:m_hc.start()].strip()
        if not any(c.isdigit() for c in prefix_before):
            hc_num = m_hc.group(2)
            box_id = m_hc.group(3)
            st1_hc = f"HC {hc_num} BOX {box_id}".strip() if box_id else f"HC {hc_num}"
            m_sz = RE_STATE_ZIP.search(clean_input.upper())
            p_st = m_sz.group(1) if m_sz else ""
            p_zp = m_sz.group(2) if m_sz else ""
            p_city = ""
            if m_sz:
                before_sz = clean_input[:m_sz.start()].rstrip(" ,")
                after_hc = before_sz[m_hc.end():].strip(" ,")
                p_city = after_hc
            return st1_hc, "", True, p_city, p_st, p_zp

    # Check for Military Unit Box
    m_mil = RE_MILITARY_UNIT_BOX.search(clean_input)
    if m_mil and not RE_PHYSICAL_STREET_INDICATOR.search(clean_input):
        prefix_before = clean_input[:m_mil.start()].strip()
        if not any(c.isdigit() for c in prefix_before):
            st1_mil = f"{' '.join(m_mil.group(1).upper().split())} {' '.join(m_mil.group(2).upper().split())}"
            m_sz = RE_STATE_ZIP.search(clean_input.upper())
            p_st = m_sz.group(1) if m_sz else ""
            p_zp = m_sz.group(2) if m_sz else ""
            p_city = ""
            if m_sz:
                before_sz = clean_input[:m_sz.start()].rstrip(" ,")
                after_mil = before_sz[m_mil.end():].strip(" ,")
                p_city = after_mil
            return st1_mil, "", True, p_city, p_st, p_zp

    p_city = ""
    p_st = ""
    p_zp = ""
    m_sz = RE_STATE_ZIP.search(clean_input.upper())
    if m_sz:
        p_st = m_sz.group(1)
        p_zp = m_sz.group(2)
        before_sz = clean_input[:m_sz.start()].rstrip(" ,")
        if "," in before_sz:
            st_part, city_cand = before_sz.rsplit(",", 1)
            p_city = city_cand.strip()
            clean_input = st_part.strip()
        else:
            tokens_raw = before_sz.split()
            tokens_upper = before_sz.upper().split()
            for num_words in (4, 3, 2):
                if len(tokens_upper) > num_words:
                    cand_city = " ".join(tokens_upper[-num_words:])
                    if cand_city in MULTI_WORD_CITIES:
                        p_city = " ".join(tokens_raw[-num_words:])
                        clean_input = " ".join(tokens_raw[:-num_words])
                        break

    # Execute CRF parser
    if usaddress is not None:
        try:
            parsed = usaddress.parse(clean_input)
        except Exception:
            parsed = None
    else:
        parsed = None

    if parsed is None:
        st_input = clean_input
        if not p_city and m_sz:
            before_sz = clean_input[:m_sz.start()].rstrip(" ,")
            if not RE_DIGITS.search(before_sz):
                st_input = ""
                p_city = before_sz.strip()
            else:
                # Right-to-Left Reverse Anchor Parsing
                split_found = False
                m_po = RE_PO_BOX.search(before_sz)
                if m_po:
                    end_idx = m_po.end()
                    st_cand = before_sz[:end_idx].strip()
                    rem_cand = before_sz[end_idx:].strip()
                    if rem_cand:
                        st_input = st_cand
                        p_city = rem_cand
                        split_found = True

                if not split_found:
                    tokens = before_sz.split()
                    for k in range(1, len(tokens)):
                        t_clean = RE_NON_ALPHANUMERIC.sub("", tokens[k]).upper()
                        if t_clean in STREET_SUFFIXES:
                            curr = k
                            if curr + 1 < len(tokens):
                                next_clean = RE_NON_ALPHANUMERIC.sub("", tokens[curr + 1]).upper()
                                if next_clean in DIRECTIONALS:
                                    curr += 1
                            if curr + 1 < len(tokens):
                                sec_cand = RE_NON_ALPHANUMERIC.sub("", tokens[curr + 1]).upper()
                                if sec_cand in SECONDARY_UNITS:
                                    curr += 1
                                    if curr + 1 < len(tokens):
                                        val_cand = RE_OCCUPANCY_VAL_CLEAN.sub("", tokens[curr + 1]).upper()
                                        if val_cand:
                                            curr += 1
                            if curr + 1 < len(tokens):
                                st_input = " ".join(tokens[:curr+1])
                                p_city = " ".join(tokens[curr+1:])
                                split_found = True
                            break

                if not split_found:
                    st_input = before_sz.strip()

        rb_st1, rb_st2, ok = _rule_based_us_street_parse(st_input, enable_fuzzy=enable_fuzzy)
        if urb_prefix:
            rb_st1 = f"{urb_prefix} {rb_st1}".strip()
        rb_st1 = re.sub(r"[\s,.\-#;:]+$", "", rb_st1).strip()
        rb_st2 = _standardize_secondary_unit(rb_st2)
        return rb_st1, rb_st2, ok, p_city, p_st, p_zp

    # Process CRF tags
    street_parts: List[str] = []
    sec_parts: List[str] = []
    building_parts: List[str] = []
    city_parts: List[str] = []
    state_parts: List[str] = []
    zip_parts: List[str] = []
    rr_parts: List[str] = []

    # Check if parsed contains any StreetName tag
    has_street_name = any(lbl == "StreetName" for _, lbl in parsed)

    i = 0
    while i < len(parsed):
        token, label = parsed[i]
        clean = _clean_token(token).upper()
        if not clean:
            i += 1
            continue

        if label in ("AddressNumber", "AddressNumberPrefix", "AddressNumberSuffix"):
            street_parts.append(clean)
        elif label in ("StreetNamePreDirectional", "StreetNamePostDirectional"):
            # Positional grammar: if no StreetName exists, this directional IS the street name!
            if not has_street_name and len(street_parts) >= 1:
                street_parts.append(clean)
            else:
                street_parts.append(DIRECTIONALS.get(clean, clean))
        elif label in ("StreetNamePostType", "StreetNamePreType"):
            if clean == "ROUTE" and street_parts and street_parts[-1] == "STATE":
                norm_suf = "ROUTE"
            else:
                norm_suf = STREET_SUFFIXES.get(clean, get_fuzzy_suffix(clean) or clean)
            street_parts.append(norm_suf)
        elif label == "StreetName":
            # Compound directional check: NORTH EAST, NORTH WEST, SOUTH EAST, SOUTH WEST
            if clean in ("NORTH", "SOUTH", "EAST", "WEST") and street_parts and street_parts[-1] in ("N", "S", "E", "W"):
                if i + 1 < len(parsed) and parsed[i+1][1] in ("StreetNamePostType", "StreetNamePreType"):
                    dir_unabbrev = {"N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST"}
                    street_parts[-1] = dir_unabbrev.get(street_parts[-1], street_parts[-1])
                    street_parts.append(clean)
                    i += 1
                    continue

            # Check for 2-token compound ordinal (e.g. Twenty First -> 21ST)
            if i + 1 < len(parsed):
                next_tok, next_lbl = parsed[i + 1]
                next_clean = _clean_token(next_tok).upper()
                if next_lbl == "StreetName" and f"{clean} {next_clean}" in COMPOUND_ORDINALS:
                    street_parts.append(COMPOUND_ORDINALS[f"{clean} {next_clean}"])
                    i += 2
                    continue
            if clean in COMPOUND_ORDINALS:
                street_parts.append(COMPOUND_ORDINALS[clean])
            elif clean in WORD_ORDINALS:
                street_parts.append(WORD_ORDINALS[clean])
            elif street_parts and street_parts[-1] in ("&", "AND", "/", "-", "TO"):
                street_parts.append(clean)
            elif clean.isdigit() and 1 <= int(clean) <= 999:
                prev = street_parts[-1] if street_parts else ""
                prev2 = f"{street_parts[-2]} {prev}" if len(street_parts) >= 2 else ""
                if prev not in ROUTE_PREFIXES and prev2 not in ROUTE_PREFIXES:
                    street_parts.append(num_to_ordinal(int(clean)))
                else:
                    street_parts.append(clean)
            else:
                # Check for typo in directional or suffix
                f_dir = get_fuzzy_directional(clean) if enable_fuzzy else None
                f_suf = get_fuzzy_suffix(clean) if enable_fuzzy else None
                m_ord = RE_NUMBERED_STREET.match(clean)
                if m_ord and 1 <= int(m_ord.group(1)) <= 999:
                    street_parts.append(num_to_ordinal(int(m_ord.group(1))))
                elif m_ord:
                    street_parts.append(clean)
                elif f_dir and len(street_parts) == 1 and i + 1 < len(parsed) and parsed[i+1][1] == "StreetName":
                    street_parts.append(f_dir)
                elif f_suf and len(street_parts) >= 2 and (i == len(parsed) - 1 or (i == len(parsed) - 2 and parsed[i+1][1] in ("StateName", "ZipCode"))):
                    street_parts.append(f_suf)
                elif enable_fuzzy:
                    from address_standardizer.fuzzy import heal_street_name
                    h_name = heal_street_name(clean)
                    street_parts.append(h_name if h_name else clean)
                else:
                    street_parts.append(clean)
        elif label == "OccupancyType":
            sec_parts.append(SECONDARY_UNITS.get(clean, clean))
        elif label in ("OccupancyIdentifier", "SubaddressIdentifier"):
            clean_id = clean.lstrip("#-").strip()
            if clean_id:
                SPANISH_PREFIX_THOROUGHFARES = {"CALLE", "AVENIDA", "CARR", "RUTA", "CAMINO", "PASEO", "CALZADA", "CARRETERA"}
                if street_parts and street_parts[-1].upper() in SPANISH_PREFIX_THOROUGHFARES:
                    street_parts.append(clean_id)
                elif clean_id in SECONDARY_UNITS:
                    sec_parts.append(SECONDARY_UNITS[clean_id])
                else:
                    starts_with_unit_prefix = any(
                        clean_id == u or clean_id.startswith(f"{u} ") or clean_id.startswith(f"{u}-")
                        for u in ("FL", "APT", "UNIT", "DEPT", "PH", "SUITE", "STE")
                    )
                    if not sec_parts and not starts_with_unit_prefix:
                        sec_parts.append("STE")
                    sec_parts.append(clean_id)
        elif label == "SubaddressType":
            sec_parts.append(SECONDARY_UNITS.get(clean, clean))
        elif label == "BuildingName":
            building_parts.append(clean)
        elif label in ("USPSBoxGroupType", "USPSBoxGroupID"):
            rr_parts.append(clean)
        elif label in ("USPSBoxType", "USPSBoxID"):
            if rr_parts:
                rr_parts.append(clean)
            else:
                sec_parts.append(clean)
        elif label == "PlaceName":
            if re.match(r"^PH-[A-Z0-9]+$", clean):
                sec_parts.append(clean)
            elif clean in STANDALONE_SEC_UNITS:
                sec_type = SECONDARY_UNITS.get(clean, clean)
                if i + 1 < len(parsed):
                    next_tok, next_lbl = parsed[i + 1]
                    next_clean = _clean_token(next_tok).upper()
                    if next_lbl in ("OccupancyIdentifier", "SubaddressIdentifier") or RE_IDENTIFIER_TOKEN.match(next_clean):
                        sec_parts.append(f"{sec_type} {next_clean}")
                        i += 2
                        continue
                sec_parts.append(sec_type)
            elif clean in ("ST", "SAINT") and i + 1 < len(parsed):
                next_tok, next_lbl = parsed[i + 1]
                next_clean = _clean_token(next_tok).upper()
                norm_c_raw = RE_NON_ALPHANUMERIC.sub("", city_raw).upper() if city_raw else ""
                if (
                    (city_raw and not norm_c_raw.startswith("ST") and not norm_c_raw.startswith("SAINT"))
                    or (not has_street_name and len(street_parts) <= 2)
                ):
                    street_parts.append(clean)
                    street_parts.append(next_clean)
                    i += 2
                    continue
                else:
                    city_parts.append(clean)
            else:
                city_parts.append(clean)
        elif label == "StateName":
            state_parts.append(clean)
        elif label == "ZipCode":
            zip_parts.append(clean)
        elif label in ("CountryName", "Recipient", "NotAddress"):
            i += 1
            continue
        elif label == "LandmarkName":
            # If preceding PlaceName/StateName or no street number present, it is a city prefix like 'LA' in 'LA JOLLA'
            if i + 1 < len(parsed) and parsed[i + 1][1] in ("PlaceName", "StateName", "LandmarkName"):
                city_parts.append(clean)
            elif not any(lbl == "AddressNumber" for _, lbl in parsed):
                city_parts.append(clean)
            else:
                building_parts.append(clean)
        else:
            street_parts.append(clean)
        i += 1

    # Route Rural Routes to street_parts if no other physical street
    if rr_parts and not street_parts:
        street_parts = rr_parts
    elif rr_parts and street_parts:
        sec_parts = rr_parts + sec_parts

    clean_st = " ".join(state_parts)
    if clean_st:
        is_valid_state = (clean_st in US_STATES or clean_st in US_STATES.values() or clean_st in CANADIAN_PROVINCES)
        if not is_valid_state:
            # Invalid state tag from CRF (e.g. "FLOOR", "SUITE", or stray words)
            cand_sec = f"{clean_st} {' '.join(zip_parts)}".strip()
            std_sec = _standardize_secondary_unit(cand_sec)
            if any(std_sec.startswith(u) for u in ("FL ", "STE ", "APT ", "UNIT ", "DEPT ", "RM ", "BLDG ")):
                sec_parts.append(std_sec)
                zip_parts = []
                state_parts = []
            elif len(state_parts) == 1 and state_parts[0] in STREET_SUFFIXES and state_parts[0] not in FROZEN_US_STATE_CODES:
                street_parts.append(STREET_SUFFIXES[state_parts[0]])
                state_parts = []
            elif len(state_parts) > 1 and state_parts[-1] in FROZEN_US_STATE_CODES:
                city_parts = state_parts[:-1] + city_parts
                state_parts = [state_parts[-1]]
            elif clean_st.upper().replace(".", "") in (
                "LP", "LLC", "INC", "CORP", "LTD", "CO", "PLLC", "PC", "SA", "AG",
                "NV", "BV", "GMBH", "SGIIC", "SL", "PLC", "BO", "BARRIO", "SEC", "SECTOR"
            ):
                state_parts = []
            else:
                street_parts.extend(state_parts)
                state_parts = []

    # If city_raw was explicitly provided, and street_parts has no thoroughfare/street name
    # (e.g. empty or only Roman numerals / bare single identifiers like "LIGHTON PLAZA II" where
    # "LIGHTON PLAZA" was tagged as PlaceName and "II" as street/state), reassociate city_parts
    if city_raw and city_parts:
        city_raw_clean = re.sub(r"[^\w]", "", city_raw.upper())
        cand_city = re.sub(r"[^\w]", "", " ".join(city_parts).upper())
        if city_raw_clean and cand_city and cand_city != city_raw_clean:
            has_addr_num = any(p.isdigit() or re.match(r"^\d+", p) for p in street_parts)
            has_thoroughfare = any(p in STREET_SUFFIXES or p in STREET_SUFFIXES.values() for p in street_parts)
            if has_addr_num and has_thoroughfare:
                is_continuation_only = False
            else:
                is_continuation_only = (not street_parts) or all(
                    p in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
                    or p in STREET_SUFFIXES
                    or p in STREET_SUFFIXES.values()
                    or p.isdigit()
                    or len(p) == 1
                    for p in street_parts
                )
            has_premise_indicator = any(
                p.upper() in LANDMARK_CAMPUS_KEYWORDS
                or p.upper() in STREET_SUFFIXES
                or p.upper() in ("CITY", "PARK", "PLACE", "TERRACE", "ROW", "MEWS", "SQUARE",
                                 "CALLE", "AVENIDA", "AVE", "CAMINO", "PASEO", "CARRETERA", "CARR", "RUTA")
                for p in city_parts
            )
            if is_continuation_only and has_premise_indicator:
                street_parts = city_parts + street_parts
                city_parts = []

    st1 = " ".join(street_parts).strip()
    st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
    if is_invalid_thoroughfare(st1):
        if st1:
            sec_parts.append(st1)
            st1 = ""
    st2 = _standardize_secondary_unit(" ".join(sec_parts).strip())
    if not p_city or not p_city.strip():
        p_city = " ".join(city_parts).strip()
    if not p_st or not p_st.strip():
        p_state = " ".join(state_parts).strip()
    else:
        p_state = p_st
    if not p_zp or not p_zp.strip():
        p_zip = " ".join(zip_parts).strip()
    else:
        p_zip = p_zp

    # Prepend Puerto Rico urbanization if present
    if urb_prefix:
        st1 = f"{urb_prefix} {st1}".strip() if st1 else urb_prefix

    # If street_parts was empty but building_parts exists (e.g. "One Financial Plaza")
    if not st1 and building_parts:
        st1 = " ".join(building_parts).strip()
    elif st1 and building_parts:
        b_name = " ".join(building_parts).strip()
        st2 = f"{b_name} {st2}".strip() if st2 else b_name

    # Bare commercial premise followed by secondary units or cataloged commercial hubs
    if not st1 and st2 and city_parts:
        st1 = " ".join(city_parts).strip()
        city_parts = []
        if not city_raw and not (p_st or p_zp):
            p_city = ""
    elif not st1 and city_parts and " ".join(city_parts).upper() in CATALOGED_COMMERCIAL_HUBS:
        st1 = " ".join(city_parts).strip()
        city_parts = []
        if not city_raw and not (p_st or p_zp):
            p_city = ""
    elif city_parts:
        cand_city = re.sub(r"[^\w]", "", " ".join(city_parts).upper())
        prov_city = re.sub(r"[^\w]", "", (city_raw or p_city or "").upper())
        SPANISH_THOROUGHFARES = {"CALLE", "AVENIDA", "CARR", "PASEO", "CAMINO", "CALZADA", "CARRETERA", "RUTA", "AVE"}
        st1_words = [
            w for w in st1.split()
            if w.upper() not in STREET_SUFFIXES
            and w.upper() not in STREET_SUFFIXES.values()
            and w.upper() not in SPANISH_THOROUGHFARES
            and not w.isdigit()
        ]
        if (not st1 or not st1_words) and (not prov_city or (cand_city and cand_city != prov_city)):
            if st1:
                st1 = f"{st1} {' '.join(city_parts)}".strip()
            else:
                st1 = " ".join(city_parts).strip()
            city_parts = []
            if not city_raw and not (p_st or p_zp):
                p_city = ""

    st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
    st2 = _standardize_secondary_unit(st2)

    # Fallback to rule-based parser if st1 is empty
    # Handles commercial campuses, business parks, landmark premises, or Recipient-tagged tokens
    # e.g., "Blue Bell Executive Campus, Suite 200", "Devonshire, Floor 10", "Two Lincoln Centre"
    if not st1:
        if not (p_city or p_state or p_zip):
            # No municipality/state/zip in address_str; address_str is purely a street/premise candidate
            rb_st1, rb_st2, ok = _rule_based_us_street_parse(clean_input, enable_fuzzy=enable_fuzzy)
            if rb_st1:
                st1 = rb_st1
                if not st2 and rb_st2:
                    st2 = rb_st2
        elif clean_input:
            # address_str contained city/state/zip, but clean_input remains
            # Check if clean_input contains landmark campus keywords or commercial hubs and is not just the city name
            clean_words = set(re.findall(r"\b[A-Z0-9]+\b", clean_input.upper()))
            norm_pc = re.sub(r"[^A-Z0-9]", "", p_city.upper()) if p_city else ""
            norm_ci = re.sub(r"[^A-Z0-9]", "", clean_input.upper())
            is_hub = (
                bool(clean_words & LANDMARK_CAMPUS_KEYWORDS)
                or clean_input.upper().strip() in CATALOGED_COMMERCIAL_HUBS
                or any(hub in clean_input.upper() for hub in CATALOGED_COMMERCIAL_HUBS)
            )
            if is_hub and norm_ci != norm_pc:
                rb_st1, rb_st2, ok = _rule_based_us_street_parse(clean_input, enable_fuzzy=enable_fuzzy)
                if rb_st1:
                    st1 = rb_st1
                    if not st2 and rb_st2:
                        st2 = rb_st2

    if st1 and st2 and re.sub(r"[^\w]", "", st1.upper()) == re.sub(r"[^\w]", "", st2.upper()):
        st2 = ""

    # Ultimate fallback to rule-based parser if empty
    if not st1 and not st2 and not (p_city or p_state or p_zip):
        rb_st1, rb_st2, ok = _rule_based_us_street_parse(address_str, enable_fuzzy=enable_fuzzy)
        return rb_st1, rb_st2, ok, p_city, p_state, p_zip

    return st1, st2, True, p_city, p_state, p_zip


def _parse_us_address_components(street1_raw: str, street2_raw: str = "", enable_fuzzy: bool = True, city_raw: str = "") -> Tuple[str, str, bool, str, str, str]:
    """Parses US address lines and returns (st1, st2, ok, p_city, p_state, p_zip)."""
    s1_clean = (street1_raw or "").strip()
    s2_clean = (street2_raw or "").strip()
    if city_raw:
        s1_clean = clean_redundant_street_tail(s1_clean, city=city_raw)
        if s2_clean:
            s2_clean = clean_redundant_street_tail(s2_clean, city=city_raw)

    # Check if street1 has physical street and street2 has PO Box (Dual-Address line)
    m_s1_po = RE_PO_BOX.search(s1_clean)
    m_s2_po = RE_PO_BOX.search(s2_clean)

    if m_s2_po and not m_s1_po:
        # Street1 has physical street, Street2 has PO Box
        st1, st2, ok, p_city, p_state, p_zip = _parse_us_street_tokens(s1_clean, enable_fuzzy=enable_fuzzy, city_raw=city_raw)
        po_box_str = f"PO BOX {m_s2_po.group(1).upper()}"
        combined_st2 = f"{st2} {po_box_str}".strip() if st2 else po_box_str
        combined_st2 = _standardize_secondary_unit(combined_st2)
        st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
        return st1, combined_st2, True, p_city, p_state, p_zip

    # Puerto Rico Highway Mile/Kilometer Markers (e.g. "PR #2 KM 82 HM. 2", "PR-2 KM 82.2", "CARR 167 KM 15")
    m_pr_hwy = RE_PR_HIGHWAY.match(s1_clean)
    if m_pr_hwy:
        hwy = m_pr_hwy.group(1).upper()
        km = m_pr_hwy.group(2).upper()
        hm = m_pr_hwy.group(3) or ""
        rest = (m_pr_hwy.group(4) or "").strip()
        km_str = f"{km}.{hm}" if (hm and "." not in km) else km
        hwy_prefix = "PR" if s1_clean.upper().startswith("PR") else "CARR"
        st1_res = f"{hwy_prefix}-{hwy} KM {km_str}"
        st2_res = _standardize_secondary_unit(rest) if rest else ""
        return st1_res, st2_res, True, "", "", ""

    combined = " ".join(filter(None, [s1_clean, s2_clean]))
    if not combined:
        return "", "", False, "", "", ""

    # Check for PO Box in combined string
    po_box_match = RE_PO_BOX.search(combined)
    if po_box_match:
        po_box_num = po_box_match.group(1).upper()
        remaining = combined[:po_box_match.start()] + combined[po_box_match.end():]
        remaining = remaining.strip(" ,.-")
        if remaining:
            st1, st2, _, p_city, p_state, p_zip = _parse_us_street_tokens(remaining, enable_fuzzy=enable_fuzzy, city_raw=city_raw)
            if st1:
                combined_st2 = f"{st2} PO BOX {po_box_num}".strip() if st2 else f"PO BOX {po_box_num}"
                combined_st2 = _standardize_secondary_unit(combined_st2)
                st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
                return st1, combined_st2, True, p_city, p_state, p_zip
            else:
                combined_st2 = _standardize_secondary_unit(st2)
                return f"PO BOX {po_box_num}", combined_st2, True, p_city, p_state, p_zip
        return f"PO BOX {po_box_num}", "", True, "", "", ""

    st1, st2, ok, p_city, p_state, p_zip = _parse_us_street_tokens(combined, enable_fuzzy=enable_fuzzy, city_raw=city_raw)
    if st1 and city_raw and st1.upper() == city_raw.strip().upper():
        st1 = ""
    st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
    st2 = _standardize_secondary_unit(st2)
    return st1, st2, ok, p_city, p_state, p_zip


def _parse_us_street_lines(street1_raw: str, street2_raw: str = "", enable_fuzzy: bool = True, city_raw: str = "") -> Tuple[str, str, bool]:
    """Parses and standardizes US street1 and street2 into USPS Pub 28 format."""
    st1, st2, ok, _, _, _ = _parse_us_address_components(street1_raw, street2_raw, enable_fuzzy=enable_fuzzy, city_raw=city_raw)
    return st1, st2, ok


def _split_international_secondary_unit(street1: str, street2: str) -> Tuple[str, str]:
    """Helper to detect and split secondary unit in international street string, and normalize suffixes."""
    st1 = (street1 or "").upper()
    st2 = (street2 or "").upper()

    # Pre-split Flat / Apt at start: "Flat 4 150 High Street" -> st1="150 High Street", st2="APT 4"
    m_flat = RE_INTL_FLAT.match(st1)
    if m_flat:
        st2_cand = f"APT {m_flat.group(1).upper()}"
        st2 = f"{st2_cand} {st2}".strip() if st2 else st2_cand
        st1 = m_flat.group(2).strip()

    if not st2:
        m = RE_INTL_SEC_INLINE.search(st1)
        if m:
            sec_type = m.group(1).upper()
            sec_id = m.group(2).upper()
            sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
            st2 = f"{sec_type_norm} {sec_id}"
            st1 = st1[:m.start()] + st1[m.end():]
            st1 = RE_WHITESPACE.sub(" ", st1.strip(" ,.-"))
    elif st2:
        m2 = RE_INTL_SEC_START.match(st2)
        if m2:
            sec_type = m2.group(1).upper()
            sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
            st2 = f"{sec_type_norm} {m2.group(2).strip()}"

    words = st1.split()
    norm_words = []
    for w in words:
        w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
        if w_clean in STREET_SUFFIXES:
            norm_words.append(STREET_SUFFIXES[w_clean])
        elif w_clean in DIRECTIONALS:
            norm_words.append(DIRECTIONALS[w_clean])
        else:
            norm_words.append(w)
    st1 = " ".join(norm_words)

    return st1, st2


def generate_building_key(
    street1: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
    allow_locality: bool = False,
    **kwargs: Any,
) -> Optional[str]:
    """
    Derives deterministic building-level matching key (omits secondary units):
      Format: {STREET1}||{CITY}|{STATE}|{ZIP5_OR_POSTAL}|{COUNTRY_ALPHA3}
    Returns None if address is empty or fails parsing.
    """
    std = standardize_address(
        street1=street1,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        allow_locality=allow_locality,
        **kwargs,
    )
    return std.building_key


def generate_normalized_address_key(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
    allow_locality: bool = False,
    **kwargs: Any,
) -> Optional[str]:
    """
    Derives deterministic matching key:
      Format: {STREET1}|{STREET2}|{CITY}|{STATE}|{ZIP5_OR_POSTAL}|{COUNTRY_ALPHA3}
    Returns None if address is empty or fails parsing.
    """
    std = standardize_address(
        street1=street1,
        street2=street2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        allow_locality=allow_locality,
        **kwargs,
    )
    return std.normalized_address_key


def _finalize_standardized_address(
    std: StandardizedAddress,
    raw_input: Optional[Dict[str, Any]] = None,
    cache_key: Optional[str] = None,
    enable_geocoding: bool = False,
) -> StandardizedAddress:
    from address_standardizer.delivery import evaluate_delivery_intelligence
    from address_standardizer.registry import evaluate_corporate_risk

    # 1. Delivery Intelligence & DPV Footnotes
    vac_override = raw_input.get("is_vacant") if raw_input and raw_input.get("is_vacant") is not None else None
    deliv = evaluate_delivery_intelligence(std, raw_input=raw_input, is_vacant_override=vac_override)
    std.rdi = deliv.rdi
    std.cmra = deliv.cmra
    std.is_cmra = deliv.is_cmra
    std.vacant = deliv.vacant
    std.is_vacant = deliv.is_vacant
    std.dpv_footnotes = deliv.dpv_footnotes
    std.deliverability = deliv.deliverability
    std.secondary_prompt_required = deliv.secondary_prompt_required
    std.prompt_message = deliv.prompt_message
    std.suggested_secondary_units = deliv.suggested_secondary_units

    # 2. Corporate Risk & BOI Transparency Flags
    corp_score, corp_flags = evaluate_corporate_risk(std, raw_input=raw_input)
    std.corporate_risk_score = corp_score
    std.corporate_risk_flags = corp_flags

    # 3. Composite Confidence Scoring
    conf = compute_confidence_score(std, raw_input=raw_input)
    std.confidence_score = conf.composite_score
    std.routing_tier = conf.routing_tier
    std.failure_reason_codes = conf.failure_reason_codes
    if (
        conf.routing_tier == RoutingTier.MANUAL_STEWARDSHIP
        or std.is_registered_agent_hub
        or std.address_status == "parse_failed"
    ):
        audit_rec = get_audit_ledger().record_standardized_address(
            std, conf, raw_input=raw_input
        )
        std.audit_record = audit_rec

    # 4. Pure Offline Spatial & Rooftop Coordinate Resolution (Zero External APIs)
    if enable_geocoding:
        from address_standardizer.spatial import resolve_spatial_coordinates
        sp = resolve_spatial_coordinates(std)
        std.spatial_result = sp
        if sp is not None:
            std.latitude = sp.latitude
            std.longitude = sp.longitude
            std.precision = sp.precision
            std.accuracy_radius_meters = sp.accuracy_radius_meters
            if hasattr(sp, "metadata") and isinstance(sp.metadata, dict):
                std.census_tract = sp.metadata.get("census_tract")
                std.fips_code = sp.metadata.get("fips_code")

        # Enrich with census tract / FIPS metadata and handle fallback from offline reference index
        from address_standardizer.geocoder import geocode_offline
        geo_dict = geocode_offline(std, fallback_to_centroids=True)
        if geo_dict:
            if not std.census_tract and geo_dict.get("census_tract"):
                std.census_tract = geo_dict["census_tract"]
                if sp is not None and hasattr(sp, "metadata") and isinstance(sp.metadata, dict):
                    sp.metadata["census_tract"] = geo_dict["census_tract"]
            if not std.fips_code and geo_dict.get("fips_code"):
                std.fips_code = geo_dict["fips_code"]
                if sp is not None and hasattr(sp, "metadata") and isinstance(sp.metadata, dict):
                    sp.metadata["fips_code"] = geo_dict["fips_code"]
            if (std.latitude is None or (sp and sp.precision == "UNRESOLVED")) and geo_dict.get("latitude") is not None:
                std.latitude = geo_dict["latitude"]
                std.longitude = geo_dict["longitude"]
                std.precision = geo_dict["precision"]
                std.accuracy_radius_meters = geo_dict["accuracy_radius_meters"]

    if cache_key is not None:
        cache = get_default_cache()
        if cache.is_enabled():
            cache.set(cache_key, copy.copy(std))
    return std


def standardize_address(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
    is_vacant: Optional[bool] = None,
    enable_fuzzy: bool = True,
    enable_geocoding: bool = False,
    use_cache: bool = True,
    allow_locality: bool = False,
    **kwargs: Any,
) -> StandardizedAddress:
    """
    Standardize an address to USPS Pub 28 (for US) or International ISO standard.
    Generates deterministic normalized_address_key, building_key, phonetic_key,
    and flags registered agent hubs and private residences.
    """
    import os
    allow_locality = allow_locality or bool(
        kwargs.get("allow_locality_only")
        or kwargs.get("allow_city_level")
        or kwargs.get("allow_locality")
        or os.environ.get("ADDRESS_STANDARDIZER_ALLOW_LOCALITY") == "1"
    )
    raw_dict = {
        "street1": str(street1) if street1 is not None else "",
        "street2": str(street2) if street2 is not None else "",
        "city": str(city) if city is not None else "",
        "state": str(state) if state is not None else "",
        "postal_code": str(postal_code) if postal_code is not None else "",
        "country": str(country) if country is not None else "",
        "is_vacant": is_vacant if is_vacant is not None else kwargs.get("vacant"),
        "enable_fuzzy": enable_fuzzy,
        "enable_geocoding": enable_geocoding,
        "allow_locality": allow_locality,
    }

    cache = get_default_cache()
    cache_key = None
    if use_cache and cache.is_enabled():
        cache_key = make_cache_key(
            street1,
            street2,
            city,
            state,
            postal_code,
            country,
            enable_fuzzy=enable_fuzzy,
            enable_geocoding=enable_geocoding,
            allow_locality=allow_locality,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return copy.copy(cached)

    # Tier 0: Pre-Flight Sanity, Multiline Bleed Recovery, & Unicode NFKC Normalization
    s1_cand = street1 if street1 is not None else kwargs.get("street")
    s1_in = str(s1_cand).strip() if s1_cand is not None else ""
    s2_in = str(street2).strip() if street2 is not None else ""
    city_in = str(city).strip() if city is not None else ""
    state_in = str(state).strip() if state is not None else ""
    postal_in = str(postal_code).strip() if postal_code is not None else ""
    country_in = str(country).strip() if country is not None else ""

    # Embedded Newline / Multiline Field Bleed Cleaner
    s1_lines_u = [line.strip().upper() for line in re.split(r"[\r\n]+", s1_in) if line.strip()]
    if "\n" in city_in or "\r" in city_in:
        c_lines = [line.strip() for line in re.split(r"[\r\n]+", city_in) if line.strip()]
        if len(c_lines) > 1:
            cleaned_city_parts = []
            for cline in c_lines:
                cline_u = cline.upper()
                if (
                    re.match(r"^(?:(?:TH|ST|ND|RD|\d+(?:TH|ST|ND|RD)?)\s+(?:FLOOR|FL)|SUITE|STE|APT|UNIT|ROOM|RM|BLDG|BUILDING)\b", cline_u)
                    or cline_u.endswith((" FLOOR", " FL", " STE", " SUITE"))
                ):
                    if not s2_in:
                        s2_in = cline
                    elif cline_u not in s2_in.upper():
                        s2_in = f"{s2_in} {cline}".strip()
                elif cline_u in ("OFFICE", "MAIN OFFICE", "BRANCH OFFICE", "HOME OFFICE"):
                    pass
                elif cline_u in s1_lines_u:
                    pass
                else:
                    cleaned_city_parts.append(cline)
            if cleaned_city_parts:
                city_in = " ".join(cleaned_city_parts)

    city_in = re.sub(r"\s+(?:OFFICE|BRANCH\s+OFFICE|MAIN\s+OFFICE)$", "", city_in, flags=re.IGNORECASE).strip()

    if "\n" in s1_in or "\r" in s1_in:
        s1_lines = [line.strip() for line in re.split(r"[\r\n]+", s1_in) if line.strip()]
        if len(s1_lines) > 1:
            cleaned_s1_parts = []
            for sline in s1_lines:
                sline_u = sline.upper()
                if re.match(r"^(?:(?:TH|ST|ND|RD|\d+(?:TH|ST|ND|RD)?)\s+(?:FLOOR|FL)|SUITE|STE|APT|UNIT|ROOM|RM)\b", sline_u):
                    if not s2_in:
                        s2_in = sline
                    elif sline_u not in s2_in.upper():
                        s2_in = f"{s2_in} {sline}".strip()
                elif re.search(r"\bOFFICE\b", sline_u) and any(word in sline_u for word in (city_in.upper(), "OFFICE", "BRANCH", "MAIN")):
                    pass
                else:
                    cleaned_s1_parts.append(sline)
            if cleaned_s1_parts:
                s1_in = " ".join(cleaned_s1_parts)
            else:
                s1_in = ""

    # Municipal Prefix / City Acronym Noise Filter in street1
    if is_city_noise_in_street1(s1_in, city_in, state_in):
        s1_in = ""

    # Care-Of / Attention Prefix Cleaner
    # Strips the leading "c/o <Company Name>" segment and any legal entity suffix, preserving all subsequent address parts
    if re.match(r"^(?:C\s*/\s*O|IN\s+CARE\s+OF|ATTN|ATTENTION)\b", s1_in, re.IGNORECASE):
        LEGAL_SUFFIXES_CLEAN = {
            "LLC", "LP", "LLP", "LLLPO", "INC", "CORP", "LTD", "CO", "PLLC", "PC",
            "SA", "AG", "NV", "BV", "GMBH", "PLC", "FSB", "ESQ", "CPA", "MD", "PA",
            "NA", "NTSA", "TRUST", "COMPANY", "LIMITED", "INCORPORATED", "CORPORATION",
            "PARTNERSHIP", "SGIIC", "SL", "SRL", "SARL", "SAS", "SP", "SPA", "PTY",
            "BHD", "SDN", "KGAA", "SE", "QC", "SC", "EIRL", "SCOP", "JR", "SR", "II", "III", "IV", "LPA", "APC",
            "GROUP", "DEPARTMENT", "DEPT", "DIVISION", "DIV", "OFFICE", "HOLDINGS", "VENTURES", "CAPITAL",
            "MANAGEMENT", "PARTNERS", "FINANCIAL", "SERVICES", "SOLUTIONS"
        }
        m_co_head = re.match(r"^(?:C\s*/\s*O|IN\s+CARE\s+OF|ATTN|ATTENTION)\b[:\s\-]*", s1_in, re.IGNORECASE)
        after_co = s1_in[m_co_head.end():].strip() if m_co_head else s1_in

        re_street_boundary = re.compile(
            r"""(?:\b|(?<=[\s,]))(?:
                # Number followed by street name and thoroughfare suffix
                (\d+\s+(?:(?:N|S|E|W|NORTH|SOUTH|EAST|WEST|NE|NW|SE|SW)\s+)?[A-Za-z0-9\.\-']+\s+(?:ST|STREET|AVE|AVENUE|BLVD|BOULEVARD|RD|ROAD|DR|DRIVE|LN|LANE|WAY|CT|COURT|PL|PLACE|CIR|CIRCLE|PKWY|PARKWAY|HWY|HIGHWAY|TER|TERRACE|TRL|TRAIL|LOOP|WALK|RUN|BLUFF|ROW|ALLEY|ALY|CTR|CENTER|PLAZA|PK|PARK|PW|HY|HW|BL|BLV|WY|AL|GADE|TPKE|TURNPIKE|EXPY|EXPRESSWAY|PIKE|WALKWAY|MEWS|SQ|SQUARE)\b.*) |
                # Word numbers: ONE WORLD TRADE CENTER, etc.
                ((?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\s+(?:WORLD\s+TRADE\s+CENTER|WTC|BROADWAY|BOWERY|PENN\s+PLAZA|[A-Za-z0-9\.\-']+\s+(?:ST|STREET|AVE|AVENUE|BLVD|BOULEVARD|RD|ROAD|DR|DRIVE|LN|LANE|WAY|CT|COURT|PL|PLACE|CIR|CIRCLE|PKWY|PARKWAY|HWY|HIGHWAY|TER|TERRACE|TRL|TRAIL|LOOP|WALK|RUN|BLUFF|ROW|ALLEY|ALY|CTR|CENTER|PLAZA|PK|PARK|PW|HY|HW|BL|BLV|WY|AL|GADE|TPKE|TURNPIKE|EXPY|EXPRESSWAY|PIKE|WALKWAY|MEWS|SQ|SQUARE))\b.*) |
                # Broadway / Bowery / Embarcadero with digits
                (\d+\s+(?:(?:N|S|E|W|NORTH|SOUTH|EAST|WEST|NE|NW|SE|SW)\s+)?(?:BROADWAY|BOWERY|THE\s+EMBARCADERO|EMBARCADERO)\b.*) |
                # PO Box / Postal
                ((?:P\.?\s*O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX|PSC|CMR|HC|RR)\b.*) |
                # Spanish thoroughfares
                ((?:CALLE|AVENIDA|CARR|PASEO|CAMINO|CALZADA)\b.*)
            )$""",
            re.IGNORECASE | re.VERBOSE
        )

        extracted_street = ""
        m_boundary = re_street_boundary.search(after_co)
        if m_boundary:
            extracted_street = m_boundary.group(0).strip(" ,.-")
        else:
            for suf in LEGAL_SUFFIXES_CLEAN:
                m_suf = re.search(rf"\b{suf}\b[\s,]+(\d+\s+[A-Za-z].*)$", after_co, re.IGNORECASE)
                if m_suf:
                    extracted_street = m_suf.group(1).strip(" ,.-")
                    break

        if not extracted_street:
            m_fb = re.search(r"\b(\d+\s+[A-Za-z].*)$", after_co)
            if m_fb:
                extracted_street = m_fb.group(1).strip(" ,.-")

        if not extracted_street:
            co_parts = [p.strip() for p in s1_in.split(",") if p.strip()]
            rem_co = co_parts[1:]
            while rem_co and rem_co[0].upper().replace(".", "").replace("&", "").replace(" ", "").strip() in LEGAL_SUFFIXES_CLEAN:
                rem_co = rem_co[1:]
            if len(rem_co) == 1 and not re.search(r"\d", rem_co[0]):
                words = set(re.findall(r"\w+", rem_co[0].upper()))
                has_street_word = bool(words & {"ST", "STREET", "RD", "ROAD", "AVE", "AVENUE", "BLVD", "BOULEVARD", "DR", "DRIVE", "LN", "LANE", "WAY", "CT", "COURT", "PL", "PLACE", "BOX", "HWY", "HIGHWAY", "PKWY", "PARKWAY", "CIR", "CIRCLE"})
                if not has_street_word:
                    rem_co = []
            extracted_street = ", ".join(rem_co)

        s1_in = extracted_street
        if not s1_in and s2_in:
            s1_in = s2_in
            s2_in = ""

    s1_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', s1_in)).strip()
    s2_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', s2_in)).strip()
    s1_raw = clean_repetitive_cycles(s1_raw)
    s1_raw = RE_GLUED_HOUSE_NUM.sub(r"\1 \2", s1_raw)
    if s2_raw:
        s2_raw = clean_repetitive_cycles(s2_raw)
    city_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', city_in)).strip()
    state_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', state_in)).strip()
    postal_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', postal_in)).strip()
    country_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', country_in)).strip()

    raw_components = [v for v in [s1_raw, s2_raw, city_raw, state_raw, postal_raw, country_raw] if v]
    raw_street_address = ", ".join(raw_components)

    # Empty / garbage check
    if not raw_components:
        empty_std = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="",
            is_us=True,
            building_key=None,
            phonetic_key=None,
            is_registered_agent_hub=False,
            rooftop_address=None,
        )
        empty_std.country_iso3 = "USA"
        return _finalize_standardized_address(empty_std, raw_dict, cache_key, enable_geocoding=enable_geocoding)

    if len(raw_components) == 1 and s1_raw.upper() in ("N/A", "NONE", "NULL", "UNKNOWN", "-", ".", "NO ADDRESS"):
        garbage_std = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address=raw_street_address,
            is_us=True,
            building_key=None,
            phonetic_key=None,
            is_registered_agent_hub=False,
            rooftop_address=None,
        )
        garbage_std.country_iso3 = "USA"
        return _finalize_standardized_address(garbage_std, raw_dict, cache_key, enable_geocoding=enable_geocoding)

    # Pre-clean legacy baked-in ETL artifacts (e.g. "10005TH UNITED ESTS", "UNITED ESTS")
    s1_raw = RE_LEGACY_CORRUPTIONS.sub("", s1_raw).strip(" ,.-")
    if s2_raw:
        s2_raw = RE_LEGACY_CORRUPTIONS.sub("", s2_raw).strip(" ,.-")

    # Detect country code
    country_iso = normalize_country_code(
        country_raw,
        state_raw,
        postal_raw,
        raw_street=raw_street_address,
        city_raw=city_raw,
    )
    is_us = country_iso in ("USA", "PRI", "GUM", "VIR", "MNP", "ASM")

    # Strip terminal sovereign country before US or international parsing if structured components present
    if city_raw or state_raw or postal_raw:
        s1_raw = RE_TERMINAL_COUNTRY.sub("", s1_raw).rstrip(" ,.-")
        if s2_raw:
            s2_raw = RE_TERMINAL_COUNTRY.sub("", s2_raw).rstrip(" ,.-")

    # Tier 1: Ultra-Fast Deterministic Fast-Path Parser (< 0.015 ms)
    if is_us:
        fast_res = fast_path_parse(
            street1=s1_raw,
            street2=s2_raw,
            city=city_raw,
            state=state_raw,
            postal_code=postal_raw,
            country=country_raw or "USA",
            is_hub_func=is_registered_agent_hub_address,
            enable_fuzzy=enable_fuzzy,
        )
        if fast_res is not None:
            fast_res.country_iso3 = country_iso
            return _finalize_standardized_address(fast_res, raw_dict, cache_key, enable_geocoding=enable_geocoding)

    # Tier 2 & Tier 3: Deterministic Rule Matrix and Statistical CRF Fallback
    if is_us:
        # US Pipeline (USPS Pub 28)
        s1_clean = clean_redundant_street_tail(s1_raw, city=city_raw, state=state_raw, postal_code=postal_raw)
        s2_clean = clean_redundant_street_tail(s2_raw, city=city_raw, state=state_raw, postal_code=postal_raw) if s2_raw else s2_raw
        if not s1_clean:
            norm_s1 = ""
            norm_s2 = _standardize_secondary_unit(s2_clean) if s2_clean else ""
            success = True
            p_city = p_state = p_zip = None
        else:
            intersection_line = parse_intersection_address(s1_clean)
            if intersection_line:
                norm_s1 = intersection_line
                norm_s2 = s2_clean or ""
                success = True
                p_city = p_state = p_zip = None
            else:
                norm_s1, norm_s2, success, p_city, p_state, p_zip = _parse_us_address_components(
                    s1_clean, s2_clean, enable_fuzzy=enable_fuzzy, city_raw=city_raw
                )
        if is_invalid_thoroughfare(norm_s1):
            if norm_s1:
                norm_s2 = f"{norm_s1} {norm_s2}".strip() if norm_s2 else norm_s1
                norm_s1 = ""
        if not city_raw and p_city:
            city_raw = p_city
        if not state_raw and p_state:
            state_raw = p_state
        if not postal_raw and p_zip:
            postal_raw = p_zip

        norm_city = RE_WHITESPACE.sub(" ", RE_NON_ALPHANUMERIC.sub("", city_raw).strip().upper())
        norm_postal, zip5 = normalize_us_postal_code(postal_raw)
        norm_state = normalize_us_state(state_raw, zip5)

        if enable_fuzzy:
            from address_standardizer.fuzzy import heal_city_token, heal_postal_code_transposition
            if norm_city:
                healed_city = heal_city_token(norm_city, state=norm_state, zip3=zip5[:3] if zip5 else None)
                if healed_city:
                    norm_city = healed_city

            # Guarded postal code healing: only when norm_s1 is valid and non-empty, and city/state are valid
            if norm_s1 and norm_s1 != "PRIVATE RESIDENCE" and norm_city and norm_state in FROZEN_US_STATE_CODES:
                if zip5:
                    healed_zip = heal_postal_code_transposition(zip5, state=norm_state)
                    if healed_zip and healed_zip != zip5:
                        if len(norm_postal) > 5 and norm_postal[:5] == zip5:
                            norm_postal = f"{healed_zip}{norm_postal[5:]}"
                        else:
                            norm_postal = healed_zip
                        zip5 = healed_zip

        # Detect private residence indicators
        raw_combined_upper = f"{s1_raw} {s2_raw} {raw_street_address}".upper()
        is_priv = any(p in raw_combined_upper for p in [
            "PRIVATE RESIDENCE", "RESIDENTIAL", "PRIVATE ADDRESS", "CONFIDENTIAL", "RESIDENCE ONLY", "PERSONAL RESIDENCE"
        ])
        if is_priv:
            norm_s1 = "PRIVATE RESIDENCE"
            norm_s2 = ""

        if norm_s1 and norm_city and norm_s1.upper() == norm_city.upper():
            norm_s1 = ""

        # Minimum viable check: requires valid non-empty street line or locality-only record
        has_locality = bool(norm_city or norm_state or zip5)
        if not norm_s1:
            if allow_locality and has_locality:
                status = LocalityOnlyStatus("locality_only")
                k_city = fold_to_ascii_key(norm_city)
                k_state = fold_to_ascii_key(norm_state)
                k_post = fold_to_ascii_key(zip5)
                k_country = fold_to_ascii_key(country_iso) or "USA"
                key = f"||{k_city}|{k_state}|{k_post}|{k_country}"
                b_key = f"||{k_city}|{k_state}|{k_post}|{k_country}"
                p_key = None
            else:
                status = "parse_failed"
                key = None
                b_key = None
                p_key = None
        else:
            status = "standardized"
            k_s1 = fold_to_ascii_key(norm_s1)
            k_s2 = fold_to_ascii_key(norm_s2)
            k_city = fold_to_ascii_key(norm_city)
            k_state = fold_to_ascii_key(norm_state)
            k_post = fold_to_ascii_key(zip5)
            k_country = fold_to_ascii_key(country_iso) or "USA"
            key = f"{k_s1}|{k_s2}|{k_city}|{k_state}|{k_post}|{k_country}"
            b_key = f"{k_s1}||{k_city}|{k_state}|{k_post}|{k_country}"
            p_key = generate_phonetic_address_key(k_s1, k_post, k_city)

        if is_priv:
            is_hub = False
        else:
            is_hub = is_registered_agent_hub_address(
                street1=norm_s1,
                street2=norm_s2,
                city=norm_city,
                state=norm_state,
                postal_code=zip5,
                country=country_iso,
                raw_street=raw_street_address,
            )

        has_po = bool(re.search(r"\b(?:P\.?\s*O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX|APO|FPO|DPO)\b", f"{norm_s1} {norm_s2} {raw_street_address}".upper()))
        is_dual_physical = has_po and bool(norm_s1 and re.match(r"^(?:\d+|PR-|CARR-|KM\b)", norm_s1))
        rooftop_addr = None if (is_priv or (has_po and not is_dual_physical) or not norm_s1 or status != "standardized") else clean_rooftop_address(norm_s1)

        std_us = StandardizedAddress(
            street1=norm_s1,
            street2=norm_s2,
            city=norm_city,
            state=norm_state,
            postal_code=norm_postal,
            country=country_iso,
            normalized_address_key=key,
            address_status=status,
            raw_street_address=raw_street_address,
            is_us=True,
            is_private_residence=is_priv,
            building_key=b_key,
            phonetic_key=p_key,
            is_registered_agent_hub=is_hub,
            rooftop_address=rooftop_addr,
        )
        std_us.country_iso3 = country_iso
        return _finalize_standardized_address(std_us, raw_dict, cache_key, enable_geocoding=enable_geocoding)
    else:
        # International Pipeline
        if state_raw in ("US", "USA"):
            state_raw = ""
        if postal_raw == "00000":
            postal_raw = ""
        norm_s1 = ""
        norm_s2 = ""
        dep_loc = None
        bldg_name = None
        raw_combined_upper = f"{s1_raw} {s2_raw} {raw_street_address}".upper()
        is_priv = any(p in raw_combined_upper for p in [
            "PRIVATE RESIDENCE", "RESIDENTIAL", "PRIVATE ADDRESS", "CONFIDENTIAL", "RESIDENCE ONLY", "PERSONAL RESIDENCE"
        ])
        if is_priv:
            norm_s1 = "PRIVATE RESIDENCE"
            norm_s2 = ""
            norm_city = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
            norm_state = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", state_raw).strip().upper())
            norm_postal = RE_WHITESPACE.sub(" ", postal_raw.strip().upper())
        else:
            grammar = CountryGrammarRegistry.get(country_iso)
            parsed = grammar.standardize(
                street1=s1_raw,
                street2=s2_raw,
                city=city_raw,
                state=state_raw,
                postal_code=postal_raw,
                country=country_iso,
                raw_street_address=raw_street_address,
            )
            norm_s1 = parsed.format_street1()
            norm_s2 = parsed.format_street2()
            norm_city = parsed.city or ""
            norm_state = parsed.state or ""
            norm_postal = parsed.postal_code or ""
            dep_loc = parsed.dependent_locality
            bldg_name = parsed.building_name

        if norm_s1 and norm_city and norm_s1.upper() == norm_city.upper():
            norm_s1 = ""

        if is_invalid_thoroughfare(norm_s1):
            if norm_s1:
                norm_s2 = f"{norm_s1} {norm_s2}".strip() if norm_s2 else norm_s1
                norm_s1 = ""

        # If thoroughfare (street1) is empty but secondary delivery line / PO Box exists, promote it
        if not norm_s1 and norm_s2:
            if norm_s2.startswith("PO BOX ") or (RE_PHYSICAL_STREET_INDICATOR.search(norm_s2) and not is_invalid_thoroughfare(norm_s2)):
                norm_s1 = norm_s2
                norm_s2 = ""

        # Minimum viable check: requires valid non-empty street line or locality-only record
        has_locality = bool(norm_city or norm_state or norm_postal)
        if not norm_s1:
            if allow_locality and has_locality:
                status = LocalityOnlyStatus("locality_only")
                k_city = fold_to_ascii_key(norm_city)
                k_state = fold_to_ascii_key(norm_state)
                k_post = fold_to_ascii_key(norm_postal)
                k_country = fold_to_ascii_key(country_iso)
                key = f"||{k_city}|{k_state}|{k_post}|{k_country}"
                b_key = f"||{k_city}|{k_state}|{k_post}|{k_country}"
                p_key = None
            else:
                status = "parse_failed"
                key = None
                b_key = None
                p_key = None
        else:
            status = "standardized"
            k_s1 = fold_to_ascii_key(norm_s1)
            k_s2 = fold_to_ascii_key(norm_s2)
            k_city = fold_to_ascii_key(norm_city)
            k_state = fold_to_ascii_key(norm_state)
            k_post = fold_to_ascii_key(norm_postal)
            k_country = fold_to_ascii_key(country_iso)
            key = f"{k_s1}|{k_s2}|{k_city}|{k_state}|{k_post}|{k_country}"
            b_key = f"{k_s1}||{k_city}|{k_state}|{k_post}|{k_country}"
            p_key = generate_phonetic_address_key(k_s1, k_post, k_city)

        if is_priv:
            is_hub = False
        else:
            is_hub = is_registered_agent_hub_address(
                street1=norm_s1,
                street2=norm_s2,
                city=norm_city,
                state=norm_state,
                postal_code=norm_postal,
                country=country_iso,
                raw_street=raw_street_address,
            )

        has_po = bool(re.search(r"\b(?:P\.?\s*O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX|APO|FPO|DPO)\b", f"{norm_s1} {norm_s2} {raw_street_address}".upper()))
        is_dual_physical = has_po and bool(norm_s1 and re.match(r"^(?:\d+|PR-|CARR-|KM\b)", norm_s1))
        rooftop_addr = None if (is_priv or (has_po and not is_dual_physical) or not norm_s1 or status != "standardized") else clean_rooftop_address(norm_s1)

        std_intl = StandardizedAddress(
            street1=norm_s1,
            street2=norm_s2,
            city=norm_city,
            state=norm_state,
            postal_code=norm_postal,
            country=country_iso,
            normalized_address_key=key,
            address_status=status,
            raw_street_address=raw_street_address,
            is_us=False,
            is_private_residence=is_priv,
            building_key=b_key,
            phonetic_key=p_key,
            is_registered_agent_hub=is_hub,
            dependent_locality=dep_loc,
            building_name=bldg_name,
            rooftop_address=rooftop_addr,
        )
        std_intl.country_iso3 = country_iso
        return _finalize_standardized_address(std_intl, raw_dict, cache_key, enable_geocoding=enable_geocoding)
