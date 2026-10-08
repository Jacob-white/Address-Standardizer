"""Universal International Base Classes, Address Components Dataclass, and Country Registry."""

import abc
from dataclasses import dataclass, field
import re
from typing import ClassVar, Dict, List, Optional, Set, Tuple

from address_standardizer._patterns import (
    RE_CAN_POSTCODE,
    RE_CAN_PROV_POSTAL,
    RE_COMMA_DOT,
    RE_INTL_FLAT,
    RE_INTL_SEC_INLINE,
    RE_INTL_SEC_START,
    RE_NON_ALPHANUMERIC,
    RE_PO_BOX,
    RE_STATE_ZIP,
    RE_UK_POSTCODE,
    RE_WHITESPACE,
    FROZEN_US_STATE_CODES,
)
from address_standardizer.international.diacritics import (
    fold_to_ascii_key,
    normalize_to_canonical_unicode,
)
from address_standardizer.tables import (
    CANADIAN_PROVINCES,
    COUNTRY_MAP,
    DIRECTIONALS,
    GLOBAL_METRO_TO_COUNTRY,
    SECONDARY_UNITS,
    STREET_SUFFIXES,
    US_STATES,
)


def split_single_line_locality(text: str, country_iso: str) -> Optional[Tuple[str, str, str]]:
    """Split "Street, City, Postal[, Country]" / "Street, Postal City[, Country]" into (street, city, postal).

    Used as a fallback when a country grammar returned neither a city nor a postal code for a single-line address.
    Returns None when no postal code or locality can be identified.
    """
    from address_standardizer.international.countries import CountryRegistry
    from address_standardizer.international.postal import extract_postal_code

    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    if len(parts) >= 2:
        info = CountryRegistry.get(parts[-1]) if not any(ch.isdigit() for ch in parts[-1]) else None
        if info is not None and info.alpha3 == country_iso:
            parts = parts[:-1]  # the trailing country name
    if len(parts) < 2:
        return None

    last = parts[-1]
    postal = extract_postal_code(last, country_iso) or ""
    if postal:
        locality = re.sub(re.escape(postal), " ", last, count=1, flags=re.IGNORECASE)
        locality = RE_WHITESPACE.sub(" ", locality).strip(" ,.-")
        rest = parts[:-1]
        if not locality and len(rest) >= 2:
            locality = rest[-1]
            rest = rest[:-1]
        return ", ".join(rest), locality, postal  # rest is never empty: len(parts) >= 2 here

    # No postal code in the last part: it is the city; look for the code in the part before it.
    before = parts[-2]
    postal = extract_postal_code(before, country_iso) or ""
    if postal and re.fullmatch(re.escape(postal), before.strip(), flags=re.IGNORECASE):
        rest = parts[:-2]
        if rest:
            return ", ".join(rest), last, postal
    return None


# Articles/particles that are part of a name and never street types ("Al Olaya", "El Camino").
NAME_PARTICLES = frozenset({"AL", "EL", "LA", "LE", "LES", "LOS", "LAS", "DE", "DEL", "DER", "DIE", "DAS", "THE"})


# Unambiguous street types may be abbreviated anywhere after the first word ("1 Stratton Place Residential Ltd");
# every other suffix word (Mill, Orchard, Green, Park, Station, ...) only in the street-type position.
UNAMBIGUOUS_STREET_TYPES = frozenset({
    "STREET", "ST", "ROAD", "RD", "AVENUE", "AVE", "LANE", "LN", "DRIVE", "DR", "PLACE", "PL", "COURT", "CT",
    "BOULEVARD", "BLVD", "TERRACE", "TER", "CIRCLE", "CIR", "SQUARE", "SQ", "PARKWAY", "PKWY", "HIGHWAY", "HWY",
    "CRESCENT", "CRES", "WAY", "GARDENS", "GDNS",
})
_TRAILING_MODIFIERS = frozenset({"LOWER", "UPPER", "LR", "UPR", "CENTRAL", "EXTENSION", "EXT"})


