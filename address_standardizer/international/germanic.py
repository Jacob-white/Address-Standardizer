"""Germanic and Nordic Address Grammar (DEU, AUT, CHE, NLD, DNK, SWE, NOR)."""

import re
from typing import ClassVar, List, Optional, Tuple

from address_standardizer._patterns import RE_COMMA_DOT
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
    split_intl_secondary_unit,
)
from address_standardizer.international.diacritics import normalize_to_canonical_unicode

# Dutch 4-digit + 2-letter postal code
RE_NLD_POSTCODE = re.compile(r"^([1-9]\d{3})\s*([A-Z]{2})$", re.IGNORECASE)
DISALLOWED_NLD_COMBOS = {"SA", "SD", "SS"}

# General 4 to 5 digit European postal codes
RE_EURO_POSTCODE = re.compile(r"^(\d{4,5})$")

# Inverted Germanic street number: Thoroughfare followed by number and optional addition
# e.g. "Musterstraße 12", "Am Hauptbahnhof 5a", "Friedrichstraße 43-45", "Keizersgracht 421-B", "Mannerheimintie 12 B"
RE_INVERTED_STREET_NUMBER = re.compile(
    r"^(.*?)\s+(\d+[A-Za-z0-9\-\/]*(?:\s+[A-Za-z]\b)?)(?:[\s,]+(?:Apt|Suite|Unit|Fl|Wohnung|Wg)\.?\s*([A-Za-z0-9\-]+))?$",
    re.IGNORECASE,
)

# Nordic floor and door indicators (e.g. "2. tv.", "st. th.", "1. mf.")
RE_NORDIC_FLOOR_DOOR = re.compile(
    r"[, ]+(\d+\.|\bst\.)\s*(tv|th|mf)\.?",
    re.IGNORECASE,
)

# Compound suffix patterns to protect
COMPOUND_SUFFIXES = (
    "straße",
    "strasse",
    "gasse",
    "weg",
    "platz",
    "allee",
    "damm",
    "ring",
    "chaussee",
    "ufer",
    "markt",
    "steig",
    "zeile",
    "tor",
    "brücke",
    "gatan",
    "vägen",
    "gade",
    "vei",
    "katu",
    "tie",
    "kuja",
    "väylä",
    "polku",
    "kaari",
    "ranta",
    "aukio",
)


def is_valid_dutch_postcode(raw_code: str) -> bool:
    """Validate Netherlands postal code (4 digits + 2 letters, excluding SA/SD/SS)."""
    if not raw_code:
        return False
    clean = " ".join(raw_code.strip().upper().split())
    m = RE_NLD_POSTCODE.match(clean)
    if not m:
        return False
    letters = m.group(2).upper()
    return letters not in DISALLOWED_NLD_COMBOS


class GermanicGrammar(CountryGrammar):
    """Germanic and Nordic address grammar with inverted house number ordering."""

    country_iso3: ClassVar[str] = "DEU"
    supported_countries: ClassVar[Tuple[str, ...]] = (
        "DEU",
        "GERMANY",
        "DEUTSCHLAND",
        "AUT",
        "AUSTRIA",
        "OESTERREICH",
        "CHE",
        "SWITZERLAND",
        "SCHWEIZ",
        "SUISSE",
        "SVIZZERA",
        "NLD",
        "NETHERLANDS",
        "HOLLAND",
        "DNK",
        "DENMARK",
        "SWE",
        "SWEDEN",
        "NOR",
        "NORWAY",
        "FIN",
        "FINLAND",
        "SUOMI",
    )

    def normalize_postal_code(self, raw_code: str) -> str:
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().upper().split())
        m_nld = RE_NLD_POSTCODE.match(clean)
        if m_nld:
            return f"{m_nld.group(1)} {m_nld.group(2).upper()}"
        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract inverted (premise, street_number, thoroughfare) from Germanic address line."""
        if not street_line:
            return None, None, None

        line = street_line.strip()
        m = RE_INVERTED_STREET_NUMBER.match(line)
        if m:
            thoroughfare = m.group(1).strip()
            st_num = m.group(2).strip()
            return None, st_num, thoroughfare

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
        street_line = s1_raw

        # Handle comma-delimited single string when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            # Strip trailing country if present
            if len(parts_comma) >= 2 and parts_comma[-1].upper() in self.supported_countries:
                parts_comma = parts_comma[:-1]

            if len(parts_comma) >= 2:
                last_part = parts_comma[-1].strip()
                # Check for "10115 Berlin", "1016 EK Amsterdam", or "111 35 Stockholm"
                m_post_city = re.match(
                    r"^(\d{4,5}(?:\s+[A-Z]{2})?|\d{3}\s+\d{2})\s+(.*)$",
                    last_part,
                    re.IGNORECASE,
                )
                if m_post_city:
                    postal_raw = m_post_city.group(1)
                    city_raw = m_post_city.group(2)
                    street_line = ", ".join(parts_comma[:-1])
                else:
                    city_raw = parts_comma[-1]
                    street_line = ", ".join(parts_comma[:-1])
            elif len(parts_comma) == 1:
                street_line = parts_comma[0]

        # Check for Nordic floor/door (e.g. "45, 2. tv.")
        m_nordic_fd = RE_NORDIC_FLOOR_DOOR.search(street_line)
        if m_nordic_fd:
            if not unit_number:
                unit_number = f"{m_nordic_fd.group(1)} {m_nordic_fd.group(2).lower()}"
            street_line = street_line[:m_nordic_fd.start()] + street_line[m_nordic_fd.end():]
            street_line = street_line.strip(" ,")

        # Extract secondary unit from s2_raw or street_line
        st1_base, st2_base = split_intl_secondary_unit(street_line, s2_raw)
        if st2_base and not unit_number:
            s2_parts = st2_base.split(maxsplit=1)
            unit_type = s2_parts[0]
            unit_number = s2_parts[1] if len(s2_parts) > 1 else None

        # Check for Dutch/Germanic addition like "421-B" -> number: 421, unit: APT B
        m_dash_unit = re.match(r"^(.*?)\s+(\d+)-([A-Za-z0-9]+)$", st1_base)
        # Check for Finnish/Nordic stairwell and apartment like "12 B 25"
        m_stair_apt = re.match(r"^(.*?)\s+(\d+)\s+([A-Za-z]\s*\d+)$", st1_base)
        if m_dash_unit and not unit_type and not unit_number:
            thoroughfare_stem = m_dash_unit.group(1).strip()
            st_num = m_dash_unit.group(2).strip()
            unit_type = "APT"
            unit_number = m_dash_unit.group(3).strip().upper()
            full_street = f"{thoroughfare_stem} {st_num}"
        elif m_stair_apt and not unit_type and not unit_number:
            thoroughfare_stem = m_stair_apt.group(1).strip()
            st_num = m_stair_apt.group(2).strip()
            unit_number = m_stair_apt.group(3).strip().upper()
            full_street = f"{thoroughfare_stem} {st_num}"
        else:
            _, st_num, thoroughfare_stem = self.extract_premise_and_thoroughfare(st1_base)
            if st_num and thoroughfare_stem:
                full_street = f"{thoroughfare_stem} {st_num}"
            else:
                full_street = st1_base

        norm_postal = self.normalize_postal_code(postal_raw)
        norm_city = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
        norm_state = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", state_raw).strip().upper())

        return ParsedAddressComponents(
            street_number=st_num,
            street_name=normalize_to_canonical_unicode(full_street) if full_street else None,
            unit_type=unit_type,
            unit_number=unit_number,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )
