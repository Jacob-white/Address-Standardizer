"""
Offline Rooftop Reference Index & Coordinate Resolver.
======================================================
Embedded SQLite reference database capable of resolving rooftop / point-level
coordinates and parcel validation without external network calls, featuring
thread-safe zero-downtime atomic hot-swapping.
"""

import json
import os
import re
import sqlite3
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class RooftopRecord:
    """Rooftop / point-level reference delivery point."""
    address_key: str
    building_key: str
    street1: str
    street2: str
    city: str
    state: str
    postal_code: str
    country: str
    latitude: float
    longitude: float
    precision: str = "ROOFTOP"
    accuracy_radius_meters: float = 5.0
    parcel_id: Optional[str] = None
    is_multi_unit: bool = False
    known_units: List[str] = field(default_factory=list)
    rdi: str = "Unknown"
    is_cmra: bool = False
    is_vacant: bool = False
    census_tract: Optional[str] = None
    fips_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "address_key": self.address_key,
            "building_key": self.building_key,
            "street1": self.street1,
            "street2": self.street2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "precision": self.precision,
            "accuracy_radius_meters": self.accuracy_radius_meters,
            "parcel_id": self.parcel_id,
            "is_multi_unit": self.is_multi_unit,
            "known_units": list(self.known_units),
            "rdi": self.rdi,
            "is_cmra": self.is_cmra,
            "is_vacant": self.is_vacant,
            "census_tract": self.census_tract,
            "fips_code": self.fips_code,
            "metadata": dict(self.metadata),
        }


@dataclass
class ParcelValidationResult:
    """Offline parcel verification outcome."""
    is_valid_parcel: bool
    parcel_id: Optional[str] = None
    is_multi_unit: bool = False
    matched_rooftop: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_radius_meters: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "is_valid_parcel": self.is_valid_parcel,
            "parcel_id": self.parcel_id,
            "is_multi_unit": self.is_multi_unit,
            "matched_rooftop": self.matched_rooftop,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy_radius_meters": self.accuracy_radius_meters,
        }


