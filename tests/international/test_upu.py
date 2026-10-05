"""Unit and integration tests for Universal Postal Union (UPU S42) Address Formatter."""

from address_standardizer.international.base import ParsedAddressComponents
from address_standardizer.international.upu import format_upu_address
from address_standardizer.models import StandardizedAddress
from address_standardizer.standardizer import standardize_address


class TestUPUFormattingRegionalLayouts:
    """Verify UPU S42 envelope formatting across regional postal grammars."""

    def test_anglo_saxon_us_style(self):
        parsed = ParsedAddressComponents(
            street_number="100",
            street_name="Wall St",
            unit_type="Suite",
            unit_number="400",
            city="New York",
            state="NY",
            postal_code="10005",
            country_iso3="USA",
        )
        res = format_upu_address(parsed)
        expected = (
            "100 Wall St\n"
            "Suite 400\n"
            "New York, NY 10005\n"
            "UNITED STATES"
        )
        assert res == expected

    def test_anglo_saxon_with_recipient(self):
        parsed = ParsedAddressComponents(
            street_number="100",
            street_name="Wall St",
            city="New York",
            state="NY",
            postal_code="10005",
            country_iso3="USA",
        )
        res = format_upu_address(parsed, recipient="Jane Doe")
        expected = (
            "Jane Doe\n"
            "100 Wall St\n"
            "New York, NY 10005\n"
            "UNITED STATES"
        )
        assert res == expected

    def test_anglo_saxon_without_country_name(self):
        parsed = ParsedAddressComponents(
            street_number="100",
            street_name="Wall St",
            city="New York",
            state="NY",
            postal_code="10005",
            country_iso3="USA",
        )
        res = format_upu_address(parsed, include_country_name=False)
        expected = (
            "100 Wall St\n"
            "New York, NY 10005"
        )
        assert res == expected

    def test_anglo_saxon_uk_style(self):
        parsed = ParsedAddressComponents(
            street_number="10",
            street_name="Downing St",
            city="London",
            postal_code="SW1A 2AA",
            country_iso3="GBR",
        )
        res = format_upu_address(parsed, recipient="The Prime Minister")
        expected = (
            "The Prime Minister\n"
            "10 Downing St\n"
            "London SW1A 2AA\n"
            "UNITED KINGDOM"
        )
        assert res == expected

    def test_anglo_saxon_canada_style(self):
        parsed = ParsedAddressComponents(
            street_number="123",
            street_name="Yonge St",
            city="Toronto",
            state="ON",
            postal_code="M5V 2T6",
            country_iso3="CAN",
        )
        res = format_upu_address(parsed)
        expected = (
            "123 Yonge St\n"
            "Toronto, ON M5V 2T6\n"
            "CANADA"
        )
        assert res == expected

    def test_european_postal_first_germany(self):
        # Germanic postal first: <street> <house_number>\n<postal_code> <city>\n<COUNTRY>
        parsed = ParsedAddressComponents(
            street_number="43",
            street_name="Friedrichstraße",
            city="Berlin",
            postal_code="10117",
            country_iso3="DEU",
        )
        res = format_upu_address(parsed)
        expected = (
            "Friedrichstraße 43\n"
            "10117 Berlin\n"
            "GERMANY"
        )
        assert res == expected

    def test_european_postal_first_france(self):
        # France: <house_number> <street>\n<postal_code> <city>\n<COUNTRY>
        parsed = ParsedAddressComponents(
            street_number="10",
            street_name="Rue de la Paix",
            city="Paris",
            postal_code="75002",
            country_iso3="FRA",
        )
        res = format_upu_address(parsed)
        expected = (
            "10 Rue de la Paix\n"
            "75002 Paris\n"
            "FRANCE"
        )
        assert res == expected

    def test_european_postal_first_spain(self):
        parsed = ParsedAddressComponents(
            street_number="28",
            street_name="Calle Gran Vía",
            city="Madrid",
            postal_code="28013",
            country_iso3="ESP",
        )
        res = format_upu_address(parsed)
        expected = (
            "Calle Gran Vía 28\n"
            "28013 Madrid\n"
            "SPAIN"
        )
        assert res == expected

    def test_east_asian_japan_style(self):
        # Japan: 〒<postal_code>\n<state/prefecture><city><street>\n<COUNTRY>
        parsed = ParsedAddressComponents(
            street_name="丸の内1-1-1",
            city="千代田区",
            state="東京都",
            postal_code="100-0001",
            country_iso3="JPN",
        )
        res = format_upu_address(parsed, recipient="山田太郎")
        expected = (
            "山田太郎\n"
            "〒100-0001\n"
            "東京都千代田区丸の内1-1-1\n"
            "JAPAN"
        )
        assert res == expected

    def test_non_postal_nation_layout(self):
        # Non-postal nation (UAE): no postal code, NO blank line artifacts
        parsed = ParsedAddressComponents(
            street_name="Al Sufouh Rd",
            city="Dubai",
            country_iso3="ARE",
        )
        res = format_upu_address(parsed)
        expected = (
            "Al Sufouh Rd\n"
            "Dubai\n"
            "UNITED ARAB EMIRATES"
        )
        assert res == expected
        assert "\n\n" not in res  # Ensure zero empty lines

    def test_non_postal_qatar(self):
        parsed = ParsedAddressComponents(
            street_name="Corniche St",
            city="Doha",
            country_iso3="QAT",
        )
        res = format_upu_address(parsed)
        expected = (
            "Corniche St\n"
            "Doha\n"
            "QATAR"
        )
        assert res == expected
        assert "\n\n" not in res


class TestStandardizedAddressUPUIntegration:
    """Verify models.py integration with format_upu and 14-key contract."""

    def test_standardized_address_format_upu_method(self):
        std = StandardizedAddress(
            street1="100 WALL ST",
            street2="SUITE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|SUITE 400|NEW YORK|NY|10005|USA",
            address_status="valid",
            raw_street_address="100 Wall St Suite 400",
            is_us=True,
        )
        res = std.format_upu()
        expected = (
            "100 WALL ST\n"
            "SUITE 400\n"
            "NEW YORK, NY 10005\n"
            "UNITED STATES"
        )
        assert res == expected

    def test_standardize_address_end_to_end_upu(self):
        # End-to-end standardization pipeline
        std = standardize_address("100 Wall St Suite 400, New York, NY 10005")
        upu = std.format_upu(recipient="Acme Corp")
        assert upu == (
            "Acme Corp\n"
            "100 WALL ST\n"
            "STE 400\n"
            "NEW YORK, NY 10005\n"
            "UNITED STATES"
        )

    def test_strict_14_key_invariant(self):
        # CRITICAL INVARIANT: as_dict() must return EXACTLY the 14 canonical keys
        std = standardize_address("100 Wall St, New York, NY 10005")
        d = std.as_dict()
        assert len(d) == 14, f"Expected 14 keys, got {len(d)}: {list(d.keys())}"

        expected_14_keys = {
            "street1",
            "street2",
            "city",
            "state",
            "postal_code",
            "country",
            "normalized_address_key",
            "building_key",
            "phonetic_key",
            "address_status",
            "raw_street_address",
            "is_us",
            "is_private_residence",
            "is_registered_agent_hub",
        }
        assert set(d.keys()) == expected_14_keys
