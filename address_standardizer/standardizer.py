"""
Core Address Standardizer & Entity Resolution Engine.
=====================================================
Standardizes US and International addresses to USPS Publication 28 and ISO standards:
  - CRF tokenization via usaddress with a resilient regex fallback matrix.
  - Numbered street and ordinal word normalization (e.g. 5th Ave, 1st St, 42nd St).
  - Two-tier matching keys: suite-level (normalized_address_key) and building-level (building_key).
  - Phonetic Soundex blocking keys for typo tolerance.
  - Commercial formation / registered agent hub detection.
  - ZIP3 US state auto-healing.
"""

import re
import logging
from typing import Optional, Tuple, List, Dict, Any

try:
    import usaddress
except ImportError:
    usaddress = None

from address_standardizer.models import StandardizedAddress
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
)
from address_standardizer.phonetics import (
    compute_soundex,
    generate_phonetic_address_key,
)

logger = logging.getLogger(__name__)

STANDALONE_SEC_UNITS = set(SECONDARY_UNITS.keys()) - {"KEY"}


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
    return re.sub(r"^[,\.#;:]+|[,\.#;:]+$", "", t.strip())


def normalize_country_code(country_raw: Optional[str], state_raw: Optional[str] = None) -> str:
    """Resolve country to ISO-3166-1 alpha-3 code, defaulting to USA if state is a US state."""
    if country_raw:
        c_clean = country_raw.strip().upper()
        c_clean_alphanumeric = re.sub(r"[^\w\s]", "", c_clean)
        if c_clean_alphanumeric in COUNTRY_MAP:
            return COUNTRY_MAP[c_clean_alphanumeric]
        if len(c_clean_alphanumeric) == 3 and c_clean_alphanumeric.isalpha():
            return c_clean_alphanumeric

    if state_raw:
        s_clean = re.sub(r"[^\w\s]", "", state_raw.strip().upper())
        if s_clean in US_STATES:
            return "USA"

    return "USA"


normalize_country = normalize_country_code


def normalize_us_state(state_raw: Optional[str], zip5: Optional[str] = None) -> str:
    """Normalize US state string or full name to standard 2-letter postal code, with ZIP3 auto-healing."""
    res = ""
    if state_raw:
        s_clean = re.sub(r"[^\w\s]", "", state_raw.strip().upper())
        res = US_STATES.get(s_clean, s_clean[:2] if len(s_clean) == 2 else s_clean)
    if (not res or res not in US_STATES.values()) and zip5:
        zip3_st = get_state_from_zip3(zip5)
        if zip3_st:
            res = zip3_st
    return res


def normalize_us_postal_code(postal_raw: Optional[str]) -> Tuple[str, str]:
    """Returns (formatted_postal_code, zip5)."""
    if not postal_raw:
        return "", ""
    digits = re.sub(r"[^\d]", "", postal_raw.strip())
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
    combined = f"{street1} {street2} {city} {state} {postal_code} {raw_street}".upper()

    # Cayman / Offshore Legal Hubs
    if country in ("CYM", "CAYMAN ISLANDS") or "CAYMAN" in combined:
        if any(h in combined for h in ["UGLAND HOUSE", "PO BOX 309", "190 ELGIN", "CLIFTON HOUSE", "75 FORT ST"]):
            return True

    # US Delaware / Corporate Service Hubs
    if "1209 N ORANGE" in combined or "1209 NORTH ORANGE" in combined:
        return True  # Corporation Trust Center, Wilmington DE
    if "160 GREENTREE" in combined and ("DOVER" in combined or "19904" in combined or "DE" in combined):
        return True  # National Registered Agents, Dover DE
    if ("251 LITTLE FALLS" in combined or "2711 CENTERVILLE" in combined) and ("WILMINGTON" in combined or "DE" in combined):
        return True  # CSC, Wilmington DE
    if "850 NEW BURTON" in combined and ("DOVER" in combined or "19904" in combined):
        return True  # Cogency Global, Dover DE
    if "820 BEAR TAVERN" in combined and ("TRENTON" in combined or "NJ" in combined):
        return True  # Corporation Trust Company, NJ
    if "16192 COASTAL" in combined and ("LEWES" in combined or "19958" in combined):
        return True  # Harvard Business Services, DE
    if "30 N GOULD" in combined and ("SHERIDAN" in combined or "82801" in combined or "WY" in combined):
        return True  # Registered Agents Inc, WY
    if "3500 S DUPONT" in combined and ("DOVER" in combined or "19901" in combined):
        return True  # Registered Agents Inc, DE
    if "3773 HOWARD HUGHES" in combined and ("LAS VEGAS" in combined or "89169" in combined):
        return True  # Incorp Services, NV

    return False