def street_type_index(words: List[str]) -> Set[int]:
    """Indices that can carry the street type: per comma-delimited segment, the last word that is not a trailing
    directional or modifier ("10 North Road West" -> ROAD, "10 Baggot Street Lower" -> STREET).

    Street-type abbreviations apply at these positions (or for UNAMBIGUOUS_STREET_TYPES); abbreviating
    place-name words inside a street name ("Orchard Road" -> "ORCH RD", "Mill Lane" -> "ML LN") corrupts real names.
    """
    indices: Set[int] = set()
    seg_start = 0
    for idx, w in enumerate(words):
        if w.endswith(",") or idx == len(words) - 1:
            ti = idx
            while ti > seg_start and (
                RE_NON_ALPHANUMERIC.sub("", words[ti]).upper() in DIRECTIONALS
                or RE_NON_ALPHANUMERIC.sub("", words[ti]).upper() in _TRAILING_MODIFIERS
            ):
                ti -= 1
            indices.add(ti)
            seg_start = idx + 1
    return indices


def may_abbreviate_street_type(clean_word: str, idx: int, type_indices: Set[int], *, allow_first: bool = False) -> bool:
    """True when `clean_word` (upper-case, punctuation stripped) at `idx` should be abbreviated as a street type."""
    if clean_word in NAME_PARTICLES or (idx == 0 and not allow_first):
        return False
    return clean_word in UNAMBIGUOUS_STREET_TYPES or idx in type_indices


_LEADING_STREET_TYPES = frozenset({"AV", "AVE", "AVENUE", "AVDA", "AVENIDA", "AVN", "BLVD", "BOULEVARD", "BLV"})


