"""Coverage-driven tests for us_street_parser, _patterns, normalization and the standardizer pipeline glue."""

from types import SimpleNamespace

import pytest

from address_standardizer import standardizer as std_mod
from address_standardizer import us_street_parser as usp
from address_standardizer._patterns import (
    clean_redundant_street_tail,
    clean_repetitive_cycles,
    clean_rooftop_address,
    is_city_noise_in_street1,
    is_invalid_thoroughfare,
    parse_intersection_address,
)
from address_standardizer.normalization import normalize_country_code, normalize_us_postal_code
from address_standardizer.standardizer import _finalize_standardized_address, standardize_address
from address_standardizer.us_street_parser import (
    _move_trailing_house_number,
    _ordinal_floor_to_unit,
    _parse_us_address_components,
    _parse_us_street_tokens,
    _rule_based_us_street_parse,
)


@pytest.fixture
def crf(monkeypatch):
    """Replace the usaddress CRF with a canned tagging so tag-handling branches can be driven directly."""

    def install(tags):
        monkeypatch.setattr(usp, "usaddress", SimpleNamespace(parse=lambda _s: list(tags)))

    return install


@pytest.fixture
def no_crf(monkeypatch):
    monkeypatch.setattr(usp, "usaddress", None)


# --------------------------------------------------------------------------- us_street_parser: rule-based paths


class TestRuleBasedParser:
    def test_rural_route_and_highway_contract_with_a_house_number_are_ordinary_streets(self):
        # A leading house number means the RR/HC token is a unit-like suffix, not the whole address.
        assert _rule_based_us_street_parse("12 Oak Lane RR 2 Box 5") == ("12 OAK LN RR 2 BOX 5", "", True)
        assert _rule_based_us_street_parse("12 Oak Lane HC 2 Box 5") == ("12 OAK LN HC 2 BOX 5", "", True)

    def test_bare_rural_route_is_recognised(self):
        assert _rule_based_us_street_parse("RR 2 Box 5") == ("RR 2 BOX 5", "", True)
        assert _rule_based_us_street_parse("HC 3 Box 9") == ("HC 3 BOX 9", "", True)

    def test_military_unit_box(self):
        assert _rule_based_us_street_parse("UNIT 1234 BOX 5") == ("UNIT 1234 BOX 5", "", True)

    def test_descriptive_unit_word_becomes_secondary_unit(self):
        st1, st2, ok = _rule_based_us_street_parse("100 Main St Basement")
        assert (st1, st2, ok) == ("100 MAIN ST", "BSMT", True)


class TestTokenParserRoutes:
    def test_rural_route_with_house_number_stays_a_street_with_a_route_unit(self):
        res = _parse_us_street_tokens("12 Oak Lane RR 2 Box 5")
        assert tuple(res)[:3] == ("12 OAK LN", "RR 2 BOX 5", True)
        res = _parse_us_street_tokens("12 Oak Lane HC 2 Box 5")
        assert tuple(res)[:3] == ("12 OAK LN", "HC 2 BOX 5", True)

    def test_military_box_with_apo_tail(self):
        assert tuple(_parse_us_street_tokens("UNIT 1234 BOX 5, APO AE 09012")) == (
            "UNIT 1234 BOX 5", "", True, "APO", "AE", "09012",
        )

    def test_dangling_preposition_before_the_city_is_dropped(self):
        assert tuple(_parse_us_street_tokens("100 Main St de, Denver, CO 80202")) == (
            "100 MAIN ST", "", True, "Denver", "CO", "80202",
        )

    def test_ordinal_word_before_floor_with_street_type_is_a_street_name(self):
        m = usp._RE_ORDINAL_FLOOR.search("100 Fifth Floor Rd")
        assert _ordinal_floor_to_unit(m) == m.group(0)
        m = usp._RE_ORDINAL_FLOOR.search("Fifth Floor")
        assert _ordinal_floor_to_unit(m) == "FL 5"
        m = usp._RE_ORDINAL_FLOOR.search("Bogus Floor")
        assert _ordinal_floor_to_unit(m) == m.group(0)


class TestTokenParserFallbackWithoutCrf:
    """The usaddress package is optional: the right-to-left anchor parser takes over when it is absent."""

    def test_po_box_directly_before_state_zip_has_no_city(self, no_crf):
        assert tuple(_parse_us_street_tokens("PO Box 5 CO 80202")) == ("PO BOX 5", "", True, "", "CO", "80202")

    def test_po_box_followed_by_a_city_splits_the_city_off(self, no_crf):
        assert tuple(_parse_us_street_tokens("PO Box 5 Denver CO 80202")) == ("PO BOX 5", "", True, "Denver", "CO", "80202")

    def test_street_without_suffix_keeps_everything_as_street(self, no_crf):
        assert tuple(_parse_us_street_tokens("100 Foo CO 80202")) == ("100 FOO", "", True, "", "CO", "80202")

    def test_unit_word_at_the_end_has_no_value_to_consume(self, no_crf):
        assert tuple(_parse_us_street_tokens("100 Main St Apt CO 80202"))[0] == "100 MAIN ST APT"

    def test_unit_word_followed_by_punctuation_only_value(self, no_crf):
        res = tuple(_parse_us_street_tokens("100 Main St Apt ## Denver CO 80202"))
        assert res[0] == "100 MAIN ST APT"
        assert res[3:] == ("## Denver", "CO", "80202")

    def test_unit_with_value_then_city(self, no_crf):
        assert tuple(_parse_us_street_tokens("100 Main St Apt 5 Denver CO 80202")) == (
            "100 MAIN ST", "APT 5", True, "Denver", "CO", "80202",
        )

    def test_missing_street_digits_means_the_text_is_the_city(self, no_crf):
        assert tuple(_parse_us_street_tokens("Denver CO 80202")) == ("", "", False, "Denver", "CO", "80202")


# --------------------------------------------------------------------------- us_street_parser: CRF tag handling


class TestCrfTagHandling:
    def test_standalone_unit_word_at_the_end(self, crf):
        crf([("100", "AddressNumber"), ("Main", "StreetName"), ("St", "StreetNamePostType"), ("Penthouse", "PlaceName")])
        assert tuple(_parse_us_street_tokens("x"))[:2] == ("100 MAIN ST", "PH")

    def test_standalone_unit_word_followed_by_non_identifier(self, crf):
        crf([("100", "AddressNumber"), ("Main", "StreetName"), ("St", "StreetNamePostType"),
             ("Penthouse", "PlaceName"), ("Foo", "PlaceName")])
        res = tuple(_parse_us_street_tokens("x"))
        assert res[:2] == ("100 MAIN ST", "PH")
        assert res[3] == "FOO"

    def test_recipient_run_after_a_spanish_thoroughfare_skips_punctuation_tokens(self, crf):
        crf([("Calle", "Recipient"), ("-", "Recipient"), ("Luna", "Recipient"), ("5", "AddressNumber")])
        assert tuple(_parse_us_street_tokens("x"))[0] == "CALLE LUNA 5"

    def test_country_and_notaddress_tags_are_ignored(self, crf):
        crf([("100", "AddressNumber"), ("Main", "StreetName"), ("St", "StreetNamePostType"),
             ("USA", "CountryName"), ("junk", "NotAddress")])
        assert tuple(_parse_us_street_tokens("x"))[:2] == ("100 MAIN ST", "")

    def test_landmark_inside_a_numbered_address_becomes_the_building_name(self, crf):
        crf([("100", "AddressNumber"), ("Acme", "LandmarkName"), ("Main", "StreetName"), ("St", "StreetNamePostType")])
        res = _parse_us_street_tokens("x")
        assert tuple(res)[:2] == ("100 MAIN ST", "ACME")
        assert res.building_name == "ACME"

    def test_street_type_misfiled_as_zip_is_rescued_onto_the_city_words(self, crf):
        crf([("Elm", "PlaceName"), ("Ave", "ZipCode")])
        assert tuple(_parse_us_street_tokens("x"))[:2] == ("ELM AVE", "")

    def test_properly_tagged_zip_is_not_taken_as_a_street_number(self, crf):
        crf([("Calle", "StreetName"), ("Luna", "StreetName"), ("00901", "ZipCode")])
        assert tuple(_parse_us_street_tokens("Calle Luna, San Juan PR 00901")) == (
            "CALLE LUNA", "", True, "San Juan", "PR", "00901",
        )

    def test_premise_name_followed_by_unit_is_the_street(self, crf):
        crf([("Acme Plaza", "PlaceName"), ("Suite", "OccupancyType"), ("200", "OccupancyIdentifier")])
        assert tuple(_parse_us_street_tokens("x"))[:2] == ("ACME PLAZA", "STE 200")

    def test_cataloged_commercial_hub_in_the_place_slot_is_the_street(self, crf):
        crf([("Canary Wharf", "PlaceName")])
        assert tuple(_parse_us_street_tokens("x")) == ("CANARY WHARF", "", True, "", "", "")

    def test_place_name_alone_is_a_city_unless_a_different_city_was_supplied(self, crf):
        crf([("Acme", "PlaceName")])
        assert tuple(_parse_us_street_tokens("x")) == ("", "", True, "ACME", "", "")
        assert tuple(_parse_us_street_tokens("x", city_raw="Boston"))[0] == "ACME"

    def test_place_name_differing_from_the_csz_city_is_a_street(self, crf):
        crf([("Acme", "PlaceName")])
        res = tuple(_parse_us_street_tokens("Foo, Denver, CO 80202"))
        assert res == ("ACME", "", True, "Denver", "CO", "80202")

    def test_empty_crf_result_falls_back_to_rule_based_parse_for_street_and_unit(self, crf):
        crf([])
        assert tuple(_parse_us_street_tokens("100 Main St, Suite 5"))[:2] == ("100 MAIN ST", "STE 5")

    def test_empty_crf_result_with_landmark_premise_and_csz_uses_rule_based_parse(self, crf):
        crf([])
        assert tuple(_parse_us_street_tokens("Executive Campus, Denver, CO 80202")) == (
            "EXECUTIVE CP", "", True, "Denver", "CO", "80202",
        )

    def test_empty_crf_result_hub_with_unit_keeps_the_unit(self, crf):
        crf([])
        assert tuple(_parse_us_street_tokens("Executive Campus Suite 5, Denver, CO 80202")) == (
            "EXECUTIVE CP", "STE 5", True, "Denver", "CO", "80202",
        )

    def test_empty_crf_result_where_rule_based_parse_finds_only_a_unit_leaves_street_empty(self, crf):
        crf([])
        res = tuple(_parse_us_street_tokens("Building 5, Denver, CO 80202"))
        assert res[0] == "" and res[3:] == ("Denver", "CO", "80202")

    def test_hub_name_keeps_its_city_when_the_caller_supplied_one(self, crf):
        crf([("Canary Wharf", "PlaceName")])
        assert tuple(_parse_us_street_tokens("x", city_raw="London")) == ("CANARY WHARF", "", True, "CANARY WHARF", "", "")

    def test_empty_crf_result_with_plain_text_and_csz_leaves_street_empty(self, crf):
        crf([])
        assert tuple(_parse_us_street_tokens("Foo Bar, Denver, CO 80202")) == ("", "", True, "Denver", "CO", "80202")
        assert tuple(_parse_us_street_tokens(", Denver, CO 80202")) == ("", "", True, "Denver", "CO", "80202")

    def test_street_that_merely_repeats_the_supplied_city_is_blanked(self, crf, monkeypatch):
        monkeypatch.setattr(usp, "clean_redundant_street_tail", lambda s, **_k: s)
        crf([("Springfield", "StreetName")])
        assert tuple(_parse_us_address_components("Springfield", city_raw="Springfield"))[:3] == ("", "", True)


# --------------------------------------------------------------------------- us_street_parser: component assembly