def _rule_based_us_street_parse(address_str: str) -> Tuple[str, str, bool]:
    """
    Robust rule-based parser that standardizes US streets according to USPS Pub 28
    when usaddress is unavailable or raises parsing exceptions (e.g. RepeatedLabelError).
    """
    clean_addr = re.sub(r"[,\.]+", " ", address_str).strip()
    clean_addr = re.sub(r"\s+", " ", clean_addr).upper()
    if not clean_addr:
        return "", "", False

    # Check for PO Box
    m_po = re.search(r"\b(P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+)\b", clean_addr)
    if m_po:
        pob_num = m_po.group(2)
        rem = clean_addr[:m_po.start()] + clean_addr[m_po.end():]
        rem = rem.strip(" ,.-")
        if rem:
            st1_sub, _, _ = _rule_based_us_street_parse(rem)
            return st1_sub, f"PO BOX {pob_num}", True
        return f"PO BOX {pob_num}", "", True

    # Secondary unit extraction
    sec_unit = ""
    sec_pat = (
        r"\b(SUITE|STE|SUIT|UNIT|UNT|APT|APARTMENT|APPT|FLOOR|FL|FLR|ROOM|RM|BLDG|BUILDING|BLD|"
        r"DEPT|DEPARTMENT|LOT|SPC|SPACE|LEVEL|LVL|PH|PENTHOUSE|BSMT|BASEMENT|OFC|OFFICE|"
        r"HNGR|HANGAR|LBBY|LOBBY|LOWR|LOWER|MEZZ|MEZZANINE|PIER|REAR|SIDE|SLIP|STP|STOP|"
        r"TRLR|TRAILER|UPPR|UPPER|FRNT|FRONT|KEY)\b\.?\s*#?\s*([A-Z0-9\-]+)|"
        r"(?:^|\s)#\s*([A-Z0-9\-]+)|"
        r"\b(BSMT|BASEMENT|FRNT|FRONT|LBBY|LOBBY|LOWR|LOWER|MEZZ|MEZZANINE|OFC|OFFICE|PH|PENTHOUSE|REAR|SIDE|UPPR|UPPER)\b$"
    )
    m_sec = re.search(sec_pat, clean_addr)
    if m_sec:
        if m_sec.group(1):
            sec_type = SECONDARY_UNITS.get(m_sec.group(1), m_sec.group(1))
            sec_val = m_sec.group(2)
            sec_unit = f"{sec_type} {sec_val}"
        elif m_sec.group(3):
            sec_unit = f"STE {m_sec.group(3)}"
        elif m_sec.group(4):
            sec_unit = SECONDARY_UNITS.get(m_sec.group(4), m_sec.group(4))
        clean_addr = clean_addr[:m_sec.start()] + clean_addr[m_sec.end():]
        clean_addr = re.sub(r"\s+", " ", clean_addr).strip()

    tokens = clean_addr.split()
    norm_tokens = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        # Preserve house number at index 0 when address has 3+ tokens (e.g. 100 Wall St)
        if i == 0 and t.isdigit() and len(tokens) > 2:
            norm_tokens.append(t)
            i += 1
            continue

        if i + 1 < len(tokens):
            compound_candidate = f"{t} {tokens[i+1]}"
            if compound_candidate in COMPOUND_ORDINALS:
                norm_tokens.append(COMPOUND_ORDINALS[compound_candidate])
                i += 2
                continue
        if t in COMPOUND_ORDINALS:
            norm_tokens.append(COMPOUND_ORDINALS[t])
        elif t in WORD_ORDINALS:
            norm_tokens.append(WORD_ORDINALS[t])
        elif t in DIRECTIONALS:
            norm_tokens.append(DIRECTIONALS[t])
        elif t in STREET_SUFFIXES:
            norm_tokens.append(STREET_SUFFIXES[t])
        elif t.isdigit() and 1 <= int(t) <= 999:
            prev = norm_tokens[-1] if norm_tokens else ""
            if prev not in ("RTE", "ROUTE", "HWY", "HIGHWAY", "CR", "SR") and i + 1 < len(tokens) and tokens[i+1] in STREET_SUFFIXES:
                norm_tokens.append(num_to_ordinal(int(t)))
            else:
                norm_tokens.append(t)
        else:
            norm_tokens.append(t)
        i += 1

    st1 = " ".join(norm_tokens).strip()
    return st1, sec_unit, bool(st1)


def _parse_us_street_tokens(address_str: str) -> Tuple[str, str, bool, str, str, str]:
    """Parse address string using usaddress with rule-based fallback and USPS Pub 28 mapping."""
    if usaddress is not None:
        try:
            parsed = usaddress.parse(address_str)
        except Exception:
            parsed = None
    else:
        parsed = None

    if parsed is None:
        st_input = address_str
        p_city = ""
        m_sz = re.search(r"\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b", address_str.upper())
        p_st = m_sz.group(1) if m_sz else ""
        p_zp = m_sz.group(2) if m_sz else ""
        if m_sz:
            before_sz = address_str[:m_sz.start()].rstrip(" ,")
            if "," in before_sz:
                st_part, city_cand = before_sz.rsplit(",", 1)
                st_input = st_part.strip()
                p_city = city_cand.strip()
            elif not re.search(r"\d", before_sz):
                st_input = ""
                p_city = before_sz.strip()
            else:
                st_input = before_sz.strip()
        rb_st1, rb_st2, ok = _rule_based_us_street_parse(st_input)
        return rb_st1, rb_st2, ok, p_city, p_st, p_zp

    street_parts: List[str] = []
    sec_parts: List[str] = []
    building_parts: List[str] = []
    city_parts: List[str] = []
    state_parts: List[str] = []
    zip_parts: List[str] = []

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
            street_parts.append(DIRECTIONALS.get(clean, clean))
        elif label in ("StreetNamePostType", "StreetNamePreType"):
            street_parts.append(STREET_SUFFIXES.get(clean, clean))
        elif label == "StreetName":
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
            elif clean.isdigit() and 1 <= int(clean) <= 999:
                prev = street_parts[-1] if street_parts else ""
                if prev not in ("RTE", "ROUTE", "HWY", "HIGHWAY", "CR", "SR"):
                    street_parts.append(num_to_ordinal(int(clean)))
                else:
                    street_parts.append(clean)
            else:
                street_parts.append(clean)
        elif label == "OccupancyType":
            sec_parts.append(SECONDARY_UNITS.get(clean, clean))
        elif label in ("OccupancyIdentifier", "SubaddressIdentifier"):
            clean_id = clean.lstrip("#").strip()
            if clean_id:
                if clean_id in SECONDARY_UNITS:
                    sec_parts.append(SECONDARY_UNITS[clean_id])
                else:
                    if not sec_parts:
                        sec_parts.append("STE")
                    sec_parts.append(clean_id)
        elif label == "SubaddressType":
            sec_parts.append(SECONDARY_UNITS.get(clean, clean))
        elif label == "BuildingName":
            building_parts.append(clean)
        elif label in ("USPSBoxType", "USPSBoxID", "USPSBoxGroupType", "USPSBoxGroupID"):
            sec_parts.append(clean)
        elif label == "PlaceName":
            if clean in STANDALONE_SEC_UNITS:
                sec_type = SECONDARY_UNITS.get(clean, clean)
                if i + 1 < len(parsed):
                    next_tok, next_lbl = parsed[i + 1]
                    next_clean = _clean_token(next_tok).upper()
                    if next_lbl in ("ZipCode", "PlaceName", "OccupancyIdentifier", "SubaddressIdentifier") and (len(next_clean) <= 4 or next_clean.isalnum()):
                        sec_parts.append(f"{sec_type} {next_clean}")
                        i += 2
                        continue
                sec_parts.append(sec_type)
            else:
                city_parts.append(clean)
        elif label == "StateName":
            state_parts.append(clean)
        elif label == "ZipCode":
            zip_parts.append(clean)
        elif label in ("CountryName", "Recipient", "NotAddress"):
            i += 1
            continue
        else:
            street_parts.append(clean)
        i += 1

    clean_st = " ".join(state_parts)
    if clean_st not in US_STATES and len(state_parts) > 1:
        if state_parts[-1] in US_STATES.values():
            city_parts = state_parts[:-1] + city_parts
            state_parts = [state_parts[-1]]

    st1 = " ".join(street_parts).strip()
    st2 = " ".join(sec_parts).strip()
    p_city = " ".join(city_parts).strip()
    p_state = " ".join(state_parts).strip()
    p_zip = " ".join(zip_parts).strip()

    # If street_parts was empty but building_parts exists (e.g. "One Financial Plaza")
    if not st1 and building_parts:
        st1 = " ".join(building_parts).strip()
    elif st1 and building_parts:
        # Preserve building name in st2 rather than discarding it
        b_name = " ".join(building_parts).strip()
        st2 = f"{b_name} {st2}".strip() if st2 else b_name

    # Fallback to rule-based parser if both empty and no city/state/zip was parsed
    if not st1 and not st2 and not (p_city or p_state or p_zip):
        rb_st1, rb_st2, ok = _rule_based_us_street_parse(address_str)
        return rb_st1, rb_st2, ok, p_city, p_state, p_zip

    return st1, st2, True, p_city, p_state, p_zip


