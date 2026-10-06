"""Phase 6 Empirical Adversarial Challenge Test Suite.

Author: challenger_6_1
Role: Empirical Challenger & Critic
Purpose: Comprehensive adversarial stress, property testing, ReDoS boundaries,
         249 ISO country resolution, postal validation/extraction edge cases,
         5 regional grammar families, multi-script handling, domestic namesake collision guards,
         14-key contract invariant, and SLA performance/memory limits.
"""

import time
import tracemalloc

from address_standardizer import (
    standardize_address,
    validate_postal_code,
    extract_postal_code,
)
from address_standardizer.international.countries import CountryRegistry
from address_standardizer.international.postal import PostalValidationResult

EXPECTED_14_KEYS = {
    "street1",
    "street2",
    "city",
    "state",
    "postal_code",
    "country",
    "normalized_address_key",
    "building_key",
    "phonetic_key",
    "address_status",
    "raw_street_address",
    "is_us",
    "is_private_residence",
    "is_registered_agent_hub",
}


# ==============================================================================
# Suite 1: Country Registry & Adversarial Country Resolution
# ==============================================================================

class TestCountryRegistryAdversarial:
    """Stress tests and boundary checks for the 249 ISO-3166-1 country catalog."""

    def test_all_249_countries_resolution_matrix(self):
        """Verify all 249 countries resolve via alpha2, alpha3, numeric, name, and aliases."""
        all_countries = CountryRegistry.all_countries()
        assert len(all_countries) == 249, f"Expected 249 countries, got {len(all_countries)}"
        assert len(CountryRegistry.all_iso3()) == 249

        for c in all_countries:
            # Alpha-2 upper and lower
            assert CountryRegistry.get(c.alpha2) == c
            assert CountryRegistry.get(c.alpha2.lower()) == c
            # Alpha-3 upper and lower
            assert CountryRegistry.get(c.alpha3) == c
            assert CountryRegistry.get(c.alpha3.lower()) == c
            # Numeric padded and unpadded
            assert CountryRegistry.get(c.numeric) == c
            unpadded = c.numeric.lstrip("0") or "0"
            assert CountryRegistry.get(unpadded) == c
            # Official name
            assert CountryRegistry.get(c.name) == c
            # Aliases
            for alias in c.aliases:
                assert CountryRegistry.get(alias) == c

    def test_country_resolution_whitespace_and_punctuation(self):
        """Verify whitespace, casing, and punctuation variations resolve cleanly."""
        assert CountryRegistry.get("  USA  ").alpha3 == "USA"
        assert CountryRegistry.get("u.s.a.").alpha3 == "USA"
        assert CountryRegistry.get("u-s-a").alpha3 == "USA"
        assert CountryRegistry.get("\tDEU\n").alpha3 == "DEU"
        assert CountryRegistry.get("  japan  ").alpha3 == "JPN"
        assert CountryRegistry.get("united-kingdom").alpha3 == "GBR"

    def test_country_registry_malformed_inputs(self):
        """Verify malformed and non-existent queries return None without exception."""
        assert CountryRegistry.get(None) is None
        assert CountryRegistry.get("") is None
        assert CountryRegistry.get("   ") is None
        assert CountryRegistry.get("000") is None
        assert CountryRegistry.get("99999") is None
        assert CountryRegistry.get("NonExistentCountryXYZ") is None
        assert CountryRegistry.get("\x00\x00") is None
        assert CountryRegistry.get("!@#$%^&*()") is None

    def test_non_postal_countries_catalog(self):
        """Verify explicit cataloging of non-postal jurisdictions."""
        known_non_postal = ["ARE", "QAT", "BHS", "PAN", "SYC", "COM", "DJI", "ERI", "GMB", "STP", "TUV", "VUT", "SLB", "HKG", "MAC"]
        for alpha3 in known_non_postal:
            assert CountryRegistry.has_postal_codes(alpha3) is False, f"{alpha3} should be non-postal"

        non_postal_all = [c for c in CountryRegistry.all_countries() if not c.has_postal_codes]
        assert len(non_postal_all) == 55, f"Expected 55 non-postal countries, found {len(non_postal_all)}"

    def test_domestic_namesake_collision_with_zip(self):
        """Verify domestic US namesake cities with ZIP resolve strictly to USA."""
        namesakes = [
            ("100 Main St, Paris, TX 75460", "USA"),
            ("50 S Main St, London, OH 43140", "USA"),
            ("123 Farmington Ave, Berlin, CT 06037", "USA"),
            ("100 First St, Montevideo, MN 56265", "USA"),
            ("200 Broad St, Rome, GA 30161", "USA"),
            ("123 Main St, Moscow, ID 83843", "USA"),
            ("456 Oak St, Lebanon, NH 03766", "USA"),
        ]
        for addr, expected_iso in namesakes:
            det = CountryRegistry.detect_country(addr)
            assert det is not None
            assert det.alpha3 == expected_iso, f"detect_country failed for {addr}: got {det.alpha3}"

            std = standardize_address(addr)
            assert std.country == expected_iso, f"standardize_address failed for {addr}: got {std.country}"
            assert std.is_us is True

    def test_domestic_namesake_collision_structured_kwargs(self):
        """Verify structured input kwargs for namesake locations resolve to USA."""
        cases = [
            ("100 Main St", "Paris", "TX"),
            ("50 S Main St", "London", "OH"),
            ("123 Farmington Ave", "Berlin", "CT"),
            ("100 First St", "Montevideo", "MN"),
            ("200 Broad St", "Rome", "GA"),
        ]
        for st, city, state in cases:
            std = standardize_address(street1=st, city=city, state=state)
            assert std.country == "USA"
            assert std.is_us is True

    def test_domestic_namesake_collision_without_zip_fails(self):
        """Verify domestic namesake addresses without 5-digit ZIP resolve cleanly to USA."""
        addr = "100 Main St, Paris, TX"
        std = standardize_address(addr)
        assert std.country == "USA"
        assert std.is_us is True


