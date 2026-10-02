"""
Tests for Real-Time Typeahead & Autocomplete Engine.
====================================================
"""

import time
from address_standardizer.autocomplete import (
    AutocompleteSuggestion,
    AutocompleteEngine,
    autocomplete_address,
)


class TestAutocomplete:
    def test_autocomplete_suggestion_as_dict(self):
        sug = AutocompleteSuggestion(
            text="100 WALL ST, NEW YORK, NY 10005",
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            secondary_prompt_required=True,
            suggested_secondary_units=["STE 400", "STE 800"],
            highlight_ranges=[(0, 8)],
            score=1.5,
        )
        d = sug.as_dict()
        assert d["text"] == "100 WALL ST, NEW YORK, NY 10005"
        assert d["secondary_prompt_required"] is True
        assert d["suggested_secondary_units"] == ["STE 400", "STE 800"]
        assert d["highlight_ranges"] == [(0, 8)]
        assert d["score"] == 1.5

    def test_empty_and_whitespace_query(self):
        engine = AutocompleteEngine(seed=True)
        assert engine.search("") == []
        assert engine.search("    ") == []
        assert engine.search("---") == []

    def test_typeahead_search_and_sub_8ms_latency(self):
        engine = AutocompleteEngine(seed=True)

        # Warm up
        engine.search("100 Wall")

        t0 = time.perf_counter()
        results = engine.search("100 Wall")
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert len(results) >= 1
        assert "100 WALL ST" in results[0].text
        # Enforce < 8ms real-time latency requirement
        assert elapsed_ms < 8.0

    def test_secondary_unit_prompting(self):
        engine = AutocompleteEngine(seed=True)

        # 1. Multi-unit building searched without secondary unit
        res_no_sec = engine.search("100 Wall")
        assert len(res_no_sec) >= 1
        top_match = res_no_sec[0]
        assert top_match.secondary_prompt_required is True
        assert len(top_match.suggested_secondary_units) > 0
        assert "STE 400" in top_match.suggested_secondary_units

        # 2. Multi-unit building searched WITH secondary unit
        res_with_sec = engine.search("100 Wall St Ste 400")
        assert len(res_with_sec) >= 1
        match_sec = res_with_sec[0]
        assert match_sec.secondary_prompt_required is False

        # 3. Single-unit parcel (not multi-unit)
        res_single = engine.search("251 Little Falls")
        assert len(res_single) >= 1
        assert res_single[0].secondary_prompt_required is False

    def test_state_filtering(self):
        engine = AutocompleteEngine(seed=True)

        # Search with state filter NY
        res_ny = engine.search("100", state_filter="NY")
        assert all(r.state == "NY" for r in res_ny)

        # Search with state filter DE
        res_de = engine.search("1209", state_filter="DE")
        assert len(res_de) >= 1
        assert res_de[0].state == "DE"

        # Search with non-matching state filter
        res_none = engine.search("1209 N Orange", state_filter="CA")
        assert len(res_none) == 0

    def test_custom_address_indexing(self):
        engine = AutocompleteEngine(seed=False)
        assert len(engine.search("742 Evergreen")) == 0

        engine.index_address(
            street1="742 EVERGREEN TER",
            city="SPRINGFIELD",
            state="OR",
            postal_code="97477",
            is_multi_unit=False,
        )

        res = engine.search("742 Evergreen")
        assert len(res) == 1
        assert res[0].street1 == "742 EVERGREEN TER"
        assert res[0].city == "SPRINGFIELD"

        # Batch indexing
        batch = [
            {
                "street1": "1040 WEST ADDISON ST",
                "city": "CHICAGO",
                "state": "IL",
                "postal_code": "60613",
                "is_multi_unit": True,
                "known_units": ["STE 100"],
            },
            {
                "street1": "123 FAKE ST",
                "city": "SEATTLE",
                "state": "WA",
                "postal_code": "98101",
                "is_multi_unit": False,
            }
        ]
        engine.index_addresses(batch)
        res_chicago = engine.search("1040 W Addison")
        assert len(res_chicago) >= 1
        assert res_chicago[0].state == "IL"

    def test_max_results_limit(self):
        engine = AutocompleteEngine(seed=True)
        res_all = engine.search("Park", max_results=10)
        res_one = engine.search("Park", max_results=1)
        assert len(res_one) <= 1
        if res_all:
            assert len(res_one) == 1

    def test_public_functional_autocomplete_address(self):
        res = autocomplete_address("350 5th Ave", max_results=3)
        assert len(res) >= 1
        assert "350 5TH AVE" in res[0].text

    def test_fallback_unindexed_secondary_unit_and_street2(self):
        engine = AutocompleteEngine(seed=False)
        engine.index_address(
            street1="1209 N ORANGE ST",
            street2="STE 400",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
        )
        # Search exact base + unindexed secondary unit "APT 999" triggers fallback
        res = engine.search("1209 Orange Apt 999")
        assert len(res) >= 1
        assert "STE 400" in res[0].text

        # Search with non-matching base token + secondary unit breaks fallback loop early
        res_none = engine.search("1209 Nonexistent St Ste 400")
        assert len(res_none) == 0

    def test_secondary_unit_with_hash_symbol(self):
        # When query includes '#400', secondary unit is supplied so prompt should NOT be required
        results = autocomplete_address("100 Wall St #400")
        assert len(results) >= 1
        assert results[0].secondary_prompt_required is False

    def test_state_filter_full_name_and_lowercase(self):
        res_ny = autocomplete_address("100 Wall", state_filter="New York")
        assert len(res_ny) >= 1
        assert res_ny[0].state == "NY"

        res_lower = autocomplete_address("100 Wall", state_filter="ny")
        assert len(res_lower) >= 1
        assert res_lower[0].state == "NY"

    def test_accented_indexing_and_unaccented_search(self):
        engine = AutocompleteEngine(seed=False)
        engine.index_address(
            street1="100 AVENIDA DE LA CONSTITUCIÓN",
            city="SAN JUAN",
            state="PR",
            postal_code="00901",
        )
        res_unaccented = engine.search("Constitucion")
        assert len(res_unaccented) == 1
        assert "CONSTITUCIÓN" in res_unaccented[0].street1

