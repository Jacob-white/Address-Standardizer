"""Romance and Latin American Address Grammar (FRA, ESP, ITA, PRT, MEX, COL, ARG, BRA)."""

import re
from typing import ClassVar, Dict, List, Optional, Tuple

from address_standardizer._patterns import RE_COMMA_DOT
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
    split_intl_secondary_unit,
)
from address_standardizer.international.diacritics import normalize_to_canonical_unicode
from address_standardizer.tables import COUNTRY_MAP, GLOBAL_METRO_TO_COUNTRY

# Road type abbreviations for Romance languages
ROMANCE_ROAD_TYPES: Dict[str, str] = {
    "AVENIDA": "AVENIDA",
    "AV": "AV",
    "AVE": "AV",
    "BOULEVARD": "BD",
    "BLVD": "BD",
    "BD": "BD",
    "CALLE": "CALLE",
    "C": "CALLE",
    "CLLE": "CALLE",
    "CARRERA": "CRA",
    "CRA": "CRA",
    "CR": "CRA",
    "RUE": "RUE",
    "RUA": "RUA",
    "VIA": "VIA",
    "ALLEE": "ALLEE",
    "ALLÉE": "ALLEE",
    "PLACE": "PL",
    "PLAZA": "PZ",
    "PIAZZA": "PZ",
    "PRAÇA": "PRACA",
    "PRACA": "PRACA",
    "PASEO": "PASEO",
    "CALZADA": "CALZ",
    "CALZ": "CALZ",
    "CAMINO": "CAMINO",
    "CARRETERA": "CTRA",
    "CTRA": "CTRA",
    "DIAGONAL": "DIAG",
    "DIAG": "DIAG",
    "TRANSVERSAL": "TRANSV",
}

# French road type mappings
FRENCH_ROAD_TYPES: Dict[str, str] = {
    "BOULEVARD": "BD",
    "BD": "BD",
    "BLVD": "BD",
    "AVENUE": "AV",
    "AV": "AV",
    "AVE": "AV",
    "RUE": "RUE",
    "ALLEE": "ALLEE",
    "ALLÉE": "ALLEE",
    "PLACE": "PL",
    "IMPASSE": "IMP",
    "IMP": "IMP",
}

# Brazilian CEP: 12345-678 or 12345678
RE_BRA_CEP = re.compile(r"^\b(\d{5})-?(\d{3})\b$")

# Colonia / Barrio prefix
RE_COLONIA = re.compile(
    r"^\b(?:COL|COLONIA|BARRIO|BO|FRACC|FRACCIONAMIENTO)\.?\s+(.+)$", re.IGNORECASE
)

# Secondary unit indicators (Int, Piso, Esc, Apt, Depto)
RE_ROMANCE_SEC = re.compile(
    r"\b(INT|INTERIOR|DEPTO|DEPARTAMENTO|PISO|ESC|ESCALIER|BAT|BATIMENT|BÂTIMENT|ETAGE|ÉTAGE|PIANO|APT|APARTMENT|SUITE|STE|UNIT)\.?\s*([A-Za-z0-9\-]+)?",
    re.IGNORECASE,
)

# Floor/door like 2º B, 2o B, 2ª B, 2° B
# The ordinal marker is º/ª/° (optionally spaced) or a lowercase "o" glued to the number ("2o B"); a letter "o"
# after a space is a word ("12 Oeste", "5 Oriente"). The door/letter is at most 3 characters ("B", "IZQ").
RE_FLOOR_DOOR = re.compile(r"\b(\d+)(?:\s*[ºª°]\s*|o\s+)([A-Za-z0-9\-]{1,3})\b", re.IGNORECASE)


