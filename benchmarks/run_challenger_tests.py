"""
Adversarial Verification & Stress Test Suite for Address-Standardizer.
Author: challenger_5_1 (teamwork_preview_challenger)
"""

import csv
import gc
import json
import os

import subprocess
import sys
import time

# Ensure project root is in path


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from address_standardizer._memory import peak_rss_kb as _peak_rss_kb  # noqa: E402
from address_standardizer import standardize_address, batch_standardize, stream_standardize_jsonl
from address_standardizer.batch import stream_standardize_csv
from address_standardizer import _pure_python_core


def get_current_rss_mb() -> float:
    """Returns current process Resident Set Size in MB."""
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    return float(parts[1]) / 1024.0
    except Exception:
        pass
    usage_kb = _peak_rss_kb()
    return usage_kb / 1024.0


def test_public_invariants():
    print("=" * 80)
    print("TEST 1: PUBLIC INVARIANTS & AS_DICT(include_metadata=False)")
    print("=" * 80)

    test_cases = [
        "100 Main St, New York, NY 10001",
        "PSC 1004, BOX 500, APO, AE 09724",
        "PO BOX 123, CHICAGO, IL 60601",
        "URB LAS GLADIOLAS, 123 CALLE A, SAN JUAN, PR 00926",
        "10 Downing St, London, SW1A 2AA, UK",
        "",
        "INVALID RANDOM STRING !@#$%",
    ]

    expected_14_keys = {
        "street1", "street2", "city", "state", "postal_code", "country",
        "normalized_address_key", "building_key", "phonetic_key",
        "address_status", "raw_street_address", "is_us",
        "is_private_residence", "is_registered_agent_hub"
    }

    all_passed = True
    for raw in test_cases:
        res = standardize_address(raw)
        d_no_meta = res.as_dict(include_metadata=False)
        _ = res.as_dict(include_metadata=True)
        keys_no_meta = set(d_no_meta.keys())

        if len(keys_no_meta) != 14:
            print(f"FAILED 14-key count invariant for '{raw}': got {len(keys_no_meta)} keys: {keys_no_meta}")
            all_passed = False
        if keys_no_meta != expected_14_keys:
            print(f"FAILED exact keys match for '{raw}': diff: {keys_no_meta.symmetric_difference(expected_14_keys)}")
            all_passed = False

    if all_passed:
        print("PASS: Exactly 14 keys maintained across all diverse inputs!")
        print(f"Verified 14 keys: {sorted(list(expected_14_keys))}")
    return all_passed


def test_pure_python_fallback():
    print("=" * 80)
    print("TEST 2: PURE PYTHON FALLBACK EXECUTION")
    print("=" * 80)

    # Verify _pure_python_core can parse directly
    raw_tuples = [
        ("100 Main St", "Suite 400", "New York", "NY", "10001", "USA"),
        ("PSC 1004 BOX 500", "", "APO", "AE", "09724", "USA"),
        ("Calle Mayor 45", "2º B", "Madrid", "", "28013", "ESP"),
    ]

    batch_results = _pure_python_core.standardize_batch(raw_tuples, finalize=True)
    if len(batch_results) != 3:
        print("FAILED: _pure_python_core.standardize_batch did not return 3 results")
        return False

    print(f"PASS: _pure_python_core processed {len(batch_results)} records cleanly.")
    for idx, r in enumerate(batch_results):
        print(f"  [{idx}] normalized_address_key={r.normalized_address_key}, building_key={r.building_key}")

    return True


def test_adversarial_inputs():
    print("=" * 80)
    print("TEST 3: ADVERSARIAL INPUT PARSING")
    print("=" * 80)

    cases = [
        # Military variations
        {
            "raw": "PSC 1004, BOX 500, APO, AE 09724",
            "check": lambda r: "PSC 1004 BOX 500" in r.street1 and r.city == "APO" and r.state == "AE" and r.postal_code == "09724" and "F1" in (r.dpv_footnotes or []),
            "desc": "Military PSC with comma before BOX"
        },
        {
            "raw": "cmr 411 box 2000, dpo, aa 34004",
            "check": lambda r: "CMR 411 BOX 2000" in r.street1 and r.city == "DPO" and r.state == "AA" and r.postal_code == "34004" and "F1" in (r.dpv_footnotes or []),
            "desc": "Military CMR lowercase with DPO and AA"
        },
        {
            "raw": "UNIT 1234 BOX 5678, FPO, AP 96606",
            "check": lambda r: "UNIT 1234 BOX 5678" in r.street1 and r.city == "FPO" and r.state == "AP" and r.postal_code == "96606" and "F1" in (r.dpv_footnotes or []),
            "desc": "Military UNIT with FPO and AP"
        },
        {
            "raw": "cmr   411   box   2000, dpo, aa 34004",
            "check": lambda r: "CMR 411 BOX 2000" in r.street1 and r.city == "DPO",
            "desc": "Military CMR with excessive whitespace"
        },
        {
            "raw": "123 PSC WAY, DALLAS, TX 75001",
            "check": lambda r: r.street1 == "123 PSC WAY" and r.city == "DALLAS" and r.state == "TX" and "F1" not in (r.dpv_footnotes or []),
            "desc": "Non-military street containing PSC keyword"
        },
        {
            "raw": "456 CMR BLVD, AUSTIN, TX 78701",
            "check": lambda r: r.street1 == "456 CMR BLVD" and r.city == "AUSTIN" and r.state == "TX" and "F1" not in (r.dpv_footnotes or []),
            "desc": "Non-military street containing CMR keyword"
        },
        # Puerto Rico Urbanizations
        {
            "raw": "URB LAS GLADIOLAS, 123 CALLE A, SAN JUAN, PR 00926",
            "check": lambda r: "CALLE A" in (r.street1 or "") and r.state == "PR" and r.postal_code == "09724"[:2] == "09" or r.state == "PR",
            "desc": "Puerto Rico Urbanization leading"
        },
        {
            "raw": "123 CALLE A, URB LAS GLADIOLAS, SAN JUAN, PR 00926",
            "check": lambda r: "CALLE A" in (r.street1 or "") and r.state == "PR",
            "desc": "Puerto Rico Urbanization trailing street"
        },
        # Multi-line unstructured
        {
            "raw": "123 Main St\nSuite 400\nBuilding B\nDallas, TX 75001",
            "check": lambda r: r.street1 == "123 MAIN ST" and "400" in (r.street2 or "") and r.city == "DALLAS" and r.state == "TX" and r.postal_code == "75001",
            "desc": "Multi-line newline separated address"
        },
        {
            "raw": "456 Oak Avenue\r\nApt 2B\r\nFloor 3\r\nChicago, IL 60601",
            "check": lambda r: "456 OAK" in r.street1 and "2B" in (r.street2 or "") and r.city == "CHICAGO" and r.state == "IL" and r.postal_code == "60601",
            "desc": "Multi-line CRLF separated address"
        },
        # Secondary units
        {
            "raw": "100 Main St, Ste 400, New York, NY 10001",
            "check": lambda r: r.street2 == "STE 400",
            "desc": "Secondary unit Ste"
        },
        {
            "raw": "200 Broad St, Apt 2B, Philadelphia, PA 19102",
            "check": lambda r: r.street2 == "APT 2B",
            "desc": "Secondary unit Apt"
        },
        {
            "raw": "300 Market St, Fl 3, San Francisco, CA 94105",
            "check": lambda r: r.street2 == "FL 3",
            "desc": "Secondary unit Fl"
        },
        {
            "raw": "400 Tech Way, Bldg C, Rm 101, Seattle, WA 98101",
            "check": lambda r: "BLDG C" in (r.street2 or "") and "RM 101" in (r.street2 or ""),
            "desc": "Secondary units Bldg and Rm"
        },
        # PO Boxes
        {
            "raw": "PO BOX 123, NEW YORK, NY 10001",
            "check": lambda r: r.street1 == "PO BOX 123" and r.city == "NEW YORK" and r.state == "NY" and r.postal_code == "10001",
            "desc": "PO BOX format"
        },
        {
            "raw": "P.O. Box 456, Chicago, IL 60601",
            "check": lambda r: r.street1 == "PO BOX 456" and r.city == "CHICAGO",
            "desc": "P.O. Box with periods"
        },
        {
            "raw": "Post Office Box 789, Miami, FL 33101",
            "check": lambda r: r.street1 == "PO BOX 789" and r.city == "MIAMI",
            "desc": "Post Office Box spelled out"
        },
        {
            "raw": "POB 101, Seattle, WA 98101",
            "check": lambda r: r.street1 == "PO BOX 101" and r.city == "SEATTLE",
            "desc": "POB abbreviation"
        },
        {
            "raw": "123 Main St, PO Box 456, Austin, TX 78701",
            "check": lambda r: ("123 MAIN ST" in r.street1 or "PO BOX 456" in r.street1) and r.city == "AUSTIN",
            "desc": "Dual address (street + PO Box)"
        },
        # Rural routes
        {
            "raw": "RR 1 BOX 12, BLUFFS, IL 62621",
            "check": lambda r: "RR 1" in r.street1 and "BOX 12" in r.street1 and r.city == "BLUFFS" and r.state == "IL",
            "desc": "Rural Route RR format"
        },
        {
            "raw": "RURAL ROUTE 2 BOX 45, SPRINGFIELD, IL 62701",
            "check": lambda r: "RR 2" in r.street1 and "BOX 45" in r.street1 and r.city == "SPRINGFIELD",
            "desc": "Rural Route spelled out"
        },
        {
            "raw": "HC 3 BOX 10, TAOS, NM 87571",
            "check": lambda r: "HC 3" in r.street1 and "BOX 10" in r.street1 and r.city == "TAOS",
            "desc": "Highway Contract HC format"
        },
    ]

    passed_count = 0
    for case in cases:
        res = standardize_address(case["raw"])
        ok = case["check"](res)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed_count += 1
        else:
            print(f"FAILED: {case['desc']}")
            print(f"  Raw: {case['raw']!r}")
            print(f"  Result: street1={res.street1!r}, street2={res.street2!r}, city={res.city!r}, state={res.state!r}, zip={res.postal_code!r}, dpv={res.dpv_footnotes}")
        print(f"[{status}] {case['desc']} -> street1='{res.street1}', street2='{res.street2}', city='{res.city}', state='{res.state}', zip='{res.postal_code}'")

    print(f"Adversarial Input Summary: {passed_count}/{len(cases)} passed.")
    return passed_count == len(cases)


