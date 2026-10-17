"""Unit and integration tests for Address-Standardizer MCP server and tools."""

import argparse
import asyncio
import builtins
import sys
from unittest.mock import MagicMock, patch
import pytest

from address_standardizer.cli import _cmd_mcp
from address_standardizer.mcp import (
    autocomplete_address_tool,
    batch_standardize_tool,
    create_mcp_server,
    explain_parse_tool,
    main as mcp_main,
    standardize_address_tool,
    validate_postal_tool,
)
import address_standardizer.mcp.server as mcp_server_module


def test_standardize_address_tool_basic():
    res = standardize_address_tool(address="1600 Amphitheatre Pkwy, Mountain View, CA 94043")
    assert res["street1"] == "1600 AMPHITHEATRE PKWY"
    assert res["city"] == "MOUNTAIN VIEW"
    assert res["state"] == "CA"
    assert res["postal_code"] == "94043"
    assert res["country"] == "USA"
    assert res["routing_tier"] in ("AUTO_PASS", "FUZZY_REVIEW", "MANUAL_STEWARDSHIP")
    assert "confidence_score" in res
    assert "normalized_address_key" in res
    assert "building_key" in res
    assert "address_status" in res
    assert "deliverability" in res
    assert "latitude" not in res
    assert "dpv_footnotes" not in res
    assert "explanation" not in res


def test_standardize_address_tool_with_options():
    res = standardize_address_tool(
        street1="100 Main St",
        street2="Apt 4B",
        city="Seattle",
        state="WA",
        postal_code="98101",
        country="USA",
        enable_geocoding=True,
        include_metadata=True,
        explain=True,
        correct_state_from_zip=True,
    )
    assert res["street1"] == "100 MAIN ST"
    assert res["street2"] == "APT 4B"
    assert "latitude" in res
    assert "longitude" in res
    assert "dpv_footnotes" in res
    assert "failure_reason_codes" in res
    assert "is_vacant" in res
    assert "is_registered_agent_hub" in res
    assert "is_private_residence" in res
    assert "suggested_secondary_units" in res
    assert "explanation" in res
    assert "alternatives" in res


def test_batch_standardize_tool_success():
    items = [
        "100 Main St, Seattle, WA 98101",
        {
            "street1": "200 Pine St",
            "street2": "Ste 100",
            "city": "Seattle",
            "state": "WA",
            "postal_code": "98101",
            "country": "USA",
        },
    ]
    batch_res = batch_standardize_tool(items, enable_geocoding=False, correct_state_from_zip=False)
    assert batch_res["count"] == 2
    assert len(batch_res["results"]) == 2
    assert batch_res["results"][0]["city"] == "SEATTLE"
    assert batch_res["results"][1]["street2"] == "STE 100"


def test_batch_standardize_tool_validation():
    with pytest.raises(ValueError, match="at least 1 address"):
        batch_standardize_tool([])

    with pytest.raises(ValueError, match="exceeds maximum allowed batch size"):
        batch_standardize_tool(["100 Main St"] * 501)

    with pytest.raises(TypeError, match="Invalid address item type"):
        batch_standardize_tool([12345])  # type: ignore


def test_validate_postal_tool_us():
    res = validate_postal_tool("94043", country="US")
    assert res["is_valid"] is True
    assert res["country_iso2"] == "US"
    assert res["country_iso3"] == "USA"
    assert res["has_postal_system"] is True
    assert res["format_pattern"] is not None


def test_validate_postal_tool_uk():
    res = validate_postal_tool("SW1A 1AA", country="GB")
    assert res["is_valid"] is True
    assert res["country_iso2"] == "GB"
    assert res["country_iso3"] == "GBR"


def test_validate_postal_tool_non_postal_country():
    res = validate_postal_tool("", country="AE")
    assert res["is_valid"] is True
    assert res["has_postal_system"] is False


def test_validate_postal_tool_unknown_country():
    res = validate_postal_tool("12345", country="ZZZ")
    assert res["is_valid"] is False
    assert res["country_iso2"] == "ZZ"
    assert res["country_iso3"] == "ZZZ"


def test_autocomplete_address_tool():
    res = autocomplete_address_tool("1600 Amphitheatre", limit=3)
    assert isinstance(res, list)


