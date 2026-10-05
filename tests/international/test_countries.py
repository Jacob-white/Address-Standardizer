"""Unit and integration tests for ISO-3166-1 Universal Country Registry."""

from address_standardizer import standardize_address
from address_standardizer.international.countries import CountryInfo, CountryRegistry
from address_standardizer.standardizer import normalize_country_code
from address_standardizer.tables import COUNTRY_MAP


class TestCountryRegistryCatalog:
    """Verify completeness and structural integrity of the 249 ISO-3166-1 catalog."""

    def test_all_249_countries_present(self):
        countries = CountryRegistry.all_countries()
        iso3_set = CountryRegistry.all_iso3()

        assert len(countries) == 249, f"Expected 249 countries, got {len(countries)}"
        assert len(iso3_set) == 249, f"Expected 249 ISO3 codes, got {len(iso3_set)}"

    def test_every_country_has_valid_fields(self):
        valid_regions = {"Africa", "Americas", "Asia", "Europe", "Oceania", "Antarctica"}
        alpha2_seen = set()
        alpha3_seen = set()
        numeric_seen = set()

        for c in CountryRegistry.all_countries():
            assert isinstance(c, CountryInfo)
            # Alpha-2
            assert len(c.alpha2) == 2, f"Invalid alpha2: {c.alpha2}"
            assert c.alpha2.isupper(), f"alpha2 not uppercase: {c.alpha2}"
            assert c.alpha2 not in alpha2_seen, f"Duplicate alpha2: {c.alpha2}"
            alpha2_seen.add(c.alpha2)

            # Alpha-3
            assert len(c.alpha3) == 3, f"Invalid alpha3: {c.alpha3}"
            assert c.alpha3.isupper(), f"alpha3 not uppercase: {c.alpha3}"
            assert c.alpha3 not in alpha3_seen, f"Duplicate alpha3: {c.alpha3}"
            alpha3_seen.add(c.alpha3)

            # Numeric (3 digits with leading zeroes)
            assert len(c.numeric) == 3, f"Invalid numeric: {c.numeric}"
            assert c.numeric.isdigit(), f"Numeric not all digits: {c.numeric}"
            assert c.numeric not in numeric_seen, f"Duplicate numeric: {c.numeric}"
            numeric_seen.add(c.numeric)

            # Name and Region
            assert c.name and len(c.name.strip()) > 0, "Empty name"
            assert c.region in valid_regions, f"Invalid region: {c.region} for {c.alpha3}"
            assert isinstance(c.has_postal_codes, bool)
            assert isinstance(c.native_names, tuple)
            assert isinstance(c.aliases, tuple)


class TestCountryRegistryLookups:
    """Verify lookup mechanics across all identifiers and edge cases."""

    def test_lookup_all_249_by_alpha2(self):
        for c in CountryRegistry.all_countries():
            found = CountryRegistry.get(c.alpha2)
            assert found is not None, f"Failed to look up alpha2 {c.alpha2}"
            assert found.alpha3 == c.alpha3

    def test_lookup_all_249_by_alpha3(self):
        for c in CountryRegistry.all_countries():
            found = CountryRegistry.get(c.alpha3)
            assert found is not None, f"Failed to look up alpha3 {c.alpha3}"
            assert found.alpha3 == c.alpha3

    def test_lookup_all_249_by_numeric(self):
        for c in CountryRegistry.all_countries():
            found = CountryRegistry.get(c.numeric)
            assert found is not None, f"Failed to look up numeric {c.numeric}"
            assert found.alpha3 == c.alpha3

    def test_lookup_all_249_by_name(self):
        for c in CountryRegistry.all_countries():
            found = CountryRegistry.get(c.name)
            assert found is not None, f"Failed to look up name {c.name}"
            assert found.alpha3 == c.alpha3

    def test_case_insensitivity(self):
        test_queries = [
            ("usa", "USA"),
            ("Usa", "USA"),
            ("uSa", "USA"),
            ("deu", "DEU"),
            ("de", "DEU"),
            ("jp", "JPN"),
            ("jpn", "JPN"),
            ("united states", "USA"),
            ("germany", "DEU"),
            ("japan", "JPN"),
            ("france", "FRA"),
            ("united arab emirates", "ARE"),
        ]
        for query, expected_iso3 in test_queries:
            res = CountryRegistry.get(query)
            assert res is not None, f"Query '{query}' returned None"
            assert res.alpha3 == expected_iso3

    def test_numeric_stripped_zeros(self):
        # 004 -> Afghanistan
        assert CountryRegistry.get("4").alpha3 == "AFG"
        assert CountryRegistry.get("004").alpha3 == "AFG"
        # 076 -> Brazil
        assert CountryRegistry.get("76").alpha3 == "BRA"
        assert CountryRegistry.get("076").alpha3 == "BRA"

    def test_aliases(self):
        assert CountryRegistry.get("UK").alpha3 == "GBR"
        assert CountryRegistry.get("Great Britain").alpha3 == "GBR"
        assert CountryRegistry.get("England").alpha3 == "GBR"
        assert CountryRegistry.get("Scotland").alpha3 == "GBR"
        assert CountryRegistry.get("UAE").alpha3 == "ARE"
        assert CountryRegistry.get("Dubai").alpha3 == "ARE"
        assert CountryRegistry.get("Abu Dhabi").alpha3 == "ARE"
        assert CountryRegistry.get("Holland").alpha3 == "NLD"
        assert CountryRegistry.get("South Korea").alpha3 == "KOR"
        assert CountryRegistry.get("North Korea").alpha3 == "PRK"
        assert CountryRegistry.get("Taiwan").alpha3 == "TWN"
        assert CountryRegistry.get("Cayman").alpha3 == "CYM"
        assert CountryRegistry.get("BVI").alpha3 == "VGB"
        assert CountryRegistry.get("USVI").alpha3 == "VIR"

    def test_native_names(self):
        assert CountryRegistry.get("日本").alpha3 == "JPN"
        assert CountryRegistry.get("Deutschland").alpha3 == "DEU"
        assert CountryRegistry.get("Schweiz").alpha3 == "CHE"
        assert CountryRegistry.get("Österreich").alpha3 == "AUT"
        assert CountryRegistry.get("대한민국").alpha3 == "KOR"
        assert CountryRegistry.get("中国").alpha3 == "CHN"
        assert CountryRegistry.get("Polska").alpha3 == "POL"
        assert CountryRegistry.get("España").alpha3 == "ESP"
        assert CountryRegistry.get("Brasil").alpha3 == "BRA"
        assert CountryRegistry.get("الإمارات العربية المتحدة").alpha3 == "ARE"
        assert CountryRegistry.get("Россия").alpha3 == "RUS"
        assert CountryRegistry.get("Ελλάδα").alpha3 == "GRC"
        assert CountryRegistry.get("Türkiye").alpha3 == "TUR"

    def test_nonexistent_returns_none(self):
        assert CountryRegistry.get(None) is None
        assert CountryRegistry.get("") is None
        assert CountryRegistry.get("   ") is None
        assert CountryRegistry.get("NONEXISTENT_COUNTRY_XYZ") is None


class TestNonPostalCountries:
    """Verify identification of nations without national postal code systems."""

    def test_non_postal_countries(self):
        non_postal_samples = [
            "ARE", "UAE", "United Arab Emirates",
            "QAT", "Qatar",
            "PAN", "Panama",
            "BHS", "Bahamas",
            "SYC", "Seychelles",
            "ATG", "Antigua and Barbuda",
            "BLZ", "Belize",
            "BEN", "Benin",
            "BWA", "Botswana",
            "BFA", "Burkina Faso",
            "BDI", "Burundi",
            "CMR", "Cameroon",
            "CAF", "Central African Republic",
            "TCD", "Chad",
            "COM", "Comoros",
            "COG", "Congo",
            "DJI", "Djibouti",
            "DMA", "Dominica",
            "GNQ", "Equatorial Guinea",
            "ERI", "Eritrea",
            "FJI", "Fiji",
            "GAB", "Gabon",
            "GMB", "Gambia",
            "GHA", "Ghana",
            "GRD", "Grenada",
            "GUY", "Guyana",
            "KIR", "Kiribati",
            "MLI", "Mali",
            "MRT", "Mauritania",
            "NRU", "Nauru",
            "NIU", "Niue",
            "RWA", "Rwanda",
            "KNA", "Saint Kitts and Nevis",
            "LCA", "Saint Lucia",
            "STP", "Sao Tome and Principe",
            "SLE", "Sierra Leone",
            "SLB", "Solomon Islands",
            "SOM", "Somalia",
            "SSD", "South Sudan",
            "SUR", "Suriname",
            "SYR", "Syria",
            "TLS", "Timor-Leste",
            "TKL", "Tokelau",
            "TON", "Tonga",
            "TUV", "Tuvalu",
            "VUT", "Vanuatu",
            "YEM", "Yemen",
            "ZWE", "Zimbabwe",
        ]
        for query in non_postal_samples:
            assert CountryRegistry.has_postal_codes(query) is False, f"Expected non-postal for {query}"

    def test_postal_countries(self):
        postal_samples = [
            "USA", "US", "United States",
            "CAN", "Canada",
            "GBR", "UK", "United Kingdom",
            "DEU", "Germany", "Deutschland",
            "FRA", "France",
            "JPN", "Japan",
            "CHN", "China",
            "BRA", "Brazil",
            "AUS", "Australia",
            "MEX", "Mexico",
            "IND", "India",
            "ZAF", "South Africa",
        ]
        for query in postal_samples:
            assert CountryRegistry.has_postal_codes(query) is True, f"Expected postal for {query}"

    def test_unknown_country_defaults_to_true(self):
        assert CountryRegistry.has_postal_codes("NONEXISTENT_COUNTRY") is True


