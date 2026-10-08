"""Behavioural coverage tests for international.postal and international.uk."""

import pytest

from address_standardizer.international import postal as P
from address_standardizer.international import uk as UK
from address_standardizer.international.postal import (
    PostalValidationResult,
    extract_postal_code,
    validate_postal_code,
)


def _v(code, country):
    res = validate_postal_code(code, country, return_details=True)
    assert isinstance(res, PostalValidationResult)
    return res


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fn, raw, expected",
    [
        (P._format_uk, "gir0aa", "GIR 0AA"),
        (P._format_uk, "sw1a1aa", "SW1A 1AA"),
        (P._format_uk, "M1", "M1"),
        (P._format_canada, "m5v2t6", "M5V 2T6"),
        (P._format_canada, "m5v", "M5V"),
        (P._format_netherlands, "1012js", "1012 JS"),
        (P._format_netherlands, "1012", "1012"),
        (P._format_japan, "1000001", "100-0001"),
        (P._format_japan, "10000", "10000"),
        (P._format_poland, "00950", "00-950"),
        (P._format_poland, "950", "950"),
        (P._format_portugal, "1000001", "1000-001"),
        (P._format_portugal, "1000", "1000"),
        (P._format_brazil, "01310200", "01310-200"),
        (P._format_brazil, "01310", "01310"),
        (P._format_sweden, "11122", "111 22"),
        (P._format_sweden, "111", "111"),
        (P._format_czech_slovak, "11000", "110 00"),
        (P._format_czech_slovak, "11", "11"),
        (P._format_greece, "10431", "104 31"),
        (P._format_greece, "1043", "1043"),
        (P._format_usa, "100051234", "10005-1234"),
        (P._format_usa, "10005", "10005"),
        (P._format_saudi, "115641234", "11564-1234"),
        (P._format_saudi, "11564", "11564"),
        (P._format_korea, "123456", "123-456"),
        (P._format_korea, "03186", "03186"),
        (P._format_ireland, "d02-x285", "D02 X285"),
        (P._format_ireland, "d02", "D02"),
        (P._format_malta, "vlt1115", "VLT 1115"),
        (P._format_malta, "VLT", "VLT"),
        (P._format_bermuda, "hm11", "HM 11"),
        (P._format_bermuda, "HMX", "HMX"),
    ],
)
def test_formatters(fn, raw, expected):
    assert fn(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("ky1-1104", "KY1-1104"),
        ("CYM KY2-1104", "KY2-1104"),
        ("KY1104", "KY1-1104"),  # KY + 4 digits -> default island 1
        ("1104", "KY1-1104"),
        ("KY11104", "KY1-1104"),  # KY + 5 digits: island digit kept
        ("KYZ1104", "KYZ-1104"),  # 7 chars starting with KY but not KY[123]
        ("ABC", "ABC"),
    ],
)
def test_format_cayman(raw, expected):
    assert P._format_cayman(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [("VG1110", "VG1110"), ("vg 1110", "VG1110"), ("1110", "VG1110"), ("11", "11")],
)
def test_format_vgb(raw, expected):
    assert P._format_vgb(raw) == expected


# ---------------------------------------------------------------------------
# validate_postal_code: control flow
# ---------------------------------------------------------------------------


def test_unknown_country_details_and_bool():
    res = _v("12345", "Atlantis")
    assert not res.is_valid
    assert res.country_code == "ATLANTIS"
    assert "Unknown or unsupported country" in res.reason
    assert validate_postal_code("12345", "Atlantis") is False
    res2 = validate_postal_code(None, None, return_details=True)
    assert res2.country_code == "" and res2.postal_code == ""


def test_country_alias_keyword_and_none_code():
    assert validate_postal_code("10115", country="DE") is True
    assert validate_postal_code(None, "DE") is False


def test_non_postal_country_is_accepted():
    res = _v("whatever", "ARE")
    assert res.is_valid and res.is_non_postal_country
    assert res.formatted_code == "whatever"
    empty = _v("", "ARE")
    assert empty.is_valid and empty.formatted_code is None
    assert validate_postal_code("", "ARE") is True


def test_missing_postal_code_for_postal_country():
    res = _v("   ", "USA")
    assert not res.is_valid
    assert "required" in res.reason
    assert validate_postal_code("", "USA") is False


