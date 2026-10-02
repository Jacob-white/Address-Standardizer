"""
Unit and Integration Tests for Memory-Bounded Streaming Batch Processing.
========================================================================
Validates chunk generation, multiprocessing worker pool bounding,
peak RSS memory invariance, custom column mapping, and Census geocoding enrichment.
"""

import csv
import resource
from unittest.mock import MagicMock

from address_standardizer.batch import (
    chunk_generator,
    process_chunk,
    stream_standardize_csv,
    _process_row_dict,
)
from address_standardizer.geocoder import CensusGeocoder


class TestChunkGenerator:
    """Tests chunk_generator behavior across boundary conditions."""

    def test_empty_generator(self):
        chunks = list(chunk_generator([], chunk_size=10))
        assert chunks == []

    def test_exact_multiple(self):
        items = [{"id": i} for i in range(6)]
        chunks = list(chunk_generator(iter(items), chunk_size=3))
        assert len(chunks) == 2
        assert len(chunks[0]) == 3
        assert len(chunks[1]) == 3

    def test_with_remainder(self):
        items = [{"id": i} for i in range(7)]
        chunks = list(chunk_generator(iter(items), chunk_size=3))
        assert len(chunks) == 3
        assert len(chunks[0]) == 3
        assert len(chunks[1]) == 3
        assert len(chunks[2]) == 1

    def test_chunk_size_larger_than_input(self):
        items = [{"id": 1}, {"id": 2}]
        chunks = list(chunk_generator(iter(items), chunk_size=100))
        assert len(chunks) == 1
        assert len(chunks[0]) == 2