class TestComponentAssembly:
    def test_trailing_house_number_and_farm_to_market(self):
        assert _parse_us_address_components("St. Louis Ave 100")[0] == "100 ST LOUIS AVE"
        assert _parse_us_address_components("Farm to Market Road 1960")[0] == "FM 1960"
        assert _parse_us_address_components("County Road 12")[0] == "COUNTY RD 12"

    def test_street_type_after_a_leading_saint_is_not_moved(self):
        assert _move_trailing_house_number("St Ave 100") == "St Ave 100"
        assert _move_trailing_house_number("Elm Street 12") == "12 Elm Street"
        assert _move_trailing_house_number("Elm 12") == "Elm 12"

    def test_puerto_rico_highway_markers(self):
        assert tuple(_parse_us_address_components("PR #2 KM 82 HM. 2")) == ("PR-2 KM 82.2", "", True, "", "", "")
        assert tuple(_parse_us_address_components("PR-2 KM 82.2 Bldg 5"))[:2] == ("PR-2 KM 82.2", "BLDG 5")
        assert tuple(_parse_us_address_components("CARR 167 KM 15"))[:2] == ("CARR-167 KM 15", "")

    def test_empty_input_is_not_ok(self):
        assert tuple(_parse_us_address_components("", "")) == ("", "", False, "", "", "")
        assert tuple(_parse_us_address_components("   ", ""))[2] is False

    def test_urbanization_line_with_thoroughfare_in_street2(self):
        res = _parse_us_address_components("Urb Las Flores", "Calle 5 #12")
        assert tuple(res)[:2] == ("URB LAS FLORES CALLE 5", "STE 12")

    def test_urbanization_line_with_po_box_in_street2_keeps_the_box(self):
        assert tuple(_parse_us_address_components("Urb Las Flores", "PO Box 5"))[:2] == ("URB LAS FLORES", "PO BOX 5")

    def test_urbanization_line_with_only_a_unit_in_street2_is_not_a_thoroughfare(self):
        res = _parse_us_address_components("Urb Las Flores", "Apt 5")
        assert "URB LAS FLORES" in res[0] and "5" in res[1]

    def test_po_box_in_either_line(self):
        assert tuple(_parse_us_address_components("100 Main St", "PO Box 5"))[:2] == ("100 MAIN ST", "PO BOX 5")
        assert tuple(_parse_us_address_components("PO Box 5", "100 Main St"))[:2] == ("100 MAIN ST", "PO BOX 5")
        assert tuple(_parse_us_address_components("PO Box 5, Denver CO 80202")) == (
            "PO BOX 5", "", True, "DENVER", "CO", "80202",
        )
        assert tuple(_parse_us_address_components("PO Box 5")) == ("PO BOX 5", "", True, "", "", "")

    def test_two_physical_street_lines_keep_both(self):
        assert tuple(_parse_us_address_components("100 Main St", "200 Oak Ave"))[:2] == ("100 MAIN ST", "200 OAK AVE")

    def test_second_line_that_is_a_numbered_unit_is_not_a_second_street(self):
        # "200 Ste 5": the word after the number is a unit designator, so the dual-street rule does not apply.
        res = _parse_us_address_components("100 Main St", "200 Ste 5")
        assert res[0] == "100 MAIN ST"
        assert "STE" in res[1]

    def test_second_line_numbered_street_without_a_street_type_is_not_a_second_street(self):
        res = _parse_us_address_components("100 Main St", "200 Oak")
        assert res[0] == "100 MAIN ST"
        assert res[1] != "200 OAK"


# --------------------------------------------------------------------------- _patterns


