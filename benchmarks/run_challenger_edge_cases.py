"""
Adversarial Edge Case Verification Suite for Address-Standardizer.
Author: challenger_5_2 (teamwork_preview_challenger)
"""

import csv
import json
import os
import subprocess
import sys
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from address_standardizer import standardize_address, batch_standardize, stream_standardize_jsonl
from address_standardizer.batch import stream_standardize_csv
from address_standardizer.models import StandardizedAddress

CANONICAL_14_KEYS = {
    "street1", "street2", "city", "state", "postal_code", "country",
    "normalized_address_key", "building_key", "phonetic_key",
    "address_status", "raw_street_address", "is_us",
    "is_private_residence", "is_registered_agent_hub"
}

def verify_14_keys(addr: StandardizedAddress, label: str) -> bool:
    d = addr.as_dict(include_metadata=False)
    keys = set(d.keys())
    if len(keys) != 14:
        print(f"FAILED [14 keys count] for {label}: got {len(keys)} keys -> {keys}")
        return False
    if keys != CANONICAL_14_KEYS:
        print(f"FAILED [14 keys exact match] for {label}: diff -> {keys.symmetric_difference(CANONICAL_14_KEYS)}")
        return False
    return True

def test_large_integer_scalars():
    print("=" * 80)
    print("EDGE CASE TEST 1: VERY LARGE INTEGER & EXOTIC SCALARS")
    print("=" * 80)

    test_cases = [
        {"desc": "Standard int zip and street", "input": {"postal_code": 90210, "street": 123}},
        {"desc": "Very large integer (64-bit+)", "input": {"street": 12345678901234567890, "city": "Dallas", "state": "TX", "postal_code": 75001}},
        {"desc": "Huge integer 10**25", "input": {"street": "100 Main St", "postal_code": 10**25}},
        {"desc": "Negative integer postal code", "input": {"street": "100 Main St", "city": "Dallas", "state": "TX", "postal_code": -90210}},
        {"desc": "Zero integer postal code", "input": {"street": "100 Main St", "city": "Dallas", "state": "TX", "postal_code": 0}},
        {"desc": "Float postal code & street", "input": {"street": 123.45, "city": "Dallas", "state": "TX", "postal_code": 90210.0}},
        {"desc": "Boolean True/False", "input": {"street": True, "city": "Dallas", "state": False, "postal_code": 75001}},
        {"desc": "All scalar numeric fields", "input": {"street": 100, "street2": 200, "city": 300, "state": 400, "postal_code": 500, "country": 600}},
    ]

    all_ok = True
    for case in test_cases:
        try:
            results = list(batch_standardize([case["input"]]))
            if len(results) != 1:
                print(f"FAILED: Expected 1 result for {case['desc']}, got {len(results)}")
                all_ok = False
                continue
            res = results[0]
            if not verify_14_keys(res, case["desc"]):
                all_ok = False
                continue
            print(f"[PASS] {case['desc']}: street1={res.street1!r}, zip={res.postal_code!r}, key={res.normalized_address_key!r}")
        except Exception as e:
            print(f"[FAIL] {case['desc']} raised exception: {type(e).__name__}: {e}")
            all_ok = False

    return all_ok

def test_empty_whitespace_mixed_streaming():
    print("=" * 80)
    print("EDGE CASE TEST 2: EMPTY, WHITESPACE & MIXED-TYPE JSONL & CSV STREAMING")
    print("=" * 80)

    tmp_jsonl_in = "/tmp/adv_mixed_in.jsonl"
    tmp_jsonl_out = "/tmp/adv_mixed_out.jsonl"
    tmp_csv_in = "/tmp/adv_mixed_in.csv"
    tmp_csv_out = "/tmp/adv_mixed_out.csv"

    # 1. JSONL mixed records with empty lines, whitespace lines, non-string scalars, missing keys
    jsonl_records = [
        {"street1": "100 Main St", "city": "New York", "state": "NY", "postal_code": 10001},
        "",  # blank string line
        "   \t  ",  # whitespace line
        {"postal_code": 90210, "street": 123},
        {"street": "", "city": "   ", "state": "\t\n", "postal_code": None},
        {"unrelated_key": 9999, "another_key": "xyz"},
        {"street1": 555, "street2": None, "city": "Chicago", "state": "IL", "postal_code": "60601"},
        {"street1": "200 Broad St", "postal_code": 19102.5},
        {},
        {"street1": "10 Downing St", "city": "London", "postal_code": "SW1A 2AA", "country": "GBR"},
    ]

    with open(tmp_jsonl_in, "w", encoding="utf-8") as f:
        for r in jsonl_records:
            if isinstance(r, dict):
                f.write(json.dumps(r) + "\n")
            else:
                f.write(r + "\n")

    jsonl_ok = True
    try:
        n_jsonl = stream_standardize_jsonl(tmp_jsonl_in, tmp_jsonl_out, chunk_size=3, max_workers=2)
        print(f"stream_standardize_jsonl processed {n_jsonl} valid lines without crashing.")

        # Verify output records
        with open(tmp_jsonl_out, "r", encoding="utf-8") as f:
            out_lines = [json.loads(line) for line in f if line.strip()]

        print(f"Output JSONL contains {len(out_lines)} valid JSON lines.")
        if len(out_lines) != 8:
            print(f"WARNING: Expected 8 lines, got {len(out_lines)}")

        for idx, out_dict in enumerate(out_lines):
            for req_field in ["std_street1", "std_city", "std_state", "std_postal_code", "std_country", "normalized_address_key", "address_status"]:
                if req_field not in out_dict:
                    print(f"FAILED: Output row {idx} missing required standard field {req_field}: {out_dict}")
                    jsonl_ok = False
        if jsonl_ok:
            print("PASS: JSONL streaming handled empty, whitespace, and mixed-type records cleanly.")
    except Exception as e:
        print(f"FAILED stream_standardize_jsonl on mixed inputs: {type(e).__name__}: {e}")
        jsonl_ok = False

    # 2. CSV mixed records
    csv_rows = [
        ["street1", "street2", "city", "state", "postal_code", "country"],
        ["100 Main St", "", "New York", "NY", "10001", "USA"],
        ["", "", "", "", "", ""],  # empty row
        ["   ", "  ", "  ", " ", " ", ""],  # whitespace row
        ["123 Elm St", "Suite 4B", "Dallas", "TX", "75001", "USA"],
        ["9999", "8888", "7777", "6666", "5555", "USA"],  # numeric strings
        ["", "Apt 1", "Boston", "MA", "02101", "USA"],  # missing street1
        ["10 Downing St", "", "London", "", "SW1A 2AA", "GBR"],  # UK address
    ]

    with open(tmp_csv_in, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for r in csv_rows:
            writer.writerow(r)

    csv_ok = True
    try:
        n_csv = stream_standardize_csv(tmp_csv_in, tmp_csv_out, chunk_size=3, max_workers=2)
        print(f"stream_standardize_csv processed {n_csv} rows successfully.")

        with open(tmp_csv_out, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            out_rows = list(reader)

        print(f"Output CSV contains {len(out_rows)} records.")
        for idx, row in enumerate(out_rows):
            for req_col in ["std_street1", "std_city", "std_state", "std_postal_code", "std_country", "normalized_address_key"]:
                if req_col not in row:
                    print(f"FAILED: Output CSV row {idx} missing required column {req_col}")
                    csv_ok = False
        if csv_ok:
            print("PASS: CSV streaming handled empty, whitespace, and mixed rows cleanly.")
    except Exception as e:
        print(f"FAILED stream_standardize_csv on mixed inputs: {type(e).__name__}: {e}")
        csv_ok = False

    for p in [tmp_jsonl_in, tmp_jsonl_out, tmp_csv_in, tmp_csv_out]:
        if os.path.exists(p):
            os.remove(p)

    return jsonl_ok and csv_ok

def test_piped_cli_streams():
    print("=" * 80)
    print("EDGE CASE TEST 3: PIPED CLI STREAMS (`cat ... | address-standardizer`)")
    print("=" * 80)

    cli_exec = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "address-standardizer"))

    # 3.1 Piped text with various delimiters, empty lines, and non-ASCII chars
    test_data = (
        "100 Main St, New York, NY 10001\n"
        "\n"
        "   \n"
        "742 Evergreen Terrace, Springfield, OR 97477\n"
        "Calle Mayor 45, 2º B, Madrid, 28013, Spain\n"
        "Musterstraße 12, 10115 Berlin, Germany\n"
        "PO Box 999, Honolulu, HI 96801\n"
        "123 Main St\n"
        "GARBAGE_NO_DELIMITERS_1234567\n"
    )

    formats = ["table", "csv", "json"]
    all_formats_ok = True
    for fmt in formats:
        p = subprocess.run(
            [cli_exec, "--format", fmt],
            input=test_data,
            text=True,
            capture_output=True
        )
        if p.returncode != 0:
            print(f"FAILED CLI pipe --format {fmt}: rc={p.returncode}, stderr={p.stderr}")
            all_formats_ok = False
        else:
            lines = [item_line for item_line in p.stdout.strip().split("\n") if item_line]
            print(f"[PASS] CLI pipe --format {fmt}: returned {len(lines)} non-empty lines.")
            if fmt == "json":
                for jl in lines:
                    try:
                        parsed = json.loads(jl)
                        if "street1" not in parsed or "city" not in parsed:
                            print(f"FAILED: CLI JSON output missing standard keys: {jl}")
                            all_formats_ok = False
                    except Exception as e:
                        print(f"FAILED invalid JSON line: {jl}: {e}")
                        all_formats_ok = False

    # 3.2 Pipe with large payload (10,000 records) using actual shell pipe: `cat file.txt | address-standardizer`
    print("Testing shell piped stream (`cat file.txt | address-standardizer --format json`) with 10,000 records...")
    tmp_piped_file = "/tmp/challenger_large_pipe.txt"
    with open(tmp_piped_file, "w", encoding="utf-8") as f:
        for i in range(10000):
            f.write(f"{i} Market St, Ste {i % 50}, San Francisco, CA 94105\n")

    t0 = time.perf_counter()
    shell_cmd = f"cat {tmp_piped_file} | {cli_exec} --format json"
    p_pipe = subprocess.run(
        shell_cmd,
        shell=True,
        text=True,
        capture_output=True
    )
    elapsed = time.perf_counter() - t0
    if p_pipe.returncode != 0:
        print(f"FAILED 10,000 piped records: {p_pipe.stderr}")
        pipe_ok = False
    else:
        out_lines = [item_line for item_line in p_pipe.stdout.strip().split("\n") if item_line]
        print(f"PASS: 10,000 records shell-piped in {elapsed:.2f}s ({10000 / elapsed:.1f} rec/s, got {len(out_lines)} lines).")
        pipe_ok = (len(out_lines) == 10000)

    if os.path.exists(tmp_piped_file):
        os.remove(tmp_piped_file)

    return all_formats_ok and pipe_ok

def test_14_keys_comprehensive_invariant():
    print("=" * 80)
    print("EDGE CASE TEST 4: COMPREHENSIVE 14-KEYS INVARIANT RIGOROUS AUDIT")
    print("=" * 80)

    varied_inputs = [
        # Normal US
        "100 Main St, New York, NY 10001",
        "500 5th Ave Apt 12B, New York, NY 10110",
        # Non-US
        "10 Downing St, Westminster, London SW1A 2AA, UK",
        "123 rue de Rivoli, 75001 Paris, France",
        "Musterstraße 12, 10115 Berlin, Germany",
        "100 Queen St W, Toronto, ON M5H 2N2, Canada",
        "Av. Insurgentes Sur 1602, Crédito Constructor, Benito Juárez, 03940 Ciudad de México, CDMX, Mexico",
        "1 Chome-1-2 Oshiage, Sumida City, Tokyo 131-0045, Japan",
        "George Town, Grand Cayman KY1-1102, Cayman Islands",
        # Military
        "PSC 1004, BOX 500, APO, AE 09724",
        "UNIT 1234 BOX 5678, FPO, AP 96606",
        "CMR 411 BOX 2000, DPO, AA 34004",
        # Territories
        "URB LAS GLADIOLAS, 123 CALLE A, SAN JUAN, PR 00926",
        "Cond El Centro I Ste 800, San Juan, PR 00918",
        # PO Box & Rural
        "PO BOX 100, CHICAGO, IL 60601",
        "RR 1 BOX 12, BLUFFS, IL 62621",
        "HC 3 BOX 10, TAOS, NM 87571",
        # Malformed / Edge
        "",
        "   ",
        "123",
        "JUSTACITYNAME",
        "!@#$%^&*()_+",
        "\n\r\t",
        "1234567890" * 10,
    ]

    all_ok = True
    for raw in varied_inputs:
        res = standardize_address(raw)
        if not verify_14_keys(res, f"raw={raw!r:.30}"):
            all_ok = False

    # Also test manual StandardizedAddress instantiation
    manual_addr = StandardizedAddress(
        street1="123 MAIN ST",
        street2="",
        city="ANYTOWN",
        state="TX",
        postal_code="12345",
        country="USA",
        normalized_address_key="123 MAIN ST||ANYTOWN|TX|12345|USA",
        address_status="standardized",
        raw_street_address="123 Main St",
        is_us=True
    )
    if not verify_14_keys(manual_addr, "Manual StandardizedAddress"):
        all_ok = False
    else:
        print("[PASS] Manually constructed StandardizedAddress has exactly 14 keys.")

    return all_ok

def main():
    print("=" * 80)
    print("ADVERSARIAL EDGE CASE RE-VERIFICATION FOR CHALLENGER 5.2")
    print("=" * 80)

    e1 = test_large_integer_scalars()
    e2 = test_empty_whitespace_mixed_streaming()
    e3 = test_piped_cli_streams()
    e4 = test_14_keys_comprehensive_invariant()

    print("=" * 80)
    print("EDGE CASE TEST SUMMARY")
    print("=" * 80)
    print(f"Edge Test 1: Very Large Integer & Exotic Scalars : {'PASS' if e1 else 'FAIL'}")
    print(f"Edge Test 2: Empty/Whitespace/Mixed Streaming    : {'PASS' if e2 else 'FAIL'}")
    print(f"Edge Test 3: Piped CLI Streams (`cat ... | CLI`) : {'PASS' if e3 else 'FAIL'}")
    print(f"Edge Test 4: Comprehensive 14-Key Invariant      : {'PASS' if e4 else 'FAIL'}")
    print("=" * 80)

    if e1 and e2 and e3 and e4:
        print("ALL ADVERSARIAL EDGE CASES PASSED CLEANLY -> APPROVE")
        sys.exit(0)
    else:
        print("ADVERSARIAL EDGE CASE FAILURE -> FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
