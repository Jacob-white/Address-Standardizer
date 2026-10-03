"""
Bit-for-Bit Key Equivalence Validation Suite.
=============================================
Validates that _pure_python_core.standardize_record produces 100% bit-for-bit
identical fields and deterministic keys as standardizer.standardize_address
across domestic, international, and edge-case inputs.
"""

from typing import Any, Dict, List
import pytest

from address_standardizer._pure_python_core import standardize_record
from address_standardizer.standardizer import standardize_address


EQUIVALENCE_TEST_CASES: List[Dict[str, Any]] = [
    # Clean structured US addresses
    {
        "street1": "100 Main St",
        "street2": "Suite 200",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
    },
    {
        "street1": "555 Montgomery St",
        "street2": "Floor 12",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94111",
        "country": "USA",
    },
    {
        "street1": "200 South Wacker Dr",
        "street2": "Ste 3100",
        "city": "Chicago",
        "state": "IL",
        "postal_code": "60606",
        "country": "USA",
    },
    # Comma-delimited single-line US addresses
    {
        "street1": "100 Wall St, Suite 400, New York, NY 10005",
    },
    {
        "street1": "701 5th Ave, Fl 50, Seattle, WA 98104",
    },
    # Secondary units variants
    {
        "street1": "100 Park Ave",
        "street2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10017",
    },
    {
        "street1": "200 Elm St",
        "street2": "PMB 502",
        "city": "Dallas",
        "state": "TX",
        "postal_code": "75201",
    },
    {
        "street1": "300 Pine St",
        "street2": "Unit 12",
        "city": "Atlanta",
        "state": "GA",
        "postal_code": "30303",
    },
    # Queens hyphenated house numbers
    {
        "street1": "123-45 82nd Ave",
        "street2": "Apt 4B",
        "city": "Kew Gardens",
        "state": "NY",
        "postal_code": "11415",
    },
    {
        "street1": "67-12 Yellowstone Blvd",
        "city": "Forest Hills",
        "state": "NY",
        "postal_code": "11375",
    },
    # PO Box and Dual-Address
    {
        "street1": "PO Box 789",
        "city": "Denver",
        "state": "CO",
        "postal_code": "80202",
    },
    {
        "street1": "100 Main St",
        "street2": "PO Box 456",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78701",
    },
    # Rural Route & Highway Contracts
    {
        "street1": "RR 2 Box 152",
        "city": "Robinson",
        "state": "IL",
        "postal_code": "62428",
    },
    {
        "street1": "HC 1 Box 22",
        "city": "Radium Springs",
        "state": "NM",
        "postal_code": "88054",
    },
    # Corporate Registered Agent Formation Hubs
    {
        "street1": "1209 North Orange St",
        "street2": "Suite 100",
        "city": "Wilmington",
        "state": "DE",
        "postal_code": "19801",
    },
    {
        "street1": "251 Little Falls Dr",
        "city": "Wilmington",
        "state": "DE",
        "postal_code": "19808",
    },
    {
        "street1": "3500 S DuPont Hwy",
        "city": "Dover",
        "state": "DE",
        "postal_code": "19901",
    },
    # Private residence placeholders
    {
        "street1": "Private Residence",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
    },
    {
        "street1": "Confidential",
        "city": "Los Angeles",
        "state": "CA",
        "postal_code": "90001",
    },
    # Typo recovery & fuzzy healing
    {
        "street1": "500 South St",
        "city": "Phildelphia",
        "state": "PA",
        "postal_code": "91147-1234",
    },
    # UK & Commonwealth
    {
        "street1": "15 High Street",
        "street2": "Headingley",
        "city": "Leeds",
        "postal_code": "LS6 2AA",
        "country": "GBR",
    },
    {
        "street1": "10 Downing Street",
        "city": "London",
        "postal_code": "SW1A 2AA",
        "country": "GBR",
    },
    # Canada
    {
        "street1": "123 rue Saint-Denis",
        "city": "Montreal",
        "state": "QC",
        "postal_code": "H2X 3J8",
        "country": "CAN",
    },
    {
        "street1": "100 King Street West",
        "street2": "Suite 500",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5X 1A9",
        "country": "CAN",
    },
    # Germanic Europe
    {
        "street1": "Musterstraße 12",
        "city": "Berlin",
        "postal_code": "10115",
        "country": "DEU",
    },
    {
        "street1": "Willy-Brandt-Straße 1",
        "city": "Berlin",
        "postal_code": "10557",
        "country": "DEU",
    },
    # Romance & Latin America
    {
        "street1": "Calle Mayor 45, 2º B",
        "city": "Madrid",
        "postal_code": "28013",
        "country": "ESP",
    },
    {
        "street1": "142 Boulevard Saint-Germain",
        "street2": "Apt 12",
        "city": "Paris",
        "postal_code": "75006",
        "country": "FRA",
    },
    # Offshore Corporate Centers
    {
        "street1": "Ugland House South Church St",
        "street2": "PO Box 309",
        "city": "George Town",
        "postal_code": "KY1-1104",
        "country": "CYM",
    },
    {
        "street1": "Craigmuir Chambers",
        "street2": "PO Box 71",
        "city": "Road Town",
        "postal_code": "VG1110",
        "country": "VGB",
    },
    # Empty and garbage
    {
        "street1": "",
    },
    {
        "street1": "NULL",
    },
    {
        "street1": "N/A",
    },
    {
        "street1": "UNKNOWN",
    },
]


@pytest.mark.parametrize("addr_dict", EQUIVALENCE_TEST_CASES)
def test_pure_python_vs_standardize_address_bit_for_bit(addr_dict):
    """
    Asserts bit-for-bit equivalence between _pure_python_core and standardize_address.
    """
    pure_res = standardize_record(**addr_dict, finalize=True)
    std_res = standardize_address(**addr_dict)

    # Core postal components
    assert pure_res.street1 == std_res.street1, f"Mismatch in street1 for {addr_dict}"
    assert pure_res.street2 == std_res.street2, f"Mismatch in street2 for {addr_dict}"
    assert pure_res.city == std_res.city, f"Mismatch in city for {addr_dict}"
    assert pure_res.state == std_res.state, f"Mismatch in state for {addr_dict}"
    assert pure_res.postal_code == std_res.postal_code, f"Mismatch in postal_code for {addr_dict}"
    assert pure_res.country == std_res.country, f"Mismatch in country for {addr_dict}"
    assert pure_res.country_iso3 == std_res.country_iso3, f"Mismatch in country_iso3 for {addr_dict}"

    # Deterministic entity resolution keys
    assert pure_res.normalized_address_key == std_res.normalized_address_key, f"Mismatch in normalized_address_key for {addr_dict}"
    assert pure_res.building_key == std_res.building_key, f"Mismatch in building_key for {addr_dict}"
    assert pure_res.phonetic_key == std_res.phonetic_key, f"Mismatch in phonetic_key for {addr_dict}"

    # Invariant attributes and risk flags
    assert pure_res.is_us == std_res.is_us, f"Mismatch in is_us for {addr_dict}"
    assert pure_res.is_registered_agent_hub == std_res.is_registered_agent_hub, f"Mismatch in is_registered_agent_hub for {addr_dict}"
    assert pure_res.is_private_residence == std_res.is_private_residence, f"Mismatch in is_private_residence for {addr_dict}"
    assert pure_res.address_status == std_res.address_status, f"Mismatch in address_status for {addr_dict}"

    # Subsystem specific fields
    assert pure_res.dependent_locality == std_res.dependent_locality
    assert pure_res.building_name == std_res.building_name