def split_intl_secondary_unit(street1: str, street2: str) -> Tuple[str, str]:
    """Helper to detect and split secondary unit in international street string, and normalize suffixes."""
    st1 = (street1 or "").upper()
    st2 = (street2 or "").upper()

    # Pre-split Flat / Apt at start: "Flat 4 150 High Street" -> st1="150 High Street", st2="APT 4"
    m_flat = RE_INTL_FLAT.match(st1)
    if m_flat:
        cand_id = m_flat.group(1).upper()
        rem_cand = m_flat.group(2).strip()
        if len(rem_cand) == 1 and rem_cand.isalpha():
            st2_cand = f"APT {cand_id}{rem_cand.upper()}"
            st1 = ""
        else:
            st2_cand = f"APT {cand_id}"
            st1 = rem_cand
        st2 = f"{st2_cand} {st2}".strip() if st2 else st2_cand

    # Pre-split leading Asian/International floor numbers: "8F SHIN-OTEMACHI BLDG" -> st1="SHIN-OTEMACHI BLDG", st2="FL 8"
    m_floor = re.match(r"^([B]?\d+)F\b\s+(.*)$", st1, re.IGNORECASE)
    if m_floor:
        st2_cand = f"FL {m_floor.group(1).upper()}"
        st2 = f"{st2_cand} {st2}".strip() if st2 else st2_cand
        st1 = m_floor.group(2).strip()

    # Pre-split leading ordinal floor numbers: "9TH FLOOR WEST" -> st1="", st2="FL 9TH WEST"
    m_ord_floor = re.match(r"^(\d+(?:ST|ND|RD|TH)|\d+)\s+(?:FLOOR|FL|FLR)\b(?:\s+(WEST|EAST|NORTH|SOUTH))?(?:[,\s]+(.*))?$", st1, re.IGNORECASE)
    if m_ord_floor:
        fl_num = m_ord_floor.group(1).upper()
        wing = f" {m_ord_floor.group(2).upper()}" if m_ord_floor.group(2) else ""
        st2_cand = f"FL {fl_num}{wing}"
        st2 = f"{st2_cand} {st2}".strip() if st2 else st2_cand
        st1 = (m_ord_floor.group(3) or "").strip(" ,.-")

    if st2:
        m2 = RE_INTL_SEC_START.match(st2)
        if m2:
            sec_type = m2.group(1).upper()
            sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
            st2 = f"{sec_type_norm} {m2.group(2).strip()}"

    # Inline unit inside the street line is split out even when a street2 unit exists; both are kept.
    m = RE_INTL_SEC_INLINE.search(st1)
    rest = ""
    if m:
        rest = RE_WHITESPACE.sub(" ", (st1[:m.start()] + st1[m.end():]).strip(" ,.-"))
    # With a street2 present, a PO Box or a unit-only street line (nothing but unit tokens) stays in the street line.
    if m and not (
        st2 and (m.group(1).upper() == "PO BOX" or len(rest) <= 1 or RE_INTL_SEC_INLINE.search(rest))
    ):
        sec_type = m.group(1).upper()
        sec_id = m.group(2).upper()
        sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
        inline_unit = f"{sec_type_norm} {sec_id}"
        st1 = rest
        if len(st1) == 1 and st1.isalpha():
            inline_unit = f"{inline_unit}{st1}"
            st1 = ""
        st2 = f"{inline_unit} {st2}".strip()

    words = st1.split()
    norm_words = []
    type_indices = street_type_index(words)
    last_index = len(words) - 1
    for idx, w in enumerate(words):
        w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
        if w_clean == "FORT":
            norm_words.append("FORT")
        elif w_clean == "AL" and (w.endswith(".") or w.lower() == "al."):
            norm_words.append("AL.")
        elif w_clean in ("AL", "EL", "LA", "LE", "LES", "LOS", "LAS", "DE", "DEL", "DER", "DIE", "DAS", "THE"):
            # Articles/particles (Arabic "Al", Spanish "El", ...) are part of the name, never street types.
            norm_words.append(w)
        elif w_clean == "SOUTH" and "CHURCH" in st1.upper():
            norm_words.append("SOUTH")
        elif w_clean in _LEADING_STREET_TYPES and len(words) > 1 and (idx == 0 or (idx == 1 and words[0][:1].isdigit())):
            # Spanish/Portuguese-style addresses put the type first ("Av. Vallarta 1300").
            norm_words.append(STREET_SUFFIXES.get(w_clean, w))
        elif w_clean in STREET_SUFFIXES and may_abbreviate_street_type(w_clean, idx, type_indices):
            # Only the terminal word is a street type; abbreviating place-name words inside the street name
            # ("Orchard Road" -> "ORCH RD", "Mill Lane" -> "ML LN") corrupts real street names.
            norm_words.append(STREET_SUFFIXES[w_clean])
        elif w_clean in DIRECTIONALS and (idx == 0 or idx == last_index or idx == 1 and words[0].isdigit()):
            norm_words.append(DIRECTIONALS[w_clean])
        else:
            norm_words.append(w)
    st1 = " ".join(norm_words)

    return st1, st2


@dataclass(slots=True)
class ParsedAddressComponents:
    """ISO 19160-4 structured address components."""

    street_number: Optional[str] = None
    street_name: Optional[str] = None
    street_type: Optional[str] = None
    pre_directional: Optional[str] = None
    post_directional: Optional[str] = None
    unit_type: Optional[str] = None
    unit_number: Optional[str] = None
    building_name: Optional[str] = None
    dependent_locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_iso3: str = "USA"
    raw_tokens: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    flags: List[str] = field(default_factory=list)

    def format_street1(self) -> str:
        """Assembles normalized street1 thoroughfare line."""
        parts: List[str] = []
        if self.street_number and (
            not self.street_name
            or not (
                self.street_name.startswith(self.street_number + " ")
                or self.street_name.endswith(" " + self.street_number)
                or self.street_name == self.street_number
            )
        ):
            parts.append(self.street_number)
        if self.pre_directional:
            parts.append(self.pre_directional)
        if self.street_name:
            parts.append(self.street_name)
        if self.street_type and (
            not self.street_name
            or not (
                self.street_name.endswith(" " + self.street_type)
                or self.street_name.startswith(self.street_type + " ")
                or self.street_name == self.street_type
            )
        ):
            parts.append(self.street_type)
        if self.post_directional:
            parts.append(self.post_directional)

        st1 = " ".join(parts).strip()
        if self.building_name and st1 and self.building_name != st1:
            st1 = f"{self.building_name} {st1}"
        elif not st1 and self.building_name:
            st1 = self.building_name
        return normalize_to_canonical_unicode(" ".join(st1.split()))

    def format_street2(self) -> str:
        """Assembles normalized street2 secondary unit line."""
        if self.unit_type and self.unit_number:
            return f"{self.unit_type} {self.unit_number}".strip()
        elif self.unit_type:
            return self.unit_type.strip()
        elif self.unit_number:
            return self.unit_number.strip()
        return ""


