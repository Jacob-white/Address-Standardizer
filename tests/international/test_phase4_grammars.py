"""Tests for Phase 4 dedicated international grammars:
- Hong Kong (HKG)
- Singapore (SGP)
- Australia (AUS)
- India (IND)
- Ireland (IRL)
"""


from address_standardizer import standardize_address
from address_standardizer.international import (
    CountryGrammarRegistry,
    HongKongGrammar,
    SingaporeGrammar,
    AustraliaGrammar,
    IndiaGrammar,
    IrelandGrammar,
    is_valid_eircode,
    format_eircode,
)


class TestGrammarRegistration:
    """Verifies all Phase 4 country grammars are registered in CountryGrammarRegistry."""

    def test_registered_types(self):
        assert isinstance(CountryGrammarRegistry.get("HKG"), HongKongGrammar)
        assert isinstance(CountryGrammarRegistry.get("HK"), HongKongGrammar)
        assert isinstance(CountryGrammarRegistry.get("HONG KONG"), HongKongGrammar)

        assert isinstance(CountryGrammarRegistry.get("SGP"), SingaporeGrammar)
        assert isinstance(CountryGrammarRegistry.get("SG"), SingaporeGrammar)
        assert isinstance(CountryGrammarRegistry.get("SINGAPORE"), SingaporeGrammar)

        assert isinstance(CountryGrammarRegistry.get("AUS"), AustraliaGrammar)
        assert isinstance(CountryGrammarRegistry.get("AU"), AustraliaGrammar)
        assert isinstance(CountryGrammarRegistry.get("AUSTRALIA"), AustraliaGrammar)

        assert isinstance(CountryGrammarRegistry.get("IND"), IndiaGrammar)
        assert isinstance(CountryGrammarRegistry.get("IN"), IndiaGrammar)
        assert isinstance(CountryGrammarRegistry.get("INDIA"), IndiaGrammar)

        assert isinstance(CountryGrammarRegistry.get("IRL"), IrelandGrammar)
        assert isinstance(CountryGrammarRegistry.get("IE"), IrelandGrammar)
        assert isinstance(CountryGrammarRegistry.get("IRELAND"), IrelandGrammar)


class TestHongKongGrammar:
    """Verifies Hong Kong address parsing, floor/flat handling, and district recognition."""

    def test_floor_and_flat_extraction(self):
        res = standardize_address("Flat A, 15/F, Two International Finance Centre, Central, Hong Kong")
        assert res.address_status == "standardized"
        assert res.country == "HKG"
        assert res.is_us is False
        assert "FLAT A" in (res.street2 or "")
        assert "15/F" in (res.street2 or "")
        assert res.city in ("CENTRAL", "HONG KONG")
        assert res.postal_code == ""  # HK has no domestic postal code

    def test_room_floor_and_premise(self):
        res = standardize_address("Room 1205, 12/F, Chater House, 8 Connaught Road, Central, Hong Kong")
        assert res.address_status == "standardized"
        assert res.country == "HKG"
        assert "1205" in (res.street2 or "")
        assert "8 CONNAUGHT RD" in res.street1 or "CHATER HOUSE" in (res.building_name or res.street1)

    def test_kowloon_district(self):
        res = standardize_address("Suite 801, 8/F, The Gateway Tower 1, Harbour City, Tsim Sha Tsui, Kowloon, Hong Kong")
        assert res.address_status == "standardized"
        assert res.country == "HKG"
        assert res.city in ("TSIM SHA TSUI", "KOWLOON")


class TestSingaporeGrammar:
    """Verifies Singapore address parsing, 6-digit postal code, and unit hashtags."""

    def test_postal_code_and_unit_hashtag(self):
        res = standardize_address("#08-01, 1 Raffles Place, Singapore 048616")
        assert res.address_status == "standardized"
        assert res.country == "SGP"
        assert res.postal_code == "048616"
        assert "#08-01" in (res.street2 or "")
        assert "1 RAFFLES PL" in res.street1
        assert res.city == "SINGAPORE"

    def test_marina_bay_tower(self):
        res = standardize_address("Level 24, Marina Bay Financial Centre Tower 1, 8 Marina Boulevard, Singapore 018981")
        assert res.address_status == "standardized"
        assert res.country == "SGP"
        assert res.postal_code == "018981"
        assert "8 MARINA BLVD" in res.street1
        assert "24" in (res.street2 or "")


