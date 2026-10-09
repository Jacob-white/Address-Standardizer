"""Optional transliteration: built-in Cyrillic/Greek fallback, anyascii path (fake module), std_to_latin, CLI --latin."""

import json
import sys

import pytest

from address_standardizer import cli
from address_standardizer.transliterate import (
    LATIN_FIELDS,
    SUPPORTED_SCRIPTS,
    TransliterationUnavailable,
    std_to_latin,
    transliterate,
)


@pytest.fixture
def no_anyascii(monkeypatch):
    monkeypatch.setitem(sys.modules, "anyascii", None)  # "from anyascii import ..." raises ImportError


@pytest.fixture
def fake_anyascii(monkeypatch):
    import types

    module = types.ModuleType("anyascii")
    module.anyascii = lambda text: "<" + text + ">"
    monkeypatch.setitem(sys.modules, "anyascii", module)
    return module


def test_empty_and_ascii_are_unchanged(no_anyascii):
    assert transliterate(None) == ""
    assert transliterate("") == ""
    assert transliterate("100 Main St") == "100 Main St"
    assert transliterate("ignored", script="latin") == "ignored"
    assert transliterate("Müller Straße 5, Zürich") == "Müller Straße 5, Zürich"  # accented Latin needs nothing


def test_cyrillic_fallback_preserves_case_and_digits(no_anyascii):
    assert transliterate("ул. Тверская 12") == "ul. Tverskaya 12"
    assert transliterate("Щи") == "Shchi"
    assert transliterate("ЩЕЛКОВО") == "SHCHELKOVO"  # all-caps word stays all caps
    assert transliterate("Ъ") == ""  # hard/soft signs are dropped (documented)
    assert transliterate("Ё", script="Cyrillic") == "E"


def test_greek_fallback_drops_accents(no_anyascii):
    assert transliterate("Λεωφόρος Αθηνών 5") == "Leoforos Athinon 5"
    assert transliterate("ΛΕΩΦΟΡΟΣ ΑΘΗΝΩΝ") == "LEOFOROS ATHINON"
    assert transliterate("Ψ") == "Ps"


def test_unsupported_script_raises_not_implemented_never_question_marks(no_anyascii):
    with pytest.raises(NotImplementedError) as info:
        transliterate("東京 1-2")
    assert isinstance(info.value, TransliterationUnavailable)
    assert "han" in str(info.value) and "address-standardizer[translit]" in str(info.value)
    with pytest.raises(TransliterationUnavailable):
        transliterate("Ж 東京")  # a mixed string fails as a whole in strict mode
    with pytest.raises(TransliterationUnavailable):
        transliterate("Ө")  # a Cyrillic letter missing from the table is not guessed


def test_passthrough_leaves_unsupported_characters_alone(no_anyascii):
    assert transliterate("Ж 東京 東", errors="passthrough") == "Zh 東京 東"
    assert "?" not in transliterate("Ө", errors="passthrough")


def test_argument_validation(no_anyascii):
    with pytest.raises(ValueError):
        transliterate("x", script="klingon")
    with pytest.raises(ValueError):
        transliterate("x", errors="ignore")
    assert {"cyrillic", "greek", "latin", "han"} <= SUPPORTED_SCRIPTS


def test_anyascii_is_used_when_installed(fake_anyascii):
    assert transliterate("東京") == "<東京>"
    assert transliterate("100 Main St") == "100 Main St"  # ASCII never reaches the library
    assert transliterate("東京", script="han", errors="strict") == "<東京>"
    assert transliterate("ignored", script="latin") == "ignored"


def test_std_to_latin_same_keys_as_as_dict(no_anyascii):
    from address_standardizer import standardize_address

    std = standardize_address("100 Main St", "Ste 4", "New York", "NY", "10001", "USA", use_cache=False)
    std.street1, std.city = "ул. Тверская 12", "Москва"
    data = std_to_latin(std)
    assert set(data) == set(std.as_dict())
    assert data["street1"] == "ul. Tverskaya 12" and data["city"] == "Moskva"
    assert data["street2"] == std.street2 and data["postal_code"] == std.postal_code
    assert std.street1 == "ул. Тверская 12"  # the model is not modified
    std.state = "東京"
    assert std_to_latin(std)["state"] == "東京"  # default passthrough: no failure, no invention
    with pytest.raises(TransliterationUnavailable):
        std_to_latin(std, errors="strict")
    assert LATIN_FIELDS == ("street1", "street2", "city", "state")


def test_std_to_latin_with_anyascii(fake_anyascii):
    from address_standardizer import standardize_address

    std = standardize_address("100 Main St", "", "New York", "NY", "10001", "USA", use_cache=False)
    std.city = "東京"
    assert std_to_latin(std)["city"] == "<東京>"


def test_cli_parse_latin_flag(no_anyascii, capsys, monkeypatch):
    from address_standardizer import cache as cache_mod

    monkeypatch.setattr(cache_mod, "_DEFAULT_CACHE", cache_mod._DEFAULT_CACHE)  # restores after --no-cache
    def run(*argv):
        monkeypatch.setattr(sys, "argv", ["address-standardizer", *argv])
        cli.main()

    run("parse", "--latin", "--street1", "ул. Тверская 12", "--city", "Москва", "--country", "RUS", "--no-cache")
    out = json.loads(capsys.readouterr().out)
    assert out["native"]["street1"].startswith("УЛ") or out["native"]["street1"].startswith("ул")
    assert all(ord(ch) < 128 for ch in out["street1"] + out["city"])
    run("parse", "--street1", "100 Main St", "--city", "New York", "--state", "NY", "--no-cache")
    assert "native" not in json.loads(capsys.readouterr().out)
