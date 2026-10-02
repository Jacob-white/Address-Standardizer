"""
Tests for Expanded Formation Hub & Corporate Transparency (BOI) Registry.
=========================================================================
"""

from address_standardizer import standardize_address
from address_standardizer.models import StandardizedAddress
from address_standardizer.registry import (
    RegistryCategory,
    CorporateRiskFlag,
    CorporateRegistryEntry,
    lookup_corporate_registry,
    is_registered_agent_hub_address,
    can_safely_merge_corporate_entities,
    evaluate_corporate_risk,
)


class TestCorporateRegistry:
    def test_registry_entry_as_dict(self):
        entry = CorporateRegistryEntry(
            provider_name="Test Provider",
            category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
            street_patterns=["123 TEST ST"],
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            base_risk_score=0.90,
            estimated_entities=100000,
            notes="Test notes",
            aliases=["ALIAS1"],
        )
        d = entry.as_dict()
        assert d["provider_name"] == "Test Provider"
        assert d["category"] == "COMMERCIAL_REGISTERED_AGENT"
        assert d["base_risk_score"] == 0.90
        assert d["estimated_entities"] == 100000
        assert d["aliases"] == ["ALIAS1"]

    def test_lookup_curated_registered_agents(self):
        # CT Corporation / Corporation Trust Center
        e1 = lookup_corporate_registry(street1="1209 N Orange St", city="Wilmington", state="DE")
        assert e1 is not None
        assert "CT Corporation" in e1.provider_name
        assert e1.category == RegistryCategory.COMMERCIAL_REGISTERED_AGENT

        # CSC Global HQ
        e2 = lookup_corporate_registry(street1="251 Little Falls Dr", city="Wilmington", state="DE")
        assert e2 is not None
        assert "CSC" in e2.provider_name

        # Registered Agents Inc (Wyoming)
        e3 = lookup_corporate_registry(street1="30 N Gould St", city="Sheridan", state="WY")
        assert e3 is not None
        assert "Wyoming Privacy Hub" in e3.provider_name

        # Harvard Business Services
        e4 = lookup_corporate_registry(street1="16192 Coastal Hwy", city="Lewes", state="DE")
        assert e4 is not None
        assert "Harvard Business Services" in e4.provider_name

        # Northwest Registered Agent (Spokane)
        e5 = lookup_corporate_registry(street1="522 W Riverside Ave", city="Spokane", state="WA")
        assert e5 is not None
        assert "Northwest Registered Agent" in e5.provider_name

        # LegalZoom (Glendale)
        e6 = lookup_corporate_registry(street1="101 N Brand Blvd", city="Glendale", state="CA")
        assert e6 is not None
        assert "LegalZoom" in e6.provider_name

    def test_lookup_virtual_offices_and_shared_spaces(self):
        # Regus 245 Park Ave NY (tower requires secondary match FL 39 / STE 3900)
        e_regus = lookup_corporate_registry(street1="245 Park Ave", street2="FL 39", city="New York", state="NY")
        assert e_regus is not None
        assert e_regus.category == RegistryCategory.VIRTUAL_OFFICE
        # Non-matching floor returns None to protect legitimate tenants
        assert lookup_corporate_registry(street1="245 Park Ave", street2="FL 12", city="New York", state="NY") is None
        assert lookup_corporate_registry(street1="245 Park Ave", city="New York", state="NY") is None

        # WeWork 115 W 18th St NY
        e_wework = lookup_corporate_registry(street1="115 W 18th St", city="New York", state="NY")
        assert e_wework is not None
        assert e_wework.category == RegistryCategory.VIRTUAL_OFFICE

        # DaVinci Virtual Offices
        e_davinci = lookup_corporate_registry(street1="275 Madison Ave", city="New York", state="NY")
        assert e_davinci is not None
        assert e_davinci.category == RegistryCategory.VIRTUAL_OFFICE

        # Opus Virtual Offices Boca Raton
        e_opus = lookup_corporate_registry(street1="777 Yamato Rd", city="Boca Raton", state="FL")
        assert e_opus is not None
        assert e_opus.category == RegistryCategory.VIRTUAL_OFFICE

    def test_lookup_offshore_secrecy_hubs(self):
        # Ugland House Grand Cayman
        e_ugland = lookup_corporate_registry(
            street1="South Church St",
            raw_street="Ugland House, South Church St",
            country="CYM",
        )
        assert e_ugland is not None
        assert e_ugland.category == RegistryCategory.OFFSHORE_SECRECY
        assert "Ugland House" in e_ugland.provider_name

        # BVI Craigmuir Chambers
        e_bvi = lookup_corporate_registry(
            street1="Craigmuir Chambers",
            city="Road Town",
            country="VGB",
        )
        assert e_bvi is not None
        assert e_bvi.category == RegistryCategory.OFFSHORE_SECRECY

        # Panama Calle 50
        e_pan = lookup_corporate_registry(
            street1="Calle 50",
            city="Panama City",
            country="PAN",
        )
        assert e_pan is not None
        assert e_pan.category == RegistryCategory.OFFSHORE_SECRECY

    def test_lookup_non_hub_address(self):
        res = lookup_corporate_registry(
            street1="500 Elm Street",
            city="Springfield",
            state="IL",
            postal_code="62701",
        )
        assert res is None

    def test_is_registered_agent_hub_address_parity_and_expansion(self):
        # Original 11 hubs
        assert is_registered_agent_hub_address("1209 N Orange St", city="Wilmington", state="DE") is True
        assert is_registered_agent_hub_address("160 Greentree Dr", city="Dover", state="DE") is True
        assert is_registered_agent_hub_address("251 Little Falls Dr", city="Wilmington", state="DE") is True
        assert is_registered_agent_hub_address("2711 Centerville Rd", city="Wilmington", state="DE") is True
        assert is_registered_agent_hub_address("850 New Burton Rd", city="Dover", state="DE") is True
        assert is_registered_agent_hub_address("820 Bear Tavern Rd", city="Trenton", state="NJ") is True
        assert is_registered_agent_hub_address("16192 Coastal Hwy", city="Lewes", state="DE") is True
        assert is_registered_agent_hub_address("30 N Gould St", city="Sheridan", state="WY") is True
        assert is_registered_agent_hub_address("3500 S Dupont Hwy", city="Dover", state="DE") is True
        assert is_registered_agent_hub_address("3773 Howard Hughes Pkwy", city="Las Vegas", state="NV") is True
        assert is_registered_agent_hub_address("Ugland House", country="CYM") is True

        # Non-hub
        assert is_registered_agent_hub_address("100 Main St", city="Dallas", state="TX") is False

    def test_enterprise_entity_resolution_invariant_cra_co_location(self):
        # Two distinct corporations registered at 1209 N Orange St (CT Corp)
        addr1 = StandardizedAddress(
            street1="1209 N ORANGE ST",
            street2="STE 400",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            country="USA",
            normalized_address_key="1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
            address_status="standardized",
            raw_street_address="1209 N Orange St, Ste 400",
            is_us=True,
            building_key="1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
            is_registered_agent_hub=True,
        )
        addr2 = StandardizedAddress(
            street1="1209 N ORANGE ST",
            street2="STE 400",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            country="USA",
            normalized_address_key="1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
            address_status="standardized",
            raw_street_address="1209 N Orange St, Ste 400",
            is_us=True,
            building_key="1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
            is_registered_agent_hub=True,
        )

        can_merge, reason = can_safely_merge_corporate_entities(addr1, addr2)
        assert can_merge is False
        assert "CO_LOCATION_ISOLATION_INVARIANT" in reason

    def test_entity_resolution_normal_commercial_buildings(self):
        # Case A: Different buildings
        a1 = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key="100 MAIN ST||NEW YORK|NY|10001|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
            building_key="100 MAIN ST||NEW YORK|NY|10001|USA",
        )
        a2 = StandardizedAddress(
            street1="200 PARK AVE",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10166",
            country="USA",
            normalized_address_key="200 PARK AVE||NEW YORK|NY|10166|USA",
            address_status="standardized",
            raw_street_address="200 Park Ave",
            is_us=True,
            building_key="200 PARK AVE||NEW YORK|NY|10166|USA",
        )
        can_merge, reason = can_safely_merge_corporate_entities(a1, a2)
        assert can_merge is False
        assert "DISTINCT_BUILDINGS" in reason

        # Case B: Single tenant commercial building (both have no secondary units)
        a3 = StandardizedAddress(
            street1="500 INDUSTRIAL PKWY",
            street2="",
            city="AUSTIN",
            state="TX",
            postal_code="78701",
            country="USA",
            normalized_address_key="500 INDUSTRIAL PKWY||AUSTIN|TX|78701|USA",
            address_status="standardized",
            raw_street_address="500 Industrial Pkwy",
            is_us=True,
            building_key="500 INDUSTRIAL PKWY||AUSTIN|TX|78701|USA",
        )
        a4 = StandardizedAddress(
            street1="500 INDUSTRIAL PKWY",
            street2="",
            city="AUSTIN",
            state="TX",
            postal_code="78701",
            country="USA",
            normalized_address_key="500 INDUSTRIAL PKWY||AUSTIN|TX|78701|USA",
            address_status="standardized",
            raw_street_address="500 Industrial Pkwy",
            is_us=True,
            building_key="500 INDUSTRIAL PKWY||AUSTIN|TX|78701|USA",
        )
        can_merge, reason = can_safely_merge_corporate_entities(a3, a4)
        assert can_merge is True
        assert "SINGLE_TENANT_BUILDING" in reason

        # Case C: Same building with matching suite
        a5 = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 400",
            is_us=True,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        a6 = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 400",
            is_us=True,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        can_merge, reason = can_safely_merge_corporate_entities(a5, a6)
        assert can_merge is True
        assert "MATCHING_SECONDARY_UNIT" in reason

        # Case D: Same building with mismatched suites
        a7 = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 500",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 500|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 500",
            is_us=True,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        can_merge, reason = can_safely_merge_corporate_entities(a5, a7)
        assert can_merge is False
        assert "SECONDARY_UNIT_MISMATCH" in reason

        # Case E: Asymmetric secondary unit (one has suite, one does not)
        a8 = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St",
            is_us=True,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        can_merge, reason = can_safely_merge_corporate_entities(a5, a8)
        assert can_merge is False
        assert "SECONDARY_UNIT_ASYMMETRY" in reason

    def test_corporate_risk_score_and_flags_evaluation(self):
        # 1. CRA hub without secondary unit
        std_hub_no_sec = standardize_address(
            street1="1209 N Orange St",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        score, flags = evaluate_corporate_risk(std_hub_no_sec)
        assert score >= 0.95
        assert CorporateRiskFlag.RISK_CRA_CO_LOCATION in flags
        assert CorporateRiskFlag.RISK_MISSING_SECONDARY_AT_HUB in flags

        # 2. Virtual office
        std_regus = standardize_address(
            street1="245 Park Ave",
            street2="FL 39",
            city="New York",
            state="NY",
            postal_code="10167",
        )
        score_v, flags_v = evaluate_corporate_risk(std_regus)
        assert score_v >= 0.70
        assert CorporateRiskFlag.RISK_VIRTUAL_OFFICE in flags_v

        # Non-matching suite at multi-tenant tower has 0.0 risk score
        std_non_regus = standardize_address(
            street1="245 Park Ave",
            street2="Suite 2400",
            city="New York",
            state="NY",
            postal_code="10167",
        )
        score_nr, flags_nr = evaluate_corporate_risk(std_non_regus)
        assert score_nr == 0.0
        assert CorporateRiskFlag.RISK_VIRTUAL_OFFICE not in flags_nr

        # 3. Disguised PMB
        std_pmb = standardize_address(
            street1="100 Main St",
            street2="PMB 500",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        score_p, flags_p = evaluate_corporate_risk(std_pmb)
        assert score_p >= 0.60
        assert CorporateRiskFlag.RISK_CMRA_MAIL_DROP in flags_p

        # 4. Private residence commercial registration
        std_res = standardize_address(
            street1="Private Residence",
            city="Denver",
            state="CO",
            postal_code="80202",
        )
        score_r, flags_r = evaluate_corporate_risk(std_res)
        assert CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL in flags_r

        # 5. Clean commercial address
        std_clean = standardize_address(
            street1="500 Elm St",
            city="Springfield",
            state="IL",
            postal_code="62701",
        )
        score_c, flags_c = evaluate_corporate_risk(std_clean)
        assert score_c == 0.0
        assert flags_c == []

        # 6. CMRA Mail Drop registry match
        std_cmra_hub = standardize_address(
            street1="277 4th Ave",
            street2="Suite 100",
            city="Brooklyn",
            state="NY",
            postal_code="11215",
        )
        score_cmra, flags_cmra = evaluate_corporate_risk(std_cmra_hub)
        assert score_cmra >= 0.75
        assert CorporateRiskFlag.RISK_CMRA_MAIL_DROP in flags_cmra

        # 7. Disguised PMB with raw 'PMB 100' and standardized 'STE 100'
        std_disguised = StandardizedAddress(
            street1="100 MAIN ST",
            street2="STE 100",
            city="NEW YORK",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key="100 MAIN ST|STE 100|NEW YORK|NY|10001|USA",
            address_status="standardized",
            raw_street_address="100 Main St, PMB 100",
            is_us=True,
        )
        score_disg, flags_disg = evaluate_corporate_risk(
            std_disguised,
            raw_input={"street1": "100 Main St", "street2": "PMB 100"},
        )
        assert CorporateRiskFlag.RISK_DISGUISED_PMB in flags_disg
        assert score_disg >= 0.65

        # 8. Unregistered hub marked with is_registered_agent_hub = True
        std_unregistered_hub = StandardizedAddress(
            street1="999 CUSTOM HUB WAY",
            street2="",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            country="USA",
            normalized_address_key="999 CUSTOM HUB WAY||WILMINGTON|DE|19801|USA",
            address_status="standardized",
            raw_street_address="999 Custom Hub Way",
            is_us=True,
            is_registered_agent_hub=True,
        )
        score_unreg, flags_unreg = evaluate_corporate_risk(std_unregistered_hub)
        assert score_unreg >= 0.85
        assert CorporateRiskFlag.RISK_CRA_CO_LOCATION in flags_unreg

    def test_entity_resolution_virtual_office_and_offshore_isolation(self):
        # Virtual office co-location
        a_vo1 = StandardizedAddress(
            street1="245 PARK AVE",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10167",
            country="USA",
            normalized_address_key="245 PARK AVE||NEW YORK|NY|10167|USA",
            address_status="standardized",
            raw_street_address="245 Park Ave",
            is_us=True,
            building_key="245 PARK AVE||NEW YORK|NY|10167|USA",
        )
        a_vo1.corporate_risk_flags = [CorporateRiskFlag.RISK_VIRTUAL_OFFICE]

        a_vo2 = StandardizedAddress(
            street1="245 PARK AVE",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10167",
            country="USA",
            normalized_address_key="245 PARK AVE||NEW YORK|NY|10167|USA",
            address_status="standardized",
            raw_street_address="245 Park Ave",
            is_us=True,
            building_key="245 PARK AVE||NEW YORK|NY|10167|USA",
        )
        a_vo2.corporate_risk_flags = [CorporateRiskFlag.RISK_VIRTUAL_OFFICE]

        can_merge_vo, reason_vo = can_safely_merge_corporate_entities(a_vo1, a_vo2)
        assert can_merge_vo is False
        assert "Shared virtual office or CMRA mail drop location" in reason_vo

        # Offshore secrecy hub co-location
        a_off1 = StandardizedAddress(
            street1="UGLAND HOUSE",
            street2="",
            city="GEORGE TOWN",
            state="",
            postal_code="",
            country="CYM",
            normalized_address_key="UGLAND HOUSE||GEORGE TOWN|||CYM",
            address_status="standardized",
            raw_street_address="Ugland House",
            is_us=False,
            building_key="UGLAND HOUSE||GEORGE TOWN|||CYM",
        )
        a_off1.corporate_risk_flags = [CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB]

        a_off2 = StandardizedAddress(
            street1="UGLAND HOUSE",
            street2="",
            city="GEORGE TOWN",
            state="",
            postal_code="",
            country="CYM",
            normalized_address_key="UGLAND HOUSE||GEORGE TOWN|||CYM",
            address_status="standardized",
            raw_street_address="Ugland House",
            is_us=False,
            building_key="UGLAND HOUSE||GEORGE TOWN|||CYM",
        )
        a_off2.corporate_risk_flags = [CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB]

        can_merge_off, reason_off = can_safely_merge_corporate_entities(a_off1, a_off2)
        assert can_merge_off is False
        assert "CO_LOCATION_ISOLATION_INVARIANT" in reason_off

    def test_false_positive_de_hub_prevention(self):
        # 160 Greentree Dr in Garden Grove, CA 92840 should NEVER match NRAI in Dover, DE!
        res_ca = lookup_corporate_registry(
            street1="160 Greentree Dr",
            city="Garden Grove",
            state="CA",
            postal_code="92840",
        )
        assert res_ca is None
        assert is_registered_agent_hub_address("160 Greentree Dr", city="Garden Grove", state="CA", postal_code="92840") is False

        # 160 Greentree Rd in Denver, CO 80202
        res_co = lookup_corporate_registry(
            street1="160 Greentree Rd",
            city="Denver",
            state="CO",
            postal_code="80202",
        )
        assert res_co is None

    def test_accented_foreign_hub_lookup(self):
        # Panama Calle 50 with accented "Panamá"
        entry = lookup_corporate_registry(
            street1="Calle 50",
            city="Panamá",
            country="PAN",
        )
        assert entry is not None
        assert entry.category == RegistryCategory.OFFSHORE_SECRECY

    def test_can_safely_merge_with_is_cmra_attribute(self):
        a1 = StandardizedAddress(
            street1="500 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="500 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="500 Main St",
            is_us=True,
            building_key="500 MAIN ST||DALLAS|TX|75201|USA",
        )
        a1.is_cmra = True

        a2 = StandardizedAddress(
            street1="500 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="500 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="500 Main St",
            is_us=True,
            building_key="500 MAIN ST||DALLAS|TX|75201|USA",
        )

        can_merge, reason = can_safely_merge_corporate_entities(a1, a2)
        assert can_merge is False
        assert "CO_LOCATION_ISOLATION_INVARIANT" in reason

    def test_evaluate_corporate_risk_no_duplicate_flags(self):
        std = StandardizedAddress(
            street1="500 7TH AVE",
            street2="STE 100",
            city="NEW YORK",
            state="NY",
            postal_code="10018",
            country="USA",
            normalized_address_key="500 7TH AVE|STE 100|NEW YORK|NY|10018|USA",
            address_status="standardized",
            raw_street_address="The UPS Store 500 7th Ave PMB 100",
            is_us=True,
        )
        score, flags = evaluate_corporate_risk(std, raw_input={"street1": "The UPS Store 500 7th Ave PMB 100"})
        assert len(flags) == len(set(flags))

    def test_lookup_corporate_registry_unparsed_single_line_string(self):
        # When city, state, postal_code are not passed as discrete kwargs
        entry = lookup_corporate_registry(street1="1209 N Orange St Wilmington DE 19801")
        assert entry is not None
        assert "CT Corporation" in entry.provider_name

    def test_merge_corporate_entities_empty_street_isolation(self):
        a1 = StandardizedAddress(
            street1="",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="",
            is_us=True,
            building_key=None,
        )
        a2 = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key="100 MAIN ST||NEW YORK|NY|10001|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
            building_key="100 MAIN ST||NEW YORK|NY|10001|USA",
        )
        can_merge, reason = can_safely_merge_corporate_entities(a1, a2)
        assert can_merge is False
        assert "EMPTY_STREET_ISOLATION" in reason

    def test_merge_corporate_entities_private_residence_isolation(self):
        a1 = StandardizedAddress(
            street1="742 EVERGREEN TER",
            street2="",
            city="SPRINGFIELD",
            state="OR",
            postal_code="97477",
            country="USA",
            normalized_address_key="PRIVATE RESIDENCE||742 EVERGREEN TER||SPRINGFIELD|OR|97477|USA",
            address_status="standardized",
            raw_street_address="742 Evergreen Ter",
            is_us=True,
            building_key="PRIVATE RESIDENCE||742 EVERGREEN TER||SPRINGFIELD|OR|97477|USA",
            is_private_residence=True,
        )
        a2 = StandardizedAddress(
            street1="742 EVERGREEN TER",
            street2="",
            city="SPRINGFIELD",
            state="OR",
            postal_code="97477",
            country="USA",
            normalized_address_key="PRIVATE RESIDENCE||742 EVERGREEN TER||SPRINGFIELD|OR|97477|USA",
            address_status="standardized",
            raw_street_address="742 Evergreen Ter",
            is_us=True,
            building_key="PRIVATE RESIDENCE||742 EVERGREEN TER||SPRINGFIELD|OR|97477|USA",
            is_private_residence=True,
        )
        can_merge, reason = can_safely_merge_corporate_entities(a1, a2)
        assert can_merge is False
        assert "PRIVATE_RESIDENCE_ISOLATION" in reason

    def test_merge_corporate_entities_dict_inputs(self):
        d1 = {"street1": "", "city": "NEW YORK"}
        d2 = {"street1": "100 MAIN ST", "city": "NEW YORK"}
        can_merge, reason = can_safely_merge_corporate_entities(d1, d2)
        assert can_merge is False
        assert "EMPTY_STREET_ISOLATION" in reason

        d_priv1 = {"street1": "742 EVERGREEN TER", "is_private_residence": True, "building_key": "K1"}
        d_priv2 = {"street1": "742 EVERGREEN TER", "is_private_residence": True, "building_key": "K1"}
        can_merge_p, reason_p = can_safely_merge_corporate_entities(d_priv1, d_priv2)
        assert can_merge_p is False
        assert "PRIVATE_RESIDENCE_ISOLATION" in reason_p




