"""Tests for Phase 1 empirical audit improvements.

Covers:
- Cross-border centroid guard in offline index and geocoder
- Military box / plaza box stripping guard
- Care-of prefix wiping fix preserving house numbers and building names
- Puerto Rico URB deliverability and thoroughfare extraction
- Continuation-only building prepending fix
- Glued house numbers separation
- Spanish thoroughfare preservation
"""

import pytest

from address_standardizer import standardize_address
from address_standardizer.delivery import DPVFootnote, evaluate_delivery_intelligence
from address_standardizer.geocoder import OfflineGeocoder
from address_standardizer.models import StandardizedAddress
from address_standardizer.offline_index import get_default_offline_index


class TestCrossBorderCentroidGuard:
    """Verifies that non-US addresses never receive US centroid coordinates."""

    def test_geocoder_cross_border_guard(self):
        geocoder = OfflineGeocoder()
        intl_addr = standardize_address("100 Queen St, Ottawa, ON K1P 1J9, Canada")
        assert intl_addr.is_us is False
        res = geocoder.geocode(intl_addr)
        assert res.get("latitude") is None

    def test_offline_index_cross_border_guard(self):
        index = get_default_offline_index()
        intl_addr = standardize_address("100 Main St, London, ON N6A 1A1, Canada")
        assert intl_addr.is_us is False
        geo = index.geocode(intl_addr)
        assert geo.get("latitude") is None


class TestMilitaryBoxPlazaStripping:
    """Verifies that commercial addresses with 'BOX' preceded by digits or 'PLAZA' are not stripped as military."""

    def test_plaza_box_not_stripped(self):
        res = standardize_address("123 MAIN ST PLAZA BOX 4, SPRINGFIELD, IL 62701")
        assert res.address_status == "standardized"
        assert res.street1 == "123 MAIN ST"
        assert "PLAZA BOX" in (res.street2 or "") or "BOX 4" in (res.street2 or "")

    def test_commercial_box_after_building_number(self):
        res = standardize_address("500 EXECUTIVE BLVD BOX 100, WHITE PLAINS, NY 10604")
        assert res.address_status == "standardized"
        assert res.street1 == "500 EXECUTIVE BLVD"
        assert "BOX 100" in (res.street2 or "")

    def test_plaza_unit_box_without_house_number(self):
        res = standardize_address("EDWARDS PLAZA UNIT 17, BOX 13, SPRINGFIELD, IL 62701")
        assert res.address_status == "standardized"
        assert "EDWARDS" in res.street1

    def test_plaza_unit_box_with_house_number(self):
        res = standardize_address("247 EDWARDS PLAZA UNIT 17, BOX 13, SPRINGFIELD, IL 62701")
        assert res.address_status == "standardized"
        assert res.street1 == "247 EDWARDS PLZ"
        assert "UNIT 17" in (res.street2 or "")


class TestCareOfWipingFix:
    """Verifies that care-of lines do not wipe out real house numbers or corporate entities."""

    def test_care_of_person_with_numbered_street(self):
        res = standardize_address("C/O JOHN DOE 123 MAIN ST, SAN JOSE, CA 95112")
        assert res.address_status == "standardized"
        assert res.street1 == "123 MAIN ST"

    def test_care_of_company_with_digits(self):
        res = standardize_address("C/O 3M COMPANY 100 INNOVATION WAY, ST PAUL, MN 55144")
        assert res.address_status == "standardized"
        assert res.street1 == "100 INNOVATION WAY"

    def test_care_of_word_building_number(self):
        res = standardize_address("C/O LEGAL DEPT ONE WORLD TRADE CENTER, NEW YORK, NY 10007")
        assert res.address_status == "standardized"
        assert "ONE WORLD TRADE CENTER" in res.street1 or "1 WORLD TRADE CTR" in res.street1

    def test_care_of_dept_and_broadway(self):
        res = standardize_address("ATTN: TAX DEPARTMENT 123 BROADWAY, NEW YORK, NY 10006")
        assert res.address_status == "standardized"
        assert res.street1 == "123 BROADWAY"


class TestPuertoRicoUrbDeliverability:
    """Verifies Puerto Rico addresses with urbanization prefixes are parsed and deliverable."""

    def test_pr_urb_with_numbered_calle(self):
        res = standardize_address("URB FAIR VIEW 401 CALLE 3, SAN JUAN, PR 00926")
        assert res.address_status == "standardized"
        assert res.street1 == "URB FAIR VIEW 401 CALLE 3"
        assert res.street2 == ""
        assert res.state == "PR"
        di = evaluate_delivery_intelligence(res)
        assert DPVFootnote.BB in di.dpv_footnotes
        assert di.deliverability.name == "DELIVERABLE" or di.deliverability == "Deliverability.DELIVERABLE"

    def test_pr_numbered_calle_without_urb(self):
        res = standardize_address("401 CALLE 3, SAN JUAN, PR 00926")
        assert res.address_status == "standardized"
        assert res.street1 == "401 CALLE 3"
        assert res.street2 == ""

    def test_pr_urb_standard_street(self):
        res = standardize_address("URB LOS ANGELES 120 CALLE DEL PARQUE, CAROLINA, PR 00979")
        assert res.address_status == "standardized"
        assert "120" in res.street1
        assert "CALLE DEL PARQUE" in res.street1
        assert res.state == "PR"
        di = evaluate_delivery_intelligence(res)
        assert DPVFootnote.BB in di.dpv_footnotes


class TestContinuationBuildingPrepending:
    """Verifies continuation-only lines do not lead to invalid prepending."""

    def test_building_continuation_without_house_number(self):
        res = standardize_address(
            street1="TOWER 1",
            street2="SUITE 400",
            city="CHICAGO",
            state="IL",
            postal_code="60601",
        )
        assert res.address_status == "standardized"
        assert "TOWER 1" in (res.street1 or res.street2 or res.building_name or "")


class TestGluedHouseNumbers:
    """Verifies that glued house numbers (e.g. '100MAIN ST') are separated cleanly."""

    def test_glued_number_and_name(self):
        res = standardize_address("100MAIN ST, AUSTIN, TX 78701")
        assert res.address_status == "standardized"
        assert res.street1 == "100 MAIN ST"

    def test_glued_number_avenue(self):
        res = standardize_address("450LEXINGTON AVE, NEW YORK, NY 10017")
        assert res.address_status == "standardized"
        assert res.street1 == "450 LEXINGTON AVE"


class TestSpanishThoroughfarePreservation:
    """Verifies Spanish thoroughfare prefixes and particles are retained."""

    def test_calle_del_parque(self):
        res = standardize_address("100 CALLE DEL PARQUE, SAN JUAN, PR 00907")
        assert res.address_status == "standardized"
        assert res.street1 == "100 CALLE DEL PARQUE"

    def test_avenida_de_las_americas(self):
        res = standardize_address("50 AVENIDA DE LAS AMERICAS, PONCE, PR 00730")
        assert res.address_status == "standardized"
        assert "AVENIDA DE LAS AMERICAS" in res.street1

    def test_calle_san_francisco_preserves_street_name(self):
        res = standardize_address(
            street1="100 CALLE SAN FRANCISCO",
            city="SAN JUAN",
            state="PR",
            postal_code="00901",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "100 CALLE SAN FRANCISCO"
        assert res.city == "SAN JUAN"

