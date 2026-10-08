"""
Country, US state and postal-code normalization helpers (split out of standardizer.py).
"""

import unicodedata
import logging
import re
from typing import Optional, Tuple

from address_standardizer.tables import (
    STREET_SUFFIXES,
    US_STATES,
    COUNTRY_MAP,
    CANADIAN_PROVINCES,
    ZIP3_TO_STATE,
    GLOBAL_METRO_TO_COUNTRY,
)
from address_standardizer._patterns import (
    RE_CLEAN_TOKEN,
    RE_NON_ALPHANUMERIC,
    RE_NON_DIGITS,
    RE_STATE_ZIP,
    RE_UK_POSTCODE,
    RE_CAN_POSTCODE,
    FROZEN_US_STATE_CODES,
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


_US_STATE_NAMES = sorted((k for k in US_STATES if len(k) > 2 and k.replace(" ", "").isalpha()), key=len, reverse=True)
_RE_STATE_NAME_ZIP = re.compile(
    r"(?:^|[,\s])(?:" + "|".join(re.escape(n) for n in _US_STATE_NAMES) + r")\s+\d{5}(?:-\d{4})?\s*$"
)


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
        # "..., Poland, Ohio 44514": a full US state name followed by a 5-digit ZIP is a US address even when the
        # city (Poland, Denmark, Holland, Peru) or the state (Georgia) is also a country name.
        if _RE_STATE_NAME_ZIP.search(st_clean):
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

        # A trailing comma part that is a country's name in any supported language/accent ("Italia", "Belgique",
        # "Sverige", "México") resolves through the same registry the structured `country` field uses.
        if len(raw_parts) >= 2:
            trailing = raw_parts[-1].strip()
            if 3 <= len(trailing) <= 40 and not any(ch.isdigit() for ch in trailing):
                from address_standardizer.international.countries import CountryRegistry

                info = CountryRegistry.get(trailing)
                if info is not None and info.alpha3 != "USA":
                    return info.alpha3

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
