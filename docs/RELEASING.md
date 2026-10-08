# Releasing

Releases are driven by `.github/workflows/release.yml` (push a `vX.Y.Z` tag). This page lists the one-time
account setup that cannot be done from the repository, and what has already been verified locally.

## One-time setup (needs an account owner)

| Target | What to create | Where it is used |
| :--- | :--- | :--- |
| **GitHub** | Environment named `release` with required reviewers | every publish job waits on it |
| **PyPI** | Project `address-standardizer`; add this repo + `release.yml` + environment `release` as a *trusted publisher* | `pypi` job (no token needed) |
| **npm** | Organization/scope `@address-standardizer`; an automation token stored as secret `NPM_TOKEN` | `npm` job |
| **NuGet** | Reserve package id `AddressStandardizer.Client`; API key stored as secret `NUGET_API_KEY` | `nuget` job |
| **Go** | Nothing to create; push a `sdks/go/v1.Y.Z` tag | consumers run `go get github.com/Jacob-white/Address-Standardizer/sdks/go` |

If the `@address-standardizer` npm scope or the NuGet id is unavailable, rename `name` in
`sdks/typescript/package.json` / `<PackageId>` in `sdks/dotnet/AddressStandardizer.Client.csproj` and update the
install commands in `sdks/README.md`.

## Per-release checklist

1. Bump the version in `pyproject.toml`, `address_standardizer/__init__.py`, `sdks/typescript/package.json`
   and `sdks/dotnet/AddressStandardizer.Client.csproj`; run `python scripts/check_versions.py`.
2. Merge to `main` and wait for CI to pass (Python 3.11/3.13 on Linux and Windows, Rust, and the SDK job).
3. Tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`. Approve the `release` environment when prompted.
4. For a Go release, push `sdks/go/v1.Y.Z` separately.

## Verified locally (3.3.0)

- `python -m build` produces a wheel and sdist that pass `twine check`; the wheel contains every module.
- `npm pack --dry-run` in `sdks/typescript` packs only `dist/` plus `package.json` (18 files).
- Not verifiable here: `dotnet pack` and `go` (no SDKs installed) and the publish steps themselves.
