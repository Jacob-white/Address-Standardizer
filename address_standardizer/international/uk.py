from dataclasses import dataclass
import re
from typing import ClassVar, List, Optional, Set, Tuple

from address_standardizer._patterns import (
    RE_COMMA_DOT,
    RE_INTL_FLAT,
    RE_INTL_SEC_INLINE,
    RE_INTL_SEC_START,
    RE_NON_ALPHANUMERIC,
    RE_WHITESPACE,
)
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
)
from address_standardizer.tables import DIRECTIONALS, SECONDARY_UNITS, STREET_SUFFIXES


@dataclass(slots=True)
class UKParsedAddressComponents(ParsedAddressComponents):
    """Royal Mail PAF / BS 7666 structured component formatter."""

    def format_street1(self) -> str:
        """Formats street1 as numbered thoroughfare delivery line."""
        if self.street_number and self.street_name:
            parts = [self.street_number]
            if self.pre_directional:
                parts.append(self.pre_directional)
            parts.append(self.street_name)
            if self.street_type and not (
                self.street_name.endswith(" " + self.street_type)
                or self.street_name.startswith(self.street_type + " ")
                or self.street_name == self.street_type
            ):
                parts.append(self.street_type)
            if self.post_directional:
                parts.append(self.post_directional)
            return " ".join(parts).strip()
        return ParsedAddressComponents.format_street1(self)

    def format_street2(self) -> str:
        """Formats street2 combining secondary unit and premise name."""
        sec = ParsedAddressComponents.format_street2(self)
        if self.building_name and self.street_number:
            if sec:
                return f"{sec} {self.building_name}".strip()
            return self.building_name.strip()
        return sec

RE_UK_POSTCODE_EXACT = re.compile(
    r"^(GIR|[A-Z]{1,2}[0-9][A-Z0-9]?)\s*([0-9][A-Z]{2})$", re.IGNORECASE
)
RE_UK_POSTCODE_SEARCH = re.compile(
    r"\b(GIR\s*0AA|[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2})\b", re.IGNORECASE
)

# Royal Mail Post Towns
UK_POST_TOWNS: Set[str] = {
    "ABERDEEN",
    "ARMAGH",
    "BATH",
    "BELFAST",
    "BIRMINGHAM",
    "BRADFORD",
    "BRIGHTON",
    "BRISTOL",
    "CAMBRIDGE",
    "CANTERBURY",
    "CARDIFF",
    "CARLISLE",
    "CHELMSFORD",
    "CHESTER",
    "CHICHESTER",
    "COLCHESTER",
    "COVENTRY",
    "DERBY",
    "DERRY",
    "DONCASTER",
    "DUNDEE",
    "DURHAM",
    "EDINBURGH",
    "ELY",
    "EXETER",
    "GLASGOW",
    "GLOUCESTER",
    "HEREFORD",
    "INVERNESS",
    "IPSWICH",
    "KINGSTON UPON HULL",
    "HULL",
    "LANCASTER",
    "LEEDS",
    "LEICESTER",
    "LICHFIELD",
    "LINCOLN",
    "LIVERPOOL",
    "LONDON",
    "LUTON",
    "MANCHESTER",
    "MILTON KEYNES",
    "NEWCASTLE UPON TYNE",
    "NEWCASTLE",
    "NEWPORT",
    "NORWICH",
    "NOTTINGHAM",
    "OXFORD",
    "PERTH",
    "PETERBOROUGH",
    "PLYMOUTH",
    "PORTSMOUTH",
    "PRESTON",
    "READING",
    "RIPON",
    "SALFORD",
    "SALISBURY",
    "SHEFFIELD",
    "SOUTHAMPTON",
    "SOUTHEND-ON-SEA",
    "ST ALBANS",
    "ST ASAPH",
    "ST DAVIDS",
    "STIRLING",
    "STOKE-ON-TRENT",
    "SUNDERLAND",
    "SWANSEA",
    "TRURO",
    "WAKEFIELD",
    "WELLS",
    "WESTMINSTER",
    "WINCHESTER",
    "WOLVERHAMPTON",
    "WORCESTER",
    "WREXHAM",
    "YORK",
    "BOURNEMOUTH",
    "BOLTON",
    "BLACKPOOL",
    "BLACKBURN",
    "HUDDERSFIELD",
    "STOCKPORT",
    "ROTHERHAM",
    "SWINDON",
    "NORTHAMPTON",
    "SLOUGH",
    "ST HELIER",
    "ST PETER PORT",
    "DOUGLAS",
}

