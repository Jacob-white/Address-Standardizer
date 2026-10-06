"""Canada Post Bilingual English/French Address Grammar."""

import re
from typing import ClassVar, Dict, List, Optional, Tuple

from address_standardizer._patterns import (
    RE_CAN_POSTCODE,
    RE_CAN_PROV_POSTAL,
    RE_COMMA_DOT,
    RE_NON_ALPHANUMERIC,
    RE_PO_BOX,
    RE_WHITESPACE,
    clean_redundant_street_tail,
)
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
    split_intl_secondary_unit,
)
from address_standardizer.tables import CANADIAN_PROVINCES, DIRECTIONALS, STREET_SUFFIXES

RE_CAN_POSTCODE_EXACT = re.compile(
    r"^([A-CEGHJ-NPR-TVXY]\d[A-CEGHJ-NPR-TV-Z])\s*(\d[A-CEGHJ-NPR-TV-Z]\d)$",
    re.IGNORECASE,
)

FRENCH_STREET_TYPES: Dict[str, str] = {
    "RUE": "RUE",
    "BOULEVARD": "BD",
    "BD": "BD",
    "BLVD": "BD",
    "AVENUE": "AV",
    "AV": "AV",
    "AVE": "AV",
    "CHEMIN": "CH",
    "CH": "CH",
    "CROISSANT": "CROIS",
    "CROIS": "CROIS",
    "ROUTE": "RTE",
    "RTE": "RTE",
    "MONTEE": "MTE",
    "MONTÉE": "MTE",
    "MTE": "MTE",
    "ALLEE": "ALLEE",
    "ALLÉE": "ALLEE",
    "PLACE": "PL",
    "PL": "PL",
    "COTE": "COTE",
    "CÔTE": "COTE",
    "IMPASSE": "IMP",
    "IMP": "IMP",
    "PROMENADE": "PROM",
    "PROM": "PROM",
    "TERRASSE": "TERR",
    "TERR": "TERR",
    "RANG": "RG",
    "RG": "RG",
    "CARREFOUR": "CARREF",
    "SQUARE": "SQ",
}

FRENCH_DIRECTIONS: Dict[str, str] = {
    "OUEST": "O",
    "EST": "E",
    "NORD": "N",
    "SUD": "S",
    "NORD-EST": "NE",
    "NORDEST": "NE",
    "NORD-OUEST": "NO",
    "NORDOUEST": "NO",
    "SUD-EST": "SE",
    "SUDEST": "SE",
    "SUD-OUEST": "SO",
    "SUDOUEST": "SO",
}

RURAL_DELIVERY_MODES: Dict[str, str] = {
    "RR": "RR",
    "RURAL ROUTE": "RR",
    "SS": "SS",
    "SUBURBAN SERVICE": "SS",
    "MR": "MR",
    "MOBILE ROUTE": "MR",
    "STN MAIN": "STN MAIN",
    "STATION MAIN": "STN MAIN",
    "COMP": "COMP",
    "COMPARTMENT": "COMP",
    "CP": "PO BOX",
    "CASE POSTALE": "PO BOX",
}


def is_valid_canadian_postal_code(raw_code: str) -> bool:
    """Validate Canadian postal code against Canada Post FSA/LDU specification."""
    if not raw_code:
        return False
    clean = " ".join(raw_code.strip().upper().split())
    m = RE_CAN_POSTCODE_EXACT.match(clean)
    if not m:
        return False
    # Characters D, F, I, O, Q, U and initial W, Z are prohibited by regex [A-CEGHJ-NPR-TVXY]
    return True