# ==============================================================================
# Suite 2: Postal Code Validation, Extraction & ReDoS Resilience
# ==============================================================================

class TestPostalValidationAdversarial:
    """Stress tests for postal code validation and extraction across global formats."""

    def test_non_postal_countries_graceful_validation(self):
        """Verify non-postal nations validate empty, None, and arbitrary codes gracefully."""
        for c in ["ARE", "QAT", "BHS", "PAN", "SYC"]:
            assert validate_postal_code(None, c) is True
            assert validate_postal_code("", c) is True
            assert validate_postal_code("12345", c) is True

            res = validate_postal_code(None, c, return_details=True)
            assert isinstance(res, PostalValidationResult)
            assert res.is_valid is True
            assert res.is_non_postal_country is True
            assert "Non-postal" in res.reason

    def test_uk_royal_mail_semantic_boundaries(self):
        """Verify Royal Mail outward and inward character rules."""
        valid_uk = [
            "SW1A 1AA", "EC1A 1BB", "W1A 0AX", "M1 1AA",
            "B33 8TH", "CR2 6XH", "DN55 1PT", "GIR 0AA",
        ]
        for code in valid_uk:
            assert validate_postal_code(code, "GBR") is True, f"Failed valid UK code: {code}"

        # Forbidden inward letters: C, I, K, M, O, V
        for char in ["C", "I", "K", "M", "O", "V"]:
            bad_code = f"SW1A 1A{char}"
            assert validate_postal_code(bad_code, "GBR") is False, f"Expected reject for inward {char}: {bad_code}"

        # Forbidden outward first position: Q, V, X
        for char in ["Q", "V", "X"]:
            bad_code = f"{char}1A 1AA"
            assert validate_postal_code(bad_code, "GBR") is False, f"Expected reject for outward pos 1 {char}: {bad_code}"

    def test_canada_post_semantic_boundaries(self):
        """Verify Canada Post alternating letter-digit pattern and forbidden letters."""
        valid_can = ["K1A 0B1", "H0H 0H0", "M5V 2T6"]
        for code in valid_can:
            assert validate_postal_code(code, "CAN") is True, f"Failed valid CAN code: {code}"

        # Forbidden letters anywhere: D, F, I, O, Q, U
        for char in ["D", "F", "I", "O", "Q", "U"]:
            bad_code = f"K1{char} 0B1"
            assert validate_postal_code(bad_code, "CAN") is False, f"Expected reject for CAN forbidden char {char}"

        # Forbidden starting letters: W, Z
        for char in ["W", "Z"]:
            bad_code = f"{char}1A 0B1"
            assert validate_postal_code(bad_code, "CAN") is False, f"Expected reject for CAN starting char {char}"

    def test_netherlands_postnl_semantic_boundaries(self):
        """Verify PostNL 4-digit + 2-letter constraints and forbidden combinations (SA, SD, SS)."""
        valid_nld = ["1012 JS", "1012JS", "2513 AA", "3011 WN"]
        for code in valid_nld:
            res = validate_postal_code(code, "NLD", return_details=True)
            assert res.is_valid is True
            assert res.formatted_code == f"{code[:4]} {code[-2:]}".replace("  ", " ")

        # Forbidden combinations SA, SD, SS
        for combo in ["SA", "SD", "SS"]:
            bad_code = f"1012 {combo}"
            assert validate_postal_code(bad_code, "NLD") is False, f"Expected reject for PostNL combo {combo}"

    def test_japan_and_brazil_postal_formats(self):
        """Verify Japan (3+4) and Brazil (5+3) postal formats and normalization."""
        # Japan
        assert validate_postal_code("100-8111", "JPN") is True
        assert validate_postal_code("1008111", "JPN") is True
        assert validate_postal_code("100-811", "JPN") is False
        assert validate_postal_code("100-81111", "JPN") is False

        # Brazil
        assert validate_postal_code("01310-200", "BRA") is True
        assert validate_postal_code("01310200", "BRA") is True
        assert validate_postal_code("0131-200", "BRA") is False

    def test_extract_postal_code_from_noisy_lines(self):
        """Verify postal code isolation from unformatted, noisy strings."""
        vectors = [
            ("Deliver to 100 Wall St, New York, NY 10005 USA", "USA", "10005"),
            ("Musterstraße 123, 10115 Berlin, Germany", "DEU", "10115"),
            ("〒100-8111 東京都千代田区千代田1-1", "JPN", "100-8111"),
            ("Av. Paulista, 1578, CEP 01310-200, São Paulo", "BRA", "01310-200"),
            ("10 Downing Street, London SW1A 2AA, UK", "GBR", "SW1A 2AA"),
            ("PO Box 12345, Dubai, UAE", "ARE", None),  # Non-postal country
        ]
        for line, country_hint, expected in vectors:
            extracted = extract_postal_code(line, country_hint)
            assert extracted == expected, f"Failed extraction for '{line}': got {extracted}, expected {expected}"

    def test_redos_safety_long_inputs(self):
        """Verify regexes do not exhibit exponential backtracking on pathological inputs."""
        pathological = [
            "A" * 10000,
            ("1A1 " * 2000) + "1AA",
            ("Calle " * 1000) + "10 # 20-30",
            ("ul. " * 1000) + "Marszalkowska 10/12",
            ("P.O. Box " * 1000) + "12345",
            ("," * 10000),
        ]
        for s in pathological:
            t0 = time.perf_counter()
            _ = extract_postal_code(s, "USA")
            _ = extract_postal_code(s)
            _ = CountryRegistry.detect_country(s)
            elapsed = time.perf_counter() - t0
            assert elapsed < 0.25, f"ReDoS vulnerability detected: took {elapsed:.3f}s on input len {len(s)}"


