"""
Validation Benchmark for Address Standardizer on Production Contact Association Data.
=====================================================================================
Evaluates real-world efficacy, throughput, and privacy invariants on:
1. 17,316 contact association addresses from production.contact_association
2. 2,678 private residence records from production.contact_association
"""

import os
import sys
import time
import psycopg2
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from address_standardizer import standardize_address


def run_contact_association_benchmark() -> Dict[str, Any]:
    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "firm_association"),
        user=os.environ.get("DB_USER", "daas_user"),
        password=os.environ.get("DB_PASSWORD", "change-me"),
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "5434")),
    )
    cur = conn.cursor()

    # 1. Fetch 17,316 contact records
    cur.execute("""
        SELECT association_id, stationed_street1, stationed_street2, stationed_city, stationed_state, stationed_postal_code, stationed_country
        FROM production.contact_association
        WHERE NULLIF(TRIM(stationed_street1), '') IS NOT NULL OR NULLIF(TRIM(stationed_city), '') IS NOT NULL
        LIMIT 17316;
    """)
    batch_17k = cur.fetchall()

    # 2. Fetch 2,678 private residence records
    cur.execute("""
        SELECT association_id, stationed_street1, stationed_street2, stationed_city, stationed_state, stationed_postal_code, stationed_country
        FROM production.contact_association
        WHERE stationed_street1 ILIKE '%PRIVATE RESIDENCE%' OR stationed_address_key ILIKE '%PRIVATE RESIDENCE%'
        LIMIT 2678;
    """)
    batch_private = cur.fetchall()
    conn.close()

    # Benchmark 1: 17,316 Contact Association Addresses
    t0 = time.perf_counter()
    std_count = 0
    loc_count = 0
    fail_count = 0
    for row in batch_17k:
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
        if res.address_status == "standardized":
            std_count += 1
        elif res.address_status == "locality_only":
            loc_count += 1
        else:
            fail_count += 1
    t1 = time.perf_counter()

    # Benchmark 2: 2,678 Private Residences
    t2 = time.perf_counter()
    priv_detected = 0
    priv_keys_clean = 0
    priv_tiers = {}
    for row in batch_private:
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
            priv_keys_clean += 1
        priv_tiers[res.routing_tier] = priv_tiers.get(res.routing_tier, 0) + 1
    t3 = time.perf_counter()

    return {
        "unlinked_contacts": {
            "total_evaluated": len(batch_17k),
            "fully_standardized": std_count,
            "locality_only": loc_count,
            "total_resolved": std_count + loc_count,
            "resolution_pct": round((std_count + loc_count) / len(batch_17k) * 100.0, 2),
            "parse_failures": fail_count,
            "execution_sec": round(t1 - t0, 3),
            "throughput_rec_sec": round(len(batch_17k) / (t1 - t0), 1),
            "avg_latency_ms": round((t1 - t0) / len(batch_17k) * 1000.0, 4),
        },
        "private_residences": {
            "total_evaluated": len(batch_private),
            "privacy_flags_detected": priv_detected,
            "detection_pct": round(priv_detected / len(batch_private) * 100.0, 2),
            "sanitized_keys_created": priv_keys_clean,
            "sanitized_key_pct": round(priv_keys_clean / len(batch_private) * 100.0, 2),
            "routing_tiers": priv_tiers,
            "execution_sec": round(t3 - t2, 3),
            "throughput_rec_sec": round(len(batch_private) / (t3 - t2), 1),
            "avg_latency_ms": round((t3 - t2) / len(batch_private) * 1000.0, 4),
        },
    }


if __name__ == "__main__":
    results = run_contact_association_benchmark()
    import json
    print(json.dumps(results, indent=2))
