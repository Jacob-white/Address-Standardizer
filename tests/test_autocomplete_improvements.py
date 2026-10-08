"""
Test Suite for Real-time Autocomplete Engine Improvements.
==========================================================
Tests:
  - Damerau-Levenshtein typo tolerance (distance <= 1)
  - Secondary unit requirement prompt and suggestions
  - Geographic proximity radius biasing and distance calculation
  - Reference index streaming
"""


from address_standardizer.autocomplete import (
    AutocompleteEngine,
    calculate_haversine_distance_meters,
    damerau_levenshtein_distance,
)


def test_damerau_levenshtein_distance():
    assert damerau_levenshtein_distance("WALL", "WALL") == 0
    # Substitution (distance 1)
    assert damerau_levenshtein_distance("WALL", "WELL") == 1
    # Deletion / insertion (distance 1)
    assert damerau_levenshtein_distance("WAL", "WALL") == 1
    assert damerau_levenshtein_distance("WALL", "WAL") == 1
    # Transposition (distance 1)
    assert damerau_levenshtein_distance("WLAL", "WALL") == 1
    # Distance >= 2
    assert damerau_levenshtein_distance("WLLE", "WALL") >= 2


def test_autocomplete_typo_tolerance_single_edit():
    engine = AutocompleteEngine(seed=True)

    # Transposition: "100 WLAL" instead of "100 WALL"
    results_transposition = engine.search("100 Wlal", typo_tolerance=True)
    assert any("WALL" in s.street_line for s in results_transposition)

    # Substitution: "100 Wqll"
    results_sub = engine.search("100 Wqll", typo_tolerance=True)
    assert any("WALL" in s.street_line for s in results_sub)


def test_secondary_unit_prompting():
    engine = AutocompleteEngine(seed=True)

    # Multi-unit address without secondary unit specified
    suggestions = engine.search("100 Wall St")
    assert len(suggestions) > 0
    first = suggestions[0]
    assert first.secondary_prompt_required is True
    assert first.prompt_message == "Requires Suite / Apartment Number"
    assert len(first.suggested_secondary_units) > 0
    assert any("STE" in u or "APT" in u or "FL" in u for u in first.suggested_secondary_units)

    # Query with secondary unit already provided
    suggestions_with_unit = engine.search("100 Wall St Ste 400")
    if suggestions_with_unit:
        assert suggestions_with_unit[0].secondary_prompt_required is False


def test_proximity_radius_biasing():
    # NYC coords: 40.7128, -74.0060
    # Chicago coords: 41.8781, -87.6298
    engine = AutocompleteEngine(seed=True)

    # Client located near NYC
    nyc_client_results = engine.search(
        "Ave",
        client_lat=40.7128,
        client_lon=-74.0060,
        max_results=5,
    )
    # The top candidate near NYC should have distance_meters populated and be closer than Chicago
    assert len(nyc_client_results) > 0
    assert nyc_client_results[0].distance_meters is not None
    # Verify the top candidate is from NY when client is in NYC
    assert nyc_client_results[0].state == "NY"


def test_haversine_distance_meters():
    # Distance between NYC (40.7128, -74.0060) and Wall St (40.7061, -74.0060) is ~745m
    dist = calculate_haversine_distance_meters(40.7128, -74.0060, 40.7061, -74.0060)
    assert 700.0 < dist < 800.0


def test_load_reference_stream():
    engine = AutocompleteEngine(seed=False)
    records = [
        {"street1": "742 EVERGREEN TER", "city": "SPRINGFIELD", "state": "OR", "postal_code": "97477"},
        {"street1": "1042 ELM ST", "city": "SPRINGFIELD", "state": "IL", "postal_code": "62701"},
    ]
    loaded = engine.load_reference_stream(iter(records))
    assert loaded == 2
    res = engine.search("742 Evergreen")
    assert len(res) == 1
    assert res[0].street_line == "742 EVERGREEN TER"
