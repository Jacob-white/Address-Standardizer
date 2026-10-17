"""
Download and compress GeoNames US postal code data into a compact package asset.
License: CC-BY-4.0
Source: https://download.geonames.org/export/zip/US.zip
"""

import gzip
import io
import os
import urllib.request
import zipfile
from pathlib import Path

DATA_URL = "https://download.geonames.org/export/zip/US.zip"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "address_standardizer" / "reference" / "data" / "us_zip5.tsv.gz"


def build():
    print(f"Downloading {DATA_URL}...")
    req = urllib.request.Request(DATA_URL, headers={"User-Agent": "address-standardizer"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read()

    zf = zipfile.ZipFile(io.BytesIO(content))
    raw_lines = zf.read("US.txt").decode("utf-8").splitlines()
    print(f"Processing {len(raw_lines)} records from GeoNames US.txt...")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with gzip.GzipFile(OUTPUT_PATH, mode="wb", compresslevel=9, mtime=0) as gz_out:
        for line in raw_lines:
            parts = line.split("\t")
            if len(parts) >= 11:
                # postal_code, place_name, admin1, admin1_code, admin2, latitude, longitude
                row = "\t".join([parts[1], parts[2], parts[3], parts[4], parts[5], parts[9], parts[10]]) + "\n"
                gz_out.write(row.encode("utf-8"))
                count += 1

    sz = os.path.getsize(OUTPUT_PATH)
    print(f"Wrote {count} records to {OUTPUT_PATH} ({sz} bytes, ~{round(sz / 1024)} KB)")


if __name__ == "__main__":
    build()
