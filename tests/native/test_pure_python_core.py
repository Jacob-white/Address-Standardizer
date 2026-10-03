"""
Unit Tests for Pure Python Acceleration Core Engine (_pure_python_core.py).
===========================================================================
Tests zero-external-C-dependency execution, domestic and international parsing,
phonetic blocking, deterministic key derivation, pre-allocated batch processing,
and engine capability introspection with 100% statement coverage.
"""

from address_standardizer import _pure_python_core
from address_standardizer.models import StandardizedAddress


class TestPurePythonCoreEngineBasics:
    """Tests basic introspection and phonetic utilities."""

    def test_engine_introspection(self):
        assert _pure_python_core.get_engine_name() == "PurePythonCore"
        assert _pure_python_core.is_native() is False
        caps = _pure_python_core.get_capabilities()
        assert caps["engine"] == "PurePythonCore"
        assert caps["is_native"] is False
        assert caps["version"] == "3.3.0"
        assert caps["pure_python"] is True
        assert caps["simd"] is False
        assert "throughput_tier" in caps

    def test_soundex_computation(self):
        assert _pure_python_core.compute_soundex("Washington") == "W252"
        assert _pure_python_core.compute_soundex("Montgomery") == "M532"
        assert _pure_python_core.compute_soundex("") == ""

    def test_phonetic_address_key_generation(self):
        key = _pure_python_core.generate_phonetic_address_key(
            street1="555 Montgomery St", postal_or_zip="94111", city="San Francisco"
        )
        assert key == "555|M532|94111"

        empty_key = _pure_python_core.generate_phonetic_address_key(street1="")
        assert empty_key is None

    def test_generate_keys(self):
        norm_key, bldg_key, phon_key = _pure_python_core.generate_keys(
            street1="100 Wall St",
            street2="Suite 400",
            city="New York",
            state="NY",
            postal_code="10005",
            country="USA",
        )
        assert norm_key == "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"
        assert bldg_key == "100 WALL ST||NEW YORK|NY|10005|USA"
        assert phon_key == "100|W400|10005"