class TestAustraliaGrammar:
    """Verifies Australia address parsing, state validation, and slash unit syntax."""

    def test_slash_unit_notation(self):
        res = standardize_address("5/100 George St, Sydney NSW 2000, Australia")
        assert res.address_status == "standardized"
        assert res.country == "AUS"
        assert res.street1 == "100 GEORGE ST"
        assert "5" in (res.street2 or "")
        assert res.city == "SYDNEY"
        assert res.state == "NSW"
        assert res.postal_code == "2000"

    def test_level_notation(self):
        res = standardize_address("Level 15, 225 George Street, Sydney NSW 2000, Australia")
        assert res.address_status == "standardized"
        assert res.country == "AUS"
        assert res.street1 == "225 GEORGE ST"
        assert "15" in (res.street2 or "")
        assert res.state == "NSW"
        assert res.postal_code == "2000"

    def test_level_slash_notation(self):
        res = standardize_address("Level 15/225 George St, Sydney NSW 2000, Australia")
        assert res.address_status == "standardized"
        assert res.country == "AUS"
        assert res.street1 == "225 GEORGE ST"
        assert res.street2 == "LEVEL 15"
        assert res.city == "SYDNEY"
        assert res.state == "NSW"
        assert res.postal_code == "2000"


    def test_postcode_state_validation(self):
        grammar = AustraliaGrammar()
        assert grammar.validate_postcode_state("2000", "NSW") is True
        assert grammar.validate_postcode_state("2000", "VIC") is False
        assert grammar.validate_postcode_state("3000", "VIC") is True
        assert grammar.validate_postcode_state("4000", "QLD") is True
        assert grammar.validate_postcode_state("6000", "WA") is True


class TestIndiaGrammar:
    """Verifies India address parsing, 6-digit PIN code, and SEZ / Sector handling."""

    def test_pin_code_and_sector(self):
        res = standardize_address("Plot 48, Sector 18, Gurugram, Haryana 122015, India")
        assert res.address_status == "standardized"
        assert res.country == "IND"
        assert res.postal_code == "122015"
        assert res.state == "HR"
        assert "SECTOR 18" in (res.street1 or res.street2 or res.dependent_locality or "")

    def test_tech_park_bengaluru(self):
        res = standardize_address("Bagmane Tech Park, CV Raman Nagar, Bengaluru, Karnataka 560093, India")
        assert res.address_status == "standardized"
        assert res.country == "IND"
        assert res.postal_code == "560093"
        assert res.state == "KA"
        assert "BENGALURU" in res.city or "BANGALORE" in res.city

    def test_mumbai_nariman_point(self):
        res = standardize_address("Maker Chambers IV, Nariman Point, Mumbai, Maharashtra 400021, India")
        assert res.address_status == "standardized"
        assert res.country == "IND"
        assert res.postal_code == "400021"
        assert res.state == "MH"
        assert res.city == "MUMBAI"


class TestIrelandGrammar:
    """Verifies Ireland address parsing, Eircode canonical formatting, and county normalization."""

    def test_eircode_validation_and_formatting(self):
        assert is_valid_eircode("D02 X285") is True
        assert is_valid_eircode("d02x285") is True
        assert is_valid_eircode("T12 C9D8") is True
        assert is_valid_eircode("INVALID") is False
        assert is_valid_eircode("") is False

        assert format_eircode("d02x285") == "D02 X285"
        assert format_eircode("T12-C9D8") == "T12 C9D8"

    def test_dublin_financial_district_address(self):
        res = standardize_address("10 Baggot Street Lower, Dublin 2, D02 X285, Ireland")
        assert res.address_status == "standardized"
        assert res.country == "IRL"
        assert "10 BAGGOT ST LOWER" in res.street1
        assert res.postal_code == "D02 X285"
        assert "DUBLIN" in res.city

    def test_ifsc_block_address(self):
        res = standardize_address("Block A, George's Dock House, IFSC, Dublin 1, Ireland")
        assert res.address_status == "standardized"
        assert res.country == "IRL"
        assert "GEORGE'S DOCK HOUSE" in (res.street1 or res.building_name or "")
        assert "BLOCK A" in (res.street2 or "")
        assert res.dependent_locality == "IFSC"
        assert "DUBLIN" in res.city

    def test_county_normalization(self):
        grammar = IrelandGrammar()
        p1 = grammar.standardize(street1="Main Street", city="Cork", state="Co. Cork", country="IRL")
        assert p1.state == "CO CORK"

        p2 = grammar.standardize(street1="High Street", city="Galway", state="County Galway", country="IRL")
        assert p2.state == "CO GALWAY"
