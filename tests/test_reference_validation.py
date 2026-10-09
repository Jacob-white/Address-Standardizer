"""validate_against_reference, the standardize_address hook, the CLI commands and the REST attachment."""

import json
import sys
from unittest.mock import patch

import pytest

from address_standardizer import standardize_address
from address_standardizer.cli import main
from address_standardizer.models import StandardizedAddress
from address_standardizer.reference import (
    ERR_POSTAL_STATE_MISMATCH,
    ERR_POSTAL_UNKNOWN,
    WARN_POSTAL_PLACE_MISMATCH,
    GeoNamesPostalProvider,
    ReferenceValidation,
    validate_against_reference,
)
from address_standardizer.reference import validation as val
from tests._geonames_fixture import build_fixture_db, make_source_dir


@pytest.fixture()
def provider(tmp_path):
    p = GeoNamesPostalProvider(build_fixture_db(tmp_path))
    yield p
    p.close()


def addr(city="", state="", postal="", country="USA", **extra):
    a = StandardizedAddress(
        street1="1 MAIN ST", street2="", city=city, state=state, postal_code=postal, country=country,
        normalized_address_key="k", address_status="standardized", raw_street_address="1 Main St", is_us=country == "USA",
    )
    for key, value in extra.items():
        setattr(a, key, value)
    return a


class TestValidate:
    def test_confirmed(self, provider):
        r = validate_against_reference(addr("NEW YORK", "NY", "10005"), provider)
        assert r.status == "confirmed" and r.reason_codes == []
        assert r.checks == ["postal", "state", "place"]
        assert r.matched_place.place_name == "New York"
        assert r.provider == "geonames-postal" and r.license == "CC-BY-4.0" and r.as_of == "2026-01-01"
        assert r.country == "US" and r.distance_km is None

    def test_accent_case_and_typo_tolerance(self, provider):
        assert validate_against_reference(addr("montréal", "QC", "H2X 1Y4", "CAN"), provider).status == "confirmed"
        assert validate_against_reference(addr("Springfeld", "IL", "62704"), provider).status == "confirmed"
        assert validate_against_reference(addr("ST LOUIS", "MO", "63101"), provider).status == "confirmed"

    def test_county_name_counts_as_place(self, provider):
        # Mailing city "LOS ANGELES" is not a GeoNames place for 90210 (Beverly Hills) but is its county.
        assert validate_against_reference(addr("LOS ANGELES", "CA", "90210"), provider).status == "confirmed"

    def test_dependent_locality_counts(self, provider):
        r = validate_against_reference(addr("Elsewhere", "NY", "11201", dependent_locality="Brooklyn"), provider)
        assert r.status == "confirmed" and r.matched_place.place_name == "Brooklyn"

    def test_place_mismatch_is_a_warning(self, provider):
        r = validate_against_reference(addr("CHICAGO", "NY", "10005"), provider)
        assert r.status == "place_mismatch" and r.reason_codes == [WARN_POSTAL_PLACE_MISMATCH]
        assert r.matched_place is None and r.candidate_places == ["New York"]
        assert r.reason_codes[0].startswith("WARN_")

    def test_state_mismatch(self, provider):
        r = validate_against_reference(addr("SPRINGFIELD", "MO", "62704"), provider)
        assert r.status == "state_mismatch" and r.reason_codes == [ERR_POSTAL_STATE_MISMATCH]
        assert r.matched_place.place_name == "Springfield"  # the city itself is fine
        both = validate_against_reference(addr("Nowhere", "MO", "62704"), provider)
        assert both.status == "state_mismatch"
        assert both.reason_codes == [ERR_POSTAL_STATE_MISMATCH, WARN_POSTAL_PLACE_MISMATCH]

    def test_state_matters_only_for_us_and_ca(self, provider):
        r = validate_against_reference(addr("Amsterdam", "ZZ", "1011 AB", "Netherlands"), provider)
        assert r.status == "confirmed" and r.checks == ["postal", "place"]

    def test_state_skipped_when_blank_or_reference_has_none(self, provider):
        blank = validate_against_reference(addr("New York", "", "10005"), provider)
        assert blank.status == "confirmed" and blank.checks == ["postal", "place"]
        no_state_data = validate_against_reference(addr("Odd Place", "NY", "00501"), provider)
        assert no_state_data.status == "confirmed" and no_state_data.checks == ["postal", "place"]

    def test_multi_state_postal_prefers_supplied_state(self, provider):
        r = validate_against_reference(addr("Other Hamlet", "WA", "97001"), provider)
        assert r.status == "confirmed" and r.matched_place.admin1_code == "WA"
        # a code spanning several localities must not reject any of them
        assert validate_against_reference(addr("Border Town", "OR", "97001"), provider).status == "confirmed"

    def test_unknown_postal(self, provider):
        r = validate_against_reference(addr("New York", "NY", "00000"), provider)
        assert r.status == "postal_unknown" and r.reason_codes == [ERR_POSTAL_UNKNOWN]
        assert r.checks == ["postal"] and "00000" in r.detail

    def test_not_checked_cases(self, provider):
        assert validate_against_reference(addr("X", "", "", "USA"), provider).status == "not_checked"
        assert validate_against_reference(addr("X", "", "12345", "Atlantis"), provider).status == "not_checked"
        no_country = addr("X", "", "12345")
        no_country.country = None
        assert validate_against_reference(no_country, provider).detail == "country not recognised"
        de = validate_against_reference(addr("Berlin", "", "10115", "Germany"), provider)
        assert de.status == "not_checked" and "DE" in de.detail and de.reason_codes == []

    def test_no_city_single_place_is_matched(self, provider):
        one = validate_against_reference(addr("", "NY", "10005"), provider)
        assert one.status == "confirmed" and one.checks == ["postal", "state"] and one.matched_place.place_name == "New York"
        many = validate_against_reference(addr("", "", "97001"), provider)
        assert many.status == "confirmed" and many.matched_place is None

    def test_distance(self, provider):
        near = validate_against_reference(addr("New York", "NY", "10005", latitude=40.7061, longitude=-74.0088), provider)
        assert near.distance_km == 0.0
        far = validate_against_reference(addr("New York", "NY", "10005", latitude=34.05, longitude=-118.24), provider)
        assert 3900 < far.distance_km < 4000
        # reference centroid missing -> no distance
        assert validate_against_reference(addr("Los Angeles", "CA", "90001", latitude=1.0, longitude=2.0), provider).distance_km is None

    def test_haversine_clamps(self):
        assert val._haversine_km(0.0, 0.0, 0.0, 180.0) == pytest.approx(20015.1, rel=1e-3)

    def test_as_dict_roundtrips_json(self, provider):
        r = validate_against_reference(addr("New York", "NY", "10005"), provider)
        d = json.loads(json.dumps(r.as_dict()))
        assert d["status"] == "confirmed" and d["matched_place"]["postal_code"] == "10005" and d["distance_km"] is None
        assert ReferenceValidation("not_checked").as_dict()["matched_place"] is None


