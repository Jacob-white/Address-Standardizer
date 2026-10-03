"""
Command-Line Interface for Address Standardizer.
================================================
Provides a standalone CLI for single address parsing, batch CSV standardization,
benchmark SLA verification, offline spatial R*Tree geocoding, multi-tier verification cascade,
audit ledger triage, and reference cache management.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict

from address_standardizer.audit import get_audit_ledger
from address_standardizer.batch import stream_standardize_csv
from address_standardizer.cache import (
    clear_cache,
    configure_cache,
    get_cache_stats,
)
from address_standardizer.cascade import resolve_verification_cascade
from address_standardizer.geocoder import CensusGeocoder
from address_standardizer.spatial import (
    SpatialEngine,
    get_default_spatial_engine,
    resolve_spatial_coordinates,
)
from address_standardizer.standardizer import standardize_address


def _format_text_address(data: Dict[str, Any]) -> str:
    lines = [
        "STANDARDIZED ADDRESS",
        "====================",
        f"Street 1:              {data.get('street1', '')}",
        f"Street 2:              {data.get('street2', '')}",
        f"City:                  {data.get('city', '')}",
        f"State:                 {data.get('state', '')}",
        f"Postal Code:           {data.get('postal_code', '')}",
        f"Country:               {data.get('country', '')} (ISO3: {data.get('country_iso3', data.get('country', ''))})",
        f"Address Key:           {data.get('normalized_address_key', '')}",
        f"Building Key:          {data.get('building_key', '')}",
        f"Phonetic Key:          {data.get('phonetic_key', '')}",
        f"Status:                {data.get('address_status', '')}",
        f"Is US Address:         {data.get('is_us', True)}",
        f"Private Residence:     {data.get('is_private_residence', False)}",
        f"Registered Agent Hub:  {data.get('is_registered_agent_hub', False)}",
    ]
    if data.get("dependent_locality"):
        lines.append(f"Dependent Locality:    {data['dependent_locality']}")
    if data.get("building_name"):
        lines.append(f"Building Name:         {data['building_name']}")
    if "latitude" in data and "longitude" in data and data["latitude"] is not None and str(data["latitude"]) != "":
        prec = data.get("spatial_precision") or data.get("geocode_precision", "UNKNOWN")
        stage = ""
        if isinstance(data.get("spatial_result"), dict) and data["spatial_result"].get("stage"):
            stage = f", Stage {data['spatial_result']['stage']}"
        elif data.get("cascade_stage"):
            stage = f", Stage {data['cascade_stage']}"
        lines.append(f"Coordinates:           {data['latitude']}, {data['longitude']} ({prec}{stage})")
    if "confidence_score" in data and data["confidence_score"] is not None:
        lines.append(f"Confidence Score:      {data['confidence_score']} (Tier: {data.get('routing_tier', '')})")
    return "\n".join(lines)


def main():
    # Direct shorthand invocation: address-standardizer "100 Wall St, New York, NY 10005"
    if (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in (
            "parse", "batch", "benchmark", "spatial", "audit", "cache", "autocomplete"
        )
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
    parse_parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")
    parse_parser.add_argument("--enable-geocoding", action="store_true", help="Enrich with offline spatial R*Tree geocoder")
    parse_parser.add_argument("--spatial-db", "--db", dest="spatial_db", help="Path to offline SQLite spatial database file")
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
    batch_parser.add_argument("--enable-geocoding", action="store_true", help="Batch geocode with offline spatial engine")
    batch_parser.add_argument("--spatial-db", "--db", dest="spatial_db", help="Path to offline SQLite spatial database file")
    batch_parser.add_argument("--include-intl", action="store_true", help="Include international columns (dependent_locality, building_name)")
    batch_parser.add_argument("--geocode", action="store_true", help="Batch geocode US addresses with Census API")
    batch_parser.add_argument("--confidence", action="store_true", help="Include confidence_score and routing_tier columns")
    batch_parser.add_argument("--audit-csv", help="Path to write audit ledger records as CSV")
    batch_parser.add_argument("--no-cache", action="store_true", help="Disable caching during batch processing")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Execute performance and golden accuracy benchmarks")
    bench_parser.add_argument(
        "--dataset",
        default="domestic",
        help="Benchmark dataset: 'domestic' (US 1k), 'multi_national' (Global 1k), 'all' (Both 2k), or file path (default: domestic)",
    )
    bench_parser.add_argument("--iterations", type=int, default=1, help="Repetitions for throughput profiling (default: 1)")
    bench_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format: 'text' (SLA table report) or 'json' (default: text)")

    # Command: spatial
    spatial_parser = subparsers.add_parser("spatial", help="Offline SQLite R*Tree spatial engine lookup and diagnostics")
    spatial_sub = spatial_parser.add_subparsers(dest="spatial_action", help="Spatial action")

    # spatial lookup
    spatial_lookup = spatial_sub.add_parser("lookup", help="Query spatial database by address, coordinates, or bounding box")
    spatial_lookup.add_argument("address", nargs="*", help="Address string to resolve via spatial cascade")
    spatial_lookup.add_argument("--address", dest="explicit_address", help="Explicit address string")
    spatial_lookup.add_argument("--lat", "--latitude", dest="lat", type=float, help="Latitude for radius query")
    spatial_lookup.add_argument("--lon", "--longitude", dest="lon", type=float, help="Longitude for radius query")
    spatial_lookup.add_argument("--radius", type=float, default=1000.0, help="Search radius in meters (default: 1000.0)")
    spatial_lookup.add_argument("--min-lat", type=float, help="Minimum latitude for bounding box query")
    spatial_lookup.add_argument("--min-lon", type=float, help="Minimum longitude for bounding box query")
    spatial_lookup.add_argument("--max-lat", type=float, help="Maximum latitude for bounding box query")
    spatial_lookup.add_argument("--max-lon", type=float, help="Maximum longitude for bounding box query")
    spatial_lookup.add_argument("--bbox", help="Bounding box as min_lon,min_lat,max_lon,max_lat")
    spatial_lookup.add_argument("--limit", type=int, default=10, help="Maximum results to return (default: 10)")
    spatial_lookup.add_argument("--spatial-db", "--db", dest="spatial_db", help="Path to offline SQLite spatial database file")
    spatial_lookup.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")

    # spatial info
    spatial_info = spatial_sub.add_parser("info", help="Display spatial database index statistics and table counts")
    spatial_info.add_argument("--spatial-db", "--db", dest="spatial_db", help="Path to offline SQLite spatial database file")
    spatial_info.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")

    # spatial stats alias
    spatial_stats = spatial_sub.add_parser("stats", help="Alias for spatial info")
    spatial_stats.add_argument("--spatial-db", "--db", dest="spatial_db", help="Path to offline SQLite spatial database file")
    spatial_stats.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")

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

    raw_args = sys.argv[1:]
    normalized_args = []
    i = 0
    while i < len(raw_args):
        arg = raw_args[i]
        if arg == "--bbox" and i + 1 < len(raw_args) and not raw_args[i + 1].startswith("--"):
            normalized_args.append(f"--bbox={raw_args[i + 1]}")
            i += 2
        else:
            normalized_args.append(arg)
            i += 1

    args = parser.parse_args(normalized_args)

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
        if res.dependent_locality:
            data["dependent_locality"] = res.dependent_locality
        if res.building_name:
            data["building_name"] = res.building_name
        data["country_iso3"] = getattr(res, "country_iso3", None) or res.country or ""

        if args.enable_geocoding:
            engine_to_close = None
            if args.spatial_db:
                engine = SpatialEngine(db_path=args.spatial_db)
                engine_to_close = engine
                sp_res = engine.resolve(res)
            else:
                sp_res = resolve_spatial_coordinates(res)
            if sp_res:
                data["latitude"] = sp_res.latitude
                data["longitude"] = sp_res.longitude
                data["spatial_precision"] = sp_res.precision
                data["geocode_precision"] = sp_res.precision
                data["spatial_source"] = sp_res.source
                data["accuracy_radius_meters"] = sp_res.accuracy_radius_meters
                data["h3_r10_index"] = sp_res.h3_res10
                data["spatial_result"] = sp_res.as_dict()
                res.spatial_result = sp_res
            if engine_to_close:
                engine_to_close.close()

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

        if args.format == "text":
            print(_format_text_address(data))
        else:
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
            enable_geocoding=args.enable_geocoding,
            spatial_db=args.spatial_db,
            include_intl=args.include_intl,
        )
        print(f"Standardized {total} record(s) -> {args.output_csv}")
        if args.audit_csv:
            print(f"Wrote audit record(s) -> {args.audit_csv}")

    elif args.command == "benchmark":
        try:
            from benchmarks.run_benchmarks import print_report, run_all_benchmarks
        except ImportError:
            import importlib.util
            bench_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "run_benchmarks.py"))
            spec = importlib.util.spec_from_file_location("benchmarks.run_benchmarks", bench_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                run_all_benchmarks = getattr(mod, "run_all_benchmarks")
                print_report = getattr(mod, "print_report")
            else:
                raise ImportError(f"Cannot load benchmarks from {bench_path}")

        results = run_all_benchmarks(dataset_path=args.dataset, iterations=args.iterations)
        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            print_report(results)

    elif args.command == "spatial":
        if not args.spatial_action:
            spatial_parser.print_help()
            sys.exit(1)

        engine = SpatialEngine(db_path=args.spatial_db) if args.spatial_db else get_default_spatial_engine()
        engine_to_close = engine if args.spatial_db else None
        try:
            if args.spatial_action == "lookup":
                addr_input = args.explicit_address or (" ".join(args.address) if args.address else None)
                if addr_input:
                    std_addr = standardize_address(street1=addr_input)
                    sp_res = engine.resolve(std_addr)
                    if args.format == "text":
                        print("SPATIAL RESOLUTION RESULT")
                        print("=========================")
                        print(f"Status:                {sp_res.precision}")
                        print(f"Latitude:              {sp_res.latitude}")
                        print(f"Longitude:             {sp_res.longitude}")
                        print(f"Accuracy Radius (m):   {sp_res.accuracy_radius_meters}")
                        print(f"Cascade Stage:         {sp_res.stage}")
                        print(f"Source:                {sp_res.source}")
                        print(f"H3 Res10:              {sp_res.h3_res10}")
                        print(f"Parcel ID:             {sp_res.parcel_id or 'None'}")
                    else:
                        print(json.dumps([sp_res.as_dict()], indent=2))
                elif args.bbox:
                    try:
                        sep = "," if "," in args.bbox else None
                        parts = [float(x.strip()) for x in (args.bbox.split(",") if sep else args.bbox.split())]
                    except ValueError:
                        parts = []
                    if len(parts) != 4:
                        sys.stderr.write("Error: --bbox requires 4 values: min_lon,min_lat,max_lon,max_lat\n")
                        sys.exit(2)
                    min_lon, min_lat, max_lon, max_lat = parts
                    results = engine.query_bounding_box(min_lon, min_lat, max_lon, max_lat, limit=args.limit)
                    if args.format == "text":
                        print(f"Found {len(results)} spatial point(s) in bounding box:")
                        for i, r in enumerate(results, 1):
                            print(f"{i}. {r.latitude}, {r.longitude} ({r.precision}, {r.source}) - H3: {r.h3_res10}")
                    else:
                        print(json.dumps([r.as_dict() for r in results], indent=2))
                elif (
                    args.min_lat is not None
                    and args.min_lon is not None
                    and args.max_lat is not None
                    and args.max_lon is not None
                ):
                    results = engine.query_bounding_box(
                        args.min_lon, args.min_lat, args.max_lon, args.max_lat, limit=args.limit
                    )
                    if args.format == "text":
                        print(f"Found {len(results)} spatial point(s) in bounding box:")
                        for i, r in enumerate(results, 1):
                            print(f"{i}. {r.latitude}, {r.longitude} ({r.precision}, {r.source}) - H3: {r.h3_res10}")
                    else:
                        print(json.dumps([r.as_dict() for r in results], indent=2))
                elif args.lat is not None and args.lon is not None:
                    results = engine.query_radius(
                        lon=args.lon, lat=args.lat, radius_meters=args.radius, limit=args.limit
                    )
                    if args.format == "text":
                        print(f"Found {len(results)} spatial point(s) within {args.radius:.1f}m:")
                        for i, r in enumerate(results, 1):
                            print(f"{i}. {r.latitude}, {r.longitude} ({r.precision}, {r.source}) - H3: {r.h3_res10}")
                    else:
                        print(json.dumps([r.as_dict() for r in results], indent=2))
                else:
                    sys.stderr.write(
                        "Error: spatial lookup requires address, coordinates (--lat and --lon), or bounding box (--min-lat, --min-lon, --max-lat, --max-lon or --bbox).\n"
                    )
                    sys.exit(2)
            elif args.spatial_action in ("info", "stats"):
                with engine._lock:
                    pts_count = engine.count()
                    cur = engine._conn.execute("SELECT count(*) FROM street_segments")
                    seg_count = cur.fetchone()[0]
                    cur = engine._conn.execute("SELECT count(*) FROM postal_centroids")
                    post_count = cur.fetchone()[0]
                    cur = engine._conn.execute("SELECT count(*) FROM municipal_centroids")
                    muni_count = cur.fetchone()[0]

                stats = {
                    "database_path": engine._db_path,
                    "total_spatial_points": pts_count,
                    "street_segments_count": seg_count,
                    "postal_centroids_count": post_count,
                    "municipal_centroids_count": muni_count,
                    "rtree_index_enabled": True,
                    "memory_pragmas": {
                        "journal_mode": "WAL",
                        "cache_size_kb": 64000,
                        "mmap_size_mb": 256,
                        "temp_store": "MEMORY",
                    },
                }
                if args.format == "json":
                    print(json.dumps(stats, indent=2))
                else:
                    print("SPATIAL DATABASE DIAGNOSTICS & INDEX STATISTICS")
                    print("================================================")
                    print(f"Database Path:             {stats['database_path']}")
                    print(f"Indexed Spatial Points:    {stats['total_spatial_points']:,}")
                    print(f"Street Segments:           {stats['street_segments_count']:,}")
                    print(f"Postal Centroids:          {stats['postal_centroids_count']:,}")
                    print(f"Municipal Centroids:       {stats['municipal_centroids_count']:,}")
                    print(f"R*Tree Index Enabled:      {stats['rtree_index_enabled']}")
                    print("Pragmas:                   WAL, cache_size=-64000, mmap_size=256MB")
        finally:
            if engine_to_close:
                engine_to_close.close()

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
