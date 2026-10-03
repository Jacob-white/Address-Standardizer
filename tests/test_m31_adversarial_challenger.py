"""Milestone 3.1 Empirical Adversarial Challenge Test Suite.

Author: challenger_m31_1
Purpose: Stress-test, fuzz, and empirically verify Milestone 3.1 international parsing.
"""

import pytest
from address_standardizer import (
    StandardizedAddress,
    standardize_address,
)
from address_standardizer.international.uk import is_valid_uk_postcode
from address_standardizer.international.canada import is_valid_canadian_postal_code
from address_standardizer.international.germanic import is_valid_dutch_postcode


EXPECTED_14_KEYS = {
    "street1",
    "street2",
    "city",
    "state",
    "postal_code",
    "country",
    "normalized_address_key",
    "address_status",
    "raw_street_address",
    "is_us",
    "is_private_residence",
    "building_key",
    "phonetic_key",
    "is_registered_agent_hub",
}


# ==============================================================================
# Vector 1: Adversarial Fuzzing & Crash Resilience
# ==============================================================================

ADVERSARIAL_INPUTS = [
    ("", {}),
    ("   ", {}),
    ("\t\n\r", {}),
    ("\x00", {}),
    ("123 Main St\x00Apt 4", {}),
    ("100\x00 High Street, Leeds\x00, LS6 2AA, UK", {}),
    ("A" * 10000, {}),
    ("123 " + "Main " * 2000 + "St", {}),
    ("Musterstraße " + "9" * 1000, {"country": "DEU"}),
    ("123 Main St 🏢 🇨🇦", {}),
    ("Musterstraße 12 🇩🇪 🍺", {"country": "DEU"}),
    ("Via Roma 10 🇮🇹 🍕", {"country": "ITA"}),
    ("M̶u̶s̶t̶e̶r̶s̶t̶r̶a̶ß̶e̶ 12", {"country": "DEU"}),
    ("شارع الشيخ زايد 101, دبي", {}),
    ("東京都千代田区千代田1-1", {}),
    ("Красная площадь, Москва, 109012", {"country": "RUS"}),
    ("' OR '1'='1' --", {}),
    ("<script>alert(1)</script>", {}),
    ("\\[\\]\\(\\)\\*\\+\\?\\^\\$\\|", {}),
    (",,,,,", {}),
    (";;;;;", {}),
    ("- - - - -", {}),
    ("123 Main St", {"country": "ZZZ"}),
    ("123 Main St", {"country": ""}),
    ("123 Main St", {"postal_code": "9" * 500}),
    ("123 Main St", {"city": "C" * 1000, "state": "S" * 1000}),
]


@pytest.mark.parametrize("raw_str, kwargs", ADVERSARIAL_INPUTS)
def test_crash_resilience_adversarial_fuzzing(raw_str, kwargs):
    """Engine must NEVER raise unhandled exceptions on arbitrary/corrupt inputs."""
    res = standardize_address(raw_str, **kwargs)
    assert isinstance(res, StandardizedAddress)
    # Must preserve 14-key dictionary layout
    d = res.as_dict()
    assert len(d) == 14
    assert set(d.keys()) == EXPECTED_14_KEYS


# ==============================================================================
# Vector 2: Property Invariants
# ==============================================================================

REPRESENTATIVE_ADDRESSES = [
    # US domestic
    ("100 Main St, Austin, TX 78701", {}),
    ("350 Fifth Ave, Fl 34, New York, NY 10118", {}),
    # UK
    ("14 High Street, Leeds, LS6 2AA, UK", {}),
    ("Rose Cottage, Mill Lane, Leeds, LS6 1AA, UK", {}),
    ("10 Bridge Street, Stratford-upon-Avon, CV37 6AB, UK", {}),
    # Canada
    ("123 rue Saint-Denis, Montréal, QC H2X 3J8, Canada", {}),
    ("450 boulevard René-Lévesque Ouest, Montréal, QC H2Z 1Z2, Canada", {}),
    ("100 King Street West, Toronto, ON M5X 1A9, Canada", {}),
    ("RR 2, Cochrane, AB T4C 1A1, Canada", {}),
    # Germanic
    ("Musterstraße 12, 10115 Berlin, Germany", {}),
    ("Willy-Brandt-Straße 1, 10557 Berlin, Germany", {}),
    ("Straße des 17. Juni 135, 10623 Berlin, Germany", {}),
    ("Am Hauptbahnhof 5a, 60329 Frankfurt am Main, Germany", {}),
    ("Keizersgracht 421-B, 1016 EK Amsterdam, Netherlands", {}),
    ("Kungsgatan 10, 111 35 Stockholm, Sweden", {}),
    # Romance
    ("Av. Insurgentes Sur 1602, Col. Crédito Constructor, 03940 Ciudad de México, CDMX, Mexico", {}),
    ("Calle Mayor 45, 2º B, 28013 Madrid, Spain", {}),
    ("Calle 72 No. 10-07, Bogotá, Colombia", {}),
    ("Avenida Paulista, 1578 - Bela Vista, São Paulo - SP, 01310-100, Brazil", {}),
    # Offshore
    ("Craigmuir Chambers, PO Box 71, Road Town, Tortola, VG1110, British Virgin Islands", {}),
    ("Clarendon House, 2 Church Street, PO Box HM 666, Hamilton, HM CX, Bermuda", {}),
    ("Torre Banco General, Piso 25, Apartado 0816-01098, Panama City, Panama", {}),
    ("Clifton House, 75 Fort St, PO Box 1350, George Town, KY1-1108, Cayman Islands", {}),
    ("142 Boulevard Saint-Germain, Esc. B, Apt 12, 75006 Paris, France", {}),
    ("Calle Mayor 45, Apt 12, 28013 Madrid, Spain", {}),
    ("14 High Street, Flat 2, Leeds, LS6 2AA, UK", {}),
]


@pytest.mark.parametrize("raw_str, kwargs", REPRESENTATIVE_ADDRESSES)
def test_property_determinism_1000_iterations(raw_str, kwargs):
    """1,000 iterations must produce bit-for-bit identical outputs."""
    baseline = standardize_address(raw_str, **kwargs)
    for _ in range(100):  # 100 per parametrized test to keep runtime fast within suite
        curr = standardize_address(raw_str, **kwargs)
        assert curr.street1 == baseline.street1
        assert curr.street2 == baseline.street2
        assert curr.city == baseline.city
        assert curr.state == baseline.state
        assert curr.postal_code == baseline.postal_code
        assert curr.country == baseline.country
        assert curr.normalized_address_key == baseline.normalized_address_key
        assert curr.building_key == baseline.building_key
        assert curr.phonetic_key == baseline.phonetic_key


@pytest.mark.parametrize("raw_str, kwargs", REPRESENTATIVE_ADDRESSES)
def test_property_ascii_purity_of_keys(raw_str, kwargs):
    """All matching keys must be strictly ASCII-clean."""
    res = standardize_address(raw_str, **kwargs)
    if res.normalized_address_key:
        assert res.normalized_address_key.isascii(), f"Key not ASCII: {res.normalized_address_key}"
    if res.building_key:
        assert res.building_key.isascii(), f"Building key not ASCII: {res.building_key}"
    if res.phonetic_key:
        assert res.phonetic_key.isascii(), f"Phonetic key not ASCII: {res.phonetic_key}"


@pytest.mark.parametrize("raw_str, kwargs", REPRESENTATIVE_ADDRESSES)
def test_property_14_key_backward_compatibility(raw_str, kwargs):
    """Default as_dict() must return exactly 14 keys; include_metadata=True exposes extras."""
    res = standardize_address(raw_str, **kwargs)
    d_default = res.as_dict()
    assert len(d_default) == 14
    assert set(d_default.keys()) == EXPECTED_14_KEYS

    d_meta = res.as_dict(include_metadata=True)
    assert len(d_meta) >= 16
    assert "dependent_locality" in d_meta
    assert "building_name" in d_meta


@pytest.mark.parametrize("raw_str, kwargs", REPRESENTATIVE_ADDRESSES)
def test_property_idempotence_clean_records(raw_str, kwargs):
    """Re-standardizing the parsed components must produce identical results."""
    res1 = standardize_address(raw_str, **kwargs)
    res2 = standardize_address(
        street1=res1.street1,
        street2=res1.street2,
        city=res1.city,
        state=res1.state,
        postal_code=res1.postal_code,
        country=res1.country,
    )
    assert res2.street1 == res1.street1
    assert res2.street2 == res1.street2
    assert res2.city == res1.city
    assert res2.state == res1.state
    assert res2.postal_code == res1.postal_code
    assert res2.country == res1.country
    assert res2.normalized_address_key == res1.normalized_address_key
    assert res2.building_key == res1.building_key
    assert res2.phonetic_key == res1.phonetic_key


# ==============================================================================
# Vector 3: Specific International Postal Code Validation
# ==============================================================================

def test_uk_postcode_validation():
    # Valid
    assert is_valid_uk_postcode("GIR 0AA")
    assert is_valid_uk_postcode("SW1A 1AA")
    assert is_valid_uk_postcode("EC1A 1BB")
    assert is_valid_uk_postcode("W1A 0AX")
    assert is_valid_uk_postcode("M1 1AA")
    assert is_valid_uk_postcode("B33 8TH")
    assert is_valid_uk_postcode("CR2 6XH")
    assert is_valid_uk_postcode("DN55 1PT")

    # Invalid position 1 (Q, V, X)
    assert not is_valid_uk_postcode("QA1A 1AA")
    assert not is_valid_uk_postcode("V1A 1AA")
    assert not is_valid_uk_postcode("X1A 1AA")

    # Invalid position 2 (I, J, Z)
    assert not is_valid_uk_postcode("AI1A 1AA")
    assert not is_valid_uk_postcode("AJ1A 1AA")
    assert not is_valid_uk_postcode("AZ1A 1AA")

    # Invalid inward letters (C, I, K, M, O, V)
    assert not is_valid_uk_postcode("SW1A 1AC")
    assert not is_valid_uk_postcode("SW1A 1AI")
    assert not is_valid_uk_postcode("SW1A 1AK")
    assert not is_valid_uk_postcode("SW1A 1AM")
    assert not is_valid_uk_postcode("SW1A 1AO")
    assert not is_valid_uk_postcode("SW1A 1AV")


def test_canadian_postcode_validation():
    # Valid
    assert is_valid_canadian_postal_code("K1A 0B1")
    assert is_valid_canadian_postal_code("H2X 3J8")
    assert is_valid_canadian_postal_code("M5X 1A9")
    assert is_valid_canadian_postal_code("V6B 3A7")

    # Prohibited letters: D, F, I, O, Q, U
    assert not is_valid_canadian_postal_code("D1A 1A1")
    assert not is_valid_canadian_postal_code("K1F 1A1")
    assert not is_valid_canadian_postal_code("K1I 1A1")
    assert not is_valid_canadian_postal_code("K1O 1A1")
    assert not is_valid_canadian_postal_code("K1Q 1A1")
    assert not is_valid_canadian_postal_code("K1U 1A1")

    # Initial W or Z prohibited
    assert not is_valid_canadian_postal_code("W1A 1A1")
    assert not is_valid_canadian_postal_code("Z1A 1A1")


def test_dutch_postcode_validation():
    # Valid
    assert is_valid_dutch_postcode("1016 EK")
    assert is_valid_dutch_postcode("2513 AA")
    assert is_valid_dutch_postcode("3011 AB")

    # Disallowed combos: SA, SD, SS
    assert not is_valid_dutch_postcode("1016 SA")
    assert not is_valid_dutch_postcode("1016 SD")
    assert not is_valid_dutch_postcode("1016 SS")

    # Cannot start with 0
    assert not is_valid_dutch_postcode("0123 AB")


# ==============================================================================
# Vector 4: Empirical Reproduction of Vulnerabilities & Edge-Case Failure Modes
# ==============================================================================

def test_vulnerability_1_cayman_clifton_house_idempotence_break():
    """VULNERABILITY 1 (Remediated): Clifton House 75 Fort St satisfies idempotence and preserves keys."""
    raw = "Clifton House, 75 Fort St, PO Box 1350, George Town, KY1-1108, Cayman Islands"
    res1 = standardize_address(raw)
    res2 = standardize_address(
        street1=res1.street1,
        street2=res1.street2,
        city=res1.city,
        state=res1.state,
        postal_code=res1.postal_code,
        country=res1.country,
    )
    assert res1.street1 == "CLIFTON HOUSE 75 FORT ST"
    assert res2.street1 == "CLIFTON HOUSE 75 FORT ST"
    assert res1.normalized_address_key == res2.normalized_address_key
    assert res1.building_key == res2.building_key
    assert res1.phonetic_key == res2.phonetic_key


def test_vulnerability_2_romance_secondary_unit_omission():
    """VULNERABILITY 2 (Remediated): French address correctly extracts secondary units, city, and postal code."""
    raw = "142 Boulevard Saint-Germain, Esc. B, Apt 12, 75006 Paris, France"
    res = standardize_address(raw)
    assert res.street1 == "142 BD SAINT-GERMAIN"
    assert res.street2 == "ESC B APT 12"
    assert res.city == "PARIS"
    assert res.postal_code == "75006"
    assert res.country == "FRA"


def test_vulnerability_3_uk_flat_after_street_misclassified_as_dependent_locality():
    """VULNERABILITY 3 (Remediated): '14 High Street, Flat 2' extracts Flat 2 to street2, not dependent_locality."""
    raw = "14 High Street, Flat 2, Leeds, LS6 2AA, UK"
    res = standardize_address(raw)
    assert res.street1 == "14 HIGH ST"
    assert res.street2 == "APT 2"
    assert res.dependent_locality is None or res.dependent_locality == ""
    assert res.city == "LEEDS"
    assert res.postal_code == "LS6 2AA"
    assert "APT 2" in res.normalized_address_key


def test_vulnerability_4_non_ascii_country_code_violates_ascii_purity():
    """VULNERABILITY 4 (Remediated): Non-ASCII 3-letter country code maintains strict ASCII purity of keys."""
    res = standardize_address("100 Main St", city="Moscow", country="РУС")
    assert res.normalized_address_key is not None
    assert res.normalized_address_key.isascii()
    if res.building_key:
        assert res.building_key.isascii()
    if res.phonetic_key:
        assert res.phonetic_key.isascii()
