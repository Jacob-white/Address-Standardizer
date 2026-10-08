"""Latin American Address Grammar (MEX, BRA, COL, ARG, CHL).

Provides specialized parsing and normalization for:
- Mexico (MEX): Colonias, Fraccionamientos, Manzana/Lote, No. Ext/Int.
- Brazil (BRA): Logradouros (Rua, Avenida, etc.), Bairros, CEP formatting (01310-200).
- Colombia (COL): Carrera/Calle/Diagonal/Transversal with # XX-YY intersection syntax.
- Argentina (ARG): Calles, Avenidas, Pasajes, floor/dept (Piso/Depto), CPA 8-char postal codes.
- Chile (CHL): Comunas, Calles, Avenidas, Depto/Oficina, 7-digit postal codes.
"""

from __future__ import annotations

import re
from typing import ClassVar, Dict, List, Optional, Tuple

from address_standardizer._patterns import RE_COMMA_DOT
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
    split_intl_secondary_unit,
)
from address_standardizer.international.diacritics import (
    normalize_to_canonical_unicode,
)
from address_standardizer.international.romance import (
    _SEC_END,
    extract_units_from_part,
    make_strict_sec_regex,
    merge_units,
    parse_street2_unit,
)
from address_standardizer.tables import COUNTRY_MAP, GLOBAL_METRO_TO_COUNTRY

# Road type abbreviations for Latin America (Spanish & Portuguese)
LATAM_ROAD_TYPES: Dict[str, str] = {
    # Spanish
    "AVENIDA": "AVENIDA",
    "AV": "AV",
    "AVE": "AV",
    "BOULEVARD": "BLVD",
    "BLVD": "BLVD",
    "CALLE": "CALLE",
    "C": "CALLE",
    "CLLE": "CALLE",
    "CARRERA": "CRA",
    "CRA": "CRA",
    "CR": "CRA",
    "DIAGONAL": "DIAG",
    "DIAG": "DIAG",
    "TRANSVERSAL": "TRANSV",
    "TRANSV": "TRANSV",
    "CIRCULAR": "CIRC",
    "AUTOPISTA": "AUTOP",
    "PASEO": "PASEO",
    "CALZADA": "CALZ",
    "CALZ": "CALZ",
    "CAMINO": "CAMINO",
    "CARRETERA": "CTRA",
    "CTRA": "CTRA",
    "PASAJE": "PJE",
    "PJE": "PJE",
    "CERRADA": "CDA",
    "CDA": "CDA",
    "PROLONGACION": "PROL",
    "PROLONGACIÓN": "PROL",
    "PLAZA": "PZ",
    # Portuguese (Brazil)
    "RUA": "RUA",
    "R": "RUA",
    "ALAMEDA": "AL",
    "AL": "AL",
    "TRAVESSA": "TV",
    "TV": "TV",
    "RODOVIA": "ROD",
    "ROD": "ROD",
    "PRAÇA": "PRACA",
    "PRACA": "PRACA",
    "ESTRADA": "EST",
    "LARGO": "LARGO",
}

# Brazilian CEP: 12345-678 or 12345678
RE_BRA_CEP = re.compile(r"^\b(\d{5})-?(\d{3})\b$")

# Argentine CPA (Código Postal Argentino): e.g. C1024CWN or 4-digit 1024
RE_ARG_CPA = re.compile(r"^\b([A-Z]\d{4}[A-Z]{3}|\d{4})\b$", re.IGNORECASE)

# Colonia / Barrio prefix (Mexico / LATAM)
RE_COLONIA = re.compile(
    r"^\b(?:COL|COLONIA|BARRIO|BO|FRACC|FRACCIONAMIENTO|RESIDENCIAL|URB|URBANIZACION)\.?\s+(.+)$",
    re.IGNORECASE,
)

# Manzana / Lote pattern (Mexico)
RE_MANZANA_LOTE = re.compile(
    r"\b(?:MZ|MZA|MANZANA)\.?\s*([A-Za-z0-9\-]+)(?:[\s,]+(?:LT|LOTE)\.?\s*([A-Za-z0-9\-]+))?\b",
    re.IGNORECASE,
)

