# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) as described in [docs/VERSIONING.md](docs/VERSIONING.md).

The Python package, the npm package and the NuGet package share one version number (see `docs/RELEASING.md`). A release
is refused by CI unless this file has a `## [X.Y.Z]` section for the tagged version.

## [Unreleased]

Changes since 3.3.0 (commit `5fa7862`). Review the "Changed" section before upgrading: several fixes alter outputs that
were previously incorrect, and matching keys for non-Latin addresses changed.

### Added

- Explainable results (opt-in, defaults unchanged): `standardize_address(..., explain=True)` attaches `std.explanation`
  (ordered change records with stable rule ids) and heuristic per-field `std.field_confidence` (optional `calibrator=`);
  `alternatives=N` attaches next-best readings. REST `include_explanation` / `alternatives` request fields and SDK models.
  Steward review page `GET /review` with `GET /v1/audit` and `POST /v1/audit/{id}/override` (off unless API keys are
  configured or `ADDRESS_STANDARDIZER_ENABLE_REVIEW_UI=1`). `apply_manual_override` gained a `review_status` argument.
- Pluggable result-cache backends (`address_standardizer.cache_backends`): `CacheBackend` protocol and an optional
  `RedisCacheBackend` (`pip install "address-standardizer[redis]"`; TTL, key prefix, never breaks standardization on a
  Redis outage). Select with `configure_cache(backend=...)` or `ADDRESS_STANDARDIZER_CACHE_URL`. Default behaviour (L1 LRU +
  SQLite L2) is unchanged. See `docs/performance.md`.
- `address_standardizer.transliterate` (`transliterate`, `std_to_latin`) and `parse --latin`: Latin rendering of Cyrillic and
  Greek built in, any script with the optional `anyascii` package (`[translit]` extra); never invents output.
- `scripts/load_test.py` (stdlib HTTP load test with p50/p95/p99) and `benchmarks/run_profile.py` (cProfile of the mixed path).
- `care_of` field on `StandardizedAddress` (also in the HTTP API, the SDKs and `as_dict(include_metadata=True)`).
- Opt-in `correct_state_from_zip` (API, SDKs, CLI, environment): replaces the state when it contradicts the ZIP and
  reports `WARN_STATE_CORRECTED_FROM_ZIP`. By default a ZIP/state mismatch is still only reported
  (`ERR_ZIP_STATE_MISMATCH`) and never changes the address.
- SDKs: streaming batch with cancellation, inactivity timeouts and per-record errors (`StreamBatchRecords` /
  `StreamBatchRecordsAsync` / `streamBatch`), typed HTTP errors (`APIError` in Go), GET autocomplete with proximity
  parameters, tri-state CMRA/Vacant flags.
- Server: request-body size cap (HTTP 413), `/v1/batch` size cap (413), validated batch payloads (HTTP 400), inline
  per-record error lines in NDJSON streams, switchable API docs.
- `audit-db` tooling and a reviewed golden-data overrides overlay for reproducible benchmark datasets.
- A working `Dockerfile` (non-root, native core included) and a hardened `docker-compose.service.yml` (loopback-only
  port, read-only root filesystem, dropped capabilities).
- CI: SDK contract tests against the server's OpenAPI schema, live-server integration tests for all three SDKs, a
  native-extension parity job that cannot silently skip, a Docker smoke test, and a throughput/memory SLA job.
- Release workflow: tag must be on `main`, build job without credentials, sequential publish from the built artifacts.

### Changed

- Performance: the corporate-registry lookup (run several times per address) no longer compiles a regex per registry entry
  and is memoized; outputs are identical. Measured +33% on cold mixed input (`docs/performance.md`).
- **Python 3.11 or newer is required** (previously the metadata allowed older versions).
- **Matching keys for non-Latin addresses changed.** Latin, Cyrillic and Greek are transliterated; other scripts (CJK,
  Hangul, Arabic, ...) are encoded as `~<hex code point>` instead of being dropped, so different non-Latin streets no
  longer share a key. Persisted keys for such addresses will not match keys produced by 3.3.0.
- Real `h3` is now required; the approximate fallback was removed. Invalid coordinates raise `ValueError`.
- Unresolved geocodes report `null` coordinates (previously `0, 0`) in the server and CLI JSON.
- Fuzzy healing is conservative: valid cities, street names and suffixes are no longer rewritten.
- Only the street-type word is abbreviated in international addresses (street names such as "Al", "Orchard", "Mill" are
  no longer corrupted).
- The native Rust module is slimmed to the Soundex implementation and verified against the Python reference; the Python
  core is the single source of truth. Unmeasured native performance claims were removed from the capabilities.
- The CLI serves on `127.0.0.1` by default; unknown shorthand flags are errors; numeric arguments are validated.
- CORS credentials are allowed only for explicitly configured origins; 500 responses are generic.
- Golden benchmark data was corrected where it had encoded earlier corruptions (for example JE/GG/IM country codes,
  German house-number ranges).
- Dependency security updates: `pyo3` 0.29 (GHSA-36hh-v3qg-5jq4, GHSA-chgr-c6px-7xpp, RUSTSEC-2025-0020), Rust 1.85.

### Fixed

- US: trailing house numbers, Farm-to-Market roads, `Urb` plus unit, floor in the city field, second street line with
  a unit, PO Box spellings, rural routes, dual-line addresses, street words (Front, Upper, Office) no longer treated as
  units, route numbers no longer ordinalized, ZIP+4 with a space.
- Care-of parsing: company names and "Attention" streets, no truncation of `c/o` names, deterministic output.
- International: script detection, Latin America, Romance, German, Nordic, Korean, Hong Kong, Australia, UK/Ireland
  (including `GIR 0AA`), offshore hubs, Canadian PO Box plus suite, single-line `Street, City, Postal, Country` split,
  generic postal-code extraction, stricter postal validators, unified country aliases, country detection from native
  country names.
- ZIP/state: a contradictory ZIP is reported as undeliverable instead of being silently accepted.
- Spatial: antimeridian- and pole-safe radius and bounding-box queries, nearest-first limits, coordinate validation,
  idempotent ingestion, ASCII-only digit parsing, tier-accurate centroid labels, exact street-name matching,
  polygon-centroid precision.
- Server and batch: CPU-bound work off the event loop, bounded metric labels, safe NDJSON splitting, refusal of
  same-file input/output, atomic output, CSV formula neutralization, ragged-row handling, empty-batch handling.
- Cache and audit: LRU recency (strictly increasing stamps so eviction is correct on coarse clocks such as Windows),
  escaped cache keys, unreadable L2 payloads treated as misses, append-only audit ledger with history on override.
- Security: polynomial-backtracking regular expressions removed (CodeQL).
- SDKs: streaming resource cleanup, nullable response types, wire-format fixtures captured from the real server.

## [3.3.0] - 2026-10-07

Baseline for this changelog. Earlier history is available in `git log`.
