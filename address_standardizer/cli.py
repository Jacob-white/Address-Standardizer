"""
Command-Line Interface for Address Standardizer.
================================================
Provides a standalone CLI for single address parsing, batch CSV standardization,
and Census geocoding enrichment.
"""

import sys
import json
import csv
import argparse
from typing import List

from address_standardizer.standardizer import standardize_address
from address_standardizer.geocoder import CensusGeocoder


def main():
    # Direct shorthand invocation: address-standardizer "100 Wall St, New York, NY 10005"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in ("parse", "batch"):
        raw_addr = " ".join(sys.argv[1:])
        res = standardize_address(street1=raw_addr)
        print(json.dumps(res.as_dict(), indent=2))
        return

    parser = argparse.ArgumentParser(
        prog="address-standardizer",
        description="Standardize US and international addresses to USPS Pub 28 and ISO standards.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: parse single address
    parse_parser = subparsers.add_parser("parse", help="Parse and standardize a single address string")
    parse_parser.add_argument("address", nargs="*", help="Full address string (e.g. '100 Wall St, Ste 400, New York, NY 10005')")
    parse_parser.add_argument("--street1", help="Street address line 1")
    parse_parser.add_argument("--street2", help="Street address line 2 (Suite, Floor, Apt)")
    parse_parser.add_argument("--city", help="City name")
    parse_parser.add_argument("--state", help="State / province code or name")
    parse_parser.add_argument("--zip", dest="postal_code", help="Postal code or ZIP")
    parse_parser.add_argument("--country", default="USA", help="Country name or ISO code (default: USA)")
    parse_parser.add_argument("--geocode", action="store_true", help="Enrich with US Census geocoder coordinates")

    # Command: batch CSV processing
    batch_parser = subparsers.add_parser("batch", help="Batch standardize a CSV file")
    batch_parser.add_argument("input_csv", help="Path to input CSV file")
    batch_parser.add_argument("output_csv", help="Path to write standardized CSV output")
    batch_parser.add_argument("--street-col", default="street1", help="Column name for street (default: street1)")
    batch_parser.add_argument("--street2-col", default="street2", help="Column name for street line 2 (default: street2)")
    batch_parser.add_argument("--city-col", default="city", help="Column name for city (default: city)")
    batch_parser.add_argument("--state-col", default="state", help="Column name for state (default: state)")
    batch_parser.add_argument("--zip-col", default="postal_code", help="Column name for zip (default: postal_code)")
    batch_parser.add_argument("--country-col", default="country", help="Column name for country (default: country)")
    batch_parser.add_argument("--geocode", action="store_true", help="Batch geocode US addresses with Census API")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "parse":
        st1 = args.street1
        if not st1 and args.address:
            st1 = " ".join(args.address)
        res = standardize_address(
            street1=st1,
            street2=args.street2,
            city=args.city,
            state=args.state,
            postal_code=args.postal_code,
            country=args.country,
        )
        data = res.as_dict()
        if args.geocode and res.is_us and res.street1:
            geocoder = CensusGeocoder()
            geo_res = geocoder.geocode_batch([("1", res.street1, res.city, res.state, res.postal_code)])
            if "1" in geo_res:
                data["latitude"] = geo_res["1"]["latitude"]
                data["longitude"] = geo_res["1"]["longitude"]
                data["geocode_precision"] = geo_res["1"]["precision"]
        print(json.dumps(data, indent=2))

    elif args.command == "batch":
        with open(args.input_csv, "r", encoding="utf-8", errors="replace") as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = (reader.fieldnames or []) + [
                "std_street1", "std_street2", "std_city", "std_state", "std_postal_code",
                "std_country", "normalized_address_key", "building_key", "phonetic_key",
                "is_registered_agent_hub", "is_private_residence", "address_status"
            ]
            if args.geocode:
                fieldnames.extend(["latitude", "longitude", "geocode_precision"])

            rows: List[dict] = []
            for row in reader:
                st = standardize_address(
                    street1=row.get(args.street_col, ""),
                    street2=row.get(args.street2_col, ""),
                    city=row.get(args.city_col, ""),
                    state=row.get(args.state_col, ""),
                    postal_code=row.get(args.zip_col, ""),
                    country=row.get(args.country_col, "USA"),
                )
                row["std_street1"] = st.street1
                row["std_street2"] = st.street2
                row["std_city"] = st.city
                row["std_state"] = st.state
                row["std_postal_code"] = st.postal_code
                row["std_country"] = st.country
                row["normalized_address_key"] = st.normalized_address_key or ""
                row["building_key"] = st.building_key or ""
                row["phonetic_key"] = st.phonetic_key or ""
                row["is_registered_agent_hub"] = str(st.is_registered_agent_hub)
                row["is_private_residence"] = str(st.is_private_residence)
                row["address_status"] = st.address_status
                rows.append(row)

        if args.geocode:
            geocoder = CensusGeocoder()
            geo_batch = []
            for idx, r in enumerate(rows):
                if r.get("std_country") == "USA" and r.get("std_street1"):
                    geo_batch.append((str(idx), r["std_street1"], r["std_city"], r["std_state"], r["std_postal_code"]))
            
            geo_results = geocoder.geocode_batch(geo_batch)
            for idx, r in enumerate(rows):
                idx_str = str(idx)
                if idx_str in geo_results:
                    r["latitude"] = geo_results[idx_str]["latitude"]
                    r["longitude"] = geo_results[idx_str]["longitude"]
                    r["geocode_precision"] = geo_results[idx_str]["precision"]
                else:
                    r["latitude"] = ""
                    r["longitude"] = ""
                    r["geocode_precision"] = ""

        with open(args.output_csv, "w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Standardized {len(rows)} record(s) -> {args.output_csv}")


if __name__ == "__main__":
    main()