class RomanceGrammar(CountryGrammar):
    """Romance and Latin American address grammar with prefix road types and colonias."""

    country_iso3: ClassVar[str] = "FRA"
    supported_countries: ClassVar[Tuple[str, ...]] = (
        "FRA",
        "FRANCE",
        "ESP",
        "SPAIN",
        "ESPANA",
        "ITA",
        "ITALY",
        "ITALIA",
        "PRT",
        "PORTUGAL",
        "MEX",
        "MEXICO",
        "COL",
        "COLOMBIA",
        "ARG",
        "ARGENTINA",
        "BRA",
        "BRAZIL",
        "BRASIL",
    )

    def normalize_postal_code(self, raw_code: str) -> str:
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().upper().split())
        m_bra = RE_BRA_CEP.match(clean)
        if m_bra:
            return f"{m_bra.group(1)}-{m_bra.group(2)}"
        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not street_line:
            return None, None, None

        line = street_line.strip()

        # Check French number-first format: "142 Boulevard Saint-Germain"
        m_fr = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+([A-Za-zÀ-ÿ]+)\s+(.*)$", line)
        if m_fr:
            st_num = m_fr.group(1).upper()
            road_type_cand = m_fr.group(2).upper()
            rest = m_fr.group(3).strip()
            if road_type_cand in FRENCH_ROAD_TYPES:
                norm_type = FRENCH_ROAD_TYPES[road_type_cand]
                st_name = f"{norm_type} {rest.strip(' ,.').upper()}"
                return None, st_num, st_name

        # Check Latin American numbered street: "Calle 72 No. 10-07" or "Calle 72 # 10-07"
        if re.search(r"\b(?:NO\.?|#)\s*\d", line, re.IGNORECASE):
            return None, None, line.upper()

        # Latin American / Spanish prefix format: "Av. Insurgentes Sur 1602" or "Calle Mayor 45"
        # Road type + Name + Number
        m_es = re.match(r"^([A-Za-zÀ-ÿ\.]+)\s+(.*?)\s+(\d+[A-Za-z0-9\-\/]*)$", line)
        if m_es:
            prefix_cand = m_es.group(1).strip(".").upper()
            rest_name = m_es.group(2).strip(" ,.")
            st_num = m_es.group(3).strip().upper()
            if prefix_cand in ROMANCE_ROAD_TYPES:
                norm_prefix = ROMANCE_ROAD_TYPES[prefix_cand]
                st_name = f"{norm_prefix} {rest_name.upper()} {st_num}"
                return None, st_num, st_name

        return None, None, line

    def parse(self, raw_tokens: List[str], metadata: dict) -> ParsedAddressComponents:
        s1_raw = metadata.get("street1", "")
        s2_raw = metadata.get("street2", "")
        city_raw = metadata.get("city", "")
        state_raw = metadata.get("state", "")
        postal_raw = metadata.get("postal_code", "")
        country_iso = metadata.get("country", self.country_iso3)

        unit_type: Optional[str] = None
        unit_number: Optional[str] = None
        dep_locality: Optional[str] = None
        street_line = s1_raw

        # Handle comma-delimited single string when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            if len(parts_comma) >= 2 and (
                parts_comma[-1].upper() in self.supported_countries
                or parts_comma[-1].upper() in COUNTRY_MAP
                or parts_comma[-1].upper()
                in ("USA", "US", "UNITED STATES", "CANADA", "UK", "UNITED KINGDOM", "FRANCE", "SPAIN", "MEXICO", "COLOMBIA", "ARGENTINA", "BRAZIL")
            ):
                parts_comma = parts_comma[:-1]

            # Scan from right for State / Postal / City
            sec_units: List[str] = []
            rem_parts: List[str] = []
            for part in parts_comma:
                # Check for Colonia
                m_col = RE_COLONIA.match(part)
                if m_col:
                    dep_locality = m_col.group(1).strip()
                    continue

                # Check for secondary units: "Int. 401", "Esc. B", "Apt 12"
                m_sec = RE_ROMANCE_SEC.search(part)
                m_fd = RE_FLOOR_DOOR.search(part)
                if m_sec:
                    sec_t = m_sec.group(1).upper()
                    sec_n = m_sec.group(2) or ""
                    sec_units.append(f"{sec_t} {sec_n.upper()}".strip())
                    continue
                elif m_fd:
                    sec_units.append(f"{m_fd.group(1)} {m_fd.group(2).upper()}")
                    continue

                # Check if entire part is a postal code
                if RE_BRA_CEP.match(part.strip()) or re.match(r"^\d{5}(?:-\d{3})?$", part.strip()):
                    postal_raw = part.strip()
                    continue

                rem_parts.append(part)

            if sec_units:
                unit_number = " ".join(sec_units)
                unit_type = None

            if len(rem_parts) >= 2:
                last_p = rem_parts[-1]
                m_city_st = re.match(r"^(.*?)\s*-\s*([A-Za-z]{2})$", last_p)
                if m_city_st and not state_raw:
                    city_raw = m_city_st.group(1).strip()
                    state_raw = m_city_st.group(2).strip()
                    rem_parts = rem_parts[:-1]

            if city_raw:
                street_line = ", ".join(rem_parts)
            elif len(rem_parts) >= 3:
                # e.g. "Av. Insurgentes Sur 1602", "03940 Ciudad de México", "CDMX"
                # OR "142 Boulevard Saint-Germain", "Quartier Latin", "75006 Paris"
                m_pc_last = re.match(r"^(\d{5}(?:-\d{3})?)\s+(.*)$", rem_parts[-1])
                if m_pc_last:
                    postal_raw = m_pc_last.group(1)
                    city_raw = m_pc_last.group(2)
                    street_line = ", ".join(rem_parts[:-1])
                else:
                    state_raw = rem_parts[-1]
                    m_pc = re.match(r"^(\d{5}(?:-\d{3})?)\s+(.*)$", rem_parts[-2])
                    if m_pc:
                        postal_raw = m_pc.group(1)
                        city_raw = m_pc.group(2)
                    else:
                        city_raw = rem_parts[-2]
                    street_line = ", ".join(rem_parts[:-2])
            elif len(rem_parts) == 2:
                # e.g. "Calle Mayor 45", "28013 Madrid"
                m_pc = re.match(r"^(\d{5}(?:-\d{3})?)\s+(.*)$", rem_parts[1])
                if m_pc:
                    postal_raw = m_pc.group(1)
                    city_raw = m_pc.group(2)
                else:
                    city_raw = rem_parts[1]
                street_line = rem_parts[0]
            elif len(rem_parts) == 1:
                p0 = rem_parts[0].strip().upper()
                if not city_raw and (p0 in GLOBAL_METRO_TO_COUNTRY or p0 in (
                    "PARIS",
                    "MADRID",
                    "ROME",
                    "ROMA",
                    "BOGOTA",
                    "BOGOTÁ",
                    "BUENOS AIRES",
                    "SAO PAULO",
                    "SÃO PAULO",
                    "RIO DE JANEIRO",
                )):
                    city_raw = rem_parts[0]
                    street_line = ""
                else:
                    street_line = rem_parts[0]

        # Handle secondary units in s2_raw or embedded in street_line
        if s2_raw and not unit_number:
            m_fd = RE_FLOOR_DOOR.search(s2_raw)
            m_secs = list(RE_ROMANCE_SEC.finditer(s2_raw))
            if "," not in s2_raw and len(m_secs) > 1:
                sec_items = []
                for m in m_secs:
                    sec_t = m.group(1).upper()
                    sec_n = m.group(2) or ""
                    sec_items.append(f"{sec_t} {sec_n.upper()}".strip())
                unit_number = " ".join(sec_items)
                unit_type = None
            elif m_fd:
                unit_number = f"{m_fd.group(1)} {m_fd.group(2).upper()}"
            elif m_secs:
                m_sec = m_secs[0]
                unit_type = m_sec.group(1).upper()
                unit_number = m_sec.group(2).upper() if m_sec.group(2) else None
            else:
                unit_number = s2_raw.strip().upper()

        # Check for Brazil " - " separator before split_intl_secondary_unit
        if " - " in street_line:
            p_dash = street_line.split(" - ", 1)
            street_line = p_dash[0].strip()
            if not dep_locality:
                dep_locality = p_dash[1].strip()

        st1_base, st2_base = split_intl_secondary_unit(street_line, "")
        if st2_base and not unit_number:
            s2_p = st2_base.split(maxsplit=1)
            unit_type = s2_p[0]
            unit_number = s2_p[1] if len(s2_p) > 1 else None

        # Check floor/door in st1_base: "Calle Mayor 45 2º B"
        m_fd_inline = RE_FLOOR_DOOR.search(st1_base)
        if m_fd_inline:
            if not unit_number:
                unit_number = f"{m_fd_inline.group(1)} {m_fd_inline.group(2).upper()}"
            st1_base = st1_base[:m_fd_inline.start()] + st1_base[m_fd_inline.end():]
            st1_base = st1_base.strip(" ,.-")

        # Normalize thoroughfare
        _, st_num, thoroughfare = self.extract_premise_and_thoroughfare(st1_base)

        norm_postal = self.normalize_postal_code(postal_raw)
        norm_city = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
        norm_state = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", state_raw).strip().upper())
        norm_dep_loc = normalize_to_canonical_unicode(dep_locality.upper()) if dep_locality else None

        return ParsedAddressComponents(
            street_number=st_num,
            street_name=normalize_to_canonical_unicode(thoroughfare) if thoroughfare else None,
            unit_type=unit_type,
            unit_number=unit_number,
            dependent_locality=norm_dep_loc,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )
