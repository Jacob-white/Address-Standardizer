"""
Advanced Typo Recovery & Localized Fuzzy Correction Engine.
===========================================================
Implements Damerau-Levenshtein distance 1-2 candidate generation constrained
by state and ZIP3 for misspelled street suffixes, names, and city tokens,
along with digit transposition recovery for postal codes and street numbers.
"""

import functools
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from address_standardizer.tables import (
    STREET_SUFFIXES,
    DIRECTIONALS,
    US_STATES,
    ZIP3_TO_STATE,
)
from address_standardizer._patterns import MULTI_WORD_CITIES


@functools.lru_cache(maxsize=16384)
def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes true Damerau-Levenshtein edit distance between s1 and s2.
    Supports insertion, deletion, substitution, and transposition of adjacent characters.
    """
    len1, len2 = len(s1), len(s2)
    if s1 == s2:
        return 0
    if len1 == 0:
        return len2
    if len2 == 0:
        return len1

    # Matrix of size (len1 + 2) x (len2 + 2)
    inf = len1 + len2
    da: Dict[str, int] = {}
    h = [[0] * (len2 + 2) for _ in range(len1 + 2)]

    h[0][0] = inf
    for i in range(len1 + 1):
        h[i + 1][0] = inf
        h[i + 1][1] = i
    for j in range(len2 + 1):
        h[0][j + 1] = inf
        h[1][j + 1] = j

    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            i1 = da.get(s2[j - 1], 0)
            j1 = db
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            if cost == 0:
                db = j

            h[i + 1][j + 1] = min(
                h[i][j + 1] + 1,        # deletion
                h[i + 1][j] + 1,        # insertion
                h[i][j] + cost,         # substitution
                h[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1)  # transposition
            )
        da[s1[i - 1]] = i

    return h[len1 + 1][len2 + 1]


# ---------------------------------------------------------------------------
# Canonical City Reference by State
# ---------------------------------------------------------------------------

PROMINENT_STATE_CITIES: Dict[str, List[str]] = {
    "NY": ["NEW YORK", "BUFFALO", "ROCHESTER", "YONKERS", "SYRACUSE", "ALBANY", "WHITE PLAINS", "NEW ROCHELLE", "SCHENECTADY", "UTICA"],
    "CA": ["LOS ANGELES", "SAN DIEGO", "SAN JOSE", "SAN FRANCISCO", "FRESNO", "SACRAMENTO", "LONG BEACH", "OAKLAND", "BAKERSFIELD", "ANAHEIM", "SANTA BARBARA", "PALM SPRINGS"],
    "IL": ["CHICAGO", "AURORA", "NAPERVILLE", "JOLIET", "ROCKFORD", "SPRINGFIELD", "ELGIN", "PEORIA", "CHAMPAIGN"],
    "TX": ["HOUSTON", "SAN ANTONIO", "DALLAS", "AUSTIN", "FORT WORTH", "EL PASO", "ARLINGTON", "CORPUS CHRISTI", "PLANO", "LUBBOCK"],
    "FL": ["MIAMI", "ORLANDO", "TAMPA", "JACKSONVILLE", "ST PETERSBURG", "HIALEAH", "TALLAHASSEE", "FORT LAUDERDALE", "PORT ST LUCIE", "CAPE CORAL"],
    "PA": ["PHILADELPHIA", "PITTSBURGH", "ALLENTOWN", "READING", "ERIE", "SCRANTON", "BETHLEHEM", "LANCASTER", "HARRISBURG"],
    "GA": ["ATLANTA", "AUGUSTA", "COLUMBUS", "MACON", "SAVANNAH", "ATHENS", "SANDY SPRINGS", "ROSWELL"],
    "MA": ["BOSTON", "WORCESTER", "SPRINGFIELD", "CAMBRIDGE", "LOWELL", "BROCKTON", "QUINCY", "LYNN", "NEW BEDFORD"],
    "WA": ["SEATTLE", "SPOKANE", "TACOMA", "VANCOUVER", "BELLEVUE", "KENT", "EVERETT", "RENTON"],
    "CO": ["DENVER", "COLORADO SPRINGS", "AURORA", "FORT COLLINS", "LAKEWOOD", "THORNTON", "ARVADA", "WESTMINSTER", "BOULDER"],
    "AZ": ["PHOENIX", "TUCSON", "MESA", "CHANDLER", "SCOTTSDALE", "GLENDALE", "GILBERT", "TEMPE", "PEORIA", "SURPRISE"],
    "DE": ["WILMINGTON", "DOVER", "NEWARK", "MIDDLETOWN", "SMYRNA", "MILFORD", "SEAFORD", "GEORGETOWN", "LEWES"],
    "WY": ["CHEYENNE", "CASPER", "LARAMIE", "GILLETTE", "SHERIDAN", "ROCK SPRINGS", "JACKSON", "BUFFALO", "CODY"],
    "NV": ["LAS VEGAS", "HENDERSON", "RENO", "NORTH LAS VEGAS", "SPARKS", "CARSON CITY"],
    "NJ": ["NEWARK", "JERSEY CITY", "PATERSON", "ELIZABETH", "TRENTON", "CLIFTON", "CAMDEN", "PASSAIC"],
}

# Common US Street Names susceptible to typos
COMMON_STREET_NAMES = frozenset({
    "MAIN", "BROADWAY", "WASHINGTON", "LINCOLN", "JEFFERSON", "MADISON", "JACKSON",
    "LEXINGTON", "HIGHLAND", "SUNSET", "PARK", "OAK", "PINE", "MAPLE", "CEDAR",
    "ELM", "CHESTNUT", "WALNUT", "PEACHTREE", "MARKET", "CENTER", "SPRING", "FRONT",
    "RIVER", "CHURCH", "SECOND", "THIRD", "FOURTH", "FIFTH", "COLLEGE", "FRANKLIN",
    "ADAMS", "MONROE", "HICKORY", "WALNUT", "SPRUCE", "WILLOW", "CYPRESS", "LAUREL",
})

# Protected Proper Names, Spanish Indicators, and Standard Terms never to be fuzzy corrupted
PROTECTED_STREET_WORDS: frozenset[str] = frozenset({
    # Common proper names / historic names often found in street names
    "MARTIN", "LUTHER", "KING", "JR", "PRESIDENT", "SAINT", "SAN", "SANTA",
    "KENNEDY", "ROOSEVELT", "JEFFERSON", "LINCOLN", "WASHINGTON", "MADISON",
    "JACKSON", "ADAMS", "ADAM", "MONROE", "FRANKLIN", "HAMILTON", "GRANT", "LEE",
    "CLARK", "LEWIS", "BOONE", "CROCKETT", "HOUSTON", "AUSTIN", "TRAVIS",
    "PAINE", "RIVERA", "RIVERO", "CENTRE", "MAINE", "BRUCE", "PRICE", "PIERCE",
    "STONE", "WAYNE", "PAYNE", "CLINTON", "WILSON", "TAYLOR", "HARDING", "HOOVER",
    "TRUMAN", "CARTER", "BUSH", "OBAMA", "EISENHOWER", "MACARTHUR",
    # Spanish street types and indicators (especially Puerto Rico and Southwest)
    "CALLE", "AVENIDA", "PASEO", "CAMINO", "CARRETERA", "CALLEJON", "URB",
    "URBANIZACION", "SOL", "LUNA", "MAR", "FLAMBOYAN", "JARDINES", "PINOS",
    "DOS", "LAS", "DEL", "DE", "LOS", "PLAYA", "ISLA", "VALLE", "MONTE",
    "RIO", "VISTA", "BO", "BARRIO", "SECTOR", "PARC", "PARCELA", "CARR",
    "COND", "CONDOMINIO", "EDIF", "EDIFICIO", "RES", "RESIDENCIAL",
    # Prominent boroughs, geographic markers, and common street words
    "QUEENS", "BROOKLYN", "BRONX", "MANHATTAN", "STATEN", "ISLAND", "YORK",
    "FALLS", "LITTLE", "ORANGE", "GREENTREE", "GOULD", "UGLAND", "HOUSE",
    "FORT", "KISSENA", "CORONA", "JAMAICA", "WALL", "BAY", "BANK", "HIGH",
    "TREE", "PEACH", "ASH", "BIRCH", "FLOWER", "GRAND", "BROADWAY", "MARKET",
    "BELL", "BALL", "HALL", "CALL", "TALL", "BILL", "BULL", "DOLL", "POLL", "ROLL", "TOLL",
    "MICHIGAN", "PENNSYLVANIA", "CALIFORNIA",
    # Sovereign country / territorial words
    "STATES", "UNITED", "AMERICA", "ISLANDS",
})


@functools.lru_cache(maxsize=4096)
def heal_street_suffix(token: str, max_distance: int = 2) -> Optional[str]:
    """
    Recovers misspelled street suffixes using Damerau-Levenshtein distance <= max_distance.
    Only checks words of length >= 3 to avoid 2-letter abbreviation collisions.
    Rejects tokens containing digits or hyphens, protected words, and short substitutions.
    """
    if not token or re.search(r"[\d\-]", token):
        return None

    tok_clean = re.sub(r"[^A-Z]", "", token.upper())
    if not tok_clean or tok_clean in ("STATE", "STATES", "COUNTY", "UNITED", "AMERICA", "ISLANDS", "COUNTRY", "NORTH", "SOUTH", "EAST", "WEST"):
        return None

    if tok_clean in STREET_SUFFIXES:
        return STREET_SUFFIXES[tok_clean]

    if len(tok_clean) < 3 or tok_clean in PROTECTED_STREET_WORDS:
        return None

    t_len = len(tok_clean)
    allowed_distance = 1 if t_len <= 5 else max_distance
    best_match: Optional[str] = None
    min_dist = allowed_distance + 1

    for canonical, abbr in STREET_SUFFIXES.items():
        if len(canonical) >= 4 and abs(len(canonical) - t_len) <= allowed_distance:
            # For short tokens (<= 4 chars), reject substitutions (require anagram or omission/insertion)
            if t_len <= 4:
                if sorted(tok_clean) != sorted(canonical) and not (
                    set(tok_clean).issubset(set(canonical)) or set(canonical).issubset(set(tok_clean))
                ):
                    continue
            d = damerau_levenshtein_distance(tok_clean, canonical)
            if d <= allowed_distance and d < min_dist:
                min_dist = d
                best_match = abbr
                if d == 1:
                    break

    return best_match


@functools.lru_cache(maxsize=4096)
def heal_city_token(
    city_raw: str,
    state: Optional[str] = None,
    zip3: Optional[str] = None,
    max_distance: int = 2,
) -> Optional[str]:
    """
    Recovers misspelled city names constrained by state and/or ZIP3 sectional centers.
    """
    if not city_raw:
        return None

    city_unaccented = unicodedata.normalize("NFKD", city_raw).encode("ASCII", "ignore").decode("utf-8")
    clean_city = re.sub(r"[^\w\s]", "", city_unaccented).strip().upper()
    clean_city = re.sub(r"\s+", " ", clean_city)

    # 1. Direct match check
    if clean_city in MULTI_WORD_CITIES:
        return clean_city

    # Determine state from state arg or zip3
    target_state = (state or "").strip().upper()
    target_state = US_STATES.get(target_state, target_state)
    if not target_state and zip3 and zip3 in ZIP3_TO_STATE:
        target_state = ZIP3_TO_STATE[zip3]

    candidate_cities: List[str] = []
    if target_state in PROMINENT_STATE_CITIES:
        candidate_cities.extend(PROMINENT_STATE_CITIES[target_state])
    else:
        # Check all state cities if state is not specified
        for cities in PROMINENT_STATE_CITIES.values():
            candidate_cities.extend(cities)

    # Add multi-word cities
    candidate_cities.extend(MULTI_WORD_CITIES)

    best_match: Optional[str] = None
    min_dist = max_distance + 1
    c_len = len(clean_city)

    for cand in candidate_cities:
        if abs(len(cand) - c_len) <= max_distance:
            d = damerau_levenshtein_distance(clean_city, cand)
            if d <= max_distance and d < min_dist:
                min_dist = d
                best_match = cand
                if d == 1:
                    break

    return best_match


@functools.lru_cache(maxsize=4096)
def heal_street_name(name_raw: str, max_distance: int = 1) -> Optional[str]:
    """
    Recovers prominent misspelled street names using edit distance <= max_distance.
    Guarded against corrupting valid English proper names, Spanish street indicators,
    and dictionary words.
    """
    name_unaccented = unicodedata.normalize("NFKD", name_raw).encode("ASCII", "ignore").decode("utf-8")
    clean_name = re.sub(r"[^A-Z]", "", name_unaccented.upper())
    if not clean_name or len(clean_name) < 3:
        return None

    if clean_name in COMMON_STREET_NAMES:
        return clean_name

    if clean_name in PROTECTED_STREET_WORDS:
        return None

    from address_standardizer.tables import (
        WORD_ORDINALS,
        COMPOUND_ORDINALS,
        SECONDARY_UNITS,
        US_STATES,
    )
    from address_standardizer._patterns import ROUTE_PREFIXES

    if (
        clean_name in DIRECTIONALS
        or clean_name in DIRECTIONALS.values()
        or clean_name in STREET_SUFFIXES
        or clean_name in STREET_SUFFIXES.values()
        or clean_name in ROUTE_PREFIXES
        or clean_name in WORD_ORDINALS
        or clean_name in COMPOUND_ORDINALS
        or clean_name in SECONDARY_UNITS
        or clean_name in SECONDARY_UNITS.values()
        or clean_name in US_STATES
        or clean_name in US_STATES.values()
    ):
        return None

    n_len = len(clean_name)
    best_match: Optional[str] = None
    allowed_distance = min(max_distance, 1)
    min_dist = allowed_distance + 1

    for cand in sorted(COMMON_STREET_NAMES):
        if abs(len(cand) - n_len) <= allowed_distance:
            # Never mutate plural or singular variants of street names
            if (
                cand + "S" == clean_name
                or cand + "ES" == clean_name
                or clean_name + "S" == cand
                or clean_name + "ES" == cand
            ):
                continue
            if n_len < 5 and sorted(clean_name) != sorted(cand):
                continue
            d = damerau_levenshtein_distance(clean_name, cand)
            if d <= allowed_distance and d < min_dist:
                min_dist = d
                best_match = cand
                if d == 1:
                    break

    return best_match



def heal_postal_code_transposition(postal_code: str, state: Optional[str] = None) -> Optional[str]:
    """
    Detects and corrects adjacent digit transpositions in 5-digit US postal codes
    when cross-referenced against valid ZIP3-to-state mappings.
    """
    if not postal_code or not state:
        return None

    digits = re.sub(r"[^\d]", "", postal_code)
    if len(digits) < 5:
        return None

    zip5 = digits[:5]
    norm_st = state.strip().upper()
    expected_st = US_STATES.get(norm_st, norm_st)

    # Check if current zip already matches expected state
    curr_z3 = zip5[:3]
    if curr_z3 in ZIP3_TO_STATE and ZIP3_TO_STATE[curr_z3] == expected_st:
        return zip5

    # Test adjacent digit transpositions: (0,1), (1,2), (2,3), (3,4)
    char_list = list(zip5)
    candidates: List[str] = []

    for i in range(len(char_list) - 1):
        if char_list[i] != char_list[i + 1]:
            swapped = list(char_list)
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            cand_zip = "".join(swapped)
            cand_z3 = cand_zip[:3]
            if cand_z3 in ZIP3_TO_STATE and ZIP3_TO_STATE[cand_z3] == expected_st:
                candidates.append(cand_zip)

    if len(candidates) == 1:
        return candidates[0]

    return None


def heal_street_number_transposition(
    number_str: str,
    valid_ranges: Optional[List[Tuple[int, int]]] = None,
) -> Optional[str]:
    """
    Detects and corrects adjacent digit transpositions in street house numbers
    when cross-referenced against valid building number ranges.
    """
    if not number_str or not valid_ranges:
        return None

    digits = re.sub(r"[^\d]", "", number_str)
    if len(digits) < 2:
        return None

    val = int(digits)
    # If already within a valid range, no healing needed
    for low, high in valid_ranges:
        if low <= val <= high:
            return number_str

    # Test adjacent transpositions
    char_list = list(digits)
    candidates: List[str] = []
    for i in range(len(char_list) - 1):
        if char_list[i] != char_list[i + 1]:
            swapped = list(char_list)
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            cand_str = "".join(swapped)
            cand_val = int(cand_str)
            for low, high in valid_ranges:
                if low <= cand_val <= high:
                    if cand_str not in candidates:
                        candidates.append(cand_str)
                    break

    if len(candidates) == 1:
        m = re.match(r"^(\d+)(.*)$", number_str.strip())
        if m and m.group(2):
            return f"{candidates[0]}{m.group(2)}"
        return candidates[0]

    return None