# ==============================================================================
# Suite 3: Regional Grammar Families & Multi-Script Normalization
# ==============================================================================

class TestRegionalGrammarsAdversarial:
    """Stress tests across all 5 regional grammar families."""

    def test_cjk_grammar_full_width_and_unspaced(self):
        """Verify CJK grammar parses full-width digits, continuous Kanji, and hierarchies."""
        # Full-width digits
        std_fw = standardize_address("東京都千代田区千代田１−２−３", country="JPN")
        assert std_fw.normalized_address_key is not None
        assert std_fw.normalized_address_key.isascii()
        assert len(std_fw.as_dict()) == 14

        # Continuous unspaced Japanese
        std_jp = standardize_address("東京都千代田区千代田1-1", country="JPN")
        assert std_jp.state == "東京都"
        assert std_jp.city == "千代田区"
        assert std_jp.country == "JPN"

        # Chinese administrative hierarchy
        std_cn = standardize_address("北京市海淀区中关村南大街1号", country="CHN")
        assert std_cn.state == "北京市"
        assert std_cn.city == "海淀区"
        assert std_cn.country == "CHN"

        # Korean Road Name address
        std_kr = standardize_address("서울특별시 강남구 테헤란로 152", country="KOR")
        assert std_kr.state == "서울특별시"
        assert std_kr.city == "강남구"
        assert std_kr.country == "KOR"

        # Unbroken digit payload performance (no quadratic backtracking)
        t0 = time.perf_counter()
        std_digits = standardize_address("1" * 10000, country="JPN")
        assert (time.perf_counter() - t0) < 0.25
        assert std_digits.country == "JPN"

    def test_latin_america_grammar_patterns(self):
        """Verify Latin America colonias, manzana/lote, and Colombian # intersection syntax."""
        # Mexico colonia
        std_mx = standardize_address(
            "Av. Insurgentes Sur 1602, Col. Credito Constructor, Benito Juarez, 03940 Ciudad de Mexico, CDMX",
            country="MEX",
        )
        assert std_mx.country == "MEX"
        assert std_mx.postal_code == "03940"

        # Mexico manzana / lote
        std_mzl = standardize_address("Mz 14 Lt 3, Col. San Miguel, Iztapalapa, 09360 CDMX", country="MEX")
        assert std_mzl.country == "MEX"

        # Colombia # syntax
        std_co = standardize_address("Carrera 7 # 71-21, Chapinero, Bogota 110221", country="COL")
        assert std_co.country == "COL"
        assert std_co.postal_code == "110221"

        # Brazil CEP and logradouro
        std_br = standardize_address("Av. Paulista, 1578 - Bela Vista, Sao Paulo - SP, 01310-200", country="BRA")
        assert std_br.country == "BRA"
        assert std_br.postal_code == "01310-200"

    def test_nordic_germanic_grammar_patterns(self):
        """Verify Germanic/Nordic compound street words and Finnish road suffixes."""
        # Germany house number with letter addition
        std_de = standardize_address("Musterstraße 123 B, 10115 Berlin", country="DEU")
        assert std_de.country == "DEU"
        assert std_de.postal_code == "10115"
        assert "123" in std_de.street1

        # Finland road suffix
        std_fi = standardize_address("Mannerheimintie 14 B, 00100 Helsinki", country="FIN")
        assert std_fi.country == "FIN"
        assert std_fi.postal_code == "00100"

        # Netherlands
        std_nl = standardize_address("Keizersgracht 421, 1016 EK Amsterdam", country="NLD")
        assert std_nl.country == "NLD"
        assert std_nl.postal_code == "1016 EK"

    def test_eastern_europe_grammar_patterns_structured(self):
        """Verify Eastern Europe structured parsing across Poland, Czechia, Romania, Greece, Ukraine, Serbia."""
        # Poland structured
        std_pl = standardize_address(street1="ul. Marszalkowska 10/12", city="Warszawa", postal_code="00-590", country="POL")
        assert std_pl.country == "POL"
        assert std_pl.postal_code == "00-590"

        # Czechia
        std_cz = standardize_address("Vaclavske namesti 846/1, 110 00 Praha 1", country="CZE")
        assert std_cz.country == "CZE"
        assert std_cz.postal_code == "110 00"

        # Romania
        std_ro = standardize_address("Strada Mihai Eminescu 15, Bl. 2, Sc. A, Ap. 4, 010512 Bucuresti", country="ROU")
        assert std_ro.country == "ROU"
        assert std_ro.postal_code == "010512"

        # Greece (Greek script preserved, ASCII key folded)
        std_gr = standardize_address("Βασιλίσσης Σοφίας 2, 106 74 Αθήνα", country="GRC")
        assert std_gr.country == "GRC"
        assert any(ord(c) > 127 for c in std_gr.street1)  # Native Greek preserved
        assert std_gr.normalized_address_key.isascii()     # Deterministic ASCII key

        # Ukraine (Cyrillic script preserved, ASCII key folded)
        std_ua = standardize_address("вул. Хрещатик 22, кв. 10, 01001 Київ", country="UKR")
        assert std_ua.country == "UKR"
        assert any(ord(c) > 127 for c in std_ua.street1)  # Native Cyrillic preserved
        assert std_ua.normalized_address_key.isascii()     # Deterministic ASCII key

    def test_eastern_europe_polish_single_line_failure(self):
        """Verify single-line Polish address with inline secondary unit parses postal code cleanly."""
        std_pl = standardize_address("ul. Marszalkowska 10/12 m. 14, 00-590 Warszawa", country="POL")
        assert std_pl.postal_code == "00-590"

    def test_mena_africa_grammar_patterns(self):
        """Verify Saudi Arabia National Address, Egypt, and African metro routing."""
        # Saudi Arabia National Address
        std_sa = standardize_address("7543 King Fahd Road, Al-Malaz, Riyadh 11564", country="SAU")
        assert std_sa.country == "SAU"
        assert std_sa.postal_code == "11564"

        # Egypt
        std_eg = standardize_address("15 Tahrir Street, Dokki, Giza 12311", country="EGY")
        assert std_eg.country == "EGY"

        # South Africa
        std_za = standardize_address("100 Sandton Drive, Sandton, Johannesburg 2196", country="ZAF")
        assert std_za.country == "ZAF"

    def test_mena_africa_uae_dubai_country_collision_failure(self):
        """Verify UAE PO Box single-line address assigns street1 and city cleanly."""
        std_ae_en = standardize_address("P.O. Box 12345, Dubai", country="ARE")
        assert "PO BOX 12345" in std_ae_en.street1
        assert std_ae_en.city == "DUBAI"


