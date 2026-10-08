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

## International parsing (done; limitations noted)

- [x] CJK, Hangul and Cyrillic single-line detection and split (`international/scripts.py`).
- [x] Brazil single-line unit; Romance/LatAm unit word boundaries; grammar registry collision (a test now fails if two grammars claim one country).
- [x] Hong Kong "Central" kept in road names; Canada 4-part single line, `PO BOX 123 STN A`, bare `, ON` tail selects Canada.
- [x] IE/GB locality handling; offshore "Tower 2"; JE/GG/IM country detection; PO box + unit uniform across GB/JE/GG/IM/CA/AU/IE/KY/BM/HK/DE/FR.
- [x] Multi-part `street2` (FR "Bât."/"Esc."/"étage") keeps every part.
- [x] Country alias tables unified (registry now includes every `COUNTRY_MAP` name); `N/A`/`none`/`unknown` are "no country"; an unrecognised country is `ZZZ`, not USA.
- [x] Postal validators: NL (no leading zero), Eircode alphabet, Bermuda `AA NN` / `HM <letter>X`.
- [x] AU single line without a country; German `Str.`/`Pl.` expansion and house-number ranges; `RE_NUM_FIRST` made linear.
- [x] Russian `кв.`; Greek tonos in keys; zero-width characters.
- [ ] **Decision needed:** keys are ASCII-only by contract (`test_cjk_grammar_full_width_and_unspaced`), so CJK/Hangul street names fold to digits only and distinct streets can share a `normalized_address_key`. Fixing it means changing that contract.
- [ ] **Decision needed:** `c/o` / care-of text is removed engine-wide (`care_of.strip_care_of`) and the model has no field for it.
- [ ] Bulgarian/Ukrainian grammars keep dots (`БУЛ.`, `ВУЛ.`, `КВ.`) where Russian drops them (shared grammar behaviour, left as is).
- [ ] Hong Kong: "8 Finance Street Central" (no comma) now keeps CENTRAL in the street line.
- [ ] A 5-digit postcode after an Australian state (`NSW 02000`) still falls through to US.
- [ ] UK grammar deliberately keeps `HILL`/`HILLS` unabbreviated (Royal Mail has no abbreviation) although the shared table maps HILL to HL.

## US core (done; limitations noted)

- [x] `enable_fuzzy=False`, RR/HC boxes, `No.`/`Number` units, word-number units/floors, premise-name duplication, two street lines, odd-length ZIPs.
- [x] Dead patterns removed (`RE_ATTACHED_SEC_UNIT` and eight more).
- [x] `LocalityOnlyStatus`: contract documented (equal to both spellings; hash follows `locality_only`).
- [x] Confidence/audit policy: kept as designed and documented. `routing_tier` is parse/deliverability confidence; `review_status` is the stewardship queue, so a registered-agent hub can be AUTO_PASS yet PENDING.
- [x] `phonetic_key` `#5` token is intentional (numbered streets get a `#<n>` token so `2nd` and `42nd` do not collide).
- [x] "Paris" with a Texas ZIP now stays USA.
- [ ] Trailing house numbers (`St. Louis Ave 100`) are not supported by the US parser; it produces a wrong street. Not fixed because moving a trailing number to the front would corrupt `County Road 12` / `Highway 66`.
- [ ] A lone non-numeric street word (`XYZ`) is reported `standardized` (routing tier MANUAL_STEWARDSHIP flags it for review).

## Server and CLI (done)

- [x] Arrow/Polars, CSV formula neutralization, streaming `correct_state_from_zip`, `audit --audit-db` persistence, benchmark SLA scale.

## Verification still outstanding

- [ ] Push and confirm the GitHub Actions run is green (CI failures were reproduced and fixed in Linux containers; Windows jobs not run locally).
- [ ] Line coverage is 92% (not 100%); remaining gaps are mostly error branches in the grammars and CLI.

## Known behavior notes (for the release notes)

- Street-type abbreviation applies only to the type word.
- ZIP/state mismatch keeps the supplied state by default; `correct_state_from_zip` is opt-in.
- Unresolved geocodes serialize null latitude/longitude.
- Batch size and body size limits return 413.
- `serve` binds to 127.0.0.1 by default.
- The Rust module is trimmed to Soundex only.
- Python 3.11 or newer is required.
- Golden datasets were regenerated from engine output where the old expectations encoded bugs.
- `h3` is a required dependency; there is no approximate fallback. Invalid or out-of-range coordinates raise `ValueError` instead of being clamped.
- A country name that cannot be resolved is reported as `ZZZ`, not `USA`; `N/A`, `none`, `unknown` mean "no country given".
- Postal validation is stricter: Dutch codes cannot start with 0, Eircodes must use the Eircode alphabet, Bermuda codes must be `AA NN` (or `HM <letter>X`).
- `normalize_us_postal_code` no longer pads, truncates or invents a ZIP from malformed input (returns the cleaned text with an empty ZIP5).
- Jersey, Guernsey and the Isle of Man now report `JEY`, `GGY`, `IMN` (previously `GBR`), so their keys end in those codes.
- German house-number ranges (`5-7`) stay in street1; `Str.`/`Pl.` expand to `STRASSE`/`PLATZ`.
- CLI: `--audit-db` / `ADDRESS_STANDARDIZER_AUDIT_DB` persist the audit ledger; `parse` no longer forces a default `--country USA`.
