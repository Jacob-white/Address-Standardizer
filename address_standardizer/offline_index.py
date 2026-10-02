"""
Offline Rooftop Reference Index & Coordinate Resolver.
======================================================
Embedded SQLite reference database capable of resolving rooftop / point-level
coordinates and parcel validation without external network calls, featuring
thread-safe zero-downtime atomic hot-swapping.
"""

import json
import os
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
    },
]


class OfflineReferenceIndex:
    """
    Embedded SQLite reference index supporting rooftop coordinates resolution,
    parcel validation, and zero-downtime hot-swapping.
    """

    def __init__(self, db_path: Optional[str] = None, seed: bool = True):
        self._db_path = db_path or ":memory:"
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema(self._conn)

        if seed and self.count() == 0:
            self.insert_records(SEED_ROOFTOP_RECORDS)

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
                    metadata_json TEXT
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rooftop_building ON rooftop_reference(building_key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rooftop_zip_st ON rooftop_reference(postal_code, street1);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rooftop_parcel ON rooftop_reference(parcel_id);")
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
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Inserts or replaces a rooftop reference record."""
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO rooftop_reference (
                        address_key, building_key, street1, street2, city, state, postal_code,
                        country, latitude, longitude, precision, accuracy_radius_meters,
                        parcel_id, is_multi_unit, known_units, rdi, is_cmra, is_vacant, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        json.dumps(metadata or {}),
                    ),
                )

    def insert_records(self, records: List[Dict[str, Any]]):
        """Batch insert rooftop reference records."""
        for rec in records:
            self.insert_record(**rec)

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
            metadata=meta,
        )

    def resolve_coordinates(self, address: Any) -> Optional[RooftopRecord]:
        """
        Resolves rooftop point coordinates for a StandardizedAddress or key.
        Checks normalized_address_key, building_key, (postal_code, street1),
        street number transposition healing, and parcel_id.
        """
        with self._lock:
            # 1. Try normalized_address_key
            norm_key = getattr(address, "normalized_address_key", None)
            if isinstance(address, str):
                norm_key = address

            if norm_key:
                cur = self._conn.execute(
                    "SELECT * FROM rooftop_reference WHERE address_key = ?",
                    (norm_key.strip().upper(),),
                )
                row = cur.fetchone()
                if row:
                    return self._row_to_record(row)

            # 2. Try building_key
            b_key = getattr(address, "building_key", None)
            if b_key:
                cur = self._conn.execute(
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
                cur = self._conn.execute(
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
                    cur = self._conn.execute(
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
                            cur = self._conn.execute(
                                "SELECT * FROM rooftop_reference WHERE postal_code LIKE ? AND street1 = ? LIMIT 1",
                                (f"{zip5}%", healed_st1),
                            )
                            row = cur.fetchone()
                            if row:
                                return self._row_to_record(row)

            # 5. Try parcel_id or plain string address parsing
            if isinstance(address, str) and norm_key:
                cur = self._conn.execute(
                    "SELECT * FROM rooftop_reference WHERE parcel_id = ? LIMIT 1",
                    (norm_key.strip().upper(),),
                )
                row = cur.fetchone()
                if row:
                    return self._row_to_record(row)

                if "|" not in address:
                    from address_standardizer.standardizer import standardize_address
                    std = standardize_address(address)
                    if std.address_status != "parse_failed":
                        return self.resolve_coordinates(std)

            return None

    def validate_parcel(self, address: Any) -> ParcelValidationResult:
        """
        Validates whether the address corresponds to a known physical parcel
        in the offline reference database.
        """
        if isinstance(address, str) and "|" not in address:
            with self._lock:
                cur = self._conn.execute(
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
            cur = self._conn.execute("SELECT count(*) FROM rooftop_reference")
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