# ==============================================================================
# Suite 4: Invariants, UPU Formatting & 14-Key Contract
# ==============================================================================

class TestInvariantsAndContracts:
    """Rigorous contract enforcement: 14 keys, UPU envelopes, and multi-script purity."""

    def test_strict_14_keys_contract_across_all_nations(self):
        """Verify as_dict(include_metadata=False) strictly returns exactly 14 keys across all nations."""
        test_addresses = [
            ("100 Wall St, New York, NY 10005", "USA"),
            ("Musterstraße 123 B, 10115 Berlin", "DEU"),
            ("6-10-1 Roppongi, Minato-ku, Tokyo 106-6132, Japan", "JPN"),
            ("北京市海淀区中关村南大街1号", "CHN"),
            ("서울특별시 강남구 테헤란로 152", "KOR"),
            ("Av. Insurgentes Sur 1602, Col. Credito Constructor, Benito Juarez, 03940 Ciudad de Mexico, CDMX", "MEX"),
            ("Carrera 7 # 71-21, Chapinero, Bogota 110221", "COL"),
            ("Av. Paulista, 1578 - Bela Vista, Sao Paulo - SP, 01310-200", "BRA"),
            ("Vaclavske namesti 846/1, 110 00 Praha 1", "CZE"),
            ("Βασιλίσσης Σοφίας 2, 106 74 Αθήνα", "GRC"),
            ("вул. Хрещатик 22, кв. 10, 01001 Київ", "UKR"),
            ("7543 King Fahd Road, Al-Malaz, Riyadh 11564", "SAU"),
            ("100 Sandton Drive, Sandton, Johannesburg 2196", "ZAF"),
            ("Plot 123 Victoria Island, Lagos 101241", "NGA"),
            ("P.O. Box 30197-00100, Waiyaki Way, Nairobi", "KEN"),
        ]
        for addr, country in test_addresses:
            std = standardize_address(addr, country=country)
            d = std.as_dict(include_metadata=False)
            assert len(d) == 14, f"14-key contract violated for {addr}: got {len(d)} keys"
            assert set(d.keys()) == EXPECTED_14_KEYS

    def test_upu_s42_envelope_layouts(self):
        """Verify UPU S42 envelope layouts match regional conventions."""
        # European postal-first style
        std_de = standardize_address("Musterstraße 123, 10115 Berlin, Germany", country="DEU")
        upu_de = std_de.format_upu()
        assert "10115 BERLIN" in upu_de
        assert "GERMANY" in upu_de

        # Anglo-Saxon postal-last style
        std_us = standardize_address("100 Wall St, New York, NY 10005", country="USA")
        upu_us = std_us.format_upu()
        assert "NEW YORK, NY 10005" in upu_us
        assert "UNITED STATES" in upu_us

        # Non-postal country: omits postal code cleanly without empty line
        std_ae = standardize_address("Sheikh Zayed Road, Dubai", country="ARE")
        upu_ae = std_ae.format_upu()
        lines = upu_ae.strip().split("\n")
        assert all(line.strip() for line in lines), "UPU envelope should not contain blank lines"
        assert "UNITED ARAB EMIRATES" in upu_ae


# ==============================================================================
# Suite 5: Performance & Memory SLA Verification
# ==============================================================================

class TestPerformanceAndMemorySLA:
    """Verify latency, throughput, and memory bounds for international standardization."""

    def test_batch_latency_and_memory_sla(self):
        """Verify sub-millisecond execution and bounded RSS across 1,000 international records."""
        records = [
            ("100 Wall St, New York, NY 10005", "USA"),
            ("Musterstraße 123 B, 10115 Berlin", "DEU"),
            ("6-10-1 Roppongi, Minato-ku, Tokyo 106-6132, Japan", "JPN"),
            ("Av. Insurgentes Sur 1602, Col. Credito Constructor, Benito Juarez, 03940 Ciudad de Mexico, CDMX", "MEX"),
            ("Vaclavske namesti 846/1, 110 00 Praha 1", "CZE"),
            ("7543 King Fahd Road, Al-Malaz, Riyadh 11564", "SAU"),
            ("Carrera 7 # 71-21, Chapinero, Bogota 110221", "COL"),
            ("Sheikh Zayed Road, Dubai", "ARE"),
        ]

        tracemalloc.start()
        t0 = time.perf_counter()
        N = 1000
        for i in range(N):
            addr, c = records[i % len(records)]
            std = standardize_address(addr, country=c)
            assert len(std.as_dict()) == 14

        total_time = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        avg_lat_ms = (total_time / N) * 1000
        peak_mb = peak / (1024 * 1024)

        assert avg_lat_ms < 5.0, f"Average latency SLA violated: {avg_lat_ms:.3f}ms (threshold: < 5.0ms)"
        assert peak_mb < 50.0, f"Peak memory SLA violated: {peak_mb:.2f}MB (threshold: < 50.0MB)"