def test_country_without_rule_uses_generic_fallback(monkeypatch):
    monkeypatch.delitem(P.POSTAL_RULES, "NZL")
    res = _v("  60 11 ", "NZL")
    assert res.is_valid
    assert res.formatted_code == "60 11"
    assert validate_postal_code("6011", "NZL") is True


def test_illegal_alphabetic_and_symbol_characters_numeric_country():
    res = _v("1001A", "DEU")
    assert not res.is_valid and "illegal alphabetic" in res.reason
    assert validate_postal_code("1001A", "DEU") is False
    res = _v("1011*", "DEU")
    assert not res.is_valid and "illegal characters" in res.reason
    assert validate_postal_code("1011*", "DEU") is False


def test_illegal_symbol_in_alphanumeric_country():
    res = _v("M5V *T6", "CAN")
    assert not res.is_valid and "illegal characters" in res.reason
    assert validate_postal_code("M5V *T6", "CAN") is False


def test_length_bounds():
    short = _v("1234", "DEU")
    assert not short.is_valid and "too short" in short.reason
    assert validate_postal_code("1234", "DEU") is False
    long_ = _v("123456", "DEU")
    assert not long_.is_valid and "too long" in long_.reason
    assert validate_postal_code("123456", "DEU") is False


def test_pattern_mismatch():
    res = _v("00000", "ESP")
    assert not res.is_valid and "does not match official format" in res.reason
    assert validate_postal_code("00000", "ESP") is False


def test_prefix_stripping():
    assert _v("D-10115", "DEU").formatted_code == "10115"
    assert _v("NSW 2000", "AUS").formatted_code == "2000"
    assert _v("S238880", "SGP").formatted_code == "238880"


def test_us_formatting_and_ncl():
    assert _v("100051234", "USA").formatted_code == "10005-1234"
    assert _v("10005", "USA").formatted_code == "10005"


# ---------------------------------------------------------------------------
# validate_postal_code: jurisdictional normalisation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("VG 1110", "VG1110"),
        ("BVI 1110", "VG1110"),
        ("1110", "VG1110"),
    ],
)
def test_bvi_variants(raw, expected):
    res = _v(raw, "VGB")
    assert res.is_valid and res.formatted_code == expected


@pytest.mark.parametrize(
    "raw",
    ["KY1-1104", "KY 1104", "KY-1104", "KY1 1104", "KY11104", "1104", "CYM 1104"],
)
def test_cayman_variants_all_canonicalise(raw):
    res = _v(raw, "CYM")
    assert res.is_valid, raw
    assert res.formatted_code == "KY1-1104"


def test_cayman_island_digit_preserved():
    assert _v("KY2 1104", "CYM").formatted_code == "KY2-1104"
    assert _v("KY31104", "CYM").formatted_code == "KY3-1104"


def test_jersey_guernsey_man_hyphenated_area():
    assert _v("JE-2 3RP", "JEY").formatted_code == "JE2 3RP"
    assert _v("GY-1 1AA", "GGY").formatted_code == "GY1 1AA"
    assert _v("IM-1 1AA", "IMN").formatted_code == "IM1 1AA"
    assert _v("GB-JE2 3RP", "JEY").formatted_code == "JE2 3RP"


# ---------------------------------------------------------------------------
# Semantic checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code, ok",
    [
        ("SW1A 1AA", True),
        ("GIR 0AA", True),
        ("QA1 1AA", False),  # Q not allowed first
        ("AI1 1AA", False),  # I not allowed second letter
        ("SW1A 1AC", False),  # C not allowed in inward unit letters
        ("SW1A1AA", True),
        ("???", False),  # no regex match
    ],
)
def test_validate_uk_semantics(code, ok):
    assert P._validate_uk_semantics(code) is ok


def test_gbr_semantic_rejection_reason():
    res = _v("QA1 1AA", "GBR")
    assert not res.is_valid and "Royal Mail" in res.reason
    assert validate_postal_code("QA1 1AA", "GBR") is False
    assert _v("sw1a1aa", "GBR").formatted_code == "SW1A 1AA"


def test_canadian_semantic_rejection(monkeypatch):
    assert P._validate_canadian_semantics("M5V 2T6") is True
    assert P._validate_canadian_semantics("D5V 2T6") is False
    # Force the rule regex to be permissive so the semantic layer is what rejects.
    rule = P.POSTAL_RULES["CAN"]
    import re
    from dataclasses import replace

    loose = replace(rule, pattern=re.compile(r"^[A-Z]\d[A-Z]\s*\d[A-Z]\d$", re.I))
    monkeypatch.setitem(P.POSTAL_RULES, "CAN", loose)
    res = _v("D5V 2T6", "CAN")
    assert not res.is_valid and "Canada Post" in res.reason
    assert validate_postal_code("D5V 2T6", "CAN") is False


