"""
Property-Based Fuzzing: Key ASCII Purity.
=========================================
Validates that all generated deduplication keys (normalized_address_key, building_key,
phonetic_key) are strictly 7-bit ASCII strings (isascii() == True), even when input
addresses contain heavy Unicode diacritics, Cyrillic, or non-Latin scripts.
"""

from address_standardizer import standardize_address

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


NON_ASCII_SAMPLES = [
    # German Umlauts & Eszett
    ("Münchner Straße 45", "", "München", "", "80331", "DEU"),
    ("Große Bleichen 21", "", "Hamburg", "", "20354", "DEU"),
    ("Königsallee 60", "Etage 3", "Düsseldorf", "", "40212", "DEU"),
    ("Nürnberger Straße 18", "", "Nürnberg", "", "90402", "DEU"),
    ("Lützowplatz 17", "", "Berlin", "", "10785", "DEU"),
    # French Accents & Cedillas
    ("80 Rue François 1er", "", "Paris", "", "75008", "FRA"),
    ("30 Rue de la République", "", "Lyon", "", "69002", "FRA"),
    ("450 Boulevard René-Lévesque Ouest", "Suite 400", "Montréal", "QC", "H2X 3J8", "CAN"),
    ("123 Rue Saint-Denis", "", "Montréal", "QC", "H2X 3J8", "CAN"),
    ("15 Rue Sainte-Catherine", "", "Bordeaux", "", "33000", "FRA"),
    # Spanish Accents & Tildes
    ("Calle Núñez de Balboa 12", "2º B", "Madrid", "", "28001", "ESP"),
    ("Av. Constitución 400", "", "Monterrey", "NL", "64060", "MEX"),
    ("Av. Insurgentes Sur 1602", "Col. Crédito Constructor", "Ciudad de México", "CDMX", "03940", "MEX"),
    ("Paseo de la Reforma 222", "Piso 5", "Ciudad de México", "CDMX", "06600", "MEX"),
    ("Calle San Martín 150", "", "Buenos Aires", "", "C1004AAD", "ARG"),
    # Nordic Characters
    ("Købmagergade 52", "", "København", "", "1150", "DNK"),
    ("Västra Hamngatan 7", "", "Göteborg", "", "411 17", "SWE"),
    ("Malmövägen 10", "", "Malmö", "", "211 18", "SWE"),
    ("Østergade 24", "", "København", "", "1100", "DNK"),
    # Polish Diacritics
    ("ul. Świętokrzyska 12", "", "Warszawa", "", "00-048", "POL"),
    ("ul. Długa 25", "", "Gdańsk", "", "80-827", "POL"),
    ("ul. Piotrkowska 80", "", "Łódź", "", "90-102", "POL"),
    ("ul. Marszałkowska 100", "", "Warszawa", "", "00-026", "POL"),
    # Non-Latin Scripts (Greek, Cyrillic, CJK, Arabic)
    ("Охотный Ряд 1", "", "Москва", "", "103265", "RUS"),
    ("вулиця Хрещатик 22", "", "Київ", "", "01001", "UKR"),
    ("東京都千代田区大手町1-1-1", "", "Tokyo", "", "100-0004", "JPN"),
    ("北京市朝阳区建国门外大街1号", "", "Beijing", "", "100004", "CHN"),
    ("شارع الشيخ زايد 100", "", "دبي", "", "00000", "ARE"),
    ("Ερμού 15", "", "Αθήνα", "", "10563", "GRC"),
]


def assert_key_ascii_purity(res):
    """Verifies that all non-None deduplication keys are strictly ASCII."""
    for key_name in ["normalized_address_key", "building_key", "phonetic_key"]:
        val = getattr(res, key_name, None)
        if val is not None and val != "":
            assert val.isascii(), f"Key '{key_name}' contains non-ASCII characters: {val!r}"


def test_deterministic_non_ascii_samples_key_ascii_purity():
    """Verify that 30+ multilingual and non-Latin samples produce strictly ASCII keys."""
    for s1, s2, city, state, postal, country in NON_ASCII_SAMPLES:
        res = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
        )
        assert_key_ascii_purity(res)


if HAS_HYPOTHESIS:
    # Character categories including Latin-1 supplement, Latin extended, Cyrillic, Greek
    unicode_alphabets = st.characters(
        blacklist_categories=("Cs",),  # Exclude surrogates
        min_codepoint=32,
        max_codepoint=0x04FF,
    )

    @settings(max_examples=100, deadline=None)
    @given(
        s1=st.text(alphabet=unicode_alphabets, min_size=1, max_size=100),
        s2=st.text(alphabet=unicode_alphabets, min_size=0, max_size=50),
        city=st.text(alphabet=unicode_alphabets, min_size=1, max_size=50),
        state=st.text(alphabet=unicode_alphabets, min_size=0, max_size=20),
        postal=st.text(alphabet=unicode_alphabets, min_size=0, max_size=20),
        country=st.sampled_from(["DEU", "FRA", "ESP", "POL", "SWE", "DNK", "MEX", "ARG", "BRA", "RUS", "GRC", "USA", "GBR"]),
    )
    def test_hypothesis_key_ascii_purity_property(s1, s2, city, state, postal, country):
        """Hypothesis property: arbitrary Unicode characters always fold into ASCII keys."""
        res = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
        )
        assert_key_ascii_purity(res)