class TestStandardizeHook:
    def test_default_is_untouched(self):
        s = standardize_address("100 Wall St", city="New York", state="NY", postal_code="10005")
        assert s.reference_validation is None
        assert "reference_validation" not in s.as_dict(include_metadata=True)

    def test_validation_attached_and_codes_merged(self, provider):
        s = standardize_address("100 Wall St", city="New York", state="NY", postal_code="10005", reference_provider=provider)
        assert s.reference_validation.status == "confirmed"
        assert s.as_dict(include_metadata=True)["reference_validation"]["status"] == "confirmed"
        bad = standardize_address("100 Wall St", city="Chicago", state="NY", postal_code="10005", reference_provider=provider)
        assert bad.reference_validation.status == "place_mismatch"
        assert WARN_POSTAL_PLACE_MISMATCH in bad.failure_reason_codes
        again = standardize_address("100 Wall St", city="Chicago", state="NY", postal_code="10005", reference_provider=provider)
        assert again.failure_reason_codes.count(WARN_POSTAL_PLACE_MISMATCH) == 1
        # the provider-less call (served from the cache) must not inherit the validation
        plain = standardize_address("100 Wall St", city="Chicago", state="NY", postal_code="10005")
        assert plain.reference_validation is None and WARN_POSTAL_PLACE_MISMATCH not in plain.failure_reason_codes

    def test_unknown_postal_through_standardize(self, provider):
        s = standardize_address("5 Main St", city="Nowhere", state="NY", postal_code="00000", reference_provider=provider, finalize=False)
        assert s.reference_validation.status == "postal_unknown"
        assert ERR_POSTAL_UNKNOWN in s.failure_reason_codes

    def test_merge_keeps_existing_codes(self, provider):
        s = standardize_address("100 Wall St", city="New York", state="CA", postal_code="10005", reference_provider=provider)
        assert "ERR_ZIP_STATE_MISMATCH" in s.failure_reason_codes
        assert ERR_POSTAL_STATE_MISMATCH in s.failure_reason_codes


