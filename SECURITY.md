# Security Policy — Address Standardizer 📍

At **Address Standardizer**, security, data privacy, and defensive engineering are foundational architectural pillars. Owned and maintained by **HobbyHabbit LLC** under the **MIT License**, Address Standardizer is a high-throughput, universal multi-national address standardization, offline spatial rooftop geocoding, and cross-border corporate entity resolution platform.

This document outlines our security policies, vulnerability reporting procedures, threat model, defensive architecture, and configuration best practices for developers and enterprise integrators.

---

## 1. Supported Versions

We provide security patches, bug fixes, and vulnerability reviews for the following versions:

| Version | Supported | Status |
| :--- | :--- | :--- |
| `3.x` (Current: `3.3.0`) | :white_check_mark: | Current Active Production (Full Security Support) |
| `2.x` | :white_check_mark: | Critical Security Fixes Only |
| `< 2.0.0` | :x: | Unsupported — Please upgrade immediately |

---

## 2. Reporting a Vulnerability

We deeply appreciate the efforts of security researchers, system administrators, and developers in identifying potential security vulnerabilities. We strictly adhere to **Coordinated Vulnerability Disclosure (CVD)** principles.

### A. How to Report
- **Email**: Send vulnerability reports directly to `security@hobbyhabbit.com`, `support@hobbyhabbit.com`, and `jake@hobbyhabbit.com`.
- **Subject Line**: `[SECURITY VULNERABILITY] Address-Standardizer — <Brief Description>`
- **GitHub Private Vulnerability Reporting**: You may also report vulnerabilities privately via GitHub's [Advisory Submission Portal](https://github.com/Jacob-white/Address-Standardizer/security/advisories/new).

### B. What to Include
To help our security team triage and remediate issues rapidly, please include:
1. **Description**: Clear explanation of the vulnerability, attack vector, and potential impact.
2. **Component Affected**: Specify affected modules (e.g., `_address_standardizer_rs`, `spatial.py`, `standardizer.py`, `batch.py`, `registry.py`, `cache.py`).
3. **Proof-of-Concept (PoC)**: Minimal reproducible Python snippet, curl payload, or raw address string triggering unexpected behavior.
4. **Environment**: Python version, architecture (x86_64 / aarch64), OS, and whether native Rust FFI or pure-Python fallback is active.

### C. Response SLA
- **Initial Acknowledgment**: Within **24 hours** of receipt.
- **Triage & Severity Assessment**: Within **48 hours**.
- **Remediation & Patch Deployment**: Critical issues are prioritized for patch release within **7 days**.
- **Coordinated Public Disclosure**: We follow a standard 90-day disclosure timeline, allowing users sufficient time to deploy updates before details are made public.

> [!IMPORTANT]
> **Please do NOT file public GitHub issues for suspected security vulnerabilities.** Always use private communication channels to protect downstream users and production systems.

---

## 3. Threat Model & Defense-in-Depth Architecture

