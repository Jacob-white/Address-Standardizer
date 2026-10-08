"""
Tests for Open Reference Data Ingestion Subsystem (ETL).
=========================================================
Validates parsing and batch ingestion for:
  - OpenAddresses cadastral points and parcel IDs
  - US Census TIGER/Line road centerline segments
  - OpenStreetMap (OSM) building centroid Shoelace polygon calculations
  - Complete database initialization via build_spatial_database
"""

import io
import json
import pytest

from address_standardizer.spatial.engine import SpatialEngine
from address_standardizer.spatial.ingestion import (
    snap_coordinate,
    calculate_polygon_centroid,
    OpenAddressesIngestor,
    TigerLineIngestor,
    OsmBuildingIngestor,
    build_spatial_database,
)


class TestSpatialIngestion:
    @classmethod
    def setup_class(cls):
        cls.engine = SpatialEngine(seed=False)

    @classmethod
    def teardown_class(cls):
        cls.engine.close()

    def test_snap_coordinate(self):
        assert snap_coordinate(40.123456789) == 40.123457
        assert snap_coordinate(40.123456789, precision=2) == 40.12

    def test_calculate_polygon_centroid_branches(self):
        # 1. Empty coordinates (n == 0)
        assert calculate_polygon_centroid([]) == (0.0, 0.0)

        # 2. n < 3 (1 or 2 points)
        assert calculate_polygon_centroid([[10.0, 20.0]]) == (10.0, 20.0)
        assert calculate_polygon_centroid([[10.0, 20.0], [30.0, 40.0]]) == (20.0, 30.0)

        # 3. Valid polygon (Square: (0,0), (2,0), (2,2), (0,2), (0,0))
        # Centroid should be (1.0, 1.0)
        coords = [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0], [0.0, 0.0]]
        cx, cy = calculate_polygon_centroid(coords)
        assert cx == 1.0
        assert cy == 1.0

        # 4. Degenerate collinear points (Area ~ 0)
        degenerate = [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [0.0, 0.0]]
        dcx, dcy = calculate_polygon_centroid(degenerate)
        assert isinstance(dcx, float)
        assert isinstance(dcy, float)

    def test_openaddresses_ingestor_records_and_skips(self):
        ingestor = OpenAddressesIngestor(self.engine)
        records = [
            # Valid record with uppercase keys
            {
                "LATITUDE": 40.7128,
                "LONGITUDE": -74.0060,
                "NUMBER": "250",
                "STREET": "Broadway",
                "UNIT": "Ste 100",
                "CITY": "New York",
                "REGION": "NY",
                "POSTCODE": "10007",
                "COUNTRY": "USA",
                "ID": "NY-MAN-250",
            },
            # Valid record with lowercase keys
            {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "number": 100,
                "street": "Market St",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105",
                "country": "USA",
                "parcel_id": "SF-100",
            },
            # Missing latitude/longitude -> skipped
            {"NUMBER": "1", "STREET": "Main St"},
            # Invalid non-numeric latitude -> skipped
            {"LATITUDE": "bad_lat", "LONGITUDE": -70.0, "STREET": "Main St"},
            # Missing street -> skipped
            {"LATITUDE": 40.0, "LONGITUDE": -74.0, "STREET": ""},
        ]
        count = ingestor.ingest_records(records)
        assert count == 2

    def test_openaddresses_ingest_csv(self, tmp_path):
        ingestor = OpenAddressesIngestor(self.engine)
        csv_content = (
            "LATITUDE,LONGITUDE,NUMBER,STREET,UNIT,CITY,REGION,POSTCODE,COUNTRY,ID\n"
            "34.0522,-118.2437,200,N Spring St,,Los Angeles,CA,90012,USA,LA-200\n"
        )
        # From buffer
        buf = io.StringIO(csv_content)
        count_buf = ingestor.ingest_csv(buf)
        assert count_buf == 1

        # From file path
        csv_file = str(tmp_path / "openaddrs.csv")
        with open(csv_file, "w") as f:
            f.write(csv_content)
        count_file = ingestor.ingest_csv(csv_file)
        assert count_file == 0  # same address_key: re-ingesting must not duplicate points

        # Error on bad type
        with pytest.raises(TypeError, match="Expected file path or file-like buffer"):
            ingestor.ingest_csv(12345)

    def test_tiger_line_ingestor_records_and_skips(self):
        ingestor = TigerLineIngestor(self.engine)
        segments = [
            # Valid segment
            {
                "street_name": "PINE ST",
                "from_number": 1,
                "to_number": 99,
                "start_lat": 47.61,
                "start_lon": -122.33,
                "end_lat": 47.62,
                "end_lon": -122.34,
                "parity": "BOTH",
                "postal_code": "98101",
                "city": "SEATTLE",
                "state": "WA",
                "country_iso3": "USA",
                "source": "TIGER",
            },
            # Missing street name -> skipped
            {"from_number": 1, "to_number": 10},
            # Missing coordinates -> skipped
            {"street_name": "BAD ST", "from_number": 1, "to_number": 10},
            # Non-numeric coordinate -> skipped
            {
                "street_name": "BAD NUM ST",
                "from_number": 1,
                "to_number": 10,
                "start_lat": "not_a_num",
                "start_lon": -122.0,
                "end_lat": 47.0,
                "end_lon": -122.0,
            },
        ]
        count = ingestor.ingest_segments(segments)
        assert count == 1

    def test_tiger_line_ingest_csv(self, tmp_path):
        ingestor = TigerLineIngestor(self.engine)
        csv_content = (
            "street_name,from_number,to_number,start_lat,start_lon,end_lat,end_lon,parity,postal_code,city,state,country_iso3,source\n"
            "OAK ST,100,200,42.0,-71.0,42.01,-71.01,EVEN,02108,BOSTON,MA,USA,TIGER\n"
        )
        # From buffer
        buf = io.StringIO(csv_content)
        assert ingestor.ingest_csv(buf) == 1

        # From file path
        f_path = str(tmp_path / "tiger.csv")
        with open(f_path, "w") as f:
            f.write(csv_content)
        assert ingestor.ingest_csv(f_path) == 1

        # Error on bad type
        with pytest.raises(TypeError, match="Expected file path or file-like buffer"):
            ingestor.ingest_csv(None)

    def test_osm_building_ingestor_features_and_skips(self):
        ingestor = OsmBuildingIngestor(self.engine)
        features = [
            # Point feature
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-73.9851, 40.7488]},
                "properties": {
                    "addr:housenumber": "350",
                    "addr:street": "5th Ave",
                    "addr:city": "New York",
                    "addr:state": "NY",
                    "addr:postcode": "10118",
                },
            },
            # Polygon feature
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[-73.986, 40.748], [-73.984, 40.748], [-73.984, 40.749], [-73.986, 40.749], [-73.986, 40.748]]
                    ],
                },
                "properties": {
                    "addr:housenumber": "352",
                    "addr:street": "5th Ave",
                    "addr:city": "New York",
                    "addr:state": "NY",
                    "addr:postcode": "10118",
                },
            },
            # MultiPolygon feature
            {
                "type": "Feature",
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [[[-73.98, 40.74], [-73.97, 40.74], [-73.97, 40.75], [-73.98, 40.74]]]
                    ],
                },
                "properties": {
                    "addr:housenumber": "400",
                    "addr:street": "Lexington Ave",
                },
            },
            # Missing geometry coordinates -> skipped
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": []},
                "properties": {"addr:street": "Bad St"},
            },
            # Missing street name in properties -> skipped
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-73.0, 40.0]},
                "properties": {"addr:housenumber": "10"},
            },
        ]
        count = ingestor.ingest_features(features)
        assert count == 3

    def test_osm_building_ingest_geojson(self, tmp_path):
        ingestor = OsmBuildingIngestor(self.engine)
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-74.0, 40.7]},
                    "properties": {"addr:housenumber": "1", "addr:street": "Liberty St"},
                }
            ],
        }
        # Buffer
        buf = io.StringIO(json.dumps(geojson_data))
        assert ingestor.ingest_geojson(buf) == 1

        # File
        g_file = str(tmp_path / "osm.geojson")
        with open(g_file, "w") as f:
            json.dump(geojson_data, f)
        assert ingestor.ingest_geojson(g_file) == 0  # already ingested: no duplicate points

        # Error
        with pytest.raises(TypeError, match="Expected file path or file-like buffer"):
            ingestor.ingest_geojson(123)

    def test_build_spatial_database(self, tmp_path):
        out_db = str(tmp_path / "built_spatial.db")
        oa_sample = [
            {
                "LATITUDE": 40.75,
                "LONGITUDE": -73.98,
                "NUMBER": "10",
                "STREET": "Time Sq",
                "CITY": "New York",
                "REGION": "NY",
                "POSTCODE": "10036",
            }
        ]
        tiger_sample = [
            {
                "street_name": "7TH AVE",
                "from_number": 1,
                "to_number": 100,
                "start_lat": 40.75,
                "start_lon": -73.98,
                "end_lat": 40.76,
                "end_lon": -73.99,
            }
        ]
        osm_sample = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-73.98, 40.75]},
                "properties": {"addr:housenumber": "11", "addr:street": "Time Sq"},
            }
        ]

        engine = build_spatial_database(
            output_db_path=out_db,
            openaddresses_data=oa_sample,
            tiger_segments=tiger_sample,
            osm_features=osm_sample,
        )
        assert engine.count() >= 7  # 5 seeded + 1 OA + 1 OSM
        engine.close()
