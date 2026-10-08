"""Tests for Phase 3 deliverability intelligence and commercial multi-unit catalog.

Covers:
- Cataloged institutional commercial towers in offline index
- Missing secondary unit triggering DPVFootnote.N1 (REQUIRES_SECONDARY)
- Secondary prompt fields: secondary_prompt_required, prompt_message, suggested_secondary_units
- Resolution when secondary unit is supplied
"""


from address_standardizer import standardize_address
from address_standardizer.delivery import DPVFootnote, evaluate_delivery_intelligence
from address_standardizer.offline_index import get_default_offline_index


class TestCommercialTowerCatalog:
    """Verifies that top institutional commercial towers are cataloged in the offline index."""

    def test_tower_seed_records_exist(self):
        index = get_default_offline_index()

        towers_to_check = [
            ("1450 BRICKELL AVE", "MIAMI", "FL", "33131"),
            ("555 CALIFORNIA ST", "SAN FRANCISCO", "CA", "94104"),
            ("40 WALL ST", "NEW YORK", "NY", "10005"),
            ("111 S WACKER DR", "CHICAGO", "IL", "60606"),
            ("227 W MONROE ST", "CHICAGO", "IL", "60606"),
            ("520 MADISON AVE", "NEW YORK", "NY", "10022"),
            ("590 MADISON AVE", "NEW YORK", "NY", "10022"),
            ("1330 AVE OF THE AMERICAS", "NEW YORK", "NY", "10019"),
            ("ONE EMBARCADERO CENTER", "SAN FRANCISCO", "CA", "94111"),
            ("100 WILSHIRE BLVD", "SANTA MONICA", "CA", "90401"),
            ("ONE WORLD TRADE CENTER", "NEW YORK", "NY", "10007"),
            ("1111 BRICKELL AVE", "MIAMI", "FL", "33131"),
            ("110 N WACKER DR", "CHICAGO", "IL", "60606"),
            ("777 BRICKELL AVE", "MIAMI", "FL", "33131"),
            ("11111 SANTA MONICA BLVD", "LOS ANGELES", "CA", "90025"),
        ]

        for st1, city, state, zip5 in towers_to_check:
            rec = index.resolve_coordinates(f"{st1}||{city}|{state}|{zip5}|USA")
            assert rec is not None, f"Expected {st1} in {city}, {state} to be indexed"
            assert rec.is_multi_unit is True


class TestCommercialTowerSecondaryPrompt:
    """Verifies that missing secondary unit triggers DPVFootnote.N1 and prompt metadata."""

    def test_unsuited_tower_triggers_prompt(self):
        # 1450 Brickell Ave without suite
        res = standardize_address("1450 Brickell Ave, Miami, FL 33131")
        assert res.address_status == "standardized"
        assert res.secondary_prompt_required is True
        assert res.prompt_message is not None
        assert "N1" in res.dpv_footnotes
        assert len(res.suggested_secondary_units) > 0

        di = evaluate_delivery_intelligence(res)
        assert di.secondary_prompt_required is True
        assert DPVFootnote.N1 in di.dpv_footnotes

    def test_suited_tower_clears_prompt(self):
        # 1450 Brickell Ave with suite 1400
        res = standardize_address("1450 Brickell Ave Ste 1400, Miami, FL 33131")
        assert res.address_status == "standardized"
        assert res.secondary_prompt_required is False
        assert res.prompt_message is None
        assert res.street2 == "STE 1400"
        assert "N1" not in res.dpv_footnotes

    def test_unsuited_california_st_tower(self):
        res = standardize_address("555 California St, San Francisco, CA 94104")
        assert res.address_status == "standardized"
        assert res.secondary_prompt_required is True
        assert "555 CALIFORNIA ST" in res.street1

    def test_unsuited_40_wall_st(self):
        res = standardize_address("40 Wall St, New York, NY 10005")
        assert res.address_status == "standardized"
        assert res.secondary_prompt_required is True

    def test_unsuited_one_world_trade_center(self):
        res = standardize_address("One World Trade Center, New York, NY 10007")
        assert res.address_status == "standardized"
        assert res.secondary_prompt_required is True
        assert res.prompt_message == "Requires Suite / Apartment Number"
        assert "85TH FLOOR" in res.suggested_secondary_units

