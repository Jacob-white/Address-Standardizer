"""
Generate 1,000-record categorized golden evaluation dataset for Address Standardizer.
Conforms to USPS Publication 28, ISO 19160-4, and the project architectural specification.
"""

import json
import os
from typing import List, Dict, Any


def build_golden_dataset() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    # =========================================================================
    # CAT-01: Clean US Standard (200 records)
    # =========================================================================
    us_cities = [
        ("New York", "NY", "10001"), ("Los Angeles", "CA", "90001"), ("Chicago", "IL", "60601"),
        ("Houston", "TX", "77001"), ("Phoenix", "AZ", "85001"), ("Philadelphia", "PA", "19101"),
        ("San Antonio", "TX", "78201"), ("San Diego", "CA", "92101"), ("Dallas", "TX", "75201"),
        ("San Jose", "CA", "95101"), ("Austin", "TX", "78701"), ("Jacksonville", "FL", "32201"),
        ("San Francisco", "CA", "94101"), ("Columbus", "OH", "43201"), ("Indianapolis", "IN", "46201"),
        ("Fort Worth", "TX", "76101"), ("Charlotte", "NC", "28201"), ("Seattle", "WA", "98101"),
        ("Denver", "CO", "80201"), ("Washington", "DC", "20001"), ("Boston", "MA", "02101"),
        ("El Paso", "TX", "79901"), ("Nashville", "TN", "37201"), ("Detroit", "MI", "48201"),
        ("Oklahoma City", "OK", "73101"), ("Portland", "OR", "97201"), ("Las Vegas", "NV", "89101"),
        ("Memphis", "TN", "38101"), ("Louisville", "KY", "40201"), ("Baltimore", "MD", "21201"),
        ("Milwaukee", "WI", "53201"), ("Albuquerque", "NM", "87101"), ("Tucson", "AZ", "85701"),
        ("Fresno", "CA", "93701"), ("Sacramento", "CA", "95801"), ("Mesa", "AZ", "85201"),
        ("Kansas City", "MO", "64101"), ("Atlanta", "GA", "30301"), ("Omaha", "NE", "68101"),
        ("Colorado Springs", "CO", "80901")
    ]

    street_templates = [
        ("Main Street", "MAIN ST", "M500"),
        ("Wall Street", "WALL ST", "W400"),
        ("Broadway", "BROADWAY", "B630"),
        ("Park Avenue", "PARK AVE", "P620"),
        ("Market Street", "MARKET ST", "M623"),
        ("Oak Street", "OAK ST", "O200"),
        ("Pine Street", "PINE ST", "P500"),
        ("Maple Avenue", "MAPLE AVE", "M140"),
        ("Cedar Road", "CEDAR RD", "C360"),
        ("Elm Street", "ELM ST", "E450"),
    ]

    sec_units = [
        ("", ""),
        ("Suite 100", "STE 100"),
        ("Suite 500", "STE 500"),
        ("Apt 4B", "APT 4B"),
        ("Unit 12", "UNIT 12"),
    ]

    # Generate 200 CAT-01 records
    cat1_count = 0
    for city, state, zip5 in us_cities:
        for st_name, st_norm, snd in street_templates:
            for sec_raw, sec_norm in sec_units:
                cat1_count += 1
                rec_id = f"CAT-01-{cat1_count:03d}"
                num = str(100 + cat1_count)
                raw_st1 = f"{num} {st_name}"
                norm_st1 = f"{num} {st_norm}"
                norm_city = city.upper()
                norm_key = f"{norm_st1}|{sec_norm}|{norm_city}|{state}|{zip5}|USA"
                bld_key = f"{norm_st1}||{norm_city}|{state}|{zip5}|USA"
                phonetic = f"{num}|{snd}|{zip5}"

                # Alternate structured input vs comma-delimited single string input
                if cat1_count % 2 == 1:
                    raw_input = {
                        "street1": raw_st1,
                        "street2": sec_raw if sec_raw else None,
                        "city": city,
                        "state": state,
                        "postal_code": zip5,
                        "country": "USA"
                    }
                else:
                    combined = f"{raw_st1}, {sec_raw + ', ' if sec_raw else ''}{city}, {state} {zip5}"
                    raw_input = {
                        "street1": combined,
                        "street2": None,
                        "city": None,
                        "state": None,
                        "postal_code": None,
                        "country": None
                    }

                records.append({
                    "test_id": rec_id,
                    "category": "clean_us_standard",
                    "raw_input": raw_input,
                    "expected_output": {
                        "street1": norm_st1,
                        "street2": sec_norm,
                        "city": norm_city,
                        "state": state,
                        "postal_code": zip5,
                        "country": "USA",
                        "normalized_address_key": norm_key,
                        "building_key": bld_key,
                        "phonetic_key": phonetic,
                        "address_status": "standardized",
                        "is_us": True,
                        "is_registered_agent_hub": False
                    }
                })
                if cat1_count >= 200:
                    break
            if cat1_count >= 200:
                break
        if cat1_count >= 200:
            break

    # =========================================================================
    # CAT-02: Missing Commas / Delimiters (150 records)
    # =========================================================================
    multi_cities = [
        ("New York", "NY", "10005"),
        ("Salt Lake City", "UT", "84101"),
        ("Elk Grove Village", "IL", "60007"),
        ("Kansas City", "MO", "64101"),
        ("San Francisco", "CA", "94104"),
        ("Los Angeles", "CA", "90012"),
        ("Baton Rouge", "LA", "70801"),
        ("Oklahoma City", "OK", "73102"),
        ("Colorado Springs", "CO", "80903"),
        ("Virginia Beach", "VA", "23451"),
        ("Jersey City", "NJ", "07302"),
        ("Fort Worth", "TX", "76102"),
        ("Saint Paul", "MN", "55101"),
        ("San Antonio", "TX", "78205"),
        ("San Diego", "CA", "92101"),
    ]

    streets_c2 = [
        ("100 Main Street", "100 MAIN ST", "100", "M500"),
        ("555 California Street", "555 CALIFORNIA ST", "555", "C416"),
        ("123 Martin Luther King Jr Boulevard", "123 MARTIN LUTHER KING JR BLVD", "123", "M635"),
        ("450 Lexington Avenue", "450 LEXINGTON AVE", "450", "L252"),
        ("700 South Flower Street", "700 S FLOWER ST", "700", "F460"),
        ("800 West Peach Tree Street", "800 W PEACH TREE ST", "800", "P200"),
        ("1200 Grand Avenue", "1200 GRAND AVE", "1200", "G653"),
        ("250 Montgomery Street", "250 MONTGOMERY ST", "250", "M532"),
        ("999 Third Avenue", "999 3RD AVE", "999", "#3"),
        ("1000 Fifth Avenue", "1000 5TH AVE", "1000", "#5"),
    ]

    units_c2 = [
        ("", ""),
        ("Suite 200", "STE 200"),
        ("Apt 4B", "APT 4B"),
        ("Unit 101", "UNIT 101"),
        ("Floor 14", "FL 14"),
    ]

    cat2_count = 0
    for city, state, zip5 in multi_cities:
        for raw_s, norm_s, hnum, snd in streets_c2:
            for u_raw, u_norm in units_c2:
                cat2_count += 1
                rec_id = f"CAT-02-{cat2_count:03d}"
                # Construct raw string without commas
                if u_raw:
                    raw_str = f"{raw_s} {u_raw} {city} {state} {zip5}"
                else:
                    raw_str = f"{raw_s} {city} {state} {zip5}"

                norm_city = city.upper()
                norm_key = f"{norm_s}|{u_norm}|{norm_city}|{state}|{zip5}|USA"
                bld_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
                p_key = f"{hnum}|{snd}|{zip5}"

                records.append({
                    "test_id": rec_id,
                    "category": "missing_commas_delimiters",
                    "raw_input": {
                        "street1": raw_str,
                        "street2": None,
                        "city": None,
                        "state": None,
                        "postal_code": None,
                        "country": None
                    },
                    "expected_output": {
                        "street1": norm_s,
                        "street2": u_norm,
                        "city": norm_city,
                        "state": state,
                        "postal_code": zip5,
                        "country": "USA",
                        "normalized_address_key": norm_key,
                        "building_key": bld_key,
                        "phonetic_key": p_key,
                        "address_status": "standardized",
                        "is_us": True,
                        "is_registered_agent_hub": False
                    }
                })
                if cat2_count >= 150:
                    break
            if cat2_count >= 150:
                break
        if cat2_count >= 150:
            break

    # =========================================================================
    # CAT-03: Secondary Units & PMB (150 records)
    # =========================================================================
    pmb_and_units = [
        # (raw_st, norm_st1, norm_st2, house_num, snd)
        ("100 Main St PMB 456", "100 MAIN ST", "PMB 456", "100", "M500"),
        ("200 Park Ave Private Mailbox 789", "200 PARK AVE", "PMB 789", "200", "P620"),
        ("300 Market St PMB #101", "300 MARKET ST", "PMB 101", "300", "M623"),
        ("400 Oak St # 500", "400 OAK ST", "STE 500", "400", "O200"),
        ("500 Pine St #B", "500 PINE ST", "STE B", "500", "P500"),
        ("100 1/2 Main St", "100 1/2 MAIN ST", "", "100 1/2", "M500"),
        ("200 1/2 Park Ave", "200 1/2 PARK AVE", "", "200 1/2", "P620"),
        ("300 1/4 Market St", "300 1/4 MARKET ST", "", "300 1/4", "M623"),
        ("400 3/4 Elm St", "400 3/4 ELM ST", "", "400 3/4", "E450"),
        ("100 Main St#101", "100 MAIN ST", "STE 101", "100", "M500"),
        ("200 Park Ave Apt.4B", "200 PARK AVE", "APT 4B", "200", "P620"),
        ("300 Market St STE-400", "300 MARKET ST", "STE 400", "300", "M623"),
        ("100 Main St Basement", "100 MAIN ST", "BSMT", "100", "M500"),
        ("200 Park Ave Penthouse", "200 PARK AVE", "PH", "200", "P620"),
        ("300 Market St Penthouse B", "300 MARKET ST", "PH B", "300", "M623"),
        ("400 Elm St Lobby", "400 ELM ST", "LBBY", "400", "E450"),
        ("500 Pine St Rear", "500 PINE ST", "REAR", "500", "P500"),
        ("600 Cedar Rd Mezzanine", "600 CEDAR RD", "MEZZ", "600", "C360"),
        ("700 Walnut St Lower", "700 WALNUT ST", "LOWR", "700", "W453"),
        ("800 Chestnut St Upper", "800 CHESTNUT ST", "UPPR", "800", "C235"),
        ("900 Spruce St Front", "900 SPRUCE ST", "FRNT", "900", "S162"),
        ("1000 Ash St Side", "1000 ASH ST", "SIDE", "1000", "A200"),
        ("1100 Birch St Office 3", "1100 BIRCH ST", "OFC 3", "1100", "B620"),
        ("1200 Maple Ave Ste. 200", "1200 MAPLE AVE", "STE 200", "1200", "M140"),
        ("1300 Willow Rd Apt#5C", "1300 WILLOW RD", "APT 5C", "1300", "W400"),
    ]

    cat3_count = 0
    city_pool = us_cities[:6]  # 6 cities * 25 patterns = 150 records
    for city, state, zip5 in city_pool:
        for raw_st, n_s1, n_s2, hnum, snd in pmb_and_units:
            cat3_count += 1
            rec_id = f"CAT-03-{cat3_count:03d}"
            norm_city = city.upper()
            norm_key = f"{n_s1}|{n_s2}|{norm_city}|{state}|{zip5}|USA"
            bld_key = f"{n_s1}||{norm_city}|{state}|{zip5}|USA"
            p_key = f"{hnum}|{snd}|{zip5}"

            raw_addr = f"{raw_st}, {city}, {state} {zip5}"
            records.append({
                "test_id": rec_id,
                "category": "secondary_units_pmb",
                "raw_input": {
                    "street1": raw_addr,
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                },
                "expected_output": {
                    "street1": n_s1,
                    "street2": n_s2,
                    "city": norm_city,
                    "state": state,
                    "postal_code": zip5,
                    "country": "USA",
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": True,
                    "is_registered_agent_hub": False
                }
            })
            if cat3_count >= 150:
                break
        if cat3_count >= 150:
            break

    # =========================================================================
    # CAT-04: Hyphenated Street Numbers (100 records)
    # =========================================================================
    # Queens grid numbers, building ranges, attached secondary units
    queens_and_hyphens = [
        # Queens NY addresses
        ("123-45 82nd Ave", "Kew Gardens", "NY", "11415", "123-45 82ND AVE", "", "123-45", "#82"),
        ("14-02 150th St", "Whitestone", "NY", "11357", "14-02 150TH ST", "", "14-02", "#150"),
        ("71-11 Austin St", "Forest Hills", "NY", "11375", "71-11 AUSTIN ST", "", "71-11", "A235"),
        ("30-30 47th Ave", "Long Island City", "NY", "11101", "30-30 47TH AVE", "", "30-30", "#47"),
        ("90-15 Queens Blvd", "Elmhurst", "NY", "11373", "90-15 QUEENS BLVD", "", "90-15", "Q520"),
        ("41-25 Kissena Blvd", "Flushing", "NY", "11355", "41-25 KISSENA BLVD", "", "41-25", "K250"),
        ("108-01 Corona Ave", "Corona", "NY", "11368", "108-01 CORONA AVE", "", "108-01", "C650"),
        ("82-11 37th Ave", "Jackson Heights", "NY", "11372", "82-11 37TH AVE", "", "82-11", "#37"),
        ("21-50 31st St", "Astoria", "NY", "11105", "21-50 31ST ST", "", "21-50", "#31"),
        ("163-18 Jamaica Ave", "Jamaica", "NY", "11432", "163-18 JAMAICA AVE", "", "163-18", "J520"),
        # Address numerical ranges
        ("100-102 Main St", "New York", "NY", "10001", "100-102 MAIN ST", "", "100-102", "M500"),
        ("500-504 Broadway", "New York", "NY", "10012", "500-504 BROADWAY", "", "500-504", "B630"),
        ("20-22 Market St", "Philadelphia", "PA", "19106", "20-22 MARKET ST", "", "20-22", "M623"),
        ("1200-1204 Grand Ave", "Kansas City", "MO", "64106", "1200-1204 GRAND AVE", "", "1200-1204", "G653"),
        ("350-352 5th Ave", "New York", "NY", "10118", "350-352 5TH AVE", "", "350-352", "#5"),
        # Suffix-attached secondary units (e.g. Main St-4B -> Main St, Apt 4B)
        ("100 Main St-4B", "New York", "NY", "10001", "100 MAIN ST", "APT 4B", "100", "M500"),
        ("200 Park Ave-Ste 200", "New York", "NY", "10166", "200 PARK AVE", "STE 200", "200", "P620"),
        ("500 Market St-Unit 12", "San Francisco", "CA", "94105", "500 MARKET ST", "UNIT 12", "500", "M623"),
        ("450 Lexington Ave-Fl 14", "New York", "NY", "10017", "450 LEXINGTON AVE", "FL 14", "450", "L252"),
        ("300 Pine St-Apt 1A", "Seattle", "WA", "98101", "300 PINE ST", "APT 1A", "300", "P500"),
    ]

    cat4_count = 0
    # Duplicate template with 5 variations each to reach 100 records
    for i in range(5):
        for raw_s, city, st, zip5, norm_s1, norm_s2, hnum, snd in queens_and_hyphens:
            cat4_count += 1
            rec_id = f"CAT-04-{cat4_count:03d}"
            norm_city = city.upper()
            norm_key = f"{norm_s1}|{norm_s2}|{norm_city}|{st}|{zip5}|USA"
            bld_key = f"{norm_s1}||{norm_city}|{st}|{zip5}|USA"
            p_key = f"{hnum}|{snd}|{zip5}"

            # Format raw input
            raw_addr = f"{raw_s}, {city}, {st} {zip5}"
            records.append({
                "test_id": rec_id,
                "category": "hyphenated_street_numbers",
                "raw_input": {
                    "street1": raw_addr,
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                },
                "expected_output": {
                    "street1": norm_s1,
                    "street2": norm_s2,
                    "city": norm_city,
                    "state": st,
                    "postal_code": zip5,
                    "country": "USA",
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": True,
                    "is_registered_agent_hub": False
                }
            })
            if cat4_count >= 100:
                break
        if cat4_count >= 100:
            break

    # =========================================================================
    # CAT-05: Directional Ambiguities (100 records)
    # =========================================================================
    # Positional directional grammar: '500 South St' must NOT become '500 S ST'
    directionals_cases = [
        # (raw_s, norm_s, house_num, snd, city, state, zip)
        ("500 South Street", "500 SOUTH ST", "500", "S300", "Philadelphia", "PA", "19147"),
        ("100 North Street", "100 NORTH ST", "100", "N630", "Boston", "MA", "02109"),
        ("200 East Street", "200 EAST ST", "200", "E230", "Pittsfield", "MA", "01201"),
        ("300 West Street", "300 WEST ST", "300", "W230", "New York", "NY", "10014"),
        ("100 North East Street", "100 NORTH EAST ST", "100", "N630", "Indianapolis", "IN", "46204"),
        ("200 North West Street", "200 NORTH WEST ST", "200", "N630", "Alexandria", "VA", "22314"),
        ("300 South East Street", "300 SOUTH EAST ST", "300", "S300", "Amherst", "MA", "01002"),
        ("400 South West Street", "400 SOUTH WEST ST", "400", "S300", "Falls Church", "VA", "22046"),
        ("100 South Boulevard", "100 SOUTH BLVD", "100", "S300", "Richmond", "VA", "23220"),
        ("200 North Boulevard", "200 NORTH BLVD", "200", "N630", "Tampa", "FL", "33602"),
        ("500 South Main Street", "500 S MAIN ST", "500", "M500", "Los Angeles", "CA", "90013"),
        ("100 North Michigan Avenue", "100 N MICHIGAN AVE", "100", "M225", "Chicago", "IL", "60601"),
        ("200 East 42nd Street", "200 E 42ND ST", "200", "#42", "New York", "NY", "10017"),
        ("300 West 34th Street", "300 W 34TH ST", "300", "#34", "New York", "NY", "10001"),
        ("100 Main Street NW", "100 MAIN ST NW", "100", "M500", "Washington", "DC", "20001"),
        ("200 Pennsylvania Avenue NW", "200 PENNSYLVANIA AVE NW", "200", "P524", "Washington", "DC", "20004"),
        ("300 K Street NE", "300 K ST NE", "300", "K000", "Washington", "DC", "20002"),
        ("400 4th Street SW", "400 4TH ST SW", "400", "#4", "Washington", "DC", "20024"),
        ("500 M Street SE", "500 M ST SE", "500", "M000", "Washington", "DC", "20003"),
        ("600 South Park Avenue", "600 S PARK AVE", "600", "P620", "Winter Park", "FL", "32789"),
    ]

    cat5_count = 0
    for i in range(5):
        for raw_s, norm_s, hnum, snd, city, state, zip5 in directionals_cases:
            cat5_count += 1
            rec_id = f"CAT-05-{cat5_count:03d}"
            norm_city = city.upper()
            norm_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
            bld_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
            p_key = f"{hnum}|{snd}|{zip5}"

            raw_addr = f"{raw_s}, {city}, {state} {zip5}"
            records.append({
                "test_id": rec_id,
                "category": "directional_ambiguities",
                "raw_input": {
                    "street1": raw_addr,
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                },
                "expected_output": {
                    "street1": norm_s,
                    "street2": "",
                    "city": norm_city,
                    "state": state,
                    "postal_code": zip5,
                    "country": "USA",
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": True,
                    "is_registered_agent_hub": False
                }
            })
            if cat5_count >= 100:
                break
        if cat5_count >= 100:
            break

    # =========================================================================
    # CAT-06: Dual-Address Lines (75 records)
    # =========================================================================
    dual_lines = [
        ("100 Main Street", "PO Box 456", "New York", "NY", "10001", "100 MAIN ST", "PO BOX 456", "100", "M500"),
        ("200 Park Avenue", "PO Box 123", "New York", "NY", "10166", "200 PARK AVE", "PO BOX 123", "200", "P620"),
        ("500 Market Street", "PO Box 789", "San Francisco", "CA", "94105", "500 MARKET ST", "PO BOX 789", "500", "M623"),
        ("123 Maple St", "PO Box 55", "Springfield", "IL", "62701", "123 MAPLE ST", "PO BOX 55", "123", "M140"),
        ("750 Elm Street", "PO Box 999", "Dallas", "TX", "75202", "750 ELM ST", "PO BOX 999", "750", "E450"),
    ]

    cat6_count = 0
    for i in range(15):
        for s1, s2, city, state, zip5, ns1, ns2, hnum, snd in dual_lines:
            cat6_count += 1
            rec_id = f"CAT-06-{cat6_count:03d}"
            norm_city = city.upper()
            norm_key = f"{ns1}|{ns2}|{norm_city}|{state}|{zip5}|USA"
            bld_key = f"{ns1}||{norm_city}|{state}|{zip5}|USA"
            p_key = f"{hnum}|{snd}|{zip5}"

            # Alternate passing separate street1/street2 vs combined single string
            if cat6_count % 2 == 1:
                raw_input = {
                    "street1": s1,
                    "street2": s2,
                    "city": city,
                    "state": state,
                    "postal_code": zip5,
                    "country": "USA"
                }
            else:
                raw_input = {
                    "street1": f"{s1} {s2}, {city}, {state} {zip5}",
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                }

            records.append({
                "test_id": rec_id,
                "category": "dual_address_lines",
                "raw_input": raw_input,
                "expected_output": {
                    "street1": ns1,
                    "street2": ns2,
                    "city": norm_city,
                    "state": state,
                    "postal_code": zip5,
                    "country": "USA",
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": True,
                    "is_registered_agent_hub": False
                }
            })
            if cat6_count >= 75:
                break
        if cat6_count >= 75:
            break

    # =========================================================================
    # CAT-07: Typo Scenarios (75 records)
    # =========================================================================
    typo_cases = [
        ("100 Main Strteet", "100 MAIN ST", "100", "M500", "New York", "NY", "10001"),
        ("200 Park Avnue", "200 PARK AVE", "200", "P620", "New York", "NY", "10166"),
        ("300 Ocean Boulvard", "300 OCEAN BLVD", "300", "O250", "Miami", "FL", "33139"),
        ("400 Market Stret", "400 MARKET ST", "400", "M623", "San Francisco", "CA", "94105"),
        ("500 Elm Aveneu", "500 ELM AVE", "500", "E450", "Dallas", "TX", "75201"),
        ("600 Pine Raod", "600 PINE RD", "600", "P500", "Seattle", "WA", "98101"),
        ("700 Cedar Driv", "700 CEDAR DR", "700", "C360", "Austin", "TX", "78701"),
        ("800 Maple Lne", "800 MAPLE LN", "800", "M140", "Denver", "CO", "80201"),
        ("900 Walnut Curcle", "900 WALNUT CIR", "900", "W453", "Atlanta", "GA", "30301"),
        ("1000 Birch Pkway", "1000 BIRCH PKWY", "1000", "B620", "Chicago", "IL", "60601"),
        ("100 Nort Main St", "100 N MAIN ST", "100", "M500", "Boston", "MA", "02108"),
        ("200 Sout Elm St", "200 S ELM ST", "200", "E450", "Dallas", "TX", "75201"),
        ("300 Wes 42nd St", "300 W 42ND ST", "300", "#42", "New York", "NY", "10036"),
        ("400 Eas Market St", "400 E MARKET ST", "400", "M623", "Louisville", "KY", "40202"),
        ("500 Norh Broadway", "500 N BROADWAY", "500", "B630", "Saint Louis", "MO", "63102"),
    ]

    cat7_count = 0
    for i in range(5):
        for raw_s, norm_s, hnum, snd, city, state, zip5 in typo_cases:
            cat7_count += 1
            rec_id = f"CAT-07-{cat7_count:03d}"
            norm_city = city.upper()
            norm_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
            bld_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
            p_key = f"{hnum}|{snd}|{zip5}"

            raw_addr = f"{raw_s}, {city}, {state} {zip5}"
            records.append({
                "test_id": rec_id,
                "category": "typo_scenarios",
                "raw_input": {
                    "street1": raw_addr,
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                },
                "expected_output": {
                    "street1": norm_s,
                    "street2": "",
                    "city": norm_city,
                    "state": state,
                    "postal_code": zip5,
                    "country": "USA",
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": True,
                    "is_registered_agent_hub": False
                }
            })
            if cat7_count >= 75:
                break
        if cat7_count >= 75:
            break

    # =========================================================================
    # CAT-08: Rural Routes & Highways (75 records)
    # =========================================================================
    rural_cases = [
        # (raw_s, norm_s, hnum, snd, city, state, zip)
        ("RR 2 Box 152", "RR 2 BOX 152", "RR 2", "B200", "Greenup", "IL", "62428"),
        ("RR 1 Box 40", "RR 1 BOX 40", "RR 1", "B200", "Altamont", "IL", "62411"),
        ("RR 3 Box 88", "RR 3 BOX 88", "RR 3", "B200", "Toledo", "IL", "62468"),
        ("HC 64 Box 23", "HC 64 BOX 23", "HC 64", "B200", "Moab", "UT", "84532"),
        ("HC 72 Box 101", "HC 72 BOX 101", "HC 72", "B200", "Tok", "AK", "99780"),
        ("HC 33 Box 450", "HC 33 BOX 450", "HC 33", "B200", "Rolla", "MO", "65401"),
        ("County Road 500 N", "COUNTY RD 500 N", "", "C530", "North Vernon", "IN", "47265"),
        ("County Road 300 E", "COUNTY RD 300 E", "", "C530", "Columbus", "IN", "47201"),
        ("County Road 100 S", "COUNTY RD 100 S", "", "C530", "Greensburg", "IN", "47240"),
        ("County Road 25", "COUNTY RD 25", "", "C530", "Findlay", "OH", "45840"),
        ("CR 400 W", "CR 400 W", "", "C600", "Kokomo", "IN", "46901"),
        ("CR 12", "CR 12", "", "C600", "Elkhart", "IN", "46514"),
        ("State Route 4", "STATE ROUTE 4", "", "S330", "Dayton", "OH", "45402"),
        ("State Route 32", "STATE ROUTE 32", "", "S330", "Batavia", "OH", "45103"),
        ("SR 60", "SR 60", "", "S600", "Zanesville", "OH", "43701"),
    ]

    cat8_count = 0
    for i in range(5):
        for raw_s, norm_s, hnum, snd, city, state, zip5 in rural_cases:
            cat8_count += 1
            rec_id = f"CAT-08-{cat8_count:03d}"
            norm_city = city.upper()
            norm_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
            bld_key = f"{norm_s}||{norm_city}|{state}|{zip5}|USA"
            p_key = f"{hnum}|{snd}|{zip5}".lstrip("|")

            raw_addr = f"{raw_s}, {city}, {state} {zip5}"
            records.append({
                "test_id": rec_id,
                "category": "rural_routes",
                "raw_input": {
                    "street1": raw_addr,
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                },
                "expected_output": {
                    "street1": norm_s,
                    "street2": "",
                    "city": norm_city,
                    "state": state,
                    "postal_code": zip5,
                    "country": "USA",
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": True,
                    "is_registered_agent_hub": False
                }
            })
            if cat8_count >= 75:
                break
        if cat8_count >= 75:
            break

    # =========================================================================
    # CAT-09: International & Non-Standard (75 records)
    # =========================================================================
    intl_cases = [
        # Puerto Rico Urbanization
        {
            "raw": "Urb Las Gladiolas 123 Calle Flamboyan, San Juan, PR 00926",
            "s1": "URB LAS GLADIOLAS 123 CALLE FLAMBOYAN", "s2": "",
            "city": "SAN JUAN", "st": "PR", "zip": "00926", "country": "USA", "is_us": True,
            "hub": False, "hnum": "123", "snd": "C400"
        },
        {
            "raw": "Urb Jardines 456 Calle Luna, Caguas, PR 00725",
            "s1": "URB JARDINES 456 CALLE LUNA", "s2": "",
            "city": "CAGUAS", "st": "PR", "zip": "00725", "country": "USA", "is_us": True,
            "hub": False, "hnum": "456", "snd": "C400"
        },
        {
            "raw": "Urb Dos Pinos 789 Calle Sol, Ponce, PR 00716",
            "s1": "URB DOS PINOS 789 CALLE SOL", "s2": "",
            "city": "PONCE", "st": "PR", "zip": "00716", "country": "USA", "is_us": True,
            "hub": False, "hnum": "789", "snd": "C400"
        },
        # Military
        {
            "raw": "Unit 1234 Box 5678, APO, AE 09012",
            "s1": "UNIT 1234 BOX 5678", "s2": "",
            "city": "APO", "st": "AE", "zip": "09012", "country": "USA", "is_us": True,
            "hub": False, "hnum": "1234", "snd": "B200"
        },
        {
            "raw": "Unit 4321 Box 8765, FPO, AP 96515",
            "s1": "UNIT 4321 BOX 8765", "s2": "",
            "city": "FPO", "st": "AP", "zip": "96515", "country": "USA", "is_us": True,
            "hub": False, "hnum": "4321", "snd": "B200"
        },
        # Canada
        {
            "raw": "100 King St W Suite 500, Toronto, ON M5X 1A9, Canada",
            "s1": "100 KING ST W", "s2": "STE 500",
            "city": "TORONTO", "st": "ON", "zip": "M5X 1A9", "country": "CAN", "is_us": False,
            "hub": False, "hnum": "100", "snd": "K520"
        },
        {
            "raw": "200 Bay Street Floor 14, Toronto, ON M5J 2J2, Canada",
            "s1": "200 BAY ST", "s2": "FL 14",
            "city": "TORONTO", "st": "ON", "zip": "M5J 2J2", "country": "CAN", "is_us": False,
            "hub": False, "hnum": "200", "snd": "B000"
        },
        # UK
        {
            "raw": "150 High Street Apt 4, Oxford, OX1 4DJ, United Kingdom",
            "s1": "150 HIGH ST", "s2": "APT 4",
            "city": "OXFORD", "st": "", "zip": "OX1 4DJ", "country": "GBR", "is_us": False,
            "hub": False, "hnum": "150", "snd": "H200"
        },
        {
            "raw": "25 Bank Street Suite 100, London, E14 5JP, UK",
            "s1": "25 BANK ST", "s2": "STE 100",
            "city": "LONDON", "st": "", "zip": "E14 5JP", "country": "GBR", "is_us": False,
            "hub": False, "hnum": "25", "snd": "B520"
        },
        # Registered Agent Hubs - Domestic
        {
            "raw": "1209 North Orange St, Wilmington, DE 19801",
            "s1": "1209 N ORANGE ST", "s2": "",
            "city": "WILMINGTON", "st": "DE", "zip": "19801", "country": "USA", "is_us": True,
            "hub": True, "hnum": "1209", "snd": "O652"
        },
        {
            "raw": "251 Little Falls Dr, Wilmington, DE 19808",
            "s1": "251 LITTLE FALLS DR", "s2": "",
            "city": "WILMINGTON", "st": "DE", "zip": "19808", "country": "USA", "is_us": True,
            "hub": True, "hnum": "251", "snd": "L340"
        },
        {
            "raw": "30 N Gould St, Sheridan, WY 82801",
            "s1": "30 N GOULD ST", "s2": "",
            "city": "SHERIDAN", "st": "WY", "zip": "82801", "country": "USA", "is_us": True,
            "hub": True, "hnum": "30", "snd": "G430"
        },
        {
            "raw": "160 Greentree Dr, Dover, DE 19904",
            "s1": "160 GREENTREE DR", "s2": "",
            "city": "DOVER", "st": "DE", "zip": "19904", "country": "USA", "is_us": True,
            "hub": True, "hnum": "160", "snd": "G653"
        },
        # Registered Agent Hubs - Offshore (Cayman Islands)
        {
            "raw": "Ugland House, PO Box 309, George Town, KY1-1104, Cayman Islands",
            "s1": "UGLAND HOUSE", "s2": "PO BOX 309",
            "city": "GEORGE TOWN", "st": "", "zip": "KY1-1104", "country": "CYM", "is_us": False,
            "hub": True, "hnum": "", "snd": "U245"
        },
        {
            "raw": "Clifton House, 75 Fort St, George Town, KY1-1108, Cayman Islands",
            "s1": "75 FORT ST", "s2": "CLIFTON HOUSE",
            "city": "GEORGE TOWN", "st": "", "zip": "KY1-1108", "country": "CYM", "is_us": False,
            "hub": True, "hnum": "75", "snd": "F630"
        },
        {
            "raw": "Ugland House, South Church St, George Town, KY1-1104, Cayman Islands",
            "s1": "SOUTH CHURCH ST", "s2": "UGLAND HOUSE",
            "city": "GEORGE TOWN", "st": "", "zip": "KY1-1104", "country": "CYM", "is_us": False,
            "hub": True, "pkey": "C620|KY1-1104"
        },
        # Registered Agent & Secrecy Hubs - Production Additions
        {
            "raw": "1221 Brickell Ave, Miami, FL 33131",
            "s1": "1221 BRICKELL AVE", "s2": "",
            "city": "MIAMI", "st": "FL", "zip": "33131", "country": "USA", "is_us": True,
            "hub": False, "pkey": "1221|B624|33131"
        },
        {
            "raw": "100 Park Ave, New York, NY 10017",
            "s1": "100 PARK AVE", "s2": "",
            "city": "NEW YORK", "st": "NY", "zip": "10017", "country": "USA", "is_us": True,
            "hub": False, "pkey": "100|P620|10017"
        },
        # Compliance Privacy Placeholders
        {
            "raw": "Private Residence, Miami, FL 33131",
            "s1": "PRIVATE RESIDENCE", "s2": "",
            "city": "MIAMI", "st": "FL", "zip": "33131", "country": "USA", "is_us": True,
            "hub": False, "pkey": "P613|33131"
        },
        {
            "raw": "Confidential, New York, NY 10005",
            "s1": "PRIVATE RESIDENCE", "s2": "",
            "city": "NEW YORK", "st": "NY", "zip": "10005", "country": "USA", "is_us": True,
            "hub": False, "pkey": "P613|10005"
        },
        # International Metro Disambiguation (Erroneous US Defaults)
        {
            "raw": "Rambla Republica de Mexico 6135, Montevideo, USA",
            "s1": "RAMBLA REPUBLICA DE MEXICO 6135", "s2": "",
            "city": "MONTEVIDEO", "st": "", "zip": "", "country": "URY", "is_us": False,
            "hub": False, "pkey": "R514|MONTEVIDEO"
        },
        {
            "raw": "Calle 72 No. 10-07, Bogota, USA",
            "s1": "CALLE 72 NO. 10-07", "s2": "",
            "city": "BOGOTA", "st": "", "zip": "", "country": "COL", "is_us": False,
            "hub": False, "pkey": "C400|BOGOTA"
        },
        {
            "raw": "Avenida Corrientes 1234, Buenos Aires, USA",
            "s1": "AVENIDA CORRIENTES 1234", "s2": "",
            "city": "BUENOS AIRES", "st": "", "zip": "", "country": "ARG", "is_us": False,
            "hub": False, "pkey": "A153|BUENOS AIRES"
        },
        {
            "raw": "Kenyatta Avenue, Nairobi, USA",
            "s1": "KENYATTA AVE", "s2": "",
            "city": "NAIROBI", "st": "", "zip": "", "country": "KEN", "is_us": False,
            "hub": False, "pkey": "K530|NAIROBI"
        },
        {
            "raw": "Marszalkowska 100, Warsaw, USA",
            "s1": "MARSZALKOWSKA 100", "s2": "",
            "city": "WARSAW", "st": "", "zip": "", "country": "POL", "is_us": False,
            "hub": False, "pkey": "M624|WARSAW"
        },
    ]

    cat9_count = 0
    for i in range(3):
        for item in intl_cases:
            cat9_count += 1
            rec_id = f"CAT-09-{cat9_count:03d}"
            norm_key = f"{item['s1']}|{item['s2']}|{item['city']}|{item['st']}|{item['zip']}|{item['country']}"
            bld_key = f"{item['s1']}||{item['city']}|{item['st']}|{item['zip']}|{item['country']}"
            if "pkey" in item:
                p_key = item["pkey"]
            elif item.get('hnum'):
                p_key = f"{item['hnum']}|{item['snd']}|{item['zip']}"
            else:
                p_key = f"{item['snd']}|{item['zip']}"

            records.append({
                "test_id": rec_id,
                "category": "international_nonstandard",
                "raw_input": {
                    "street1": item['raw'],
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None
                },
                "expected_output": {
                    "street1": item['s1'],
                    "street2": item['s2'],
                    "city": item['city'],
                    "state": item['st'],
                    "postal_code": item['zip'],
                    "country": item['country'],
                    "normalized_address_key": norm_key,
                    "building_key": bld_key,
                    "phonetic_key": p_key,
                    "address_status": "standardized",
                    "is_us": item['is_us'],
                    "is_registered_agent_hub": item['hub']
                }
            })
            if cat9_count >= 75:
                break
        if cat9_count >= 75:
            break

    return records


def main():
    records = build_golden_dataset()
    print(f"Generated {len(records)} golden records across categories:")
    from collections import Counter
    counts = Counter(r["category"] for r in records)
    for cat, cnt in counts.items():
        print(f"  - {cat}: {cnt}")

    bench_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(bench_dir, "data"), exist_ok=True)
    target_1 = os.path.join(bench_dir, "golden_dataset.json")
    target_2 = os.path.join(bench_dir, "data", "golden_evaluation_dataset.json")

    with open(target_1, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    with open(target_2, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"Saved dataset to {target_1} and {target_2}")


if __name__ == "__main__":
    main()