class TestPatternHelpers:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("   ", True),
            ("(HELLO)", True),
            ("A&B", True),
            ("ONE", True),
            ("AVE", True),
            ("A1", True),
            ("5C", True),
            ("Main", False),
            ("BROADWAY", False),
        ],
    )
    def test_is_invalid_thoroughfare(self, text, expected):
        assert is_invalid_thoroughfare(text) is expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Main N and Elm St", "MAIN N & ELM ST"),
            ("Main St at Elm St", "MAIN ST & ELM ST"),
            ("Main St @ Elm Ave", "MAIN ST & ELM AVE"),
            ("Main St and Fourth Streets", "MAIN ST & 4TH ST"),
            ("Routes 60 And 155", "RT 60 & RT 155"),
            ("Corner of 5th Ave and 42nd St", "5TH AVE & 42ND ST"),
            ("Route 5 and Highways 9 St", "RTE 5 & HWY 9 ST"),
            ("Main and Elm", None),
            ("Suite 5 and Elm St", None),
            ("Elm St and Suite 5", None),
            ("Main St at Elm", None),
            ("The Shops at Main St", None),
            ("a and", None),
        ],
    )
    def test_parse_intersection_address(self, text, expected):
        assert parse_intersection_address(text) == expected

    def test_plural_route_and_highway_words_are_abbreviated(self):
        from address_standardizer._patterns import _normalize_intersection_branch

        assert _normalize_intersection_branch("routes 5 highways 9") == "RT 5 HWY 9"

    def test_redundant_tail_stripping_stops_after_four_passes(self):
        got = clean_redundant_street_tail("100 Main St Denver, Denver, Denver, Denver, Denver", city="Denver")
        assert got == "100 Main St Denver"

    def test_postal_code_variants_at_the_end(self):
        assert clean_redundant_street_tail("100 Main St H2X1Y4", postal_code="H2X 1Y4") == "100 Main St"
        assert clean_redundant_street_tail("100 Main St 80202", postal_code="80202-1234") == "100 Main St"

    def test_canadian_postcode_tail_is_removed_when_no_postal_code_is_supplied(self):
        assert clean_redundant_street_tail("100 Main St, Montreal QC H2X 1Y4") == "100 Main St, Montreal QC"

    def test_blank_state_or_city_and_numeric_remainders_are_left_alone(self):
        assert clean_redundant_street_tail("100 Main St CO", state="  ") == "100 Main St CO"
        assert clean_redundant_street_tail("100 CO", state="CO") == "100 CO"
        assert clean_redundant_street_tail("100 Main St Denver", city="  ") == "100 Main St Denver"
        assert clean_redundant_street_tail("100 Denver", city="Denver") == "100 Denver"
        assert clean_redundant_street_tail("100 de Denver", city="Denver") == "100 de"
        assert clean_redundant_street_tail("Calle de Denver", city="Denver") == "Calle"

    def test_repetition_collapse_keeps_one_unit(self):
        assert clean_repetitive_cycles("STE 4075 4075 4075") == "STE 4075"
        assert clean_repetitive_cycles("100 Main St 100 Main") == "100 Main St 100 Main"

    @pytest.mark.parametrize(
        "s1,city,state,expected",
        [
            ("CO", "Denver", "CO", True),
            ("HALF MOON", "Half Moon Bay", "", True),
            ("S BND IN", "South Bend", "IN", True),
            ("CHADDS FRD", "Chadds Ford", "", True),
            ("XYZ IN", "South Bend", "IN", False),
            ("100 Main St", "Denver", "CO", False),
            ("", "Denver", "CO", False),
        ],
    )
    def test_city_noise_in_street1(self, s1, city, state, expected):
        assert is_city_noise_in_street1(s1, city, state) is expected

    def test_rooftop_address_cleaning(self):
        assert clean_rooftop_address("ST") is None
        assert clean_rooftop_address("100 MAIN ST APT 5") == "100 MAIN ST"
        # every trailing unit is stripped (up to a bound of eight)
        assert clean_rooftop_address("100 MAIN ST APT 5 STE 6 FL 2 RM 3") == "100 MAIN ST"
        # a "#N" whose identifier is a directional is not a unit
        assert clean_rooftop_address("100 MAIN #N") == "100 MAIN #N"
        # a bare building word is only a unit after a street type or a comma
        assert clean_rooftop_address("100 MAIN BLDG") == "100 MAIN BLDG"
        assert clean_rooftop_address("100 MAIN ST BLDG") == "100 MAIN ST"


# --------------------------------------------------------------------------- normalization


