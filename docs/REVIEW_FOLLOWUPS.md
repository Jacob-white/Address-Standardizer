# Review follow-ups

Open items from the whole-codebase review. The review's other findings are fixed and committed. Tick items off as they land.

## Spatial and autocomplete

- [x] H3 fallback (`spatial/h3_indexer.py`) was not real H3: removed; `h3` is now a required dependency and the wrapper only returns real H3 values; validate coordinates; add known-vector tests when `h3` is present.
- [x] `autocomplete.py`: exclude records without coordinates when a radius is given.
- [x] `autocomplete.py`: dedupe in `connect_reference_index`.
- [x] `autocomplete.py`: clamp the haversine intermediate value to [0, 1].
- [x] `autocomplete.py`: handle negative `max_results`.
- [x] `calculate_polygon_centroid`: antimeridian handling; skip empty polygon rings.

## Tests and benchmarks

- [x] `benchmarks/run_benchmarks.py::benchmark_accuracy` skips expected keys not in its hard-coded dict (`address_status`, `is_us` are never compared): compare every expected key, fail on unknown ones.
- [x] Mark wall-clock assertions as `perf` (`tests/test_m32*`, `tests/test_autocomplete.py`, `tests/spatial/test_integration.py`, ReDoS timings in `tests/test_phase6*`).
- [x] Make hypothesis fuzz tests deterministic (derandomize / fixed seed).
- [x] Add arrow, polars and duckdb to the dev extras, or fail CI when their tests skip.
- [x] SDK contract test (`tests/test_sdk_contract.py`) only checks names: extend to types, nullability and defaults; make its regex parsers fail loudly when they match nothing.
- [x] H3 tests need known vectors.
- [x] `generate_multinational_golden_dataset.py` does not reproduce the committed JSON: fix it, or document why.

## Docs (verified wrong, high severity)

- [x] `docs/api_reference.md`: Python API names and signatures, REST paths (`/v1/*`), batch limit (10,000, 413), CLI syntax (`parse`, not `standardize`; `batch` positional args; `benchmark` flags).
- [x] `docs/quickstart.md`: almost every snippet fails; fix the curl path and the install extras (`[server]`, `[arrow]`).
- [x] `README.md`: wrong outputs; unclosed code fence (~line 504); false claims ("960+ tests", "100% coverage" (actual ~89.6%), "220,000 rec/sec native SIMD", "bit-for-bit"); wrong CLI flags (`--include-intl`, `spatial ingest`, `audit --summary`); wrong install steps.
- [x] SDK READMEs:
  - TypeScript: `RequestOptions`, `isStreamError`, typed errors, `react` peer dependency.
  - Go: `StreamBatchRecords`, `WithTimeout`, `AutocompleteGetRequest`, `*bool` CMRA/Vacant, `testdata` fixtures.
  - .NET: `StreamBatchRecordsAsync`, nullable flags, `AddressStandardizerRecordException` / `AddressStandardizerException`, `AutocompleteGetAsync`.
- [x] Document `correct_state_from_zip` (param, API field, CLI flag, env var). Streaming library functions only honor the env var.
- [x] Document the env vars: `ADDRESS_STANDARDIZER_MAX_BATCH`, `_MAX_BODY_BYTES`, `_CORS_ORIGINS`, `_DISABLE_DOCS`, `_FORCE_PURE`, `_AUDIT_MAX_ROWS`, `_CORRECT_STATE_FROM_ZIP`.
- [x] Document that the Rust module is Soundex-only.
- [x] `docs/RELEASING.md`.

## International parsing

- [ ] CJK, Hangul and Cyrillic single-line addresses are classified as USA/BGR.
- [ ] Brazil: single-line unit loses the street.
- [ ] Romance/LatAm unit regex has no word boundary and matches street names containing INT/ESC/PISO/STE.
- [ ] Hong Kong: "Central" is peeled off the street.
- [ ] Canada: 4+ part "Street, City, Province, Postal"; "PO Box 123 Stn A" should become `PO BOX 123 STN A`.
- [ ] IE/GB locality drops.
- [ ] Offshore: "Tower 2" reorder; JE/GG/IM PO box + suite; JE/GY/IM single-line country.
- [ ] Multi-part `street2` information loss (FR "Bât.", DE/AU c/o).
- [ ] PO box + unit handling is inconsistent across countries.
- [ ] Two country alias tables disagree (`CountryRegistry` vs `tables.COUNTRY_MAP`); unknown countries default to USA; "N/A" maps to Namibia.
- [ ] Postal validators: NL leading zero, Eircode, BM.
- [ ] AU single-line without a country falls back to USA.
- [ ] German `Str.` abbreviations and house-number ranges.
- [ ] `RE_NUM_FIRST` is quadratic (mitigated by the 600-char field cap).
- [ ] Russian `кв.`; Greek tonos; zero-width characters.
- [ ] `RomanceGrammar` / `LatinAmericaGrammar` registry collision (MEX/COL/ARG/BRA).

## US core

- [x] `enable_fuzzy=False` is not honored in `us_street_parser` (~line 466, `get_fuzzy_suffix` and the recursion).
- [x] RR box comma / `R.R.` normalization.
- [x] Ordinal word floors; `No.` / `Number` units.
- [x] Single-token street + unit duplication (`Acme` + `Suite 500`, lone numbers).
- [x] Dual-address / Urbanization branches lose data.
- [ ] CRF path splits a `St.` prefix.
- [x] `normalize_us_postal_code` with odd lengths.
- [ ] "Paris" with a TX ZIP resolves to FRA.
- [ ] `LocalityOnlyStatus` eq/hash contract (`models.py`).
- [ ] Dead code: `RE_ATTACHED_SEC_UNIT`, unused aliases.
- [ ] **Decision needed:** a hub address is AUTO_PASS but the audit marks it PENDING. Pick one policy.

## Server and CLI

- [x] `arrow.py`: empty batch returns `None`; duplicate columns on re-apply; missing columns silently become null.
- [x] CLI csv output: neutralize formula injection (`cli_formatting._format_csv_row`).
- [x] `parse --enable-geocoding --spatial-db <bad>`: confirm it fails cleanly, not with a traceback.
- [x] Streaming library functions: accept `correct_state_from_zip` as a parameter.

## Found while verifying (open)

- [ ] `St. Louis Ave 100` (trailing house number) is parsed as street `LOUIS AVE ST` + unit `STE 100`.
- [ ] `Urbanization ...` single-line input drops the urbanization name when no street follows.
- [ ] Japanese single-line input: `normalized_address_key` loses city/state and mangles the street.
- [ ] `audit` CLI always uses a fresh in-memory ledger, so it is always empty across invocations (documented, not fixed).
- [ ] `standardize_address("xyz", city="Nowhere")` returns status `standardized` with routing tier MANUAL_STEWARDSHIP.
- [ ] `phonetic_key` for "350 5th Ave" is `350|#5|10118` (odd token).
- [ ] The `benchmark` command's SLA gate fails the mixed-throughput row on slow machines (1,729 rec/s vs a 2,000 target).
- [ ] Verify the GitHub Actions run after pushing `9ef4553` (CI failures were reproduced and fixed locally in Linux containers; not yet confirmed on GitHub).

## Known behavior notes (for the release notes)

- Street-type abbreviation applies only to the type word.
- ZIP/state mismatch keeps the supplied state by default; `correct_state_from_zip` is opt-in.
- Unresolved geocodes serialize null latitude/longitude.
- Batch size and body size limits return 413.
- `serve` binds to 127.0.0.1 by default.
- The Rust module is trimmed to Soundex only.
- Python 3.11 or newer is required.
- Golden datasets were regenerated from engine output where the old expectations encoded bugs.