class TestDetectCountry:
    """Verify country detection from strings and hints."""

    def test_detect_with_country_hint(self):
        assert CountryRegistry.detect_country("100 Main St", country_hint="DEU").alpha3 == "DEU"
        assert CountryRegistry.detect_country("100 Main St", country_hint="jp").alpha3 == "JPN"
        assert CountryRegistry.detect_country("100 Main St", country_hint="840").alpha3 == "USA"
        assert CountryRegistry.detect_country("100 Main St", country_hint="United Kingdom").alpha3 == "GBR"

    def test_detect_from_address_strings(self):
        # US State + ZIP
        d_us = CountryRegistry.detect_country("100 Wall St, New York, NY 10005")
        assert d_us is not None and d_us.alpha3 == "USA"

        d_tx = CountryRegistry.detect_country("123 Congress Ave, Austin, TX 78701")
        assert d_tx is not None and d_tx.alpha3 == "USA"

        # UK postcode
        d_uk = CountryRegistry.detect_country("10 Downing St, London, SW1A 2AA, UK")
        assert d_uk is not None and d_uk.alpha3 == "GBR"

        d_uk2 = CountryRegistry.detect_country("10 Downing St, London SW1A 2AA")
        assert d_uk2 is not None and d_uk2.alpha3 == "GBR"

        # Canada
        d_can = CountryRegistry.detect_country("123 Yonge St, Toronto, ON M5V 2T6, Canada")
        assert d_can is not None and d_can.alpha3 == "CAN"

        # Germany
        d_de = CountryRegistry.detect_country("Friedrichstraße 43, 10117 Berlin, Germany")
        assert d_de is not None and d_de.alpha3 == "DEU"

        # France
        d_fr = CountryRegistry.detect_country("10 Rue de la Paix, 75002 Paris, France")
        assert d_fr is not None and d_fr.alpha3 == "FRA"

        # UAE
        d_uae = CountryRegistry.detect_country("Al Sufouh Rd, Dubai, UAE")
        assert d_uae is not None and d_uae.alpha3 == "ARE"

        # Global Metros
        d_mvd = CountryRegistry.detect_country("Rambla Republica de Mexico 6135, Montevideo")
        assert d_mvd is not None and d_mvd.alpha3 == "URY"

        d_bog = CountryRegistry.detect_country("Carrera 7 # 12-34, Bogota")
        assert d_bog is not None and d_bog.alpha3 == "COL"

    def test_detect_unresolvable_returns_none(self):
        assert CountryRegistry.detect_country(None) is None
        assert CountryRegistry.detect_country("") is None
        assert CountryRegistry.detect_country("   ") is None
        assert CountryRegistry.detect_country("Random text without any geographic indicator") is None


class TestTablesCountryMapSynchronization:
    """Verify that tables.py COUNTRY_MAP contains all 249 ISO-3166-1 identifiers."""

    def test_country_map_coverage(self):
        for c in CountryRegistry.all_countries():
            assert c.alpha2 in COUNTRY_MAP, f"alpha2 {c.alpha2} missing from COUNTRY_MAP"
            assert COUNTRY_MAP[c.alpha2] == c.alpha3

            assert c.alpha3 in COUNTRY_MAP, f"alpha3 {c.alpha3} missing from COUNTRY_MAP"
            assert COUNTRY_MAP[c.alpha3] == c.alpha3

            assert c.numeric in COUNTRY_MAP, f"numeric {c.numeric} missing from COUNTRY_MAP"
            assert COUNTRY_MAP[c.numeric] == c.alpha3

    def test_normalize_country_code_numeric_resolutions(self):
        assert normalize_country_code("840") == "USA"
        assert normalize_country_code("124") == "CAN"
        assert normalize_country_code("276") == "DEU"
        assert normalize_country_code("392") == "JPN"
        assert normalize_country_code("784") == "ARE"

    def test_domestic_namesake_protection_preserved(self):
        # US State presence overrides global metro names
        assert normalize_country_code("USA", state_raw="MN", city_raw="Montevideo") == "USA"
        assert normalize_country_code("USA", state_raw="TX", city_raw="Paris") == "USA"

        # Number in raw street (e.g. Apt 124) must not resolve to Canada (CAN numeric 124)
        assert normalize_country_code(None, raw_street="100 Main St Apt 124") == "USA"


def test_domestic_sovereign_namesake_cities():
    vectors = [
        ("456 Oak St, Lebanon, NH", "LEBANON", "NH"),
        ("100 Main St, Mexico, ME", "MEXICO", "ME"),
        ("200 Main St, Brazil, IN", "BRAZIL", "IN"),
    ]
    for raw, city, state in vectors:
        res = standardize_address(raw)
        assert res.country == "USA"
        assert res.is_us is True
        assert res.city == city
        assert res.state == state
        det = CountryRegistry.detect_country(raw)
        assert det is not None and det.alpha3 == "USA"

