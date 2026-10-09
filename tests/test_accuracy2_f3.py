"""US / GB / IE accuracy round 2 (F3): route numbers are not ordinals, GB name-directionals, comma-less GB/IE lines,
and swapped US city/state. Deterministic: no network, no clock, no ordering dependence."""

import pytest

from address_standardizer import standardize_address
from address_standardizer._patterns import is_route_number_prefix
from address_standardizer.international.ireland import _is_eircode_run
from address_standardizer.international.uk import (
    UK_POST_TOWNS,
    _is_name_directional,
    is_valid_uk_postcode,
    split_commaless_postal_city,
)
from address_standardizer.normalization import swap_us_city_state
from address_standardizer.us_street_parser import _unswap_state_city


def _std(street1, country, **kw):
    r = standardize_address(street1=street1, country=country, **kw)
    return r.street1, r.street2, r.city, r.postal_code


# --------------------------------------------------------------------------- route numbers are never ordinals


@pytest.mark.parametrize(
    "line,street",
    [
        ("82 North Interstate Highway 35 Service Road, Austin, TX 78701", "82 N INTERSTATE HWY 35 SERVICE RD"),
        ("82 N Interstate Hwy 35 Service Rd, Austin, TX 78701", "82 N INTERSTATE HWY 35 SERVICE RD"),
        ("123 US Highway 90, Houston, TX 77001", "123 US HWY 90"),
        ("9 US 90, Houston, TX 77001", "9 US 90"),
        ("1200 State Route 9, Albany, NY 12203", "1200 STATE ROUTE 9"),
        ("500 County Road 12, Dallas, TX 75201", "500 COUNTY RD 12"),
        ("77 Farm to Market 1960, Houston, TX 77070", "77 FM 1960"),
        ("300 I-35 N, Austin, TX 78701", "300 I-35 N"),
        ("300 Interstate 35 N, Austin, TX 78701", "300 INTERSTATE 35 N"),
        ("10 Highway 1, Monterey, CA 93940", "10 HWY 1"),
        ("9 SH 71, Austin, TX 78701", "9 SH 71"),
        ("9 Texas 71, Austin, TX 78701", "9 TEXAS 71"),
        ("9 N Interstate 35 Frontage Rd, Austin, TX 78701", "9 N INTERSTATE 35 FRONTAGE RD"),
        ("9 Highway 35 Service Road, Austin, TX 78701", "9 HWY 35 SERVICE RD"),
    ],
)
def test_route_numbers_are_not_ordinals(line, street):
    assert _std(line, "US")[0] == street


def test_real_numbered_streets_are_still_ordinals():
    assert _std("15 35 Street, Austin, TX 78701", "US")[0] == "15 35TH ST"
    assert _std("100 Fifth Avenue, New York, NY 10003", "US")[0] == "100 5TH AVE"
    assert _std("100 5 Avenue, New York, NY 10003", "US")[0] == "100 5TH AVE"


def test_is_route_number_prefix():
    assert is_route_number_prefix("INTERSTATE")
    assert is_route_number_prefix("HWY")
    assert is_route_number_prefix("X", "STATE ROUTE")
    assert is_route_number_prefix("TEXAS")
    assert not is_route_number_prefix("MAIN")
    assert not is_route_number_prefix("TX")  # a state *code* before a number is left alone


# --------------------------------------------------------------------------- swapped US city / state


def test_swap_us_city_state():
    assert swap_us_city_state("IL", "Chicago") == ("Chicago", "IL")
    assert swap_us_city_state("Illinois.", "Chicago") == ("Chicago", "Illinois.")
    assert swap_us_city_state("Chicago", "IL") == ("Chicago", "IL")  # already right
    assert swap_us_city_state("Indiana", "PA") == ("Indiana", "PA")  # a real town, real state: untouched
    assert swap_us_city_state("IL", "") == ("IL", "")
    assert swap_us_city_state("", "Chicago") == ("", "Chicago")
    assert swap_us_city_state(None, None) == (None, None)


def test_structured_swapped_city_state_is_repaired():
    r = standardize_address(street1="1840 North Clybourn Avenue", city="IL", state="Chicago",
                            postal_code="60614", country="US")
    assert (r.city, r.state) == ("CHICAGO", "IL")


def test_unswap_state_city_text():
    assert _unswap_state_city("1840 N Clybourn Ave, IL, Chicago 60614") == "1840 N Clybourn Ave, Chicago, IL 60614"
    assert _unswap_state_city("1 Main St, Illinois, Salt Lake City 60614-1234") == (
        "1 Main St, Salt Lake City, Illinois 60614-1234"
    )
    assert _unswap_state_city("1 Main St, Chicago, IL 60614") == "1 Main St, Chicago, IL 60614"  # already right
    assert _unswap_state_city("1 Main St, Apt, Chicago 60614") == "1 Main St, Apt, Chicago 60614"  # not a state
    assert _unswap_state_city("1 Main St, LA, Los Angeles CA 90001") == "1 Main St, LA, Los Angeles CA 90001"
    assert _unswap_state_city("1 Main St, IL, Chicago") == "1 Main St, IL, Chicago"  # no ZIP: left alone


def test_line_swapped_city_state_is_repaired():
    r = standardize_address(street1="1840 North Clybourn Avenue, IL, Chicago 60614", country="US")
    assert (r.street1, r.city, r.state, r.postal_code) == ("1840 N CLYBOURN AVE", "CHICAGO", "IL", "60614")


# --------------------------------------------------------------------------- GB: name directionals / Arcade


def test_gb_name_directional_and_arcade():
    assert _std("3 North Western Arcade, Birmingham, B2 5LH", "GB")[0] == "3 NORTH WESTERN ARCADE"
    assert _std("12 West Register Street, Edinburgh, EH2 2AA", "GB")[0] == "12 WEST REGISTER ST"
    # golden-pinned: a directional directly followed by a street type stays abbreviated
    assert _std("38 North Street, Brighton, BN1 1AA", "GB")[0] == "38 N ST"
    assert _std("10 North Road West, Brighton, BN1 1AA", "GB")[0] == "10 N RD W"


def test_is_name_directional():
    assert _is_name_directional(["NORTH", "WESTERN", "ARCADE"], 0)
    assert not _is_name_directional(["NORTH", "STREET"], 0)  # two words: "North Street"
    assert not _is_name_directional(["NORTH", "ROAD", "WEST"], 0)  # followed by a street type
    assert not _is_name_directional(["TEMPLE", "BACK", "EAST"], 2)  # trailing directional


# --------------------------------------------------------------------------- comma-less GB lines


@pytest.mark.parametrize(
    "line,expected",
    [
        ("15 Johnston Terrace Edinburgh EH1 2PW", ("15 JOHNSTON TER", "", "EDINBURGH", "EH1 2PW")),
        ("3 North Western Arcade Birmingham B2 5LH", ("3 NORTH WESTERN ARCADE", "", "BIRMINGHAM", "B2 5LH")),
        ("3 Temple Back East Bristol BS1 6DZ", ("3 TEMPLE BACK E", "", "BRISTOL", "BS1 6DZ")),
        ("64A Stapleton Road Bristol BS5 0RB", ("64A STAPLETON RD", "", "BRISTOL", "BS5 0RB")),
        ("21-23 Stokes Croft Bristol BS1 3PY", ("21-23 STOKES CROFT", "", "BRISTOL", "BS1 3PY")),
        ("10 Downing Street London SW1A 2AA", ("10 DOWNING ST", "", "LONDON", "SW1A 2AA")),
        ("10 High Street St Albans AL1 3AA", ("10 HIGH ST", "", "ST ALBANS", "AL1 3AA")),
        ("10 High Street West Bromwich B70 6AA", ("10 HIGH ST", "", "WEST BROMWICH", "B70 6AA")),
        ("7 Church Street Ballymena BT43 6AA", ("7 CHURCH ST", "", "BALLYMENA", "BT43 6AA")),
        ("14 Park Lane Great Yarmouth NR30 1AA", ("14 PARK LN", "", "GREAT YARMOUTH", "NR30 1AA")),
        ("10 High Street St Ives PE27 5AA", ("10 HIGH ST", "", "ST IVES", "PE27 5AA")),
        ("10 Queen Street Cardiff CF10 2AA United Kingdom", ("10 QUEEN ST", "", "CARDIFF", "CF10 2AA")),
        ("Flat 2 15 Johnston Terrace Edinburgh EH1 2PW", ("15 JOHNSTON TER", "APT 2", "EDINBURGH", "EH1 2PW")),
    ],
)
def test_gb_commaless_lines(line, expected):
    assert _std(line, "GB") == expected


