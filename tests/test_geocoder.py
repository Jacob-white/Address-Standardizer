"""
Tests for Census Batch Geocoder and Fallback Centroid Service.
==============================================================
"""

import io
import pytest
from unittest.mock import patch, MagicMock
from address_standardizer.geocoder import (
    CensusGeocoder,
    get_fallback_centroid,
    parse_census_geocoder_response,
)


class TestGeocoder:
    def test_fallback_centroid_zip3(self):
        # NY 10005 -> Metro NYC centroid
        coords = get_fallback_centroid(zip5="10005", state="NY")
        assert coords is not None
        lat, lon = coords
        assert round(lat, 2) == 40.71
        assert round(lon, 2) == -74.01

        # CO 80202 -> Denver centroid
        coords_co = get_fallback_centroid(zip5="80202", state="CO")
        assert coords_co is not None
        assert round(coords_co[0], 2) == 39.74

    def test_fallback_centroid_state_only(self):
        coords = get_fallback_centroid(state="TX")
        assert coords is not None
        lat, lon = coords
        assert round(lat, 2) == 31.05
        assert round(lon, 2) == -97.56

    def test_fallback_centroid_invalid(self):
        assert get_fallback_centroid(zip5="00000", state="ZZ") is None
        assert get_fallback_centroid() is None

    def test_parse_census_geocoder_response(self):
        mock_csv = (
            '"1","100 WALL ST, NEW YORK, NY, 10005","Match","Exact","100 WALL ST, NEW YORK, NY, 10005","-74.0060,40.7061","123456","R"\n'
            '"2","999 FAKE ST, NOWHERE, ZZ, 00000","No_Match","","","","",""\n'
        )
        parsed = parse_census_geocoder_response(mock_csv)
        assert len(parsed) == 1
        assert "1" in parsed
        lat, lon, tract = parsed["1"]
        assert lat == 40.7061
        assert lon == -74.0060
        assert tract == "123456"

    def test_census_geocoder_batch_success(self):
        mock_csv = (
            '"rec1","100 WALL ST, NEW YORK, NY, 10005","Match","Exact","100 WALL ST, NEW YORK, NY, 10005","-74.0060,40.7061","123456","R"\n'
        )
        geocoder = CensusGeocoder()

        mock_resp = MagicMock()
        mock_resp.read.return_value = mock_csv.encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False

        with patch("urllib.request.urlopen", return_value=mock_resp):
            records = [("rec1", "100 Wall St", "New York", "NY", "10005")]
            res = geocoder.geocode_batch(records)
            assert "rec1" in res
            assert res["rec1"]["precision"] == "rooftop"
            assert res["rec1"]["latitude"] == 40.7061
            assert res["rec1"]["longitude"] == -74.0060

    def test_census_geocoder_fallback_on_unmatched(self):
        mock_csv = (
            '"rec2","999 UNKNOWN ST, NEW YORK, NY, 10005","No_Match","","","","",""\n'
        )
        geocoder = CensusGeocoder()

        mock_resp = MagicMock()
        mock_resp.read.return_value = mock_csv.encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False

        with patch("urllib.request.urlopen", return_value=mock_resp):
            records = [("rec2", "999 Unknown St", "New York", "NY", "10005")]
            res = geocoder.geocode_batch(records, fallback_to_centroids=True)
            assert "rec2" in res
            assert res["rec2"]["precision"] == "zip_centroid"
            assert round(res["rec2"]["latitude"], 2) == 40.71
