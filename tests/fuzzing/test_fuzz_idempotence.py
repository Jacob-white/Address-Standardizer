"""
Property-Based Fuzzing: Mathematical Idempotence.
=================================================
Validates the mathematical fixed-point idempotence property:
  S(S(A)) == S(A)
For any standardized address, re-standardizing its canonical output fields
produces identical normalized fields and identical deterministic keys.
"""

from address_standardizer import standardize_address

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


CANONICAL_IDEMPOTENCE_SAMPLES = [
    # US Standard
    ("100 Main St", "Suite 400", "New York", "NY", "10001", "USA"),
    ("200 Park Ave", "Fl 12", "New York", "NY", "10166", "USA"),
    ("555 California St", "Ste 200", "San Francisco", "CA", "94104", "USA"),
    ("1000 Elm St", "Apt 2B", "Dallas", "TX", "75201", "USA"),
    ("PO Box 456", "", "Denver", "CO", "80202", "USA"),
    ("1209 North Orange Street", "", "Wilmington", "DE", "19801", "USA"),
    ("30 N Gould St", "Ste 100", "Sheridan", "WY", "82801", "USA"),
    ("16192 Coastal Hwy", "", "Lewes", "DE", "19958", "USA"),
    # UK & Commonwealth
    ("15 High Street", "Flat 2", "Leeds", "", "LS6 2AA", "GBR"),
    ("25 Park Road", "Suite 10", "London", "", "SW1A 1AA", "GBR"),
    ("St Andrews Court, 10 Church St", "", "Manchester", "", "M1 1AA", "GBR"),
    ("10 Station Road", "Flat 3", "Edinburgh", "", "EH1 1YZ", "GBR"),
    ("50 Victoria Street", "", "Bristol", "", "BS1 4ST", "GBR"),
    ("71-75 Shelton Street", "", "London", "", "WC2H 9JQ", "GBR"),
    ("20-22 Wenlock Road", "", "London", "", "N1 7GU", "GBR"),
    ("12 King Street", "Apt 4", "St Helier", "", "JE2 3XX", "JEY"),
    ("8 Queen Street", "", "St Peter Port", "", "GY1 2YY", "GGY"),
    ("14 Bank Street", "", "Douglas", "", "IM1 1ZZ", "IMN"),
    # Canada
    ("100 King Street West", "Suite 400", "Toronto", "ON", "M5X 1A9", "CAN"),
    ("123 rue Saint-Denis", "", "Montréal", "QC", "H2X 3J8", "CAN"),
    ("450 boulevard René-Lévesque Ouest", "Suite 1200", "Montréal", "QC", "H2X 3J8", "CAN"),
    ("200 Bay Street", "Fl 30", "Toronto", "ON", "M5J 2J2", "CAN"),
    ("789 avenue Mont-Royal Est", "", "Montréal", "QC", "H2H 1Y1", "CAN"),
    ("RR 2", "", "Smiths Falls", "ON", "K7A 4S5", "CAN"),
    ("PO Box 450", "", "Ottawa", "ON", "K1A 0B1", "CAN"),
    # European Union
    ("Musterstraße 12", "", "Berlin", "", "10115", "DEU"),
    ("Friedrichstraße 43-45", "", "Berlin", "", "10117", "DEU"),
    ("Am Hauptbahnhof 5a", "", "Frankfurt am Main", "", "60329", "DEU"),
    ("Maximilianstraße 25", "", "München", "", "80331", "DEU"),
    ("142 Boulevard Saint-Germain", "", "Paris", "", "75006", "FRA"),
    ("25 Rue de Rivoli", "", "Paris", "", "75004", "FRA"),
    ("Keizersgracht 421", "Apt B", "Amsterdam", "", "1016 EK", "NLD"),
    ("Herengracht 182", "", "Amsterdam", "", "1016 BR", "NLD"),
    ("Calle Mayor 45", "2º B", "Madrid", "", "28013", "ESP"),
    ("Paseo de la Castellana 89", "4ª A", "Madrid", "", "28046", "ESP"),
    ("Via Roma 10", "", "Roma", "", "00184", "ITA"),
    ("Corso Buenos Aires 33", "", "Milano", "", "20124", "ITA"),
    ("ul. Marszałkowska 100", "", "Warszawa", "", "00-026", "POL"),
    ("Kungsgatan 14", "", "Stockholm", "", "111 35", "SWE"),
    ("Østergade 24", "", "København", "", "1100", "DNK"),
    # Latin America
    ("Av. Insurgentes Sur 1602", "Int 401", "Ciudad de México", "CDMX", "03940", "MEX"),
    ("Paseo de la Reforma 222", "Piso 5", "Ciudad de México", "CDMX", "06600", "MEX"),
    ("Calle 72 No. 10-07", "", "Bogotá", "", "110221", "COL"),
    ("Av. Corrientes 1234", "Piso 4", "Buenos Aires", "", "C1043AAZ", "ARG"),
    ("Av. Paulista 1000", "Conjunto 14", "São Paulo", "SP", "01310-100", "BRA"),
    ("Av. Providencia 1208", "Of 501", "Santiago", "", "7500000", "CHL"),
    ("Av. Larco 101", "Dpto 402", "Lima", "", "15074", "PER"),
    # Offshore
    ("Ugland House, South Church Street", "PO Box 309", "George Town", "", "KY1-1104", "CYM"),
    ("Clifton House, 75 Fort Street", "PO Box 190", "George Town", "", "KY1-1104", "CYM"),
    ("Craigmuir Chambers", "PO Box 71", "Road Town", "TORTOLA", "VG1110", "VGB"),
    ("Wickhams Cay 1", "Trident Chambers", "Road Town", "", "VG1110", "VGB"),
    ("Clarendon House, 2 Church Street", "", "Hamilton", "", "HM 11", "BMU"),
]


