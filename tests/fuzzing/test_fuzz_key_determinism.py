"""
Property-Based Fuzzing: Key Determinism.
========================================
Validates that repeated executions, concurrent threads, and argument permutations
yield bit-for-bit identical normalized_address_key and building_key values.
"""

from concurrent.futures import ThreadPoolExecutor
from address_standardizer import standardize_address

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


DETERMINISM_SAMPLES = [
    ("100 Main St", "Suite 400", "New York", "NY", "10001", "USA"),
    ("15 High Street", "Flat 2", "Leeds", "", "LS6 2AA", "GBR"),
    ("100 King Street West", "Suite 400", "Toronto", "ON", "M5X 1A9", "CAN"),
    ("Musterstraße 12", "", "Berlin", "", "10115", "DEU"),
    ("Av. Insurgentes Sur 1602", "Int 401", "Ciudad de México", "CDMX", "03940", "MEX"),
    ("Ugland House, South Church St", "PO Box 309", "George Town", "", "KY1-1104", "CYM"),
    ("71-75 Shelton Street", "", "London", "", "WC2H 9JQ", "GBR"),
    ("1209 North Orange Street", "", "Wilmington", "DE", "19801", "USA"),
    ("Keizersgracht 421", "Apt B", "Amsterdam", "", "1016 EK", "NLD"),
    ("Calle Mayor 45", "2º B", "Madrid", "", "28013", "ESP"),
]


def test_repetition_determinism_sequential():
    """Verify 10 sequential repetitions of each sample yield bit-for-bit identical keys."""
    for s1, s2, city, state, postal, country in DETERMINISM_SAMPLES:
        baseline = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
        for _ in range(10):
            rep = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
            assert rep.normalized_address_key == baseline.normalized_address_key
            assert rep.building_key == baseline.building_key
            assert rep.phonetic_key == baseline.phonetic_key
            assert rep.street1 == baseline.street1
            assert rep.street2 == baseline.street2


def test_concurrent_multithreaded_determinism():
    """Verify concurrent thread execution yields identical keys without race conditions."""
    def worker(item):
        s1, s2, city, state, postal, country = item
        res = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
        return (res.normalized_address_key, res.building_key, res.phonetic_key)

    tasks = DETERMINISM_SAMPLES * 10
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(worker, tasks))

    # Check that identical inputs in tasks produced identical outputs
    expected_map = {}
    for item in DETERMINISM_SAMPLES:
        s1, s2, city, state, postal, country = item
        res = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
        expected_map[item] = (res.normalized_address_key, res.building_key, res.phonetic_key)

    for item, actual in zip(tasks, results):
        assert actual == expected_map[item]


def test_kwargs_ordering_determinism():
    """Verify dictionary argument insertion ordering has zero effect on generated keys."""
    for s1, s2, city, state, postal, country in DETERMINISM_SAMPLES:
        order1 = {"street1": s1, "street2": s2, "city": city, "state": state, "postal_code": postal, "country": country}
        order2 = {"country": country, "postal_code": postal, "state": state, "city": city, "street2": s2, "street1": s1}
        order3 = {"city": city, "street1": s1, "country": country, "street2": s2, "postal_code": postal, "state": state}

        r1 = standardize_address(**order1)
        r2 = standardize_address(**order2)
        r3 = standardize_address(**order3)

        assert r1.normalized_address_key == r2.normalized_address_key == r3.normalized_address_key
        assert r1.building_key == r2.building_key == r3.building_key


if HAS_HYPOTHESIS:
    @settings(max_examples=100, deadline=None)
    @given(
        s1=st.text(min_size=1, max_size=100),
        s2=st.text(min_size=0, max_size=50),
        city=st.text(min_size=1, max_size=50),
        state=st.text(min_size=0, max_size=20),
        postal=st.text(min_size=0, max_size=20),
        country=st.text(min_size=0, max_size=20),
    )
    def test_hypothesis_key_determinism_property(s1, s2, city, state, postal, country):
        """Hypothesis property: 3 consecutive runs on identical inputs yield identical keys."""
        r1 = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
        r2 = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
        r3 = standardize_address(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)

        assert r1.normalized_address_key == r2.normalized_address_key == r3.normalized_address_key
        assert r1.building_key == r2.building_key == r3.building_key
        assert r1.phonetic_key == r2.phonetic_key == r3.phonetic_key