class TestPurePythonStandardizeRecordUS:
    """Tests US domestic parsing through _pure_python_core.standardize_record."""

    def test_empty_record(self):
        # finalize=False
        std_raw = _pure_python_core.standardize_record(finalize=False)
        assert std_raw.address_status == "parse_failed"
        assert std_raw.normalized_address_key is None
        assert std_raw.country_iso3 == "USA"

        # finalize=True
        std_fin = _pure_python_core.standardize_record(finalize=True)
        assert std_fin.address_status == "parse_failed"
        assert std_fin.normalized_address_key is None
        assert std_fin.confidence_score is not None

    def test_garbage_record(self):
        for garbage in ("N/A", "NONE", "NULL", "UNKNOWN", "-", ".", "NO ADDRESS"):
            std_raw = _pure_python_core.standardize_record(street1=garbage, finalize=False)
            assert std_raw.address_status == "parse_failed"
            assert std_raw.normalized_address_key is None

            std_fin = _pure_python_core.standardize_record(street1=garbage, finalize=True)
            assert std_fin.address_status == "parse_failed"

    def test_tier1_fast_path_structured(self):
        # finalize=False
        std_raw = _pure_python_core.standardize_record(
            street1="100 Main St",
            street2="Suite 200",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
            finalize=False,
        )
        assert std_raw.street1 == "100 MAIN ST"
        assert std_raw.street2 == "STE 200"
        assert std_raw.city == "NEW YORK"
        assert std_raw.state == "NY"
        assert std_raw.postal_code == "10001"
        assert std_raw.normalized_address_key == "100 MAIN ST|STE 200|NEW YORK|NY|10001|USA"
        assert std_raw.building_key == "100 MAIN ST||NEW YORK|NY|10001|USA"
        assert std_raw.is_us is True
        assert std_raw.is_registered_agent_hub is False

        # finalize=True
        std_fin = _pure_python_core.standardize_record(
            street1="100 Main St",
            street2="Suite 200",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
            finalize=True,
        )
        assert std_fin.normalized_address_key == "100 MAIN ST|STE 200|NEW YORK|NY|10001|USA"
        assert std_fin.confidence_score is not None
        assert std_fin.routing_tier == "AUTO_PASS"

    def test_tier2_rule_based_queens_hyphenated(self):
        std = _pure_python_core.standardize_record(
            street1="123-45 82nd Ave",
            street2="Apt 4B",
            city="Kew Gardens",
            state="NY",
            postal_code="11415",
            finalize=False,
        )
        assert std.street1 == "123-45 82ND AVE"
        assert std.street2 == "APT 4B"
        assert std.normalized_address_key == "123-45 82ND AVE|APT 4B|KEW GARDENS|NY|11415|USA"

    def test_tier2_rule_based_queens_hyphenated_finalize(self):
        std = _pure_python_core.standardize_record(
            street1="123-45 82nd Ave",
            street2="Apt 4B",
            city="Kew Gardens",
            state="NY",
            postal_code="11415",
            finalize=True,
        )
        assert std.street1 == "123-45 82ND AVE"
        assert std.confidence_score is not None

    def test_tier2_rule_based_rural_route_and_po_box(self):
        std_rr = _pure_python_core.standardize_record(
            street1="RR 2 Box 152",
            city="Robinson",
            state="IL",
            postal_code="62428",
            finalize=False,
        )
        assert "RR 2" in std_rr.street1
        assert std_rr.normalized_address_key is not None

        std_po = _pure_python_core.standardize_record(
            street1="PO Box 789",
            city="Denver",
            state="CO",
            postal_code="80202",
            finalize=False,
        )
        assert std_po.street1 == "PO BOX 789"
        assert std_po.normalized_address_key == "PO BOX 789||DENVER|CO|80202|USA"

    def test_tier2_fuzzy_city_and_postal_healing(self):
        # Transposition of 19147 (PA) where 9 and 1 are swapped -> 91147 with +4
        std_plus4 = _pure_python_core.standardize_record(
            street1="500 South St",
            city="Phildelphia",  # typo
            state="PA",
            postal_code="91147-1234",  # transposition of 19147 with +4
            finalize=False,
            enable_fuzzy=True,
        )
        assert std_plus4.city == "PHILADELPHIA"
        assert std_plus4.postal_code == "19147-1234"

        # Transposition of 19147 (PA) 5-digit only
        std_5digit = _pure_python_core.standardize_record(
            street1="500 South St",
            city="Phildelphia",
            state="PA",
            postal_code="91147",
            finalize=False,
            enable_fuzzy=True,
        )
        assert std_5digit.city == "PHILADELPHIA"
        assert std_5digit.postal_code == "19147"

    def test_tier2_private_residence(self):
        std = _pure_python_core.standardize_record(
            street1="Private Residence",
            city="New York",
            state="NY",
            postal_code="10001",
            finalize=False,
        )
        assert std.street1 == "PRIVATE RESIDENCE"
        assert std.is_private_residence is True

    def test_tier2_rule_based_private_residence(self):
        # Bypasses fast-path because of Queens hyphenation or complex tokens
        std = _pure_python_core.standardize_record(
            street1="Private Residence 123-45 82nd Ave",
            city="Kew Gardens",
            state="NY",
            postal_code="11415",
            finalize=False,
        )
        assert std.street1 == "PRIVATE RESIDENCE"
        assert std.is_private_residence is True

    def test_tier2_registered_agent_hub(self):
        std = _pure_python_core.standardize_record(
            street1="1209 North Orange St",
            street2="Suite 100",
            city="Wilmington",
            state="DE",
            postal_code="19801",
            finalize=False,
        )
        assert std.street1 == "1209 N ORANGE ST"
        assert std.is_registered_agent_hub is True

    def test_tier2_street_equals_city_fails(self):
        std = _pure_python_core.standardize_record(
            street1="Boston",
            city="Boston",
            state="MA",
            postal_code="02108",
            finalize=False,
        )
        assert std.address_status == "parse_failed"
        assert std.normalized_address_key is None

    def test_tier2_parse_extracted_city_state_zip(self):
        # Input has empty city, state, zip; parser extracts them from single line
        std = _pure_python_core.standardize_record(
            street1="100 Main St, Austin, TX 78701",
            finalize=False,
        )
        assert std.street1 == "100 MAIN ST"
        assert std.city == "AUSTIN"
        assert std.state == "TX"
        assert std.postal_code == "78701"


