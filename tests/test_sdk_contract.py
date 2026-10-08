"""
SDK contract tests: the field names in each client SDK must match the server's OpenAPI schema.

Catches drift between `address_standardizer/server.py` (Pydantic models) and the hand-written
TypeScript, Go and .NET models in `sdks/`.
"""

import re
from pathlib import Path

import pytest

from tests._deps import require  # noqa: E402

require("fastapi")

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


def _ts_typed(name):
    """field -> (kind, optional) from the TypeScript interface."""
    text = (SDKS / "typescript/src/types.ts").read_text(encoding="utf-8")
    body = _block(text, rf"export interface {name}\b")
    out = {}
    for field, opt, typ in re.findall(r"^\s{2}(\w+)(\??):\s*([^;]+);", body, re.M):
        if field == "fetch":
            continue
        if "[]" in typ or "Array<" in typ:
            kind = "list"
        elif "string" in typ or '"' in typ:
            kind = "str"
        elif "number" in typ:
            kind = "num"
        elif "boolean" in typ:
            kind = "bool"
        else:
            kind = "obj"
        out[field] = (kind, bool(opt) or "| null" in typ)
    return out


def _go_typed(name):
    text = (SDKS / "go/models.go").read_text(encoding="utf-8")
    body = _block(text, rf"type {name} struct\b")
    out = {}
    for typ, tag in re.findall(r'^\s*\w+\s+(\S+)\s+`json:"([^`]+)"`', body, re.M):
        field = tag.split(",")[0]
        if field == "-":
            continue
        base = typ.lstrip("*")
        if base.startswith("[]"):
            kind = "list"
        elif base == "string":
            kind = "str"
        elif base.startswith("int") or base == "uint":
            kind = "int"
        elif base.startswith("float"):
            kind = "num"
        elif base == "bool":
            kind = "bool"
        else:
            kind = "obj"
        optional = typ.startswith("*") or base.startswith(("[]", "map", "interface")) or "omitempty" in tag
        out[field] = (kind, optional)
    return out


def _dotnet_typed(name):
    text = (SDKS / "dotnet/Models.cs").read_text(encoding="utf-8")
    body = _block(text, rf"public class {name}\b")
    out = {}
    for field, typ in re.findall(r'\[JsonPropertyName\("([^"]+)"\)\]\s*public\s+([^\s]+(?:<[^>]*>)?\??)\s+\w+\s*\{', body):
        base = typ.rstrip("?")
        if base.startswith(("List<", "IList<", "IReadOnlyList<", "IEnumerable<")) or base.endswith("[]"):
            kind = "list"
        elif base == "string":
            kind = "str"
        elif base in ("int", "long", "short"):
            kind = "int"
        elif base in ("double", "float", "decimal"):
            kind = "num"
        elif base == "bool":
            kind = "bool"
        else:
            kind = "obj"
        out[field] = (kind, typ.endswith("?"))
    return out


def _ts_fields(name):
    return set(_ts_typed(name))


def _go_fields(name):
    return set(_go_typed(name))


def _dotnet_fields(name):
    return set(_dotnet_typed(name))


def _server_typed(name):
    """field -> (kind, nullable, has_default) from the server's OpenAPI schema."""
    props = app.openapi()["components"]["schemas"][name]["properties"]
    out = {}
    for field, spec in props.items():
        branches = spec.get("anyOf", [spec])
        nullable = any(b.get("type") == "null" for b in branches)
        real = next(b for b in branches if b.get("type") != "null")
        kind = {"string": "str", "integer": "int", "number": "num", "boolean": "bool", "array": "list", "object": "obj"}.get(
            real.get("type"), "obj"
        )
        out[field] = (kind, nullable, "default" in spec)
    return out


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


# Go decodes a JSON null into a plain string as "" (no error, no data corruption). The string fields the server may
# send as null are deliberately modelled as `string` so callers get idiomatic zero values; numeric/boolean tri-state
# fields (coordinates, CMRA, vacant) are pointers because 0/false would be misleading.
GO_STRING_NULL_AS_EMPTY = {
    ("go", f)
    for f in (
        "normalized_address_key", "building_key", "phonetic_key", "deliverability", "precision", "census_tract",
        "fips_code", "routing_tier", "rdi", "rooftop_address", "full_rooftop_address",
    )
}

# Request fields whose SDK model initialises the same value as the server default, so "unset" and "default" agree.
MIRRORED_DEFAULTS = {("AutocompleteRequest", "max_results")}

# Kinds an SDK may use for a server kind (TypeScript has a single `number` type).
_COMPATIBLE = {"int": {"int", "num"}, "num": {"num"}, "str": {"str"}, "bool": {"bool"}, "list": {"list"}, "obj": {"obj"}}


@pytest.mark.parametrize("server_name", sorted(MODELS))
@pytest.mark.parametrize("sdk", ["ts", "go", "dotnet"])
def test_sdk_field_types_and_nullability_match_server(server_name, sdk):
    ts, go, cs = MODELS[server_name]
    typed, sdk_name = {"ts": (_ts_typed, ts), "go": (_go_typed, go), "dotnet": (_dotnet_typed, cs)}[sdk]
    sdk_fields = typed(sdk_name)
    server_fields = _server_typed(server_name)
    assert sdk_fields, f"parser found no fields for {sdk}:{sdk_name}: the contract test would pass vacuously"

    wrong_type, not_nullable, not_optional = [], [], []
    for field, (kind, nullable, has_default) in server_fields.items():
        if field not in sdk_fields:
            continue  # reported by the field-name test
        sdk_kind, sdk_optional = sdk_fields[field]
        if sdk_kind not in _COMPATIBLE[kind]:
            wrong_type.append(f"{field}: server {kind}, sdk {sdk_kind}")
        if nullable and not sdk_optional:
            not_nullable.append(field)
        if has_default and server_name.endswith("Request") and not sdk_optional:
            # An SDK request field with a server-side default must be omittable, or callers can't pick "server default".
            not_optional.append(field)
    not_nullable = [f for f in not_nullable if (sdk, f) not in GO_STRING_NULL_AS_EMPTY or sdk != "go"]
    not_optional = [f for f in not_optional if (sdk_name, f) not in MIRRORED_DEFAULTS]
    assert not wrong_type, f"{sdk}:{sdk_name} type mismatch: {wrong_type}"
    assert not not_nullable, f"{sdk}:{sdk_name} fields the server may return as null are not nullable: {not_nullable}"
    assert not not_optional, f"{sdk}:{sdk_name} request fields with server defaults are not optional: {not_optional}"


def test_parsers_do_not_pass_vacuously():
    for name in ("StandardizeRequest", "StandardizedAddress"):
        assert len(_go_typed(name)) >= 10
        assert len(_dotnet_typed(name)) >= 10
    assert len(_ts_typed("StandardizeResponse")) >= 20