UK_BUILDING_INDICATORS: Set[str] = {
    "COURT",
    "HOUSE",
    "MANSIONS",
    "MANSION",
    "TOWER",
    "TOWERS",
    "CHAMBERS",
    "HALL",
    "LODGE",
    "COTTAGE",
    "VILLA",
    "VILLAS",
    "BUILDING",
    "BUILDINGS",
    "CENTRE",
    "CENTER",
    "WHARF",
    "MEWS",
    "PRIORY",
    "MANOR",
    "GRANGE",
    "CASTLE",
    "PALACE",
}


def is_uk_building_name(text: str) -> bool:
    """Returns True if text matches UK building / premise naming conventions."""
    if not text:
        return False
    clean = text.strip().upper()
    if clean.startswith("THE "):
        return True
    tokens = set(re.findall(r"[A-Z]+", clean))
    return bool(tokens & UK_BUILDING_INDICATORS)


DISALLOWED_OUTWARD_POS1 = {"Q", "V", "X"}
DISALLOWED_OUTWARD_POS2 = {"I", "J", "Z"}
DISALLOWED_INWARD_LETTERS = {"C", "I", "K", "M", "O", "V"}


def is_valid_uk_postcode(raw_code: str) -> bool:
    """Validate Royal Mail alphanumeric postcode format and character constraints."""
    if not raw_code:
        return False
    clean = " ".join(raw_code.strip().upper().split())
    if clean == "GIR 0AA":
        return True

    m = RE_UK_POSTCODE_EXACT.match(clean)
    if not m:
        return False

    outward = m.group(1).upper()
    inward = m.group(2).upper()

    if len(outward) >= 1 and outward[0] in DISALLOWED_OUTWARD_POS1:
        return False
    if len(outward) >= 2 and outward[1].isalpha() and outward[1] in DISALLOWED_OUTWARD_POS2:
        return False

    if len(inward) == 3:
        if inward[1] in DISALLOWED_INWARD_LETTERS or inward[2] in DISALLOWED_INWARD_LETTERS:
            return False

    return True


