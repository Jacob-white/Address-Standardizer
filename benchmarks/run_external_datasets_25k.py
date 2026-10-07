#!/usr/bin/env python3
"""
Run 25,000 samples for Datasets 1-4 and merge with Dataset 5 into investigation_5_datasets_results.json
"""
import os
import sys
import time
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from benchmarks.run_investigation_5_datasets import (
    benchmark_openaddresses,
    benchmark_overture_global,
    benchmark_census_tiger,
    benchmark_uk_paf_upu,
    DatasetMetrics,
)
from collections import Counter

def main():
    print("=" * 80)
    print("RUNNING 25,000 RECORDS PER EXTERNAL BENCHMARK DATASET")
    print("=" * 80)

    sample_size = 25000
    res_oa = benchmark_openaddresses(sample_limit=sample_size)
    res_overture = benchmark_overture_global(sample_limit=sample_size)
    res_tiger = benchmark_census_tiger(sample_limit=sample_size)
    res_uk_upu = benchmark_uk_paf_upu(sample_limit=sample_size)

    # Load existing report to preserve Dataset 5 (Firm Network 214,129 records)
    report_path = os.path.join(REPO_ROOT, "benchmarks", "investigation_5_datasets_results.json")
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    external_results = [res_oa, res_overture, res_tiger, res_uk_upu]

    for r in external_results:
        tot = max(r.total_records, 1)
        std_pct = r.standardized_count / tot * 100.0
        loc_pct = r.locality_only_count / tot * 100.0
        fail_pct = r.parse_failed_count / tot * 100.0

        auto_pct = r.auto_pass_count / tot * 100.0
        fuzzy_pct = r.fuzzy_review_count / tot * 100.0
        manual_pct = r.manual_stewardship_count / tot * 100.0

        deliv_pct = r.deliverable_count / tot * 100.0
        sec_pct = r.requires_secondary_count / tot * 100.0
        undeliv_pct = r.undeliverable_count / tot * 100.0

        roof_prec_pct = r.confirmed_rooftop_count / tot * 100.0
        range_prec_pct = r.range_interpolated_count / tot * 100.0
        post_prec_pct = r.postal_centroid_count / tot * 100.0
        unres_prec_pct = r.unresolved_precision_count / tot * 100.0

        fp_breakdown = Counter(fp.get("type") for fp in r.false_positives)
        fn_breakdown = Counter(fn.get("type") for fn in r.false_negatives)

        report["datasets"][r.dataset_name] = {
            "total_records": r.total_records,
            "duration_seconds": round(r.duration_seconds, 2),
            "throughput_rec_sec": round(r.throughput_rec_sec, 1),
            "status": {
                "standardized": r.standardized_count,
                "locality_only": r.locality_only_count,
                "parse_failed": r.parse_failed_count,
                "usable_yield_percent": round(r.usable_yield_percent, 2),
            },
            "routing_tiers": {
                "auto_pass": r.auto_pass_count,
                "fuzzy_review": r.fuzzy_review_count,
                "manual_stewardship": r.manual_stewardship_count,
                "auto_pass_pct": round(auto_pct, 2),
                "fuzzy_review_pct": round(fuzzy_pct, 2),
                "manual_stewardship_pct": round(manual_pct, 2),
            },
            "deliverability": {
                "deliverable": r.deliverable_count,
                "requires_secondary": r.requires_secondary_count,
                "undeliverable": r.undeliverable_count,
                "deliverable_pct": round(deliv_pct, 2),
                "requires_secondary_pct": round(sec_pct, 2),
                "undeliverable_pct": round(undeliv_pct, 2),
            },
            "spatial_precision": {
                "confirmed_rooftop": r.confirmed_rooftop_count,
                "range_interpolated": r.range_interpolated_count,
                "postal_centroid": r.postal_centroid_count,
                "municipal_centroid": r.municipal_centroid_count,
                "unresolved": r.unresolved_precision_count,
                "confirmed_rooftop_pct": round(roof_prec_pct, 2),
                "range_interpolated_pct": round(range_prec_pct, 2),
                "postal_centroid_pct": round(post_prec_pct, 2),
                "unresolved_pct": round(unres_prec_pct, 2),
            },
            "rooftop_address_extracted_count": r.rooftop_extracted_count,
            "entity_features": {
                "private_residences": r.private_residence_count,
                "registered_agent_hubs": r.registered_agent_hub_count,
                "cmra": r.cmra_count,
                "vacant": r.vacant_count,
            },
            "geography": {
                "us_count": r.us_records,
                "intl_count": r.intl_records,
                "jurisdictions_count": len(r.country_distribution),
                "top_jurisdictions": dict(r.country_distribution.most_common(10)),
            },
            "failure_reason_codes": dict(r.failure_reasons.most_common(12)),
            "false_positives": {
                "total_count": len(r.false_positives),
                "breakdown": dict(fp_breakdown),
                "samples": r.false_positives[:10],
            },
            "false_negatives": {
                "total_count": len(r.false_negatives),
                "breakdown": dict(fn_breakdown),
                "samples": r.false_negatives[:10],
            },
            "edge_cases": r.edge_cases[:10],
        }

    # Recalculate totals
    total_eval = sum(d["total_records"] for d in report["datasets"].values())
    total_dur = sum(d["duration_seconds"] for d in report["datasets"].values())
    report["total_records_evaluated"] = total_eval
    report["overall_duration_seconds"] = round(total_dur, 2)
    report["overall_throughput_rec_sec"] = round(total_eval / max(total_dur, 0.001), 1)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nSuccessfully updated {report_path} with {total_eval:,} total records across 5 datasets!")

if __name__ == "__main__":
    main()