def test_cli_piped_stream():
    print("=" * 80)
    print("TEST 4: CLI PIPED STREAM STRESS TESTING")
    print("=" * 80)

    cli_path = sys.executable
    cmd_base = [cli_path, "-m", "address_standardizer.cli"]

    # 1. Piped table format
    input_text = (
        "100 Main St, New York, NY 10001\n"
        "\n"  # blank line
        "   \t   \n"  # whitespace line
        "PSC 1004, BOX 500, APO, AE 09724\n"
        "MALFORMED_LINE_WITHOUT_COMMAS\n"
        "123 Calle Niña, San Juan, PR 00901\n"
    )

    p = subprocess.run(cmd_base + ["--format", "table"], input=input_text, text=True, capture_output=True)
    if p.returncode != 0:
        print(f"FAILED CLI --format table: rc={p.returncode}, stderr={p.stderr}")
        return False
    print("PASS: CLI table output generated:")
    print("\n".join(p.stdout.strip().split("\n")[:10]))

    # 2. Piped CSV format
    p_csv = subprocess.run(cmd_base + ["--format", "csv"], input=input_text, text=True, capture_output=True)
    if p_csv.returncode != 0:
        print(f"FAILED CLI --format csv: rc={p_csv.returncode}, stderr={p_csv.stderr}")
        return False
    csv_lines = [line for line in p_csv.stdout.strip().split("\n") if line]
    # Verify header occurs exactly once
    header_count = sum(1 for line in csv_lines if "street1" in line and "city" in line)
    if header_count != 1:
        print(f"FAILED CLI --format csv header count: {header_count} (expected 1)")
        return False
    print(f"PASS: CLI CSV output generated ({len(csv_lines)} lines, 1 header):")
    print("\n".join(csv_lines[:5]))

    # 3. Piped JSON format
    p_json = subprocess.run(cmd_base + ["--format", "json"], input=input_text, text=True, capture_output=True)
    if p_json.returncode != 0:
        print(f"FAILED CLI --format json: rc={p_json.returncode}, stderr={p_json.stderr}")
        return False
    # Validate each line is valid json
    json_lines = [line for line in p_json.stdout.strip().split("\n") if line]
    for jl in json_lines:
        try:
            json.loads(jl)
        except Exception as e:
            print(f"FAILED CLI --format json line is invalid JSON: {jl!r}: {e}")
            return False
    print(f"PASS: CLI JSON output generated ({len(json_lines)} valid JSON lines).")

    # 4. Large scale piped stream (5,000 lines)
    print("Testing 5,000 piped lines to CLI...")
    large_input = "\n".join(f"{i} Main St, Suite {i % 100}, Springfield, IL 6270{i % 10}" for i in range(5000))
    t0 = time.perf_counter()
    p_large = subprocess.run(cmd_base + ["--format", "csv"], input=large_input, text=True, capture_output=True)
    t_elapsed = time.perf_counter() - t0
    if p_large.returncode != 0:
        print(f"FAILED large CLI run: {p_large.stderr}")
        return False
    out_lines = [line for line in p_large.stdout.strip().split("\n") if line]
    print(f"PASS: 5,000 lines streamed through CLI in {t_elapsed:.2f}s (rate: {5000 / t_elapsed:.1f} lines/s, output lines: {len(out_lines)}).")

    return True


