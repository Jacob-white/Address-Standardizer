"""Coverage-driven behavioural tests for cli.py, run in-process by patching sys.argv / sys.stdin."""

import csv
import io
import json
import os
import sys

import pytest

from address_standardizer import cli
from address_standardizer._inputs import CORRECT_STATE_ENV

UK_ADDRESS = "Flat 2, The Mansions, 15 High Street, Headingley, Leeds LS6 2AA, UK"
ORANGE = "1209 North Orange St, Wilmington, DE 19801"


@pytest.fixture
def run(monkeypatch, capsys):
    """Invoke cli.main() with the given argv; returns (stdout, stderr). Exits propagate as SystemExit."""
    monkeypatch.setenv(CORRECT_STATE_ENV, "0")  # --correct-state-from-zip mutates the environment; restored on teardown
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))

    def _run(*argv, stdin=None):
        if stdin is not None:
            monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        monkeypatch.setattr(sys, "argv", ["address-standardizer", *argv])
        cli.main()
        captured = capsys.readouterr()
        return captured.out, captured.err

    return _run


def _exit_code(run, *argv, **kw):
    with pytest.raises(SystemExit) as exc:
        run(*argv, **kw)
    return exc.value.code


# ---------------------------------------------------------------------------
# stdin detection
# ---------------------------------------------------------------------------


class _Stdin:
    """Minimal stdin double: no getvalue(), configurable fileno/seek behaviour."""

    def __init__(self, text="", fileno_error=True, seekable=True, read_error=False, tty=False):
        self._buf = io.StringIO(text)
        self._fileno_error = fileno_error
        self._seekable = seekable
        self._read_error = read_error
        self._tty = tty

    def isatty(self):
        return self._tty

    def fileno(self):
        raise OSError("no descriptor")

    def seekable(self):
        return self._seekable

    def tell(self):
        return self._buf.tell()

    def read(self, n=-1):
        if self._read_error:
            raise OSError("unreadable")
        return self._buf.read(n)

    def seek(self, pos):
        self._buf.seek(pos)


def test_has_stdin_data_false_without_stdin_or_on_a_terminal(monkeypatch):
    monkeypatch.setattr(sys, "stdin", None)
    assert cli._has_stdin_data() is False
    monkeypatch.setattr(sys, "stdin", _Stdin("data", tty=True))
    assert cli._has_stdin_data() is False


def test_has_stdin_data_for_in_memory_streams(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("  \n"))
    assert cli._has_stdin_data() is False  # whitespace only
    monkeypatch.setattr(sys, "stdin", io.StringIO("1 Main St"))
    assert cli._has_stdin_data() is True


def test_has_stdin_data_uses_stream_type_for_real_files(monkeypatch, tmp_path):
    path = tmp_path / "in.txt"
    path.write_text("x", encoding="utf-8")
    with open(path, encoding="utf-8") as f:
        monkeypatch.setattr(sys, "stdin", f)
        assert cli._has_stdin_data() is True  # regular file
    with open(os.devnull, encoding="utf-8") as f:
        monkeypatch.setattr(sys, "stdin", f)
        assert cli._has_stdin_data() is False  # NUL / /dev/null is not a data source


def test_has_stdin_data_falls_back_to_peeking_seekable_streams(monkeypatch):
    stdin = _Stdin("abc")
    monkeypatch.setattr(sys, "stdin", stdin)
    assert cli._has_stdin_data() is True
    assert stdin.tell() == 0  # the peeked character is put back
    monkeypatch.setattr(sys, "stdin", _Stdin(""))
    assert cli._has_stdin_data() is False
    monkeypatch.setattr(sys, "stdin", _Stdin("abc", read_error=True))
    assert cli._has_stdin_data() is False
    monkeypatch.setattr(sys, "stdin", _Stdin("abc", seekable=False))
    assert cli._has_stdin_data() is False


def test_has_stdin_data_pytest_capture_placeholder_is_ignored(monkeypatch):
    class DontReadFromInput:
        def isatty(self):
            return False

    monkeypatch.setattr(sys, "stdin", DontReadFromInput())
    assert cli._has_stdin_data() is False