class TestPurePythonStandardizeRecordInternational:
    """Tests international jurisdiction routing through _pure_python_core."""

    def test_uk_address(self):
        std = _pure_python_core.standardize_record(
            street1="15 High Street",
            street2="Headingley",
            city="Leeds",
            postal_code="LS6 2AA",
            country="GBR",
            finalize=False,
        )
        assert std.street1 == "15 HIGH ST"
        assert std.city == "LEEDS"
        assert std.country == "GBR"
        assert std.country_iso3 == "GBR"
        assert std.is_us is False
        assert std.normalized_address_key is not None
        assert "LS6 2AA|GBR" in std.normalized_address_key

    def test_canadian_address(self):
        std = _pure_python_core.standardize_record(
            street1="123 rue Saint-Denis",
            city="Montreal",
            state="QC",
            postal_code="H2X 3J8",
            country="CAN",
            finalize=False,
        )
        assert "123 RUE SAINT-DENIS" in std.street1
        assert std.country == "CAN"
        assert std.is_us is False

    def test_germanic_address(self):
        std = _pure_python_core.standardize_record(
            street1="Musterstraße 12",
            city="Berlin",
            postal_code="10115",
            country="DEU",
            finalize=False,
        )
        assert std.street1 == "MUSTERSTRASSE 12"
        assert std.country == "DEU"
        assert std.is_us is False

    def test_romance_address(self):
        std = _pure_python_core.standardize_record(
            street1="Calle Mayor 45, 2º B",
            city="Madrid",
            postal_code="28013",
            country="ESP",
            finalize=False,
        )
        assert "CALLE MAYOR 45" in std.street1
        assert std.country == "ESP"

    def test_offshore_address_finalize(self):
        std = _pure_python_core.standardize_record(
            street1="Ugland House South Church St",
            street2="PO Box 309",
            city="George Town",
            postal_code="KY1-1104",
            country="CYM",
            finalize=True,
        )
        assert "UGLAND HOUSE" in std.street1
        assert std.country == "CYM"
        assert std.is_registered_agent_hub is True
        assert std.confidence_score is not None

    def test_international_private_residence(self):
        std = _pure_python_core.standardize_record(
            street1="Private Residence",
            city="London",
            postal_code="SW1A 1AA",
            country="GBR",
            finalize=False,
        )
        assert std.street1 == "PRIVATE RESIDENCE"
        assert std.is_private_residence is True
        assert std.country == "GBR"

    def test_international_street_equals_city_fails(self):
        std = _pure_python_core.standardize_record(
            street1="Paris",
            city="Paris",
            postal_code="75001",
            country="FRA",
            finalize=False,
        )
        assert std.address_status == "parse_failed"
        assert std.normalized_address_key is None


class TestPurePythonStandardizeBatch:
    """Tests pre-allocated buffer batch processing in _pure_python_core."""

    def test_empty_batch(self):
        res = _pure_python_core.standardize_batch([])
        assert res == []

    def test_batch_heterogeneous_formats(self):
        records = [
            ("100 Main St", "Suite 200", "New York", "NY", "10001", "USA"),  # 6-tuple
            {"street1": "200 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"},  # dict
            "500 South St, Philadelphia, PA 19147",  # string
            ("PO Box 123",),  # 1-tuple
            None,  # invalid/empty fallback
        ]
        results = _pure_python_core.standardize_batch(records, chunk_size=5, finalize=False)
        assert len(results) == 5
        assert isinstance(results[0], StandardizedAddress)
        assert results[0].street1 == "100 MAIN ST"
        assert results[1].street1 == "200 WALL ST"
        assert results[2].city == "PHILADELPHIA"
        assert results[3].street1 == "PO BOX 123"
        assert results[4].address_status == "parse_failed"

    def test_batch_with_finalize(self):
        records = [
            ("100 Main St", "", "New York", "NY", "10001", "USA"),
            ("1209 North Orange St", "Suite 100", "Wilmington", "DE", "19801", "USA"),
        ]
        results = _pure_python_core.standardize_batch(records, finalize=True)
        assert len(results) == 2
        assert results[0].confidence_score is not None
        assert results[1].is_registered_agent_hub is True
