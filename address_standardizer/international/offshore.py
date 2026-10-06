"""Offshore Financial Centers and Crown Dependencies Grammar (CYM, VGB, BMU, PAN)."""

import re
from typing import ClassVar, List, Optional, Tuple

from address_standardizer._patterns import (
    RE_COMMA_DOT,
    RE_NON_ALPHANUMERIC,
)
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
    split_intl_secondary_unit,
)
from address_standardizer.international.diacritics import normalize_to_canonical_unicode
from address_standardizer.tables import COUNTRY_MAP, DIRECTIONALS, STREET_SUFFIXES

RE_CYM_POSTCODE = re.compile(r"^(?:CYM[- ]*)?(?:KY([1-3])?[- ]*)?(\d{4})$", re.IGNORECASE)
RE_VGB_POSTCODE = re.compile(r"^(VG\d{4})$", re.IGNORECASE)
RE_BMU_POSTCODE = re.compile(r"^([A-Z]{2})\s*([A-Z0-9]{2})$", re.IGNORECASE)

RE_APARTADO = re.compile(r"\b(?:APARTADO|APDO)\.?\s*([A-Za-z0-9\-]+)\b", re.IGNORECASE)
RE_OFFSHORE_PO_BOX = re.compile(
    r"\b(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+(?:\s+[A-Z0-9\-]+)*)\b",
    re.IGNORECASE,
)

OFFSHORE_BUILDING_KEYWORDS = (
    "HOUSE",
    "CHAMBERS",
    "TOWER",
    "TORRE",
    "BUILDING",
    "COURT",
    "CENTRE",
    "CENTER",
    "PAVILION",
    "HALL",
    "MANSION",
    "PLAZA",
)

RE_OFFSHORE_BLDG_SPLIT = re.compile(
    r"^(.*?\b(?:" + "|".join(OFFSHORE_BUILDING_KEYWORDS) + r")\b)(?:\s+(.+))?$",
    re.IGNORECASE,
)