def test_gb_commaless_unknown_city_is_left_empty_not_guessed():
    # no known town and no street type to anchor on: the postcode is still extracted, the city stays empty
    s1, _, city, postal = _std("5 Foo Row EH1 2PW", "GB")
    assert (s1, city, postal) == ("5 FOO ROW", "", "EH1 2PW")
    # a 'Lower/Upper'-led tail and a directional-led tail are ambiguous: city stays empty
    assert _std("15 Johnston Terrace Upper Largo KY8 6AA", "GB")[2] == ""
    assert _std("15 Johnston Terrace West Foo KY8 6AA", "GB")[2] == ""
    # too many words after the street type
    assert _std("5 Foo Row Bar Baz Qux Quux EH1 2PW", "GB")[2] == ""


def test_gb_commaless_without_postcode_is_unchanged():
    assert _std("3 North Western Arcade Birmingham", "GB")[2] == ""
    assert _std("EH1 2PW", "GB")[3] == ""


def test_commaless_with_comma_and_with_fields_is_untouched():
    assert _std("15 Johnston Terrace, Edinburgh, EH1 2PW", "GB") == ("15 JOHNSTON TER", "", "EDINBURGH", "EH1 2PW")
    r = standardize_address(street1="15 Johnston Terrace Edinburgh", city="Edinburgh", country="GB")
    assert r.city == "EDINBURGH"


def test_split_commaless_postal_city_unit():
    def run(text):
        return split_commaless_postal_city(text, is_valid_uk_postcode, UK_POST_TOWNS)

    assert run("15 Johnston Terrace Edinburgh EH1 2PW") == ("15 Johnston Terrace", "Edinburgh", "EH1 2PW")
    assert run("15 Johnston Terrace Edinburgh EH12PW") == ("15 Johnston Terrace", "Edinburgh", "EH12PW")
    assert run("no postcode here") is None
    assert run("EH1 2PW") is None
    assert run("10 20 EH1 2PW") is None  # nothing but digits before the postcode
    assert run("10 Bath EH1 2PW") == ("10 Bath", "", "EH1 2PW")  # a lone number is not a street: city stays inside
    assert run("5 Foo Street 12 EH1 2PW") == ("5 Foo Street 12", "", "EH1 2PW")  # non-word tail
    assert run("5 Foo Street Bar Baz Qux Quux EH1 2PW") == ("5 Foo Street Bar Baz Qux Quux", "", "EH1 2PW")
    assert run("5 Foo Street Fooville EH1 2PW") == ("5 Foo Street", "Fooville", "EH1 2PW")


# --------------------------------------------------------------------------- comma-less IE lines


@pytest.mark.parametrize(
    "line,expected",
    [
        ("9 High Street Galway H91 KW97", ("9 HIGH ST", "", "GALWAY", "H91 KW97")),
        ("9 High Street Galway H91KW97", ("9 HIGH ST", "", "GALWAY", "H91 KW97")),
        ("101 North Main Street Cork T12 AKA6", ("101 N MAIN ST", "", "CORK", "T12 AKA6")),
        ("60 Dominick Street Lower Galway H91 P526", ("60 DOMINICK ST LOWER", "", "GALWAY", "H91 P526")),
        ("3 William Street West Galway H91 V184", ("3 WILLIAM ST W", "", "GALWAY", "H91 V184")),
        ("1 Main Street Ballina F26 AB12", ("1 MAIN ST", "", "BALLINA", "F26 AB12")),
        ("1 Main Street Foo Bar Station Y35 AB12", ("1 MAIN ST", "", "FOO BAR STATION", "Y35 AB12")),
        ("9 High Street Galway H91 KW97 Ireland", ("9 HIGH ST", "", "GALWAY", "H91 KW97")),
    ],
)
def test_ie_commaless_lines(line, expected):
    assert _std(line, "IE") == expected


def test_ie_commaless_without_eircode_is_unchanged():
    assert _std("1 Main Street Cork", "IE")[2] == ""
    assert _std("1 Main Street, Cork, T12 AKA6", "IE") == ("1 MAIN ST", "", "CORK", "T12 AKA6")


def test_is_eircode_run():
    assert _is_eircode_run("H91 KW97")
    assert _is_eircode_run("H91KW97")
    assert not _is_eircode_run("Main Street")
    assert not _is_eircode_run("High Lane")
    assert not _is_eircode_run("Hxx KW97")  # routing key needs a digit
