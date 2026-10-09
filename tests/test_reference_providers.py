"""Reference layer: GeoNames index builder, downloader, provider, composite provider, adapter interfaces."""

import io
import sqlite3
import zipfile

import pytest

from address_standardizer.reference import (
    ATTRIBUTION,
    DPV_MATCH_CODES,
    AuthoritativeDeliveryProvider,
    CompositeProvider,
    DeliveryMatch,
    GeoNamesPostalProvider,
    ReferencePlace,
    ReferenceProvider,
    build_geonames_index,
    download_geonames,
)
from address_standardizer.reference import geonames as gn
from address_standardizer.reference._match import name_tokens, names_match
from tests._geonames_fixture import (
    CA_ROWS,
    US_ROWS,
    build_fixture_db,
    make_source_dir,
    row,
    write_txt,
    write_zip,
)


class TestBuild:
    def test_build_from_directory(self, tmp_path):
        db = tmp_path / "out" / "idx.db"
        summary = build_geonames_index(db, source=make_source_dir(tmp_path), as_of="2026-02-03")
        assert db.is_file()
        assert not (tmp_path / "out" / "idx.db.tmp").exists()
        assert summary["countries"] == ["CA", "FR", "GB", "NL", "US"]
        assert summary["rows"] == len(US_ROWS) + len(CA_ROWS) + 3
        assert summary["skipped"] == 0
        assert summary["as_of"] == "2026-02-03"

    def test_country_filter_and_file_list(self, tmp_path):
        src = make_source_dir(tmp_path)
        db = tmp_path / "idx.db"
        summary = build_geonames_index(db, countries=["us", " ca "], source=[src / "US.txt", src / "CA.zip", src / "GB.zip"])
        assert summary["countries"] == ["CA", "US"]

    def test_single_file_source_and_default_as_of(self, tmp_path):
        src = make_source_dir(tmp_path)
        summary = build_geonames_index(tmp_path / "i.db", source=str(src / "US.txt"))
        assert summary["countries"] == ["US"]
        y, m, d = summary["as_of"].split("-")
        assert len(y) == 4 and len(m) == 2 and len(d) == 2

    def test_skips_malformed_rows_and_duplicates(self, tmp_path):
        f = write_txt(
            tmp_path / "US.txt",
            [
                "too\tfew\tcolumns",
                row("US", "", "No Postal"),
                row("US", "12345", ""),
                row("", "12345", "No Country"),
                row("US", "12345", "Goodville", "State", "ST", "", "", "not-a-float", "-1.5", "x"),
                row("US", "12345", "Goodville", "State", "ST", "", "", "1", "2", "4"),  # duplicate key -> ignored
                "US\t54321\tShort Row\tState\tST\t\t\t\t\t3.5\t4.5",  # 11 columns, no accuracy
            ],
        )
        db = tmp_path / "i.db"
        summary = build_geonames_index(db, source=f, as_of="x")
        assert summary["skipped"] == 4
        assert summary["rows"] == 2
        with GeoNamesPostalProvider(db) as p:
            good = p.lookup_postal("US", "12345")[0]
            assert good.latitude is None and good.longitude == -1.5
            assert p.lookup_postal("US", "54321")[0].latitude == 3.5

    def test_batching(self, tmp_path, monkeypatch):
        monkeypatch.setattr(gn, "_BATCH", 2)
        summary = build_geonames_index(tmp_path / "i.db", source=make_source_dir(tmp_path), as_of="x")
        assert summary["rows"] == len(US_ROWS) + len(CA_ROWS) + 3

    def test_rebuild_replaces_existing_and_clears_stale_tmp(self, tmp_path):
        db = tmp_path / "i.db"
        (tmp_path / "i.db.tmp").write_text("stale", encoding="utf-8")
        src = make_source_dir(tmp_path)
        build_geonames_index(db, countries=["US"], source=src, as_of="a")
        second = build_geonames_index(db, countries=["CA"], source=src, as_of="b")
        assert second["countries"] == ["CA"]
        with GeoNamesPostalProvider(db) as p:
            assert not p.covers_country("US") and p.as_of == "b"

    def test_missing_sources(self, tmp_path, monkeypatch):
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(FileNotFoundError, match="no GeoNames"):
            build_geonames_index(tmp_path / "i.db", source=empty)
        with pytest.raises(FileNotFoundError, match="not found"):
            build_geonames_index(tmp_path / "i.db", source=[tmp_path / "nope.zip"])
        monkeypatch.chdir(tmp_path)  # source=None means ./data/geonames, which does not exist here
        with pytest.raises(FileNotFoundError, match="not found"):
            build_geonames_index(tmp_path / "i.db")

    def test_bad_zip_keeps_previous_index(self, tmp_path):
        src = make_source_dir(tmp_path)
        db = tmp_path / "i.db"
        build_geonames_index(db, source=src / "US.txt", as_of="old")
        bad = tmp_path / "bad.zip"
        bad.write_bytes(b"this is not a zip")
        with pytest.raises(ValueError, match="not a valid zip"):
            build_geonames_index(db, source=[bad])
        assert not (tmp_path / "i.db.tmp").exists()
        with GeoNamesPostalProvider(db) as p:
            assert p.as_of == "old"

    def test_allcountries_zip_with_filter(self, tmp_path):
        z = write_zip(tmp_path / "allCountries.zip", US_ROWS + CA_ROWS, "allCountries.txt")
        summary = build_geonames_index(tmp_path / "i.db", countries=["CA"], source=z, as_of="x")
        assert summary["countries"] == ["CA"]


