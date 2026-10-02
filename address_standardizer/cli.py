"""
Command-Line Interface for Address Standardizer.
================================================
Provides a standalone CLI for single address parsing, batch CSV standardization,
Census geocoding enrichment, multi-tier verification cascade, audit ledger triage,
and reference cache management.
"""

import sys
import json
import argparse

from address_standardizer.standardizer import standardize_address
from address_standardizer.geocoder import CensusGeocoder
from address_standardizer.cascade import resolve_verification_cascade
from address_standardizer.batch import stream_standardize_csv
from address_standardizer.cache import (
    configure_cache,
    clear_cache,
    get_cache_stats,
)
from address_standardizer.audit import get_audit_ledger


def main():
    # Direct shorthand invocation: address-standardizer "100 Wall St, New York, NY 10005"
    if (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in ("parse", "batch", "audit", "cache", "autocomplete")
    ):
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
    parse_parser.add_argument("--cascade", action="store_true", help="Run 4-stage graceful verification cascade")
    parse_parser.add_argument("--confidence", action="store_true", help="Include composite confidence score and routing tier")
    parse_parser.add_argument("--audit", action="store_true", help="Include stewardship audit record details")
    parse_parser.add_argument("--no-cache", action="store_true", help="Bypass multi-tier reference cache")

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
    batch_parser.add_argument("--chunk-size", type=int, default=5000, help="Streaming chunk size (default: 5000)")
    batch_parser.add_argument("--workers", type=int, default=2, help="Multiprocessing workers, max 2 (default: 2)")
    batch_parser.add_argument("--geocode", action="store_true", help="Batch geocode US addresses with Census API")
    batch_parser.add_argument("--confidence", action="store_true", help="Include confidence_score and routing_tier columns")
    batch_parser.add_argument("--audit-csv", help="Path to write audit ledger records as CSV")
    batch_parser.add_argument("--no-cache", action="store_true", help="Disable caching during batch processing")

    # Command: audit ledger triage
    audit_parser = subparsers.add_parser("audit", help="Inspect and export stewardship audit ledger")
    audit_parser.add_argument("--list", action="store_true", help="List recent audit records")
    audit_parser.add_argument("--status", choices=["PENDING", "APPROVED", "MODIFIED", "REJECTED"], help="Filter by review status")
    audit_parser.add_argument("--export", choices=["json", "sql", "dict"], default="json", help="Export format (default: json)")
    audit_parser.add_argument("--clear", action="store_true", help="Clear audit ledger")

    # Command: cache inspection & management
    cache_parser = subparsers.add_parser("cache", help="Inspect and manage multi-tier reference cache")
    cache_parser.add_argument("--stats", action="store_true", help="Display L1 and L2 cache statistics")
    cache_parser.add_argument("--clear", action="store_true", help="Clear L1 and L2 cache entries")

    # Command: autocomplete typeahead
    auto_parser = subparsers.add_parser("autocomplete", help="Real-time address typeahead and secondary unit prompt")
    auto_parser.add_argument("query", help="Prefix or address query to autocomplete")
    auto_parser.add_argument("--limit", type=int, default=5, help="Maximum suggestions (default: 5)")
    auto_parser.add_argument("--state", help="Filter suggestions by state code")
    auto_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format (default: text)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "parse":
        if args.no_cache:
            configure_cache(enabled=False)

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

        if args.confidence:
            data["confidence_score"] = res.confidence_score
            data["routing_tier"] = res.routing_tier
            data["failure_reason_codes"] = res.failure_reason_codes

        if args.audit:
            if not res.audit_record:
                raw_dict = {
                    "street1": st1,
                    "street2": args.street2,
                    "city": args.city,
                    "state": args.state,
                    "postal_code": args.postal_code,
                    "country": args.country,
                }
                from address_standardizer.confidence import compute_confidence_score
                conf = compute_confidence_score(res, raw_input=raw_dict)
                res.audit_record = get_audit_ledger().record_standardized_address(
                    res, conf, raw_input=raw_dict
                )
            if res.audit_record:
                data["audit_record"] = res.audit_record.as_dict()

        if args.geocode and res.is_us and res.street1:
            geocoder = CensusGeocoder()
            geo_res = geocoder.geocode_batch([("1", res.street1, res.city, res.state, res.postal_code)])
            if "1" in geo_res:
                data["latitude"] = geo_res["1"]["latitude"]
                data["longitude"] = geo_res["1"]["longitude"]
                data["geocode_precision"] = geo_res["1"]["precision"]

        if args.cascade and res.is_us:
            casc = resolve_verification_cascade(
                street1=res.street1,
                street2=res.street2,
                city=res.city,
                state=res.state,
                postal_code=res.postal_code,
                country=res.country,
                normalized_address_key=res.normalized_address_key,
                census_geocoder=CensusGeocoder(),
            )
            if casc:
                data["latitude"] = casc.latitude
                data["longitude"] = casc.longitude
                data["geocode_precision"] = casc.precision
                data["accuracy_radius_meters"] = casc.accuracy_radius_meters
                data["cascade_source"] = casc.source
                data["cascade_stage"] = casc.stage

        print(json.dumps(data, indent=2))

    elif args.command == "batch":
        if args.no_cache:
            configure_cache(enabled=False)

        geocoder = CensusGeocoder() if args.geocode else None
        total = stream_standardize_csv(
            input_path=args.input_csv,
            output_path=args.output_csv,
            chunk_size=args.chunk_size,
            max_workers=args.workers,
            street_col=args.street_col,
            street2_col=args.street2_col,
            city_col=args.city_col,
            state_col=args.state_col,
            zip_col=args.zip_col,
            country_col=args.country_col,
            geocode=args.geocode,
            geocoder=geocoder,
            include_confidence=args.confidence,
            audit_csv_path=args.audit_csv,
        )
        print(f"Standardized {total} record(s) -> {args.output_csv}")
        if args.audit_csv:
            print(f"Wrote audit record(s) -> {args.audit_csv}")

    elif args.command == "audit":
        ledger = get_audit_ledger()
        if args.clear:
            ledger.clear()
            print("Audit ledger cleared.")
            return

        records = ledger.list_records(review_status=args.status)
        if args.export == "sql":
            print(ledger.export(format="sql"))
        elif args.export == "dict":
            print(f"Audit ledger contains {len(records)} record(s):")
            for r in records[:50]:
                print(f"[{r.review_status}] {r.action_type} - {r.record_id} ({r.confidence_score:.4f})")
        else:
            print(json.dumps([r.as_dict() for r in records], indent=2))

    elif args.command == "cache":
        if args.clear:
            clear_cache()
            print("Cache cleared.")
        else:
            stats = get_cache_stats()
            print(json.dumps(stats, indent=2))

    elif args.command == "autocomplete":
        from address_standardizer.autocomplete import autocomplete_address
        suggestions = autocomplete_address(
            query=args.query,
            max_results=args.limit,
            state_filter=args.state,
        )
        if args.format == "json":
            print(json.dumps([s.as_dict() for s in suggestions], indent=2))
        else:
            if not suggestions:
                print("No suggestions found.")
            for i, s in enumerate(suggestions, 1):
                sec_notice = f" [Secondary Unit Required: {', '.join(s.suggested_secondary_units)}]" if s.secondary_prompt_required else ""
                print(f"{i}. {s.text}{sec_notice}")


if __name__ == "__main__":
    main()