# ---------------------------------------------------------------------------
# postal validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, country, expected_country, valid, postal",
    [
        ("12345", "ZZZ", "ZZZ", False, "12345"),  # unknown country hint
        ("Dubai", "ARE", "ARE", True, "Dubai"),  # country without postal codes
        ("Apt 5, 90210", "US", "USA", True, "90210"),  # code extracted from surrounding text
        ("K1A 0B1", "US", "USA", False, "K1A 0B1"),  # direct failure is reported, not hidden
        ("SW1A 1AA", None, "GBR", True, "SW1A 1AA"),  # country inferred from the code
        ("Dubai", None, "ARE", True, "Dubai"),  # inferred country without postal codes
        ("12345-6789", None, "USA", True, "12345-6789"),  # ZIP+4 fallback when nothing else matches
        ("Hello", None, "", False, "Hello"),
    ],
)
def test_postal_validation_paths(text, country, expected_country, valid, postal):
    res = cli._execute_postal_validation(text, country)
    assert res["country"] == expected_country
    assert res["is_valid"] is valid
    assert res["postal_code"] == postal


def test_postal_validation_unknown_country_reason_and_unresolvable_input():
    assert "Unknown or unsupported country" in cli._execute_postal_validation("12345", "ZZZ")["reason"]
    assert "could not be inferred" in cli._execute_postal_validation("Hello")["reason"]


def test_validate_postal_streams_stdin_in_all_formats(run):
    out, _ = run("validate-postal", "-", "--format", "table", stdin="K1A 0B1\n\n90210\n")
    assert out.count("\n") >= 3 and "CAN" in out and "USA" in out
    out, _ = run("validate-postal", "-", "--format", "text", "-c", "CA", stdin="K1A 0B1\n")
    assert "K1A 0B1" in out
    out, _ = run("validate-postal", "--format", "json", stdin="K1A 0B1\n\n")  # implicit stdin, blank line skipped
    lines = [json.loads(ln) for ln in out.strip().splitlines()]
    assert len(lines) == 1 and lines[0]["country"] == "CAN" and lines[0]["is_valid"] is True


def test_validate_postal_table_for_a_single_code(run):
    out, _ = run("validate-postal", "K1A", "0B1", "--format", "table")
    assert "CAN" in out


def test_validate_postal_without_input_prints_help_and_exits_1(run, capsys):
    assert _exit_code(run, "validate-postal") == 1
    assert "usage:" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# argument validators and flags
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv, fragment",
    [
        (["batch", "in.csv", "out.csv", "--workers", "0"], "must be a positive integer"),
        (["autocomplete", "1 Main", "--limit", "99"], "between 1 and 50"),
        (["serve", "--port", "70000"], "TCP port between 1 and 65535"),
    ],
)
def test_argument_validators_reject_out_of_range_values(run, capsys, argv, fragment):
    assert _exit_code(run, *argv) == 2
    assert fragment in capsys.readouterr().err


def test_parse_correct_state_from_zip_flag_sets_environment_for_workers(run):
    out, _ = run("parse", "100 Main St, Los Angeles, NY 90012", "--correct-state-from-zip")
    assert json.loads(out)["state"] == "CA"
    assert os.environ[CORRECT_STATE_ENV] == "1"


# ---------------------------------------------------------------------------
# piped / shorthand output
# ---------------------------------------------------------------------------


def test_piped_stream_formats_and_optional_fields(run):
    stdin = f"\n{UK_ADDRESS}\n   \n{ORANGE}\n"
    out, _ = run("parse", "-", "--format", "text", stdin=stdin)
    assert out.count("STANDARDIZED ADDRESS") == 2
    assert "Dependent Locality:    HEADINGLEY" in out and "Building Name:         THE MANSIONS" in out

    out, _ = run("parse", "-", "--confidence", stdin=stdin)
    rows = [json.loads(ln) for ln in out.strip().splitlines()]
    assert len(rows) == 2
    assert rows[0]["dependent_locality"] == "HEADINGLEY" and rows[0]["building_name"] == "THE MANSIONS"
    assert 0.0 <= rows[1]["confidence_score"] <= 1.0 and rows[1]["routing_tier"]
    assert "dependent_locality" not in rows[1]