def test_batch_streaming_memory_safety():
    print("=" * 80)
    print("TEST 5: BATCH STREAMING MEMORY SAFETY (RSS < 100MB)")
    print("=" * 80)

    gc.collect()
    init_rss = get_current_rss_mb()
    print(f"Initial Baseline RSS: {init_rss:.2f} MB")

    # Generate test files in memory/disk
    tmp_jsonl_in = "/tmp/challenger_stress_in.jsonl"
    tmp_jsonl_out = "/tmp/challenger_stress_out.jsonl"
    tmp_csv_in = "/tmp/challenger_stress_in.csv"
    tmp_csv_out = "/tmp/challenger_stress_out.csv"

    n_records = 30_000
    print(f"Generating {n_records:,} synthetic records for JSONL and CSV...")

    with open(tmp_jsonl_in, "w", encoding="utf-8") as f_jsonl, \
         open(tmp_csv_in, "w", encoding="utf-8", newline="") as f_csv:
        csv_writer = csv.writer(f_csv)
        csv_writer.writerow(["street1", "street2", "city", "state", "postal_code", "country"])
        for i in range(n_records):
            s1 = f"{i + 1} Main St"
            s2 = f"Suite {i % 500}"
            city = "New York"
            state = "NY"
            postal = f"1000{(i % 9) + 1}"
            country = "USA"

            f_jsonl.write(json.dumps({
                "street1": s1,
                "street2": s2,
                "city": city,
                "state": state,
                "postal_code": postal,
                "country": country
            }) + "\n")

            csv_writer.writerow([s1, s2, city, state, postal, country])

    # --- Test 5A: stream_standardize_jsonl ---
    print("\n--- Subtest 5A: stream_standardize_jsonl ---")
    t0 = time.perf_counter()
    n_proc_jsonl = stream_standardize_jsonl(tmp_jsonl_in, tmp_jsonl_out, chunk_size=5000, max_workers=2)
    t_jsonl = time.perf_counter() - t0
    rss_after_jsonl = get_current_rss_mb()
    print(f"Processed {n_proc_jsonl:,} JSONL rows in {t_jsonl:.2f}s ({n_proc_jsonl / t_jsonl:,.1f} rows/s)")
    print(f"RSS after JSONL: {rss_after_jsonl:.2f} MB (Delta: {rss_after_jsonl - init_rss:.2f} MB)")
    if rss_after_jsonl > 100.0:
        print(f"FAILED: RSS exceeded 100MB ceiling ({rss_after_jsonl:.2f} MB > 100.0 MB)")
        return False
    print("PASS: JSONL streaming memory is strictly < 100MB.")

    # --- Test 5B: stream_standardize_csv ---
    print("\n--- Subtest 5B: stream_standardize_csv ---")
    t0 = time.perf_counter()
    n_proc_csv = stream_standardize_csv(tmp_csv_in, tmp_csv_out, chunk_size=5000, max_workers=2)
    t_csv = time.perf_counter() - t0
    rss_after_csv = get_current_rss_mb()
    print(f"Processed {n_proc_csv:,} CSV rows in {t_csv:.2f}s ({n_proc_csv / t_csv:,.1f} rows/s)")
    print(f"RSS after CSV: {rss_after_csv:.2f} MB (Delta: {rss_after_csv - init_rss:.2f} MB)")
    if rss_after_csv > 100.0:
        print(f"FAILED: RSS exceeded 100MB ceiling ({rss_after_csv:.2f} MB > 100.0 MB)")
        return False
    print("PASS: CSV streaming memory is strictly < 100MB.")

    # --- Test 5C: batch_standardize generator stream ---
    print("\n--- Subtest 5C: batch_standardize lazy generator (50,000 items) ---")
    def gen_addresses(n):
        for i in range(n):
            if i % 2 == 0:
                yield f"{i + 1} Elm St, Apt {i % 20}, Chicago, IL 60601"
            else:
                yield {
                    "address": f"{i + 1} Oak Ave",
                    "suite": f"Ste {i % 100}",
                    "city": "Dallas",
                    "state": "TX",
                    "zip": f"7500{(i % 9) + 1}",
                }

    t0 = time.perf_counter()
    batch_count = 0
    max_rss_seen = init_rss
    for item in batch_standardize(gen_addresses(50_000), batch_size=1000):
        batch_count += 1
        if batch_count % 10000 == 0:
            cur_rss = get_current_rss_mb()
            if cur_rss > max_rss_seen:
                max_rss_seen = cur_rss
    t_batch = time.perf_counter() - t0
    rss_after_batch = get_current_rss_mb()
    print(f"Processed {batch_count:,} items via batch_standardize in {t_batch:.2f}s ({batch_count / t_batch:,.1f} items/s)")
    print(f"Peak RSS seen during batch: {max_rss_seen:.2f} MB, Final RSS: {rss_after_batch:.2f} MB")
    if max_rss_seen > 100.0:
        print(f"FAILED: Peak RSS during batch_standardize exceeded 100MB ceiling ({max_rss_seen:.2f} MB > 100.0 MB)")
        return False
    print("PASS: batch_standardize memory is strictly < 100MB.")

    # Cleanup temp files
    for p in [tmp_jsonl_in, tmp_jsonl_out, tmp_csv_in, tmp_csv_out]:
        if os.path.exists(p):
            os.remove(p)

    return not (max_rss_seen > 100.0)


def test_scalar_type_resilience():
    print("=" * 80)
    print("TEST 6: NON-STRING SCALAR TYPES RESILIENCE (JSON numeric postal codes / street numbers)")
    print("=" * 80)

    # 6A: batch_standardize with numeric postal code
    passed_batch = False
    try:
        list(batch_standardize([{"street": "123 Main St", "city": "Dallas", "state": "TX", "zip": 75001}]))
        print("PASS: batch_standardize handled integer zip code.")
        passed_batch = True
    except Exception as e:
        print(f"FAILED: batch_standardize crashed on integer zip code: {type(e).__name__}: {e}")

    # 6B: stream_standardize_jsonl with numeric postal code
    passed_jsonl = False
    tmp_in = "/tmp/challenger_scalar_test_in.jsonl"
    tmp_out = "/tmp/challenger_scalar_test_out.jsonl"
    try:
        with open(tmp_in, "w", encoding="utf-8") as f:
            f.write(json.dumps({"street": "123 Main St", "city": "Dallas", "state": "TX", "postal_code": 75001}) + "\n")
        stream_standardize_jsonl(tmp_in, tmp_out)
        print("PASS: stream_standardize_jsonl handled integer postal_code.")
        passed_jsonl = True
    except Exception as e:
        print(f"FAILED: stream_standardize_jsonl crashed on integer postal_code: {type(e).__name__}: {e}")
    finally:
        for p in [tmp_in, tmp_out]:
            if os.path.exists(p):
                os.remove(p)

    return passed_batch and passed_jsonl


def main():
    print("=" * 80)
    print("    CHALLENGER 5.1 EMPIRICAL ADVERSARIAL VERIFICATION SUITE")
    print("=" * 80)

    t_start = time.perf_counter()

    p1 = test_public_invariants()
    p2 = test_pure_python_fallback()
    p3 = test_adversarial_inputs()
    p4 = test_cli_piped_stream()
    p5 = test_batch_streaming_memory_safety()
    p6 = test_scalar_type_resilience()

    t_total = time.perf_counter() - t_start
    print("=" * 80)
    print("                     FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Test 1: Public Invariants (14 keys)       : {'PASS' if p1 else 'FAIL'}")
    print(f"Test 2: Pure Python Fallback Core        : {'PASS' if p2 else 'FAIL'}")
    print(f"Test 3: Adversarial Input Variations     : {'PASS' if p3 else 'FAIL'}")
    print(f"Test 4: CLI Piped Stream Stress          : {'PASS' if p4 else 'FAIL'}")
    print(f"Test 5: Batch Streaming Memory (<100MB)  : {'PASS' if p5 else 'FAIL'}")
    print(f"Test 6: Scalar Type Resilience           : {'PASS' if p6 else 'FAIL'}")
    print(f"Total Execution Time: {t_total:.2f}s")
    print("=" * 80)

    all_ok = p1 and p2 and p3 and p4 and p5 and p6
    if all_ok:
        print("OVERALL VERDICT: APPROVE")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()