class TestProcessRowAndChunk:
    """Tests single row dictionary standardization and chunk processing."""

    def test_process_row_dict_standard_columns(self):
        row = {
            "street1": "100 Main St",
            "street2": "Suite 200",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA",
        }
        res = _process_row_dict(row)
        assert res["std_street1"] == "100 MAIN ST"
        assert res["std_street2"] == "STE 200"
        assert res["std_city"] == "NEW YORK"
        assert res["std_state"] == "NY"
        assert res["std_postal_code"] == "10001"
        assert res["std_country"] == "USA"
        assert res["normalized_address_key"] == "100 MAIN ST|STE 200|NEW YORK|NY|10001|USA"
        assert res["address_status"] == "standardized"
        assert res["is_registered_agent_hub"] == "False"

    def test_process_row_dict_custom_columns(self):
        row = {
            "addr": "200 Park Ave",
            "suite": "Fl 14",
            "town": "Chicago",
            "region": "IL",
            "zip": "60611",
            "nation": "USA",
        }
        res = _process_row_dict(
            row,
            street_col="addr",
            street2_col="suite",
            city_col="town",
            state_col="region",
            zip_col="zip",
            country_col="nation",
        )
        assert res["std_street1"] == "200 PARK AVE"
        assert res["std_street2"] == "FL 14"
        assert res["std_city"] == "CHICAGO"
        assert res["std_state"] == "IL"

    def test_process_chunk(self):
        chunk = [
            {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"},
            {"street1": "PO Box 456", "city": "Denver", "state": "CO", "postal_code": "80202"},
        ]
        results = process_chunk(chunk)
        assert len(results) == 2
        assert results[0]["std_street1"] == "100 WALL ST"
        assert results[1]["std_street1"] == "PO BOX 456"


class TestStreamStandardizeCSV:
    """Tests streaming CSV standardization, multiprocessing pool, and memory bounding."""

    def test_stream_standardize_single_worker(self, tmp_path):
        input_csv = tmp_path / "in.csv"
        output_csv = tmp_path / "out.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            w.writerow(["1", "500 South Street", "", "Philadelphia", "PA", "19147", "USA"])
            w.writerow(["2", "123-45 82nd Ave", "Apt 4B", "Kew Gardens", "NY", "11415", "USA"])

        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=1,
            max_workers=1,
        )
        assert total == 2
        assert output_csv.exists()

        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["std_street1"] == "500 SOUTH ST"
            assert rows[1]["std_street1"] == "123-45 82ND AVE"
            assert rows[1]["std_street2"] == "APT 4B"

    def test_stream_standardize_multiprocessing_pool(self, tmp_path):
        input_csv = tmp_path / "in_mp.csv"
        output_csv = tmp_path / "out_mp.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            for i in range(20):
                w.writerow([str(i), f"{100 + i} Main St", "", "New York", "NY", "10001", "USA"])

        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=5,
            max_workers=2,
        )
        assert total == 20
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 20
            assert rows[0]["std_street1"] == "100 MAIN ST"
            assert rows[19]["std_street1"] == "119 MAIN ST"

    def test_stream_standardize_with_geocoding(self, tmp_path):
        input_csv = tmp_path / "in_geo.csv"
        output_csv = tmp_path / "out_geo.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "city", "state", "postal_code"])
            w.writerow(["1", "100 Wall St", "New York", "NY", "10005"])

        mock_geocoder = MagicMock(spec=CensusGeocoder)
        mock_geocoder.geocode_batch.return_value = {
            "0": {"latitude": 40.7061, "longitude": -74.0060, "precision": "rooftop"}
        }

        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=10,
            max_workers=1,
            geocode=True,
            geocoder=mock_geocoder,
        )
        assert total == 1
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["latitude"] == "40.7061"
            assert rows[0]["longitude"] == "-74.006"
            assert rows[0]["geocode_precision"] == "rooftop"

    def test_stream_standardize_with_geocoding_multiprocessing(self, tmp_path):
        input_csv = tmp_path / "in_geo_mp.csv"
        output_csv = tmp_path / "out_geo_mp.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "city", "state", "postal_code"])
            w.writerow(["1", "100 Wall St", "New York", "NY", "10005"])
            w.writerow(["2", "200 Park Ave", "New York", "NY", "10166"])

        mock_geocoder = MagicMock(spec=CensusGeocoder)
        mock_geocoder.geocode_batch.return_value = {
            "0": {"latitude": 40.7061, "longitude": -74.0060, "precision": "rooftop"},
            "1": {"latitude": 40.7533, "longitude": -73.9774, "precision": "rooftop"},
        }

        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=5,
            max_workers=2,
            geocode=True,
            geocoder=mock_geocoder,
        )
        assert total == 2
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["latitude"] == "40.7061"
            assert rows[1]["latitude"] == "40.7533"

    def test_stream_standardize_geocode_partial_matches(self, tmp_path):
        input_csv = tmp_path / "in_geo_partial.csv"
        output_csv = tmp_path / "out_geo_partial.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "city", "state", "postal_code", "country"])
            w.writerow(["1", "100 Wall St", "New York", "NY", "10005", "USA"])
            w.writerow(["2", "Unmatched Address", "Nowhere", "NY", "10005", "USA"])

        mock_geocoder = MagicMock(spec=CensusGeocoder)
        # Only row "0" is matched; row "1" is omitted from geocoder result
        mock_geocoder.geocode_batch.return_value = {
            "0": {"latitude": 40.7061, "longitude": -74.0060, "precision": "rooftop"},
        }

        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=5,
            max_workers=1,
            geocode=True,
            geocoder=mock_geocoder,
        )
        assert total == 2
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]["latitude"] == "40.7061"
            assert rows[1]["latitude"] == ""

    def test_stream_standardize_geocode_non_us(self, tmp_path):
        input_csv = tmp_path / "in_geo_non_us.csv"
        output_csv = tmp_path / "out_geo_non_us.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "city", "state", "postal_code", "country"])
            w.writerow(["1", "100 King St", "Toronto", "ON", "M5V 2T6", "CAN"])

        mock_geocoder = MagicMock(spec=CensusGeocoder)
        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=5,
            max_workers=1,
            geocode=True,
            geocoder=mock_geocoder,
        )
        assert total == 1
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]["latitude"] == ""

    def test_memory_bounded_large_stream(self, tmp_path):
        """Validates that a 5,000 row stream operates within bounded memory footprint (< 100MB RSS)."""
        input_csv = tmp_path / "large_in.csv"
        output_csv = tmp_path / "large_out.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            for i in range(5000):
                w.writerow([str(i), f"{i % 1000 + 1} Main St", "Suite 100", "Springfield", "IL", "62701", "USA"])

        def _get_rss_mb() -> float:
            try:
                with open("/proc/self/status") as f_stat:
                    for line in f_stat:
                        if line.startswith("VmRSS:"):
                            return float(line.split()[1]) / 1024.0
            except Exception:
                pass
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

        mem_before = _get_rss_mb()

        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=1000,
            max_workers=2,
        )
        assert total == 5000

        mem_after = _get_rss_mb()
        rss_growth_mb = mem_after - mem_before
        # Growth during streaming must remain tiny (< 50MB)
        assert rss_growth_mb < 50.0, f"Memory grew excessively: {rss_growth_mb:.2f} MB"

    def test_batch_with_confidence_single_and_multi_worker(self, tmp_path):
        input_csv = tmp_path / "conf_in.csv"
        out_single = tmp_path / "conf_out_single.csv"
        out_multi = tmp_path / "conf_out_multi.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            w.writerow(["1", "100 Wall St", "Suite 400", "New York", "NY", "10005", "USA"])
            w.writerow(["2", "1209 North Orange St", "Suite 100", "Wilmington", "DE", "19801", "USA"])

        # Test single worker
        total_1 = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(out_single),
            chunk_size=10,
            max_workers=1,
            include_confidence=True,
        )
        assert total_1 == 2
        with open(out_single, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert "confidence_score" in rows[0]
            assert "routing_tier" in rows[0]
            assert float(rows[0]["confidence_score"]) >= 0.95
            assert rows[0]["routing_tier"] == "AUTO_PASS"

        # Test multi worker
        total_2 = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(out_multi),
            chunk_size=1,
            max_workers=2,
            include_confidence=True,
        )
        assert total_2 == 2
        with open(out_multi, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[1]["std_street1"] == "1209 N ORANGE ST"
            assert rows[1]["is_registered_agent_hub"] == "True"
            assert "confidence_score" in rows[1]