def test_shorthand_renders_every_format_and_optional_fields(run):
    out, _ = run(UK_ADDRESS)
    data = json.loads(out)
    assert data["dependent_locality"] == "HEADINGLEY" and data["building_name"] == "THE MANSIONS"
    assert data["country_iso3"] == "GBR"

    out, _ = run("--format", "text", UK_ADDRESS)
    assert "Dependent Locality:    HEADINGLEY" in out

    out, _ = run("--format", "table", ORANGE)
    assert "1209 N ORANGE ST" in out and out.count("\n") >= 3

    out, _ = run("--format", "csv", ORANGE)
    header, row = out.strip().splitlines()[:2]
    assert "street1" in header and "1209 N ORANGE ST" in row

    out, _ = run("--format", "upu", ORANGE)
    assert "1209 N ORANGE ST" in out


def test_shorthand_with_invalid_choice_defers_to_the_main_parser(run, capsys):
    assert _exit_code(run, "--format", "bogus", "1 Main St") == 2
    assert "invalid choice" in capsys.readouterr().err


def test_shorthand_without_address_or_stdin_prints_help(run, capsys):
    assert _exit_code(run, "--format", "json") == 1
    assert "usage:" in capsys.readouterr().out


def test_shorthand_reads_stdin_when_no_address_is_given(run):
    out, _ = run("--format", "json", stdin=f"{ORANGE}\n")
    assert json.loads(out)["street1"] == "1209 N ORANGE ST"


# ---------------------------------------------------------------------------
# parse enrichment branches that find nothing
# ---------------------------------------------------------------------------


def test_parse_geocoding_without_a_spatial_result_adds_no_coordinates(run, monkeypatch):
    monkeypatch.setattr(cli, "resolve_spatial_coordinates", lambda res: None)
    out, _ = run("parse", ORANGE, "--enable-geocoding")
    data = json.loads(out)
    assert "latitude" not in data and "spatial_result" not in data


def test_parse_audit_without_a_ledger_record_omits_audit_field(run, monkeypatch):
    class NullLedger:
        def record_standardized_address(self, *a, **k):
            return None

    monkeypatch.setattr(cli, "_audit_ledger", lambda args: NullLedger())
    out, _ = run("parse", "100 Wall St, New York, NY 10005", "--audit")
    assert "audit_record" not in json.loads(out)


def test_parse_census_geocode_without_a_match_adds_no_coordinates(run, monkeypatch):
    class NoMatch:
        def geocode_batch(self, records):
            return {}

    monkeypatch.setattr(cli, "CensusGeocoder", NoMatch)
    out, _ = run("parse", "100 Wall St, New York, NY 10005", "--geocode")
    assert "latitude" not in json.loads(out)


def test_parse_cascade_without_a_result_adds_no_cascade_fields(run, monkeypatch):
    monkeypatch.setattr(cli, "resolve_verification_cascade", lambda **kw: None)
    monkeypatch.setattr(cli, "CensusGeocoder", lambda: None)
    out, _ = run("parse", "100 Wall St, New York, NY 10005", "--cascade")
    assert "cascade_source" not in json.loads(out)


# ---------------------------------------------------------------------------
# batch
# ---------------------------------------------------------------------------


def _csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


ROW = {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"}


def test_batch_json_by_extension_and_by_explicit_format(run, tmp_path):
    src = tmp_path / "in.json"
    src.write_text(json.dumps([ROW]), encoding="utf-8")
    out, _ = run("batch", str(src), str(tmp_path / "out.json"), "--workers", "1")
    assert "Standardized 1 record(s)" in out
    assert json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))[0]["std_street1"] == "100 WALL ST"

    out, _ = run("batch", str(src), str(tmp_path / "out.dat"), "--format", "json", "--workers", "1")
    assert json.loads((tmp_path / "out.dat").read_text(encoding="utf-8"))[0]["std_postal_code"] == "10005"


def test_batch_jsonl_via_output_extension(run, tmp_path):
    src = tmp_path / "in.jsonl"
    src.write_text(json.dumps(ROW) + "\n", encoding="utf-8")
    run("batch", str(src), str(tmp_path / "out.ndjson"), "--workers", "1")
    line = (tmp_path / "out.ndjson").read_text(encoding="utf-8").strip()
    assert json.loads(line)["std_street1"] == "100 WALL ST"


def test_batch_mapping_must_be_a_json_object(run, tmp_path, capsys):
    src = tmp_path / "in.csv"
    _csv(src, [ROW])
    assert _exit_code(run, "batch", str(src), str(tmp_path / "o.csv"), "--mapping", "[1, 2]") == 2
    assert "--mapping must be a JSON object" in capsys.readouterr().err