class OffshoreGrammar(CountryGrammar):
    """Offshore Financial Center address grammar with dual physical office complex and PO Box handling."""

    country_iso3: ClassVar[str] = "CYM"
    supported_countries: ClassVar[Tuple[str, ...]] = (
        "CYM",
        "CAYMAN",
        "CAYMAN ISLANDS",
        "VGB",
        "BRITISH VIRGIN ISLANDS",
        "BVI",
        "BMU",
        "BERMUDA",
        "PAN",
        "PANAMA",
    )

    def normalize_postal_code(self, raw_code: str) -> str:
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().upper().split())
        m_cym = RE_CYM_POSTCODE.match(clean)
        if m_cym:
            sec = m_cym.group(1) or "1"
            return f"KY{sec}-{m_cym.group(2)}"
        m_vgb = RE_VGB_POSTCODE.match(clean)
        if m_vgb:
            return m_vgb.group(1).upper()
        m_bmu = RE_BMU_POSTCODE.match(clean)
        if m_bmu:
            return f"{m_bmu.group(1).upper()} {m_bmu.group(2).upper()}"
        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not street_line:
            return None, None, None

        line = street_line.strip()
        premise: Optional[str] = None
        st_num: Optional[str] = None
        st_name: Optional[str] = None

        if "," in line:
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 2:
                premise = parts[0].upper()
                thoroughfare_part = parts[1]
                m_num = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", thoroughfare_part)
                if m_num:
                    st_num = m_num.group(1).upper()
                    st_name = f"{st_num} {self._normalize_street_tokens(m_num.group(2))}"
                else:
                    st_name = self._normalize_street_tokens(thoroughfare_part)
                return premise, st_num, st_name

        m_bldg = RE_OFFSHORE_BLDG_SPLIT.match(line)
        m_num = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", line)
        if m_bldg:
            premise = m_bldg.group(1).upper()
            rest = m_bldg.group(2)
            if rest:
                m_num_rest = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", rest)
                if m_num_rest:
                    st_num = m_num_rest.group(1).upper()
                    st_name = f"{st_num} {self._normalize_street_tokens(m_num_rest.group(2))}"
                else:
                    st_name = self._normalize_street_tokens(rest)
        elif m_num:
            st_num = m_num.group(1).upper()
            st_name = f"{st_num} {self._normalize_street_tokens(m_num.group(2))}"
        else:
            st_name = self._normalize_street_tokens(line)

        return premise, st_num, st_name

    def _normalize_street_tokens(self, text: str) -> str:
        if not text:
            return ""
        words = text.strip().split()
        norm_words: List[str] = []
        for w in words:
            w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
            if w_clean == "FORT":
                norm_words.append("FORT")
            elif w_clean == "SOUTH" and "CHURCH" in text.upper():
                norm_words.append("SOUTH")
            elif w_clean in STREET_SUFFIXES:
                norm_words.append(STREET_SUFFIXES[w_clean])
            elif w_clean in DIRECTIONALS:
                norm_words.append(DIRECTIONALS[w_clean])
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
        building_name: Optional[str] = None
        street_line = s1_raw

        # Handle comma-delimited single string when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            if len(parts_comma) >= 2 and (
                parts_comma[-1].upper() in self.supported_countries
                or parts_comma[-1].upper() in COUNTRY_MAP
                or parts_comma[-1].upper() in ("CAYMAN ISLANDS", "BVI", "BERMUDA", "PANAMA")
            ):
                parts_comma = parts_comma[:-1]

            rem_parts: List[str] = []
            for part in parts_comma:
                m_box = RE_OFFSHORE_PO_BOX.search(part)
                m_apdo = RE_APARTADO.search(part)
                if m_box:
                    unit_type = "PO BOX"
                    unit_number = m_box.group(1).upper()
                    continue
                elif m_apdo:
                    unit_type = "APARTADO"
                    unit_number = m_apdo.group(1).upper()
                    continue

                if (
                    RE_CYM_POSTCODE.match(part)
                    or RE_VGB_POSTCODE.match(part)
                    or RE_BMU_POSTCODE.match(part)
                ):
                    postal_raw = part
                    continue

                rem_parts.append(part)

            if len(rem_parts) >= 3:
                if rem_parts[-1].upper() in ("TORTOLA", "GRAND CAYMAN"):
                    state_raw = rem_parts[-1]
                    city_raw = rem_parts[-2]
                    street_line = ", ".join(rem_parts[:-2])
                elif any(kw in rem_parts[0].upper() for kw in OFFSHORE_BUILDING_KEYWORDS):
                    city_raw = rem_parts[2]
                    building_name = rem_parts[0].upper()
                    street_line = self._normalize_street_tokens(rem_parts[1])
                else:
                    city_raw = rem_parts[-1]
                    street_line = ", ".join(rem_parts[:-1])
            elif len(rem_parts) == 2:
                city_raw = rem_parts[-1]
                street_line = rem_parts[0]
            elif len(rem_parts) == 1:
                street_line = rem_parts[0]

        # Check secondary unit in s2_raw
        if s2_raw and not unit_number:
            m_box2 = RE_OFFSHORE_PO_BOX.search(s2_raw)
            m_apdo2 = RE_APARTADO.search(s2_raw)
            if m_box2:
                unit_type = "PO BOX"
                unit_number = m_box2.group(1).upper()
            elif m_apdo2:
                unit_type = "APARTADO"
                unit_number = m_apdo2.group(1).upper()
            else:
                unit_type = None
                unit_number = s2_raw.strip().upper()

        st1_base, st2_base = split_intl_secondary_unit(street_line, "")
        if "CHURCH" in street_line.upper():
            st1_base = self._normalize_street_tokens(street_line)

        if st2_base and not unit_number:
            m_box_s2 = RE_OFFSHORE_PO_BOX.search(st2_base)
            m_apdo_s2 = RE_APARTADO.search(st2_base)
            if m_box_s2:
                unit_type = "PO BOX"
                unit_number = m_box_s2.group(1).upper()
            elif m_apdo_s2:
                unit_type = "APARTADO"
                unit_number = m_apdo_s2.group(1).upper()
            else:
                s2_p = st2_base.split(maxsplit=1)
                unit_type = s2_p[0]
                unit_number = s2_p[1] if len(s2_p) > 1 else None

        # Check PO Box in st1_base
        m_box_in = RE_OFFSHORE_PO_BOX.search(st1_base)
        m_apdo_in = RE_APARTADO.search(st1_base)
        if m_box_in and not unit_number:
            unit_type = "PO BOX"
            unit_number = m_box_in.group(1).upper()
            st1_base = st1_base[:m_box_in.start()] + st1_base[m_box_in.end():]
            st1_base = st1_base.strip(" ,.-")
        elif m_apdo_in and not unit_number:
            unit_type = "APARTADO"
            unit_number = m_apdo_in.group(1).upper()
            st1_base = st1_base[:m_apdo_in.start()] + st1_base[m_apdo_in.end():]
            st1_base = st1_base.strip(" ,.-")

        premise, st_num, st_name = self.extract_premise_and_thoroughfare(st1_base)
        if not building_name:
            building_name = premise

        # If there is both a building name and thoroughfare, but NO PO Box/Apartado unit:
        # thoroughfare becomes street1, and premise becomes street2.
        if building_name and st_name and not unit_number and not unit_type:
            unit_number = building_name
            final_street_name = st_name
            final_building_name = None  # Prevents format_street1 from prepending building_name
        elif building_name and st_name and (unit_number or unit_type):
            final_street_name = st_name
            final_building_name = building_name
        else:
            final_street_name = st_name
            final_building_name = building_name

        norm_postal = self.normalize_postal_code(postal_raw)
        norm_city = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
        norm_state = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", state_raw).strip().upper())

        return ParsedAddressComponents(
            street_number=st_num,
            street_name=final_street_name,
            unit_type=unit_type,
            unit_number=unit_number,
            building_name=final_building_name,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )
