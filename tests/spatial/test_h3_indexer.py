"""
Tests for H3 Hexagonal Spatial Indexing Subsystem.
===================================================
Validates Resolution 10 cell calculation, k-ring expansion,
grid distance, parent hierarchy, bit packing, and pure-Python fallback.
"""

from unittest.mock import MagicMock, patch
import pytest

from address_standardizer.spatial.h3_indexer import (
    has_compiled_h3,
    lat_lng_to_h3,
    is_valid_h3,
    h3_to_int,
    int_to_h3,
    k_ring,
    h3_distance,
    h3_to_parent,
    _axial_round,
)


class TestH3Indexer:
    def test_has_compiled_h3(self):
        # In current environment, compiled h3 is not installed
        res = has_compiled_h3()
        assert isinstance(res, bool)

    def test_axial_round_branches(self):
        # Case 1: x_diff > y_diff and x_diff > z_diff
        rx, rz = _axial_round(1.4, -0.7)
        assert isinstance(rx, int)
        assert isinstance(rz, int)

        # Case 2: y_diff > z_diff
        rx2, rz2 = _axial_round(0.1, 0.1)
        assert isinstance(rx2, int)
        assert isinstance(rz2, int)

        # Case 3: else branch (z_diff >= y_diff and z_diff >= x_diff)
        rx3, rz3 = _axial_round(0.1, 1.4)
        assert isinstance(rx3, int)
        assert isinstance(rz3, int)

    def test_module_import_with_compiled_h3(self):
        import sys
        import importlib
        mock_h3 = MagicMock()
        with patch.dict(sys.modules, {"h3": mock_h3}):
            mod = importlib.import_module("address_standardizer.spatial.h3_indexer")
            importlib.reload(mod)
            assert mod.has_compiled_h3() is True

        # Reload cleanly back without h3
        if "h3" in sys.modules:
            del sys.modules["h3"]
        mod = importlib.import_module("address_standardizer.spatial.h3_indexer")
        importlib.reload(mod)
        assert mod.has_compiled_h3() is False

    def test_lat_lng_to_h3_pure_python(self):
        # Standard Manhattan coords
        h3_idx = lat_lng_to_h3(40.7061, -74.0060, resolution=10)
        assert len(h3_idx) == 15
        assert is_valid_h3(h3_idx)

        # Clamping / extreme coords
        h3_north = lat_lng_to_h3(95.0, 190.0, resolution=10)
        assert is_valid_h3(h3_north)

        h3_south = lat_lng_to_h3(-95.0, -190.0, resolution=10)
        assert is_valid_h3(h3_south)

        # Different resolutions
        h3_res8 = lat_lng_to_h3(40.7061, -74.0060, resolution=8)
        assert is_valid_h3(h3_res8)
        assert (int(h3_res8, 16) >> 52) & 0xF == 8

        h3_res15 = lat_lng_to_h3(40.7061, -74.0060, resolution=15)
        assert is_valid_h3(h3_res15)
        assert (int(h3_res15, 16) >> 52) & 0xF == 15

    def test_is_valid_h3(self):
        # Valid
        assert is_valid_h3("8a226204db27fff") is True
        assert is_valid_h3("8A226204DB27FFF") is True

        # Non-string
        assert is_valid_h3(None) is False  # type: ignore
        assert is_valid_h3(12345) is False  # type: ignore

        # Invalid lengths
        assert is_valid_h3("8a226204db27ff") is False  # 14 chars
        assert is_valid_h3("8a226204db27ffff") is False  # 16 chars

        # Invalid hex
        assert is_valid_h3("8a226204db27ffg") is False

        # Invalid mode (mode != 1)
        # val with mode 0
        bad_mode = f"{((0 & 0xF) << 59) | ((10 & 0xF) << 52):015x}"
        assert is_valid_h3(bad_mode) is False

        # Invalid resolution (> 15)
        # In a 15-char hex, bits 52-55 can hold up to 15, so res is always <= 15 for valid integer.

    def test_h3_to_int_and_int_to_h3(self):
        h3_str = "8a226204db27fff"
        h3_int = h3_to_int(h3_str)
        assert isinstance(h3_int, int)
        assert h3_int > 0

        recovered = int_to_h3(h3_int)
        assert recovered == h3_str

        # Errors on invalid input
        with pytest.raises(ValueError, match="Invalid H3 index"):
            h3_to_int("not_an_h3_index")

        with pytest.raises(ValueError, match="Invalid integer representation"):
            int_to_h3(0)  # mode 0

    def test_k_ring_pure_python(self):
        h3_str = "8a226204db27fff"

        # ring_size <= 0
        assert k_ring(h3_str, 0) == [h3_str]
        assert k_ring(h3_str, -1) == [h3_str]

        # ring_size = 1
        ring1 = k_ring(h3_str, 1)
        assert h3_str in ring1
        assert len(ring1) > 1
        for cell in ring1:
            assert is_valid_h3(cell)

        # ring_size = 2
        ring2 = k_ring(h3_str, 2)
        assert len(ring2) >= len(ring1)

        # Invalid index error
        with pytest.raises(ValueError, match="Invalid H3 index"):
            k_ring("invalid", 1)

    def test_h3_distance_pure_python(self):
        h3_1 = "8a226204db27fff"
        h3_2 = "8a226204db20fff"

        # Same cell
        assert h3_distance(h3_1, h3_1) == 0

        # Different cells
        dist = h3_distance(h3_1, h3_2)
        assert dist >= 0

        # Errors
        with pytest.raises(ValueError, match="Invalid H3 cell"):
            h3_distance("bad_origin", h3_1)
        with pytest.raises(ValueError, match="Invalid H3 cell"):
            h3_distance(h3_1, "bad_dest")

    def test_h3_to_parent_pure_python(self):
        h3_str = "8a226204db27fff"
        p8 = h3_to_parent(h3_str, 8)
        assert is_valid_h3(p8)
        assert (int(p8, 16) >> 52) & 0xF == 8

        p5 = h3_to_parent(h3_str, 5)
        assert is_valid_h3(p5)
        assert (int(p5, 16) >> 52) & 0xF == 5

        # Same res parent
        p10 = h3_to_parent(h3_str, 10)
        assert is_valid_h3(p10)

        # Finer res error
        with pytest.raises(ValueError, match="cannot be finer"):
            h3_to_parent(h3_str, 11)

        # Negative res error
        with pytest.raises(ValueError, match="cannot be negative"):
            h3_to_parent(h3_str, -1)

        # Invalid h3
        with pytest.raises(ValueError, match="Invalid H3 index"):
            h3_to_parent("invalid", 5)

    def test_compiled_h3_mocked_branches(self):
        # Test the branches where compiled h3 library is available
        mock_lib = MagicMock()
        mock_lib.latlng_to_cell.return_value = "8a226204db27fff"
        mock_lib.grid_disk.return_value = ["8a226204db27fff", "8a226204db20fff"]
        mock_lib.grid_distance.return_value = 2
        mock_lib.cell_to_parent.return_value = "88226204dbfffff"

        with patch("address_standardizer.spatial.h3_indexer._HAS_COMPILED_H3", True), \
             patch("address_standardizer.spatial.h3_indexer._h3_lib", mock_lib):
            # lat_lng_to_h3
            c = lat_lng_to_h3(40.0, -74.0, 10)
            assert c == "8a226204db27fff"
            mock_lib.latlng_to_cell.assert_called_once_with(40.0, -74.0, 10)

            # k_ring
            ring = k_ring("8a226204db27fff", 1)
            assert len(ring) == 2
            mock_lib.grid_disk.assert_called_once_with("8a226204db27fff", 1)

            # h3_distance
            d = h3_distance("8a226204db27fff", "8a226204db20fff")
            assert d == 2
            mock_lib.grid_distance.assert_called_once_with("8a226204db27fff", "8a226204db20fff")

            # h3_to_parent
            p = h3_to_parent("8a226204db27fff", 8)
            assert p == "88226204dbfffff"
            mock_lib.cell_to_parent.assert_called_once_with("8a226204db27fff", 8)

        # Test alternative legacy compiled method names: geo_to_h3, k_ring, h3_distance, h3_to_parent
        mock_lib_legacy = MagicMock(spec=["geo_to_h3", "k_ring", "h3_distance", "h3_to_parent"])
        mock_lib_legacy.geo_to_h3.return_value = "8a226204db27fff"
        mock_lib_legacy.k_ring.return_value = ["8a226204db27fff"]
        mock_lib_legacy.h3_distance.return_value = 3
        mock_lib_legacy.h3_to_parent.return_value = "88226204dbfffff"

        with patch("address_standardizer.spatial.h3_indexer._HAS_COMPILED_H3", True), \
             patch("address_standardizer.spatial.h3_indexer._h3_lib", mock_lib_legacy):
            c_leg = lat_lng_to_h3(40.0, -74.0, 10)
            assert c_leg == "8a226204db27fff"
            mock_lib_legacy.geo_to_h3.assert_called_once_with(40.0, -74.0, 10)

            ring_leg = k_ring("8a226204db27fff", 1)
            assert ring_leg == ["8a226204db27fff"]
            mock_lib_legacy.k_ring.assert_called_once_with("8a226204db27fff", 1)

            d_leg = h3_distance("8a226204db27fff", "8a226204db20fff")
            assert d_leg == 3
            mock_lib_legacy.h3_distance.assert_called_once_with("8a226204db27fff", "8a226204db20fff")

            p_leg = h3_to_parent("8a226204db27fff", 8)
            assert p_leg == "88226204dbfffff"
            mock_lib_legacy.h3_to_parent.assert_called_once_with("8a226204db27fff", 8)