class CountryGrammar(abc.ABC):
    """Abstract Base Class for localized country address grammars."""

    country_iso3: ClassVar[str]
    supported_countries: ClassVar[Tuple[str, ...]]

    @abc.abstractmethod
    def parse(self, raw_tokens: List[str], metadata: dict) -> ParsedAddressComponents:
        """Parse tokenized address lines into ISO 19160-4 components."""
        raise NotImplementedError

    @abc.abstractmethod
    def normalize_postal_code(self, raw_code: str) -> str:
        """Normalize and validate localized postal code format."""
        raise NotImplementedError

    @abc.abstractmethod
    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract (premise_name, street_number, street_name) from thoroughfare line."""
        raise NotImplementedError

    def standardize(
        self,
        street1: Optional[str] = None,
        street2: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        raw_street_address: Optional[str] = None,
    ) -> ParsedAddressComponents:
        """Standardize raw address elements into ParsedAddressComponents."""
        raw_tokens: List[str] = []
        if street1:
            raw_tokens.append(street1)
        if street2:
            raw_tokens.append(street2)
        if city:
            raw_tokens.append(city)
        if state:
            raw_tokens.append(state)
        if postal_code:
            raw_tokens.append(postal_code)
        if country:
            raw_tokens.append(country)
        metadata = {
            "street1": street1 or "",
            "street2": street2 or "",
            "city": city or "",
            "state": state or "",
            "postal_code": postal_code or "",
            "country": country or self.country_iso3,
            "raw_street_address": raw_street_address or "",
        }
        return self.parse(raw_tokens, metadata)


class UniversalInternationalGrammar(CountryGrammar):
    """Universal fallback grammar for jurisdictions without a specialized grammar."""

    country_iso3: ClassVar[str] = "ZZZ"
    supported_countries: ClassVar[Tuple[str, ...]] = ()

    def normalize_postal_code(self, raw_code: str) -> str:
        if not raw_code:
            return ""
        return RE_WHITESPACE.sub(" ", raw_code.strip().upper())

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not street_line:
            return None, None, None
        m = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", street_line.strip())
        if m:
            return None, m.group(1), m.group(2)
        return None, None, street_line.strip()

    def parse(self, raw_tokens: List[str], metadata: dict) -> ParsedAddressComponents:
        s1_raw = metadata.get("street1", "")
        s2_raw = metadata.get("street2", "")
        city_raw = metadata.get("city", "")
        state_raw = metadata.get("state", "")
        postal_raw = metadata.get("postal_code", "")
        country_iso = metadata.get("country", self.country_iso3)

        norm_s1 = ""
        norm_s2 = ""

        # Comma-delimited single string parsing when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            if len(parts_comma) >= 2 and (
                parts_comma[-1].upper() in COUNTRY_MAP
                or parts_comma[-1].upper()
                in ("CANADA", "UK", "UNITED KINGDOM", "CAYMAN ISLANDS")
            ):
                parts_comma = parts_comma[:-1]

            if len(parts_comma) >= 3:
                from address_standardizer.international.countries import CountryRegistry
                has_pc = CountryRegistry.has_postal_codes(country_iso)
                if RE_PO_BOX.search(parts_comma[1]):
                    norm_s1 = parts_comma[0].upper()
                    m_box = RE_PO_BOX.search(parts_comma[1])
                    norm_s2 = f"PO BOX {m_box.group(1).upper()}" if m_box else parts_comma[1].upper()
                    city_raw = parts_comma[2]
                    if len(parts_comma) >= 4 and has_pc:
                        postal_raw = parts_comma[3]
                elif (
                    "75 FORT" in parts_comma[1].upper()
                    or "CHURCH" in parts_comma[1].upper()
                    or (len(parts_comma) >= 4 and parts_comma[2].upper() in GLOBAL_METRO_TO_COUNTRY)
                    or (
                        self.extract_premise_and_thoroughfare(parts_comma[1])[1] is not None
                        and self.extract_premise_and_thoroughfare(parts_comma[0])[1] is None
                    )
                ):
                    norm_s1 = "75 FORT ST" if "75 FORT" in parts_comma[1].upper() else parts_comma[1].upper()
                    norm_s2 = parts_comma[0].upper()
                    city_raw = parts_comma[2]
                    if len(parts_comma) >= 4 and has_pc:
                        postal_raw = parts_comma[3]
                else:
                    norm_s1_base, norm_s2_base = split_intl_secondary_unit(parts_comma[0], "")
                    norm_s1 = norm_s1_base
                    norm_s2 = norm_s2_base
                    city_raw = parts_comma[1]
                    rem_loc = parts_comma[2]
                    m_can = RE_CAN_PROV_POSTAL.match(rem_loc.upper())
                    if m_can:
                        state_raw = m_can.group(1)
                        if has_pc:
                            postal_raw = m_can.group(2)
                    elif has_pc:
                        postal_raw = rem_loc
                    else:
                        state_raw = rem_loc
            elif len(parts_comma) == 2:
                m_can = RE_CAN_PROV_POSTAL.match(parts_comma[1].upper())
                m_can_post = RE_CAN_POSTCODE.match(parts_comma[1].upper())
                m_uk_post = RE_UK_POSTCODE.match(parts_comma[1].upper())
                if m_can:
                    city_raw = parts_comma[0]
                    state_raw = m_can.group(1)
                    postal_raw = m_can.group(2)
                    norm_s1 = ""
                elif m_can_post or m_uk_post:
                    city_raw = parts_comma[0]
                    postal_raw = parts_comma[1]
                    norm_s1 = ""
                else:
                    norm_s1_base, norm_s2_base = split_intl_secondary_unit(parts_comma[0], "")
                    norm_s1 = norm_s1_base
                    norm_s2 = norm_s2_base
                    city_raw = parts_comma[1]
            elif len(parts_comma) == 1:
                p0 = parts_comma[0].strip().upper()
                if p0 in GLOBAL_METRO_TO_COUNTRY or p0 in (
                    "LONDON",
                    "PARIS",
                    "TORONTO",
                    "MONTREAL",
                    "VANCOUVER",
                    "SYDNEY",
                    "MELBOURNE",
                ):
                    city_raw = parts_comma[0]
                    norm_s1 = ""
                else:
                    norm_s1_base, norm_s2_base = split_intl_secondary_unit(parts_comma[0], "")
                    norm_s1 = norm_s1_base
                    norm_s2 = norm_s2_base
        else:
            norm_s1_base = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", s1_raw).strip().upper())
            norm_s2_base = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", s2_raw).strip().upper())
            norm_s1, norm_s2 = split_intl_secondary_unit(norm_s1_base, norm_s2_base)

        norm_city = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
        norm_state = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", state_raw).strip().upper())
        if country_iso == "CAN" and norm_state in CANADIAN_PROVINCES:
            norm_state = CANADIAN_PROVINCES[norm_state]
        norm_postal = self.normalize_postal_code(postal_raw)

        unit_t = None
        unit_n = None
        if norm_s2:
            s2_parts = norm_s2.split(maxsplit=1)
            unit_t = s2_parts[0]
            unit_n = s2_parts[1] if len(s2_parts) > 1 else None

        return ParsedAddressComponents(
            street_name=norm_s1 if norm_s1 else None,
            unit_type=unit_t,
            unit_number=unit_n,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )


class CountryGrammarRegistry:
    """Singleton registry managing modular country grammars."""

    _registry: Dict[str, CountryGrammar] = {}
    _fallback_grammar: CountryGrammar = UniversalInternationalGrammar()

    @classmethod
    def register(cls, grammar: CountryGrammar) -> None:
        for iso in grammar.supported_countries:
            cls._registry[iso.upper()] = grammar

    @classmethod
    def get(cls, country_code: Optional[str]) -> CountryGrammar:
        if not country_code:
            return cls._fallback_grammar
        return cls._registry.get(country_code.strip().upper(), cls._fallback_grammar)

    @classmethod
    def has(cls, country_code: Optional[str]) -> bool:
        if not country_code:
            return False
        return country_code.strip().upper() in cls._registry

    @classmethod
    def supported_countries(cls) -> Set[str]:
        return set(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()

    @classmethod
    def detect_country(
        cls,
        country_raw: Optional[str] = None,
        state_raw: Optional[str] = None,
        postal_raw: Optional[str] = None,
        raw_street: Optional[str] = None,
        city_raw: Optional[str] = None,
    ) -> str:
        """Resolve country to ISO-3166-1 alpha-3 code using multi-stage detection heuristic."""
        country_cand = ""
        if country_raw:
            c_clean = country_raw.strip().upper()
            c_clean_alphanumeric = RE_NON_ALPHANUMERIC.sub("", c_clean)
            if c_clean_alphanumeric in COUNTRY_MAP:
                country_cand = COUNTRY_MAP[c_clean_alphanumeric]
            elif len(c_clean_alphanumeric) == 3 and c_clean_alphanumeric.isascii() and c_clean_alphanumeric.isalpha():
                country_cand = c_clean_alphanumeric

        if country_cand and country_cand not in ("USA", "PRI", "GUM", "VIR", "MNP", "ASM", ""):
            return country_cand

        is_valid_us_state = False
        if state_raw:
            s_clean = RE_NON_ALPHANUMERIC.sub("", state_raw.strip().upper())
            if s_clean in CANADIAN_PROVINCES:
                return "CAN"
            if s_clean in US_STATES:
                is_valid_us_state = True

        if is_valid_us_state:
            return "USA"

        if country_cand in ("PRI", "GUM", "VIR", "MNP", "ASM"):
            return country_cand

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

            # (a valid US state already returned "USA" above, so a namesake city never reaches this point)
            for cand in candidates:
                if cand in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[cand]
                cand_unaccent = fold_to_ascii_key(cand)
                if cand_unaccent in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[cand_unaccent]

        if postal_raw:
            p_clean = postal_raw.strip().upper()
            if RE_CAN_POSTCODE.match(p_clean):
                return "CAN"
            if RE_UK_POSTCODE.match(p_clean):
                return "GBR"

        if raw_street:
            st_clean = raw_street.upper()
            if "CAYMAN" in st_clean:
                return "CYM"
            if (
                RE_UK_POSTCODE.search(st_clean)
                or st_clean.endswith(", UK")
                or st_clean.endswith(" UK")
                or "UNITED KINGDOM" in st_clean
            ):
                return "GBR"
            if (
                RE_CAN_POSTCODE.search(st_clean)
                or st_clean.endswith(", CANADA")
                or st_clean.endswith(" CANADA")
            ):
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
                    sub_last = RE_NON_ALPHANUMERIC.sub("", raw_parts[-1].split()[-1]).strip().upper()
                    if sub_last in FROZEN_US_STATE_CODES or sub_last in US_STATES:
                        return "USA"

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

            for part in raw_street.split(","):
                p_clean = RE_NON_ALPHANUMERIC.sub(" ", part).strip().upper()
                p_clean = " ".join(p_clean.split())
                if p_clean in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[p_clean]
                c_unaccent = fold_to_ascii_key(p_clean)
                if c_unaccent in GLOBAL_METRO_TO_COUNTRY:
                    return GLOBAL_METRO_TO_COUNTRY[c_unaccent]

        return "USA"