class TestNormalizationEdges:
    def test_country_names_resolve_through_the_registry(self):
        assert normalize_country_code("Deutschland") == "DEU"
        assert normalize_country_code("México") == "MEX"
        assert normalize_country_code("Puerto Rico") == "PRI"

    def test_us_territory_country_without_us_state_keeps_the_territory(self):
        assert normalize_country_code("Guam", "", "") == "GUM"

    def test_global_metro_city_is_not_foreign_when_state_is_a_us_state(self):
        assert normalize_country_code("", "OH", "", city_raw="London") == "USA"
        assert normalize_country_code("", "", "", city_raw="London") == "GBR"

    def test_trailing_state_code_inside_last_component_means_usa(self):
        assert normalize_country_code("", "", "", raw_street="Foo, Denver CO") == "USA"

    def test_single_component_country_name(self):
        assert normalize_country_code("", "", "", raw_street="Panama") == "PAN"
        assert normalize_country_code("", "", "", raw_street="Germany 10115") == "DEU"
        assert normalize_country_code("", "", "", raw_street="x, Germany 10115 Foo, Bar") == "DEU"

    def test_country_abbreviation_with_punctuation_is_matched_without_dots(self):
        assert normalize_country_code("", "", "", raw_street="U.A.E., Foo Bar") == "ARE"

    def test_metro_with_number_suffix_or_prefix(self):
        assert normalize_country_code("", "", "", raw_street="Paris 75008, Foo") == "FRA"
        assert normalize_country_code("", "", "", raw_street="75008 Paris, Foo") == "FRA"
        assert normalize_country_code("", "", "", raw_street="75008 Zürich, Foo") == "CHE"
        assert normalize_country_code("", "", "", raw_street="75008 Zúrich, Foo") == "CHE"  # accent variant
        assert normalize_country_code("", "", "", raw_street="10115 Germany, Foo") == "DEU"

    def test_street_suffix_component_is_never_mistaken_for_a_country(self):
        assert normalize_country_code("", "", "", raw_street="Foo, Dr, Bar") == "USA"

    def test_postal_code_normalisation(self):
        assert normalize_us_postal_code("   ") == ("", "")
        assert normalize_us_postal_code("1234") == ("01234", "01234")
        assert normalize_us_postal_code("12 345") == ("12345", "12345")
        assert normalize_us_postal_code("12-345") == ("12-345", "")
        assert normalize_us_postal_code("123456789") == ("12345-6789", "12345")


# --------------------------------------------------------------------------- standardizer pipeline glue


def _addr_kwargs():
    return dict(street1="100 Main St", city="Denver", state="CO", postal_code="80202")


class TestFinalizeGeocoding:
    def _std(self):
        return standardize_address(**_addr_kwargs())

    def test_geocode_results_are_copied_onto_the_address_and_enriched(self, monkeypatch):
        sp = SimpleNamespace(latitude=1.0, longitude=2.0, precision="RANGE_INTERPOLATED", accuracy_radius_meters=9.0,
                             metadata={})
        monkeypatch.setattr("address_standardizer.spatial.resolve_spatial_coordinates", lambda _a: sp)
        monkeypatch.setattr(
            "address_standardizer.geocoder.geocode_offline",
            lambda *_a, **_k: {"census_tract": "T1", "fips_code": "F1"},
        )
        out = _finalize_standardized_address(self._std(), None, None, enable_geocoding=True)
        assert (out.latitude, out.longitude, out.precision) == (1.0, 2.0, "RANGE_INTERPOLATED")
        assert out.census_tract == "T1" and out.fips_code == "F1"
        assert sp.metadata == {"census_tract": "T1", "fips_code": "F1"}

    def test_offline_reference_fills_in_when_the_spatial_engine_is_unresolved(self, monkeypatch):
        sp = SimpleNamespace(latitude=0.0, longitude=0.0, precision="UNRESOLVED", accuracy_radius_meters=0.0, metadata={})
        geo = {"latitude": 5.0, "longitude": 6.0, "precision": "ROOFTOP", "accuracy_radius_meters": 3.0}
        monkeypatch.setattr("address_standardizer.spatial.resolve_spatial_coordinates", lambda _a: sp)
        monkeypatch.setattr("address_standardizer.geocoder.geocode_offline", lambda *_a, **_k: geo)
        out = _finalize_standardized_address(self._std(), None, None, enable_geocoding=True)
        assert (out.latitude, out.longitude, out.precision, out.accuracy_radius_meters) == (5.0, 6.0, "ROOFTOP", 3.0)

    def test_missing_spatial_result_is_tolerated_and_offline_reference_still_applies(self, monkeypatch):
        geo = {"census_tract": "T9", "fips_code": "F9", "latitude": 7.0, "longitude": 8.0, "precision": "ROOFTOP",
               "accuracy_radius_meters": 4.0}
        monkeypatch.setattr("address_standardizer.spatial.resolve_spatial_coordinates", lambda _a: None)
        monkeypatch.setattr("address_standardizer.geocoder.geocode_offline", lambda *_a, **_k: geo)
        out = _finalize_standardized_address(self._std(), None, None, enable_geocoding=True)
        assert out.spatial_result is None
        assert (out.latitude, out.census_tract, out.fips_code) == (7.0, "T9", "F9")

    def test_spatial_result_without_metadata_dict_is_left_untouched(self, monkeypatch):
        sp = SimpleNamespace(latitude=1.0, longitude=2.0, precision="ROOFTOP", accuracy_radius_meters=3.0, metadata=None)
        monkeypatch.setattr("address_standardizer.spatial.resolve_spatial_coordinates", lambda _a: sp)
        monkeypatch.setattr(
            "address_standardizer.geocoder.geocode_offline",
            lambda *_a, **_k: {"census_tract": "T2", "fips_code": "F2"},
        )
        out = _finalize_standardized_address(self._std(), None, None, enable_geocoding=True)
        assert out.census_tract == "T2" and out.fips_code == "F2"
        assert sp.metadata is None

    def test_no_offline_geocode_leaves_spatial_result_as_is(self, monkeypatch):
        sp = SimpleNamespace(latitude=1.0, longitude=2.0, precision="ROOFTOP", accuracy_radius_meters=3.0, metadata={})
        monkeypatch.setattr("address_standardizer.spatial.resolve_spatial_coordinates", lambda _a: sp)
        monkeypatch.setattr("address_standardizer.geocoder.geocode_offline", lambda *_a, **_k: None)
        out = _finalize_standardized_address(self._std(), None, None, enable_geocoding=True)
        assert (out.latitude, out.longitude) == (1.0, 2.0)
        assert out.census_tract is None

    def test_disabled_cache_is_not_written(self, monkeypatch):
        class Off:
            def is_enabled(self):
                return False

            def set(self, *_a):
                raise AssertionError("a disabled cache must not be written")

        monkeypatch.setattr(std_mod, "get_default_cache", lambda: Off())
        out = _finalize_standardized_address(self._std(), None, "some-key")
        assert out.street1 == "100 MAIN ST"