class UKGrammar(CountryGrammar):
    """Royal Mail PAF / BS 7666 compliant United Kingdom grammar."""

    country_iso3: ClassVar[str] = "GBR"
    supported_countries: ClassVar[Tuple[str, ...]] = ("GBR", "UK", "UNITED KINGDOM", "JEY", "GGY", "IMN")

    def normalize_postal_code(self, raw_code: str) -> str:
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().upper().split())
        m = RE_UK_POSTCODE_EXACT.match(clean)
        if m:
            outward = m.group(1).upper()
            inward = m.group(2).upper()
            return f"{outward} {inward}"
        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract (premise_name, street_number, street_name) from UK thoroughfare line."""
        if not street_line:
            return None, None, None

        line = street_line.strip()
        premise: Optional[str] = None
        st_num: Optional[str] = None
        st_name: Optional[str] = None

        if "," in line:
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 2:
                # Part 0 is potential premise name
                m_num0 = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", parts[0])
                if not m_num0:
                    premise = parts[0].upper()
                    rest = ", ".join(parts[1:])
                else:
                    rest = line
            else:
                rest = line
        else:
            rest = line

        # Split remaining into street number and street name
        m_num = re.match(r"^(\d+[A-Za-z0-9\-\/]*)\s+(.*)$", rest.strip())
        if m_num:
            st_num = m_num.group(1).upper()
            st_name = self._normalize_street_tokens(m_num.group(2))
        else:
            st_name = self._normalize_street_tokens(rest)

        return premise, st_num, st_name

    def _normalize_street_tokens(self, text: str) -> str:
        """Normalizes thoroughfare tokens while preserving double-barrelled hyphens."""
        if not text:
            return ""
        words = text.strip().split()
        norm_words: List[str] = []
        for w in words:
            if "-" in w and any(c.isalpha() for c in w):
                subparts = w.split("-")
                norm_sub = []
                for sp in subparts:
                    sp_clean = RE_NON_ALPHANUMERIC.sub("", sp).upper()
                    if sp_clean in STREET_SUFFIXES:
                        norm_sub.append(STREET_SUFFIXES[sp_clean])
                    elif sp_clean in DIRECTIONALS:
                        norm_sub.append(DIRECTIONALS[sp_clean])
                    else:
                        norm_sub.append(sp.upper())
                norm_words.append("-".join(norm_sub))
            else:
                w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
                if w_clean in STREET_SUFFIXES:
                    norm_words.append(STREET_SUFFIXES[w_clean])
                elif w_clean in DIRECTIONALS:
                    norm_words.append(DIRECTIONALS[w_clean])
                else:
                    norm_words.append(w.upper())
        return " ".join(norm_words)

    def parse(self, raw_tokens: List[str], metadata: dict) -> UKParsedAddressComponents:
        s1_raw = metadata.get("street1", "")
        s2_raw = metadata.get("street2", "")
        city_raw = metadata.get("city", "")
        state_raw = metadata.get("state", "")
        postal_raw = metadata.get("postal_code", "")
        country_iso = metadata.get("country", self.country_iso3)

        unit_type: Optional[str] = None
        unit_number: Optional[str] = None
        building_name: Optional[str] = None
        dep_locality: Optional[str] = None
        street_line = s1_raw

        # Handle single-line comma-separated address when city_raw is empty
        if not city_raw and s1_raw and "," in s1_raw:
            parts_comma = [p.strip() for p in s1_raw.split(",") if p.strip()]
            if len(parts_comma) >= 2:
                last_up = parts_comma[-1].upper()
                if last_up in (
                    "UK", "GBR", "UNITED KINGDOM", "ENGLAND", "SCOTLAND", "WALES",
                    "JERSEY", "GUERNSEY", "ISLE OF MAN", "JEY", "GGY", "IMN"
                ):
                    parts_comma = parts_comma[:-1]

            # Check if last token is UK postcode
            if parts_comma and (
                RE_UK_POSTCODE_EXACT.match(parts_comma[-1])
                or RE_UK_POSTCODE_SEARCH.search(parts_comma[-1])
            ):
                m_post = RE_UK_POSTCODE_SEARCH.search(parts_comma[-1])
                if m_post:
                    postal_raw = m_post.group(1)
                    rem = parts_comma[-1][:m_post.start()].strip()
                    if rem:
                        parts_comma[-1] = rem
                    else:
                        parts_comma = parts_comma[:-1]

            # Pre-check if any part is secondary unit (e.g. "Flat 3" or post-street "Flat 2")
            new_parts: List[str] = []
            for part in parts_comma:
                m_f = re.match(
                    r"^(?:FLAT|APT|UNIT|SUITE|STE)\s*#?\s*([A-Za-z0-9\-]+)$",
                    part.strip(),
                    re.IGNORECASE,
                )
                if m_f and not unit_number:
                    p_type = part.strip().split()[0].upper()
                    unit_type = SECONDARY_UNITS.get(p_type, "APT" if p_type == "FLAT" else p_type)
                    unit_number = m_f.group(1).upper()
                else:
                    new_parts.append(part)
            parts_comma = new_parts

            if len(parts_comma) == 1:
                p0 = parts_comma[0].strip().upper()
                if p0 in UK_POST_TOWNS:
                    city_raw = parts_comma[0]
                    street_line = ""
                else:
                    street_line = parts_comma[0]
            elif len(parts_comma) == 2:
                street_line = parts_comma[0]
                city_raw = parts_comma[1]
            elif len(parts_comma) >= 3:
                last_token = parts_comma[-1].strip().upper()
                if last_token in UK_POST_TOWNS:
                    city_raw = parts_comma[-1]
                    # Check if second to last is thoroughfare or dependent locality
                    m_num_prev = re.match(r"^\d+", parts_comma[-2].strip())
                    if m_num_prev:
                        # parts_comma[-2] is thoroughfare, parts_comma[0] is building
                        building_name = parts_comma[0].upper()
                        street_line = ", ".join(parts_comma[1:-1])
                    else:
                        dep_locality = parts_comma[-2].strip().upper()
                        street_line = ", ".join(parts_comma[:-2])
                else:
                    city_raw = parts_comma[-1]
                    street_line = ", ".join(parts_comma[:-1])

        # Handle s2_raw: classify non-unit as building_name or dependent_locality, or extract unit
        if s2_raw:
            m_s2 = RE_INTL_SEC_START.match(s2_raw.strip())
            if m_s2:
                sec_type = m_s2.group(1).upper()
                unit_type = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
                sec_rest = m_s2.group(2).strip()
                m_id = re.match(r"^([A-Za-z0-9\-]+)[,\s]+(.*)$", sec_rest, re.IGNORECASE)
                if m_id:
                    unit_number = m_id.group(1).upper()
                    rest = m_id.group(2).strip()
                    if is_uk_building_name(rest) and not building_name:
                        building_name = rest.upper()
                    elif not dep_locality:
                        dep_locality = rest.upper()
                else:
                    unit_number = sec_rest.upper()
            else:
                if is_uk_building_name(s2_raw) and not building_name:
                    building_name = s2_raw.strip().upper()
                elif not dep_locality:
                    dep_locality = s2_raw.strip().upper()

        # Pre-split leading or inline secondary unit from street_line if not already found
        if not unit_number and street_line:
            m_flat = RE_INTL_FLAT.match(street_line)
            if m_flat:
                unit_type = "APT"
                unit_number = m_flat.group(1).upper()
                street_line = m_flat.group(2).strip()
            else:
                m_sec = RE_INTL_SEC_START.match(street_line)
                if m_sec:
                    sec_type = m_sec.group(1).upper()
                    sec_rest = m_sec.group(2).strip()
                    m_id = re.match(r"^([A-Z0-9\-]+)[,\s]+(.*)$", sec_rest, re.IGNORECASE)
                    if m_id:
                        sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
                        unit_type = sec_type_norm
                        unit_number = m_id.group(1).upper()
                        street_line = m_id.group(2).strip()
                elif RE_INTL_SEC_INLINE.search(street_line):
                    m_inline = RE_INTL_SEC_INLINE.search(street_line)
                    sec_type = m_inline.group(1).upper()
                    sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
                    unit_type = sec_type_norm
                    unit_number = m_inline.group(2).upper()
                    street_line = street_line[:m_inline.start()] + street_line[m_inline.end():]
                    street_line = RE_WHITESPACE.sub(" ", street_line.strip(" ,.-"))

        premise, st_num, st_name = self.extract_premise_and_thoroughfare(street_line)
        if not building_name and premise:
            building_name = premise

        norm_postal = self.normalize_postal_code(postal_raw)
        norm_city = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", city_raw).strip().upper())
        norm_state = RE_WHITESPACE.sub(" ", RE_COMMA_DOT.sub(" ", state_raw).strip().upper())

        return UKParsedAddressComponents(
            street_number=st_num,
            street_name=st_name,
            unit_type=unit_type,
            unit_number=unit_number,
            building_name=building_name,
            dependent_locality=dep_locality,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )
