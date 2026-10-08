"""
Tests for the H3 spatial indexing wrapper.
==========================================
Every value must come from the real ``h3`` library (a required dependency); known vectors come from the H3
reference implementation.
"""

import h3
import pytest

from address_standardizer.spatial.h3_indexer import (
    H3_HEX_PATTERN,
    h3_distance,
    h3_to_int,
    h3_to_parent,
    int_to_h3,
    is_valid_h3,
    k_ring,
    lat_lng_to_h3,
)

KNOWN_CELL = "8a226204db27fff"


class TestEncoding:
    def test_known_reference_vectors(self):
        assert lat_lng_to_h3(37.3615593, -122.0553238, 5) == "85283473fffffff"
        assert lat_lng_to_h3(37.7749, -122.4194, 9) == h3.latlng_to_cell(37.7749, -122.4194, 9)

    def test_default_resolution_is_10(self):
        cell = lat_lng_to_h3(40.7061, -74.0060)
        assert h3.get_resolution(cell) == 10
        assert H3_HEX_PATTERN.match(cell) and is_valid_h3(cell)

    def test_every_resolution(self):
        for res in range(0, 16):
            cell = lat_lng_to_h3(40.7061, -74.0060, resolution=res)
            assert h3.get_resolution(cell) == res

    @pytest.mark.parametrize("lat,lng", [(90.0, 180.0), (-90.0, -180.0), (0.0, 0.0), (90.0, 0.0)])
    def test_boundary_coordinates_are_accepted(self, lat, lng):
        assert is_valid_h3(lat_lng_to_h3(lat, lng))

    @pytest.mark.parametrize(
        "lat,lng",
        [(95.0, 0.0), (-95.0, 0.0), (0.0, 190.0), (0.0, -190.0), (float("nan"), 0.0), (0.0, float("inf"))],
    )
    def test_invalid_coordinates_raise_instead_of_being_clamped(self, lat, lng):
        with pytest.raises(ValueError):
            lat_lng_to_h3(lat, lng)

    @pytest.mark.parametrize("res", [-1, 16, True, 1.5, "10"])
    def test_invalid_resolution_raises(self, res):
        with pytest.raises(ValueError):
            lat_lng_to_h3(0.0, 0.0, resolution=res)


class TestValidationAndIntegerForm:
    def test_is_valid_h3(self):
        assert is_valid_h3(KNOWN_CELL)
        assert is_valid_h3(KNOWN_CELL.upper())
        assert not is_valid_h3("invalid")
        assert not is_valid_h3("")
        assert not is_valid_h3(None)
        assert not is_valid_h3(12345)
        assert not is_valid_h3("0" * 15)

    def test_int_round_trip(self):
        assert int_to_h3(h3_to_int(KNOWN_CELL)) == KNOWN_CELL
        with pytest.raises(ValueError):
            h3_to_int("invalid")
        with pytest.raises(ValueError, match="Invalid integer representation"):
            int_to_h3(0)


class TestTopology:
    def test_k_ring_matches_h3(self):
        assert k_ring(KNOWN_CELL, 0) == [KNOWN_CELL]
        assert k_ring(KNOWN_CELL, -1) == [KNOWN_CELL]
        ring1, ring2 = k_ring(KNOWN_CELL, 1), k_ring(KNOWN_CELL, 2)
        assert len(ring1) == 7 and len(ring2) == 19
        assert set(ring1) == {c.lower() for c in h3.grid_disk(KNOWN_CELL, 1)}
        assert ring1 == sorted(ring1)
        with pytest.raises(ValueError, match="Invalid H3 index"):
            k_ring("invalid", 1)

    def test_distance(self):
        assert h3_distance(KNOWN_CELL, KNOWN_CELL) == 0
        neighbour = next(c for c in k_ring(KNOWN_CELL, 1) if c != KNOWN_CELL)
        assert h3_distance(KNOWN_CELL, neighbour) == 1
        far = next(c for c in k_ring(KNOWN_CELL, 3) if h3.grid_distance(KNOWN_CELL, c) == 3)
        assert h3_distance(KNOWN_CELL, far) == 3
        with pytest.raises(ValueError, match="Invalid H3 cell"):
            h3_distance("bad_origin", KNOWN_CELL)
        with pytest.raises(ValueError, match="Invalid H3 cell"):
            h3_distance(KNOWN_CELL, "bad_dest")

    def test_distance_undefined_for_far_apart_cells_is_an_error_not_a_guess(self):
        sf = lat_lng_to_h3(37.7749, -122.4194, 10)
        nyc = lat_lng_to_h3(40.7128, -74.0060, 10)
        with pytest.raises(ValueError, match="undefined"):
            h3_distance(sf, nyc)

    def test_parent(self):
        parent = h3_to_parent(KNOWN_CELL, 8)
        assert parent == h3.cell_to_parent(KNOWN_CELL, 8)
        assert h3.get_resolution(parent) == 8
        assert h3_to_parent(KNOWN_CELL, 10) == KNOWN_CELL
        with pytest.raises(ValueError, match="cannot be finer"):
            h3_to_parent("88226204dbfffff", 10)
        with pytest.raises(ValueError, match="negative"):
            h3_to_parent(KNOWN_CELL, -1)
        with pytest.raises(ValueError, match="Invalid H3 index"):
            h3_to_parent("invalid", 5)