class TestStandardizerInputCleaning:
    def test_city_field_bleed_lines_are_split_into_unit_and_city(self):
        res = standardize_address(street1="100 Main St", street2="Rm 2", city="Denver\nSuite 5\nFloor 3", state="CO",
                                  postal_code="80202")
        assert res.street2 == "RM 2 STE 5 FL 3"
        assert res.city == "DENVER"

    def test_office_label_lines_in_city_are_dropped(self):
        res = standardize_address(street1="100 Main St", city="Denver\nMain Office\nSuite 5", state="CO", postal_code="80202")
        assert (res.city, res.street2) == ("DENVER", "STE 5")

    def test_trailing_office_word_is_removed_from_city(self):
        for city in ("Denver Office", "Denver Branch Office"):
            res = standardize_address(street1="100 Main St", city=city, state="CO", postal_code="80202")
            assert res.city == "DENVER"

    def test_street_field_bleed_extra_units_are_merged_without_duplicates(self):
        res = standardize_address(street1="100 Main St\nSuite 5\nSuite 6", street2="Suite 5", city="Denver", state="CO",
                                  postal_code="80202")
        assert res.street1 == "100 MAIN ST"
        assert res.street2 == "STE 5 STE 6"

    def test_street_equal_to_city_is_not_a_street(self):
        res = standardize_address(street1="Denver", city="Denver", state="CO", postal_code="80202")
        assert res.address_status == "parse_failed"
        res = standardize_address(street1="Denver", city="Denver", state="CO", postal_code="80202", allow_locality=True)
        assert res.address_status == "locality_only"

    def test_script_text_with_a_structured_city_keeps_the_given_city(self):
        for kwargs in ({"country": "JP"}, {}):
            res = standardize_address(street1="東京都渋谷区1-1", city="Tokyo", **kwargs)
            assert res.city == "TOKYO"
            assert res.street1.startswith("東京")
        assert res.country == "JPN"

    def test_street_that_normalises_to_the_city_name_is_dropped(self):
        res = standardize_address(street1="Fort Worth", city="Ft Worth", state="CO", postal_code="80202")
        assert res.street1 == ""
        assert res.city == "FORT WORTH"
        assert res.address_status == "parse_failed"

    def test_state_correction_for_single_line_input(self):
        res = standardize_address(street1="100 Main St, Los Angeles, NY 90012", correct_state_from_zip=True)
        assert res.state == "CA"
        res = standardize_address(street1="100 Main St, Los Angeles", correct_state_from_zip=True)
        assert res.state == ""