def test_dutch_semantics_and_rejection(monkeypatch):
    assert P._validate_dutch_semantics("1012 JS") is True
    assert P._validate_dutch_semantics("1012 SS") is False
    assert P._validate_dutch_semantics("0123 AB") is False
    assert P._validate_dutch_semantics("junk") is False
    res = _v("1012 SA", "NLD")
    assert not res.is_valid and "disallowed combination" in res.reason
    assert validate_postal_code("1012 SD", "NLD") is False
    assert _v("1012js", "NLD").formatted_code == "1012 JS"


def test_netherlands_no_leading_zero():
    assert validate_postal_code("0123 AB", "NLD") is False


def test_bermuda_and_eircode_rules():
    assert _v("HM 11", "BMU").formatted_code == "HM 11"
    assert _v("HM AX", "BMU").is_valid
    assert validate_postal_code("HM BB", "BMU") is False  # Hamilton PO box form needs X as 2nd letter
    assert validate_postal_code("D02 X285", "IRL") is True
    assert validate_postal_code("D02 B285", "IRL") is False  # B not in Eircode alphabet


# ---------------------------------------------------------------------------
# extract_postal_code: country-specific
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, hint, expected",
    [
        ("Toronto ON m5v2t6", "CAN", "M5V 2T6"),
        ("Toronto ON nothing", "CAN", None),
        ("Toronto ON D5V 2T6", "CAN", None),
        ("London SW1A 1AA UK", "GBR", "SW1A 1AA"),
        ("London no code", "GBR", None),
        ("St Helier JE2 3RP", "JEY", "JE2 3RP"),
        ("London QA1 1AA", "GBR", None),
        ("Amsterdam 1012 JS", "NLD", "1012 JS"),
        ("Amsterdam 1012 SS", "NLD", None),
        ("Amsterdam", "NLD", None),
        ("Dublin D02 X285", "IRL", "D02 X285"),
        ("Dublin nothing", "IRL", None),
        ("Dublin Z99 ZZZZ", "IRL", None),
        ("Tokyo 100-0001", "JPN", "100-0001"),
        ("Tokyo 〒 100-0001", "JPN", "100-0001"),
        ("Tokyo 1000001", "JPN", "100-0001"),
        ("Tokyo 99-99", "JPN", None),
        ("Tokyo 123456789", "JPN", None),
        ("Sao Paulo CEP 01310-200", "BRA", "01310-200"),
        ("Sao Paulo", "BRA", None),
        ("Warszawa 00-950", "POL", "00-950"),
        ("Warszawa", "POL", None),
        ("Lisboa 1000-001", "PRT", "1000-001"),
        ("Lisboa", "PRT", None),
        ("Buenos Aires C1024CWN", "ARG", "C1024CWN"),
        ("Buenos Aires", "ARG", None),
        ("1 Raffles Place SG 048616", "SGP", "048616"),
        ("1 Raffles Place 048616", "SGP", "048616"),
        ("1 Raffles Place", "SGP", None),
        ("Sydney NSW 2000", "AUS", "2000"),
        ("Sydney 2000", "AUS", "2000"),
        ("Sydney", "AUS", None),
        ("Road Town VG 1110", "VGB", "VG1110"),
        ("Road Town 1110", "VGB", "VG1110"),
        ("Road Town", "VGB", None),
        ("George Town KY1-1104", "CYM", "KY1-1104"),
        ("George Town 1104", "CYM", "KY1-1104"),
        ("George Town", "CYM", None),
        ("New York NY 10005", "USA", "10005"),
        ("New York 10005-1234", "USA", "10005-1234"),
        ("New York ?? 123456 99999", "USA", "99999"),
        ("New York", "USA", None),
        ("Berlin D-10115", "DEU", "10115"),
        ("Berlin 10115", "DEU", "10115"),
        ("Praha 110 00", "CZE", "110 00"),
        ("Berlin nothing", "DEU", None),
        ("Beijing 100000", "CHN", "100000"),
        ("Beijing", "CHN", None),
        ("Zurich 8001", "CHE", "8001"),
        ("Zurich", "CHE", None),
        ("HM 11", "BMU", "HM 11"),
        ("Hamilton", "BMU", None),
        ("Dubai 12345", "ARE", None),
    ],
)
def test_extract_with_country_hint(text, hint, expected):
    assert extract_postal_code(text, hint) == expected


def test_zip_plus_four_is_not_mistaken_for_japanese_postcode():
    # Regression: the 3-4 Japanese pattern used to match the tail "005-1234" of a ZIP+4.
    assert extract_postal_code("Somewhere 10005-1234") == "10005-1234"
    assert extract_postal_code("Somewhere 10005-1234", "JPN") is None
    assert extract_postal_code("Tokyo 100-0001") == "100-0001"


def test_extract_unknown_hint_and_empty():
    assert extract_postal_code("12345", "Atlantis") is None
    assert extract_postal_code("", "USA") is None
    assert extract_postal_code("   ", "USA") is None
    assert extract_postal_code(None) is None
    assert extract_postal_code("10115", country="DEU") == "10115"


def test_extract_five_digit_fallback_for_countries_without_special_rule():
    # Two numbers: the trailing valid one wins
    assert extract_postal_code("Calle 12345 Madrid 28001", "ESP") == "28001"


def test_extract_generic_rule_search_and_miss():
    # Alphanumeric rules use the generic regex search path.
    assert extract_postal_code("LV-1050", "LVA") == "1050"  # prefix stripped by validator
    assert extract_postal_code("vlt1115", "MLT") == "VLT 1115"
    assert extract_postal_code("Riga", "LVA") is None


# ---------------------------------------------------------------------------
# extract_postal_code: auto-detect and generic candidates
# ---------------------------------------------------------------------------


def test_extract_autodetect_non_postal_country_returns_none():
    assert extract_postal_code("Dubai, United Arab Emirates 12345") is None


def test_extract_autodetect_country_found():
    assert extract_postal_code("10 Downing Street, London SW1A 2AA, United Kingdom") == "SW1A 2AA"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Toronto M5V 2T6", "M5V 2T6"),
        ("London SW1A 1AA", "SW1A 1AA"),
        ("Amsterdam 1012 JS", "1012 JS"),
        ("Dublin D02 X285", "D02 X285"),
        ("Tokyo 100-0001", "100-0001"),
        ("Sao Paulo 01310-200", "01310-200"),
        ("Warszawa 00-950", "00-950"),
        ("Lisboa 1000-001", "1000-001"),
        ("Buenos Aires C1024CWN", "C1024CWN"),
        ("Somewhere 10005-1234", "10005-1234"),
        ("Somewhere PLZ: 10115", "10115"),
        ("ref ZIP code 12 34 56", "12 34 56"),
        ("Somewhere F-75008 Paris", "75008"),
        ("Somewhere CA 90210 blah", "90210"),
        ("Somewhere 12345 and 54321", "54321"),
        ("Somewhere 123456", "123456"),
        ("Somewhere 1234", "1234"),
        ("Somewhere nothing here", None),
    ],
)
def test_extract_no_hint_candidates(text, expected):
    assert extract_postal_code(text) == expected


def test_extract_keyword_prefix_too_short_is_rejected():
    # ``POSTAL`` keyword followed by too few alphanumerics falls through to later heuristics
    assert extract_postal_code("POSTAL: 1 2") is None


def test_candidate_any_invalid_candidates_fall_through():
    # Matches each country regex but fails validation; ends at generic 5-digit rule.
    assert P._extract_candidate_any("D5V 2T6 QA1 1AA Z99 ZZZZ 99-99") is None
    assert P._extract_candidate_any("QA1 1AA 99999") == "99999"


# ---------------------------------------------------------------------------
# UK module
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code, ok",
    [
        ("", False),
        (None, False),
        ("SW1A 1AA", True),
        ("sw1a1aa", True),
        ("GIR 0AA", True),
        ("QA1 1AA", False),
        ("AI1 1AA", False),
        ("SW1A 1AC", False),
        ("not a code", False),
    ],
)
def test_is_valid_uk_postcode(code, ok):
    assert UK.is_valid_uk_postcode(code) is ok


def test_split_po_box_unit():
    assert UK.split_po_box_unit("PO Box 309 Suite 100") == ("PO BOX 309", "Suite 100")
    assert UK.split_po_box_unit("p.o. box 12, Flat 4") == ("PO BOX 12", "Flat 4")
    assert UK.split_po_box_unit("PO Box 309") is None
    assert UK.split_po_box_unit("") is None
    assert UK.split_po_box_unit(None) is None


def test_is_uk_building_name():
    assert UK.is_uk_building_name("The Gables") is True
    assert UK.is_uk_building_name("Rose Cottage") is True
    assert UK.is_uk_building_name("High Street") is False
    assert UK.is_uk_building_name("") is False


def test_uk_normalize_postal_code():
    g = UK.UKGrammar()
    assert g.normalize_postal_code("") == ""
    assert g.normalize_postal_code("sw1a1aa") == "SW1A 1AA"
    assert g.normalize_postal_code("GB-JE2 3RP") == "JE2 3RP"
    assert g.normalize_postal_code("JE-2 3RP") == "JE2 3RP"
    assert g.normalize_postal_code("garbage") == "GARBAGE"


def test_uk_format_street1_street2_components():
    C = UK.UKParsedAddressComponents
    c = C(street_number="10", street_name="DOWNING", street_type="ST", pre_directional="N", post_directional="W")
    assert c.format_street1() == "10 N DOWNING ST W"
    # Street type already part of the name is not repeated
    c = C(street_number="10", street_name="HIGH ST", street_type="ST")
    assert c.format_street1() == "10 HIGH ST"
    c = C(street_number="10", street_name="ST JOHNS", street_type="ST")
    assert c.format_street1() == "10 ST JOHNS"
    c = C(street_number="10", street_name="ST", street_type="ST")
    assert c.format_street1() == "10 ST"
    # Numeric street name with a unit
    c = C(street_name="10", unit_type="FLAT", unit_number="2")
    assert c.format_street1() == "10 FLAT 2"
    assert c.format_street2() == ""
    c = C(street_name="10", unit_number="2", building_name="  ROSE HOUSE ")
    assert c.format_street1() == "10 UNIT 2"
    assert c.format_street2() == "ROSE HOUSE"
    # Number plus unit with no street name
    c = C(street_number="10", unit_type="STE", unit_number="5")
    assert c.format_street1() == "10 STE 5"
    assert c.format_street2() == ""
    c = C(street_number="10", unit_number="5", building_name="THE OLD MILL")
    assert c.format_street2() == "THE OLD MILL"
    # Normal street2
    c = C(street_number="10", street_name="HIGH", street_type="ST", unit_type="APT", unit_number="2",
          building_name="ROSE HOUSE")
    assert c.format_street2() == "APT 2 ROSE HOUSE"
    c = C(street_number="10", street_name="HIGH", street_type="ST", building_name="ROSE HOUSE")
    assert c.format_street2() == "ROSE HOUSE"
    c = C(street_number="10", street_name="HIGH", street_type="ST", unit_type="APT", unit_number="2")
    assert c.format_street2() == "APT 2"
    # Fallback to base class when neither street nor unit present
    c = C()
    assert c.format_street1() == ""


def _uk(**meta):
    meta.setdefault("country", "GBR")
    return UK.UKGrammar().parse([], meta)


def test_uk_extract_premise_and_thoroughfare_variants():
    g = UK.UKGrammar()
    assert g.extract_premise_and_thoroughfare("") == (None, None, None)
    assert g.extract_premise_and_thoroughfare("10 High Street") == (None, "10", "HIGH ST")
    assert g.extract_premise_and_thoroughfare("Rose Cottage, 10 High Street") == ("ROSE COTTAGE", "10", "HIGH ST")
    assert g.extract_premise_and_thoroughfare("10 High Street, Leeds") == (None, "10", "HIGH ST LEEDS")
    assert g.extract_premise_and_thoroughfare("High Street") == (None, None, "HIGH ST")
    # Orphan numeric/letter token is a premise, not a thoroughfare
    assert g.extract_premise_and_thoroughfare("12A") == ("12A", None, None)
    assert g.extract_premise_and_thoroughfare("UP") == ("UP", None, None)
    # Single comma part
    assert g.extract_premise_and_thoroughfare("High Street,") == (None, None, "HIGH ST")


def test_uk_normalize_street_tokens_hyphen_hill_direction():
    g = UK.UKGrammar()
    assert g._normalize_street_tokens("") == ""
    assert g._normalize_street_tokens("Prospect Hill") == "PROSPECT HILL"
    assert g._normalize_street_tokens("Stratford-upon-Avon Road") == "STRATFORD-UPON-AVON RD"
    assert g._normalize_street_tokens("Chapel-Street") == "CHAPEL-ST"
    assert g._normalize_street_tokens("Hill-Hill") == "HILL-HILL"
    assert g._normalize_street_tokens("Queens-North") == "QUEENS-N"
    assert g._normalize_street_tokens("High Street North") == "HIGH ST N"
    assert g._normalize_street_tokens("Station Road") == "STATION RD"


def test_uk_parse_single_line_comma_address():
    p = _uk(street1="10 Downing Street, London, SW1A 2AA, UK")
    assert p.street_number == "10" and p.street_name == "DOWNING ST"
    assert p.city == "LONDON" and p.postal_code == "SW1A 2AA"


def test_uk_parse_single_line_postcode_in_own_part_removed():
    p = _uk(street1="14 High Street, Leeds LS1 1AA")
    assert p.postal_code == "LS1 1AA"
    assert p.street_number == "14"


def test_uk_parse_single_line_town_only():
    p = _uk(street1="Leeds, LS1 1AA")
    assert p.city == "LEEDS"
    assert p.street_number is None and p.street_name is None
    assert p.postal_code == "LS1 1AA"


def test_uk_parse_single_line_flat_part_extracted():
    p = _uk(street1="Flat 3, 10 High Street, Leeds, LS1 1AA")
    assert p.unit_type == "APT" and p.unit_number == "3"
    assert p.street_number == "10" and p.city == "LEEDS"
    p = _uk(street1="Suite 4, 10 High Street, Leeds")
    assert p.unit_type == "STE" and p.unit_number == "4"


def test_uk_parse_single_line_two_parts():
    p = _uk(street1="10, High Street")
    assert p.street_number == "10" and p.street_name == "HIGH ST" and not p.city
    p = _uk(street1="Rose Cottage, Leeds")
    assert p.city == "LEEDS" and p.street_number is None
    p = _uk(street1="10, Leeds")
    assert p.city == "LEEDS" and p.street_number is None


def test_uk_parse_single_line_three_parts_variants():
    p = _uk(street1="93, Queen Street, Leeds")
    assert p.street_number == "93" and p.street_name == "QUEEN ST" and p.city == "LEEDS"
    # Building, numbered thoroughfare, town
    p = _uk(street1="Rose Court, 10 High Street, Leeds")
    assert p.building_name == "ROSE COURT" and p.street_number == "10"
    # Dependent locality between street and town
    p = _uk(street1="High Street, Headingley, Leeds")
    assert p.dependent_locality == "HEADINGLEY" and p.city == "LEEDS"
    # Unknown last token becomes city
    p = _uk(street1="10 High Street, Headingley, Smalltown")
    assert p.city == "SMALLTOWN"
    assert p.street_number == "10"


def test_uk_parse_country_suffix_stripped():
    p = _uk(street1="10 High Street, Leeds, England")
    assert p.city == "LEEDS"


def test_uk_parse_postcode_only_part_dropped():
    p = _uk(street1="10 High Street, Leeds, LS1 1AA")
    assert p.postal_code == "LS1 1AA" and p.city == "LEEDS"


def test_uk_parse_po_box_with_unit_split():
    p = _uk(street1="PO Box 309 Suite 100", city="London", postal_code="EC1A 1BB")
    assert p.unit_type is not None and p.unit_number == "100"


def test_uk_parse_street2_variants():
    p = _uk(street1="10 High Street", street2="Flat 2", city="Leeds")
    assert p.unit_type == "APT" and p.unit_number == "2"
    p = _uk(street1="10 High Street", street2="Flat 2 Rose Court", city="Leeds")
    assert p.unit_number == "2" and p.building_name == "ROSE COURT"
    p = _uk(street1="10 High Street", street2="Flat 2 Headingley", city="Leeds")
    assert p.dependent_locality == "HEADINGLEY"
    p = _uk(street1="10 High Street", street2="Rose Court", city="Leeds")
    assert p.building_name == "ROSE COURT"
    p = _uk(street1="10 High Street", street2="Headingley", city="Leeds")
    assert p.dependent_locality == "HEADINGLEY"


def test_uk_parse_inline_units():
    p = _uk(street1="Flats 1-3 High Street", city="Leeds")
    assert p.unit_type == "APT" and p.unit_number == "1-3" and p.street_name == "HIGH ST"
    p = _uk(street1="Unit 4/5 Mill Lane", city="Leeds")
    assert p.unit_type == "UNIT" and p.unit_number == "4/5"
    p = _uk(street1="Top Floor Flat 2 High Street", city="Leeds")
    assert p.unit_type == "APT" and p.unit_number == "2"
    p = _uk(street1="Ground Floor Flat", city="Leeds")
    assert p.unit_type == "APT" and p.unit_number == "GROUND"
    p = _uk(street1="Flat 4 Mill Lane", city="Leeds")
    assert p.unit_type == "APT" and p.unit_number == "4" and p.street_name == "MILL LN"
    p = _uk(street1="Flat 4 B", city="Leeds")
    assert p.unit_number == "4B"
    p = _uk(street1="2nd Floor, 10 High Street", city="Leeds")
    assert p.unit_type == "FL" and p.unit_number == "2ND" and p.street_number == "10"
    p = _uk(street1="3 Floor West, 10 High Street", city="Leeds")
    assert p.unit_number == "3 WEST"
    p = _uk(street1="1st Floor Flat", city="Leeds")
    assert p.unit_type == "APT" and p.unit_number == "1ST FLAT"
    p = _uk(street1="1st Floor LHS", city="Leeds")
    assert p.unit_type == "FL" and p.unit_number == "1ST LHS"


def test_uk_parse_floor_with_dependent_locality_fallback():
    p = _uk(street1="2nd Floor", street2="Headingley", city="Leeds")
    assert p.unit_type == "FL" and p.street_name == "HEADINGLEY"
    assert p.dependent_locality is None


def test_uk_parse_sec_start_variants():
    p = _uk(street1="Suite 100 Rose House", city="London")
    assert p.unit_number is not None
    p = _uk(street1="Suite 100, A", city="London")
    assert p.unit_number == "100A" and not p.street_name
    p = _uk(street1="Suite 100", city="London")
    assert p.unit_number == "100"
    p = _uk(street1="PO Box 12, High Street", city="London")
    assert p.unit_type == "PO BOX" and p.unit_number == "12" and p.street_name == "HIGH ST"
    p = _uk(street1="PO Box 12", city="London")
    assert p.unit_type == "PO BOX" and p.unit_number == "12" and p.street_name is None


def test_uk_parse_inline_secondary_unit_in_street():
    p = _uk(street1="10 High Street Flat 3", city="Leeds")
    assert p.unit_number == "3" and p.street_name == "HIGH ST"


def test_uk_parse_dependent_locality_after_street():
    p = _uk(street1="14 High Street, Headingley", city="Leeds")
    assert p.dependent_locality == "HEADINGLEY" and p.street_name == "HIGH ST"
    # Tail equal to the city is not a locality
    p = _uk(street1="14 High Street, Leeds", city="Leeds")
    assert p.dependent_locality is None
    # Building-like tail keeps existing handling
    p = _uk(street1="14 High Street, Rose Court", city="Leeds")
    assert p.dependent_locality is None


def test_uk_parse_country_and_state_defaults():
    p = _uk(street1="10 High Street", city="Leeds", state="West Yorkshire", postal_code="ls11aa")
    assert p.state == "WEST YORKSHIRE" and p.postal_code == "LS1 1AA"
    assert p.country_iso3 == "GBR"
    p = UK.UKGrammar().parse([], {"street1": "10 High Street"})
    assert p.city is None and p.state is None and p.postal_code is None


# ---------------------------------------------------------------------------
# Extraction must never return a candidate the validator rejects
# ---------------------------------------------------------------------------


@pytest.fixture
def reject_all(monkeypatch):
    """Make the validator reject every candidate so extraction's skip-invalid paths run."""
    calls = []

    def _reject(code, country=None, return_details=False, *, country_alias=None, **kw):
        calls.append((code, country))
        return PostalValidationResult(False, str(code), str(country), "forced rejection")

    monkeypatch.setattr(P, "validate_postal_code", _reject)
    return calls


@pytest.mark.parametrize(
    "hint, text",
    [
        ("CAN", "Toronto M5V 2T6"),
        ("GBR", "London SW1A 1AA"),
        ("JEY", "Jersey JE2 3RP"),
        ("NLD", "Amsterdam 1012 JS"),
        ("IRL", "Dublin D02 X285"),
        ("JPN", "Tokyo 100-0001 and 1000001"),
        ("JPN", "Tokyo 1000001 2000002"),
        ("BRA", "Sao Paulo 01310-200"),
        ("POL", "Warszawa 00-950"),
        ("PRT", "Lisboa 1000-001"),
        ("ARG", "Buenos Aires C1024CWN"),
        ("SGP", "SG 048616 and 049315"),
        ("AUS", "NSW 2000 and 3000"),
        ("VGB", "VG 1110 and 1111"),
        ("CYM", "KY1-1104 and 1105"),
        ("USA", "NY 10005 and 10005-1234 and 94105"),
        ("DEU", "D-10115 and 10115 and 111 22"),
        ("CHN", "Beijing 100000 200000"),
        ("CHE", "Zurich 8001 9000"),
        ("LVA", "LV-1050"),
    ],
)
def test_extract_skips_candidates_rejected_by_validator(reject_all, hint, text):
    assert extract_postal_code(text, hint) is None
    assert reject_all, "validator was never consulted"


def test_extract_candidate_any_falls_back_to_unvalidated_heuristics_when_all_rejected(reject_all):
    text = "M5V 2T6 SW1A 1AA 1012 JS D02 X285 100-0001 01310-200 00-950 1000-001 C1024CWN 10005-1234"
    assert P._extract_candidate_any(text) == "10005"
    countries = [c for _, c in reject_all]
    # Every country-specific matcher was tried, in priority order
    assert countries[:10] == ["CAN", "GBR", "NLD", "IRL", "JPN", "BRA", "POL", "PRT", "ARG", "USA"]


def test_extract_country_without_rule_returns_none(monkeypatch):
    monkeypatch.delitem(P.POSTAL_RULES, "LVA")
    assert extract_postal_code("1050", "LVA") is None


def test_candidate_any_european_prefix_and_state_zip():
    assert P._extract_candidate_any("foo F-75008 bar") == "75008"
    assert P._extract_candidate_any("foo CH-8001") == "8001"
    assert P._extract_candidate_any("foo TX 77001 bar 12345") == "77001"
    assert P._extract_candidate_any("nothing at all") is None


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Toronto m5v2t6", "M5V 2T6"),
        ("London sw1a1aa", "SW1A 1AA"),
        ("Amsterdam 1012js", "1012 JS"),
        ("Dublin d02x285", "D02 X285"),
        ("Tokyo 〒 100-0001", "100-0001"),
        ("Sao Paulo CEP 01310-200", "01310-200"),
        ("Warszawa 00-950", "00-950"),
        ("Lisboa 1000-001", "1000-001"),
        ("Buenos Aires C1024CWN", "C1024CWN"),
    ],
)
def test_candidate_any_each_country_matcher_returns_formatted_code(text, expected):
    assert P._extract_candidate_any(text) == expected


def test_uk_parse_single_line_only_unit_and_postcode_has_no_street():
    # Regression: the raw line "Flat 3, LS1 1AA" used to be re-parsed as street_name="LS1 1AA".
    p = _uk(street1="Flat 3, LS1 1AA")
    assert p.unit_type == "APT" and p.unit_number == "3"
    assert p.postal_code == "LS1 1AA"
    assert p.street_name is None and p.street_number is None and p.building_name is None


def test_uk_parse_single_line_trailing_comma_and_unit_tail():
    p = _uk(street1="10 High Street,")
    assert p.street_number == "10" and p.street_name == "HIGH ST" and p.city is None
    p = _uk(street1="10 High Street, Flat 3")
    assert p.street_number == "10" and p.unit_type == "APT" and p.unit_number == "3"
    assert p.city is None


def test_uk_parse_gir_variant_is_not_extracted_as_postcode():
    # "GIR 1AA" is shaped like a postcode but only "GIR 0AA" exists
    p = _uk(street1="10 High Street, Leeds, GIR 1AA")
    assert p.postal_code is None


def test_uk_parse_s2_does_not_overwrite_existing_dependent_locality():
    p = _uk(street1="High Street, Headingley, Leeds", street2="Flat 2 Roundhay")
    assert p.unit_number == "2" and p.dependent_locality == "HEADINGLEY"
    p = _uk(street1="High Street, Headingley, Leeds", street2="Roundhay")
    assert p.dependent_locality == "HEADINGLEY" and p.city == "LEEDS"


def test_uk_parse_three_segment_street_with_city_is_left_alone():
    p = _uk(street1="10 High Street, Headingley, Roundhay", city="Leeds")
    assert p.dependent_locality is None and p.city == "LEEDS"
    assert p.street_number == "10"