def _parse_us_address_components(street1_raw: str, street2_raw: str = "") -> Tuple[str, str, bool, str, str, str]:
    """
    Parses US address lines and returns (st1, st2, ok, p_city, p_state, p_zip).
    """
    combined = " ".join(filter(None, [street1_raw.strip(), street2_raw.strip()]))
    if not combined:
        return "", "", False, "", "", ""

    # Check for PO Box pattern
    po_box_match = re.search(r"\b(P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+)\b", combined, re.IGNORECASE)
    if po_box_match:
        po_box_num = po_box_match.group(2).upper()
        remaining = combined[:po_box_match.start()] + combined[po_box_match.end():]
        remaining = remaining.strip(" ,.-")
        if remaining:
            st1, _, _, p_city, p_state, p_zip = _parse_us_street_tokens(remaining)
            if st1:
                return st1, f"PO BOX {po_box_num}", True, p_city, p_state, p_zip
            else:
                return f"PO BOX {po_box_num}", "", True, p_city, p_state, p_zip
        return f"PO BOX {po_box_num}", "", True, "", "", ""

    return _parse_us_street_tokens(combined)


def _parse_us_street_lines(street1_raw: str, street2_raw: str = "") -> Tuple[str, str, bool]:
    """
    Parses and standardizes US street1 and street2 into USPS Pub 28 format.
    Splits embedded secondary units into street2. Returns (st1, st2, ok).
    """
    st1, st2, ok, _, _, _ = _parse_us_address_components(street1_raw, street2_raw)
    return st1, st2, ok


def _split_international_secondary_unit(street1: str, street2: str) -> Tuple[str, str]:
    """Helper to detect and split secondary unit in international street string, and normalize suffixes."""
    st1 = (street1 or "").upper()
    st2 = (street2 or "").upper()
    if not st2:
        pattern = r"\b(SUITE|STE|UNIT|APT|FLOOR|FL|LEVEL|LVL|PO BOX)\s*#?\s*([A-Z0-9\-]+)\b"
        m = re.search(pattern, st1, re.IGNORECASE)
        if m:
            sec_type = m.group(1).upper()
            sec_id = m.group(2).upper()
            sec_type_norm = SECONDARY_UNITS.get(sec_type, sec_type)
            st2 = f"{sec_type_norm} {sec_id}"
            st1 = st1[:m.start()] + st1[m.end():]
            st1 = re.sub(r"\s+", " ", st1.strip(" ,.-"))
    elif st2:
        pattern2 = r"^(SUITE|STE|UNIT|APT|FLOOR|FL|LEVEL|LVL|PO BOX)\s*#?\s*(.+)$"
        m2 = re.match(pattern2, st2, re.IGNORECASE)
        if m2:
            sec_type_norm = SECONDARY_UNITS.get(m2.group(1).upper(), m2.group(1).upper())
            st2 = f"{sec_type_norm} {m2.group(2).strip()}"

    words = st1.split()
    norm_words = []
    for w in words:
        w_clean = re.sub(r"[^\w]", "", w).upper()
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


