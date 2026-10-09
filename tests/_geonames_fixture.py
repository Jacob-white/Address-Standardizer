"""Tiny GeoNames-format fixture data and helpers for the reference-layer tests (no network, no real dump)."""

import zipfile
from pathlib import Path

from address_standardizer.reference.geonames import build_geonames_index

HEADER = "country\tpostal\tplace\tadmin1\tadmin1_code\tadmin2\tadmin2_code\tadmin3\tadmin3_code\tlat\tlon\taccuracy"


def row(country, postal, place, admin1="", code1="", admin2="", code2="", lat="", lon="", acc="4"):
    return "\t".join([country, postal, place, admin1, code1, admin2, code2, "", "", lat, lon, acc])


US_ROWS = [
    row("US", "10005", "New York", "New York", "NY", "New York", "061", "40.7061", "-74.0088"),
    row("US", "11201", "Brooklyn", "New York", "NY", "Kings", "047", "40.6944", "-73.9906"),
    row("US", "62704", "Springfield", "Illinois", "IL", "Sangamon", "167", "39.7817", "-89.6501"),
    row("US", "63101", "Saint Louis", "Missouri", "MO", "Saint Louis (city)", "510", "38.6312", "-90.1922"),
    row("US", "97001", "Border Town", "Oregon", "OR", "Jefferson", "031", "44.0", "-121.0"),
    row("US", "97001", "Other Hamlet", "Washington", "WA", "Klickitat", "039", "45.0", "-120.9"),
    row("US", "90001", "Los Angeles", "California", "CA", "Los Angeles", "037"),  # no coordinates
    row("US", "90210", "Beverly Hills", "California", "CA", "Los Angeles", "037", "34.09", "-118.41"),
    row("US", "00501", "Odd Place"),  # no state data at all
]
CA_ROWS = [
    row("CA", "H2X", "Montreal", "Quebec", "QC", "", "", "45.5088", "-73.5878"),
    row("CA", "M5V", "Toronto", "Ontario", "ON", "", "", "43.6426", "-79.3871"),
]
GB_ROWS = [row("GB", "SW1A", "London", "England", "ENG", "Greater London", "GLA", "51.5014", "-0.1419")]
NL_ROWS = [row("NL", "1011", "Amsterdam", "Noord-Holland", "07", "Amsterdam", "0363", "52.37", "4.9")]
FR_ROWS = [row("FR", "75001", "Paris 01", "Ile-de-France", "11", "Paris", "75", "48.86", "2.34")]


def write_txt(path: Path, rows) -> Path:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="")
    return path


def write_zip(path: Path, rows, name: str, with_readme: bool = True) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(name, "\n".join(rows) + "\n")
        if with_readme:
            zf.writestr("readme.txt", "GeoNames readme, not data\n")
    return path


def make_source_dir(root: Path) -> Path:
    """A directory shaped like downloaded GeoNames files: a plain .txt, zips with readmes, and a stray file."""
    d = root / "geonames"
    d.mkdir()
    write_txt(d / "US.txt", US_ROWS)
    write_zip(d / "CA.zip", CA_ROWS, "CA.txt")
    write_zip(d / "GB.zip", GB_ROWS, "GB.txt")
    write_zip(d / "NL.zip", NL_ROWS, "sub/NL.txt")
    write_txt(d / "FR.txt", FR_ROWS)
    (d / "readme.txt").write_text("not data", encoding="utf-8")
    (d / "notes.md").write_text("ignored", encoding="utf-8")
    return d


def build_fixture_db(root: Path, name: str = "geonames.db") -> Path:
    db = root / name
    build_geonames_index(db, source=make_source_dir(root), as_of="2026-01-01")
    return db