# Secondary unit indicators (Int, Ext, Piso, Depto, Apto, Bloco, Torre, etc.)
# Keywords are whole words: "INT" never matches inside "Internacional", "ESC" never inside "Escuela".
_LATAM_SEC_TYPES = (
    r"INTERIOR|INT|EXTERIOR|EXT|DEPARTAMENTO|DEPTO|DPTO|PISO|ESC|APARTAMENTO|APTO|APT|SUITE|STE|UNIT|BLOCO|BL"
    r"|SALA|CONJUNTO|CONJ|OFICINA|OF|TORRE|EDIFICIO|EDIF"
)
RE_LATAM_SEC = re.compile(rf"(?<!\w)({_LATAM_SEC_TYPES}){_SEC_END}([A-Za-z0-9\-]+)?", re.IGNORECASE)
RE_LATAM_SEC_STRICT = make_strict_sec_regex(_LATAM_SEC_TYPES)

# Floor/door like 2º B, 2o B, 2ª B, 2° B
# The ordinal marker is º/ª/° (optionally spaced) or a lowercase "o" glued to the number ("2o B"); a letter "o"
# after a space is a word ("12 Oeste", "5 Oriente"). The door/letter is at most 3 characters ("B", "IZQ").
RE_FLOOR_DOOR = re.compile(r"\b(\d+)(?:\s*[ºª°]\s*|o\s+)([A-Za-z0-9\-]{1,3})\b", re.IGNORECASE)