Address Standardizer operates at the boundary of external, untrusted user input and internal enterprise data platforms. It defends against five core vulnerability classes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                               │
│           (HobbyHabbit, Firm Network, Batch ETL Pipelines)             │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│            INPUT NORMALIZATION & UNICODE SANITIZATION                  │
│  - NFKD Diacritic Regularization     - ReDoS-Safe Compiled Regexes     │
│  - Strict Null-Byte & UTF-8 Clamping - Delimiter Injection Defense     │
│  - Universal 249-Country Parsing     - Multi-Script Boundary Isolation │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│              MEMORY SAFETY & NATIVE FFI DISPATCH LAYER                 │
│  - Rust DFA/SIMD Acceleration Core   - Panic-Safe PyO3 Boundaries      │
│  - Bounded Memory Buffer (< 35MB)    - Zero-Buffer-Overflow Guarantees │
│  - Pure-Python Fallback Core         - 100% Bit-for-Bit Key Equivalence│
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│            AIR-GAPPED OFFLINE SPATIAL & GEOCODING ENGINE               │
│  - Zero Network Egress / No SSRF     - Parameterized SQLite R*Tree     │
│  - Pure-Python Uber H3 Res 10 Cell   - Bounding Box Query Limiters     │
│  - 4-Stage Resolution Cascade        - Air-Gapped Centroid Fallbacks   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│            CORPORATE TRANSPARENCY & ANTI-FRAUD INVARIANTS              │
│  - Multi-Tenant Skyscraper Suite     - Private Residence Protection    │
│  - Formation Hub Co-Location Guard   - Offshore Secrecy Flagging       │
│  - Immutable Stewardship Audit Ledger- Salted/Deterministic Hash Keys  │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1. Input Normalization & ReDoS Prevention (`address_standardizer/_patterns.py`, `international.py`)
- **Regular Expression Denial of Service (ReDoS) Defense**: All regular expressions used for address parsing, postal code extraction, and directional normalization are pre-compiled, bounded, and audited for catastrophic backtracking.
- **Unicode NFKD Diacritic Normalization**: Accented characters (e.g. `é`, `ñ`, `ü`) are deterministically separated and decomposed, eliminating homoglyph and normalization-evasion attacks while preserving human-readable representations.
- **Null-Byte & Control Character Scrubbing**: Raw inputs containing embedded null bytes (`\x00`), carriage return injections, or terminal control sequences are stripped prior to parsing or batch writing.

### 3.2. Memory Safety & FFI Isolation (`address_standardizer/_native_dispatch.py`, `src/lib.rs`)
- **Rust Native Acceleration (`_address_standardizer_rs`)**: The compiled FFI core uses Rust's memory safety guarantees, eliminating memory corruption risks such as buffer overflows, use-after-free, and dangling pointers.
- **Panic Boundary Safety**: All native Rust PyO3 entry points catch panics gracefully and translate them into typed Python exceptions (`ValueError` / `RuntimeError`), preventing process segmentation faults.
- **Throttled Memory Footprint**: Streaming chunk processors (`stream_standardize_csv`, `buffered_chunk_generator`) pre-allocate record slots and enforce strict worker memory constraints (< 35 MB RSS) to guard against memory exhaustion (OOM) denial-of-service attacks.
- **Pure-Python Equivalent Fallback**: When native binaries are unavailable or disabled, the pure-Python acceleration core (`_pure_python_core.py`) executes with 100% bit-for-bit key equivalence and identical safety invariants.

### 3.3. Air-Gapped Offline Spatial Execution & SSRF Immunity (`address_standardizer/spatial.py`, `geocoder.py`)
- **Zero External Network Egress**: The spatial resolution engine (`SpatialEngine`, `OfflineReferenceIndex`) executes 100% offline. No external HTTP/HTTPS calls are made to commercial geocoding providers (Google Maps, Smarty, Loqate), ensuring total immunity to Server-Side Request Forgery (SSRF) and zero egress data leaks.
- **SQL Injection Prevention in Spatial Lookups**: All lookups against SQLite `R*Tree` spatial indexes (`rtree_nodes`) and persistent reference caches use strict parameterized SQL bindings (`?`).
- **Spatial Search Boundary Caps**: Bounding-box expansion radiuses are clamped to prevent unbounded index scans or spatial denial-of-service queries.

### 3.4. Corporate Transparency & Anti-Fraud Invariants (`address_standardizer/registry.py`)
Address Standardizer enforces three mandatory anti-fraud invariants under FinCEN Corporate Transparency Act (CTA/BOI) rules:
1. **Multi-Tenant Skyscraper Suite Isolation**: In high-density commercial office buildings (e.g., 28 Liberty St, 245 Park Ave, 1209 Orange St), an address only flags as a formation agent or service hub if the specific suite or floor matches the registered agent.
2. **Private Residence Protection**: Commercial corporate entities cannot be automatically merged into residential properties without verified corporate records.
3. **Formation Hub Co-Location Isolation**: Two distinct corporate entities registered at the same registered agent address cannot be merged into a single entity without secondary unit and corporate identifier confirmation.