def assert_idempotence(s1, s2, city, state, postal, country):
    """Executes S(S(A)) == S(A) assertion."""
    # First pass: S(A)
    s = standardize_address(
        street1=s1,
        street2=s2,
        city=city,
        state=state,
        postal_code=postal,
        country=country,
    )
    if s.address_status != "standardized":
        return

    # Second pass: S'(S(A))
    s_prime = standardize_address(
        street1=s.street1,
        street2=s.street2,
        city=s.city,
        state=s.state,
        postal_code=s.postal_code,
        country=s.country,
    )

    assert s_prime.address_status == "standardized"
    assert s_prime.street1 == s.street1, f"street1 mismatch: {s_prime.street1} != {s.street1}"
    assert s_prime.street2 == s.street2, f"street2 mismatch: {s_prime.street2} != {s.street2}"
    assert s_prime.city == s.city, f"city mismatch: {s_prime.city} != {s.city}"
    assert s_prime.state == s.state, f"state mismatch: {s_prime.state} != {s.state}"
    assert s_prime.postal_code == s.postal_code, f"postal_code mismatch: {s_prime.postal_code} != {s.postal_code}"
    assert s_prime.country == s.country, f"country mismatch: {s_prime.country} != {s.country}"
    assert s_prime.normalized_address_key == s.normalized_address_key, f"key mismatch: {s_prime.normalized_address_key} != {s.normalized_address_key}"
    assert s_prime.building_key == s.building_key, f"building_key mismatch: {s_prime.building_key} != {s.building_key}"


def test_deterministic_idempotence_matrix():
    """Verifies that re-standardizing 50+ canonical addresses preserves mathematical fixed-point identity."""
    for s1, s2, city, state, postal, country in CANONICAL_IDEMPOTENCE_SAMPLES:
        assert_idempotence(s1, s2, city, state, postal, country)