class TestCLI:
    def run(self, capsys, *argv):
        with patch.object(sys, "argv", ["address-standardizer", *argv]):
            main()
        return capsys.readouterr().out

    def test_fetch_build_info(self, tmp_path, capsys, monkeypatch):
        import io

        import address_standardizer.reference.geonames as gn

        class Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        import zipfile

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("US.txt", "US\t10005\tNew York\tNew York\tNY\tNew York\t061\t\t\t40.7\t-74.0\t4\n")
        monkeypatch.setattr(gn.urllib.request, "urlopen", lambda req, timeout=None: Resp(buf.getvalue()))
        out = json.loads(self.run(capsys, "data", "fetch", "geonames", "--countries", "US, ,CA", "--out", str(tmp_path / "dl")))
        assert [p.rsplit("dl", 1)[1].lstrip("\\/") for p in out["downloaded"]] == ["US.zip", "CA.zip"]

        (tmp_path / "dl" / "CA.zip").unlink()
        db = tmp_path / "idx.db"
        built = json.loads(self.run(capsys, "data", "build", "geonames", "--from", str(tmp_path / "dl"), "--out", str(db), "--as-of", "2026-05-05"))
        assert built["rows"] == 1 and built["as_of"] == "2026-05-05"
        filtered = json.loads(self.run(capsys, "data", "build", "geonames", "--from", str(tmp_path / "dl"), "--out", str(db), "--countries", "us"))
        assert filtered["countries"] == ["US"]
        info = json.loads(self.run(capsys, "data", "info", str(db)))
        assert info["countries"] == ["US"] and "GeoNames" in info["attribution"]

    def test_parse_with_reference_db(self, tmp_path, capsys):
        db = build_fixture_db(tmp_path)
        out = json.loads(self.run(
            capsys, "parse", "--street1", "100 Wall St", "--city", "Chicago", "--state", "NY", "--zip", "10005",
            "--reference-db", str(db), "--confidence",
        ))
        assert out["reference_validation"]["status"] == "place_mismatch"
        assert WARN_POSTAL_PLACE_MISMATCH in out["failure_reason_codes"]

    def test_parse_without_reference_db_has_no_object(self, capsys):
        out = json.loads(self.run(capsys, "parse", "100 Wall St, New York, NY 10005"))
        assert "reference_validation" not in out

    def test_errors_are_reported_cleanly(self, tmp_path, capsys):
        with patch.object(sys, "argv", ["address-standardizer", "parse", "1 Main St, X, NY 10005", "--reference-db", str(tmp_path / "no.db")]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 2
        assert "reference database not found" in capsys.readouterr().err
        with patch.object(sys, "argv", ["address-standardizer", "data", "build", "geonames", "--from", str(tmp_path / "none"), "--out", str(tmp_path / "x.db")]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 2

    def test_data_requires_action(self, capsys):
        with patch.object(sys, "argv", ["address-standardizer", "data"]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 2


class TestServer:
    @pytest.fixture()
    def client(self, monkeypatch):
        from fastapi.testclient import TestClient

        from address_standardizer.server import app

        yield TestClient(app)
        val.close_server_providers()

    def test_absent_by_default(self, client, monkeypatch):
        monkeypatch.delenv(val.REFERENCE_DB_ENV, raising=False)
        body = client.post("/v1/standardize", json={"address": "100 Wall St, New York, NY 10005"}).json()
        assert "reference_validation" not in body

    def test_present_when_configured(self, client, monkeypatch, tmp_path):
        db = build_fixture_db(tmp_path)
        monkeypatch.setenv(val.REFERENCE_DB_ENV, str(db))
        body = client.post("/v1/standardize", json={"address": "100 Wall St, New York, NY 10005"}).json()
        assert body["reference_validation"]["status"] == "confirmed"
        assert body["reference_validation"]["license"] == "CC-BY-4.0"
        again = client.post("/v1/standardize", json={"address": "100 Wall St, Chicago, NY 10005"}).json()
        assert again["reference_validation"]["status"] == "place_mismatch"
        assert len(val._server_providers) == 1  # the index is opened once and reused

    def test_unusable_database_is_visible_not_fatal(self, client, monkeypatch, tmp_path):
        monkeypatch.setenv(val.REFERENCE_DB_ENV, str(tmp_path / "missing.db"))
        body = client.post("/v1/standardize", json={"address": "100 Wall St, New York, NY 10005"}).json()
        assert body["reference_validation"]["status"] == "not_checked"
        assert "unavailable" in body["reference_validation"]["detail"]
        assert body["street1"] == "100 WALL ST"


def test_make_source_dir_is_reusable(tmp_path):
    assert (make_source_dir(tmp_path) / "US.txt").is_file()