### 3.5. Data Governance & PII Redaction (`address_standardizer/audit.py`, `models.py`)
- **Deterministic Entity Clustering Keys**: Addresses generate cryptographic-grade deterministic matching keys (`normalized_address_key`, `building_key`, `generate_phonetic_address_key`) allowing record deduplication and cross-border linking without transmitting cleartext personally identifiable information (PII).
- **Audit Ledger Immutability**: The `StewardshipAuditLedger` stores data quality interventions and corporate secrecy alerts in an append-only SQLite store configured with Write-Ahead Logging (WAL) and integrity checkpoints.

---

## 4. Developer Configuration & Security Profiles

Address Standardizer provides environment variable controls for zero-code configuration in containerized or air-gapped environments:

| Environment Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `AS_DISABLE_NATIVE` | `bool` | `false` | Force execution via pure-Python core for hardened environments |
| `AS_CACHE_DIR` | `str` | `~/.cache/address_standardizer` | Sandboxed directory for persistent L2 SQLite cache |
| `AS_CACHE_MAX_MEMORY_ITEMS` | `int` | `10000` | In-memory L1 LRU cache item ceiling |
| `AS_SPATIAL_DB_PATH` | `str` | `None` | Path to verified offline SQLite R*Tree spatial database |
| `AS_AUDIT_LEDGER_PATH` | `str` | `None` | Destination for tamper-evident stewardship audit database |
| `AS_MAX_BATCH_CHUNK_SIZE` | `int` | `5000` | Maximum record chunk size for memory-bounded streaming |
| `AS_LOG_PII` | `bool` | `false` | When `false`, suppresses raw street numbers and names in log outputs |

---

## 5. Security Best Practices for Integrators

When embedding Address Standardizer into web services, batch ETL workflows, or compliance engines:

1. **Deploy in Air-Gapped Enclaves**:
   Address Standardizer is designed to run in air-gapped VPCs or containerized environments with outbound internet access disabled.
2. **Sanitize Batch File Inputs**:
   Validate file size limits and ensure CSV/JSONL files are uploaded from authenticated and authorized sources before dispatching to `stream_standardize_csv` or `stream_standardize_jsonl`.
3. **Protect Audit and Cache Storage**:
   Restrict file permissions (`chmod 600`) on SQLite cache files (`*.db`) and audit ledgers to prevent unauthorized inspection of cached address strings.
4. **Use Deterministic Keys for Cross-Border Matching**:
   When sharing address clusters with external partners, exchange `normalized_address_key` and `building_key` hashes rather than raw PII strings.
5. **Enforce Secondary Unit Matching in Entity Resolution**:
   Always check `can_safely_merge_corporate_entities()` before merging entity profiles that share identical street numbers in high-density metropolitan areas.

---

## 6. Audit & Test Invariants

Address Standardizer enforces zero-compromise testing invariants to maintain security and stability:
- **100.0% Statement Test Coverage** across all core, international, spatial, and delivery modules.
- **Zero Suppression Directives**: No `# pragma: no cover` exemptions on critical security or parsing logic.
- **Property-Based Fuzzing**: Continuous fuzzing batteries powered by `hypothesis` (`tests/fuzzing/`) to verify boundary conditions, unicode permutations, and memory bounds.
- **Dual Golden Benchmarks**: 2,000 ground-truth ground-verified address records (1,000 US domestic + 1,000 multinational) evaluated on every build.

---

## 7. Ownership & License

Address Standardizer is owned and maintained by **HobbyHabbit LLC** and licensed under the **MIT License**. For enterprise licensing inquiries or commercial support, contact `support@hobbyhabbit.com`.

---

*Last Updated: October 2026 — HobbyHabbit LLC Security Team*