SEED_ROOFTOP_RECORDS: List[Dict[str, Any]] = [
    {
        "address_key": "100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
        "building_key": "100 WALL ST||NEW YORK|NY|10005|USA",
        "street1": "100 WALL ST",
        "street2": "STE 400",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10005",
        "country": "USA",
        "latitude": 40.7061,
        "longitude": -74.0060,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "NY-MAN-00100",
        "is_multi_unit": True,
        "known_units": ["STE 400", "STE 800"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "000900",
        "fips_code": "36061",
    },
    {
        "address_key": "200 PARK AVE|STE 1200|NEW YORK|NY|10166|USA",
        "building_key": "200 PARK AVE||NEW YORK|NY|10166|USA",
        "street1": "200 PARK AVE",
        "street2": "STE 1200",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10166",
        "country": "USA",
        "latitude": 40.7535,
        "longitude": -73.9768,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 4.0,
        "parcel_id": "NY-MAN-00200",
        "is_multi_unit": True,
        "known_units": ["STE 1200"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "009200",
        "fips_code": "36061",
    },
    {
        "address_key": "1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
        "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
        "street1": "1209 N ORANGE ST",
        "street2": "STE 400",
        "city": "WILMINGTON",
        "state": "DE",
        "postal_code": "19801",
        "country": "USA",
        "latitude": 39.7478,
        "longitude": -75.5492,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 2.0,
        "parcel_id": "DE-NCC-26027",
        "is_multi_unit": True,
        "known_units": ["STE 400", "STE 600"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "002100",
        "fips_code": "10003",
    },
    {
        "address_key": "30 N GOULD ST|STE R|SHERIDAN|WY|82801|USA",
        "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
        "street1": "30 N GOULD ST",
        "street2": "STE R",
        "city": "SHERIDAN",
        "state": "WY",
        "postal_code": "82801",
        "country": "USA",
        "latitude": 44.7972,
        "longitude": -106.9562,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 2.5,
        "parcel_id": "WY-SHR-08280",
        "is_multi_unit": True,
        "known_units": ["STE R"],
        "rdi": "Commercial",
        "is_cmra": True,
        "is_vacant": False,
        "census_tract": "000100",
        "fips_code": "56033",
    },
    {
        "address_key": "500 N MICHIGAN AVE|STE 1400|CHICAGO|IL|60611|USA",
        "building_key": "500 N MICHIGAN AVE||CHICAGO|IL|60611|USA",
        "street1": "500 N MICHIGAN AVE",
        "street2": "STE 1400",
        "city": "CHICAGO",
        "state": "IL",
        "postal_code": "60611",
        "country": "USA",
        "latitude": 41.8919,
        "longitude": -87.6243,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "IL-COOK-17101",
        "is_multi_unit": True,
        "known_units": ["STE 1400"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "081403",
        "fips_code": "17031",
    },
    {
        "address_key": "1450 BRICKELL AVE|STE 1900|MIAMI|FL|33131|USA",
        "building_key": "1450 BRICKELL AVE||MIAMI|FL|33131|USA",
        "street1": "1450 BRICKELL AVE",
        "street2": "STE 1900",
        "city": "MIAMI",
        "state": "FL",
        "postal_code": "33131",
        "country": "USA",
        "latitude": 25.7592,
        "longitude": -80.1915,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "FL-MIA-01450",
        "is_multi_unit": True,
        "known_units": ["FL 15", "FL 17", "STE 1480", "STE 1650", "STE 1710", "STE 1900", "STE 2610", "STE 2900", "STE 3100"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "006702",
        "fips_code": "12086",
    },
    {
        "address_key": "555 CALIFORNIA ST|STE 3450|SAN FRANCISCO|CA|94104|USA",
        "building_key": "555 CALIFORNIA ST||SAN FRANCISCO|CA|94104|USA",
        "street1": "555 CALIFORNIA ST",
        "street2": "STE 3450",
        "city": "SAN FRANCISCO",
        "state": "CA",
        "postal_code": "94104",
        "country": "USA",
        "latitude": 37.7925,
        "longitude": -122.4038,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "CA-SFO-00555",
        "is_multi_unit": True,
        "known_units": ["27TH FLOOR", "40TH FLOOR", "50TH FLOOR", "FL 40", "STE 1400", "STE 2352", "STE 3100", "STE 3450"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "061100",
        "fips_code": "06075",
    },
    {
        "address_key": "40 WALL ST|STE 2816|NEW YORK|NY|10005|USA",
        "building_key": "40 WALL ST||NEW YORK|NY|10005|USA",
        "street1": "40 WALL ST",
        "street2": "STE 2816",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10005",
        "country": "USA",
        "latitude": 40.7064,
        "longitude": -74.0092,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "NY-MAN-00040",
        "is_multi_unit": True,
        "known_units": ["17TH FL", "28TH FLOOR", "FL 28", "STE 1606", "STE 1702", "STE 21-05", "STE 2816", "STE 2910", "STE 3004"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "000900",
        "fips_code": "36061",
    },
    {
        "address_key": "111 S WACKER DR|STE 2400|CHICAGO|IL|60606|USA",
        "building_key": "111 S WACKER DR||CHICAGO|IL|60606|USA",
        "street1": "111 S WACKER DR",
        "street2": "STE 2400",
        "city": "CHICAGO",
        "state": "IL",
        "postal_code": "60606",
        "country": "USA",
        "latitude": 41.8804,
        "longitude": -87.6366,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "IL-COOK-00111",
        "is_multi_unit": True,
        "known_units": ["FL 49", "STE 2400", "STE 3200", "STE 3400", "STE 4600"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "839100",
        "fips_code": "17031",
    },
    {
        "address_key": "227 W MONROE ST|STE 2400|CHICAGO|IL|60606|USA",
        "building_key": "227 W MONROE ST||CHICAGO|IL|60606|USA",
        "street1": "227 W MONROE ST",
        "street2": "STE 2400",
        "city": "CHICAGO",
        "state": "IL",
        "postal_code": "60606",
        "country": "USA",
        "latitude": 41.8828,
        "longitude": -87.6367,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "IL-COOK-00227",
        "is_multi_unit": True,
        "known_units": ["FL 10", "STE 18TH FL", "STE 21ST FL", "STE 24", "STE 2400", "STE 25TH FL"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "839100",
        "fips_code": "17031",
    },
    {
        "address_key": "520 MADISON AVE|FL 12|NEW YORK|NY|10022|USA",
        "building_key": "520 MADISON AVE||NEW YORK|NY|10022|USA",
        "street1": "520 MADISON AVE",
        "street2": "FL 12",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10022",
        "country": "USA",
        "latitude": 40.7601,
        "longitude": -73.9741,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "NY-MAN-00520",
        "is_multi_unit": True,
        "known_units": ["12TH FLOOR", "19TH FLOOR", "21ST FLOOR", "33RD FLOOR", "34TH FLOOR", "35TH FLOOR", "STE 2401"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "010200",
        "fips_code": "36061",
    },
    {
        "address_key": "590 MADISON AVE|FL 25|NEW YORK|NY|10022|USA",
        "building_key": "590 MADISON AVE||NEW YORK|NY|10022|USA",
        "street1": "590 MADISON AVE",
        "street2": "FL 25",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10022",
        "country": "USA",
        "latitude": 40.7616,
        "longitude": -73.9721,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "NY-MAN-00590",
        "is_multi_unit": True,
        "known_units": ["25TH FLOOR", "26TH FLOOR", "27TH FLOOR", "28TH FLOOR", "29TH FLOOR", "30TH FLOOR", "32ND FLOOR"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "010200",
        "fips_code": "36061",
    },
    {
        "address_key": "1330 AVE OF THE AMERICAS|FL 11|NEW YORK|NY|10019|USA",
        "building_key": "1330 AVE OF THE AMERICAS||NEW YORK|NY|10019|USA",
        "street1": "1330 AVE OF THE AMERICAS",
        "street2": "FL 11",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10019",
        "country": "USA",
        "latitude": 40.7630,
        "longitude": -73.9805,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "NY-MAN-01330",
        "is_multi_unit": True,
        "known_units": ["11TH FLOOR", "14TH FLOOR", "23RD FLOOR", "26TH FLOOR", "28TH FLOOR", "34TH FLOOR", "STE 24B"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "013100",
        "fips_code": "36061",
    },
    {
        "address_key": "ONE EMBARCADERO CENTER|FL 16|SAN FRANCISCO|CA|94111|USA",
        "building_key": "ONE EMBARCADERO CENTER||SAN FRANCISCO|CA|94111|USA",
        "street1": "ONE EMBARCADERO CENTER",
        "street2": "FL 16",
        "city": "SAN FRANCISCO",
        "state": "CA",
        "postal_code": "94111",
        "country": "USA",
        "latitude": 37.7904,
        "longitude": -122.3911,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "CA-SFO-00001",
        "is_multi_unit": True,
        "known_units": ["16TH FLOOR", "39TH FLOOR", "STE 1520", "STE 2530", "STE 37TH FL"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "061500",
        "fips_code": "06075",
    },
    {
        "address_key": "100 WILSHIRE BLVD|STE 1000|SANTA MONICA|CA|90401|USA",
        "building_key": "100 WILSHIRE BLVD||SANTA MONICA|CA|90401|USA",
        "street1": "100 WILSHIRE BLVD",
        "street2": "STE 1000",
        "city": "SANTA MONICA",
        "state": "CA",
        "postal_code": "90401",
        "country": "USA",
        "latitude": 34.1904,
        "longitude": -118.5926,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "CA-LAX-00100",
        "is_multi_unit": True,
        "known_units": ["STE 1000", "STE 1230", "STE 1500", "STE 1700", "STE 1830", "STE 500"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "701100",
        "fips_code": "06037",
    },
    {
        "address_key": "ONE WORLD TRADE CENTER|STE 8500|NEW YORK|NY|10007|USA",
        "building_key": "ONE WORLD TRADE CENTER||NEW YORK|NY|10007|USA",
        "street1": "ONE WORLD TRADE CENTER",
        "street2": "STE 8500",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10007",
        "country": "USA",
        "latitude": 40.7127,
        "longitude": -74.0134,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "NY-MAN-00001",
        "is_multi_unit": True,
        "known_units": ["85TH FLOOR", "FLOOR 84", "STE 47M", "STE 8500", "SUITE 46D", "SUITE 49P", "SUITE 83G"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "002100",
        "fips_code": "36061",
    },
    {
        "address_key": "1111 BRICKELL AVE|STE 1500|MIAMI|FL|33131|USA",
        "building_key": "1111 BRICKELL AVE||MIAMI|FL|33131|USA",
        "street1": "1111 BRICKELL AVE",
        "street2": "STE 1500",
        "city": "MIAMI",
        "state": "FL",
        "postal_code": "33131",
        "country": "USA",
        "latitude": 25.7624,
        "longitude": -80.1912,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "FL-MIA-01111",
        "is_multi_unit": True,
        "known_units": ["10TH FLOOR", "FL 10", "FL 11", "STE 1500", "STE 1820", "STE 2025", "STE 2725", "STE 2825", "SUITE 1000"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "006702",
        "fips_code": "12086",
    },
    {
        "address_key": "110 N WACKER DR|STE 2500|CHICAGO|IL|60606|USA",
        "building_key": "110 N WACKER DR||CHICAGO|IL|60606|USA",
        "street1": "110 N WACKER DR",
        "street2": "STE 2500",
        "city": "CHICAGO",
        "state": "IL",
        "postal_code": "60606",
        "country": "USA",
        "latitude": 41.8833,
        "longitude": -87.6373,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "IL-COOK-00110",
        "is_multi_unit": True,
        "known_units": ["STE 2500", "STE 2700", "STE 3125", "STE 3350", "STE 3750", "STE 4000", "STE 4525", "STE 54TH FL"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "839100",
        "fips_code": "17031",
    },
    {
        "address_key": "777 BRICKELL AVE|STE 500|MIAMI|FL|33131|USA",
        "building_key": "777 BRICKELL AVE||MIAMI|FL|33131|USA",
        "street1": "777 BRICKELL AVE",
        "street2": "STE 500",
        "city": "MIAMI",
        "state": "FL",
        "postal_code": "33131",
        "country": "USA",
        "latitude": 25.7658,
        "longitude": -80.1906,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "FL-MIA-00777",
        "is_multi_unit": True,
        "known_units": ["5TH FLOOR", "FL 9", "STE 10TH", "STE 1201", "STE 1360", "STE 500", "STE 530", "STE 708"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "006702",
        "fips_code": "12086",
    },
    {
        "address_key": "11111 SANTA MONICA BLVD|STE 1100|LOS ANGELES|CA|90025|USA",
        "building_key": "11111 SANTA MONICA BLVD||LOS ANGELES|CA|90025|USA",
        "street1": "11111 SANTA MONICA BLVD",
        "street2": "STE 1100",
        "city": "LOS ANGELES",
        "state": "CA",
        "postal_code": "90025",
        "country": "USA",
        "latitude": 34.0456,
        "longitude": -118.4485,
        "precision": "ROOFTOP",
        "accuracy_radius_meters": 3.0,
        "parcel_id": "CA-LAX-11111",
        "is_multi_unit": True,
        "known_units": ["STE 1100", "STE 1550", "STE 1650", "STE 2170", "STE 2200", "STE 2250", "STE 910", "SUITE 1250", "SUITE 2100"],
        "rdi": "Commercial",
        "is_cmra": False,
        "is_vacant": False,
        "census_tract": "267200",
        "fips_code": "06037",
    },
]

SEED_STREET_RANGES: List[Dict[str, Any]] = [
    {
        "street_name": "MAIN ST",
        "postal_code": "10001",
        "state": "NY",
        "from_number": 100,
        "to_number": 200,
        "start_latitude": 40.7480,
        "start_longitude": -73.9850,
        "end_latitude": 40.7500,
        "end_longitude": -73.9830,
        "census_tract": "010100",
        "fips_code": "36061",
    },
    {
        "street_name": "MARKET ST",
        "postal_code": "94105",
        "state": "CA",
        "from_number": 100,
        "to_number": 500,
        "start_latitude": 37.7900,
        "start_longitude": -122.4000,
        "end_latitude": 37.7950,
        "end_longitude": -122.3950,
        "census_tract": "0607501",
        "fips_code": "06075",
    },
    {
        "street_name": "PENNSYLVANIA AVE",
        "postal_code": "20500",
        "state": "DC",
        "from_number": 1500,
        "to_number": 1700,
        "start_latitude": 38.8970,
        "start_longitude": -77.0370,
        "end_latitude": 38.8990,
        "end_longitude": -77.0350,
        "census_tract": "006202",
        "fips_code": "11001",
    },
    {
        "street_name": "BROADWAY",
        "postal_code": "10007",
        "state": "NY",
        "from_number": 100,
        "to_number": 300,
        "start_latitude": 40.7120,
        "start_longitude": -74.0070,
        "end_latitude": 40.7140,
        "end_longitude": -74.0050,
        "census_tract": "002900",
        "fips_code": "36061",
    },
    {
        "street_name": "ELM ST",
        "postal_code": "75201",
        "state": "TX",
        "from_number": 1000,
        "to_number": 2000,
        "start_latitude": 32.7800,
        "start_longitude": -96.8000,
        "end_latitude": 32.7850,
        "end_longitude": -96.7900,
        "census_tract": "001900",
        "fips_code": "48113",
    },
    {
        "street_name": "PEACHTREE ST",
        "postal_code": "30303",
        "state": "GA",
        "from_number": 100,
        "to_number": 400,
        "start_latitude": 33.7550,
        "start_longitude": -84.3900,
        "end_latitude": 33.7600,
        "end_longitude": -84.3870,
        "census_tract": "002700",
        "fips_code": "13121",
    },
]


class OfflineReferenceIndex:
    """
    Embedded SQLite reference index supporting rooftop coordinates resolution,
    parcel validation, linear street edge interpolation, and zero-downtime hot-swapping.
    """

    def __init__(self, db_path: Optional[str] = None, seed: bool = True):
        self._db_path = db_path or ":memory:"
        self._seed = seed
        self._pid = os.getpid()
        self._lock = threading.RLock()
        self._real_conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._real_conn.row_factory = sqlite3.Row
        self._init_schema(self._real_conn)

        if seed and self.count() == 0:
            self.insert_records(SEED_ROOFTOP_RECORDS)
        if seed and self.count_ranges() == 0:
            self.insert_street_ranges(SEED_STREET_RANGES)

    @property
    def _conn(self) -> sqlite3.Connection:
        current_pid = os.getpid()
        if current_pid != self._pid:
            with self._lock:
                if current_pid != self._pid:
                    self._pid = current_pid
                    self._real_conn = sqlite3.connect(self._db_path, check_same_thread=False)
                    self._real_conn.row_factory = sqlite3.Row
                    self._init_schema(self._real_conn)
                    if self._seed and self.count() == 0:
                        self.insert_records(SEED_ROOFTOP_RECORDS)
                    if self._seed and self.count_ranges() == 0:
                        self.insert_street_ranges(SEED_STREET_RANGES)
        return self._real_conn

    @_conn.setter
    def _conn(self, val: Optional[sqlite3.Connection]):
        self._real_conn = val

    def _get_conn(self) -> sqlite3.Connection:
        return self._conn

    def _init_schema(self, conn: sqlite3.Connection):
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rooftop_reference (
                    address_key TEXT PRIMARY KEY,
                    building_key TEXT NOT NULL,
                    street1 TEXT NOT NULL,
                    street2 TEXT,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    postal_code TEXT NOT NULL,
                    country TEXT NOT NULL DEFAULT 'USA',
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    precision TEXT NOT NULL DEFAULT 'ROOFTOP',
                    accuracy_radius_meters REAL NOT NULL DEFAULT 5.0,
                    parcel_id TEXT,
                    is_multi_unit INTEGER NOT NULL DEFAULT 0,
                    known_units TEXT,
                    rdi TEXT DEFAULT 'Unknown',
                    is_cmra INTEGER NOT NULL DEFAULT 0,
                    is_vacant INTEGER NOT NULL DEFAULT 0,
                    census_tract TEXT,
                    fips_code TEXT,
                    metadata_json TEXT
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rooftop_building ON rooftop_reference(building_key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rooftop_zip_st ON rooftop_reference(postal_code, street1);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rooftop_parcel ON rooftop_reference(parcel_id);")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS street_ranges (
                    range_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    street_name TEXT NOT NULL,
                    postal_code TEXT NOT NULL,
                    state TEXT NOT NULL,
                    from_number INTEGER NOT NULL,
                    to_number INTEGER NOT NULL,
                    start_latitude REAL NOT NULL,
                    start_longitude REAL NOT NULL,
                    end_latitude REAL NOT NULL,
                    end_longitude REAL NOT NULL,
                    census_tract TEXT,
                    fips_code TEXT
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ranges_zip_st ON street_ranges(postal_code, street_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ranges_state_st ON street_ranges(state, street_name);")

            if self._db_path != ":memory:":
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")

    def insert_record(
        self,
        address_key: str,
        building_key: str,
        street1: str,
        city: str,
        state: str,
        postal_code: str,
        latitude: float,
        longitude: float,
        street2: str = "",
        country: str = "USA",
        precision: str = "ROOFTOP",
        accuracy_radius_meters: float = 5.0,
        parcel_id: Optional[str] = None,
        is_multi_unit: bool = False,
        known_units: Optional[List[str]] = None,
        rdi: str = "Unknown",
        is_cmra: bool = False,
        is_vacant: bool = False,
        census_tract: Optional[str] = None,
        fips_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Inserts or replaces a rooftop reference record."""
        with self._lock:
            conn = self._get_conn()
            with conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO rooftop_reference (
                        address_key, building_key, street1, street2, city, state, postal_code,
                        country, latitude, longitude, precision, accuracy_radius_meters,
                        parcel_id, is_multi_unit, known_units, rdi, is_cmra, is_vacant,
                        census_tract, fips_code, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        address_key.strip().upper(),
                        building_key.strip().upper(),
                        street1.strip().upper(),
                        street2.strip().upper(),
                        city.strip().upper(),
                        state.strip().upper(),
                        postal_code.strip(),
                        country.strip().upper(),
                        latitude,
                        longitude,
                        precision,
                        accuracy_radius_meters,
                        parcel_id,
                        1 if is_multi_unit else 0,
                        json.dumps(known_units or []),
                        rdi,
                        1 if is_cmra else 0,
                        1 if is_vacant else 0,
                        census_tract,
                        fips_code,
                        json.dumps(metadata or {}),
                    ),
                )

    def insert_records(self, records: List[Dict[str, Any]]):
        """Batch insert rooftop reference records."""
        for rec in records:
            self.insert_record(**rec)

    def insert_street_range(
        self,
        street_name: str,
        postal_code: str,
        state: str,
        from_number: int,
        to_number: int,
        start_latitude: float,
        start_longitude: float,
        end_latitude: float,
        end_longitude: float,
        census_tract: Optional[str] = None,
        fips_code: Optional[str] = None,
    ):
        """Inserts a street edge range for linear interpolation (Census TIGER style)."""
        with self._lock:
            conn = self._get_conn()
            with conn:
                conn.execute(
                    """
                    INSERT INTO street_ranges (
                        street_name, postal_code, state, from_number, to_number,
                        start_latitude, start_longitude, end_latitude, end_longitude,
                        census_tract, fips_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        street_name.strip().upper(),
                        postal_code.strip(),
                        state.strip().upper(),
                        int(from_number),
                        int(to_number),
                        float(start_latitude),
                        float(start_longitude),
                        float(end_latitude),
                        float(end_longitude),
                        census_tract,
                        fips_code,
                    ),
                )

    def insert_street_ranges(self, ranges: List[Dict[str, Any]]):
        """Batch insert street edge ranges."""
        for r in ranges:
            self.insert_street_range(**r)

    def count_ranges(self) -> int:
        """Returns total records in the street_ranges table."""
        with self._lock:
            cur = self._get_conn().execute("SELECT count(*) FROM street_ranges")
            row = cur.fetchone()
            return row[0] if row else 0

    def interpolate_street_range(
        self,
        street_number: int,
        street_name: str,
        postal_code: str = "",
        state: str = "",
    ) -> Optional[RooftopRecord]:
        """
        Linearly interpolates coordinates along street edge segments (US Census TIGER style).
        Zero external API calls.
        """
        clean_st = street_name.strip().upper()
        zip5 = postal_code[:5] if postal_code else ""
        norm_st = state.strip().upper()

        with self._lock:
            query = """
                SELECT * FROM street_ranges
                WHERE (street_name = ? OR street_name LIKE ? OR ? LIKE street_name || '%')
            """
            params: List[Any] = [clean_st, f"{clean_st}%", clean_st]
            if zip5:
                query += " AND postal_code LIKE ?"
                params.append(f"{zip5}%")
            elif norm_st:
                query += " AND state = ?"
                params.append(norm_st)

            cur = self._get_conn().execute(query, tuple(params))
            rows = cur.fetchall()
            for row in rows:
                from_num = int(row["from_number"])
                to_num = int(row["to_number"])
                min_n = min(from_num, to_num)
                max_n = max(from_num, to_num)
                if min_n <= street_number <= max_n:
                    if max_n == min_n:
                        t = 0.5
                    else:
                        t = (street_number - from_num) / (to_num - from_num)
                        t = max(0.0, min(1.0, t))

                    start_lat = float(row["start_latitude"])
                    end_lat = float(row["end_latitude"])
                    start_lon = float(row["start_longitude"])
                    end_lon = float(row["end_longitude"])

                    lat = start_lat + t * (end_lat - start_lat)
                    lon = start_lon + t * (end_lon - start_lon)

                    c_tract = row["census_tract"]
                    f_code = row["fips_code"]
                    r_post = row["postal_code"]
                    r_st = row["state"]

                    return RooftopRecord(
                        address_key=f"{street_number} {clean_st}||{r_st}|{r_post}|USA",
                        building_key=f"{street_number} {clean_st}||{r_st}|{r_post}|USA",
                        street1=f"{street_number} {clean_st}",
                        street2="",
                        city="",
                        state=r_st,
                        postal_code=r_post,
                        country="USA",
                        latitude=round(lat, 6),
                        longitude=round(lon, 6),
                        precision="RANGE_INTERPOLATED",
                        accuracy_radius_meters=15.0,
                        census_tract=c_tract,
                        fips_code=f_code,
                    )
        return None

    def _row_to_record(self, row: sqlite3.Row) -> RooftopRecord:
        known_u = []
        if row["known_units"]:
            try:
                known_u = json.loads(row["known_units"])
            except Exception:
                known_u = []

        meta = {}
        if row["metadata_json"]:
            try:
                meta = json.loads(row["metadata_json"])
            except Exception:
                meta = {}

        c_tract = row["census_tract"] if "census_tract" in row.keys() else None
        f_code = row["fips_code"] if "fips_code" in row.keys() else None
        if not c_tract and meta.get("census_tract"):
            c_tract = str(meta["census_tract"])
        if not f_code and meta.get("fips_code"):
            f_code = str(meta["fips_code"])

        return RooftopRecord(
            address_key=row["address_key"],
            building_key=row["building_key"],
            street1=row["street1"],
            street2=row["street2"] or "",
            city=row["city"],
            state=row["state"],
            postal_code=row["postal_code"],
            country=row["country"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            precision=row["precision"],
            accuracy_radius_meters=float(row["accuracy_radius_meters"]),
            parcel_id=row["parcel_id"],
            is_multi_unit=bool(row["is_multi_unit"]),
            known_units=known_u,
            rdi=row["rdi"] or "Unknown",
            is_cmra=bool(row["is_cmra"]),
            is_vacant=bool(row["is_vacant"]),
            census_tract=c_tract,
            fips_code=f_code,
            metadata=meta,
        )

    def resolve_coordinates(self, address: Any) -> Optional[RooftopRecord]:
        """
        Resolves rooftop point coordinates for a StandardizedAddress or key.
        Checks normalized_address_key, building_key, (postal_code, street1),
        street number transposition healing, and parcel_id.
        """
        with self._lock:
            conn = self._get_conn()
            # 1. Try normalized_address_key
            norm_key = getattr(address, "normalized_address_key", None)
            if isinstance(address, str):
                norm_key = address

            if norm_key:
                cur = conn.execute(
                    "SELECT * FROM rooftop_reference WHERE address_key = ? OR building_key = ? LIMIT 1",
                    (norm_key.strip().upper(), norm_key.strip().upper()),
                )
                row = cur.fetchone()
                if row:
                    return self._row_to_record(row)

            # 2. Try building_key
            b_key = getattr(address, "building_key", None)
            if b_key:
                cur = conn.execute(
                    "SELECT * FROM rooftop_reference WHERE building_key = ? LIMIT 1",
                    (b_key.strip().upper(),),
                )
                row = cur.fetchone()
                if row:
                    return self._row_to_record(row)

            # 3. Try (postal_code, street1)
            st1 = getattr(address, "street1", None)
            post = getattr(address, "postal_code", None)
            if st1 and post:
                zip5 = post[:5]
                cur = conn.execute(
                    "SELECT * FROM rooftop_reference WHERE postal_code LIKE ? AND street1 = ? LIMIT 1",
                    (f"{zip5}%", st1.strip().upper()),
                )
                row = cur.fetchone()
                if row:
                    return self._row_to_record(row)

                # 4. Street number transposition healing against reference index
                st_tokens = st1.split()
                if st_tokens and any(c.isdigit() for c in st_tokens[0]):
                    num_part = st_tokens[0]
                    rest_part = " ".join(st_tokens[1:])
                    cur = conn.execute(
                        "SELECT street1 FROM rooftop_reference WHERE postal_code LIKE ? AND street1 LIKE ?",
                        (f"{zip5}%", f"%{rest_part}"),
                    )
                    rows = cur.fetchall()
                    known_nums = []
                    for r in rows:
                        r_tokens = r["street1"].split()
                        if r_tokens and r_tokens[0].isdigit():
                            known_nums.append(int(r_tokens[0]))
                    if known_nums:
                        from address_standardizer.fuzzy import heal_street_number_transposition
                        ranges = [(n, n) for n in known_nums]
                        healed_num = heal_street_number_transposition(num_part, valid_ranges=ranges)
                        if healed_num and healed_num != num_part:
                            healed_st1 = f"{healed_num} {rest_part}".strip().upper()
                            cur = conn.execute(
                                "SELECT * FROM rooftop_reference WHERE postal_code LIKE ? AND street1 = ? LIMIT 1",
                                (f"{zip5}%", healed_st1),
                            )
                            row = cur.fetchone()
                            if row:
                                return self._row_to_record(row)

            # 5. Try parcel_id or plain string address parsing
            if isinstance(address, str) and norm_key:
                cur = conn.execute(
                    "SELECT * FROM rooftop_reference WHERE parcel_id = ? LIMIT 1",
                    (norm_key.strip().upper(),),
                )
                row = cur.fetchone()
                if row:
                    return self._row_to_record(row)

                if "|" not in address:
                    from address_standardizer.standardizer import standardize_address
                    std = standardize_address(address)
                    rec = self.resolve_coordinates(std)
                    if rec:
                        return rec
            # 6. Try street edge range interpolation (US Census TIGER style)
            st1_val = getattr(address, "street1", None)
            post_val = getattr(address, "postal_code", None)
            state_val = getattr(address, "state", None)
            if isinstance(address, str) and not st1_val:
                parts = [p.strip() for p in address.split(",") if p.strip()]
                if parts:
                    st1_val = parts[0]
            if st1_val:
                m_num = re.match(r"^(\d+)\s+(.+)$", str(st1_val).strip().upper())
                if m_num:
                    st_num = int(m_num.group(1))
                    st_name = m_num.group(2).strip()
                    interp_rec = self.interpolate_street_range(
                        street_number=st_num,
                        street_name=st_name,
                        postal_code=str(post_val) if post_val else "",
                        state=str(state_val) if state_val else "",
                    )
                    if interp_rec:
                        return interp_rec

            return None

    def geocode(self, address: Any, fallback_to_centroids: bool = True) -> Dict[str, Any]:
        """
        Pure offline rooftop geocoding (zero external network calls):
        1. Exact point rooftop match (OpenAddresses / Reference)
        2. TIGER street edge range linear interpolation
        3. Regional ZIP / state centroid fallback
        """
        if isinstance(address, str) and "|" not in address:
            from address_standardizer.standardizer import standardize_address
            address = standardize_address(address)

        rec = self.resolve_coordinates(address)
        if rec is not None:
            return {
                "latitude": rec.latitude,
                "longitude": rec.longitude,
                "precision": rec.precision,
                "accuracy_radius_meters": rec.accuracy_radius_meters,
                "census_tract": rec.census_tract,
                "fips_code": rec.fips_code,
            }
        is_us_target = getattr(address, "is_us", False)
        if not is_us_target and isinstance(address, str) and "|" in address:
            parts = address.split("|")
            c_code = parts[5].strip().upper() if len(parts) >= 6 else "USA"
            is_us_target = c_code in ("", "US", "USA", "UNITED STATES")

        if fallback_to_centroids and is_us_target:
            from address_standardizer.geocoder import get_fallback_centroid
            from address_standardizer.tables import STATE_TO_FIPS, US_STATES, ZIP3_TO_STATE
            post = getattr(address, "postal_code", None)
            st = getattr(address, "state", None)
            if isinstance(address, str):
                m_zip = re.search(r"\b(\d{5})\b", address)
                if m_zip:
                    post = m_zip.group(1)
            if not st and post and len(post) >= 3:
                st = ZIP3_TO_STATE.get(post[:3])
            coords = get_fallback_centroid(zip5=post, state=st)
            if coords:
                norm_st = US_STATES.get(str(st).upper(), str(st).upper()) if st else None
                fips = STATE_TO_FIPS.get(norm_st) if norm_st else None
                return {
                    "latitude": coords[0],
                    "longitude": coords[1],
                    "precision": "POSTAL_CENTROID" if post else "LOCALITY",
                    "accuracy_radius_meters": 5000.0,
                    "census_tract": None,
                    "fips_code": fips,
                }
        return {
            "latitude": None,
            "longitude": None,
            "precision": "UNRESOLVED",
            "accuracy_radius_meters": None,
            "census_tract": None,
            "fips_code": None,
        }

    def validate_parcel(self, address: Any) -> ParcelValidationResult:
        """
        Validates whether the address corresponds to a known physical parcel
        in the offline reference database.
        """
        if isinstance(address, str) and "|" not in address:
            with self._lock:
                cur = self._get_conn().execute(
                    "SELECT * FROM rooftop_reference WHERE parcel_id = ? LIMIT 1",
                    (address.strip().upper(),),
                )
                row = cur.fetchone()
                if row:
                    rec = self._row_to_record(row)
                    return ParcelValidationResult(
                        is_valid_parcel=True,
                        parcel_id=rec.parcel_id,
                        is_multi_unit=rec.is_multi_unit,
                        matched_rooftop=True,
                        latitude=rec.latitude,
                        longitude=rec.longitude,
                        accuracy_radius_meters=rec.accuracy_radius_meters,
                    )

        record = self.resolve_coordinates(address)
        if record is not None and record.parcel_id:
            return ParcelValidationResult(
                is_valid_parcel=True,
                parcel_id=record.parcel_id,
                is_multi_unit=record.is_multi_unit,
                matched_rooftop=True,
                latitude=record.latitude,
                longitude=record.longitude,
                accuracy_radius_meters=record.accuracy_radius_meters,
            )

        return ParcelValidationResult(
            is_valid_parcel=False,
            parcel_id=None,
            is_multi_unit=False,
            matched_rooftop=False,
            latitude=None,
            longitude=None,
            accuracy_radius_meters=None,
        )

    def hot_swap(self, new_db_path: str):
        """
        Performs a thread-safe, zero-downtime hot-swap to a newly loaded reference database.
        Verifies schema and integrity before swapping connections.
        """
        if not os.path.exists(new_db_path):
            raise FileNotFoundError(f"Hot-swap database file not found: {new_db_path}")

        # Connect and verify target database
        test_conn = sqlite3.connect(new_db_path, check_same_thread=False)
        test_conn.row_factory = sqlite3.Row
        try:
            cur = test_conn.execute("SELECT count(*) FROM rooftop_reference")
            cur.fetchone()
            if new_db_path != ":memory:":
                test_conn.execute("PRAGMA journal_mode=WAL;")
        except sqlite3.Error as e:
            test_conn.close()
            raise ValueError(f"Invalid reference database schema in {new_db_path}: {e}")

        # Atomic swap
        with self._lock:
            old_conn = self._conn
            self._conn = test_conn
            self._db_path = new_db_path
            old_conn.close()

    def count(self) -> int:
        """Returns total records in the reference table."""
        with self._lock:
            cur = self._get_conn().execute("SELECT count(*) FROM rooftop_reference")
            row = cur.fetchone()
            return row[0] if row else 0

    def close(self):
        """Closes internal database connection."""
        with self._lock:
            if self._conn:
                self._conn.close()


_DEFAULT_OFFLINE_INDEX: Optional[OfflineReferenceIndex] = None
_INDEX_LOCK = threading.Lock()


def get_default_offline_index() -> OfflineReferenceIndex:
    """Returns singleton instance of the offline rooftop reference index."""
    global _DEFAULT_OFFLINE_INDEX
    if _DEFAULT_OFFLINE_INDEX is None:
        with _INDEX_LOCK:
            if _DEFAULT_OFFLINE_INDEX is None:
                _DEFAULT_OFFLINE_INDEX = OfflineReferenceIndex(seed=True)
    return _DEFAULT_OFFLINE_INDEX


def resolve_offline_coordinates(address: Any) -> Optional[RooftopRecord]:
    """Public helper to resolve rooftop coordinates via the default offline index."""
    return get_default_offline_index().resolve_coordinates(address)


def validate_parcel_offline(address: Any) -> ParcelValidationResult:
    """Public helper to validate parcel status via the default offline index."""
    return get_default_offline_index().validate_parcel(address)


def geocode_offline(address: Any, fallback_to_centroids: bool = True) -> Dict[str, Any]:
    """Public helper to perform pure offline geocoding via the default offline index."""
    return get_default_offline_index().geocode(address, fallback_to_centroids=fallback_to_centroids)
