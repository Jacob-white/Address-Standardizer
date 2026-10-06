"""
Unit & Integration Tests for Rooftop Address Resolution.
=========================================================
Tests the 'rooftop_address' and 'full_rooftop_address' fields on StandardizedAddress,
ensuring strict exclusion of secondary units (suite, apt, fl, unit, bldg, room, etc.)
while preserving physical structural address tokens, street suffixes, and directionals.
"""

import pytest
from address_standardizer import (
    StandardizedAddress,
    standardize_address,
    clean_rooftop_address,
    batch_standardize,
)
from address_standardizer.cache import make_cache_key


class TestRooftopAddress:
    """Tests for physical rooftop address line normalization and exclusion of unit designators."""

    @pytest.mark.parametrize(
        "input_str, city, state, postal, expected_rooftop",
        [
            ("123 Main St, Suite 400", "New York", "NY", "10001", "123 MAIN ST"),
            ("123 Main St Ste 400", "New York", "NY", "10001", "123 MAIN ST"),
            ("100 Wall Street, 12th Floor", "New York", "NY", "10005", "100 WALL ST"),
            ("100 Wall St 12TH FL", "New York", "NY", "10005", "100 WALL ST"),
            ("450 Lexington Ave Apt 4B", "New York", "NY", "10017", "450 LEXINGTON AVE"),
            ("742 Evergreen Terr, Unit 3", "Springfield", "OR", "97477", "742 EVERGREEN TER"),
            ("500 North Michigan Ave # 300", "Chicago", "IL", "60611", "500 N MICHIGAN AVE"),
            ("500 North Michigan Ave #300", "Chicago", "IL", "60611", "500 N MICHIGAN AVE"),
            ("200 Park Ave Room 1000", "New York", "NY", "10166", "200 PARK AVE"),
            ("200 Park Ave RM 1000", "New York", "NY", "10166", "200 PARK AVE"),
            ("1 World Trade Center, Dept 5", "New York", "NY", "10007", "1 WORLD TRADE CTR"),
            ("1209 N Orange St, Penthouse 2", "Wilmington", "DE", "19801", "1209 N ORANGE ST"),
            ("1209 N Orange St PH 2", "Wilmington", "DE", "19801", "1209 N ORANGE ST"),
            ("30 N Gould St Bldg A", "Sheridan", "WY", "82801", "30 N GOULD ST"),
            ("100 Main St, Bldg 4, Suite 200", "Dallas", "TX", "75201", "100 MAIN ST"),
            ("100 Main St Bldg 4, Fl 3, Ste 200", "Dallas", "TX", "75201", "100 MAIN ST"),
            ("500 Broadway", "New York", "NY", "10012", "500 BROADWAY"),
            ("123 1/2 Main St Suite 200", "Los Angeles", "CA", "90012", "123 1/2 MAIN ST"),
            ("123-45 84th Rd Apt 2F", "Kew Gardens", "NY", "11415", "123-45 84TH RD"),
        ],
    )
    def test_standardize_us_rooftop_address(
        self, input_str, city, state, postal, expected_rooftop
    ):
        res = standardize_address(input_str, city=city, state=state, postal_code=postal)
        assert res.address_status == "standardized"
        assert res.rooftop_address == expected_rooftop
        assert res.full_rooftop_address is not None
        assert res.full_rooftop_address.startswith(expected_rooftop)

    def test_international_rooftop_address(self):
        res = standardize_address("Flat 4, 10 Downing Street", city="London", country="GBR")
        assert res.address_status == "standardized"
        assert res.rooftop_address == "10 DOWNING ST"
        assert res.street2 == "APT 4"
        assert res.full_rooftop_address == "10 DOWNING ST, LONDON, GBR"

    def test_fast_path_rooftop_address(self):
        # Path A: Structured parameters
        res1 = standardize_address(
            street1="100 Main St",
            street2="Suite 400",
            city="New York",
            state="NY",
            postal_code="10005",
        )
        assert res1.rooftop_address == "100 MAIN ST"
        assert res1.street2 == "STE 400"

        # Path B: Canonical comma single-string
        res2 = standardize_address("100 Main St, Suite 400, New York, NY 10005")
        assert res2.rooftop_address == "100 MAIN ST"
        assert res2.street2 == "STE 400"

    def test_dual_physical_and_po_box_rooftop(self):
        res = standardize_address(
            "100 Main St, PO Box 500",
            city="Boston",
            state="MA",
            postal_code="02108",
        )
        assert res.street1 == "100 MAIN ST"
        assert "PO BOX 500" in res.street2
        assert res.rooftop_address == "100 MAIN ST"

    def test_po_box_and_non_physical_returns_none(self):
        # Pure PO Box has no physical rooftop
        res_po = standardize_address("PO Box 500", city="Boston", state="MA", postal_code="02108")
        assert res_po.rooftop_address is None
        assert res_po.full_rooftop_address is None

        # Rural route has no physical rooftop
        res_rr = standardize_address("RR 2 BOX 15", city="Boise", state="ID", postal_code="83701")
        assert res_rr.rooftop_address is None

        # Private residence has no physical rooftop exposed
        res_priv = standardize_address("Private Residence", city="Miami", state="FL", postal_code="33101")
        assert res_priv.is_private_residence is True
        assert res_priv.rooftop_address is None

        # Locality only has no physical rooftop
        res_loc = standardize_address(city="Naples", state="FL", postal_code="34102", allow_locality=True)
        assert res_loc.rooftop_address is None

        # Empty address
        res_empty = standardize_address("")
        assert res_empty.rooftop_address is None

    def test_as_dict_backward_compatibility_and_extended(self):
        res = standardize_address("123 Main St, Suite 400, New York, NY 10001")

        # 1. Strict 14-field backward compatibility
        d_default = res.as_dict()
        assert len(d_default) == 14
        assert "rooftop_address" not in d_default

        # 2. Explicit include_rooftop flag
        d_rooftop = res.as_dict(include_rooftop=True)
        assert "rooftop_address" in d_rooftop
        assert d_rooftop["rooftop_address"] == "123 MAIN ST"
        assert d_rooftop["full_rooftop_address"] == "123 MAIN ST, NEW YORK, NY 10001"

        # 3. Comprehensive enterprise extended dict
        d_ext = res.as_extended_dict()
        assert d_ext["rooftop_address"] == "123 MAIN ST"
        assert d_ext["full_rooftop_address"] == "123 MAIN ST, NEW YORK, NY 10001"

    def test_batch_standardize_includes_rooftop(self):
        records = [
            "100 Wall Street, Suite 400, New York, NY 10005",
            "200 Park Ave, Fl 12, New York, NY 10166",
        ]
        results = list(batch_standardize(records))
        assert len(results) == 2
        assert results[0].rooftop_address == "100 WALL ST"
        assert results[1].rooftop_address == "200 PARK AVE"

    def test_cache_roundtrip_preserves_rooftop(self):
        from address_standardizer.cache import SQLiteCache
        cache = SQLiteCache()
        res = standardize_address("450 Lexington Ave, Suite 200, New York, NY 10017")
        assert res.rooftop_address == "450 LEXINGTON AVE"

        cache_key = make_cache_key({"street1": "450 Lexington Ave, Suite 200, New York, NY 10017"})
        cache.set(cache_key, res)

        cached_obj = cache.get(cache_key)
        assert isinstance(cached_obj, StandardizedAddress)
        assert cached_obj.rooftop_address == "450 LEXINGTON AVE"
        assert cached_obj.full_rooftop_address == "450 LEXINGTON AVE, NEW YORK, NY 10017"

    def test_clean_rooftop_address_standalone_function(self):
        assert clean_rooftop_address("123 MAIN ST STE 400") == "123 MAIN ST"
        assert clean_rooftop_address("100 WALL ST 12TH FL") == "100 WALL ST"
        assert clean_rooftop_address("100 MAIN ST BLDG 4 STE 200") == "100 MAIN ST"
        assert clean_rooftop_address("300 LEVEL CREEK RD") == "300 LEVEL CREEK RD"
        assert clean_rooftop_address("100 BUILDING WAY") == "100 BUILDING WAY"
        assert clean_rooftop_address("PO BOX 123") is None
        assert clean_rooftop_address("PRIVATE RESIDENCE") is None
        assert clean_rooftop_address("") is None