class CanadaGrammar(CountryGrammar):
    """Canada Post compliant bilingual English/French address grammar."""

    country_iso3: ClassVar[str] = "CAN"
    supported_countries: ClassVar[Tuple[str, ...]] = ("CAN", "CANADA")

    def normalize_postal_code(self, raw_code: str) -> str:
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().upper().split())
        m = RE_CAN_POSTCODE_EXACT.match(clean)
        if m:
            return f"{m.group(1).upper()} {m.group(2).upper()}"
        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not street_line:
            return None, None, None

        line = street_line.strip()

        # Check Rural Route / Delivery modes
        m_rr = re.match(
            r"^(RR|RURAL\s+ROUTE|SS|MR|STN\s+MAIN|COMP|CP|CASE\s+POSTALE)\s*#?\s*([A-Za-z0-9\-]+)?(.*)$",
            line,
            re.IGNORECASE,
        )
        if m_rr:
            mode_raw = m_rr.group(1).upper()
            mode_norm = RURAL_DELIVERY_MODES.get(mode_raw, mode_raw)
            mode_num = m_rr.group(2) or ""
            return None, None, f"{mode_norm} {mode_num}".strip()

        # Standard civic address
        m_num = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", line)
        if m_num:
            st_num = m_num.group(1).upper()
            rest = m_num.group(2).strip()
            st_name = self._normalize_bilingual_street(rest)
            return None, st_num, st_name

        return None, None, self._normalize_bilingual_street(line)

    def _normalize_bilingual_street(self, text: str) -> str:
        if not text:
            return ""
        words = text.strip().split()
        if not words:
            return ""

        # Check French prefix type: "rue Saint-Denis", "boulevard René-Lévesque Ouest"
        first_clean = RE_NON_ALPHANUMERIC.sub("", words[0]).upper()
        if first_clean in FRENCH_STREET_TYPES:
            prefix_norm = FRENCH_STREET_TYPES[first_clean]
            rest_words = words[1:]
            norm_rest: List[str] = []
            for w in rest_words:
                w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
                if w_clean in FRENCH_DIRECTIONS:
                    norm_rest.append(FRENCH_DIRECTIONS[w_clean])
                elif w_clean in DIRECTIONALS:
                    norm_rest.append(DIRECTIONALS[w_clean])
                else:
                    norm_rest.append(w.upper())
            return f"{prefix_norm} {' '.join(norm_rest)}"

        # English suffix type: "King Street West"
        norm_words: List[str] = []
        for w in words:
            w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
            if w_clean in STREET_SUFFIXES:
                norm_words.append(STREET_SUFFIXES[w_clean])
            elif w_clean in DIRECTIONALS:
                norm_words.append(DIRECTIONALS[w_clean])
            elif w_clean in FRENCH_DIRECTIONS:
                norm_words.append(FRENCH_DIRECTIONS[w_clean])
            else:
                norm_words.append(w.upper())
        return " ".join(norm_words)

    def parse(self, raw_tokens: List[str], metadata: dict) -> ParsedAddressComponents:
        s1_raw = metadata.get("street1", "")
        s2_raw = metadata.get("street2", "")
        city_raw = metadata.get("city", "")
        state_raw = metadata.get("state", "")
        postal_raw = metadata.get("postal_code", "")
        country_iso = metadata.get("country", self.country_iso3)

        unit_type: Optional[str] = None
        unit_number: Optional[str] = None

        street_line = s1_raw

        # Handle comma-delimited single string when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            if len(parts_comma) >= 2 and parts_comma[-1].upper() in ("CANADA", "CAN"):
                parts_comma = parts_comma[:-1]

            if len(parts_comma) >= 2:
                last_part = parts_comma[-1].upper()
                m_prov_post = RE_CAN_PROV_POSTAL.match(last_part)
                m_post = RE_CAN_POSTCODE.match(last_part)
                if m_prov_post:
                    state_raw = m_prov_post.group(1)
                    postal_raw = m_prov_post.group(2)
                    city_raw = parts_comma[-2]
                    street_line = ", ".join(parts_comma[:-2])
                elif m_post:
                    postal_raw = parts_comma[-1]
                    city_raw = parts_comma[-2]
                    street_line = ", ".join(parts_comma[:-2])
                else:
                    city_raw = parts_comma[-1]
                    street_line = ", ".join(parts_comma[:-1])
            elif len(parts_comma) == 1:
                street_line = parts_comma[0]

        # Extract trailing postal code and province from street_line if not provided
        if not postal_raw and street_line:
            m_tail_pc = re.search(r"(?:,\s*|\s+)([A-CEGHJ-NPR-TVXY]\d[A-CEGHJ-NPR-TV-Z]\s*\d[A-CEGHJ-NPR-TV-Z]\d)\s*$", street_line, re.IGNORECASE)
            if m_tail_pc:
                postal_raw = m_tail_pc.group(1)

        if not state_raw and street_line:
            m_tail_prov = re.search(r"(?:,\s*|\s+)([A-Z]{2})\s*(?:[A-CEGHJ-NPR-TVXY]\d[A-CEGHJ-NPR-TV-Z]\s*\d[A-CEGHJ-NPR-TV-Z]\d)?\s*$", street_line, re.IGNORECASE)
            if m_tail_prov and m_tail_prov.group(1).upper() in CANADIAN_PROVINCES:
                state_raw = m_tail_prov.group(1).upper()

        # Clean redundant city, province, country, and postal code from street_line and s2_raw
        street_line = clean_redundant_street_tail(street_line, city=city_raw, state=state_raw, postal_code=postal_raw)
        if s2_raw:
            s2_raw = clean_redundant_street_tail(s2_raw, city=city_raw, state=state_raw, postal_code=postal_raw)

        st1_base, st2_base = split_intl_secondary_unit(street_line, s2_raw)
        if st2_base:
            s2_parts = st2_base.split(maxsplit=1)
            unit_type = s2_parts[0]
            unit_number = s2_parts[1] if len(s2_parts) > 1 else None

        # Check for PO Box in st1_base
        m_box = RE_PO_BOX.search(st1_base)
        if m_box and not unit_type:
            unit_type = "PO BOX"
            unit_number = m_box.group(1).upper()
            st1_base = st1_base[:m_box.start()] + st1_base[m_box.end():]
            st1_base = st1_base.strip(" ,.-")

        _, st_num, st_name = self.extract_premise_and_thoroughfare(st1_base)

        # Normalize Province
        norm_state = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", state_raw).strip().upper())
        if norm_state in CANADIAN_PROVINCES:
            norm_state = CANADIAN_PROVINCES[norm_state]

        norm_city = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
        norm_postal = self.normalize_postal_code(postal_raw)

        return ParsedAddressComponents(
            street_number=st_num,
            street_name=st_name,
            unit_type=unit_type,
            unit_number=unit_number,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )
