"""Tests for international base classes, address components, and country grammar registry."""

import pytest

from address_standardizer.international import (
    CountryGrammar,
    CountryGrammarRegistry,
    ParsedAddressComponents,
    UniversalInternationalGrammar,
    register_default_grammars,
    split_intl_secondary_unit,
)


def test_split_intl_secondary_unit_variants():
    # Flat at beginning
    s1, s2 = split_intl_secondary_unit("Flat 12 100 Main Street", "")
    assert s1 == "100 MAIN ST"
    assert s2 == "APT 12"

    # Inline secondary
    s1_in, s2_in = split_intl_secondary_unit("200 Bay Street Suite 400", "")
    assert s1_in == "200 BAY ST"
    assert s2_in == "STE 400"

    # Secondary in street2
    s1_s2, s2_s2 = split_intl_secondary_unit("50 King Street", "Floor 10")
    assert s1_s2 == "50 KING ST"
    assert s2_s2 == "FL 10"

    # Directionals and suffixes
    s1_dir, _ = split_intl_secondary_unit("10 North Road West", "")
    assert s1_dir == "10 N RD W"


def test_parsed_address_components_formatting():
    # Only building name
    c1 = ParsedAddressComponents(building_name="Empire House")
    assert c1.format_street1() == "Empire House"
    assert c1.format_street2() == ""

    # Building name and street
    c2 = ParsedAddressComponents(
        building_name="The Mansions",
        street_number="14",
        street_name="High",
        street_type="ST",
        unit_type="APT",
        unit_number="3B",
    )
    assert c2.format_street1() == "The Mansions 14 High ST"
    assert c2.format_street2() == "APT 3B"

    # Pre and post directionals
    c3 = ParsedAddressComponents(
        street_number="100",
        pre_directional="N",
        street_name="Main",
        street_type="ST",
        post_directional="E",
    )
    assert c3.format_street1() == "100 N Main ST E"

    # Unit type only and unit number only
    c4 = ParsedAddressComponents(unit_type="PENTHOUSE")
    assert c4.format_street2() == "PENTHOUSE"

    c5 = ParsedAddressComponents(unit_number="4B")
    assert c5.format_street2() == "4B"


def test_country_grammar_abstract_class():
    class DummyGrammar(CountryGrammar):
        country_iso3 = "DUM"
        supported_countries = ("DUM",)

        def parse(self, raw_tokens, metadata):
            return super().parse(raw_tokens, metadata)

        def normalize_postal_code(self, raw_code):
            return super().normalize_postal_code(raw_code)

        def extract_premise_and_thoroughfare(self, street_line):
            return super().extract_premise_and_thoroughfare(street_line)

    dummy = DummyGrammar()
    with pytest.raises(NotImplementedError):
        dummy.parse([], {})
    with pytest.raises(NotImplementedError):
        dummy.normalize_postal_code("123")
    with pytest.raises(NotImplementedError):
        dummy.extract_premise_and_thoroughfare("123 Main St")


def test_universal_international_grammar():
    univ = UniversalInternationalGrammar()
    assert univ.country_iso3 == "ZZZ"
    assert univ.normalize_postal_code("") == ""
    assert univ.normalize_postal_code("  2000  ") == "2000"

    # Premise extraction
    assert univ.extract_premise_and_thoroughfare("") == (None, None, None)
    assert univ.extract_premise_and_thoroughfare("100 Main St") == (None, "100", "Main St")
    assert univ.extract_premise_and_thoroughfare("Main St") == (None, None, "Main St")

    # Structured parse
    p_struct = univ.standardize(
        street1="123 King Street",
        street2="Suite 400",
        city="Sydney",
        state="NSW",
        postal_code="2000",
        country="AUS",
    )
    assert p_struct.format_street1() == "123 KING ST"
    assert p_struct.format_street2() == "STE 400"
    assert p_struct.city == "SYDNEY"

    # Comma-separated: PO Box in part 1
    p_box = univ.standardize(street1="Ugland House, PO Box 309, George Town, KY1-1104")
    assert p_box.format_street1() == "UGLAND HOUSE"
    assert p_box.format_street2() == "PO BOX 309"
    assert p_box.city == "GEORGE TOWN"
    assert p_box.postal_code == "KY1-1104"

    # Comma-separated: Canadian prov postal
    p_can = univ.standardize(street1="100 Main St, Toronto, ON M5V 2T6")
    assert p_can.format_street1() == "100 MAIN ST"
    assert p_can.city == "TORONTO"
    assert p_can.state == "ON"
    assert p_can.postal_code == "M5V 2T6"

    # Comma-separated: 2-part Canadian
    p_can2 = univ.standardize(street1="Toronto, ON M5V 2T6")
    assert p_can2.format_street1() == ""
    assert p_can2.city == "TORONTO"
    assert p_can2.state == "ON"

    # Comma-separated: 2-part UK
    p_uk2 = univ.standardize(street1="London, EC1A 1BB")
    assert p_uk2.format_street1() == ""
    assert p_uk2.city == "LONDON"
    assert p_uk2.postal_code == "EC1A 1BB"

    # Comma-separated: 2-part generic
    p_gen2 = univ.standardize(street1="100 Main St, Sydney")
    assert p_gen2.format_street1() == "100 MAIN ST"
    assert p_gen2.city == "SYDNEY"

    # Comma-separated: 1-part metro
    p_metro = univ.standardize(street1="Sydney, Australia")
    assert p_metro.format_street1() == ""
    assert p_metro.city == "SYDNEY"

    # Comma-separated: 1-part street
    p_st = univ.standardize(street1="100 Main St, Australia")
    assert p_st.format_street1() == "100 MAIN ST"

    # Canadian province full name in state
    p_prov = univ.standardize(
        street1="100 Main St",
        city="Toronto",
        state="Ontario",
        postal_code="M5V 2T6",
        country="CAN",
    )
    assert p_prov.state == "ON"


def test_country_grammar_registry():
    CountryGrammarRegistry.clear()
    assert len(CountryGrammarRegistry.supported_countries()) == 0
    assert CountryGrammarRegistry.get(None) is not None
    assert CountryGrammarRegistry.has(None) is False
    assert CountryGrammarRegistry.has("CAN") is False

    register_default_grammars()
    assert CountryGrammarRegistry.has("CAN") is True
    assert CountryGrammarRegistry.has("GBR") is True
    assert CountryGrammarRegistry.has("DEU") is True
    assert CountryGrammarRegistry.has("FRA") is True
    assert CountryGrammarRegistry.has("CYM") is True


def test_country_detection_heuristics():
    # Explicit country
    assert CountryGrammarRegistry.detect_country(country_raw="Canada") == "CAN"
    assert CountryGrammarRegistry.detect_country(country_raw="GBR") == "GBR"

    # State indicators
    assert CountryGrammarRegistry.detect_country(state_raw="Ontario") == "CAN"
    assert CountryGrammarRegistry.detect_country(state_raw="CA") == "USA"

    # City indicators
    assert CountryGrammarRegistry.detect_country(city_raw="Tokyo") == "JPN"

    # Postal indicators
    assert CountryGrammarRegistry.detect_country(postal_raw="M5V 2T6") == "CAN"
    assert CountryGrammarRegistry.detect_country(postal_raw="SW1A 1AA") == "GBR"

    # Raw street indicators
    assert CountryGrammarRegistry.detect_country(raw_street="Ugland House, Cayman Islands") == "CYM"
    assert CountryGrammarRegistry.detect_country(raw_street="100 High St, UK") == "GBR"
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St, Canada") == "CAN"
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St, Austin TX 78701") == "USA"
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St, France") == "FRA"
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St, Paris") == "FRA"
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St Germany") == "DEU"
    assert CountryGrammarRegistry.detect_country() == "USA"


def test_base_grammar_and_heuristics_edge_branches():
    # Only building name format_street1 empty street line branch
    c_bldg_only = ParsedAddressComponents(building_name="Tower House")
    assert c_bldg_only.format_street1() == "Tower House"

    univ = UniversalInternationalGrammar()
    # 75 Fort St / Church St offshore format in universal grammar
    p_fort = univ.standardize(street1="Ugland House, 75 Fort St, George Town, KY1-1104")
    assert p_fort.format_street1() == "75 FORT ST"
    assert p_fort.format_street2() == "UGLAND HOUSE"
    assert p_fort.city == "GEORGE TOWN"
    assert p_fort.postal_code == "KY1-1104"

    # Generic comma 3 parts where 3rd is postal code
    p_3part_post = univ.standardize(street1="100 Main St, Sydney, 2000")
    assert p_3part_post.format_street1() == "100 MAIN ST"
    assert p_3part_post.city == "SYDNEY"
    assert p_3part_post.postal_code == "2000"

    # CountryGrammarRegistry.get with valid country
    assert CountryGrammarRegistry.get("CAN") is not None

    # Country detection 3-letter alpha fallback
    assert CountryGrammarRegistry.detect_country(country_raw="ZZZ") == "ZZZ"

    # City indicator with diacritics folding
    assert CountryGrammarRegistry.detect_country(city_raw="Brasília") == "BRA"

    # Raw street with punctuation country abbreviation
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St, U.K.") == "GBR"

    # Raw street with multi-word country without commas
    assert CountryGrammarRegistry.detect_country(raw_street="100 Queen St New Zealand") == "NZL"

    # Raw street with diacritics city folding
    assert CountryGrammarRegistry.detect_country(raw_street="100 Main St, Brasília") == "BRA"



