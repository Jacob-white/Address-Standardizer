# Releasing

Releases are driven by `.github/workflows/release.yml`, which runs when a tag matching `vX.Y.Z` (digits only, for
example `v3.3.1`; pre-release suffixes do not match) is pushed. This page describes what the workflow does, the
account setup it expects (which cannot be done from the repository), and the per-release checklist.

## Workflow overview

Jobs run in this order; each job needs the one before it, so a failure stops everything after it:

| Job | What it does | Credentials |
| :--- | :--- | :--- |
| `verify` | Checks out the full history, requires the tagged commit to be an ancestor of `origin/main`, and runs `python scripts/check_versions.py <tag>` | none |
| `ci` | Calls the full `.github/workflows/ci.yml` on the tag (see below) | none |
| `build` | Builds the Python sdist and wheel (`python -m build`, then `twine check`); in `sdks/typescript` runs `npm ci`, `npm test` and `npm pack`; runs `dotnet pack sdks/dotnet/AddressStandardizer.Client.csproj -c Release`; uploads everything as the `release-artifacts` artifact | none |
| `pypi` | Publishes `dist/python/` with `pypa/gh-action-pypi-publish` | `id-token: write` (trusted publishing); environment `release` |
| `npm` | Runs `npm publish --access public --provenance dist/npm/*.tgz` | secret `NPM_TOKEN`, `id-token: write` (provenance); environment `release` |
| `nuget` | Runs `dotnet nuget push "dist/nuget/*.nupkg"` to `https://api.nuget.org/v3/index.json` | secret `NUGET_API_KEY`; environment `release` |

Publishing is sequential: PyPI, then npm, then NuGet. The publish jobs upload the exact files produced by `build`
(downloaded from the `release-artifacts` artifact) rather than rebuilding them. Third-party actions are pinned to commit
SHAs; refresh them deliberately when upgrading.

### Checks that gate a release

- The tagged commit must be reachable from `main`.
- `scripts/check_versions.py` must find the same version in `pyproject.toml`, `sdks/typescript/package.json`,
  `sdks/dotnet/AddressStandardizer.Client.csproj` (`<Version>`), `address_standardizer/__init__.py` (`__version__`, when
  present) and the tag. The Go SDK is not part of this check.
- `ci.yml` must pass on the tag. It contains these jobs:
  - `python`: `ruff check .`, `pytest -m "not perf"` with coverage, then `pytest -m perf` (throughput/memory SLA tests,
    with `ADDRESS_STANDARDIZER_SLA_SCALE=0.6`), on Python 3.11 and 3.13, on Ubuntu and Windows.
  - `rust`: `cargo test --locked` (Rust 1.85.0), builds the native extension with maturin and runs the native/pure
    parity and acceleration tests.
  - `sdks`: `tests/test_sdk_contract.py` (SDK model fields against the server's OpenAPI schema), then starts a live
    server and runs the TypeScript suite (`npm ci`, `npm test`; Node 20), the Go checks (`gofmt -l`, `go vet ./...`,
    `go test ./...`; Go 1.21) and `dotnet test sdks/dotnet/tests/AddressStandardizer.Client.Tests -c Release` (.NET
    8.0.x), all with `ADDRESS_STANDARDIZER_URL=http://127.0.0.1:8000` so the live-server integration tests run.
  - `docker`: builds the image and smoke-tests it (runs as non-root, native core active, `/health` and
    `/v1/standardize` respond).
- In `build`, the npm package is tested again (`npm test`) before it is packed. The NuGet package is packed but no
  .NET tests run in that job; the .NET tests run in `ci`.

## One-time setup (needs an account owner)

The workflow expects these to exist; the repository cannot create them.

| Target | What the workflow needs | Used by |
| :--- | :--- | :--- |
| **GitHub** | An environment named `release` (add required reviewers to gate publishing) | `pypi`, `npm`, `nuget` |
| **PyPI** | Trusted publishing configured for this repository, workflow `release.yml` and environment `release`; no token is read by the workflow | `pypi` |
| **npm** | A token stored as the repository/environment secret `NPM_TOKEN` with permission to publish `@address-standardizer/client` (the package `name` in `sdks/typescript/package.json`) | `npm` |
| **NuGet** | An API key stored as the secret `NUGET_API_KEY` with permission to push package id `AddressStandardizer.Client` | `nuget` |

If a package name is unavailable on its registry, change `name` in `sdks/typescript/package.json` or `<PackageId>` in
`sdks/dotnet/AddressStandardizer.Client.csproj`, and update the install commands in `sdks/README.md` and the SDK READMEs.
The PyPI project name comes from `pyproject.toml`.

## Go SDK

`release.yml` has no Go job and nothing in the workflow publishes the Go module; it is not covered by
`check_versions.py`. The workflow's header comment and `scripts/check_versions.py` state that the Go SDK is released by
pushing a `sdks/go/vX.Y.Z` tag (the module lives in the `sdks/go` subdirectory, and `sdks/README.md` explains why it
stays on `v1`). The `vX.Y.Z` tag filter does not match such tags, so pushing one does not start `release.yml`; the `ci`
workflow's Go job is the only automated check, and it runs on pushes to `main` and on pull requests. Make sure it passed
on the commit you tag. Consumers then run `go get github.com/Jacob-white/Address-Standardizer/sdks/go`, per
`sdks/go/go.mod`.

## Per-release checklist

1. Bump the version in `pyproject.toml`, `address_standardizer/__init__.py`, `sdks/typescript/package.json` and
   `sdks/dotnet/AddressStandardizer.Client.csproj`; run `python scripts/check_versions.py` (add the tag as an argument
   to include it in the comparison).
2. Merge to `main` and wait for CI to pass.
3. Tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`. Approve the `release` environment when prompted; each of
   the `pypi`, `npm` and `nuget` jobs waits on it.
4. For a Go release, push `sdks/go/v1.Y.Z` separately.

If a publish job fails partway, the earlier registries already have the release (publishing is sequential and not
transactional). Registries typically do not allow re-uploading the same version, so fix forward with a new version.