class LatinAmericaGrammar(CountryGrammar):
    """Regional grammar family for Latin America (MEX, BRA, COL, ARG, CHL)."""

    country_iso3: ClassVar[str] = "MEX"
    supported_countries: ClassVar[Tuple[str, ...]] = (
        "MEX", "MEXICO", "MX",
        "BRA", "BRAZIL", "BRASIL", "BR",
        "COL", "COLOMBIA", "CO",
        "ARG", "ARGENTINA", "AR",
        "CHL", "CHILE", "CL",
    )

    def normalize_postal_code(self, raw_code: str) -> str:
        """Normalize localized Latin American postal code."""
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().upper().split())

        # Brazilian CEP formatting: XXXXX-XXX
        m_bra = RE_BRA_CEP.match(clean)
        if m_bra:
            return f"{m_bra.group(1)}-{m_bra.group(2)}"

        # Argentine CPA: 8 uppercase chars or 4 digits
        m_arg = RE_ARG_CPA.match(clean)
        if m_arg:
            return m_arg.group(1).upper()

        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract (premise, street_number, thoroughfare) from Latin American address line."""
        if not street_line:
            return None, None, None

        line = street_line.strip()

        # Colombian numbered street with intersection syntax:
        # e.g. "Calle 72 No. 10-07" or "Carrera 7 # 71-21"
        if re.search(r"\b(?:NO\.?|#|N°|NUMERO)\s*\d", line, re.IGNORECASE):
            return None, None, line.upper()

        # Latin American / Spanish prefix format:
        # Road type + Name + Number: e.g. "Av. Insurgentes Sur 1602", "Calle Mayor 45", "Av. Providencia 123"
        m_prefix = re.match(r"^([A-Za-zÀ-ÿ\.]+)\s+(.*?)\s+(\d+[A-Za-z0-9\-\/]*)$", line)
        if m_prefix:
            prefix_cand = m_prefix.group(1).strip(".").upper()
            rest_name = m_prefix.group(2).strip(" ,.")
            st_num = m_prefix.group(3).strip().upper()
            if prefix_cand in LATAM_ROAD_TYPES:
                norm_prefix = LATAM_ROAD_TYPES[prefix_cand]
                st_name = f"{norm_prefix} {rest_name.upper()} {st_num}"
                return None, st_num, st_name

        return None, None, line

    def _resolve_country_iso(self, country_cand: Optional[str]) -> str:
        if not country_cand:
            return "MEX"
        c = country_cand.strip().upper()
        if c in ("MEX", "MEXICO", "MX"):
            return "MEX"
        if c in ("BRA", "BRAZIL", "BRASIL", "BR"):
            return "BRA"
        if c in ("COL", "COLOMBIA", "CO"):
            return "COL"
        if c in ("ARG", "ARGENTINA", "AR"):
            return "ARG"
        if c in ("CHL", "CHILE", "CL"):
            return "CHL"
        return "MEX"

    def parse(self, raw_tokens: List[str], metadata: dict) -> ParsedAddressComponents:
        s1_raw = metadata.get("street1", "")
        s2_raw = metadata.get("street2", "")
        city_raw = metadata.get("city", "")
        state_raw = metadata.get("state", "")
        postal_raw = metadata.get("postal_code", "")
        country_raw = metadata.get("country", self.country_iso3)
        country_iso = self._resolve_country_iso(country_raw)

        unit_type: Optional[str] = None
        unit_number: Optional[str] = None
        sec_units: List[str] = []
        dep_locality: Optional[str] = None
        street_line = s1_raw

        # Handle comma-delimited single string when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            if len(parts_comma) >= 2 and (
                parts_comma[-1].upper() in self.supported_countries
                or parts_comma[-1].upper() in COUNTRY_MAP
            ):
                country_iso = self._resolve_country_iso(parts_comma[-1])
                parts_comma = parts_comma[:-1]

            rem_parts: List[str] = []
            for part in parts_comma:
                # Check for Colonia / Barrio
                m_col = RE_COLONIA.match(part)
                if m_col:
                    dep_locality = m_col.group(1).strip()
                    continue

                # Check for Manzana / Lote
                m_mzl = RE_MANZANA_LOTE.search(part)
                if m_mzl:
                    sec_units.append(m_mzl.group(0).upper())
                    continue

                # Check for secondary units: "Int. 401", "Piso 4", "Depto B", "Apt 12"
                part, found_units = extract_units_from_part(part, RE_LATAM_SEC, RE_LATAM_SEC_STRICT)
                sec_units.extend(found_units)
                if not part:
                    continue

                # Check if entire part is a postal code
                if (
                    RE_BRA_CEP.match(part.strip())
                    or RE_ARG_CPA.match(part.strip())
                    or re.match(r"^\d{5,7}$", part.strip())
                ):
                    postal_raw = part.strip()
                    continue

                rem_parts.append(part)

            if len(rem_parts) >= 2:
                last_p = rem_parts[-1]
                # Check for "São Paulo - SP"
                m_city_st = re.match(r"^(.*?)\s*-\s*([A-Za-z]{2})$", last_p)
                if m_city_st and not state_raw:
                    city_raw = m_city_st.group(1).strip()
                    state_raw = m_city_st.group(2).strip()
                    rem_parts = rem_parts[:-1]

            if city_raw:
                if len(rem_parts) >= 2 and not dep_locality:
                    last_rem = rem_parts[-1].strip()
                    if " - " in last_rem:
                        p_dash = last_rem.split(" - ", 1)
                        num_part = p_dash[0].strip()
                        dep_locality = p_dash[1].strip()
                        street_line = f"{', '.join(rem_parts[:-1])} {num_part}".strip()
                    else:
                        dep_locality = last_rem
                        street_line = ", ".join(rem_parts[:-1])
                else:
                    street_line = ", ".join(rem_parts)
            elif len(rem_parts) >= 3:
                # e.g. "Av. Insurgentes Sur 1602", "03940 Ciudad de México", "CDMX"
                # OR "Carrera 7 # 71-21", "Bogotá 110221"
                # OR "Huérfanos 48", "Santiago", "Región Metropolitana 8320000"
                m_pc_last_start = re.match(r"^(\d{5}(?:-\d{3})?|[A-Z]\d{4}[A-Z]{3})\s+(.*)$", rem_parts[-1], re.IGNORECASE)
                m_pc_last_end = re.match(r"^(.*?)\s+(\d{5}(?:-\d{3})?|[A-Z]\d{4}[A-Z]{3}|\d{4,7})$", rem_parts[-1], re.IGNORECASE)
                if m_pc_last_start:
                    postal_raw = m_pc_last_start.group(1)
                    city_raw = m_pc_last_start.group(2)
                    street_line = ", ".join(rem_parts[:-1])
                elif m_pc_last_end:
                    loc_name = m_pc_last_end.group(1).strip()
                    postal_raw = m_pc_last_end.group(2).strip()
                    if any(kw in loc_name.upper() for kw in ("REGION", "REGIÓN", "PROVINCIA", "ESTADO", "DPTO")):
                        state_raw = loc_name
                        city_raw = rem_parts[-2].strip()
                        street_line = ", ".join(rem_parts[:-2])
                    else:
                        city_raw = loc_name
                        street_line = ", ".join(rem_parts[:-1])
                else:
                    p_last_clean = rem_parts[-1].strip().upper()
                    if p_last_clean in GLOBAL_METRO_TO_COUNTRY or p_last_clean in (
                        "BOGOTÁ", "BOGOTA", "SANTIAGO", "BUENOS AIRES", "LIMA", "CARACAS", "MONTEVIDEO", "QUITO"
                    ):
                        city_raw = rem_parts[-1].strip()
                        dep_locality = rem_parts[-2].strip()
                        street_line = ", ".join(rem_parts[:-2])
                    else:
                        state_raw = rem_parts[-1]
                        m_pc_mid_start = re.match(r"^(\d{5}(?:-\d{3})?|[A-Z]\d{4}[A-Z]{3})\s+(.*)$", rem_parts[-2], re.IGNORECASE)
                        m_pc_mid_end = re.match(r"^(.*?)\s+(\d{5}(?:-\d{3})?|[A-Z]\d{4}[A-Z]{3}|\d{4,7})$", rem_parts[-2], re.IGNORECASE)
                        if m_pc_mid_start:
                            postal_raw = m_pc_mid_start.group(1)
                            city_raw = m_pc_mid_start.group(2)
                        elif m_pc_mid_end:
                            city_raw = m_pc_mid_end.group(1)
                            postal_raw = m_pc_mid_end.group(2)
                        else:
                            city_raw = rem_parts[-2]
                        street_line = ", ".join(rem_parts[:-2])
            elif len(rem_parts) == 2:
                # e.g. "Balcarce 50", "C1064AAB Buenos Aires" OR "Carrera 7 # 71-21", "Bogotá 110221"
                m_pc_start = re.match(r"^(\d{5}(?:-\d{3})?|[A-Z]\d{4}[A-Z]{3}|\d{4,7})\s+(.*)$", rem_parts[1], re.IGNORECASE)
                m_pc_end = re.match(r"^(.*?)\s+(\d{5}(?:-\d{3})?|[A-Z]\d{4}[A-Z]{3}|\d{4,7})$", rem_parts[1], re.IGNORECASE)
                if m_pc_start:
                    postal_raw = m_pc_start.group(1)
                    city_raw = m_pc_start.group(2)
                elif m_pc_end:
                    city_raw = m_pc_end.group(1)
                    postal_raw = m_pc_end.group(2)
                else:
                    city_raw = rem_parts[1]
                street_line = rem_parts[0]
            elif len(rem_parts) == 1:
                p0 = rem_parts[0].strip().upper()
                if not city_raw and p0 in GLOBAL_METRO_TO_COUNTRY:
                    city_raw = rem_parts[0]
                    street_line = ""
                else:
                    street_line = rem_parts[0]

        # Handle secondary units in s2_raw or embedded in street_line
        s2_type: Optional[str] = None
        s2_number: Optional[str] = None
        if s2_raw:
            s2_type, s2_number = parse_street2_unit(s2_raw, RE_LATAM_SEC)

        # Check for Brazil " - " separator (e.g. "Avenida Paulista, 1578 - Bela Vista")
        if " - " in street_line:
            p_dash = street_line.split(" - ", 1)
            street_line = p_dash[0].strip()
            if not dep_locality:
                dep_locality = p_dash[1].strip()

        # A unit written at the end of the street line ("Avenida Estela 100 Int 4") or a floor/door ("2º B")
        street_line, inline_units = extract_units_from_part(
            street_line, RE_LATAM_SEC_STRICT, RE_LATAM_SEC_STRICT, allow_whole=False
        )
        sec_units.extend(inline_units)
        st1_base, st2_base = split_intl_secondary_unit(street_line, "")
        if st2_base and not (sec_units or s2_type or s2_number):
            st2_parts = st2_base.split(maxsplit=1)
            unit_type = st2_parts[0]
            unit_number = st2_parts[1] if len(st2_parts) > 1 else None
        else:
            if st2_base:
                sec_units.append(st2_base)
            unit_type, unit_number = merge_units(sec_units, s2_type, s2_number)

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