class TestProvider:
    @pytest.fixture()
    def provider(self, tmp_path):
        p = GeoNamesPostalProvider(build_fixture_db(tmp_path))
        yield p
        p.close()

    def test_metadata_and_attribution(self, provider):
        assert isinstance(provider, ReferenceProvider)
        assert provider.name == "geonames-postal"
        assert provider.license == "CC-BY-4.0"
        assert provider.as_of == "2026-01-01"
        assert "geonames.org" in provider.source
        info = provider.info()
        assert info["attribution"] == ATTRIBUTION and "Creative Commons" in ATTRIBUTION
        assert info["countries"] == ["CA", "FR", "GB", "NL", "US"]
        assert info["rows"] == len(US_ROWS) + len(CA_ROWS) + 3

    def test_lookup_postal(self, provider):
        place = provider.lookup_postal("us", "10005")[0]
        assert place == ReferencePlace(
            "US", "10005", "New York", "New York", "NY", "New York", 40.7061, -74.0088, provider="geonames-postal"
        )
        assert place.as_dict()["admin1_code"] == "NY"
        assert provider.lookup_postal("US", "00000") == []
        assert [p.admin1_code for p in provider.lookup_postal("US", "97001")] == ["OR", "WA"]

    def test_postal_candidates_coarser_spellings(self, provider):
        assert provider.lookup_postal("US", "10005-1234")[0].place_name == "New York"
        assert provider.lookup_postal("CA", "h2x 1y4")[0].place_name == "Montreal"
        assert provider.lookup_postal("CA", "H2X1Y4")[0].place_name == "Montreal"
        assert provider.lookup_postal("GB", "SW1A 1AA")[0].place_name == "London"
        assert provider.lookup_postal("GB", "SW1A1AA")[0].place_name == "London"
        assert provider.lookup_postal("NL", "1011 AB")[0].place_name == "Amsterdam"
        assert provider.lookup_postal("NL", "1011AB")[0].place_name == "Amsterdam"

    def test_postal_candidates_function(self):
        assert gn.postal_candidates("US", "10005") == ["10005"]
        assert gn.postal_candidates("US", "") == []
        assert gn.postal_candidates("FR", "75 001") == ["75 001", "75001", "75"]
        assert gn.postal_candidates("GB", "AB") == ["AB"]

    def test_lookup_place(self, provider):
        assert provider.lookup_place("US", "SPRINGFIELD") == ["62704"]
        assert provider.lookup_place("us", "springfield", "il") == ["62704"]
        assert provider.lookup_place("US", "Springfield", "MO") == []
        assert provider.lookup_place("FR", "paris 01") == ["75001"]
        assert provider.lookup_place("US", "Atlantis") == []

    def test_covers_country(self, provider):
        assert provider.covers_country("us") and provider.covers_country("NL")
        assert not provider.covers_country("DE")

    def test_open_errors(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            GeoNamesPostalProvider(tmp_path / "missing.db")
        junk = tmp_path / "junk.db"
        junk.write_bytes(b"not a sqlite file at all" * 20)
        with pytest.raises(ValueError, match="not a GeoNames postal index"):
            GeoNamesPostalProvider(junk)
        other = tmp_path / "other.db"
        con = sqlite3.connect(other)
        con.execute("CREATE TABLE meta (key TEXT, value TEXT)")
        con.execute("CREATE TABLE places (country TEXT)")
        con.execute("INSERT INTO meta VALUES ('schema_version', '999')")
        con.commit()
        con.close()
        with pytest.raises(ValueError, match="not a GeoNames postal index"):
            GeoNamesPostalProvider(other)

    def test_index_is_read_only(self, provider):
        with pytest.raises(sqlite3.OperationalError):
            provider._conn.execute("DELETE FROM places")

    def test_path_with_spaces(self, tmp_path):
        d = tmp_path / "dir with space"
        d.mkdir()
        db = build_fixture_db(d)
        with GeoNamesPostalProvider(db) as p:
            assert p.lookup_postal("US", "62704")


class TestMatching:
    def test_tokens(self):
        assert name_tokens("St. Louis") == ("SAINT", "LOUIS")
        assert name_tokens("City of Industry") == ("INDUSTRY",)
        assert name_tokens("The City") == ("THE", "CITY")  # only noise words: keep them rather than match nothing
        assert name_tokens("") == ()
        assert name_tokens("Zürich") == ("ZURICH",)

    @pytest.mark.parametrize("a,b", [
        ("Montréal", "MONTREAL"),
        ("St Louis", "Saint Louis"),
        ("Springfield", "East Springfield"),
        ("Springfeld", "Springfield"),
        ("Fort Collins", "Ft Collins"),
        ("Los Angeles", "Los Angelas"),
        ("Philadelphia", "Philadelphai"),
    ])
    def test_matches(self, a, b):
        assert names_match(a, b)

    @pytest.mark.parametrize("a,b", [
        ("Boston", "Chicago"),
        ("", "Chicago"),
        ("Chicago", ""),
        ("Ab", "Ac"),  # too short for edit-distance matching
        ("Dover", "Dovex Farms Road"),
        ("Albany", "Albuquerque"),
        ("AB", "ABCD EFGH"),  # subset of fewer than 3 characters is not enough
    ])
    def test_non_matches(self, a, b):
        assert not names_match(a, b)


class _Stub:
    def __init__(self, name, countries, postal=None, places=None):
        self.name, self.source, self.license, self.as_of = name, f"src-{name}", f"lic-{name}", "2026"
        self._countries, self._postal, self._places = countries, postal or {}, places or {}

    def covers_country(self, country):
        return country in self._countries

    def lookup_postal(self, country, postal_code):
        return self._postal.get((country, postal_code), [])

    def lookup_place(self, country, place_name, admin1_code=None):
        return self._places.get((country, place_name), [])


class TestComposite:
    def test_priority_and_fallback(self):
        a_place = ReferencePlace("US", "1", "A-place", provider="a")
        b_place = ReferencePlace("US", "1", "B-place", provider="b")
        a = _Stub("a", {"US"}, {("US", "1"): [a_place]}, {("US", "x"): ["1"]})
        b = _Stub("b", {"US", "CA"}, {("US", "1"): [b_place], ("CA", "2"): [b_place]}, {("US", "x"): ["9"], ("CA", "y"): ["2"]})
        comp = CompositeProvider([a, b])
        assert comp.name == "composite(a,b)"
        assert comp.source == "src-a; src-b" and comp.license == "lic-a; lic-b" and comp.as_of == "2026; 2026"
        assert comp.covers_country("CA") and not comp.covers_country("DE")
        assert comp.lookup_postal("US", "1") == [a_place]
        assert comp.lookup_postal("CA", "2") == [b_place]
        assert comp.lookup_postal("US", "zzz") == []
        assert comp.lookup_place("US", "x") == ["1"]
        assert comp.lookup_place("CA", "y") == ["2"]
        assert comp.lookup_place("US", "nothing") == []
        assert isinstance(comp, ReferenceProvider)

    def test_requires_providers(self):
        with pytest.raises(ValueError):
            CompositeProvider([])


class TestAdapterInterface:
    def test_delivery_match_and_protocol(self):
        m = DeliveryMatch("Y", ["AA", "BB"], provider="vendor")
        assert m.as_dict() == {"match_code": "Y", "footnotes": ["AA", "BB"], "provider": "vendor"}
        assert DeliveryMatch("N").footnotes == []
        assert set(DPV_MATCH_CODES) == {"Y", "S", "D", "N"}

        class Vendor:
            name, source, license, as_of = "v", "licensed vendor", "commercial", "2026"

            def verify(self, address):
                return DeliveryMatch("D", ["N1"], provider=self.name)

        assert isinstance(Vendor(), AuthoritativeDeliveryProvider)
        assert Vendor().verify(object()).match_code == "D"
        assert not isinstance(object(), AuthoritativeDeliveryProvider)

    def test_protocol_methods_are_declarations_only(self):
        # The protocols ship no behaviour: calling the bodies does nothing and returns None.
        assert ReferenceProvider.covers_country(None, "US") is None
        assert ReferenceProvider.lookup_postal(None, "US", "1") is None
        assert ReferenceProvider.lookup_place(None, "US", "x") is None
        assert AuthoritativeDeliveryProvider.verify(None, object()) is None


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class TestDownload:
    def test_download_with_injected_opener(self, tmp_path):
        seen = []

        def fake_urlopen(request, timeout=None):
            seen.append((request.full_url, request.get_header("User-agent"), timeout))
            return _Resp(b"zipbytes-" + request.full_url.encode())

        paths = download_geonames(["us", "ALL"], tmp_path / "dl", timeout=5, urlopen=fake_urlopen)
        assert [p.name for p in paths] == ["US.zip", "allCountries.zip"]
        assert paths[0].read_bytes().startswith(b"zipbytes-https://download.geonames.org/export/zip/US.zip")
        assert seen[0][1].startswith("address-standardizer") and seen[0][2] == 5
        assert not list((tmp_path / "dl").glob("*.part"))

    def test_default_opener_is_urllib(self, tmp_path, monkeypatch):
        import urllib.request

        calls = []
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: calls.append(req) or _Resp(b"x"))
        download_geonames(["CA"], tmp_path)
        assert calls and (tmp_path / "CA.zip").read_bytes() == b"x"

    def test_validation(self, tmp_path):
        with pytest.raises(ValueError, match="invalid country"):
            download_geonames(["../etc"], tmp_path)
        with pytest.raises(ValueError, match="invalid country"):
            download_geonames(["USA"], tmp_path)
        with pytest.raises(ValueError, match="no countries"):
            download_geonames([], tmp_path)

    def test_roundtrip_zip_built_into_index(self, tmp_path):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("US.txt", "\n".join(US_ROWS))
        download_geonames(["US"], tmp_path, urlopen=lambda req, timeout=None: _Resp(buf.getvalue()))
        summary = build_geonames_index(tmp_path / "i.db", source=tmp_path, as_of="x")
        assert summary["countries"] == ["US"]
