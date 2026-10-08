"""Fail unless the Python, npm and NuGet package versions all match (and the git tag, if given).

Usage: python scripts/check_versions.py [vX.Y.Z]
The Go SDK is versioned independently via `sdks/go/vX.Y.Z` tags (Go modules at v2+ need a /vN path suffix).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    versions = {
        "pyproject.toml": re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1),
        "sdks/typescript/package.json": json.loads((ROOT / "sdks/typescript/package.json").read_text(encoding="utf-8"))["version"],
        "sdks/dotnet/AddressStandardizer.Client.csproj": re.search(
            r"<Version>([^<]+)</Version>", (ROOT / "sdks/dotnet/AddressStandardizer.Client.csproj").read_text(encoding="utf-8")
        ).group(1),
    }
    init = (ROOT / "address_standardizer/__init__.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', init)
    if m:
        versions["address_standardizer/__init__.py"] = m.group(1)

    if len(sys.argv) > 1:
        versions["git tag"] = sys.argv[1].lstrip("v")

    for name, v in versions.items():
        print(f"{name}: {v}")
    if len(set(versions.values())) != 1:
        print("Version mismatch", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