if HAS_HYPOTHESIS:
    us_addresses = st.tuples(
        st.sampled_from(["100 Main St", "250 Park Ave", "555 California St", "1000 Elm St", "1209 North Orange Street", "30 N Gould St"]),
        st.sampled_from(["", "Suite 100", "Apt 2B", "Fl 4", "Unit 12"]),
        st.sampled_from(["New York", "San Francisco", "Wilmington", "Dallas", "Denver", "Sheridan"]),
        st.sampled_from(["NY", "CA", "DE", "TX", "CO", "WY"]),
        st.sampled_from(["10001", "94104", "19801", "75201", "80202", "82801"]),
        st.just("USA"),
    )

    uk_addresses = st.tuples(
        st.sampled_from(["15 High Street", "25 Park Road", "10 Station Road", "71-75 Shelton Street", "20-22 Wenlock Road"]),
        st.sampled_from(["", "Flat 1", "Flat 2", "Apt 4", "Suite 5"]),
        st.sampled_from(["London", "Leeds", "Manchester", "Edinburgh", "Bristol"]),
        st.just(""),
        st.sampled_from(["SW1A 1AA", "LS6 2AA", "M1 1AA", "EH1 1YZ", "WC2H 9JQ"]),
        st.sampled_from(["GBR", "United Kingdom"]),
    )

    can_addresses = st.tuples(
        st.sampled_from(["100 King Street West", "200 Bay Street", "123 rue Saint-Denis", "450 boulevard René-Lévesque Ouest", "RR 2", "PO Box 450"]),
        st.sampled_from(["", "Suite 400", "Suite 1200", "Apt 2B", "Unit 5"]),
        st.sampled_from(["Toronto", "Montréal", "Ottawa", "Vancouver", "Calgary"]),
        st.sampled_from(["ON", "QC", "BC", "AB"]),
        st.sampled_from(["M5X 1A9", "H2X 3J8", "K1A 0B1", "V6B 2W9", "T2P 3N9"]),
        st.sampled_from(["CAN", "Canada"]),
    )

    eu_addresses = st.tuples(
        st.sampled_from(["Musterstraße 12", "Friedrichstraße 43-45", "142 Boulevard Saint-Germain", "Keizersgracht 421", "Calle Mayor 45", "Via Roma 10"]),
        st.sampled_from(["", "Apt B", "2º B", "Int 5"]),
        st.sampled_from(["Berlin", "Paris", "Amsterdam", "Madrid", "Roma"]),
        st.just(""),
        st.sampled_from(["10115", "75006", "1016 EK", "28013", "00184"]),
        st.sampled_from(["DEU", "FRA", "NLD", "ESP", "ITA", "Germany", "France", "Netherlands", "Spain", "Italy"]),
    )

    offshore_addresses = st.tuples(
        st.sampled_from(["Ugland House, South Church St", "Clifton House, 75 Fort St", "Craigmuir Chambers", "Wickhams Cay 1", "Clarendon House, 2 Church St"]),
        st.sampled_from(["", "PO Box 309", "PO Box 190", "PO Box 71", "Trident Chambers"]),
        st.sampled_from(["George Town", "Road Town", "Hamilton"]),
        st.sampled_from(["", "TORTOLA"]),
        st.sampled_from(["KY1-1104", "VG1110", "HM 11"]),
        st.sampled_from(["CYM", "VGB", "BMU", "Cayman Islands", "British Virgin Islands", "Bermuda"]),
    )

    latam_addresses = st.tuples(
        st.sampled_from(["Av. Insurgentes Sur 1602", "Paseo de la Reforma 222", "Calle 72 No. 10-07", "Av. Corrientes 1234", "Av. Paulista 1000"]),
        st.sampled_from(["", "Int 401", "Piso 5", "Piso 4", "Conjunto 14"]),
        st.sampled_from(["Ciudad de México", "Bogotá", "Buenos Aires", "São Paulo"]),
        st.sampled_from(["CDMX", "", "SP"]),
        st.sampled_from(["03940", "110221", "C1043AAZ", "01310-100"]),
        st.sampled_from(["MEX", "COL", "ARG", "BRA", "Mexico", "Colombia", "Argentina", "Brazil"]),
    )

    matched_addresses = st.one_of(us_addresses, uk_addresses, can_addresses, eu_addresses, offshore_addresses, latam_addresses)

    @settings(max_examples=100, deadline=None)
    @given(addr=matched_addresses)
    def test_hypothesis_idempotence_property(addr):
        """Hypothesis generative property: S(S(A)) == S(A) holds across random compositions."""
        s1, s2, city, state, postal, country = addr
        assert_idempotence(s1, s2, city, state, postal, country)
