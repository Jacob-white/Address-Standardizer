"""Fail unless the Python, npm and NuGet package versions all match (and the git tag, if given).

Usage: python scripts/check_versions.py [vX.Y.Z [--notes-out FILE]]
With a tag, CHANGELOG.md must also have a non-empty `## [X.Y.Z]` section; --notes-out writes that section to FILE
(used as the GitHub release notes).
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

    args = sys.argv[1:]
    notes_out = None
    if "--notes-out" in args:
        i = args.index("--notes-out")
        notes_out = Path(args[i + 1])
        del args[i : i + 2]
    if args:
        versions["git tag"] = args[0].lstrip("v")

    for name, v in versions.items():
        print(f"{name}: {v}")
    if len(set(versions.values())) != 1:
        print("Version mismatch", file=sys.stderr)
        return 1

    if args:  # a tagged release must have a CHANGELOG entry
        version = args[0].lstrip("v")
        notes = changelog_section(version)
        if notes is None:
            print(f"CHANGELOG.md has no '## [{version}]' section (rename [Unreleased] before tagging)", file=sys.stderr)
            return 1
        if not notes.strip():
            print(f"CHANGELOG.md section [{version}] is empty", file=sys.stderr)
            return 1
        if notes_out is not None:
            notes_out.write_text(notes.strip() + "\n", encoding="utf-8")
        print(f"CHANGELOG.md: section [{version}] found")
    return 0


def changelog_section(version: str) -> str | None:
    """Return the body of the `## [version]` section of CHANGELOG.md, or None when there is no such section."""
    path = ROOT / "CHANGELOG.md"
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = re.compile(r"^## \[" + re.escape(version) + r"\](\s|$)")
    for i, line in enumerate(lines):
        if heading.match(line):
            body = []
            for nxt in lines[i + 1 :]:
                if nxt.startswith("## "):
                    break
                body.append(nxt)
            return "\n".join(body)
    return None


if __name__ == "__main__":
    sys.exit(main())