def standardize_address(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
) -> StandardizedAddress:
    """
    Standardize an address to USPS Pub 28 (for US) or International ISO standard.
    Generates deterministic normalized_address_key, building_key, phonetic_key,
    and flags registered agent hubs and private residences.
    """
    s1_raw = (street1 or "").strip()
    s2_raw = (street2 or "").strip()
    city_raw = (city or "").strip()
    state_raw = (state or "").strip()
    postal_raw = (postal_code or "").strip()
    country_raw = (country or "").strip()

    raw_components = [v for v in [s1_raw, s2_raw, city_raw, state_raw, postal_raw, country_raw] if v]
    raw_street_address = ", ".join(raw_components)

    # Empty / garbage check
    if not raw_components:
        return StandardizedAddress(
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

    if len(raw_components) == 1 and s1_raw.upper() in ("N/A", "NONE", "NULL", "UNKNOWN", "-", ".", "NO ADDRESS"):
        return StandardizedAddress(
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

    # Country detection
    country_iso = normalize_country_code(country_raw, state_raw)
    is_us = country_iso in ("USA", "PRI", "GUM", "VIR", "MNP", "ASM")

    if is_us:
        # US Pipeline (USPS Pub 28)
        norm_s1, norm_s2, success, p_city, p_state, p_zip = _parse_us_address_components(s1_raw, s2_raw)
        if not city_raw and p_city:
            city_raw = p_city
        if not state_raw and p_state:
            state_raw = p_state
        if not postal_raw and p_zip:
            postal_raw = p_zip

        norm_city = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", city_raw).strip().upper())
        norm_postal, zip5 = normalize_us_postal_code(postal_raw)
        norm_state = normalize_us_state(state_raw, zip5)

        # Detect private residence indicators
        raw_combined_upper = f"{s1_raw} {s2_raw} {raw_street_address}".upper()
        is_priv = any(p in raw_combined_upper for p in [
            "PRIVATE RESIDENCE", "RESIDENTIAL", "PRIVATE ADDRESS", "CONFIDENTIAL", "RESIDENCE ONLY", "PERSONAL RESIDENCE"
        ])
        if is_priv:
            norm_s1 = "PRIVATE RESIDENCE"
            norm_s2 = ""

        # Minimum viable check: requires valid street line OR valid (city + state/zip)
        if not norm_s1 and not (norm_city and (norm_state or zip5)):
            status = "parse_failed"
            key = None
            b_key = None
            p_key = None
        else:
            status = "standardized"
            if norm_s1 and norm_city and norm_s1.upper() == norm_city.upper():
                norm_s1 = ""
            key = f"{norm_s1}|{norm_s2}|{norm_city}|{norm_state}|{zip5}|{country_iso}"
            b_key = f"{norm_s1}||{norm_city}|{norm_state}|{zip5}|{country_iso}"
            p_key = generate_phonetic_address_key(norm_s1, zip5, norm_city)

        is_hub = is_registered_agent_hub_address(
            street1=norm_s1,
            street2=norm_s2,
            city=norm_city,
            state=norm_state,
            postal_code=zip5,
            country=country_iso,
            raw_street=raw_street_address,
        )

        return StandardizedAddress(
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
    else:
        # International Pipeline
        norm_s1_base = re.sub(r"\s+", " ", re.sub(r"[,\.]+", " ", s1_raw).strip().upper())
        norm_s2_base = re.sub(r"\s+", " ", re.sub(r"[,\.]+", " ", s2_raw).strip().upper())
        norm_s1, norm_s2 = _split_international_secondary_unit(norm_s1_base, norm_s2_base)

        norm_city = re.sub(r"\s+", " ", re.sub(r"[,\.]+", " ", city_raw).strip().upper())
        norm_state = re.sub(r"\s+", " ", re.sub(r"[,\.]+", " ", state_raw).strip().upper())
        if country_iso == "CAN" and norm_state in CANADIAN_PROVINCES:
            norm_state = CANADIAN_PROVINCES[norm_state]
        norm_postal = re.sub(r"\s+", " ", postal_raw.strip().upper())

        # Minimum viable check: requires street OR city/postal
        if not norm_s1 and not (norm_city or norm_postal):
            status = "parse_failed"
            key = None
            b_key = None
            p_key = None
        else:
            status = "standardized"
            if norm_s1 and norm_city and norm_s1.upper() == norm_city.upper():
                norm_s1 = ""
            key = f"{norm_s1}|{norm_s2}|{norm_city}|{norm_state}|{norm_postal}|{country_iso}"
            b_key = f"{norm_s1}||{norm_city}|{norm_state}|{norm_postal}|{country_iso}"
            p_key = generate_phonetic_address_key(norm_s1, norm_postal, norm_city)

        is_hub = is_registered_agent_hub_address(
            street1=norm_s1,
            street2=norm_s2,
            city=norm_city,
            state=norm_state,
            postal_code=norm_postal,
            country=country_iso,
            raw_street=raw_street_address,
        )

        return StandardizedAddress(
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
            is_private_residence=False,
            building_key=b_key,
            phonetic_key=p_key,
            is_registered_agent_hub=is_hub,
        )
