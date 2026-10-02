"""
Tests for Census Batch Geocoder and Fallback Centroid Service.
==============================================================
"""

import io
import urllib.error
import pytest
from unittest.mock import patch, MagicMock
from address_standardizer.geocoder import (
    CensusGeocoder,
    get_fallback_centroid,
    parse_census_geocoder_response,
)


class TestGeocoder:
    def test_fallback_centroid_zip3_metro(self):
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

        # IL 60611 -> Chicago centroid
        coords_il = get_fallback_centroid(zip5="60611", state="IL")
        assert coords_il is not None
        assert round(coords_il[0], 2) == 41.88

        # CA 94105 -> San Francisco centroid
        coords_ca = get_fallback_centroid(zip5="94105", state="CA")
        assert coords_ca is not None
        assert round(coords_ca[0], 2) == 37.77

    def test_fallback_centroid_zip3_non_metro_falls_back_to_state(self):
        # 35004 -> zip3 '350' (Alabama, not in METRO_ZIP3_CENTROIDS)
        coords_al = get_fallback_centroid(zip5="35004", state="AL")
        assert coords_al is not None
        # Should resolve via ZIP3_TO_STATE to Alabama centroid
        assert round(coords_al[0], 2) == 32.81
        assert round(coords_al[1], 2) == -86.79

        # 78701 -> zip3 '787' (Austin TX, not in METRO_ZIP3_CENTROIDS)
        coords_tx = get_fallback_centroid(zip5="78701")
        assert coords_tx is not None
        assert round(coords_tx[0], 2) == 31.05
        assert round(coords_tx[1], 2) == -97.56

    def test_fallback_centroid_state_only(self):
        coords = get_fallback_centroid(state="TX")
        assert coords is not None
        lat, lon = coords
        assert round(lat, 2) == 31.05
        assert round(lon, 2) == -97.56

        # Territories
        coords_pr = get_fallback_centroid(state="PR")
        assert coords_pr is not None
        assert round(coords_pr[0], 2) == 18.22

        coords_vi = get_fallback_centroid(state="VI")
        assert coords_vi is not None
        assert round(coords_vi[0], 2) == 18.34

        coords_gu = get_fallback_centroid(state="GU")
        assert coords_gu is not None
        assert round(coords_gu[0], 2) == 13.44

    def test_fallback_centroid_short_zip_with_state(self):
        # Short zip (< 3 digits) falls back to state
        coords = get_fallback_centroid(zip5="12", state="CA")
        assert coords is not None
        assert round(coords[0], 2) == 36.12

    def test_fallback_centroid_invalid(self):
        assert get_fallback_centroid(zip5="00000", state="ZZ") is None
        assert get_fallback_centroid(zip5="abc", state="ZZ") is None
        assert get_fallback_centroid() is None

    def test_parse_census_geocoder_response(self):
        mock_csv = (
            '"1","100 WALL ST, NEW YORK, NY, 10005","Match","Exact","100 WALL ST, NEW YORK, NY, 10005","-74.0060,40.7061","123456","R"\n'
            '"2","999 FAKE ST, NOWHERE, ZZ, 00000","No_Match","","","","",""\n'
            '"3","BAD COORDS ST, NEW YORK, NY, 10005","Match","Exact","","not_float,bad_num","123456","R"\n'
            '"short_row"\n'
        )
        parsed = parse_census_geocoder_response(mock_csv)
        assert len(parsed) == 1
        assert "1" in parsed
        lat, lon, tract = parsed["1"]
        assert lat == 40.7061
        assert lon == -74.0060
        assert tract == "123456"

    def test_parse_census_geocoder_empty_response(self):
        assert parse_census_geocoder_response("") == {}

    def test_census_geocoder_batch_empty_records(self):
        geocoder = CensusGeocoder()
        assert geocoder.geocode_batch([]) == {}

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
            records = [("rec1", '100 "Wall" St', "New York", "NY", "10005")]
            res = geocoder.geocode_batch(records)
            assert "rec1" in res
            assert res["rec1"]["precision"] == "rooftop"
            assert res["rec1"]["latitude"] == 40.7061
            assert res["rec1"]["longitude"] == -74.0060
            assert res["rec1"]["census_tract"] == "123456"

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

    def test_census_geocoder_no_fallback_on_unmatched(self):
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
            res = geocoder.geocode_batch(records, fallback_to_centroids=False)
            assert "rec2" not in res

    def test_census_geocoder_network_exception_fallback(self):
        # When network request raises URLError or timeout, fallback_to_centroids still returns coords
        geocoder = CensusGeocoder(timeout_seconds=5)

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
            records = [("rec_err", "100 Wall St", "New York", "NY", "10005")]
            res = geocoder.geocode_batch(records, fallback_to_centroids=True)
            assert "rec_err" in res
            assert res["rec_err"]["precision"] == "zip_centroid"
            assert round(res["rec_err"]["latitude"], 2) == 40.71
