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

    def test_registry_taxonomy_and_risk_flags(self):
        assert RegistryCategory.COMMERCIAL_REGISTERED_AGENT == "COMMERCIAL_REGISTERED_AGENT"
        assert RegistryCategory.FORMATION_AGENT == "FORMATION_AGENT"
        assert RegistryCategory.VIRTUAL_OFFICE == "VIRTUAL_OFFICE"
        assert RegistryCategory.MAIL_DROP_CMRA == "MAIL_DROP_CMRA"
        assert RegistryCategory.OFFSHORE_SECRECY == "OFFSHORE_SECRECY"
        assert RegistryCategory.TRUST_FIDUCIARY_COMPANY == "TRUST_FIDUCIARY_COMPANY"

        assert CorporateRiskFlag.RISK_CRA_CO_LOCATION == "RISK_CRA_CO_LOCATION"
        assert CorporateRiskFlag.RISK_VIRTUAL_OFFICE == "RISK_VIRTUAL_OFFICE"
        assert CorporateRiskFlag.RISK_CMRA_MAIL_DROP == "RISK_CMRA_MAIL_DROP"
        assert CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB == "RISK_OFFSHORE_SECRECY_HUB"
        assert CorporateRiskFlag.RISK_TRUST_FIDUCIARY == "RISK_TRUST_FIDUCIARY"
        assert CorporateRiskFlag.RISK_MISSING_SECONDARY_AT_HUB == "RISK_MISSING_SECONDARY_AT_HUB"
        assert CorporateRiskFlag.RISK_DISGUISED_PMB == "RISK_DISGUISED_PMB"
        assert CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL == "RISK_RESIDENTIAL_COMMERCIAL"

    def test_curated_international_formation_hubs_completeness(self):
        from address_standardizer.registry import CURATED_CORPORATE_REGISTRY
        expected_countries = {"CYM", "VGB", "BMU", "PAN", "GBR", "NLD", "LUX", "CHE", "IRL", "SGP"}
        found_countries = {e.country.upper() for e in CURATED_CORPORATE_REGISTRY}
        assert expected_countries.issubset(found_countries)

        intl_entries = [e for e in CURATED_CORPORATE_REGISTRY if e.country.upper() != "USA"]
        assert len(intl_entries) >= 15
        for entry in intl_entries:
            assert entry.base_risk_score >= 0.85
            assert entry.estimated_entities >= 8000
            assert len(entry.street_patterns) > 0

    def test_lookup_all_15_international_hubs(self):
        # 1. Ugland House (CYM)
        e1 = lookup_corporate_registry(street1="South Church St", country="CYM")
        assert e1 is not None and e1.category == RegistryCategory.OFFSHORE_SECRECY
        assert "Ugland House" in e1.provider_name

        # 2. Clifton House (CYM)
        e2 = lookup_corporate_registry(street1="75 Fort St", country="CYM")
        assert e2 is not None and e2.category == RegistryCategory.OFFSHORE_SECRECY
        assert "Clifton House" in e2.provider_name

        # 3. 190 Elgin Ave (CYM)
        e3 = lookup_corporate_registry(street1="190 Elgin Ave", country="CYM")
        assert e3 is not None and e3.category == RegistryCategory.OFFSHORE_SECRECY

        # 4. Craigmuir Chambers (VGB)
        e4 = lookup_corporate_registry(street1="Craigmuir Chambers", country="VGB")
        assert e4 is not None and e4.category == RegistryCategory.OFFSHORE_SECRECY

        # 5. Wickhams Cay (VGB)
        e5 = lookup_corporate_registry(street1="Wickhams Cay", country="VGB")
        assert e5 is not None and e5.category == RegistryCategory.OFFSHORE_SECRECY

        # 6. Clarendon House (BMU)
        e6 = lookup_corporate_registry(street1="2 Church St", city="Hamilton", country="BMU")
        assert e6 is not None and e6.category == RegistryCategory.OFFSHORE_SECRECY
        assert "Clarendon House" in e6.provider_name

        # 7. Calle 50 (PAN)
        e7 = lookup_corporate_registry(street1="Calle 50", city="Panama City", country="PAN")
        assert e7 is not None and e7.category == RegistryCategory.OFFSHORE_SECRECY

        # 8. Shelton Street Companies Hub (GBR)
        e8 = lookup_corporate_registry(street1="71-75 Shelton St", city="London", postal_code="WC2H 9JQ", country="GBR")
        assert e8 is not None and e8.category == RegistryCategory.FORMATION_AGENT

        # 9. Wenlock Road Registered Hub (GBR)
        e9 = lookup_corporate_registry(street1="20-22 Wenlock Rd", city="London", postal_code="N1 7GU", country="GBR")
        assert e9 is not None and e9.category == RegistryCategory.FORMATION_AGENT

        # 10. Old Gloucester Street Mail Drop (GBR)
        e10 = lookup_corporate_registry(street1="27 Old Gloucester St", city="London", postal_code="WC1N 3AX", country="GBR")
        assert e10 is not None and e10.category == RegistryCategory.MAIL_DROP_CMRA

        # 11. Keizersgracht Trust District (NLD)
        e11 = lookup_corporate_registry(street1="Keizersgracht 421", city="Amsterdam", postal_code="1016 EK", country="NLD")
        assert e11 is not None and e11.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

        # 12. Boulevard Royal Financial Hub (LUX)
        e12 = lookup_corporate_registry(street1="25A Boulevard Royal", city="Luxembourg", postal_code="L-2449", country="LUX")
        assert e12 is not None and e12.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

        # 13. Baarerstrasse "Crypto Valley" (CHE)
        e13 = lookup_corporate_registry(street1="Baarerstrasse 82", city="Zug", postal_code="6300", country="CHE")
        assert e13 is not None and e13.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

        # 14. International Financial Services (IRL)
        e14 = lookup_corporate_registry(street1="1 IFC", city="Dublin", postal_code="D01", country="IRL")
        assert e14 is not None and e14.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

        # 15. Marina Bay / Raffles Virtual Hub (SGP)
        e15 = lookup_corporate_registry(street1="1 Raffles Place", city="Singapore", postal_code="048616", country="SGP")
        assert e15 is not None and e15.category == RegistryCategory.VIRTUAL_OFFICE

    def test_is_registered_agent_hub_address_international_categories(self):
        # TRUST_FIDUCIARY_COMPANY -> True
        assert is_registered_agent_hub_address("Baarerstrasse 82", city="Zug", country="CHE", postal_code="6300") is True
        assert is_registered_agent_hub_address("Keizersgracht 421", city="Amsterdam", country="NLD") is True
        assert is_registered_agent_hub_address("25A Boulevard Royal", city="Luxembourg", country="LUX") is True
        assert is_registered_agent_hub_address("1 IFC", city="Dublin", country="IRL") is True

        # FORMATION_AGENT -> True
        assert is_registered_agent_hub_address("71-75 Shelton St", city="London", country="GBR") is True
        assert is_registered_agent_hub_address("20-22 Wenlock Rd", city="London", country="GBR") is True

        # OFFSHORE_SECRECY -> True
        assert is_registered_agent_hub_address("2 Church St", city="Hamilton", country="BMU") is True
        assert is_registered_agent_hub_address("South Church St", country="CYM") is True

        # VIRTUAL_OFFICE -> False
        assert is_registered_agent_hub_address("1 Raffles Place", city="Singapore", country="SGP") is False

        # MAIL_DROP_CMRA -> False
        assert is_registered_agent_hub_address("27 Old Gloucester St", city="London", country="GBR") is False

    def test_evaluate_corporate_risk_all_categories_and_flags(self):
        # Offshore secrecy hub (tests previously unexercised offshore branch)
        std_off = standardize_address("Ugland House, South Church St, George Town, Cayman Islands")
        score_off, flags_off = evaluate_corporate_risk(std_off)
        assert score_off >= 0.95
        assert CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB in flags_off

        # Trust fiduciary hub (tests new RISK_TRUST_FIDUCIARY branch and missing secondary)
        std_trust = standardize_address("Baarerstrasse 82, 6300 Zug, Switzerland")
        score_trust, flags_trust = evaluate_corporate_risk(std_trust)
        assert score_trust >= 0.90
        assert CorporateRiskFlag.RISK_TRUST_FIDUCIARY in flags_trust
        assert CorporateRiskFlag.RISK_MISSING_SECONDARY_AT_HUB in flags_trust

        # Formation agent
        std_form = standardize_address("71-75 Shelton St, London WC2H 9JQ, UK")
        score_form, flags_form = evaluate_corporate_risk(std_form)
        assert score_form >= 0.90
        assert CorporateRiskFlag.RISK_CRA_CO_LOCATION in flags_form

        # Virtual office
        std_vo = standardize_address("1 Raffles Place, Singapore 048616", country="SGP")
        score_vo, flags_vo = evaluate_corporate_risk(std_vo)
        assert score_vo >= 0.85
        assert CorporateRiskFlag.RISK_VIRTUAL_OFFICE in flags_vo

        # CMRA mail drop
        std_cmra = standardize_address("27 Old Gloucester St, London WC1N 3AX, UK")
        score_cmra, flags_cmra = evaluate_corporate_risk(std_cmra)
        assert score_cmra >= 0.90
        assert CorporateRiskFlag.RISK_CMRA_MAIL_DROP in flags_cmra

    def test_evaluate_corporate_risk_dict_inputs(self):
        # Dict input without residential
        d1 = {
            "street1": "Baarerstrasse 82",
            "city": "Zug",
            "postal_code": "6300",
            "country": "CHE",
            "is_registered_agent_hub": True,
        }
        score1, flags1 = evaluate_corporate_risk(d1)
        assert score1 >= 0.90
        assert CorporateRiskFlag.RISK_TRUST_FIDUCIARY in flags1

        # Dict input with is_private_residence=True
        d_priv = {
            "street1": "Baarerstrasse 82",
            "city": "Zug",
            "country": "CHE",
            "is_private_residence": True,
            "is_registered_agent_hub": True,
        }
        score_p, flags_p = evaluate_corporate_risk(d_priv)
        assert score_p == 0.40
        assert flags_p == [CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL]
        assert d_priv["is_registered_agent_hub"] is False

    def test_invariant_1_skyscraper_suite_isolation_keys(self):
        # Matching suites but mismatched normalized_address_key
        a1 = StandardizedAddress(
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
        a2 = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="CORRUPTED_OR_DIFFERING_KEY",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 400",
            is_us=True,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        can_merge1, reason1 = can_safely_merge_corporate_entities(a1, a2)
        assert can_merge1 is False
        assert "KEY_MISMATCH" in reason1

        # No secondary units but mismatched normalized_address_key
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
            normalized_address_key="DIFFERING_KEY",
            address_status="standardized",
            raw_street_address="500 Industrial Pkwy",
            is_us=True,
            building_key="500 INDUSTRIAL PKWY||AUSTIN|TX|78701|USA",
        )
        can_merge2, reason2 = can_safely_merge_corporate_entities(a3, a4)
        assert can_merge2 is False
        assert "KEY_MISMATCH" in reason2

    def test_invariant_2_private_residence_protection_end_to_end(self):
        # End-to-end standardization of a private residence
        std_us = standardize_address("1209 N Orange St, Wilmington DE (Private Residence)")
        assert std_us.is_private_residence is True
        assert std_us.is_registered_agent_hub is False
        assert std_us.corporate_risk_score == 0.40
        assert std_us.corporate_risk_flags == [CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL]

        # International private residence
        std_intl = standardize_address("Baarerstrasse 82, Zug, Switzerland (Private Residence)")
        assert std_intl.is_private_residence is True
        assert std_intl.is_registered_agent_hub is False
        assert std_intl.corporate_risk_score == 0.40
        assert std_intl.corporate_risk_flags == [CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL]

    def test_invariant_3_formation_hub_co_location_isolation(self):
        # Trust fiduciary co-location at Baarerstrasse
        a_trust1 = StandardizedAddress(
            street1="BAARERSTRASSE 82",
            street2="",
            city="ZUG",
            state="",
            postal_code="6300",
            country="CHE",
            normalized_address_key="BAARERSTRASSE 82||ZUG||6300|CHE",
            address_status="standardized",
            raw_street_address="Baarerstrasse 82",
            is_us=False,
            building_key="BAARERSTRASSE 82||ZUG||6300|CHE",
            is_registered_agent_hub=True,
        )
        a_trust1.corporate_risk_flags = [CorporateRiskFlag.RISK_TRUST_FIDUCIARY]

        a_trust2 = StandardizedAddress(
            street1="BAARERSTRASSE 82",
            street2="",
            city="ZUG",
            state="",
            postal_code="6300",
            country="CHE",
            normalized_address_key="BAARERSTRASSE 82||ZUG||6300|CHE",
            address_status="standardized",
            raw_street_address="Baarerstrasse 82",
            is_us=False,
            building_key="BAARERSTRASSE 82||ZUG||6300|CHE",
            is_registered_agent_hub=True,
        )
        a_trust2.corporate_risk_flags = [CorporateRiskFlag.RISK_TRUST_FIDUCIARY]

        can_merge_t, reason_t = can_safely_merge_corporate_entities(a_trust1, a_trust2)
        assert can_merge_t is False
        assert "CO_LOCATION_ISOLATION_INVARIANT" in reason_t

        # Dict input for co-location isolation
        d1 = {
            "street1": "BAARERSTRASSE 82",
            "building_key": "B_TRUST",
            "normalized_address_key": "K_TRUST",
            "corporate_risk_flags": [CorporateRiskFlag.RISK_TRUST_FIDUCIARY],
        }
        d2 = {
            "street1": "BAARERSTRASSE 82",
            "building_key": "B_TRUST",
            "normalized_address_key": "K_TRUST",
            "corporate_risk_flags": [CorporateRiskFlag.RISK_TRUST_FIDUCIARY],
        }
        can_merge_d, reason_d = can_safely_merge_corporate_entities(d1, d2)
        assert can_merge_d is False
        assert "CO_LOCATION_ISOLATION_INVARIANT" in reason_d

    def test_international_false_positive_prevention(self):
        # Non-hub UK address
        e_uk = lookup_corporate_registry(street1="10 Downing St", city="London", country="GBR")
        assert e_uk is None

        # Non-hub Dutch address
        e_nl = lookup_corporate_registry(street1="Prinsengracht 263", city="Amsterdam", country="NLD")
        assert e_nl is None

        # Non-hub Swiss address
        e_ch = lookup_corporate_registry(street1="Bahnhofstrasse 10", city="Zug", country="CHE")
        assert e_ch is None

        # Domestic US namesake: London, OH
        e_oh = lookup_corporate_registry(street1="71-75 Shelton St", city="London", state="OH", postal_code="43140")
        assert e_oh is None

        # Domestic US namesake: Amsterdam, NY
        e_ny = lookup_corporate_registry(street1="Keizersgracht 421", city="Amsterdam", state="NY", postal_code="12010")
        assert e_ny is None

    def test_international_matching_edge_cases(self):
        # Country synonym GBR match via "UK" in combined
        e1 = lookup_corporate_registry(street1="71-75 Shelton St", raw_street="71-75 Shelton St UK")
        assert e1 is not None and e1.category == RegistryCategory.FORMATION_AGENT

        # City match via combined regex search
        e2 = lookup_corporate_registry(street1="25A Boulevard Royal", raw_street="25A Boulevard Royal Luxembourg")
        assert e2 is not None and e2.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

        # Postal match via clean prefix
        e3 = lookup_corporate_registry(street1="Baarerstrasse 82", postal_code="6300")
        assert e3 is not None and e3.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

        # Postal match in combined text
        e4 = lookup_corporate_registry(street1="20-22 Wenlock Rd", raw_street="20-22 Wenlock Rd N1 7GU")
        assert e4 is not None and e4.category == RegistryCategory.FORMATION_AGENT

        # Word boundary country regex match: "SGP" in combined
        e5 = lookup_corporate_registry(street1="1 Raffles Place", raw_street="1 Raffles Place SGP")
        assert e5 is not None and e5.category == RegistryCategory.VIRTUAL_OFFICE

        # Country synonym match for Ireland
        e6 = lookup_corporate_registry(street1="1 IFC", raw_street="1 IFC Dublin Ireland")
        assert e6 is not None and e6.category == RegistryCategory.TRUST_FIDUCIARY_COMPANY

    def test_as_dict_14_key_invariant(self):
        expected_keys = [
            "street1", "street2", "city", "state", "postal_code", "country",
            "normalized_address_key", "building_key", "phonetic_key",
            "address_status", "raw_street_address", "is_us",
            "is_private_residence", "is_registered_agent_hub",
        ]

        # 1. Domestic US address
        std_us = standardize_address("1209 N Orange St, Wilmington, DE 19801")
        d_us = std_us.as_dict(include_metadata=False)
        assert len(d_us) == 14
        assert list(d_us.keys()) == expected_keys

        # 2. International address
        std_intl = standardize_address("71-75 Shelton St, London WC2H 9JQ, UK")
        d_intl = std_intl.as_dict(include_metadata=False)
        assert len(d_intl) == 14
        assert list(d_intl.keys()) == expected_keys

        # 3. Private residence address
        std_priv = standardize_address("123 Elm St, Austin, TX 78701 (Private Residence)")
        d_priv = std_priv.as_dict(include_metadata=False)
        assert len(d_priv) == 14
        assert list(d_priv.keys()) == expected_keys

        # 4. Offshore secrecy address
        std_off = standardize_address("Ugland House, South Church St, George Town, Cayman Islands")
        d_off = std_off.as_dict(include_metadata=False)
        assert len(d_off) == 14
        assert list(d_off.keys()) == expected_keys