def test_explain_parse_tool():
    res = explain_parse_tool("100 Main St Ste 400, Seattle, WA 98101", alternatives=2)
    assert "standardized_address" in res
    assert "explanation" in res
    assert "alternatives" in res
    assert res["standardized_address"]["city"] == "SEATTLE"


def test_create_mcp_server_success_and_call_tool():
    pytest.importorskip("mcp")
    server = create_mcp_server()
    assert server is not None

    res1 = asyncio.run(server.call_tool("standardize_address", {"address": "100 Main St, Seattle, WA 98101"}))
    assert res1.is_error is False

    res2 = asyncio.run(server.call_tool("batch_standardize", {"addresses": ["100 Main St, Seattle, WA 98101"]}))
    assert res2.is_error is False

    res3 = asyncio.run(server.call_tool("validate_postal", {"postal_code": "98101", "country": "US"}))
    assert res3.is_error is False

    res4 = asyncio.run(server.call_tool("autocomplete_address", {"query": "100 Main", "limit": 2}))
    assert res4.is_error is False

    res5 = asyncio.run(server.call_tool("explain_parse", {"address": "100 Main St, Seattle, WA 98101"}))
    assert res5.is_error is False


def test_get_mcp_server_cls_fallback():
    orig_import = builtins.__import__

    # Case 1: mcpserver fails, fastmcp succeeds
    def mock_import1(name, *args, **kwargs):
        if "mcp.server.mcpserver" in name:
            raise ImportError("no mcpserver")
        if "mcp.server.fastmcp" in name:
            mod = MagicMock()
            mod.FastMCP = "MockFastMCP"
            return mod
        return orig_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import1):
        cls1 = mcp_server_module._get_mcp_server_cls()
        assert cls1 == "MockFastMCP"

    # Case 2: both fail
    def mock_import2(name, *args, **kwargs):
        if "mcp.server" in name:
            raise ImportError("no mcp")
        return orig_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import2):
        cls2 = mcp_server_module._get_mcp_server_cls()
        assert cls2 is None


def test_create_mcp_server_import_error():
    with patch.object(mcp_server_module, "_MCPServer", None):
        with pytest.raises(ImportError, match="The MCP server requires the 'mcp' extra"):
            create_mcp_server()


def test_main_cli_stdio():
    mock_server = MagicMock()
    with patch.object(mcp_server_module, "create_mcp_server", return_value=mock_server):
        ret = mcp_main(["--transport", "stdio"])
        assert ret == 0
        mock_server.run.assert_called_once_with(transport="stdio")


def test_main_cli_default_sys_argv():
    mock_server = MagicMock()
    with patch.object(mcp_server_module, "create_mcp_server", return_value=mock_server):
        with patch.object(sys, "argv", ["address-standardizer-mcp", "--transport", "stdio"]):
            ret = mcp_main()
            assert ret == 0
            mock_server.run.assert_called_once_with(transport="stdio")


def test_main_cli_sse_with_settings():
    mock_server = MagicMock()
    mock_server.settings = MagicMock()
    with patch.object(mcp_server_module, "create_mcp_server", return_value=mock_server):
        ret = mcp_main(["--transport", "sse", "--host", "0.0.0.0", "--port", "9000"])
        assert ret == 0
        assert mock_server.settings.host == "0.0.0.0"
        assert mock_server.settings.port == 9000
        mock_server.run.assert_called_once_with(transport="sse")


def test_main_cli_sse_without_settings():
    mock_server = MagicMock(spec=["run"])
    with patch.object(mcp_server_module, "create_mcp_server", return_value=mock_server):
        ret = mcp_main(["--transport", "sse", "--host", "0.0.0.0", "--port", "9000"])
        assert ret == 0
        mock_server.run.assert_called_once_with(transport="sse")


def test_cli_cmd_mcp():
    args = argparse.Namespace(transport="stdio", host="127.0.0.1", port=8000)
    with patch("address_standardizer.mcp.server.main") as mock_main:
        _cmd_mcp(args)
        mock_main.assert_called_once_with(["--transport", "stdio", "--host", "127.0.0.1", "--port", "8000"])


def test_cli_main_mcp_dispatch():
    with patch.object(sys, "argv", ["address-standardizer", "mcp", "--transport", "stdio"]):
        with patch("address_standardizer.mcp.server.main") as mock_main:
            from address_standardizer.cli import main as cli_main

            cli_main()
            mock_main.assert_called_once_with(["--transport", "stdio", "--host", "127.0.0.1", "--port", "8000"])

