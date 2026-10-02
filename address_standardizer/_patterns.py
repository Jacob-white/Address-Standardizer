"""
Pre-Compiled Regular Expressions and Fast Lookup Sets.
======================================================
Provides pre-compiled regex automata and immutable frozensets to eliminate
re.compile overhead and accelerate token validation.
"""

import re
from typing import Optional
from address_standardizer.tables import (
    DIRECTIONALS,
    STREET_SUFFIXES,
    SECONDARY_UNITS,
    US_STATES,
)

# ---------------------------------------------------------------------------
# Pre-Compiled Regular Expressions
# ---------------------------------------------------------------------------

# Token cleaning & whitespace
RE_CLEAN_TOKEN = re.compile(r"^[,\.#;:\-]+|[,\.#;:\-]+$")
RE_WHITESPACE = re.compile(r"\s+")
RE_NON_ALPHANUMERIC = re.compile(r"[^\w\s]")
RE_NON_DIGITS = re.compile(r"[^\d]")
RE_PUNCTUATION_SPLIT = re.compile(r"[,\.;:#]+")

# Tier 1 Fast-Path Regexes
# Matches: "100 Main St, New York, NY 10005" or "100 Main St, Suite 200, New York, NY 10005"
RE_CANONICAL_COMMA = re.compile(
    r"^(\d+[A-Z0-9\-\/]*)\s+([^,]+?)(?:,\s*([^,]+?))?,\s*([^,]+?),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$",
    re.IGNORECASE
)

# State and ZIP matching
RE_STATE_ZIP = re.compile(r"\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b", re.IGNORECASE)
RE_TERMINAL_ZIP = re.compile(r"\b(\d{5})(?:-(\d{4}))?\b$")

# PO Box
RE_PO_BOX = re.compile(r"\b(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+)\b", re.IGNORECASE)
RE_PO_BOX_START = re.compile(r"^(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+)", re.IGNORECASE)

# Secondary Units
RE_SEC_UNIT = re.compile(
    r"\b(SUITE|STE|SUIT|UNIT|UNT|APT|APARTMENT|APPT|FLOOR|FL|FLR|ROOM|RM|BLDG|BUILDING|BLD|"
    r"DEPT|DEPARTMENT|LOT|SPC|SPACE|LEVEL|LVL|HNGR|HANGAR|KEY|PIER|SLIP|STP|STOP|TRLR|TRAILER)\b\.?\s*#?\s*([A-Z0-9\-]+)|"
    r"#\s*([A-Z0-9\-]+)|"
    r"\b(BSMT|BASEMENT|FRNT|FRONT|LBBY|LOBBY|LOWR|LOWER|MEZZ|MEZZANINE|OFC|OFFICE|PH|PENTHOUSE|REAR|SIDE|UPPR|UPPER)\b\.?(?:\s*#?\s*(\d+[A-Z0-9\-]*|[A-Z]\b))?",
    re.IGNORECASE
)

# PMB / Private Mailbox
RE_PMB = re.compile(r"\b(?:PMB|PRIVATE\s+MAILBOX)\s*#?\s*([A-Z0-9\-]+)\b", re.IGNORECASE)

# Queens borough hyphenation vs street range vs attached secondary unit
RE_QUEENS_BOROUGH = re.compile(r"^(\d+-\d+)\s+([A-Za-z].*)$")
RE_FRACTIONAL_HOUSE = re.compile(r"^(\d+)\s+(1/2|1/4|3/4|[A-Z])\b", re.IGNORECASE)

# Suffix-attached secondary unit (e.g. "Main St-4B")
RE_ATTACHED_SEC_UNIT = re.compile(r"^([A-Z0-9\s]+?)-(?:STE|APT|UNIT|FL|RM)?\s*([A-Z0-9]+)$", re.IGNORECASE)

# Puerto Rico Urbanization
RE_URBANIZATION = re.compile(
    r"\b(?:URB|URBANIZACION)\.?\s+([A-Z\s]+?)(?=\d|\bCALLE\b|\bAVE\b|\bBO\b|,|$)",
    re.IGNORECASE
)

# International Postcodes
RE_UK_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.IGNORECASE)
RE_CAN_POSTCODE = re.compile(r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b", re.IGNORECASE)

# Numbered streets
RE_NUMBERED_STREET = re.compile(r"^(\d+)(?:ST|ND|RD|TH)?$", re.IGNORECASE)

# Glued punctuation normalization
RE_GLUED_HASH = re.compile(r"(?<=[A-Za-z0-9])#(?=[A-Za-z0-9])")
RE_GLUED_UNIT = re.compile(r"\b(APT|STE|UNIT|FL)\.?(?=\d)", re.IGNORECASE)

# Military Mail (APO, FPO, DPO)
RE_MILITARY_CITY = re.compile(r"\b(APO|FPO|DPO)\b", re.IGNORECASE)
RE_MILITARY_STATE = re.compile(r"\b(AE|AP|AA)\b", re.IGNORECASE)
RE_MILITARY_UNIT_BOX = re.compile(r"\b(UNIT\s+\d+)\s+(BOX\s+\d+)\b", re.IGNORECASE)

# Rural Route & Highway Contract
RE_RURAL_ROUTE = re.compile(r"\b(RR|RURAL\s+ROUTE)\s*#?\s*(\d+)\b(?:\s*BOX\s*([A-Z0-9\-]+))?", re.IGNORECASE)
RE_HIGHWAY_CONTRACT = re.compile(r"\b(HC|HIGHWAY\s+CONTRACT)\s*#?\s*(\d+)\b(?:\s*BOX\s*([A-Z0-9\-]+))?", re.IGNORECASE)

# Additional Pre-Compiled Utility Patterns
RE_CLEAN_ALPHA = re.compile(r"[^A-Z]")
RE_SAINT_HYPHEN = re.compile(r"\b(ST|SAINT)-([A-Za-z]{2,})\b", re.IGNORECASE)
RE_ATTACHED_SUFFIX_EXPLICIT_UNIT = re.compile(
    r"\b(ST|STREET|AVE|AVENUE|BLVD|BOULEVARD|RD|ROAD|DR|DRIVE|LN|LANE|WAY|CT|COURT|PL|PLACE|CIR|CIRCLE|PKWY|PARKWAY)-(STE|SUITE|APT|APARTMENT|UNIT|FL|FLOOR|RM|ROOM)\s*#?\s*([A-Z0-9\-]+)\b",
    re.IGNORECASE,
)
RE_ATTACHED_SUFFIX_BARE_UNIT = re.compile(
    r"\b(ST|STREET|AVE|AVENUE|BLVD|BOULEVARD|RD|ROAD|DR|DRIVE|LN|LANE|WAY|CT|COURT|PL|PLACE|CIR|CIRCLE|PKWY|PARKWAY)-(\d+[A-Z0-9\-]*|[A-Z])\b",
    re.IGNORECASE,
)
RE_ATTACHED_SUFFIX_UNIT = RE_ATTACHED_SUFFIX_BARE_UNIT
RE_PRIVATE_MAILBOX = re.compile(r"\bPRIVATE\s+MAILBOX\b", re.IGNORECASE)
RE_HYPHENATED_UNIT = re.compile(r"\b(STE|SUITE|APT|UNIT|FL)-(\d+)", re.IGNORECASE)
RE_COMMA_DOT = re.compile(r"[,\.]+")
RE_DIGITS = re.compile(r"\d")
RE_PHYSICAL_STREET_INDICATOR = re.compile(r"\b\d+\s+[A-Za-z]+\s+(ST|AVE|RD|BLVD|DR|LN|WAY)\b", re.IGNORECASE)
RE_OCCUPANCY_VAL_CLEAN = re.compile(r"[^\w\-]")
RE_IDENTIFIER_TOKEN = re.compile(r"^(\d+[A-Z0-9\-]*|[A-Z]\d+|[A-Z])$")
RE_INTL_FLAT = re.compile(r"^(?:FLAT|APT|UNIT)\s*#?\s*([A-Z0-9\-]+)\s+(.+)$", re.IGNORECASE)
RE_INTL_SEC_INLINE = re.compile(r"\b(SUITE|STE|UNIT|APT|FLOOR|FL|LEVEL|LVL|PO BOX|FLAT)\s*#?\s*([A-Z0-9\-]+)\b", re.IGNORECASE)
RE_INTL_SEC_START = re.compile(r"^(SUITE|STE|UNIT|APT|FLOOR|FL|LEVEL|LVL|PO BOX|FLAT)\s*#?\s*(.+)$", re.IGNORECASE)
RE_CAN_PROV_POSTAL = re.compile(r"^([A-Z]{2})\s+([A-Z]\d[A-Z]\s?\d[A-Z]\d)$")
RE_NUMBER_HYPHEN_NUMBER = re.compile(r"^\d+-\d+$")
RE_US_ZIP5_OR_9 = re.compile(r"^\d{5}(?:-\d{4})?$")
RE_PO_BOX_KEY = re.compile(r"^(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+)")
RE_NUMBERED_STREET_KEY = re.compile(r"^(\d+)(?:ST|ND|RD|TH)?$")

# ---------------------------------------------------------------------------
# Frozensets & Fast Lookup Dictionaries
# ---------------------------------------------------------------------------

FROZEN_STREET_SUFFIXES = frozenset(STREET_SUFFIXES.keys())
FROZEN_STREET_SUFFIX_VALUES = frozenset(STREET_SUFFIXES.values())

FROZEN_DIRECTIONALS = frozenset(DIRECTIONALS.keys())
FROZEN_DIRECTIONAL_VALUES = frozenset(DIRECTIONALS.values())

FROZEN_US_STATES = frozenset(US_STATES.keys())
FROZEN_US_STATE_CODES = frozenset(US_STATES.values())

FROZEN_SECONDARY_UNITS = frozenset(SECONDARY_UNITS.keys())
FROZEN_SECONDARY_UNIT_VALUES = frozenset(SECONDARY_UNITS.values())

ROUTE_PREFIXES = frozenset({
    "RTE", "ROUTE", "HWY", "HIGHWAY", "CR", "SR",
    "COUNTY RD", "COUNTY ROAD", "STATE ROUTE", "ROAD", "RD", "CO RD"
})

MULTI_WORD_CITIES = frozenset({
    "NEW YORK", "SAN FRANCISCO", "LOS ANGELES", "SALT LAKE CITY", "KANSAS CITY",
    "BATON ROUGE", "OKLAHOMA CITY", "COLORADO SPRINGS", "VIRGINIA BEACH",
    "JERSEY CITY", "FORT WORTH", "SAINT PAUL", "SAN ANTONIO", "SAN DIEGO",
    "ELK GROVE VILLAGE", "WHITE PLAINS", "FALLS CHURCH", "KEW GARDENS",
    "FOREST HILLS", "LONG ISLAND CITY", "JACKSON HEIGHTS", "WEST TRENTON",
    "SOUTH BEND", "NORTH VERNON", "PARK CITY", "GROVE CITY", "CEDAR RAPIDS",
    "PALM SPRINGS", "SANTA FE", "SANTA BARBARA", "SAN JOSE", "EL PASO",
    "LAS VEGAS", "CORPUS CHRISTI", "CHULA VISTA", "WINSTON SALEM", "GRAND RAPIDS",
    "SIOUX FALLS", "FORT WAYNE", "DES MOINES", "LITTLE ROCK"
})

# Known Standalone Secondary Units (Pub 28 Section 251)
STANDALONE_SEC_UNITS = frozenset({
    "BSMT", "BASEMENT", "FRNT", "FRONT", "LBBY", "LOBBY", "LOWR", "LOWER",
    "MEZZ", "MEZZANINE", "OFC", "OFFICE", "PH", "PENTHOUSE", "REAR", "SIDE", "UPPR", "UPPER"
})

def is_edit_distance_leq1(s1: str, s2: str) -> bool:
    """
    Determines if edit distance (Damerau-Levenshtein <= 1) between s1 and s2 is <= 1.
    Supports single insertion, deletion, substitution, or adjacent transposition.
    Runs in O(min(len(s1), len(s2))) time and O(1) memory.
    """
    len1, len2 = len(s1), len(s2)
    if abs(len1 - len2) > 1:
        return False

    if s1 == s2:
        return True

    if len1 == len2:
        diffs = 0
        i = 0
        while i < len1:
            if s1[i] != s2[i]:
                diffs += 1
                if diffs > 1:
                    return False
                if i + 1 < len1 and s1[i] == s2[i + 1] and s1[i + 1] == s2[i]:
                    i += 2
                    continue
            i += 1
        return diffs <= 1

    # Length difference is 1: ensure s1 is the shorter string
    if len1 > len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1

    i = 0
    j = 0
    diffs = 0
    while i < len1 and j < len2:
        if s1[i] != s2[j]:
            diffs += 1
            if diffs > 1:
                return False
            j += 1
        else:
            i += 1
            j += 1
    return True


def get_fuzzy_suffix(token: str) -> Optional[str]:
    """
    O(1) dictionary check with distance <= 1 fallback against closed STREET_SUFFIXES.
    Fuzzy distance check only applies to word tokens of length >= 4 to avoid abbreviation collisions.
    Excludes keywords like STATE and COUNTY to prevent route prefix misidentification.
    """
    if not token or re.search(r"[\d\-]", token):
        return None
    tok_clean = RE_CLEAN_ALPHA.sub("", token.upper())
    if not tok_clean:
        return None
    if tok_clean in ("STATE", "COUNTY"):
        return None
    if tok_clean in STREET_SUFFIXES:
        return STREET_SUFFIXES[tok_clean]

    from address_standardizer.fuzzy import heal_street_suffix
    return heal_street_suffix(tok_clean, max_distance=2)


def get_fuzzy_directional(token: str) -> Optional[str]:
    """
    O(1) dictionary check with distance <= 1 fallback against DIRECTIONALS.
    Fuzzy distance check only applies to word tokens of length >= 3 to avoid 1-letter collisions.
    """
    tok_clean = RE_CLEAN_ALPHA.sub("", token.upper())
    if not tok_clean:
        return None
    if tok_clean in DIRECTIONALS:
        return DIRECTIONALS[tok_clean]

    if len(tok_clean) < 3:
        return None

    t_len = len(tok_clean)
    for canonical, abbr in DIRECTIONALS.items():
        if len(canonical) >= 4 and abs(len(canonical) - t_len) <= 1:
            if is_edit_distance_leq1(tok_clean, canonical):
                return abbr
    return None