def test_batch_mapping_from_file_and_inline(run, tmp_path):
    src = tmp_path / "in.csv"
    _csv(src, [{"Addr": "100 Wall St", "Town": "New York", "St": "NY", "Z": "10005"}])
    mapping = {"Addr": "street1", "Town": "city", "St": "state", "Z": "zip"}
    mfile = tmp_path / "map.json"
    mfile.write_text(json.dumps(mapping), encoding="utf-8")
    for spec, name in ((str(mfile), "a.csv"), (json.dumps(mapping), "b.csv")):
        run("batch", str(src), str(tmp_path / name), "--mapping", spec, "--workers", "1")
        with open(tmp_path / name, newline="", encoding="utf-8") as f:
            assert next(csv.DictReader(f))["std_street1"] == "100 WALL ST"


def test_batch_missing_input_is_a_clean_error(run, tmp_path, capsys):
    assert _exit_code(run, "batch", str(tmp_path / "nope.csv"), str(tmp_path / "o.csv")) == 2
    err = capsys.readouterr().err
    assert err.startswith("Error:") and "nope.csv" in err


# ---------------------------------------------------------------------------
# benchmark / serve
# ---------------------------------------------------------------------------


def test_benchmark_without_a_source_checkout_exits_with_message(run, monkeypatch, capsys):
    real_isfile = os.path.isfile
    monkeypatch.setattr(os.path, "isfile", lambda p: False if str(p).endswith("run_benchmarks.py") else real_isfile(p))
    assert _exit_code(run, "benchmark") == 2
    assert "only available in a source checkout" in capsys.readouterr().err


def test_serve_without_uvicorn_exits_with_install_hint(run, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "uvicorn", None)
    assert _exit_code(run, "serve") == 1
    assert "uvicorn is required" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# spatial build
# ---------------------------------------------------------------------------


def test_spatial_build_ingests_all_sources_into_a_relative_db_path(run, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "oa.csv").write_text(
        "LATITUDE,LONGITUDE,NUMBER,STREET,UNIT,CITY,REGION,POSTCODE,COUNTRY,ID\n"
        "34.0522,-118.2437,200,N Spring St,,Los Angeles,CA,90012,USA,LA-200\n",
        encoding="utf-8",
    )
    (tmp_path / "tiger.csv").write_text(
        "street_name,from_number,to_number,start_lat,start_lon,end_lat,end_lon,parity,postal_code,city,state,country_iso3,source\n"
        "OAK ST,100,200,42.0,-71.0,42.01,-71.01,EVEN,02108,BOSTON,MA,USA,TIGER\n",
        encoding="utf-8",
    )
    (tmp_path / "osm.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": [{
            "type": "Feature", "geometry": {"type": "Point", "coordinates": [-74.0, 40.7]},
            "properties": {"addr:housenumber": "1", "addr:street": "Liberty St"}}]}),
        encoding="utf-8",
    )
    out, _ = run("spatial", "build", "--output", "idx.db", "--openaddresses", "oa.csv", "--tiger", "tiger.csv", "--osm", "osm.geojson")
    assert "Spatial SQLite index built successfully: idx.db" in out
    assert "Ingested OpenAddresses points: 1" in out
    assert "Ingested TIGER segments: 1" in out
    assert "Ingested OSM building features: 1" in out
    assert (tmp_path / "idx.db").exists()


@pytest.mark.parametrize("flag, label", [("--openaddresses", "OpenAddresses"), ("--tiger", "TIGER"), ("--osm", "OSM")])
def test_spatial_build_reports_missing_source_files(run, tmp_path, flag, label):
    missing = str(tmp_path / "missing.dat")
    with pytest.raises(SystemExit) as exc:
        out = run("spatial", "build", "--output", str(tmp_path / "x.db"), flag, missing)
        del out
    assert exc.value.code == 1
    assert not (tmp_path / "x.db").exists()


def test_spatial_build_missing_source_message_goes_to_stdout(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["prog", "spatial", "build", "--tiger", str(tmp_path / "t.csv")])
    with pytest.raises(SystemExit):
        cli.main()
    assert "Error: TIGER file not found" in capsys.readouterr().out
