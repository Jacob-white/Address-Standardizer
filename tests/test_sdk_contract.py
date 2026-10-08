"""
SDK contract tests: the field names in each client SDK must match the server's OpenAPI schema.

Catches drift between `address_standardizer/server.py` (Pydantic models) and the hand-written
TypeScript, Go and .NET models in `sdks/`.
"""

import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from address_standardizer.server import app  # noqa: E402

SDKS = Path(__file__).resolve().parent.parent / "sdks"

# server schema -> (TypeScript interface, Go struct, .NET class)
MODELS = {
    "StandardizeRequest": ("StandardizeRequest", "StandardizeRequest", "StandardizeRequest"),
    "StandardizeResponse": ("StandardizeResponse", "StandardizedAddress", "StandardizedAddress"),
    "AutocompleteRequest": ("AutocompleteRequest", "AutocompleteRequest", "AutocompleteRequest"),
    "AutocompleteSuggestionItem": ("AutocompleteSuggestion", "AutocompleteSuggestion", "AutocompleteSuggestion"),
    "AutocompleteResponse": ("AutocompleteResponse", "AutocompleteResponse", "AutocompleteResponse"),
}

# Fields the server accepts/returns that an SDK deliberately does not model.
SDK_ONLY = {"StandardizedAddress": {"raw_street_address"}}  # Go: optional passthrough


def _schema_fields(name):
    return set(app.openapi()["components"]["schemas"][name]["properties"])


def _block(text, header_re):
    m = re.search(header_re, text)
    assert m, header_re
    depth, i = 0, text.index("{", m.start())
    start = i
    while i < len(text):
        depth += text[i] == "{"
        depth -= text[i] == "}"
        i += 1
        if depth == 0:
            break
    return text[start:i]


def _ts_fields(name):
    text = (SDKS / "typescript/src/types.ts").read_text(encoding="utf-8")
    body = _block(text, rf"export interface {name}\b")
    return set(re.findall(r"^\s{2}(\w+)\??:", body, re.M)) - {"fetch"}


def _go_fields(name):
    text = (SDKS / "go/models.go").read_text(encoding="utf-8")
    body = _block(text, rf"type {name} struct")
    return {t for t in re.findall(r'`json:"([^",]+)', body) if t != "-"}


def _dotnet_fields(name):
    text = (SDKS / "dotnet/Models.cs").read_text(encoding="utf-8")
    body = _block(text, rf"public class {name}\b")
    return set(re.findall(r'\[JsonPropertyName\("([^"]+)"\)\]', body))


@pytest.mark.parametrize("server_name", sorted(MODELS))
@pytest.mark.parametrize("sdk", ["ts", "go", "dotnet"])
def test_sdk_model_matches_server_schema(server_name, sdk):
    ts, go, cs = MODELS[server_name]
    fields, sdk_name = {
        "ts": (_ts_fields, ts),
        "go": (_go_fields, go),
        "dotnet": (_dotnet_fields, cs),
    }[sdk]
    sdk_fields = fields(sdk_name)
    server_fields = _schema_fields(server_name)

    phantom = sdk_fields - server_fields - SDK_ONLY.get(sdk_name, set())
    missing = server_fields - sdk_fields
    assert not phantom, f"{sdk}:{sdk_name} has fields the server doesn't define: {sorted(phantom)}"
    assert not missing, f"{sdk}:{sdk_name} is missing server fields: {sorted(missing)}"


@pytest.mark.parametrize("sdk", ["ts", "go", "dotnet"])
def test_batch_request_flags(sdk):
    # /v1/batch reads the raw request body, so its model is not in OpenAPI; use the Pydantic class.
    from address_standardizer.server import BatchStandardizeRequest

    name = "BatchStandardizeRequest"
    fields = {"ts": _ts_fields, "go": _go_fields, "dotnet": _dotnet_fields}[sdk](name)
    assert fields == set(BatchStandardizeRequest.model_fields)
