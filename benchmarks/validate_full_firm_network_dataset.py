"""
Full Firm Network Dataset Validation & Empirical Audit.
======================================================
Comprehensive evaluation across 100% of all table records:
1. production.firm_branch (103,120 records)
2. production.firm_master (68,831 records)
3. production.fdic_bank_branch (10,017 records)
4. production.contact_association (17,316 contact-specific + 6,999 private residence records)
"""

import os
import sys
import time
import json
import psycopg2
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from address_standardizer import standardize_address, _native_dispatch


def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "firm_association"),
        user=os.environ.get("DB_USER", "daas_user"),
        password=os.environ.get("DB_PASSWORD", "change-me"),
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "5434")),
    )


def validate_firm_branches(conn) -> Dict[str, Any]:
    print("\n--- [1/4] Validating 100% of production.firm_branch ---")
    cur = conn.cursor(name="branch_stream_cursor")
    cur.itersize = 5000
    cur.execute("""
        SELECT branch_id, street1, street2, city, state, postal_code, country
        FROM production.firm_branch
        ORDER BY branch_id;
    """)

    total = 0
    standardized = 0
    locality_only = 0
    parse_failed = 0
    blank = 0
    tiers = {"AUTO_PASS": 0, "FUZZY_REVIEW": 0, "MANUAL_STEWARDSHIP": 0}
    campuses = 0
    failure_samples = []

    t0 = time.perf_counter()
    while True:
        rows = cur.fetchmany(5000)
        if not rows:
            break
        for row in rows:
            b_id, s1, s2, city, state, postal, country = row
            total += 1
            if not any(bool(x and str(x).strip()) for x in (s1, s2, city, state, postal)):
                blank += 1
                tiers["MANUAL_STEWARDSHIP"] += 1
                continue

            res = standardize_address(
                street1=s1,
                street2=s2,
                city=city,
                state=state,
                postal_code=postal,
                country=country or "USA",
                allow_locality=True,
            )

            status = str(res.address_status)
            if status == "standardized":
                standardized += 1
            elif status in ("locality_only", "city_level"):
                locality_only += 1
            else:
                parse_failed += 1
                if len(failure_samples) < 5:
                    failure_samples.append({
                        "branch_id": str(b_id),
                        "input": f"{s1}, {city}, {state} {postal}",
                        "error": res.status_description,
                    })

            tier = res.routing_tier or "MANUAL_STEWARDSHIP"
            tiers[tier] = tiers.get(tier, 0) + 1

            if res.building_name:
                campuses += 1

        if total % 25000 == 0:
            print(f"  Processed {total:,} branches...")

    cur.close()
    elapsed = time.perf_counter() - t0
    resolved = standardized + locality_only
    pct_resolved = (resolved / (total - blank) * 100.0) if (total - blank) > 0 else 0.0

    return {
        "total_records": total,
        "blank_records": blank,
        "evaluated_records": total - blank,
        "fully_standardized": standardized,
        "locality_only": locality_only,
        "parse_failed": parse_failed,
        "total_resolved": resolved,
        "resolution_pct": round(pct_resolved, 3),
        "routing_tiers": tiers,
        "campus_premises_detected": campuses,
        "throughput_rec_sec": round(total / elapsed, 1) if elapsed > 0 else 0,
        "elapsed_sec": round(elapsed, 2),
        "failure_samples": failure_samples,
    }


