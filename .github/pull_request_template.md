## What and why

<!-- One or two sentences. Link the issue if there is one. -->

## Type of change

- [ ] Bug fix
- [ ] New feature or opt-in flag
- [ ] Behaviour change to existing output or keys (describe below, see docs/VERSIONING.md)
- [ ] Docs, CI or tooling only

## Checklist

- [ ] `python -m ruff check .` is clean and `pytest -m "not perf"` passes (coverage gate is 100%)
- [ ] Tests added or updated (golden data changes go through the reviewed overrides file)
- [ ] `CHANGELOG.md` updated under `[Unreleased]` for user-visible changes
- [ ] API/SDK field changes keep `tests/test_sdk_contract.py` and the three SDKs in sync
- [ ] Docs updated where behaviour changed
- [ ] Test data and examples contain **no real personal addresses** (use synthetic or public-landmark addresses)

## Compatibility notes

<!-- Anything that changes outputs, matching keys, error codes or defaults. "None" if nothing. -->
