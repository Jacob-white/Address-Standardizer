"""
Stage 3 Stress & Memory Limit Testing Suite.
============================================
Validates Blueprint Section 6.3.3:
  - Streaming pipeline processes 10,000+ records with constant bounded RSS growth.
  - Memory ceiling: delta RSS < 30.0 MB across streaming batch execution.
"""

import csv
import os

import tempfile

from address_standardizer.batch import stream_standardize_csv


from address_standardizer._memory import current_rss_mb  # noqa: E402


def get_rss_mb() -> float:
    """Returns current process Resident Set Size in MB."""
    return current_rss_mb()


def test_streaming_10k_records_bounded_memory_growth():
    """
    Generates 10,000 synthetic multinational records and processes them via
    stream_standardize_csv with chunk_size=2000.
    Verifies that memory growth stays strictly under 30.0 MB.
    """
    multinational_templates = [
        ("100 Main St", "Suite 400", "New York", "NY", "10001", "USA"),
        ("15 High Street", "Flat 2", "Leeds", "", "LS6 2AA", "United Kingdom"),
        ("100 King Street West", "Suite 400", "Toronto", "ON", "M5X 1A9", "Canada"),
        ("Musterstraße 12", "", "Berlin", "", "10115", "Germany"),
        ("142 Boulevard Saint-Germain", "", "Paris", "", "75006", "France"),
        ("Keizersgracht 421", "Apt B", "Amsterdam", "", "1016 EK", "Netherlands"),
        ("Calle Mayor 45", "2º B", "Madrid", "", "28013", "Spain"),
        ("Av. Insurgentes Sur 1602", "Int 401", "Ciudad de México", "CDMX", "03940", "Mexico"),
        ("Ugland House, South Church St", "PO Box 309", "George Town", "", "KY1-1104", "Cayman Islands"),
        ("71-75 Shelton Street", "", "London", "", "WC2H 9JQ", "United Kingdom"),
    ]

    total_records = 10000

    with tempfile.TemporaryDirectory() as tmp_dir:
        input_csv = os.path.join(tmp_dir, "stress_input_10k.csv")
        output_csv = os.path.join(tmp_dir, "stress_output_10k.csv")

        # Write 10k records
        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            for i in range(total_records):
                tpl = multinational_templates[i % len(multinational_templates)]
                writer.writerow([
                    str(i + 1),
                    tpl[0],
                    tpl[1],
                    tpl[2],
                    tpl[3],
                    tpl[4],
                    tpl[5],
                ])

        # Baseline RSS before streaming execution
        initial_rss = get_rss_mb()

        processed_count = stream_standardize_csv(
            input_path=input_csv,
            output_path=output_csv,
            chunk_size=2000,
            max_workers=1,
            include_confidence=True,
        )

        final_rss = get_rss_mb()
        delta_rss = final_rss - initial_rss

        assert processed_count == total_records, f"Expected {total_records} records, got {processed_count}"
        assert os.path.exists(output_csv)

        # Verify output CSV row count
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == total_records

        # Memory bound check: growth must be < 30.0 MB
        assert delta_rss < 30.0, f"Memory growth exceeded bound: {delta_rss:.2f} MB >= 30.0 MB"
