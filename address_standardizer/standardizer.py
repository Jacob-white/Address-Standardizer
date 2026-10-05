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

from address_standardizer.models import StandardizedAddress
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
    RE_MILITARY_UNIT_BOX,
    RE_RURAL_ROUTE,
    RE_TERMINAL_COUNTRY,
    clean_redundant_street_tail,
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

    # International metro check: When state is absent or not a US state,
    # check city against global metros to prevent erroneous USA defaulting
    if city_raw:
        c_clean = RE_NON_ALPHANUMERIC.sub(" ", city_raw).strip().upper()
        c_clean = " ".join(c_clean.split())
        if c_clean in GLOBAL_METRO_TO_COUNTRY:
            return GLOBAL_METRO_TO_COUNTRY[c_clean]
        c_unaccent = unicodedata.normalize("NFKD", c_clean).encode("ASCII", "ignore").decode("utf-8")
        if c_unaccent in GLOBAL_METRO_TO_COUNTRY:
            return GLOBAL_METRO_TO_COUNTRY[c_unaccent]

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
            if (len(raw_words[-1]) > 2 or raw_words[-1] not in FROZEN_US_STATE_CODES) and not raw_words[-1].isdigit():
                return COUNTRY_MAP[raw_words[-1]]

        # Check global metros in raw street SECOND
        for part in raw_street.split(","):
            p_clean = RE_NON_ALPHANUMERIC.sub(" ", part).strip().upper()
            p_clean = " ".join(p_clean.split())
            if p_clean in GLOBAL_METRO_TO_COUNTRY:
                return GLOBAL_METRO_TO_COUNTRY[p_clean]
            c_unaccent = unicodedata.normalize("NFKD", p_clean).encode("ASCII", "ignore").decode("utf-8")
            if c_unaccent in GLOBAL_METRO_TO_COUNTRY:
                return GLOBAL_METRO_TO_COUNTRY[c_unaccent]

    return "USA"


normalize_country = normalize_country_code


def normalize_us_state(state_raw: Optional[str], zip5: Optional[str] = None) -> str:
    """Normalize US state string or full name to standard 2-letter postal code, with ZIP3 auto-healing."""
    res = ""
    if state_raw:
        s_clean = RE_NON_ALPHANUMERIC.sub("", state_raw.strip().upper())
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
    """Pre-normalizes glued punctuation, symbols, and formatting."""
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
    # Strip any leading STE or SUITE if followed by other unit types (FL, APT, UNIT, DEPT, PH, SUITE, STE)
    s = re.sub(
        r"^(?:STE|SUITE)\s+(FL|FLOOR|FLR|APT|APARTMENT|UNIT|DEPT|DEPARTMENT|PH|PENTHOUSE|SUITE|STE)\b",
        r"\1",
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
                m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[i])
                if m:
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
        rr_num = m_rr.group(2)
        box_id = m_rr.group(3)
        st1_rr = f"RR {rr_num} BOX {box_id}".strip() if box_id else f"RR {rr_num}"
        return st1_rr, "", True

    m_hc = RE_HIGHWAY_CONTRACT.search(clean_addr)
    if m_hc:
        hc_num = m_hc.group(2)
        box_id = m_hc.group(3)
        st1_hc = f"HC {hc_num} BOX {box_id}".strip() if box_id else f"HC {hc_num}"
        return st1_hc, "", True

    # Check for Military Unit Box
    m_mil = RE_MILITARY_UNIT_BOX.search(clean_addr)
    if m_mil:
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

    # Secondary unit extraction
    m_sec = RE_SEC_UNIT.search(clean_addr)
    if m_sec:
        sec_cand = ""
        if m_sec.group(1):
            sec_type = SECONDARY_UNITS.get(m_sec.group(1).upper(), m_sec.group(1).upper())
            sec_val = m_sec.group(2).upper()
            sec_cand = f"{sec_type} {sec_val}"
        elif m_sec.group(3):
            sec_cand = f"STE {m_sec.group(3).upper()}"
        elif m_sec.group(4):
            sec_type = SECONDARY_UNITS.get(m_sec.group(4).upper(), m_sec.group(4).upper())
            sec_val = m_sec.group(5).upper() if m_sec.group(5) else ""
            sec_cand = f"{sec_type} {sec_val}".strip()
        sec_unit = f"{sec_unit} {sec_cand}".strip() if sec_unit else sec_cand
        clean_addr = clean_addr[:m_sec.start()] + clean_addr[m_sec.end():]

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
    if m_mil:
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
                if clean_id in SECONDARY_UNITS:
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
    if clean_st not in US_STATES:
        if len(state_parts) == 1 and state_parts[0] in STREET_SUFFIXES and state_parts[0] not in FROZEN_US_STATE_CODES:
            street_parts.append(STREET_SUFFIXES[state_parts[0]])
            state_parts = []
        elif len(state_parts) > 1:
            if state_parts[-1] in FROZEN_US_STATE_CODES:
                city_parts = state_parts[:-1] + city_parts
                state_parts = [state_parts[-1]]

    st1 = " ".join(street_parts).strip()
    st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
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

    st1 = re.sub(r"[\s,.\-#;:]+$", "", st1).strip()
    st2 = _standardize_secondary_unit(st2)

    # Fallback to rule-based parser if empty
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
    )
    return std.building_key


def generate_normalized_address_key(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
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

    # 4. Offline Spatial Coordinate Resolution
    if enable_geocoding:
        from address_standardizer.spatial import resolve_spatial_coordinates
        std.spatial_result = resolve_spatial_coordinates(std)

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
    **kwargs: Any,
) -> StandardizedAddress:
    """
    Standardize an address to USPS Pub 28 (for US) or International ISO standard.
    Generates deterministic normalized_address_key, building_key, phonetic_key,
    and flags registered agent hubs and private residences.
    """
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
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return copy.copy(cached)

    # Tier 0: Pre-Flight Sanity & Unicode NFKC Normalization
    s1_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', str(street1))).strip() if street1 is not None else ""
    s2_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', str(street2))).strip() if street2 is not None else ""
    city_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', str(city))).strip() if city is not None else ""
    state_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', str(state))).strip() if state is not None else ""
    postal_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', str(postal_code))).strip() if postal_code is not None else ""
    country_raw = re.sub(r"[\r\n\t]+", " ", unicodedata.normalize('NFKC', str(country))).strip() if country is not None else ""

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
        )
        garbage_std.country_iso3 = "USA"
        return _finalize_standardized_address(garbage_std, raw_dict, cache_key, enable_geocoding=enable_geocoding)

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
        norm_s1, norm_s2, success, p_city, p_state, p_zip = _parse_us_address_components(
            s1_clean, s2_clean, enable_fuzzy=enable_fuzzy, city_raw=city_raw
        )
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

        # Minimum viable check: requires valid non-empty street line
        if not norm_s1:
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
        )
        std_us.country_iso3 = country_iso
        return _finalize_standardized_address(std_us, raw_dict, cache_key, enable_geocoding=enable_geocoding)
    else:
        # International Pipeline
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

        # Minimum viable check: requires valid non-empty street line
        if not norm_s1:
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
        )
        std_intl.country_iso3 = country_iso
        return _finalize_standardized_address(std_intl, raw_dict, cache_key, enable_geocoding=enable_geocoding)