def validate_firm_masters(conn) -> Dict[str, Any]:
    print("\n--- [2/4] Validating 100% of production.firm_master ---")
    cur = conn.cursor(name="master_stream_cursor")
    cur.itersize = 5000
    cur.execute("""
        SELECT
            fm.firm_master_id,
            COALESCE(
                NULLIF(TRIM(fm.street_address), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'Strt1'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'Strt1'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'street1'), '')
            ) as s1,
            COALESCE(
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'Strt2'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'Strt2'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'street2'), '')
            ) as s2,
            COALESCE(
                NULLIF(TRIM(fm.main_office_city), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'City'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'City'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'city'), '')
            ) as city,
            COALESCE(
                NULLIF(TRIM(fm.main_office_state), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'State'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'State'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'state'), '')
            ) as state,
            COALESCE(
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'PostlCd'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'PostlCd'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'postalCode'), '')
            ) as postal,
            COALESCE(
                NULLIF(TRIM(fm.main_office_country), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'Cntry'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'Cntry'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'country'), ''),
                'USA'
            ) as country
        FROM production.firm_master fm
        ORDER BY fm.firm_master_id;
    """)

    total = 0
    standardized = 0
    locality_only = 0
    parse_failed = 0
    blank = 0
    tiers = {"AUTO_PASS": 0, "FUZZY_REVIEW": 0, "MANUAL_STEWARDSHIP": 0}
    failure_samples = []

    t0 = time.perf_counter()
    while True:
        rows = cur.fetchmany(5000)
        if not rows:
            break
        for row in rows:
            m_id, s1, s2, city, state, postal, country = row
            total += 1
            if not any(bool(x and str(x).strip()) for x in (s1, s2, city, state, postal)):
                blank += 1
                tiers["MANUAL_STEWARDSHIP"] += 1
                continue

            res = standardize_address(
                street1=s1,
                street2=s2,
                city=city,
                state=state,
                postal_code=postal,
                country=country or "USA",
                allow_locality=True,
            )

            status = str(res.address_status)
            if status == "standardized":
                standardized += 1
            elif status in ("locality_only", "city_level"):
                locality_only += 1
            else:
                parse_failed += 1
                if len(failure_samples) < 5:
                    failure_samples.append({
                        "firm_master_id": str(m_id),
                        "input": f"{s1}, {city}, {state} {postal}",
                        "error": res.status_description,
                    })

            tier = res.routing_tier or "MANUAL_STEWARDSHIP"
            tiers[tier] = tiers.get(tier, 0) + 1

        if total % 25000 == 0:
            print(f"  Processed {total:,} firm masters...")

    cur.close()
    elapsed = time.perf_counter() - t0
    resolved = standardized + locality_only
    evaluated = total - blank
    pct_resolved = (resolved / evaluated * 100.0) if evaluated > 0 else 0.0

    return {
        "total_records": total,
        "blank_records": blank,
        "evaluated_records": evaluated,
        "fully_standardized": standardized,
        "locality_only": locality_only,
        "parse_failed": parse_failed,
        "total_resolved": resolved,
        "resolution_pct": round(pct_resolved, 3),
        "routing_tiers": tiers,
        "throughput_rec_sec": round(total / elapsed, 1) if elapsed > 0 else 0,
        "elapsed_sec": round(elapsed, 2),
        "failure_samples": failure_samples,
    }


def validate_fdic_branches(conn) -> Dict[str, Any]:
    print("\n--- [3/4] Validating 100% of production.fdic_bank_branch ---")
    cur = conn.cursor()
    cur.execute("""
        SELECT branch_id, address, city, state_code, zip_code
        FROM production.fdic_bank_branch
        ORDER BY branch_id;
    """)
    rows = cur.fetchall()
    cur.close()

    total = len(rows)
    standardized = 0
    locality_only = 0
    parse_failed = 0
    cross_border = 0
    sovereign_countries = set()
    tiers = {"AUTO_PASS": 0, "FUZZY_REVIEW": 0, "MANUAL_STEWARDSHIP": 0}

    t0 = time.perf_counter()
    for row in rows:
        b_id, addr, city, state_code, zip_code = row
        country_param = None if (state_code == "US" and zip_code == "00000") else "USA"
        state_param = None if state_code == "US" else state_code
        res = standardize_address(
            street1=addr,
            city=city,
            state=state_param,
            postal_code=zip_code,
            country=country_param,
            allow_locality=True,
        )

        status = str(res.address_status)
        if status == "standardized":
            standardized += 1
        elif status in ("locality_only", "city_level"):
            locality_only += 1
        else:
            parse_failed += 1

        tier = res.routing_tier or "MANUAL_STEWARDSHIP"
        tiers[tier] = tiers.get(tier, 0) + 1

        if res.country_iso3 and res.country_iso3 != "USA":
            cross_border += 1
            sovereign_countries.add(res.country_iso3)

    elapsed = time.perf_counter() - t0
    resolved = standardized + locality_only
    pct_resolved = (resolved / total * 100.0) if total > 0 else 0.0

    return {
        "total_records": total,
        "fully_standardized": standardized,
        "locality_only": locality_only,
        "parse_failed": parse_failed,
        "total_resolved": resolved,
        "resolution_pct": round(pct_resolved, 3),
        "cross_border_branches": cross_border,
        "sovereign_jurisdictions_count": len(sovereign_countries),
        "routing_tiers": tiers,
        "throughput_rec_sec": round(total / elapsed, 1) if elapsed > 0 else 0,
        "elapsed_sec": round(elapsed, 2),
    }


def validate_contact_associations(conn) -> Dict[str, Any]:
    print("\n--- [4/4] Validating production.contact_association ---")
    cur = conn.cursor()

    # 1. Total counts in table
    cur.execute("SELECT COUNT(*) FROM production.contact_association;")
    total_table_rows = cur.fetchone()[0]

    # 2. Unlinked / contact-specific addresses
    cur.execute("""
        SELECT association_id, stationed_street1, stationed_street2, stationed_city, stationed_state, stationed_postal_code, stationed_country
        FROM production.contact_association
        WHERE NULLIF(TRIM(stationed_street1), '') IS NOT NULL OR NULLIF(TRIM(stationed_city), '') IS NOT NULL;
    """)
    stationed_rows = cur.fetchall()

    # 3. Private residences
    cur.execute("""
        SELECT association_id, stationed_street1, stationed_street2, stationed_city, stationed_state, stationed_postal_code, stationed_country
        FROM production.contact_association
        WHERE stationed_street1 ILIKE '%PRIVATE RESIDENCE%' OR stationed_address_key ILIKE '%PRIVATE RESIDENCE%';
    """)
    private_rows = cur.fetchall()
    cur.close()

    # Benchmark stationed addresses
    t0 = time.perf_counter()
    std_contact = 0
    loc_contact = 0
    fail_contact = 0
    for row in stationed_rows:
        _, s1, s2, city, state, postal, country = row
        res = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country or "USA",
            allow_locality=True,
        )
        status = str(res.address_status)
        if status == "standardized":
            std_contact += 1
        elif status in ("locality_only", "city_level"):
            loc_contact += 1
        else:
            fail_contact += 1

    elapsed_contact = time.perf_counter() - t0

    # Benchmark private residences
    t1 = time.perf_counter()
    priv_detected = 0
    priv_keys = 0
    for row in private_rows:
        _, s1, s2, city, state, postal, country = row
        res = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country or "USA",
            allow_locality=True,
        )
        if res.is_private_residence:
            priv_detected += 1
        if res.normalized_address_key and "PRIVATE RESIDENCE" in res.normalized_address_key:
            priv_keys += 1
    elapsed_priv = time.perf_counter() - t1

    total_stationed = len(stationed_rows)
    resolved_stationed = std_contact + loc_contact
    pct_resolved = (resolved_stationed / total_stationed * 100.0) if total_stationed > 0 else 0.0

    return {
        "total_table_rows": total_table_rows,
        "stationed_addresses": {
            "total_evaluated": total_stationed,
            "fully_standardized": std_contact,
            "locality_only": loc_contact,
            "parse_failed": fail_contact,
            "total_resolved": resolved_stationed,
            "resolution_pct": round(pct_resolved, 3),
            "throughput_rec_sec": round(total_stationed / elapsed_contact, 1) if elapsed_contact > 0 else 0,
            "elapsed_sec": round(elapsed_contact, 2),
        },
        "private_residences": {
            "total_evaluated": len(private_rows),
            "privacy_flags_detected": priv_detected,
            "detection_pct": round(priv_detected / len(private_rows) * 100.0, 2) if private_rows else 0.0,
            "sanitized_keys_created": priv_keys,
            "sanitized_key_pct": round(priv_keys / len(private_rows) * 100.0, 2) if private_rows else 0.0,
            "throughput_rec_sec": round(len(private_rows) / elapsed_priv, 1) if elapsed_priv > 0 else 0,
            "elapsed_sec": round(elapsed_priv, 2),
        },
    }


def main():
    print("======================================================================")
    print("FIRM NETWORK ADDRESS DATASET — FULL 100% PRODUCTION VALIDATION")
    print("======================================================================")
    engine_info = _native_dispatch.get_engine_info()
    print("Engine Configuration:")
    print(f"  Active Engine: {engine_info['engine']}")
    print(f"  Native Rust Active: {engine_info['is_native']}")
    print(f"  SIMD Acceleration: {engine_info.get('simd_acceleration', False)}")
    print(f"  Throughput SLA: {engine_info['throughput_sla_target']}")

    conn = get_db_connection()
    t_start = time.perf_counter()

    results = {
        "engine_info": engine_info,
        "firm_branch": validate_firm_branches(conn),
        "firm_master": validate_firm_masters(conn),
        "fdic_bank_branch": validate_fdic_branches(conn),
        "contact_association": validate_contact_associations(conn),
    }

    t_total = time.perf_counter() - t_start
    results["total_execution_sec"] = round(t_total, 2)
    conn.close()

    print("\n======================================================================")
    print("FINAL 100% VALIDATION RESULTS")
    print("======================================================================")
    print(json.dumps(results, indent=2))

    # Save to disk
    out_path = os.path.join(os.path.dirname(__file__), "full_validation_report.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()
