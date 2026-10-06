"""Canonical ground-truth records for categories INTL-02 through INTL-06."""

from typing import Any, Dict, List

CANONICAL_INTL_02_TO_06: List[Dict[str, Any]] = [
  {
    "test_id": "INTL-02-001",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 1",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "RR 1",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "RR 1|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "RR 1||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "RR 1|R000|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-002",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "113 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "113 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "113 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "113 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "113|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-003",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "126 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "126 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "126 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "126 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "126|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-004",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "139 boulevard René-Lévesque Ouest, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "139 BD RENÉ-LÉVESQUE O",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "139 BD RENE-LEVESQUE O|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "139 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "139|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-005",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "152 boulevard Saint-Laurent",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "152 BD SAINT-LAURENT",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "152 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "152 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "152|B300|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-006",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 2, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RR 2",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "RR 2|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "RR 2||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "RR 2|R000|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-007",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "178 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "178 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "178 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "178 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "178|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-008",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "191 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "191 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "191 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "191 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "191|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-009",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "204 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "204 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "204 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "204 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "204|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-010",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "217 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "217 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "217 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "217 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "217|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-011",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "SS 1",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "SS 1",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "SS 1|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "SS 1||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "S000|K1A 0B1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-012",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "243 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "243 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "243 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "243 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "243|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-013",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "256 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "256 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "256 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "256 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "256|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-014",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "269 rue Saint-Jean, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "269 RUE SAINT-JEAN",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "269 RUE SAINT-JEAN|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "269 RUE SAINT-JEAN||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "269|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-015",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "282 avenue Mont-Royal Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "282 AV MONT-ROYAL E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "282 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "282 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "282|A100|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-016",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "MR 4, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MR 4",
      "street2": "STE 400",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "MR 4|STE 400|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "MR 4||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "M600|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-017",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "308 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "308 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "308 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "308 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "308|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-018",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "321 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "321 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "321 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "321 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "321|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-019",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "334 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "334 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "334 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "334 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "334|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-020",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "347 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "347 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "347 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "347 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "347|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-021",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "STN MAIN",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "STA MAIN",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "STA MAIN|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "STA MAIN||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "S300|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-022",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "373 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "373 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "373 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "373 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "373|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-023",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "386 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "386 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "386 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "386 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "386|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-024",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "399 rue Sherbrooke Est, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "399 RUE SHERBROOKE E",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "399 RUE SHERBROOKE E|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "399 RUE SHERBROOKE E||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "399|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-025",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "412 rue Saint-Denis",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "412 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "412 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "412 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "412|R000|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-026",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "COMP 12, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COMP 12",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "COMP 12|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "COMP 12||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "C510|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-027",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "438 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "438 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "438 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "438 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "438|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-028",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "451 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "451 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "451 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "451 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "451|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-029",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "464 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "464 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "464 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "464 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "464|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-030",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "477 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "477 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "477 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "477 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "477|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-031",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "CP 123",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "PO BOX 123",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "PO BOX 123|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "PO BOX 123||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "POB 123|K1A 0",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-032",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "503 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "503 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "503 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "503 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "503|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-033",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "516 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "516 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "516 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "516 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "516|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-034",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "529 rue Sainte-Catherine Ouest, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "529 RUE SAINTE-CATHERINE O",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "529 RUE SAINTE-CATHERINE O|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "529 RUE SAINTE-CATHERINE O||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "529|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-035",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "542 boulevard Charest Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "542 BD CHAREST E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "542 BD CHAREST E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "542 BD CHAREST E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "542|B300|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-036",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "PO Box 450, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "SUITE 400",
      "street2": "PO BOX 450",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "SUITE 400|PO BOX 450|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "SUITE 400||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "S300|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-037",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "568 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "568 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "568 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "568 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "568|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-038",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "581 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "581 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "581 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "581 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "581|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-039",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "594 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "594 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "594 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "594 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "594|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-040",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "607 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "607 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "607 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "607 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "607|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-041",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 1",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "RR 1",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "RR 1|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "RR 1||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "RR 1|R000|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-042",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "633 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "633 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "633 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "633 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "633|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-043",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "646 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "646 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "646 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "646 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "646|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-044",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "659 boulevard René-Lévesque Ouest, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "659 BD RENÉ-LÉVESQUE O",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "659 BD RENE-LEVESQUE O|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "659 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "659|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-045",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "672 boulevard Saint-Laurent",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "672 BD SAINT-LAURENT",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "672 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "672 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "672|B300|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-046",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 2, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RR 2",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "RR 2|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "RR 2||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "RR 2|R000|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-047",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "698 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "698 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "698 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "698 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "698|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-048",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "711 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "711 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "711 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "711 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "711|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-049",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "724 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "724 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "724 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "724 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "724|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-050",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "737 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "737 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "737 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "737 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "737|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-051",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "SS 1",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "SS 1",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "SS 1|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "SS 1||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "S000|K1A 0B1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-052",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "763 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "763 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "763 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "763 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "763|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-053",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "776 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "776 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "776 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "776 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "776|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-054",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "789 rue Saint-Jean, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "789 RUE SAINT-JEAN",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "789 RUE SAINT-JEAN|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "789 RUE SAINT-JEAN||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "789|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-055",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "802 avenue Mont-Royal Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "802 AV MONT-ROYAL E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "802 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "802 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "802|A100|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-056",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "MR 4, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MR 4",
      "street2": "STE 400",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "MR 4|STE 400|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "MR 4||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "M600|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-057",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "828 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "828 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "828 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "828 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "828|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-058",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "841 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "841 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "841 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "841 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "841|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-059",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "854 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "854 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "854 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "854 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "854|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-060",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "867 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "867 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "867 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "867 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "867|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-061",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "STN MAIN",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "STA MAIN",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "STA MAIN|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "STA MAIN||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "S300|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-062",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "893 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "893 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "893 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "893 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "893|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-063",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "906 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "906 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "906 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "906 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "906|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-064",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "919 rue Sherbrooke Est, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "919 RUE SHERBROOKE E",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "919 RUE SHERBROOKE E|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "919 RUE SHERBROOKE E||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "919|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-065",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "932 rue Saint-Denis",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "932 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "932 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "932 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "932|R000|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-066",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "COMP 12, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COMP 12",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "COMP 12|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "COMP 12||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "C510|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-067",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "108 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "108 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "108 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "108 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "108|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-068",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "121 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "121 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "121 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "121 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "121|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-069",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "134 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "134 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "134 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "134 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "134|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-070",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "147 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "147 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "147 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "147 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "147|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-071",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "CP 123",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "PO BOX 123",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "PO BOX 123|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "PO BOX 123||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "POB 123|K1A 0",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-072",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "173 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "173 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "173 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "173 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "173|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-073",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "186 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "186 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "186 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "186 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "186|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-074",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "199 rue Sainte-Catherine Ouest, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "199 RUE SAINTE-CATHERINE O",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "199 RUE SAINTE-CATHERINE O|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "199 RUE SAINTE-CATHERINE O||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "199|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-075",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "212 boulevard Charest Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "212 BD CHAREST E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "212 BD CHAREST E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "212 BD CHAREST E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "212|B300|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-076",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "PO Box 450, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "SUITE 400",
      "street2": "PO BOX 450",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "SUITE 400|PO BOX 450|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "SUITE 400||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "S300|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-077",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "238 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "238 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "238 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "238 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "238|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-078",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "251 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "251 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "251 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "251 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "251|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-079",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "264 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "264 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "264 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "264 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "264|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-080",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "277 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "277 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "277 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "277 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "277|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-081",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 1",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "RR 1",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "RR 1|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "RR 1||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "RR 1|R000|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-082",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "303 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "303 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "303 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "303 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "303|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-083",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "316 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "316 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "316 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "316 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "316|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-084",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "329 boulevard René-Lévesque Ouest, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "329 BD RENÉ-LÉVESQUE O",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "329 BD RENE-LEVESQUE O|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "329 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "329|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-085",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "342 boulevard Saint-Laurent",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "342 BD SAINT-LAURENT",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "342 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "342 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "342|B300|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-086",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 2, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RR 2",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "RR 2|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "RR 2||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "RR 2|R000|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-087",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "368 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "368 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "368 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "368 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "368|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-088",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "381 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "381 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "381 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "381 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "381|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-089",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "394 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "394 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "394 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "394 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "394|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-090",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "407 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "407 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "407 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "407 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "407|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-091",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "SS 1",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "SS 1",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "SS 1|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "SS 1||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "S000|K1A 0B1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-092",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "433 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "433 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "433 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "433 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "433|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-093",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "446 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "446 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "446 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "446 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "446|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-094",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "459 rue Saint-Jean, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "459 RUE SAINT-JEAN",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "459 RUE SAINT-JEAN|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "459 RUE SAINT-JEAN||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "459|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-095",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "472 avenue Mont-Royal Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "472 AV MONT-ROYAL E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "472 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "472 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "472|A100|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-096",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "MR 4, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MR 4",
      "street2": "STE 400",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "MR 4|STE 400|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "MR 4||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "M600|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-097",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "498 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "498 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "498 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "498 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "498|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-098",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "511 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "511 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "511 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "511 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "511|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-099",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "524 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "524 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "524 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "524 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "524|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-100",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "537 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "537 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "537 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "537 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "537|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-101",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "STN MAIN",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "STA MAIN",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "STA MAIN|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "STA MAIN||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "S300|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-102",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "563 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "563 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "563 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "563 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "563|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-103",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "576 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "576 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "576 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "576 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "576|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-104",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "589 rue Sherbrooke Est, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "589 RUE SHERBROOKE E",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "589 RUE SHERBROOKE E|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "589 RUE SHERBROOKE E||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "589|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-105",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "602 rue Saint-Denis",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "602 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "602 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "602 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "602|R000|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-106",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "COMP 12, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COMP 12",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "COMP 12|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "COMP 12||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "C510|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-107",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "628 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "628 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "628 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "628 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "628|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-108",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "641 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "641 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "641 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "641 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "641|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-109",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "654 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "654 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "654 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "654 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "654|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-110",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "667 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "667 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "667 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "667 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "667|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-111",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "CP 123",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "PO BOX 123",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "PO BOX 123|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "PO BOX 123||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "POB 123|K1A 0",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-112",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "693 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "693 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "693 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "693 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "693|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-113",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "706 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "706 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "706 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "706 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "706|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-114",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "719 rue Sainte-Catherine Ouest, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "719 RUE SAINTE-CATHERINE O",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "719 RUE SAINTE-CATHERINE O|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "719 RUE SAINTE-CATHERINE O||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "719|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-115",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "732 boulevard Charest Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "732 BD CHAREST E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "732 BD CHAREST E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "732 BD CHAREST E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "732|B300|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-116",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "PO Box 450, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "SUITE 400",
      "street2": "PO BOX 450",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "SUITE 400|PO BOX 450|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "SUITE 400||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "S300|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-117",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "758 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "758 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "758 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "758 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "758|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-118",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "771 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "771 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "771 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "771 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "771|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-119",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "784 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "784 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "784 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "784 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "784|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-120",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "797 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "797 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "797 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "797 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "797|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-121",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 1",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "RR 1",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "RR 1|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "RR 1||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "RR 1|R000|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-122",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "823 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "823 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "823 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "823 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "823|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-123",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "836 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "836 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "836 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "836 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "836|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-124",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "849 boulevard René-Lévesque Ouest, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "849 BD RENÉ-LÉVESQUE O",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "849 BD RENE-LEVESQUE O|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "849 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "849|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-125",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "862 boulevard Saint-Laurent",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "862 BD SAINT-LAURENT",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "862 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "862 BD SAINT-LAURENT||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "862|B300|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-126",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "RR 2, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RR 2",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "RR 2|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "RR 2||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "RR 2|R000|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-127",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "888 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "888 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "888 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "888 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "888|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-128",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "901 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "901 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "901 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "901 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "901|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-129",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "914 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "914 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "914 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "914 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "914|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-130",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "927 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "927 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "927 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "927 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "927|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-131",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "SS 1",
      "street2": "Suite 400",
      "city": "Ottawa",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "SS 1",
      "street2": "STE 400",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1A 0B1",
      "country": "CAN",
      "normalized_address_key": "SS 1|STE 400|OTTAWA|ON|K1A 0B1|CAN",
      "building_key": "SS 1||OTTAWA|ON|K1A 0B1|CAN",
      "phonetic_key": "S000|K1A 0B1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-132",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "103 Queen Street East, Suite 1200, Ottawa, ON K1P 5J2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "103 QUEEN ST E",
      "street2": "STE 1200",
      "city": "OTTAWA",
      "state": "ON",
      "postal_code": "K1P 5J2",
      "country": "CAN",
      "normalized_address_key": "103 QUEEN ST E|STE 1200|OTTAWA|ON|K1P 5J2|CAN",
      "building_key": "103 QUEEN ST E||OTTAWA|ON|K1P 5J2|CAN",
      "phonetic_key": "103|Q500|K1P 5J2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-133",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "116 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Edmonton",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "116 BLOOR ST W",
      "street2": "APT 2B",
      "city": "EDMONTON",
      "state": "AB",
      "postal_code": "T5J 0N3",
      "country": "CAN",
      "normalized_address_key": "116 BLOOR ST W|APT 2B|EDMONTON|AB|T5J 0N3|CAN",
      "building_key": "116 BLOOR ST W||EDMONTON|AB|T5J 0N3|CAN",
      "phonetic_key": "116|B460|T5J 0N3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-134",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "129 rue Saint-Jean, Unit 5, Québec, QC G1R 4P5, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "129 RUE SAINT-JEAN",
      "street2": "UNIT 5",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1R 4P5",
      "country": "CAN",
      "normalized_address_key": "129 RUE SAINT-JEAN|UNIT 5|QUEBEC|QC|G1R 4P5|CAN",
      "building_key": "129 RUE SAINT-JEAN||QUEBEC|QC|G1R 4P5|CAN",
      "phonetic_key": "129|R000|G1R 4P5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-135",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "142 avenue Mont-Royal Est",
      "street2": None,
      "city": "Québec",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "142 AV MONT-ROYAL E",
      "street2": "",
      "city": "QUÉBEC",
      "state": "QC",
      "postal_code": "G1K 7A8",
      "country": "CAN",
      "normalized_address_key": "142 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "building_key": "142 AV MONT-ROYAL E||QUEBEC|QC|G1K 7A8|CAN",
      "phonetic_key": "142|A100|G1K 7A8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-136",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "MR 4, Suite 400, Winnipeg, MB R3C 3Z3, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MR 4",
      "street2": "STE 400",
      "city": "WINNIPEG",
      "state": "MB",
      "postal_code": "R3C 3Z3",
      "country": "CAN",
      "normalized_address_key": "MR 4|STE 400|WINNIPEG|MB|R3C 3Z3|CAN",
      "building_key": "MR 4||WINNIPEG|MB|R3C 3Z3|CAN",
      "phonetic_key": "M600|R3C 3Z3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-137",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "168 Robson Street",
      "street2": "Suite 1200",
      "city": "Halifax",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "168 ROBSON ST",
      "street2": "STE 1200",
      "city": "HALIFAX",
      "state": "NS",
      "postal_code": "B3J 3N5",
      "country": "CAN",
      "normalized_address_key": "168 ROBSON ST|STE 1200|HALIFAX|NS|B3J 3N5|CAN",
      "building_key": "168 ROBSON ST||HALIFAX|NS|B3J 3N5|CAN",
      "phonetic_key": "168|R125|B3J 3N5",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-138",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "181 Bay Street, Apt 2B, Regina, SK S4P 3Y2, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "181 BAY ST",
      "street2": "APT 2B",
      "city": "REGINA",
      "state": "SK",
      "postal_code": "S4P 3Y2",
      "country": "CAN",
      "normalized_address_key": "181 BAY ST|APT 2B|REGINA|SK|S4P 3Y2|CAN",
      "building_key": "181 BAY ST||REGINA|SK|S4P 3Y2|CAN",
      "phonetic_key": "181|B000|S4P 3Y2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-139",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "194 Yonge Street",
      "street2": "Unit 5",
      "city": "Fredericton",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "194 YONGE ST",
      "street2": "UNIT 5",
      "city": "FREDERICTON",
      "state": "NB",
      "postal_code": "E3B 4Y7",
      "country": "CAN",
      "normalized_address_key": "194 YONGE ST|UNIT 5|FREDERICTON|NB|E3B 4Y7|CAN",
      "building_key": "194 YONGE ST||FREDERICTON|NB|E3B 4Y7|CAN",
      "phonetic_key": "194|Y520|E3B 4Y7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-140",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "207 Front Street East, St. John's, NL A1C 5T7, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "207 FRONT ST E",
      "street2": "",
      "city": "ST JOHN'S",
      "state": "NL",
      "postal_code": "A1C 5T7",
      "country": "CAN",
      "normalized_address_key": "207 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "building_key": "207 FRONT ST E||ST JOHN'S|NL|A1C 5T7|CAN",
      "phonetic_key": "207|F653|A1C 5T7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-141",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "STN MAIN",
      "street2": "Suite 400",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "STA MAIN",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "STA MAIN|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "STA MAIN||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "S300|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-142",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "233 Queen Street East, Suite 1200, Toronto, ON M5V 2T6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "233 QUEEN ST E",
      "street2": "STE 1200",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5V 2T6",
      "country": "CAN",
      "normalized_address_key": "233 QUEEN ST E|STE 1200|TORONTO|ON|M5V 2T6|CAN",
      "building_key": "233 QUEEN ST E||TORONTO|ON|M5V 2T6|CAN",
      "phonetic_key": "233|Q500|M5V 2T6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-143",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "246 Bloor Street West",
      "street2": "Apt 2B",
      "city": "Toronto",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "246 BLOOR ST W",
      "street2": "APT 2B",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5H 2N2",
      "country": "CAN",
      "normalized_address_key": "246 BLOOR ST W|APT 2B|TORONTO|ON|M5H 2N2|CAN",
      "building_key": "246 BLOOR ST W||TORONTO|ON|M5H 2N2|CAN",
      "phonetic_key": "246|B460|M5H 2N2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-144",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "259 rue Sherbrooke Est, Unit 5, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "259 RUE SHERBROOKE E",
      "street2": "UNIT 5",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "259 RUE SHERBROOKE E|UNIT 5|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "259 RUE SHERBROOKE E||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "259|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-145",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "272 rue Saint-Denis",
      "street2": None,
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "272 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H3B 4G7",
      "country": "CAN",
      "normalized_address_key": "272 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "building_key": "272 RUE SAINT-DENIS||MONTREAL|QC|H3B 4G7|CAN",
      "phonetic_key": "272|R000|H3B 4G7",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-146",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "COMP 12, Suite 400, Montréal, QC H2Y 1V4, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COMP 12",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2Y 1V4",
      "country": "CAN",
      "normalized_address_key": "COMP 12|STE 400|MONTREAL|QC|H2Y 1V4|CAN",
      "building_key": "COMP 12||MONTREAL|QC|H2Y 1V4|CAN",
      "phonetic_key": "C510|H2Y 1V4",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-147",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "298 Robson Street",
      "street2": "Suite 1200",
      "city": "Vancouver",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "298 ROBSON ST",
      "street2": "STE 1200",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6B 2W9",
      "country": "CAN",
      "normalized_address_key": "298 ROBSON ST|STE 1200|VANCOUVER|BC|V6B 2W9|CAN",
      "building_key": "298 ROBSON ST||VANCOUVER|BC|V6B 2W9|CAN",
      "phonetic_key": "298|R125|V6B 2W9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-148",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "311 Bay Street, Apt 2B, Vancouver, BC V6C 3E8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "311 BAY ST",
      "street2": "APT 2B",
      "city": "VANCOUVER",
      "state": "BC",
      "postal_code": "V6C 3E8",
      "country": "CAN",
      "normalized_address_key": "311 BAY ST|APT 2B|VANCOUVER|BC|V6C 3E8|CAN",
      "building_key": "311 BAY ST||VANCOUVER|BC|V6C 3E8|CAN",
      "phonetic_key": "311|B000|V6C 3E8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-149",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "324 Yonge Street",
      "street2": "Unit 5",
      "city": "Calgary",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "324 YONGE ST",
      "street2": "UNIT 5",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2P 3N9",
      "country": "CAN",
      "normalized_address_key": "324 YONGE ST|UNIT 5|CALGARY|AB|T2P 3N9|CAN",
      "building_key": "324 YONGE ST||CALGARY|AB|T2P 3N9|CAN",
      "phonetic_key": "324|Y520|T2P 3N9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-02-150",
    "category": "canada_bilingual_rural",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "337 Front Street East, Calgary, AB T2G 0P6, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "337 FRONT ST E",
      "street2": "",
      "city": "CALGARY",
      "state": "AB",
      "postal_code": "T2G 0P6",
      "country": "CAN",
      "normalized_address_key": "337 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "building_key": "337 FRONT ST E||CALGARY|AB|T2G 0P6|CAN",
      "phonetic_key": "337|F653|T2G 0P6",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-001",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Musterstraße 12",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10115",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 12",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10115",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 12||BERLIN||10115|DEU",
      "building_key": "MUSTERSTRASSE 12||BERLIN||10115|DEU",
      "phonetic_key": "M236|10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-002",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Friedrichstraße 43-45, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "FRIEDRICHSTRASSE 43",
      "street2": "APT 45",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "FRIEDRICHSTRASSE 43|APT 45|BERLIN||10117|DEU",
      "building_key": "FRIEDRICHSTRASSE 43||BERLIN||10117|DEU",
      "phonetic_key": "F636|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-003",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Kurfürstendamm 195",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10707",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KURFÜRSTENDAMM 195",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10707",
      "country": "DEU",
      "normalized_address_key": "KURFURSTENDAMM 195||BERLIN||10707|DEU",
      "building_key": "KURFURSTENDAMM 195||BERLIN||10707|DEU",
      "phonetic_key": "K616|10707",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-004",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Unter den Linden 77, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UNTER DEN LINDEN 77",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "UNTER DEN LINDEN 77||BERLIN||10117|DEU",
      "building_key": "UNTER DEN LINDEN 77||BERLIN||10117|DEU",
      "phonetic_key": "U536|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-005",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Am Hauptbahnhof 5a",
      "street2": None,
      "city": "Frankfurt am Main",
      "state": None,
      "postal_code": "60329",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "AM HAUPTBAHNHOF 5A",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60329",
      "country": "DEU",
      "normalized_address_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "building_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "phonetic_key": "A500|60329",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-006",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Zeil 106, 60311 Frankfurt am Main, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "ZEIL 106",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60311",
      "country": "DEU",
      "normalized_address_key": "ZEIL 106||FRANKFURT AM MAIN||60311|DEU",
      "building_key": "ZEIL 106||FRANKFURT AM MAIN||60311|DEU",
      "phonetic_key": "Z400|60311",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-007",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Maximilianstraße 25",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MAXIMILIANSTRASSE 25",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MAXIMILIANSTRASSE 25||MUNCHEN||80331|DEU",
      "building_key": "MAXIMILIANSTRASSE 25||MUNCHEN||80331|DEU",
      "phonetic_key": "M254|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-008",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Brienner Straße 14, 80539 München, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BRIENNER STRASSE 14",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80539",
      "country": "DEU",
      "normalized_address_key": "BRIENNER STRASSE 14||MUNCHEN||80539|DEU",
      "building_key": "BRIENNER STRASSE 14||MUNCHEN||80539|DEU",
      "phonetic_key": "B656|80539",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-009",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Jungfernstieg 14",
      "street2": None,
      "city": "Hamburg",
      "state": None,
      "postal_code": "20354",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "JUNGFERNSTIEG 14",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20354",
      "country": "DEU",
      "normalized_address_key": "JUNGFERNSTIEG 14||HAMBURG||20354|DEU",
      "building_key": "JUNGFERNSTIEG 14||HAMBURG||20354|DEU",
      "phonetic_key": "J521|20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-010",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 21, 20457 Hamburg, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 21",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20457",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 21||HAMBURG||20457|DEU",
      "building_key": "GROSSE BLEICHEN 21||HAMBURG||20457|DEU",
      "phonetic_key": "G620|20457",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-011",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 60",
      "street2": None,
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 60",
      "street2": "",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 60||DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 60||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-012",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Hohe Straße 68, 50667 Köln, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HOHE STRASSE 68",
      "street2": "",
      "city": "KÖLN",
      "state": "",
      "postal_code": "50667",
      "country": "DEU",
      "normalized_address_key": "HOHE STRASSE 68||KOLN||50667|DEU",
      "building_key": "HOHE STRASSE 68||KOLN||50667|DEU",
      "phonetic_key": "H000|50667",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-013",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "142 Boulevard Saint-Germain",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75006",
      "country": "France"
    },
    "expected_output": {
      "street1": "142 BD SAINT-GERMAIN",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75006",
      "country": "FRA",
      "normalized_address_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "building_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "phonetic_key": "142|B300|75006",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-014",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "25 Rue de Rivoli, 75004 Paris, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "25 RUE DE RIVOLI",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75004",
      "country": "FRA",
      "normalized_address_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "building_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "phonetic_key": "25|R000|75004",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-015",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75008",
      "country": "France"
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75008",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "phonetic_key": "80|R000|75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-016",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "10 Place Bellecour, 69002 Lyon, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "10 PL BELLECOUR",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "building_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "phonetic_key": "10|P400|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-017",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "50 La Canebière",
      "street2": None,
      "city": "Marseille",
      "state": None,
      "postal_code": "13001",
      "country": "France"
    },
    "expected_output": {
      "street1": "50 LA CANEBIÈRE",
      "street2": "",
      "city": "MARSEILLE",
      "state": "",
      "postal_code": "13001",
      "country": "FRA",
      "normalized_address_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "building_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "phonetic_key": "50|L000|13001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-018",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "15 Rue Sainte-Catherine, 33000 Bordeaux, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 RUE SAINTE-CATHERINE",
      "street2": "",
      "city": "BORDEAUX",
      "state": "",
      "postal_code": "33000",
      "country": "FRA",
      "normalized_address_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "building_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "phonetic_key": "15|R000|33000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-019",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Apt B",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "APT B",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|APT B|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-020",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Herengracht 182, 1016 BR Amsterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HERENGRACHT 182",
      "street2": "",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 BR",
      "country": "NLD",
      "normalized_address_key": "HERENGRACHT 182||AMSTERDAM||1016 BR|NLD",
      "building_key": "HERENGRACHT 182||AMSTERDAM||1016 BR|NLD",
      "phonetic_key": "H652|1016 BR",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-021",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Prinsengracht 263",
      "street2": "Suite 2",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 GV",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "PRINSENGRACHT 263",
      "street2": "STE 2",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 GV",
      "country": "NLD",
      "normalized_address_key": "PRINSENGRACHT 263|STE 2|AMSTERDAM||1016 GV|NLD",
      "building_key": "PRINSENGRACHT 263||AMSTERDAM||1016 GV|NLD",
      "phonetic_key": "P652|1016 GV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-022",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Coolsingel 65, 3012 AC Rotterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COOLSINGEL 65",
      "street2": "",
      "city": "ROTTERDAM",
      "state": "",
      "postal_code": "3012 AC",
      "country": "NLD",
      "normalized_address_key": "COOLSINGEL 65||ROTTERDAM||3012 AC|NLD",
      "building_key": "COOLSINGEL 65||ROTTERDAM||3012 AC|NLD",
      "phonetic_key": "C425|3012 AC",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-023",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Spui 70",
      "street2": None,
      "city": "Den Haag",
      "state": None,
      "postal_code": "2513 AA",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "SPUI 70",
      "street2": "",
      "city": "DEN HAAG",
      "state": "",
      "postal_code": "2513 AA",
      "country": "NLD",
      "normalized_address_key": "SPUI 70||DEN HAAG||2513 AA|NLD",
      "building_key": "SPUI 70||DEN HAAG||2513 AA|NLD",
      "phonetic_key": "S100|2513 AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-024",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Oudegracht 158, 3511 EV Utrecht, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "OUDEGRACHT 158",
      "street2": "",
      "city": "UTRECHT",
      "state": "",
      "postal_code": "3511 EV",
      "country": "NLD",
      "normalized_address_key": "OUDEGRACHT 158||UTRECHT||3511 EV|NLD",
      "building_key": "OUDEGRACHT 158||UTRECHT||3511 EV|NLD",
      "phonetic_key": "O326|3511 EV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-025",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Mayor 45",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE MAYOR 45",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "CALLE MAYOR 45|2 B|MADRID||28013|ESP",
      "building_key": "CALLE MAYOR 45||MADRID||28013|ESP",
      "phonetic_key": "C400|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-026",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Paseo de la Castellana 89, 4ª A, 28046 Madrid, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA CASTELLANA 89, 4A A",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28046",
      "country": "ESP",
      "normalized_address_key": "PASEO DE LA CASTELLANA 89, 4A A||MADRID||28046|ESP",
      "building_key": "PASEO DE LA CASTELLANA 89, 4A A||MADRID||28046|ESP",
      "phonetic_key": "P200|28046",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-027",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Gran Vía 32",
      "street2": None,
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "GRAN VÍA 32",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "GRAN VIA 32||MADRID||28013|ESP",
      "building_key": "GRAN VIA 32||MADRID||28013|ESP",
      "phonetic_key": "G650|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-028",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Passeig de Gràcia 43, Piso 3, 08007 Barcelona, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASSEIG DE GRÀCIA 43",
      "street2": "PISO 3",
      "city": "BARCELONA",
      "state": "",
      "postal_code": "08007",
      "country": "ESP",
      "normalized_address_key": "PASSEIG DE GRACIA 43|PISO 3|BARCELONA||08007|ESP",
      "building_key": "PASSEIG DE GRACIA 43||BARCELONA||08007|ESP",
      "phonetic_key": "P220|08007",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-029",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Colón 15",
      "street2": None,
      "city": "Valencia",
      "state": None,
      "postal_code": "46002",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE COLÓN 15",
      "street2": "",
      "city": "VALENCIA",
      "state": "",
      "postal_code": "46002",
      "country": "ESP",
      "normalized_address_key": "CALLE COLON 15||VALENCIA||46002|ESP",
      "building_key": "CALLE COLON 15||VALENCIA||46002|ESP",
      "phonetic_key": "C400|46002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-030",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Roma 10, 00184 Roma, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA ROMA 10",
      "street2": "",
      "city": "ROMA",
      "state": "",
      "postal_code": "00184",
      "country": "ITA",
      "normalized_address_key": "VIA ROMA 10||ROMA||00184|ITA",
      "building_key": "VIA ROMA 10||ROMA||00184|ITA",
      "phonetic_key": "V000|00184",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-031",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via del Corso 150",
      "street2": "Piano 2",
      "city": "Roma",
      "state": None,
      "postal_code": "00186",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "VIA DEL CORSO 150",
      "street2": "PIANO 2",
      "city": "ROMA",
      "state": "",
      "postal_code": "00186",
      "country": "ITA",
      "normalized_address_key": "VIA DEL CORSO 150|PIANO 2|ROMA||00186|ITA",
      "building_key": "VIA DEL CORSO 150||ROMA||00186|ITA",
      "phonetic_key": "V000|00186",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-032",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Montenapoleone 8, 20121 Milano, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA MONTENAPOLEONE 8",
      "street2": "",
      "city": "MILANO",
      "state": "",
      "postal_code": "20121",
      "country": "ITA",
      "normalized_address_key": "VIA MONTENAPOLEONE 8||MILANO||20121|ITA",
      "building_key": "VIA MONTENAPOLEONE 8||MILANO||20121|ITA",
      "phonetic_key": "V000|20121",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-033",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Corso Buenos Aires 33",
      "street2": "Int 5",
      "city": "Milano",
      "state": None,
      "postal_code": "20124",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "CORSO BUENOS AIRES 33",
      "street2": "INT 5",
      "city": "MILANO",
      "state": "",
      "postal_code": "20124",
      "country": "ITA",
      "normalized_address_key": "CORSO BUENOS AIRES 33|INT 5|MILANO||20124|ITA",
      "building_key": "CORSO BUENOS AIRES 33||MILANO||20124|ITA",
      "phonetic_key": "C620|20124",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-034",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Piazza del Duomo 1, 50122 Firenze, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PZ DEL DUOMO 1",
      "street2": "",
      "city": "FIRENZE",
      "state": "",
      "postal_code": "50122",
      "country": "ITA",
      "normalized_address_key": "PZ DEL DUOMO 1||FIRENZE||50122|ITA",
      "building_key": "PZ DEL DUOMO 1||FIRENZE||50122|ITA",
      "phonetic_key": "P200|50122",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-035",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Marszałkowska 100",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-026",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL MARSZAŁKOWSKA 100",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-026",
      "country": "POL",
      "normalized_address_key": "UL MARSZALKOWSKA 100||WARSZAWA||00-026|POL",
      "building_key": "UL MARSZALKOWSKA 100||WARSZAWA||00-026|POL",
      "phonetic_key": "U400|00-02",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-036",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Floriańska 15, 31-019 Kraków, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. FLORIAŃSKA 15",
      "street2": "",
      "city": "31-019 KRAKÓW",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. FLORIANSKA 15||31-019 KRAKOW|||POL",
      "building_key": "UL. FLORIANSKA 15||31-019 KRAKOW|||POL",
      "phonetic_key": "U400|31-019 KRAKOW",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-037",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Kungsgatan 14",
      "street2": None,
      "city": "Stockholm",
      "state": None,
      "postal_code": "111 35",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "KUNGSGATAN 14",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 35",
      "country": "SWE",
      "normalized_address_key": "KUNGSGATAN 14||STOCKHOLM||111 35|SWE",
      "building_key": "KUNGSGATAN 14||STOCKHOLM||111 35|SWE",
      "phonetic_key": "K523|111 3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-038",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Drottninggatan 50, 111 21 Stockholm, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "DROTTNINGGATAN 50",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 21",
      "country": "SWE",
      "normalized_address_key": "DROTTNINGGATAN 50||STOCKHOLM||111 21|SWE",
      "building_key": "DROTTNINGGATAN 50||STOCKHOLM||111 21|SWE",
      "phonetic_key": "D635|111 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-039",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Østergade 24",
      "street2": None,
      "city": "København",
      "state": None,
      "postal_code": "1100",
      "country": "Denmark"
    },
    "expected_output": {
      "street1": "ØSTERGADE 24",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1100",
      "country": "DNK",
      "normalized_address_key": "OSTERGADE 24||KOBENHAVN||1100|DNK",
      "building_key": "OSTERGADE 24||KOBENHAVN||1100|DNK",
      "phonetic_key": "O236|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-040",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Strøget 10, 1160 København, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "STRØGET 10",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1160",
      "country": "DNK",
      "normalized_address_key": "STROGET 10||KOBENHAVN||1160|DNK",
      "building_key": "STROGET 10||KOBENHAVN||1160|DNK",
      "phonetic_key": "S362|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-041",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Musterstraße 22",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10115",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 22",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10115",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 22||BERLIN||10115|DEU",
      "building_key": "MUSTERSTRASSE 22||BERLIN||10115|DEU",
      "phonetic_key": "M236|10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-042",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Friedrichstraße 43-45, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "FRIEDRICHSTRASSE 43",
      "street2": "APT 45",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "FRIEDRICHSTRASSE 43|APT 45|BERLIN||10117|DEU",
      "building_key": "FRIEDRICHSTRASSE 43||BERLIN||10117|DEU",
      "phonetic_key": "F636|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-043",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Kurfürstendamm 205",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10707",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KURFÜRSTENDAMM 205",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10707",
      "country": "DEU",
      "normalized_address_key": "KURFURSTENDAMM 205||BERLIN||10707|DEU",
      "building_key": "KURFURSTENDAMM 205||BERLIN||10707|DEU",
      "phonetic_key": "K616|10707",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-044",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Unter den Linden 87, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UNTER DEN LINDEN 87",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "UNTER DEN LINDEN 87||BERLIN||10117|DEU",
      "building_key": "UNTER DEN LINDEN 87||BERLIN||10117|DEU",
      "phonetic_key": "U536|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-045",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Am Hauptbahnhof 5a",
      "street2": None,
      "city": "Frankfurt am Main",
      "state": None,
      "postal_code": "60329",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "AM HAUPTBAHNHOF 5A",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60329",
      "country": "DEU",
      "normalized_address_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "building_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "phonetic_key": "A500|60329",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-046",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Zeil 116, 60311 Frankfurt am Main, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "ZEIL 116",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60311",
      "country": "DEU",
      "normalized_address_key": "ZEIL 116||FRANKFURT AM MAIN||60311|DEU",
      "building_key": "ZEIL 116||FRANKFURT AM MAIN||60311|DEU",
      "phonetic_key": "Z400|60311",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-047",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Maximilianstraße 35",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MAXIMILIANSTRASSE 35",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MAXIMILIANSTRASSE 35||MUNCHEN||80331|DEU",
      "building_key": "MAXIMILIANSTRASSE 35||MUNCHEN||80331|DEU",
      "phonetic_key": "M254|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-048",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Brienner Straße 24, 80539 München, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BRIENNER STRASSE 24",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80539",
      "country": "DEU",
      "normalized_address_key": "BRIENNER STRASSE 24||MUNCHEN||80539|DEU",
      "building_key": "BRIENNER STRASSE 24||MUNCHEN||80539|DEU",
      "phonetic_key": "B656|80539",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-049",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Jungfernstieg 24",
      "street2": None,
      "city": "Hamburg",
      "state": None,
      "postal_code": "20354",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "JUNGFERNSTIEG 24",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20354",
      "country": "DEU",
      "normalized_address_key": "JUNGFERNSTIEG 24||HAMBURG||20354|DEU",
      "building_key": "JUNGFERNSTIEG 24||HAMBURG||20354|DEU",
      "phonetic_key": "J521|20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-050",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 31, 20457 Hamburg, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 31",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20457",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 31||HAMBURG||20457|DEU",
      "building_key": "GROSSE BLEICHEN 31||HAMBURG||20457|DEU",
      "phonetic_key": "G620|20457",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-051",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 70",
      "street2": None,
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 70",
      "street2": "",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 70||DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 70||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-052",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Hohe Straße 78, 50667 Köln, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HOHE STRASSE 78",
      "street2": "",
      "city": "KÖLN",
      "state": "",
      "postal_code": "50667",
      "country": "DEU",
      "normalized_address_key": "HOHE STRASSE 78||KOLN||50667|DEU",
      "building_key": "HOHE STRASSE 78||KOLN||50667|DEU",
      "phonetic_key": "H000|50667",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-053",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "142 Boulevard Saint-Germain",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75006",
      "country": "France"
    },
    "expected_output": {
      "street1": "142 BD SAINT-GERMAIN",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75006",
      "country": "FRA",
      "normalized_address_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "building_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "phonetic_key": "142|B300|75006",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-054",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "25 Rue de Rivoli, 75004 Paris, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "25 RUE DE RIVOLI",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75004",
      "country": "FRA",
      "normalized_address_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "building_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "phonetic_key": "25|R000|75004",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-055",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75008",
      "country": "France"
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75008",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "phonetic_key": "80|R000|75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-056",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "10 Place Bellecour, 69002 Lyon, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "10 PL BELLECOUR",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "building_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "phonetic_key": "10|P400|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-057",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "50 La Canebière",
      "street2": None,
      "city": "Marseille",
      "state": None,
      "postal_code": "13001",
      "country": "France"
    },
    "expected_output": {
      "street1": "50 LA CANEBIÈRE",
      "street2": "",
      "city": "MARSEILLE",
      "state": "",
      "postal_code": "13001",
      "country": "FRA",
      "normalized_address_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "building_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "phonetic_key": "50|L000|13001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-058",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "15 Rue Sainte-Catherine, 33000 Bordeaux, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 RUE SAINTE-CATHERINE",
      "street2": "",
      "city": "BORDEAUX",
      "state": "",
      "postal_code": "33000",
      "country": "FRA",
      "normalized_address_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "building_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "phonetic_key": "15|R000|33000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-059",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 431",
      "street2": "Apt B",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 431",
      "street2": "APT B",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 431|APT B|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 431||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-060",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Herengracht 192, 1016 BR Amsterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HERENGRACHT 192",
      "street2": "",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 BR",
      "country": "NLD",
      "normalized_address_key": "HERENGRACHT 192||AMSTERDAM||1016 BR|NLD",
      "building_key": "HERENGRACHT 192||AMSTERDAM||1016 BR|NLD",
      "phonetic_key": "H652|1016 BR",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-061",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Prinsengracht 273",
      "street2": "Suite 2",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 GV",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "PRINSENGRACHT 273",
      "street2": "STE 2",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 GV",
      "country": "NLD",
      "normalized_address_key": "PRINSENGRACHT 273|STE 2|AMSTERDAM||1016 GV|NLD",
      "building_key": "PRINSENGRACHT 273||AMSTERDAM||1016 GV|NLD",
      "phonetic_key": "P652|1016 GV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-062",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Coolsingel 75, 3012 AC Rotterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COOLSINGEL 75",
      "street2": "",
      "city": "ROTTERDAM",
      "state": "",
      "postal_code": "3012 AC",
      "country": "NLD",
      "normalized_address_key": "COOLSINGEL 75||ROTTERDAM||3012 AC|NLD",
      "building_key": "COOLSINGEL 75||ROTTERDAM||3012 AC|NLD",
      "phonetic_key": "C425|3012 AC",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-063",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Spui 80",
      "street2": None,
      "city": "Den Haag",
      "state": None,
      "postal_code": "2513 AA",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "SPUI 80",
      "street2": "",
      "city": "DEN HAAG",
      "state": "",
      "postal_code": "2513 AA",
      "country": "NLD",
      "normalized_address_key": "SPUI 80||DEN HAAG||2513 AA|NLD",
      "building_key": "SPUI 80||DEN HAAG||2513 AA|NLD",
      "phonetic_key": "S100|2513 AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-064",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Oudegracht 168, 3511 EV Utrecht, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "OUDEGRACHT 168",
      "street2": "",
      "city": "UTRECHT",
      "state": "",
      "postal_code": "3511 EV",
      "country": "NLD",
      "normalized_address_key": "OUDEGRACHT 168||UTRECHT||3511 EV|NLD",
      "building_key": "OUDEGRACHT 168||UTRECHT||3511 EV|NLD",
      "phonetic_key": "O326|3511 EV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-065",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Mayor 55",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE MAYOR 55",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "CALLE MAYOR 55|2 B|MADRID||28013|ESP",
      "building_key": "CALLE MAYOR 55||MADRID||28013|ESP",
      "phonetic_key": "C400|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-066",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Paseo de la Castellana 99, 4ª A, 28046 Madrid, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA CASTELLANA 99, 4A A",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28046",
      "country": "ESP",
      "normalized_address_key": "PASEO DE LA CASTELLANA 99, 4A A||MADRID||28046|ESP",
      "building_key": "PASEO DE LA CASTELLANA 99, 4A A||MADRID||28046|ESP",
      "phonetic_key": "P200|28046",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-067",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Gran Vía 42",
      "street2": None,
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "GRAN VÍA 42",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "GRAN VIA 42||MADRID||28013|ESP",
      "building_key": "GRAN VIA 42||MADRID||28013|ESP",
      "phonetic_key": "G650|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-068",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Passeig de Gràcia 53, Piso 3, 08007 Barcelona, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASSEIG DE GRÀCIA 53",
      "street2": "PISO 3",
      "city": "BARCELONA",
      "state": "",
      "postal_code": "08007",
      "country": "ESP",
      "normalized_address_key": "PASSEIG DE GRACIA 53|PISO 3|BARCELONA||08007|ESP",
      "building_key": "PASSEIG DE GRACIA 53||BARCELONA||08007|ESP",
      "phonetic_key": "P220|08007",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-069",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Colón 25",
      "street2": None,
      "city": "Valencia",
      "state": None,
      "postal_code": "46002",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE COLÓN 25",
      "street2": "",
      "city": "VALENCIA",
      "state": "",
      "postal_code": "46002",
      "country": "ESP",
      "normalized_address_key": "CALLE COLON 25||VALENCIA||46002|ESP",
      "building_key": "CALLE COLON 25||VALENCIA||46002|ESP",
      "phonetic_key": "C400|46002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-070",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Roma 20, 00184 Roma, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA ROMA 20",
      "street2": "",
      "city": "ROMA",
      "state": "",
      "postal_code": "00184",
      "country": "ITA",
      "normalized_address_key": "VIA ROMA 20||ROMA||00184|ITA",
      "building_key": "VIA ROMA 20||ROMA||00184|ITA",
      "phonetic_key": "V000|00184",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-071",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via del Corso 160",
      "street2": "Piano 2",
      "city": "Roma",
      "state": None,
      "postal_code": "00186",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "VIA DEL CORSO 160",
      "street2": "PIANO 2",
      "city": "ROMA",
      "state": "",
      "postal_code": "00186",
      "country": "ITA",
      "normalized_address_key": "VIA DEL CORSO 160|PIANO 2|ROMA||00186|ITA",
      "building_key": "VIA DEL CORSO 160||ROMA||00186|ITA",
      "phonetic_key": "V000|00186",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-072",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Montenapoleone 18, 20121 Milano, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA MONTENAPOLEONE 18",
      "street2": "",
      "city": "MILANO",
      "state": "",
      "postal_code": "20121",
      "country": "ITA",
      "normalized_address_key": "VIA MONTENAPOLEONE 18||MILANO||20121|ITA",
      "building_key": "VIA MONTENAPOLEONE 18||MILANO||20121|ITA",
      "phonetic_key": "V000|20121",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-073",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Corso Buenos Aires 43",
      "street2": "Int 5",
      "city": "Milano",
      "state": None,
      "postal_code": "20124",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "CORSO BUENOS AIRES 43",
      "street2": "INT 5",
      "city": "MILANO",
      "state": "",
      "postal_code": "20124",
      "country": "ITA",
      "normalized_address_key": "CORSO BUENOS AIRES 43|INT 5|MILANO||20124|ITA",
      "building_key": "CORSO BUENOS AIRES 43||MILANO||20124|ITA",
      "phonetic_key": "C620|20124",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-074",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Piazza del Duomo 11, 50122 Firenze, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PZ DEL DUOMO 11",
      "street2": "",
      "city": "FIRENZE",
      "state": "",
      "postal_code": "50122",
      "country": "ITA",
      "normalized_address_key": "PZ DEL DUOMO 11||FIRENZE||50122|ITA",
      "building_key": "PZ DEL DUOMO 11||FIRENZE||50122|ITA",
      "phonetic_key": "P200|50122",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-075",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Marszałkowska 110",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-026",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL MARSZAŁKOWSKA 110",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-026",
      "country": "POL",
      "normalized_address_key": "UL MARSZALKOWSKA 110||WARSZAWA||00-026|POL",
      "building_key": "UL MARSZALKOWSKA 110||WARSZAWA||00-026|POL",
      "phonetic_key": "U400|00-02",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-076",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Floriańska 25, 31-019 Kraków, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. FLORIAŃSKA 25",
      "street2": "",
      "city": "31-019 KRAKÓW",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. FLORIANSKA 25||31-019 KRAKOW|||POL",
      "building_key": "UL. FLORIANSKA 25||31-019 KRAKOW|||POL",
      "phonetic_key": "U400|31-019 KRAKOW",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-077",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Kungsgatan 24",
      "street2": None,
      "city": "Stockholm",
      "state": None,
      "postal_code": "111 35",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "KUNGSGATAN 24",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 35",
      "country": "SWE",
      "normalized_address_key": "KUNGSGATAN 24||STOCKHOLM||111 35|SWE",
      "building_key": "KUNGSGATAN 24||STOCKHOLM||111 35|SWE",
      "phonetic_key": "K523|111 3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-078",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Drottninggatan 60, 111 21 Stockholm, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "DROTTNINGGATAN 60",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 21",
      "country": "SWE",
      "normalized_address_key": "DROTTNINGGATAN 60||STOCKHOLM||111 21|SWE",
      "building_key": "DROTTNINGGATAN 60||STOCKHOLM||111 21|SWE",
      "phonetic_key": "D635|111 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-079",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Østergade 34",
      "street2": None,
      "city": "København",
      "state": None,
      "postal_code": "1100",
      "country": "Denmark"
    },
    "expected_output": {
      "street1": "ØSTERGADE 34",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1100",
      "country": "DNK",
      "normalized_address_key": "OSTERGADE 34||KOBENHAVN||1100|DNK",
      "building_key": "OSTERGADE 34||KOBENHAVN||1100|DNK",
      "phonetic_key": "O236|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-080",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Strøget 20, 1160 København, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "STRØGET 20",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1160",
      "country": "DNK",
      "normalized_address_key": "STROGET 20||KOBENHAVN||1160|DNK",
      "building_key": "STROGET 20||KOBENHAVN||1160|DNK",
      "phonetic_key": "S362|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-081",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Musterstraße 32",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10115",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 32",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10115",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 32||BERLIN||10115|DEU",
      "building_key": "MUSTERSTRASSE 32||BERLIN||10115|DEU",
      "phonetic_key": "M236|10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-082",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Friedrichstraße 43-45, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "FRIEDRICHSTRASSE 43",
      "street2": "APT 45",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "FRIEDRICHSTRASSE 43|APT 45|BERLIN||10117|DEU",
      "building_key": "FRIEDRICHSTRASSE 43||BERLIN||10117|DEU",
      "phonetic_key": "F636|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-083",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Kurfürstendamm 215",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10707",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KURFÜRSTENDAMM 215",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10707",
      "country": "DEU",
      "normalized_address_key": "KURFURSTENDAMM 215||BERLIN||10707|DEU",
      "building_key": "KURFURSTENDAMM 215||BERLIN||10707|DEU",
      "phonetic_key": "K616|10707",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-084",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Unter den Linden 97, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UNTER DEN LINDEN 97",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "UNTER DEN LINDEN 97||BERLIN||10117|DEU",
      "building_key": "UNTER DEN LINDEN 97||BERLIN||10117|DEU",
      "phonetic_key": "U536|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-085",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Am Hauptbahnhof 5a",
      "street2": None,
      "city": "Frankfurt am Main",
      "state": None,
      "postal_code": "60329",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "AM HAUPTBAHNHOF 5A",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60329",
      "country": "DEU",
      "normalized_address_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "building_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "phonetic_key": "A500|60329",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-086",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Zeil 126, 60311 Frankfurt am Main, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "ZEIL 126",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60311",
      "country": "DEU",
      "normalized_address_key": "ZEIL 126||FRANKFURT AM MAIN||60311|DEU",
      "building_key": "ZEIL 126||FRANKFURT AM MAIN||60311|DEU",
      "phonetic_key": "Z400|60311",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-087",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Maximilianstraße 45",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MAXIMILIANSTRASSE 45",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MAXIMILIANSTRASSE 45||MUNCHEN||80331|DEU",
      "building_key": "MAXIMILIANSTRASSE 45||MUNCHEN||80331|DEU",
      "phonetic_key": "M254|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-088",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Brienner Straße 34, 80539 München, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BRIENNER STRASSE 34",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80539",
      "country": "DEU",
      "normalized_address_key": "BRIENNER STRASSE 34||MUNCHEN||80539|DEU",
      "building_key": "BRIENNER STRASSE 34||MUNCHEN||80539|DEU",
      "phonetic_key": "B656|80539",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-089",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Jungfernstieg 34",
      "street2": None,
      "city": "Hamburg",
      "state": None,
      "postal_code": "20354",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "JUNGFERNSTIEG 34",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20354",
      "country": "DEU",
      "normalized_address_key": "JUNGFERNSTIEG 34||HAMBURG||20354|DEU",
      "building_key": "JUNGFERNSTIEG 34||HAMBURG||20354|DEU",
      "phonetic_key": "J521|20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-090",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 41, 20457 Hamburg, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 41",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20457",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 41||HAMBURG||20457|DEU",
      "building_key": "GROSSE BLEICHEN 41||HAMBURG||20457|DEU",
      "phonetic_key": "G620|20457",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-091",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 80",
      "street2": None,
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 80",
      "street2": "",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 80||DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 80||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-092",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Hohe Straße 88, 50667 Köln, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HOHE STRASSE 88",
      "street2": "",
      "city": "KÖLN",
      "state": "",
      "postal_code": "50667",
      "country": "DEU",
      "normalized_address_key": "HOHE STRASSE 88||KOLN||50667|DEU",
      "building_key": "HOHE STRASSE 88||KOLN||50667|DEU",
      "phonetic_key": "H000|50667",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-093",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "142 Boulevard Saint-Germain",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75006",
      "country": "France"
    },
    "expected_output": {
      "street1": "142 BD SAINT-GERMAIN",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75006",
      "country": "FRA",
      "normalized_address_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "building_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "phonetic_key": "142|B300|75006",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-094",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "25 Rue de Rivoli, 75004 Paris, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "25 RUE DE RIVOLI",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75004",
      "country": "FRA",
      "normalized_address_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "building_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "phonetic_key": "25|R000|75004",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-095",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75008",
      "country": "France"
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75008",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "phonetic_key": "80|R000|75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-096",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "10 Place Bellecour, 69002 Lyon, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "10 PL BELLECOUR",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "building_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "phonetic_key": "10|P400|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-097",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "50 La Canebière",
      "street2": None,
      "city": "Marseille",
      "state": None,
      "postal_code": "13001",
      "country": "France"
    },
    "expected_output": {
      "street1": "50 LA CANEBIÈRE",
      "street2": "",
      "city": "MARSEILLE",
      "state": "",
      "postal_code": "13001",
      "country": "FRA",
      "normalized_address_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "building_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "phonetic_key": "50|L000|13001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-098",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "15 Rue Sainte-Catherine, 33000 Bordeaux, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 RUE SAINTE-CATHERINE",
      "street2": "",
      "city": "BORDEAUX",
      "state": "",
      "postal_code": "33000",
      "country": "FRA",
      "normalized_address_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "building_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "phonetic_key": "15|R000|33000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-099",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 441",
      "street2": "Apt B",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 441",
      "street2": "APT B",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 441|APT B|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 441||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-100",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Herengracht 202, 1016 BR Amsterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HERENGRACHT 202",
      "street2": "",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 BR",
      "country": "NLD",
      "normalized_address_key": "HERENGRACHT 202||AMSTERDAM||1016 BR|NLD",
      "building_key": "HERENGRACHT 202||AMSTERDAM||1016 BR|NLD",
      "phonetic_key": "H652|1016 BR",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-101",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Prinsengracht 283",
      "street2": "Suite 2",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 GV",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "PRINSENGRACHT 283",
      "street2": "STE 2",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 GV",
      "country": "NLD",
      "normalized_address_key": "PRINSENGRACHT 283|STE 2|AMSTERDAM||1016 GV|NLD",
      "building_key": "PRINSENGRACHT 283||AMSTERDAM||1016 GV|NLD",
      "phonetic_key": "P652|1016 GV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-102",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Coolsingel 85, 3012 AC Rotterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COOLSINGEL 85",
      "street2": "",
      "city": "ROTTERDAM",
      "state": "",
      "postal_code": "3012 AC",
      "country": "NLD",
      "normalized_address_key": "COOLSINGEL 85||ROTTERDAM||3012 AC|NLD",
      "building_key": "COOLSINGEL 85||ROTTERDAM||3012 AC|NLD",
      "phonetic_key": "C425|3012 AC",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-103",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Spui 90",
      "street2": None,
      "city": "Den Haag",
      "state": None,
      "postal_code": "2513 AA",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "SPUI 90",
      "street2": "",
      "city": "DEN HAAG",
      "state": "",
      "postal_code": "2513 AA",
      "country": "NLD",
      "normalized_address_key": "SPUI 90||DEN HAAG||2513 AA|NLD",
      "building_key": "SPUI 90||DEN HAAG||2513 AA|NLD",
      "phonetic_key": "S100|2513 AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-104",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Oudegracht 178, 3511 EV Utrecht, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "OUDEGRACHT 178",
      "street2": "",
      "city": "UTRECHT",
      "state": "",
      "postal_code": "3511 EV",
      "country": "NLD",
      "normalized_address_key": "OUDEGRACHT 178||UTRECHT||3511 EV|NLD",
      "building_key": "OUDEGRACHT 178||UTRECHT||3511 EV|NLD",
      "phonetic_key": "O326|3511 EV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-105",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Mayor 65",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE MAYOR 65",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "CALLE MAYOR 65|2 B|MADRID||28013|ESP",
      "building_key": "CALLE MAYOR 65||MADRID||28013|ESP",
      "phonetic_key": "C400|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-106",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Paseo de la Castellana 109, 4ª A, 28046 Madrid, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA CASTELLANA 109, 4A A",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28046",
      "country": "ESP",
      "normalized_address_key": "PASEO DE LA CASTELLANA 109, 4A A||MADRID||28046|ESP",
      "building_key": "PASEO DE LA CASTELLANA 109, 4A A||MADRID||28046|ESP",
      "phonetic_key": "P200|28046",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-107",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Gran Vía 52",
      "street2": None,
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "GRAN VÍA 52",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "GRAN VIA 52||MADRID||28013|ESP",
      "building_key": "GRAN VIA 52||MADRID||28013|ESP",
      "phonetic_key": "G650|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-108",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Passeig de Gràcia 63, Piso 3, 08007 Barcelona, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASSEIG DE GRÀCIA 63",
      "street2": "PISO 3",
      "city": "BARCELONA",
      "state": "",
      "postal_code": "08007",
      "country": "ESP",
      "normalized_address_key": "PASSEIG DE GRACIA 63|PISO 3|BARCELONA||08007|ESP",
      "building_key": "PASSEIG DE GRACIA 63||BARCELONA||08007|ESP",
      "phonetic_key": "P220|08007",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-109",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Colón 35",
      "street2": None,
      "city": "Valencia",
      "state": None,
      "postal_code": "46002",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE COLÓN 35",
      "street2": "",
      "city": "VALENCIA",
      "state": "",
      "postal_code": "46002",
      "country": "ESP",
      "normalized_address_key": "CALLE COLON 35||VALENCIA||46002|ESP",
      "building_key": "CALLE COLON 35||VALENCIA||46002|ESP",
      "phonetic_key": "C400|46002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-110",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Roma 30, 00184 Roma, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA ROMA 30",
      "street2": "",
      "city": "ROMA",
      "state": "",
      "postal_code": "00184",
      "country": "ITA",
      "normalized_address_key": "VIA ROMA 30||ROMA||00184|ITA",
      "building_key": "VIA ROMA 30||ROMA||00184|ITA",
      "phonetic_key": "V000|00184",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-111",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via del Corso 170",
      "street2": "Piano 2",
      "city": "Roma",
      "state": None,
      "postal_code": "00186",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "VIA DEL CORSO 170",
      "street2": "PIANO 2",
      "city": "ROMA",
      "state": "",
      "postal_code": "00186",
      "country": "ITA",
      "normalized_address_key": "VIA DEL CORSO 170|PIANO 2|ROMA||00186|ITA",
      "building_key": "VIA DEL CORSO 170||ROMA||00186|ITA",
      "phonetic_key": "V000|00186",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-112",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Montenapoleone 28, 20121 Milano, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA MONTENAPOLEONE 28",
      "street2": "",
      "city": "MILANO",
      "state": "",
      "postal_code": "20121",
      "country": "ITA",
      "normalized_address_key": "VIA MONTENAPOLEONE 28||MILANO||20121|ITA",
      "building_key": "VIA MONTENAPOLEONE 28||MILANO||20121|ITA",
      "phonetic_key": "V000|20121",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-113",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Corso Buenos Aires 53",
      "street2": "Int 5",
      "city": "Milano",
      "state": None,
      "postal_code": "20124",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "CORSO BUENOS AIRES 53",
      "street2": "INT 5",
      "city": "MILANO",
      "state": "",
      "postal_code": "20124",
      "country": "ITA",
      "normalized_address_key": "CORSO BUENOS AIRES 53|INT 5|MILANO||20124|ITA",
      "building_key": "CORSO BUENOS AIRES 53||MILANO||20124|ITA",
      "phonetic_key": "C620|20124",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-114",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Piazza del Duomo 21, 50122 Firenze, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PZ DEL DUOMO 21",
      "street2": "",
      "city": "FIRENZE",
      "state": "",
      "postal_code": "50122",
      "country": "ITA",
      "normalized_address_key": "PZ DEL DUOMO 21||FIRENZE||50122|ITA",
      "building_key": "PZ DEL DUOMO 21||FIRENZE||50122|ITA",
      "phonetic_key": "P200|50122",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-115",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Marszałkowska 120",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-026",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL MARSZAŁKOWSKA 120",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-026",
      "country": "POL",
      "normalized_address_key": "UL MARSZALKOWSKA 120||WARSZAWA||00-026|POL",
      "building_key": "UL MARSZALKOWSKA 120||WARSZAWA||00-026|POL",
      "phonetic_key": "U400|00-02",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-116",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Floriańska 35, 31-019 Kraków, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. FLORIAŃSKA 35",
      "street2": "",
      "city": "31-019 KRAKÓW",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. FLORIANSKA 35||31-019 KRAKOW|||POL",
      "building_key": "UL. FLORIANSKA 35||31-019 KRAKOW|||POL",
      "phonetic_key": "U400|31-019 KRAKOW",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-117",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Kungsgatan 34",
      "street2": None,
      "city": "Stockholm",
      "state": None,
      "postal_code": "111 35",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "KUNGSGATAN 34",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 35",
      "country": "SWE",
      "normalized_address_key": "KUNGSGATAN 34||STOCKHOLM||111 35|SWE",
      "building_key": "KUNGSGATAN 34||STOCKHOLM||111 35|SWE",
      "phonetic_key": "K523|111 3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-118",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Drottninggatan 70, 111 21 Stockholm, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "DROTTNINGGATAN 70",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 21",
      "country": "SWE",
      "normalized_address_key": "DROTTNINGGATAN 70||STOCKHOLM||111 21|SWE",
      "building_key": "DROTTNINGGATAN 70||STOCKHOLM||111 21|SWE",
      "phonetic_key": "D635|111 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-119",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Østergade 44",
      "street2": None,
      "city": "København",
      "state": None,
      "postal_code": "1100",
      "country": "Denmark"
    },
    "expected_output": {
      "street1": "ØSTERGADE 44",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1100",
      "country": "DNK",
      "normalized_address_key": "OSTERGADE 44||KOBENHAVN||1100|DNK",
      "building_key": "OSTERGADE 44||KOBENHAVN||1100|DNK",
      "phonetic_key": "O236|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-120",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Strøget 30, 1160 København, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "STRØGET 30",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1160",
      "country": "DNK",
      "normalized_address_key": "STROGET 30||KOBENHAVN||1160|DNK",
      "building_key": "STROGET 30||KOBENHAVN||1160|DNK",
      "phonetic_key": "S362|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-121",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Musterstraße 42",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10115",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 42",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10115",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 42||BERLIN||10115|DEU",
      "building_key": "MUSTERSTRASSE 42||BERLIN||10115|DEU",
      "phonetic_key": "M236|10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-122",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Friedrichstraße 43-45, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "FRIEDRICHSTRASSE 43",
      "street2": "APT 45",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "FRIEDRICHSTRASSE 43|APT 45|BERLIN||10117|DEU",
      "building_key": "FRIEDRICHSTRASSE 43||BERLIN||10117|DEU",
      "phonetic_key": "F636|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-123",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Kurfürstendamm 225",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10707",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KURFÜRSTENDAMM 225",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10707",
      "country": "DEU",
      "normalized_address_key": "KURFURSTENDAMM 225||BERLIN||10707|DEU",
      "building_key": "KURFURSTENDAMM 225||BERLIN||10707|DEU",
      "phonetic_key": "K616|10707",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-124",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Unter den Linden 107, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UNTER DEN LINDEN 107",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "UNTER DEN LINDEN 107||BERLIN||10117|DEU",
      "building_key": "UNTER DEN LINDEN 107||BERLIN||10117|DEU",
      "phonetic_key": "U536|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-125",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Am Hauptbahnhof 5a",
      "street2": None,
      "city": "Frankfurt am Main",
      "state": None,
      "postal_code": "60329",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "AM HAUPTBAHNHOF 5A",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60329",
      "country": "DEU",
      "normalized_address_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "building_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "phonetic_key": "A500|60329",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-126",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Zeil 136, 60311 Frankfurt am Main, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "ZEIL 136",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60311",
      "country": "DEU",
      "normalized_address_key": "ZEIL 136||FRANKFURT AM MAIN||60311|DEU",
      "building_key": "ZEIL 136||FRANKFURT AM MAIN||60311|DEU",
      "phonetic_key": "Z400|60311",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-127",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Maximilianstraße 55",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MAXIMILIANSTRASSE 55",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MAXIMILIANSTRASSE 55||MUNCHEN||80331|DEU",
      "building_key": "MAXIMILIANSTRASSE 55||MUNCHEN||80331|DEU",
      "phonetic_key": "M254|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-128",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Brienner Straße 44, 80539 München, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BRIENNER STRASSE 44",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80539",
      "country": "DEU",
      "normalized_address_key": "BRIENNER STRASSE 44||MUNCHEN||80539|DEU",
      "building_key": "BRIENNER STRASSE 44||MUNCHEN||80539|DEU",
      "phonetic_key": "B656|80539",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-129",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Jungfernstieg 44",
      "street2": None,
      "city": "Hamburg",
      "state": None,
      "postal_code": "20354",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "JUNGFERNSTIEG 44",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20354",
      "country": "DEU",
      "normalized_address_key": "JUNGFERNSTIEG 44||HAMBURG||20354|DEU",
      "building_key": "JUNGFERNSTIEG 44||HAMBURG||20354|DEU",
      "phonetic_key": "J521|20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-130",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 51, 20457 Hamburg, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 51",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20457",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 51||HAMBURG||20457|DEU",
      "building_key": "GROSSE BLEICHEN 51||HAMBURG||20457|DEU",
      "phonetic_key": "G620|20457",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-131",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 90",
      "street2": None,
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 90",
      "street2": "",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 90||DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 90||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-132",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Hohe Straße 98, 50667 Köln, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HOHE STRASSE 98",
      "street2": "",
      "city": "KÖLN",
      "state": "",
      "postal_code": "50667",
      "country": "DEU",
      "normalized_address_key": "HOHE STRASSE 98||KOLN||50667|DEU",
      "building_key": "HOHE STRASSE 98||KOLN||50667|DEU",
      "phonetic_key": "H000|50667",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-133",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "142 Boulevard Saint-Germain",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75006",
      "country": "France"
    },
    "expected_output": {
      "street1": "142 BD SAINT-GERMAIN",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75006",
      "country": "FRA",
      "normalized_address_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "building_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "phonetic_key": "142|B300|75006",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-134",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "25 Rue de Rivoli, 75004 Paris, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "25 RUE DE RIVOLI",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75004",
      "country": "FRA",
      "normalized_address_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "building_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "phonetic_key": "25|R000|75004",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-135",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75008",
      "country": "France"
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75008",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "phonetic_key": "80|R000|75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-136",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "10 Place Bellecour, 69002 Lyon, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "10 PL BELLECOUR",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "building_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "phonetic_key": "10|P400|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-137",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "50 La Canebière",
      "street2": None,
      "city": "Marseille",
      "state": None,
      "postal_code": "13001",
      "country": "France"
    },
    "expected_output": {
      "street1": "50 LA CANEBIÈRE",
      "street2": "",
      "city": "MARSEILLE",
      "state": "",
      "postal_code": "13001",
      "country": "FRA",
      "normalized_address_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "building_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "phonetic_key": "50|L000|13001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-138",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "15 Rue Sainte-Catherine, 33000 Bordeaux, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 RUE SAINTE-CATHERINE",
      "street2": "",
      "city": "BORDEAUX",
      "state": "",
      "postal_code": "33000",
      "country": "FRA",
      "normalized_address_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "building_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "phonetic_key": "15|R000|33000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-139",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 451",
      "street2": "Apt B",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 451",
      "street2": "APT B",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 451|APT B|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 451||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-140",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Herengracht 212, 1016 BR Amsterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HERENGRACHT 212",
      "street2": "",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 BR",
      "country": "NLD",
      "normalized_address_key": "HERENGRACHT 212||AMSTERDAM||1016 BR|NLD",
      "building_key": "HERENGRACHT 212||AMSTERDAM||1016 BR|NLD",
      "phonetic_key": "H652|1016 BR",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-141",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Prinsengracht 293",
      "street2": "Suite 2",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 GV",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "PRINSENGRACHT 293",
      "street2": "STE 2",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 GV",
      "country": "NLD",
      "normalized_address_key": "PRINSENGRACHT 293|STE 2|AMSTERDAM||1016 GV|NLD",
      "building_key": "PRINSENGRACHT 293||AMSTERDAM||1016 GV|NLD",
      "phonetic_key": "P652|1016 GV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-142",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Coolsingel 95, 3012 AC Rotterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COOLSINGEL 95",
      "street2": "",
      "city": "ROTTERDAM",
      "state": "",
      "postal_code": "3012 AC",
      "country": "NLD",
      "normalized_address_key": "COOLSINGEL 95||ROTTERDAM||3012 AC|NLD",
      "building_key": "COOLSINGEL 95||ROTTERDAM||3012 AC|NLD",
      "phonetic_key": "C425|3012 AC",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-143",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Spui 100",
      "street2": None,
      "city": "Den Haag",
      "state": None,
      "postal_code": "2513 AA",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "SPUI 100",
      "street2": "",
      "city": "DEN HAAG",
      "state": "",
      "postal_code": "2513 AA",
      "country": "NLD",
      "normalized_address_key": "SPUI 100||DEN HAAG||2513 AA|NLD",
      "building_key": "SPUI 100||DEN HAAG||2513 AA|NLD",
      "phonetic_key": "S100|2513 AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-144",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Oudegracht 188, 3511 EV Utrecht, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "OUDEGRACHT 188",
      "street2": "",
      "city": "UTRECHT",
      "state": "",
      "postal_code": "3511 EV",
      "country": "NLD",
      "normalized_address_key": "OUDEGRACHT 188||UTRECHT||3511 EV|NLD",
      "building_key": "OUDEGRACHT 188||UTRECHT||3511 EV|NLD",
      "phonetic_key": "O326|3511 EV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-145",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Mayor 75",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE MAYOR 75",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "CALLE MAYOR 75|2 B|MADRID||28013|ESP",
      "building_key": "CALLE MAYOR 75||MADRID||28013|ESP",
      "phonetic_key": "C400|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-146",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Paseo de la Castellana 119, 4ª A, 28046 Madrid, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA CASTELLANA 119, 4A A",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28046",
      "country": "ESP",
      "normalized_address_key": "PASEO DE LA CASTELLANA 119, 4A A||MADRID||28046|ESP",
      "building_key": "PASEO DE LA CASTELLANA 119, 4A A||MADRID||28046|ESP",
      "phonetic_key": "P200|28046",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-147",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Gran Vía 62",
      "street2": None,
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "GRAN VÍA 62",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "GRAN VIA 62||MADRID||28013|ESP",
      "building_key": "GRAN VIA 62||MADRID||28013|ESP",
      "phonetic_key": "G650|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-148",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Passeig de Gràcia 73, Piso 3, 08007 Barcelona, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASSEIG DE GRÀCIA 73",
      "street2": "PISO 3",
      "city": "BARCELONA",
      "state": "",
      "postal_code": "08007",
      "country": "ESP",
      "normalized_address_key": "PASSEIG DE GRACIA 73|PISO 3|BARCELONA||08007|ESP",
      "building_key": "PASSEIG DE GRACIA 73||BARCELONA||08007|ESP",
      "phonetic_key": "P220|08007",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-149",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Colón 45",
      "street2": None,
      "city": "Valencia",
      "state": None,
      "postal_code": "46002",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE COLÓN 45",
      "street2": "",
      "city": "VALENCIA",
      "state": "",
      "postal_code": "46002",
      "country": "ESP",
      "normalized_address_key": "CALLE COLON 45||VALENCIA||46002|ESP",
      "building_key": "CALLE COLON 45||VALENCIA||46002|ESP",
      "phonetic_key": "C400|46002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-150",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Roma 40, 00184 Roma, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA ROMA 40",
      "street2": "",
      "city": "ROMA",
      "state": "",
      "postal_code": "00184",
      "country": "ITA",
      "normalized_address_key": "VIA ROMA 40||ROMA||00184|ITA",
      "building_key": "VIA ROMA 40||ROMA||00184|ITA",
      "phonetic_key": "V000|00184",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-151",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via del Corso 180",
      "street2": "Piano 2",
      "city": "Roma",
      "state": None,
      "postal_code": "00186",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "VIA DEL CORSO 180",
      "street2": "PIANO 2",
      "city": "ROMA",
      "state": "",
      "postal_code": "00186",
      "country": "ITA",
      "normalized_address_key": "VIA DEL CORSO 180|PIANO 2|ROMA||00186|ITA",
      "building_key": "VIA DEL CORSO 180||ROMA||00186|ITA",
      "phonetic_key": "V000|00186",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-152",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Montenapoleone 38, 20121 Milano, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA MONTENAPOLEONE 38",
      "street2": "",
      "city": "MILANO",
      "state": "",
      "postal_code": "20121",
      "country": "ITA",
      "normalized_address_key": "VIA MONTENAPOLEONE 38||MILANO||20121|ITA",
      "building_key": "VIA MONTENAPOLEONE 38||MILANO||20121|ITA",
      "phonetic_key": "V000|20121",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-153",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Corso Buenos Aires 63",
      "street2": "Int 5",
      "city": "Milano",
      "state": None,
      "postal_code": "20124",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "CORSO BUENOS AIRES 63",
      "street2": "INT 5",
      "city": "MILANO",
      "state": "",
      "postal_code": "20124",
      "country": "ITA",
      "normalized_address_key": "CORSO BUENOS AIRES 63|INT 5|MILANO||20124|ITA",
      "building_key": "CORSO BUENOS AIRES 63||MILANO||20124|ITA",
      "phonetic_key": "C620|20124",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-154",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Piazza del Duomo 31, 50122 Firenze, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PZ DEL DUOMO 31",
      "street2": "",
      "city": "FIRENZE",
      "state": "",
      "postal_code": "50122",
      "country": "ITA",
      "normalized_address_key": "PZ DEL DUOMO 31||FIRENZE||50122|ITA",
      "building_key": "PZ DEL DUOMO 31||FIRENZE||50122|ITA",
      "phonetic_key": "P200|50122",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-155",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Marszałkowska 130",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-026",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL MARSZAŁKOWSKA 130",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-026",
      "country": "POL",
      "normalized_address_key": "UL MARSZALKOWSKA 130||WARSZAWA||00-026|POL",
      "building_key": "UL MARSZALKOWSKA 130||WARSZAWA||00-026|POL",
      "phonetic_key": "U400|00-02",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-156",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Floriańska 45, 31-019 Kraków, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. FLORIAŃSKA 45",
      "street2": "",
      "city": "31-019 KRAKÓW",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. FLORIANSKA 45||31-019 KRAKOW|||POL",
      "building_key": "UL. FLORIANSKA 45||31-019 KRAKOW|||POL",
      "phonetic_key": "U400|31-019 KRAKOW",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-157",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Kungsgatan 44",
      "street2": None,
      "city": "Stockholm",
      "state": None,
      "postal_code": "111 35",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "KUNGSGATAN 44",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 35",
      "country": "SWE",
      "normalized_address_key": "KUNGSGATAN 44||STOCKHOLM||111 35|SWE",
      "building_key": "KUNGSGATAN 44||STOCKHOLM||111 35|SWE",
      "phonetic_key": "K523|111 3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-158",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Drottninggatan 80, 111 21 Stockholm, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "DROTTNINGGATAN 80",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 21",
      "country": "SWE",
      "normalized_address_key": "DROTTNINGGATAN 80||STOCKHOLM||111 21|SWE",
      "building_key": "DROTTNINGGATAN 80||STOCKHOLM||111 21|SWE",
      "phonetic_key": "D635|111 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-159",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Østergade 54",
      "street2": None,
      "city": "København",
      "state": None,
      "postal_code": "1100",
      "country": "Denmark"
    },
    "expected_output": {
      "street1": "ØSTERGADE 54",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1100",
      "country": "DNK",
      "normalized_address_key": "OSTERGADE 54||KOBENHAVN||1100|DNK",
      "building_key": "OSTERGADE 54||KOBENHAVN||1100|DNK",
      "phonetic_key": "O236|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-160",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Strøget 40, 1160 København, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "STRØGET 40",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1160",
      "country": "DNK",
      "normalized_address_key": "STROGET 40||KOBENHAVN||1160|DNK",
      "building_key": "STROGET 40||KOBENHAVN||1160|DNK",
      "phonetic_key": "S362|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-161",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Musterstraße 52",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10115",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 52",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10115",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 52||BERLIN||10115|DEU",
      "building_key": "MUSTERSTRASSE 52||BERLIN||10115|DEU",
      "phonetic_key": "M236|10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-162",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Friedrichstraße 43-45, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "FRIEDRICHSTRASSE 43",
      "street2": "APT 45",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "FRIEDRICHSTRASSE 43|APT 45|BERLIN||10117|DEU",
      "building_key": "FRIEDRICHSTRASSE 43||BERLIN||10117|DEU",
      "phonetic_key": "F636|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-163",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Kurfürstendamm 235",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10707",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KURFÜRSTENDAMM 235",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10707",
      "country": "DEU",
      "normalized_address_key": "KURFURSTENDAMM 235||BERLIN||10707|DEU",
      "building_key": "KURFURSTENDAMM 235||BERLIN||10707|DEU",
      "phonetic_key": "K616|10707",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-164",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Unter den Linden 117, 10117 Berlin, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UNTER DEN LINDEN 117",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10117",
      "country": "DEU",
      "normalized_address_key": "UNTER DEN LINDEN 117||BERLIN||10117|DEU",
      "building_key": "UNTER DEN LINDEN 117||BERLIN||10117|DEU",
      "phonetic_key": "U536|10117",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-165",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Am Hauptbahnhof 5a",
      "street2": None,
      "city": "Frankfurt am Main",
      "state": None,
      "postal_code": "60329",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "AM HAUPTBAHNHOF 5A",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60329",
      "country": "DEU",
      "normalized_address_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "building_key": "AM HAUPTBAHNHOF 5A||FRANKFURT AM MAIN||60329|DEU",
      "phonetic_key": "A500|60329",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-166",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Zeil 146, 60311 Frankfurt am Main, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "ZEIL 146",
      "street2": "",
      "city": "FRANKFURT AM MAIN",
      "state": "",
      "postal_code": "60311",
      "country": "DEU",
      "normalized_address_key": "ZEIL 146||FRANKFURT AM MAIN||60311|DEU",
      "building_key": "ZEIL 146||FRANKFURT AM MAIN||60311|DEU",
      "phonetic_key": "Z400|60311",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-167",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Maximilianstraße 65",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MAXIMILIANSTRASSE 65",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MAXIMILIANSTRASSE 65||MUNCHEN||80331|DEU",
      "building_key": "MAXIMILIANSTRASSE 65||MUNCHEN||80331|DEU",
      "phonetic_key": "M254|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-168",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Brienner Straße 54, 80539 München, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BRIENNER STRASSE 54",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80539",
      "country": "DEU",
      "normalized_address_key": "BRIENNER STRASSE 54||MUNCHEN||80539|DEU",
      "building_key": "BRIENNER STRASSE 54||MUNCHEN||80539|DEU",
      "phonetic_key": "B656|80539",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-169",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Jungfernstieg 54",
      "street2": None,
      "city": "Hamburg",
      "state": None,
      "postal_code": "20354",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "JUNGFERNSTIEG 54",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20354",
      "country": "DEU",
      "normalized_address_key": "JUNGFERNSTIEG 54||HAMBURG||20354|DEU",
      "building_key": "JUNGFERNSTIEG 54||HAMBURG||20354|DEU",
      "phonetic_key": "J521|20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-170",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 61, 20457 Hamburg, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 61",
      "street2": "",
      "city": "HAMBURG",
      "state": "",
      "postal_code": "20457",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 61||HAMBURG||20457|DEU",
      "building_key": "GROSSE BLEICHEN 61||HAMBURG||20457|DEU",
      "phonetic_key": "G620|20457",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-171",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 100",
      "street2": None,
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 100",
      "street2": "",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 100||DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 100||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-172",
    "category": "eu_inverted_compound",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Hohe Straße 108, 50667 Köln, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HOHE STRASSE 108",
      "street2": "",
      "city": "KÖLN",
      "state": "",
      "postal_code": "50667",
      "country": "DEU",
      "normalized_address_key": "HOHE STRASSE 108||KOLN||50667|DEU",
      "building_key": "HOHE STRASSE 108||KOLN||50667|DEU",
      "phonetic_key": "H000|50667",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-173",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "142 Boulevard Saint-Germain",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75006",
      "country": "France"
    },
    "expected_output": {
      "street1": "142 BD SAINT-GERMAIN",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75006",
      "country": "FRA",
      "normalized_address_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "building_key": "142 BD SAINT-GERMAIN||PARIS||75006|FRA",
      "phonetic_key": "142|B300|75006",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-174",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "25 Rue de Rivoli, 75004 Paris, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "25 RUE DE RIVOLI",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75004",
      "country": "FRA",
      "normalized_address_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "building_key": "25 RUE DE RIVOLI||PARIS||75004|FRA",
      "phonetic_key": "25|R000|75004",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-175",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er",
      "street2": None,
      "city": "Paris",
      "state": None,
      "postal_code": "75008",
      "country": "France"
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS",
      "state": "",
      "postal_code": "75008",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS||75008|FRA",
      "phonetic_key": "80|R000|75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-176",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "10 Place Bellecour, 69002 Lyon, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "10 PL BELLECOUR",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "building_key": "10 PL BELLECOUR||LYON||69002|FRA",
      "phonetic_key": "10|P400|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-177",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "50 La Canebière",
      "street2": None,
      "city": "Marseille",
      "state": None,
      "postal_code": "13001",
      "country": "France"
    },
    "expected_output": {
      "street1": "50 LA CANEBIÈRE",
      "street2": "",
      "city": "MARSEILLE",
      "state": "",
      "postal_code": "13001",
      "country": "FRA",
      "normalized_address_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "building_key": "50 LA CANEBIERE||MARSEILLE||13001|FRA",
      "phonetic_key": "50|L000|13001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-178",
    "category": "eu_inverted_compound",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "15 Rue Sainte-Catherine, 33000 Bordeaux, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 RUE SAINTE-CATHERINE",
      "street2": "",
      "city": "BORDEAUX",
      "state": "",
      "postal_code": "33000",
      "country": "FRA",
      "normalized_address_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "building_key": "15 RUE SAINTE-CATHERINE||BORDEAUX||33000|FRA",
      "phonetic_key": "15|R000|33000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-179",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 461",
      "street2": "Apt B",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 461",
      "street2": "APT B",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 461|APT B|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 461||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-180",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Herengracht 222, 1016 BR Amsterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "HERENGRACHT 222",
      "street2": "",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 BR",
      "country": "NLD",
      "normalized_address_key": "HERENGRACHT 222||AMSTERDAM||1016 BR|NLD",
      "building_key": "HERENGRACHT 222||AMSTERDAM||1016 BR|NLD",
      "phonetic_key": "H652|1016 BR",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-181",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Prinsengracht 303",
      "street2": "Suite 2",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 GV",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "PRINSENGRACHT 303",
      "street2": "STE 2",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 GV",
      "country": "NLD",
      "normalized_address_key": "PRINSENGRACHT 303|STE 2|AMSTERDAM||1016 GV|NLD",
      "building_key": "PRINSENGRACHT 303||AMSTERDAM||1016 GV|NLD",
      "phonetic_key": "P652|1016 GV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-182",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Coolsingel 105, 3012 AC Rotterdam, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "COOLSINGEL 105",
      "street2": "",
      "city": "ROTTERDAM",
      "state": "",
      "postal_code": "3012 AC",
      "country": "NLD",
      "normalized_address_key": "COOLSINGEL 105||ROTTERDAM||3012 AC|NLD",
      "building_key": "COOLSINGEL 105||ROTTERDAM||3012 AC|NLD",
      "phonetic_key": "C425|3012 AC",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-183",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Spui 110",
      "street2": None,
      "city": "Den Haag",
      "state": None,
      "postal_code": "2513 AA",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "SPUI 110",
      "street2": "",
      "city": "DEN HAAG",
      "state": "",
      "postal_code": "2513 AA",
      "country": "NLD",
      "normalized_address_key": "SPUI 110||DEN HAAG||2513 AA|NLD",
      "building_key": "SPUI 110||DEN HAAG||2513 AA|NLD",
      "phonetic_key": "S100|2513 AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-184",
    "category": "eu_inverted_compound",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Oudegracht 198, 3511 EV Utrecht, Netherlands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "OUDEGRACHT 198",
      "street2": "",
      "city": "UTRECHT",
      "state": "",
      "postal_code": "3511 EV",
      "country": "NLD",
      "normalized_address_key": "OUDEGRACHT 198||UTRECHT||3511 EV|NLD",
      "building_key": "OUDEGRACHT 198||UTRECHT||3511 EV|NLD",
      "phonetic_key": "O326|3511 EV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-185",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Mayor 85",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE MAYOR 85",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "CALLE MAYOR 85|2 B|MADRID||28013|ESP",
      "building_key": "CALLE MAYOR 85||MADRID||28013|ESP",
      "phonetic_key": "C400|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-186",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Paseo de la Castellana 129, 4ª A, 28046 Madrid, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA CASTELLANA 129, 4A A",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28046",
      "country": "ESP",
      "normalized_address_key": "PASEO DE LA CASTELLANA 129, 4A A||MADRID||28046|ESP",
      "building_key": "PASEO DE LA CASTELLANA 129, 4A A||MADRID||28046|ESP",
      "phonetic_key": "P200|28046",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-187",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Gran Vía 72",
      "street2": None,
      "city": "Madrid",
      "state": None,
      "postal_code": "28013",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "GRAN VÍA 72",
      "street2": "",
      "city": "MADRID",
      "state": "",
      "postal_code": "28013",
      "country": "ESP",
      "normalized_address_key": "GRAN VIA 72||MADRID||28013|ESP",
      "building_key": "GRAN VIA 72||MADRID||28013|ESP",
      "phonetic_key": "G650|28013",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-188",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Passeig de Gràcia 83, Piso 3, 08007 Barcelona, Spain",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASSEIG DE GRÀCIA 83",
      "street2": "PISO 3",
      "city": "BARCELONA",
      "state": "",
      "postal_code": "08007",
      "country": "ESP",
      "normalized_address_key": "PASSEIG DE GRACIA 83|PISO 3|BARCELONA||08007|ESP",
      "building_key": "PASSEIG DE GRACIA 83||BARCELONA||08007|ESP",
      "phonetic_key": "P220|08007",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-189",
    "category": "eu_inverted_compound",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Colón 55",
      "street2": None,
      "city": "Valencia",
      "state": None,
      "postal_code": "46002",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE COLÓN 55",
      "street2": "",
      "city": "VALENCIA",
      "state": "",
      "postal_code": "46002",
      "country": "ESP",
      "normalized_address_key": "CALLE COLON 55||VALENCIA||46002|ESP",
      "building_key": "CALLE COLON 55||VALENCIA||46002|ESP",
      "phonetic_key": "C400|46002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-190",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Roma 50, 00184 Roma, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA ROMA 50",
      "street2": "",
      "city": "ROMA",
      "state": "",
      "postal_code": "00184",
      "country": "ITA",
      "normalized_address_key": "VIA ROMA 50||ROMA||00184|ITA",
      "building_key": "VIA ROMA 50||ROMA||00184|ITA",
      "phonetic_key": "V000|00184",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-191",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via del Corso 190",
      "street2": "Piano 2",
      "city": "Roma",
      "state": None,
      "postal_code": "00186",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "VIA DEL CORSO 190",
      "street2": "PIANO 2",
      "city": "ROMA",
      "state": "",
      "postal_code": "00186",
      "country": "ITA",
      "normalized_address_key": "VIA DEL CORSO 190|PIANO 2|ROMA||00186|ITA",
      "building_key": "VIA DEL CORSO 190||ROMA||00186|ITA",
      "phonetic_key": "V000|00186",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-192",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Via Montenapoleone 48, 20121 Milano, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "VIA MONTENAPOLEONE 48",
      "street2": "",
      "city": "MILANO",
      "state": "",
      "postal_code": "20121",
      "country": "ITA",
      "normalized_address_key": "VIA MONTENAPOLEONE 48||MILANO||20121|ITA",
      "building_key": "VIA MONTENAPOLEONE 48||MILANO||20121|ITA",
      "phonetic_key": "V000|20121",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-193",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Corso Buenos Aires 73",
      "street2": "Int 5",
      "city": "Milano",
      "state": None,
      "postal_code": "20124",
      "country": "Italy"
    },
    "expected_output": {
      "street1": "CORSO BUENOS AIRES 73",
      "street2": "INT 5",
      "city": "MILANO",
      "state": "",
      "postal_code": "20124",
      "country": "ITA",
      "normalized_address_key": "CORSO BUENOS AIRES 73|INT 5|MILANO||20124|ITA",
      "building_key": "CORSO BUENOS AIRES 73||MILANO||20124|ITA",
      "phonetic_key": "C620|20124",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-194",
    "category": "eu_inverted_compound",
    "jurisdiction": "ITA",
    "raw_input": {
      "street1": "Piazza del Duomo 41, 50122 Firenze, Italy",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PZ DEL DUOMO 41",
      "street2": "",
      "city": "FIRENZE",
      "state": "",
      "postal_code": "50122",
      "country": "ITA",
      "normalized_address_key": "PZ DEL DUOMO 41||FIRENZE||50122|ITA",
      "building_key": "PZ DEL DUOMO 41||FIRENZE||50122|ITA",
      "phonetic_key": "P200|50122",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-195",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Marszałkowska 140",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-026",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL MARSZAŁKOWSKA 140",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-026",
      "country": "POL",
      "normalized_address_key": "UL MARSZALKOWSKA 140||WARSZAWA||00-026|POL",
      "building_key": "UL MARSZALKOWSKA 140||WARSZAWA||00-026|POL",
      "phonetic_key": "U400|00-02",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-196",
    "category": "eu_inverted_compound",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Floriańska 55, 31-019 Kraków, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. FLORIAŃSKA 55",
      "street2": "",
      "city": "31-019 KRAKÓW",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. FLORIANSKA 55||31-019 KRAKOW|||POL",
      "building_key": "UL. FLORIANSKA 55||31-019 KRAKOW|||POL",
      "phonetic_key": "U400|31-019 KRAKOW",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-197",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Kungsgatan 54",
      "street2": None,
      "city": "Stockholm",
      "state": None,
      "postal_code": "111 35",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "KUNGSGATAN 54",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 35",
      "country": "SWE",
      "normalized_address_key": "KUNGSGATAN 54||STOCKHOLM||111 35|SWE",
      "building_key": "KUNGSGATAN 54||STOCKHOLM||111 35|SWE",
      "phonetic_key": "K523|111 3",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-198",
    "category": "eu_inverted_compound",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Drottninggatan 90, 111 21 Stockholm, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "DROTTNINGGATAN 90",
      "street2": "",
      "city": "STOCKHOLM",
      "state": "",
      "postal_code": "111 21",
      "country": "SWE",
      "normalized_address_key": "DROTTNINGGATAN 90||STOCKHOLM||111 21|SWE",
      "building_key": "DROTTNINGGATAN 90||STOCKHOLM||111 21|SWE",
      "phonetic_key": "D635|111 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-199",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Østergade 64",
      "street2": None,
      "city": "København",
      "state": None,
      "postal_code": "1100",
      "country": "Denmark"
    },
    "expected_output": {
      "street1": "ØSTERGADE 64",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1100",
      "country": "DNK",
      "normalized_address_key": "OSTERGADE 64||KOBENHAVN||1100|DNK",
      "building_key": "OSTERGADE 64||KOBENHAVN||1100|DNK",
      "phonetic_key": "O236|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-03-200",
    "category": "eu_inverted_compound",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Strøget 50, 1160 København, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "STRØGET 50",
      "street2": "",
      "city": "KØBENHAVN",
      "state": "",
      "postal_code": "1160",
      "country": "DNK",
      "normalized_address_key": "STROGET 50||KOBENHAVN||1160|DNK",
      "building_key": "STROGET 50||KOBENHAVN||1160|DNK",
      "phonetic_key": "S362|KOBENHAVN",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-001",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1602",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1602",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1602|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1602||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-002",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 222, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 222",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 222|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 222||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-003",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 70",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 70",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 70||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 70||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-004",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1300, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1300, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1300, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1300, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-005",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2000",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2000",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2000||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2000||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-006",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-007",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-008",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-009",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-010",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1234, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1234",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1234|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1234||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-011",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3200",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3200",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3200|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3200||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-012",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 869, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 869",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 869||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 869||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-013",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1000",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1000",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1000|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1000||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-014",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 500, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 500",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 500||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 500||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-015",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1500",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1500",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1500|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1500||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-016",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3000, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3000, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3000, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3000, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-017",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1208",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1208",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1208|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1208||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-018",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4500, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4500",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4500||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4500||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-019",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Larco 101",
      "street2": "Dpto. 402",
      "city": "Lima",
      "state": None,
      "postal_code": "15074",
      "country": "Peru"
    },
    "expected_output": {
      "street1": "AVE LARCO 101",
      "street2": "DPTO 402",
      "city": "LIMA",
      "state": "",
      "postal_code": "15074",
      "country": "PER",
      "normalized_address_key": "AVE LARCO 101|DPTO 402|LIMA||15074|PER",
      "building_key": "AVE LARCO 101||LIMA||15074|PER",
      "phonetic_key": "A100|15074",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-020",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Javier Prado Este 4200, Lima 15023, Peru",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE JAVIER PRADO ESTE 4200",
      "street2": "",
      "city": "LIMA 15023",
      "state": "",
      "postal_code": "",
      "country": "PER",
      "normalized_address_key": "AVE JAVIER PRADO ESTE 4200||LIMA 15023|||PER",
      "building_key": "AVE JAVIER PRADO ESTE 4200||LIMA 15023|||PER",
      "phonetic_key": "A100|LIMA 15023",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-021",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB LAS GLADIOLAS, 100 CALLE SOL",
      "street2": None,
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "Puerto Rico"
    },
    "expected_output": {
      "street1": "URB LAS GLADIOLAS 100 CALLE SOL",
      "street2": "",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00901",
      "country": "USA",
      "normalized_address_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "building_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "phonetic_key": "100|C400|00901",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-022",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB FAIRVIEW, 250 CALLE LUNA, Apt 2, San Juan, PR 00926, Puerto Rico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "URB FAIRVIEW 250 CALLE LUNA",
      "street2": "APT 2",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00926",
      "country": "USA",
      "normalized_address_key": "URB FAIRVIEW 250 CALLE LUNA|APT 2|SAN JUAN|PR|00926|USA",
      "building_key": "URB FAIRVIEW 250 CALLE LUNA||SAN JUAN|PR|00926|USA",
      "phonetic_key": "250|C400|00926",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-023",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1607",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1607",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1607|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1607||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-024",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 227, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 227",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 227|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 227||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-025",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 75",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 75",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 75||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 75||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-026",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1305, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1305, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1305, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1305, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-027",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2005",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2005",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2005||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2005||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-028",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-029",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-030",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-031",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-032",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1239, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1239",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1239|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1239||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-033",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3205",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3205",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3205|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3205||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-034",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 874, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 874",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 874||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 874||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-035",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1005",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1005",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1005|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1005||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-036",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 505, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 505",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 505||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 505||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-037",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1505",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1505",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1505|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1505||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-038",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3005, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3005, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3005, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3005, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-039",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1213",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1213",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1213|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1213||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-040",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4505, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4505",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4505||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4505||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-041",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Larco 106",
      "street2": "Dpto. 402",
      "city": "Lima",
      "state": None,
      "postal_code": "15074",
      "country": "Peru"
    },
    "expected_output": {
      "street1": "AVE LARCO 106",
      "street2": "DPTO 402",
      "city": "LIMA",
      "state": "",
      "postal_code": "15074",
      "country": "PER",
      "normalized_address_key": "AVE LARCO 106|DPTO 402|LIMA||15074|PER",
      "building_key": "AVE LARCO 106||LIMA||15074|PER",
      "phonetic_key": "A100|15074",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-042",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Javier Prado Este 4205, Lima 15023, Peru",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE JAVIER PRADO ESTE 4205",
      "street2": "",
      "city": "LIMA 15023",
      "state": "",
      "postal_code": "",
      "country": "PER",
      "normalized_address_key": "AVE JAVIER PRADO ESTE 4205||LIMA 15023|||PER",
      "building_key": "AVE JAVIER PRADO ESTE 4205||LIMA 15023|||PER",
      "phonetic_key": "A100|LIMA 15023",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-043",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB LAS GLADIOLAS, 100 CALLE SOL",
      "street2": None,
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "Puerto Rico"
    },
    "expected_output": {
      "street1": "URB LAS GLADIOLAS 100 CALLE SOL",
      "street2": "",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00901",
      "country": "USA",
      "normalized_address_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "building_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "phonetic_key": "100|C400|00901",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-044",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB FAIRVIEW, 250 CALLE LUNA, Apt 2, San Juan, PR 00926, Puerto Rico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "URB FAIRVIEW 250 CALLE LUNA",
      "street2": "APT 2",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00926",
      "country": "USA",
      "normalized_address_key": "URB FAIRVIEW 250 CALLE LUNA|APT 2|SAN JUAN|PR|00926|USA",
      "building_key": "URB FAIRVIEW 250 CALLE LUNA||SAN JUAN|PR|00926|USA",
      "phonetic_key": "250|C400|00926",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-045",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1612",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1612",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1612|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1612||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-046",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 232, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 232",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 232|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 232||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-047",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 80",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 80",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 80||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 80||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-048",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1310, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1310, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1310, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1310, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-049",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2010",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2010",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2010||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2010||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-050",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-051",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-052",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-053",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-054",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1244, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1244",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1244|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1244||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-055",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3210",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3210",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3210|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3210||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-056",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 879, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 879",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 879||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 879||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-057",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1010",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1010",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1010|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1010||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-058",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 510, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 510",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 510||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 510||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-059",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1510",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1510",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1510|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1510||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-060",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3010, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3010, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3010, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3010, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-061",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1218",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1218",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1218|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1218||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-062",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4510, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4510",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4510||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4510||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-063",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Larco 111",
      "street2": "Dpto. 402",
      "city": "Lima",
      "state": None,
      "postal_code": "15074",
      "country": "Peru"
    },
    "expected_output": {
      "street1": "AVE LARCO 111",
      "street2": "DPTO 402",
      "city": "LIMA",
      "state": "",
      "postal_code": "15074",
      "country": "PER",
      "normalized_address_key": "AVE LARCO 111|DPTO 402|LIMA||15074|PER",
      "building_key": "AVE LARCO 111||LIMA||15074|PER",
      "phonetic_key": "A100|15074",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-064",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Javier Prado Este 4210, Lima 15023, Peru",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE JAVIER PRADO ESTE 4210",
      "street2": "",
      "city": "LIMA 15023",
      "state": "",
      "postal_code": "",
      "country": "PER",
      "normalized_address_key": "AVE JAVIER PRADO ESTE 4210||LIMA 15023|||PER",
      "building_key": "AVE JAVIER PRADO ESTE 4210||LIMA 15023|||PER",
      "phonetic_key": "A100|LIMA 15023",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-065",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB LAS GLADIOLAS, 100 CALLE SOL",
      "street2": None,
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "Puerto Rico"
    },
    "expected_output": {
      "street1": "URB LAS GLADIOLAS 100 CALLE SOL",
      "street2": "",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00901",
      "country": "USA",
      "normalized_address_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "building_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "phonetic_key": "100|C400|00901",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-066",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB FAIRVIEW, 250 CALLE LUNA, Apt 2, San Juan, PR 00926, Puerto Rico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "URB FAIRVIEW 250 CALLE LUNA",
      "street2": "APT 2",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00926",
      "country": "USA",
      "normalized_address_key": "URB FAIRVIEW 250 CALLE LUNA|APT 2|SAN JUAN|PR|00926|USA",
      "building_key": "URB FAIRVIEW 250 CALLE LUNA||SAN JUAN|PR|00926|USA",
      "phonetic_key": "250|C400|00926",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-067",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1617",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1617",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1617|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1617||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-068",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 237, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 237",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 237|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 237||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-069",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 85",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 85",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 85||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 85||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-070",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1315, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1315, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1315, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1315, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-071",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2015",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2015",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2015||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2015||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-072",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-073",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-074",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-075",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-076",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1249, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1249",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1249|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1249||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-077",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3215",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3215",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3215|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3215||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-078",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 884, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 884",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 884||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 884||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-079",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1015",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1015",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1015|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1015||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-080",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 515, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 515",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 515||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 515||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-081",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1515",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1515",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1515|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1515||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-082",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3015, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3015, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3015, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3015, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-083",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1223",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1223",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1223|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1223||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-084",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4515, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4515",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4515||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4515||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-085",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Larco 116",
      "street2": "Dpto. 402",
      "city": "Lima",
      "state": None,
      "postal_code": "15074",
      "country": "Peru"
    },
    "expected_output": {
      "street1": "AVE LARCO 116",
      "street2": "DPTO 402",
      "city": "LIMA",
      "state": "",
      "postal_code": "15074",
      "country": "PER",
      "normalized_address_key": "AVE LARCO 116|DPTO 402|LIMA||15074|PER",
      "building_key": "AVE LARCO 116||LIMA||15074|PER",
      "phonetic_key": "A100|15074",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-086",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Javier Prado Este 4215, Lima 15023, Peru",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE JAVIER PRADO ESTE 4215",
      "street2": "",
      "city": "LIMA 15023",
      "state": "",
      "postal_code": "",
      "country": "PER",
      "normalized_address_key": "AVE JAVIER PRADO ESTE 4215||LIMA 15023|||PER",
      "building_key": "AVE JAVIER PRADO ESTE 4215||LIMA 15023|||PER",
      "phonetic_key": "A100|LIMA 15023",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-087",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB LAS GLADIOLAS, 100 CALLE SOL",
      "street2": None,
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "Puerto Rico"
    },
    "expected_output": {
      "street1": "URB LAS GLADIOLAS 100 CALLE SOL",
      "street2": "",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00901",
      "country": "USA",
      "normalized_address_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "building_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "phonetic_key": "100|C400|00901",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-088",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB FAIRVIEW, 250 CALLE LUNA, Apt 2, San Juan, PR 00926, Puerto Rico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "URB FAIRVIEW 250 CALLE LUNA",
      "street2": "APT 2",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00926",
      "country": "USA",
      "normalized_address_key": "URB FAIRVIEW 250 CALLE LUNA|APT 2|SAN JUAN|PR|00926|USA",
      "building_key": "URB FAIRVIEW 250 CALLE LUNA||SAN JUAN|PR|00926|USA",
      "phonetic_key": "250|C400|00926",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-089",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1622",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1622",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1622|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1622||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-090",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 242, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 242",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 242|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 242||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-091",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 90",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 90",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 90||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 90||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-092",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1320, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1320, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1320, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1320, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-093",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2020",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2020",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2020||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2020||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-094",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-095",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-096",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-097",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-098",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1254, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1254",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1254|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1254||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-099",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3220",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3220",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3220|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3220||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-100",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 889, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 889",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 889||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 889||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-101",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1020",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1020",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1020|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1020||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-102",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 520, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 520",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 520||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 520||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-103",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1520",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1520",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1520|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1520||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-104",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3020, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3020, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3020, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3020, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-105",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1228",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1228",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1228|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1228||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-106",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4520, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4520",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4520||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4520||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-107",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Larco 121",
      "street2": "Dpto. 402",
      "city": "Lima",
      "state": None,
      "postal_code": "15074",
      "country": "Peru"
    },
    "expected_output": {
      "street1": "AVE LARCO 121",
      "street2": "DPTO 402",
      "city": "LIMA",
      "state": "",
      "postal_code": "15074",
      "country": "PER",
      "normalized_address_key": "AVE LARCO 121|DPTO 402|LIMA||15074|PER",
      "building_key": "AVE LARCO 121||LIMA||15074|PER",
      "phonetic_key": "A100|15074",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-108",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Javier Prado Este 4220, Lima 15023, Peru",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE JAVIER PRADO ESTE 4220",
      "street2": "",
      "city": "LIMA 15023",
      "state": "",
      "postal_code": "",
      "country": "PER",
      "normalized_address_key": "AVE JAVIER PRADO ESTE 4220||LIMA 15023|||PER",
      "building_key": "AVE JAVIER PRADO ESTE 4220||LIMA 15023|||PER",
      "phonetic_key": "A100|LIMA 15023",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-109",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB LAS GLADIOLAS, 100 CALLE SOL",
      "street2": None,
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "Puerto Rico"
    },
    "expected_output": {
      "street1": "URB LAS GLADIOLAS 100 CALLE SOL",
      "street2": "",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00901",
      "country": "USA",
      "normalized_address_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "building_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "phonetic_key": "100|C400|00901",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-110",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB FAIRVIEW, 250 CALLE LUNA, Apt 2, San Juan, PR 00926, Puerto Rico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "URB FAIRVIEW 250 CALLE LUNA",
      "street2": "APT 2",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00926",
      "country": "USA",
      "normalized_address_key": "URB FAIRVIEW 250 CALLE LUNA|APT 2|SAN JUAN|PR|00926|USA",
      "building_key": "URB FAIRVIEW 250 CALLE LUNA||SAN JUAN|PR|00926|USA",
      "phonetic_key": "250|C400|00926",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-111",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1627",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1627",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1627|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1627||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-112",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 247, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 247",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 247|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 247||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-113",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 95",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 95",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 95||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 95||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-114",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1325, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1325, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1325, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1325, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-115",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2025",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2025",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2025||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2025||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-116",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-117",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-118",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-119",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-120",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1259, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1259",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1259|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1259||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-121",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3225",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3225",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3225|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3225||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-122",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 894, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 894",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 894||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 894||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-123",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1025",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1025",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1025|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1025||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-124",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 525, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 525",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 525||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 525||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-125",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1525",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1525",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1525|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1525||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-126",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3025, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3025, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3025, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3025, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-127",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1233",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1233",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1233|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1233||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-128",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4525, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4525",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4525||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4525||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-129",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Larco 126",
      "street2": "Dpto. 402",
      "city": "Lima",
      "state": None,
      "postal_code": "15074",
      "country": "Peru"
    },
    "expected_output": {
      "street1": "AVE LARCO 126",
      "street2": "DPTO 402",
      "city": "LIMA",
      "state": "",
      "postal_code": "15074",
      "country": "PER",
      "normalized_address_key": "AVE LARCO 126|DPTO 402|LIMA||15074|PER",
      "building_key": "AVE LARCO 126||LIMA||15074|PER",
      "phonetic_key": "A100|15074",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-130",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PER",
    "raw_input": {
      "street1": "Av. Javier Prado Este 4225, Lima 15023, Peru",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE JAVIER PRADO ESTE 4225",
      "street2": "",
      "city": "LIMA 15023",
      "state": "",
      "postal_code": "",
      "country": "PER",
      "normalized_address_key": "AVE JAVIER PRADO ESTE 4225||LIMA 15023|||PER",
      "building_key": "AVE JAVIER PRADO ESTE 4225||LIMA 15023|||PER",
      "phonetic_key": "A100|LIMA 15023",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-131",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB LAS GLADIOLAS, 100 CALLE SOL",
      "street2": None,
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "Puerto Rico"
    },
    "expected_output": {
      "street1": "URB LAS GLADIOLAS 100 CALLE SOL",
      "street2": "",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00901",
      "country": "USA",
      "normalized_address_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "building_key": "URB LAS GLADIOLAS 100 CALLE SOL||SAN JUAN|PR|00901|USA",
      "phonetic_key": "100|C400|00901",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-132",
    "category": "latam_compound_urbanization",
    "jurisdiction": "PRI",
    "raw_input": {
      "street1": "URB FAIRVIEW, 250 CALLE LUNA, Apt 2, San Juan, PR 00926, Puerto Rico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "URB FAIRVIEW 250 CALLE LUNA",
      "street2": "APT 2",
      "city": "SAN JUAN",
      "state": "PR",
      "postal_code": "00926",
      "country": "USA",
      "normalized_address_key": "URB FAIRVIEW 250 CALLE LUNA|APT 2|SAN JUAN|PR|00926|USA",
      "building_key": "URB FAIRVIEW 250 CALLE LUNA||SAN JUAN|PR|00926|USA",
      "phonetic_key": "250|C400|00926",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-133",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Insurgentes Sur 1632",
      "street2": "Int. 401",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV INSURGENTES SUR 1632",
      "street2": "INT 401",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "03940",
      "country": "MEX",
      "normalized_address_key": "AV INSURGENTES SUR 1632|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX",
      "building_key": "AV INSURGENTES SUR 1632||CIUDAD DE MEXICO|CDMX|03940|MEX",
      "phonetic_key": "A100|03940",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-134",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 252, Piso 12, Ciudad de México, CDMX 06600, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 252",
      "street2": "PISO 12",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX 06600",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 252|PISO 12|CIUDAD DE MEXICO|CDMX 06600||MEX",
      "building_key": "PASEO DE LA REFORMA 252||CIUDAD DE MEXICO|CDMX 06600||MEX",
      "phonetic_key": "P200|CIUDAD DE MEXICO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-135",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Juárez 100",
      "street2": None,
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV JUÁREZ 100",
      "street2": "",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06010",
      "country": "MEX",
      "normalized_address_key": "AV JUAREZ 100||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "building_key": "AV JUAREZ 100||CIUDAD DE MEXICO|CDMX|06010|MEX",
      "phonetic_key": "A100|06010",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-136",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Vallarta 1330, Of. 200, Guadalajara, JAL 44160, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV VALLARTA 1330, OF 200",
      "street2": "",
      "city": "GUADALAJARA",
      "state": "JAL 44160",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV VALLARTA 1330, OF 200||GUADALAJARA|JAL 44160||MEX",
      "building_key": "AV VALLARTA 1330, OF 200||GUADALAJARA|JAL 44160||MEX",
      "phonetic_key": "A100|GUADALAJARA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-137",
    "category": "latam_compound_urbanization",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 2030",
      "street2": None,
      "city": "Monterrey",
      "state": "NL",
      "postal_code": "64060",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 2030",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL",
      "postal_code": "64060",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 2030||MONTERREY|NL|64060|MEX",
      "building_key": "AV CONSTITUCION 2030||MONTERREY|NL|64060|MEX",
      "phonetic_key": "A100|64060",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-138",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 72 No. 10-07, Of. 401, Bogotá 110221, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CALLE 72 NO. 10-07",
      "street2": "",
      "city": "OF 401",
      "state": "BOGOTÁ 110221",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "building_key": "CALLE 72 NO. 10-07||OF 401|BOGOTA 110221||COL",
      "phonetic_key": "C400|OF 401",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-139",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 7 No. 32-16",
      "street2": None,
      "city": "Bogotá",
      "state": None,
      "postal_code": "110311",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CARRERA 7 NO. 32-16",
      "street2": "",
      "city": "BOGOTÁ",
      "state": "",
      "postal_code": "110311",
      "country": "COL",
      "normalized_address_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "building_key": "CARRERA 7 NO. 32-16||BOGOTA||110311|COL",
      "phonetic_key": "C660|11031",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-140",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Carrera 43A No. 1-50, Piso 5, Medellín 050021, Colombia",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CARRERA 43A NO. 1-50",
      "street2": "PISO 5",
      "city": "MEDELLÍN 050021",
      "state": "",
      "postal_code": "",
      "country": "COL",
      "normalized_address_key": "CARRERA 43A NO. 1-50|PISO 5|MEDELLIN 050021|||COL",
      "building_key": "CARRERA 43A NO. 1-50||MEDELLIN 050021|||COL",
      "phonetic_key": "C660|MEDELLIN 050021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-141",
    "category": "latam_compound_urbanization",
    "jurisdiction": "COL",
    "raw_input": {
      "street1": "Calle 5 No. 6-05",
      "street2": None,
      "city": "Cali",
      "state": None,
      "postal_code": "760001",
      "country": "Colombia"
    },
    "expected_output": {
      "street1": "CALLE 5 NO. 6-05",
      "street2": "",
      "city": "CALI",
      "state": "",
      "postal_code": "760001",
      "country": "COL",
      "normalized_address_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "building_key": "CALLE 5 NO. 6-05||CALI||760001|COL",
      "phonetic_key": "C400|76000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-142",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Corrientes 1264, Piso 4, Buenos Aires C1043AAZ, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CORRIENTES 1264",
      "street2": "PISO 4",
      "city": "BUENOS AIRES C1043AAZ",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV CORRIENTES 1264|PISO 4|BUENOS AIRES C1043AAZ|||ARG",
      "building_key": "AV CORRIENTES 1264||BUENOS AIRES C1043AAZ|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1043AAZ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-143",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. Santa Fe 3230",
      "street2": "Depto 2B",
      "city": "Buenos Aires",
      "state": None,
      "postal_code": "C1425BGV",
      "country": "Argentina"
    },
    "expected_output": {
      "street1": "AV SANTA FE 3230",
      "street2": "DEPTO 2B",
      "city": "BUENOS AIRES",
      "state": "",
      "postal_code": "C1425BGV",
      "country": "ARG",
      "normalized_address_key": "AV SANTA FE 3230|DEPTO 2B|BUENOS AIRES||C1425BGV|ARG",
      "building_key": "AV SANTA FE 3230||BUENOS AIRES||C1425BGV|ARG",
      "phonetic_key": "A100|C1425BGV",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-144",
    "category": "latam_compound_urbanization",
    "jurisdiction": "ARG",
    "raw_input": {
      "street1": "Av. de Mayo 899, Buenos Aires C1084AAD, Argentina",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV DE MAYO 899",
      "street2": "",
      "city": "BUENOS AIRES C1084AAD",
      "state": "",
      "postal_code": "",
      "country": "ARG",
      "normalized_address_key": "AV DE MAYO 899||BUENOS AIRES C1084AAD|||ARG",
      "building_key": "AV DE MAYO 899||BUENOS AIRES C1084AAD|||ARG",
      "phonetic_key": "A100|BUENOS AIRES C1084AAD",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-145",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Paulista 1030",
      "street2": "Conjunto 14",
      "city": "São Paulo",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV PAULISTA 1030",
      "street2": "CONJUNTO 14",
      "city": "SÃO PAULO",
      "state": "SP",
      "postal_code": "01310-100",
      "country": "BRA",
      "normalized_address_key": "AV PAULISTA 1030|CONJUNTO 14|SAO PAULO|SP|01310-100|BRA",
      "building_key": "AV PAULISTA 1030||SAO PAULO|SP|01310-100|BRA",
      "phonetic_key": "A100|01310",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-146",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Rua Oscar Freire 530, São Paulo, SP 01426-001, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "RUA OSCAR FREIRE 530",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01426-001",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "RUA OSCAR FREIRE 530||SAO PAULO|SP 01426-001||BRA",
      "building_key": "RUA OSCAR FREIRE 530||SAO PAULO|SP 01426-001||BRA",
      "phonetic_key": "R000|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-147",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Atlântica 1530",
      "street2": "Apto 302",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "Brazil"
    },
    "expected_output": {
      "street1": "AV ATLÂNTICA 1530",
      "street2": "APT O",
      "city": "RIO DE JANEIRO",
      "state": "RJ",
      "postal_code": "22021-001",
      "country": "BRA",
      "normalized_address_key": "AV ATLANTICA 1530|APT O|RIO DE JANEIRO|RJ|22021-001|BRA",
      "building_key": "AV ATLANTICA 1530||RIO DE JANEIRO|RJ|22021-001|BRA",
      "phonetic_key": "A100|22021",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-148",
    "category": "latam_compound_urbanization",
    "jurisdiction": "BRA",
    "raw_input": {
      "street1": "Av. Brigadeiro Faria Lima 3030, Andar 8, São Paulo, SP 01451-000, Brazil",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV BRIGADEIRO FARIA LIMA 3030, ANDAR 8",
      "street2": "",
      "city": "SÃO PAULO",
      "state": "SP 01451-000",
      "postal_code": "",
      "country": "BRA",
      "normalized_address_key": "AV BRIGADEIRO FARIA LIMA 3030, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "building_key": "AV BRIGADEIRO FARIA LIMA 3030, ANDAR 8||SAO PAULO|SP 01451-000||BRA",
      "phonetic_key": "A100|SAO PAULO",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-149",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Providencia 1238",
      "street2": "Of. 501",
      "city": "Santiago",
      "state": None,
      "postal_code": "7500000",
      "country": "Chile"
    },
    "expected_output": {
      "street1": "AVE PROVIDENCIA 1238",
      "street2": "OF 501",
      "city": "SANTIAGO",
      "state": "",
      "postal_code": "7500000",
      "country": "CHL",
      "normalized_address_key": "AVE PROVIDENCIA 1238|OF 501|SANTIAGO||7500000|CHL",
      "building_key": "AVE PROVIDENCIA 1238||SANTIAGO||7500000|CHL",
      "phonetic_key": "A100|75000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-04-150",
    "category": "latam_compound_urbanization",
    "jurisdiction": "CHL",
    "raw_input": {
      "street1": "Av. Apoquindo 4530, Of. 1202, Santiago 7550000, Chile",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AVE APOQUINDO 4530",
      "street2": "",
      "city": "OF 1202",
      "state": "",
      "postal_code": "SANTIAGO 7550000",
      "country": "CHL",
      "normalized_address_key": "AVE APOQUINDO 4530||OF 1202||SANTIAGO 7550000|CHL",
      "building_key": "AVE APOQUINDO 4530||OF 1202||SANTIAGO 7550000|CHL",
      "phonetic_key": "A100|SANTIAGO 7550000",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-001",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 100",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 100",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 100|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-002",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Suite 200, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 SUITE 200",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 SUITE 200|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-003",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Suite 300",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 SUITE 300",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 SUITE 300|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-004",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71 Suite 400, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71 SUITE 400",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71 SUITE 400|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-005",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 500",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 500",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 500|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-006",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Fl 2, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "FL 2",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|FL 2|||BMU",
      "building_key": "2 CHURCH ST||FL 2|||BMU",
      "phonetic_key": "2|C620|FL 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-007",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Fl 3",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "FL 3",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|FL 3|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-008",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-009",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 100",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 100",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 100|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-010",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Suite 200, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "STE 200",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST|STE 200|LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-011",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Suite 300",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "STE 300",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|STE 300|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-012",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Suite 400, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "SUITE 400",
      "state": "",
      "postal_code": "LUXEMBOURG 2449",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "building_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-013",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 500",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 500",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 500|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-014",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Fl 2, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "FL 2",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|FL 2|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-015",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Fl 3",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "FL 3",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|FL 3|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-016",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-017",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 100",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 100",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 100|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-018",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Suite 200, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 STE 200",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 STE 200|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-019",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Suite 300",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-020",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Suite 400, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "STE 400",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST|STE 400|SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-021",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 500",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 500",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 500|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-022",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Fl 2, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 FL 2",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 FL 2|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-023",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Fl 3",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 FL 3",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 FL 3|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-024",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-025",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 100",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 100",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 100|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-026",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Suite 200, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "SUITE 200",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|SUITE 200|||BMU",
      "building_key": "2 CHURCH ST||SUITE 200|||BMU",
      "phonetic_key": "2|C620|SUITE 200",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-027",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Suite 300",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "SUITE 300",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|SUITE 300|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-028",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden Suite 400, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN SUITE 400",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-029",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 500",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 500",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 500|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-030",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Fl 2, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": "FL 2",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-031",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Fl 3",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "FL 3",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|FL 3|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-032",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "LUXEMBOURG 2449",
      "state": "",
      "postal_code": "",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||LUXEMBOURG 2449|||LUX",
      "building_key": "40 BLVD ROYAL||LUXEMBOURG 2449|||LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-033",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 100",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 100",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 100|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-034",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Suite 200, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "STE 200",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|STE 200|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-035",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Suite 300",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "STE 300",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|STE 300|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-036",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Suite 400, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "STE 400",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-037",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 500",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 500",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 500|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-038",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Fl 2, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 FL 2",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 FL 2|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-039",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Fl 3",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-040",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-041",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 100",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 100",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 100|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-042",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Suite 200, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 SUITE 200",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 SUITE 200|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-043",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Suite 300",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 SUITE 300",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 SUITE 300|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-044",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71 Suite 400, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71 SUITE 400",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71 SUITE 400|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-045",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 500",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 500",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 500|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-046",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Fl 2, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "FL 2",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|FL 2|||BMU",
      "building_key": "2 CHURCH ST||FL 2|||BMU",
      "phonetic_key": "2|C620|FL 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-047",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Fl 3",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "FL 3",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|FL 3|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-048",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-049",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 100",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 100",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 100|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-050",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Suite 200, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "STE 200",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST|STE 200|LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-051",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Suite 300",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "STE 300",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|STE 300|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-052",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Suite 400, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "SUITE 400",
      "state": "",
      "postal_code": "LUXEMBOURG 2449",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "building_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-053",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 500",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 500",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 500|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-054",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Fl 2, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "FL 2",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|FL 2|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-055",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Fl 3",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "FL 3",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|FL 3|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-056",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-057",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 100",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 100",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 100|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-058",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Suite 200, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 STE 200",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 STE 200|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-059",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Suite 300",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-060",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Suite 400, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "STE 400",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST|STE 400|SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-061",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 500",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 500",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 500|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-062",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Fl 2, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 FL 2",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 FL 2|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-063",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Fl 3",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 FL 3",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 FL 3|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-064",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-065",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 100",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 100",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 100|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-066",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Suite 200, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "SUITE 200",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|SUITE 200|||BMU",
      "building_key": "2 CHURCH ST||SUITE 200|||BMU",
      "phonetic_key": "2|C620|SUITE 200",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-067",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Suite 300",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "SUITE 300",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|SUITE 300|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-068",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden Suite 400, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN SUITE 400",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-069",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 500",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 500",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 500|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-070",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Fl 2, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": "FL 2",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-071",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Fl 3",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "FL 3",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|FL 3|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-072",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "LUXEMBOURG 2449",
      "state": "",
      "postal_code": "",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||LUXEMBOURG 2449|||LUX",
      "building_key": "40 BLVD ROYAL||LUXEMBOURG 2449|||LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-073",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 100",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 100",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 100|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-074",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Suite 200, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "STE 200",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|STE 200|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-075",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Suite 300",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "STE 300",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|STE 300|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-076",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Suite 400, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "STE 400",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-077",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 500",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 500",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 500|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-078",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Fl 2, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 FL 2",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 FL 2|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-079",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Fl 3",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-080",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-081",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 100",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 100",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 100|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-082",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Suite 200, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 SUITE 200",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 SUITE 200|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-083",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Suite 300",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 SUITE 300",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 SUITE 300|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-084",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71 Suite 400, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71 SUITE 400",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71 SUITE 400|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-085",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 500",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 500",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 500|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-086",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Fl 2, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "FL 2",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|FL 2|||BMU",
      "building_key": "2 CHURCH ST||FL 2|||BMU",
      "phonetic_key": "2|C620|FL 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-087",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Fl 3",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "FL 3",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|FL 3|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-088",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-089",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 100",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 100",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 100|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-090",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Suite 200, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "STE 200",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST|STE 200|LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-091",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Suite 300",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "STE 300",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|STE 300|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-092",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Suite 400, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "SUITE 400",
      "state": "",
      "postal_code": "LUXEMBOURG 2449",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "building_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-093",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 500",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 500",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 500|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-094",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Fl 2, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "FL 2",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|FL 2|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-095",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Fl 3",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "FL 3",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|FL 3|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-096",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-097",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 100",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 100",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 100|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-098",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Suite 200, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 STE 200",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 STE 200|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-099",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Suite 300",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-100",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Suite 400, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "STE 400",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST|STE 400|SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-101",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 500",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 500",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 500|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-102",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Fl 2, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 FL 2",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 FL 2|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-103",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Fl 3",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 FL 3",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 FL 3|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-104",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-105",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 100",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 100",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 100|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-106",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Suite 200, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "SUITE 200",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|SUITE 200|||BMU",
      "building_key": "2 CHURCH ST||SUITE 200|||BMU",
      "phonetic_key": "2|C620|SUITE 200",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-107",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Suite 300",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "SUITE 300",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|SUITE 300|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-108",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden Suite 400, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN SUITE 400",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-109",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 500",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 500",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 500|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-110",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Fl 2, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": "FL 2",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-111",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Fl 3",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "FL 3",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|FL 3|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-112",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "LUXEMBOURG 2449",
      "state": "",
      "postal_code": "",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||LUXEMBOURG 2449|||LUX",
      "building_key": "40 BLVD ROYAL||LUXEMBOURG 2449|||LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-113",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 100",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 100",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 100|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-114",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Suite 200, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "STE 200",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|STE 200|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-115",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Suite 300",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "STE 300",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|STE 300|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-116",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Suite 400, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "STE 400",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-117",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 500",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 500",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 500|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-118",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Fl 2, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 FL 2",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 FL 2|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-119",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Fl 3",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-120",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-121",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 100",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 100",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 100|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-122",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Suite 200, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 SUITE 200",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 SUITE 200|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-123",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Suite 300",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 SUITE 300",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 SUITE 300|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-124",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71 Suite 400, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71 SUITE 400",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71 SUITE 400|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-125",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 500",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 500",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 500|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-126",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Fl 2, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "FL 2",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|FL 2|||BMU",
      "building_key": "2 CHURCH ST||FL 2|||BMU",
      "phonetic_key": "2|C620|FL 2",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-127",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Fl 3",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "FL 3",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|FL 3|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-128",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-129",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 100",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 100",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 100|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-130",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Suite 200, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "STE 200",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST|STE 200|LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-131",
    "category": "global_formation_hubs",
    "jurisdiction": "NLD",
    "raw_input": {
      "street1": "Keizersgracht 421",
      "street2": "Suite 300",
      "city": "Amsterdam",
      "state": None,
      "postal_code": "1016 EK",
      "country": "Netherlands"
    },
    "expected_output": {
      "street1": "KEIZERSGRACHT 421",
      "street2": "STE 300",
      "city": "AMSTERDAM",
      "state": "",
      "postal_code": "1016 EK",
      "country": "NLD",
      "normalized_address_key": "KEIZERSGRACHT 421|STE 300|AMSTERDAM||1016 EK|NLD",
      "building_key": "KEIZERSGRACHT 421||AMSTERDAM||1016 EK|NLD",
      "phonetic_key": "K262|1016 EK",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-132",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "40 Boulevard Royal, Suite 400, Luxembourg 2449, Luxembourg",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "40 BLVD ROYAL",
      "street2": "",
      "city": "SUITE 400",
      "state": "",
      "postal_code": "LUXEMBOURG 2449",
      "country": "LUX",
      "normalized_address_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "building_key": "40 BLVD ROYAL||SUITE 400||LUXEMBOURG 2449|LUX",
      "phonetic_key": "40|B413|LUXEMBOURG 2449",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-133",
    "category": "global_formation_hubs",
    "jurisdiction": "LUX",
    "raw_input": {
      "street1": "Avenue Monterey 40",
      "street2": "Suite 500",
      "city": "Luxembourg",
      "state": None,
      "postal_code": "2163",
      "country": "Luxembourg"
    },
    "expected_output": {
      "street1": "AVE MONTEREY 40",
      "street2": "STE 500",
      "city": "LUXEMBOURG",
      "state": "",
      "postal_code": "2163",
      "country": "LUX",
      "normalized_address_key": "AVE MONTEREY 40|STE 500|LUXEMBOURG||2163|LUX",
      "building_key": "AVE MONTEREY 40||LUXEMBOURG||2163|LUX",
      "phonetic_key": "A100|LUXEMBOURG",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-134",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Bahnhofstrasse 45, Fl 2, Zurich 8001, Switzerland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "BAHNHOFSTRASSE 45",
      "street2": "FL 2",
      "city": "ZURICH 8001",
      "state": "",
      "postal_code": "",
      "country": "CHE",
      "normalized_address_key": "BAHNHOFSTRASSE 45|FL 2|ZURICH 8001|||CHE",
      "building_key": "BAHNHOFSTRASSE 45||ZURICH 8001|||CHE",
      "phonetic_key": "B512|ZURICH 8001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-135",
    "category": "global_formation_hubs",
    "jurisdiction": "CHE",
    "raw_input": {
      "street1": "Rue du Rhone 42",
      "street2": "Fl 3",
      "city": "Geneva",
      "state": None,
      "postal_code": "1204",
      "country": "Switzerland"
    },
    "expected_output": {
      "street1": "RUE DU RHONE 42",
      "street2": "FL 3",
      "city": "GENEVA",
      "state": "",
      "postal_code": "1204",
      "country": "CHE",
      "normalized_address_key": "RUE DU RHONE 42|FL 3|GENEVA||1204|CHE",
      "building_key": "RUE DU RHONE 42||GENEVA||1204|CHE",
      "phonetic_key": "R000|GENEVA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-136",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "1209 North Orange Street, Wilmington, DE 19801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "1209 N ORANGE ST",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19801",
      "country": "USA",
      "normalized_address_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "building_key": "1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
      "phonetic_key": "1209|O652|19801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-137",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 Little Falls Drive",
      "street2": "Suite 100",
      "city": "Wilmington",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "STE 100",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR|STE 100|WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-138",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "850 New Burton Road, Suite 201 Suite 200, Dover, DE 19904, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "850 NEW BURTON RD",
      "street2": "STE 201 STE 200",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "850 NEW BURTON RD|STE 201 STE 200|DOVER|DE|19904|USA",
      "building_key": "850 NEW BURTON RD||DOVER|DE|19904|USA",
      "phonetic_key": "850|N000|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-139",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "160 Greentree Drive",
      "street2": "Suite 101 Suite 300",
      "city": "Dover",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA"
    },
    "expected_output": {
      "street1": "160 GREENTREE DR",
      "street2": "STE 101 STE 300",
      "city": "DOVER",
      "state": "DE",
      "postal_code": "19904",
      "country": "USA",
      "normalized_address_key": "160 GREENTREE DR|STE 101 STE 300|DOVER|DE|19904|USA",
      "building_key": "160 GREENTREE DR||DOVER|DE|19904|USA",
      "phonetic_key": "160|G653|19904",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-140",
    "category": "global_formation_hubs",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "30 N Gould St, Suite 400, Sheridan, WY 82801, USA",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "30 N GOULD ST",
      "street2": "STE 400",
      "city": "SHERIDAN",
      "state": "WY",
      "postal_code": "82801",
      "country": "USA",
      "normalized_address_key": "30 N GOULD ST|STE 400|SHERIDAN|WY|82801|USA",
      "building_key": "30 N GOULD ST||SHERIDAN|WY|82801|USA",
      "phonetic_key": "30|G430|82801",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-141",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Ugland House, South Church Street",
      "street2": "PO Box 309 Suite 500",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-1104",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "UGLAND HOUSE SOUTH CHURCH ST",
      "street2": "PO BOX 309 SUITE 500",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-1104",
      "country": "CYM",
      "normalized_address_key": "UGLAND HOUSE SOUTH CHURCH ST|PO BOX 309 SUITE 500|GEORGE TOWN||KY1-1104|CYM",
      "building_key": "UGLAND HOUSE SOUTH CHURCH ST||GEORGE TOWN||KY1-1104|CYM",
      "phonetic_key": "U245|KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "UGLAND HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-142",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "Clifton House, 75 Fort Street, PO Box 190 Fl 2, George Town KY1-1104, Cayman Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CLIFTON HOUSE 75 FORT ST",
      "street2": "PO BOX 190 FL 2",
      "city": "GEORGE TOWN KY1-1104",
      "state": "",
      "postal_code": "",
      "country": "CYM",
      "normalized_address_key": "CLIFTON HOUSE 75 FORT ST|PO BOX 190 FL 2|GEORGE TOWN KY1-1104|||CYM",
      "building_key": "CLIFTON HOUSE 75 FORT ST||GEORGE TOWN KY1-1104|||CYM",
      "phonetic_key": "C413|GEORGE TOWN KY1-1104",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CLIFTON HOUSE",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-143",
    "category": "global_formation_hubs",
    "jurisdiction": "CYM",
    "raw_input": {
      "street1": "190 Elgin Avenue",
      "street2": "PO Box 9001 Fl 3",
      "city": "George Town",
      "state": None,
      "postal_code": "KY1-9001",
      "country": "Cayman Islands"
    },
    "expected_output": {
      "street1": "190 ELGIN AVE",
      "street2": "PO BOX 9001 FL 3",
      "city": "GEORGE TOWN",
      "state": "",
      "postal_code": "KY1-9001",
      "country": "CYM",
      "normalized_address_key": "190 ELGIN AVE|PO BOX 9001 FL 3|GEORGE TOWN||KY1-9001|CYM",
      "building_key": "190 ELGIN AVE||GEORGE TOWN||KY1-9001|CYM",
      "phonetic_key": "190|E425|KY1-9001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-144",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Craigmuir Chambers, PO Box 71, Road Town, TORTOLA VG1110, British Virgin Islands",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "CRAIGMUIR CHAMBERS RD TOWN",
      "street2": "PO BOX 71",
      "city": "TORTOLA VG1110",
      "state": "",
      "postal_code": "",
      "country": "VGB",
      "normalized_address_key": "CRAIGMUIR CHAMBERS RD TOWN|PO BOX 71|TORTOLA VG1110|||VGB",
      "building_key": "CRAIGMUIR CHAMBERS RD TOWN||TORTOLA VG1110|||VGB",
      "phonetic_key": "C625|TORTOLA VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CRAIGMUIR CHAMBERS",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-145",
    "category": "global_formation_hubs",
    "jurisdiction": "VGB",
    "raw_input": {
      "street1": "Wickhams Cay 1",
      "street2": "Trident Chambers Suite 100",
      "city": "Road Town",
      "state": None,
      "postal_code": "VG1110",
      "country": "British Virgin Islands"
    },
    "expected_output": {
      "street1": "WICKHAMS CAY 1",
      "street2": "TRIDENT CHAMBERS SUITE 100",
      "city": "ROAD TOWN",
      "state": "",
      "postal_code": "VG1110",
      "country": "VGB",
      "normalized_address_key": "WICKHAMS CAY 1|TRIDENT CHAMBERS SUITE 100|ROAD TOWN||VG1110|VGB",
      "building_key": "WICKHAMS CAY 1||ROAD TOWN||VG1110|VGB",
      "phonetic_key": "W252|VG1110",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-146",
    "category": "global_formation_hubs",
    "jurisdiction": "BMU",
    "raw_input": {
      "street1": "Clarendon House, 2 Church Street, Suite 200, Hamilton HM 11, Bermuda",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "2 CHURCH ST",
      "street2": "CLARENDON HOUSE",
      "city": "SUITE 200",
      "state": "",
      "postal_code": "",
      "country": "BMU",
      "normalized_address_key": "2 CHURCH ST|CLARENDON HOUSE|SUITE 200|||BMU",
      "building_key": "2 CHURCH ST||SUITE 200|||BMU",
      "phonetic_key": "2|C620|SUITE 200",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-147",
    "category": "global_formation_hubs",
    "jurisdiction": "PAN",
    "raw_input": {
      "street1": "Calle 50, Edificio Arango Orillac",
      "street2": "Suite 300",
      "city": "Panama City",
      "state": None,
      "postal_code": None,
      "country": "Panama"
    },
    "expected_output": {
      "street1": "CALLE 50 EDIFICIO ARANGO ORILLAC",
      "street2": "SUITE 300",
      "city": "PANAMA CITY",
      "state": "",
      "postal_code": "",
      "country": "PAN",
      "normalized_address_key": "CALLE 50 EDIFICIO ARANGO ORILLAC|SUITE 300|PANAMA CITY|||PAN",
      "building_key": "CALLE 50 EDIFICIO ARANGO ORILLAC||PANAMA CITY|||PAN",
      "phonetic_key": "C400|PANAMA CITY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": "CALLE 50",
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-148",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 Shelton Street, Covent Garden Suite 400, London WC2H 9JQ, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": "COVENT GARDEN SUITE 400",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-149",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "20-22 Wenlock Road",
      "street2": "Suite 500",
      "city": "London",
      "state": None,
      "postal_code": "N1 7GU",
      "country": "United Kingdom"
    },
    "expected_output": {
      "street1": "20-22 WENLOCK RD",
      "street2": "STE 500",
      "city": "LONDON",
      "state": "",
      "postal_code": "N1 7GU",
      "country": "GBR",
      "normalized_address_key": "20-22 WENLOCK RD|STE 500|LONDON||N1 7GU|GBR",
      "building_key": "20-22 WENLOCK RD||LONDON||N1 7GU|GBR",
      "phonetic_key": "20-22|W542|N1 7GU",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-05-150",
    "category": "global_formation_hubs",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "27 Old Gloucester Street, Fl 2, London WC1N 3AX, United Kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "27 OLD GLOUCESTER ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC1N 3AX",
      "country": "GBR",
      "normalized_address_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "building_key": "27 OLD GLOUCESTER ST||LONDON||WC1N 3AX|GBR",
      "phonetic_key": "27|O430|WC1N 3AX",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": "FL 2",
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-001",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 45",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 45",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 45||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 45||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-002",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 21, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 21",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 21||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 21||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-003",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 60",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 60",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 60|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 60||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-004",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 18, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 18",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 18||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 18||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-005",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 17",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 17",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 17||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 17||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-006",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-007",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "30 Rue de la République",
      "street2": None,
      "city": "Lyon",
      "state": None,
      "postal_code": "69002",
      "country": "France"
    },
    "expected_output": {
      "street1": "30 RUE DE LA RÉPUBLIQUE",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "building_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "phonetic_key": "30|R000|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-008",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "12 Avenue Foch, Paris 75116, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "12 AV FOCH",
      "street2": "",
      "city": "PARIS 75116",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "12 AV FOCH||PARIS 75116|||FRA",
      "building_key": "12 AV FOCH||PARIS 75116|||FRA",
      "phonetic_key": "12|A100|PARIS 75116",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-009",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "450 Boulevard René-Lévesque Ouest",
      "street2": "Suite 400",
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "450 BD RENÉ-LÉVESQUE O",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "450 BD RENE-LEVESQUE O|STE 400|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "450 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "450|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-010",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "123 Rue Saint-Denis, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "123 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "123|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-011",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Núñez de Balboa 12",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28001",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE NÚÑEZ DE BALBOA 12",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28001",
      "country": "ESP",
      "normalized_address_key": "CALLE NUNEZ DE BALBOA 12|2 B|MADRID||28001|ESP",
      "building_key": "CALLE NUNEZ DE BALBOA 12||MADRID||28001|ESP",
      "phonetic_key": "C400|28001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-012",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 400, Monterrey, NL 64060, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 400",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL 64060",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 400||MONTERREY|NL 64060||MEX",
      "building_key": "AV CONSTITUCION 400||MONTERREY|NL 64060||MEX",
      "phonetic_key": "A100|MONTERREY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-013",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 222",
      "street2": "Piso 5",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 222",
      "street2": "PISO 5",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 222|PISO 5|CIUDAD DE MEXICO|CDMX|06600|MEX",
      "building_key": "PASEO DE LA REFORMA 222||CIUDAD DE MEXICO|CDMX|06600|MEX",
      "phonetic_key": "P200|06600",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-014",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Købmagergade 52, København 1150, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "KØBMAGERGADE 52",
      "street2": "",
      "city": "KØBENHAVN 1150",
      "state": "",
      "postal_code": "",
      "country": "DNK",
      "normalized_address_key": "KOBMAGERGADE 52||KOBENHAVN 1150|||DNK",
      "building_key": "KOBMAGERGADE 52||KOBENHAVN 1150|||DNK",
      "phonetic_key": "K152|KOBENHAVN 1150",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-015",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Västra Hamngatan 7",
      "street2": None,
      "city": "Göteborg",
      "state": None,
      "postal_code": "411 17",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "VÄSTRA HAMNGATAN 7",
      "street2": "",
      "city": "GÖTEBORG",
      "state": "",
      "postal_code": "411 17",
      "country": "SWE",
      "normalized_address_key": "VASTRA HAMNGATAN 7||GOTEBORG||411 17|SWE",
      "building_key": "VASTRA HAMNGATAN 7||GOTEBORG||411 17|SWE",
      "phonetic_key": "V236|411 1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-016",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Malmövägen 10, Malmö 211 18, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MALMÖVÄGEN 10",
      "street2": "",
      "city": "MALMÖ 211 18",
      "state": "",
      "postal_code": "",
      "country": "SWE",
      "normalized_address_key": "MALMOVAGEN 10||MALMO 211 18|||SWE",
      "building_key": "MALMOVAGEN 10||MALMO 211 18|||SWE",
      "phonetic_key": "M451|MALMO 211 18",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-017",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Świętokrzyska 12",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-048",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL ŚWIĘTOKRZYSKA 12",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-048",
      "country": "POL",
      "normalized_address_key": "UL SWIETOKRZYSKA 12||WARSZAWA||00-048|POL",
      "building_key": "UL SWIETOKRZYSKA 12||WARSZAWA||00-048|POL",
      "phonetic_key": "U400|00-04",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-018",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Długa 25, Gdańsk 80-827, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. DŁUGA 25",
      "street2": "",
      "city": "GDAŃSK 80-827",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. DLUGA 25||GDANSK 80-827|||POL",
      "building_key": "UL. DLUGA 25||GDANSK 80-827|||POL",
      "phonetic_key": "U400|GDANSK 80-827",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-019",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Piotrkowska 80",
      "street2": None,
      "city": "Łódź",
      "state": None,
      "postal_code": "90-102",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL PIOTRKOWSKA 80",
      "street2": "",
      "city": "ŁÓDŹ",
      "state": "",
      "postal_code": "90-102",
      "country": "POL",
      "normalized_address_key": "UL PIOTRKOWSKA 80||LODZ||90-102|POL",
      "building_key": "UL PIOTRKOWSKA 80||LODZ||90-102|POL",
      "phonetic_key": "U400|90-10",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-020",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "15 HIGH STREET, FLAT 2, LEEDS LS6 2AA, UNITED KINGDOM",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 HIGH ST",
      "street2": "APT 2",
      "city": "LEEDS",
      "state": "",
      "postal_code": "LS6 2AA",
      "country": "GBR",
      "normalized_address_key": "15 HIGH ST|APT 2|LEEDS||LS6 2AA|GBR",
      "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
      "phonetic_key": "15|H200|LS6 2AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-021",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "100 king st w",
      "street2": "suite 400",
      "city": "toronto",
      "state": "on",
      "postal_code": "m5x 1a9",
      "country": "canada"
    },
    "expected_output": {
      "street1": "100 KING ST W",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "100 KING ST W|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "100 KING ST W||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "100|K520|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-022",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "musterstrasse 12, berlin 10115, germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 12",
      "street2": "",
      "city": "BERLIN 10115",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 12||BERLIN 10115|||DEU",
      "building_key": "MUSTERSTRASSE 12||BERLIN 10115|||DEU",
      "phonetic_key": "M236|BERLIN 10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-023",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 little falls drive",
      "street2": None,
      "city": "wilmington",
      "state": "de",
      "postal_code": "19808",
      "country": "usa"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-024",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 shelton street, london wc2h 9jq, united kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-025",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 48",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 48",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 48||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 48||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-026",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 24, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 24",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 24||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 24||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-027",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 63",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 63",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 63|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 63||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-028",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 21, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 21",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 21||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 21||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-029",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 20",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 20",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 20||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 20||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-030",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-031",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "30 Rue de la République",
      "street2": None,
      "city": "Lyon",
      "state": None,
      "postal_code": "69002",
      "country": "France"
    },
    "expected_output": {
      "street1": "30 RUE DE LA RÉPUBLIQUE",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "building_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "phonetic_key": "30|R000|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-032",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "12 Avenue Foch, Paris 75116, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "12 AV FOCH",
      "street2": "",
      "city": "PARIS 75116",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "12 AV FOCH||PARIS 75116|||FRA",
      "building_key": "12 AV FOCH||PARIS 75116|||FRA",
      "phonetic_key": "12|A100|PARIS 75116",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-033",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "450 Boulevard René-Lévesque Ouest",
      "street2": "Suite 400",
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "450 BD RENÉ-LÉVESQUE O",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "450 BD RENE-LEVESQUE O|STE 400|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "450 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "450|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-034",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "123 Rue Saint-Denis, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "123 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "123|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-035",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Núñez de Balboa 15",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28001",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE NÚÑEZ DE BALBOA 15",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28001",
      "country": "ESP",
      "normalized_address_key": "CALLE NUNEZ DE BALBOA 15|2 B|MADRID||28001|ESP",
      "building_key": "CALLE NUNEZ DE BALBOA 15||MADRID||28001|ESP",
      "phonetic_key": "C400|28001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-036",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 403, Monterrey, NL 64060, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 403",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL 64060",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 403||MONTERREY|NL 64060||MEX",
      "building_key": "AV CONSTITUCION 403||MONTERREY|NL 64060||MEX",
      "phonetic_key": "A100|MONTERREY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-037",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 225",
      "street2": "Piso 5",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 225",
      "street2": "PISO 5",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 225|PISO 5|CIUDAD DE MEXICO|CDMX|06600|MEX",
      "building_key": "PASEO DE LA REFORMA 225||CIUDAD DE MEXICO|CDMX|06600|MEX",
      "phonetic_key": "P200|06600",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-038",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Købmagergade 55, København 1150, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "KØBMAGERGADE 55",
      "street2": "",
      "city": "KØBENHAVN 1150",
      "state": "",
      "postal_code": "",
      "country": "DNK",
      "normalized_address_key": "KOBMAGERGADE 55||KOBENHAVN 1150|||DNK",
      "building_key": "KOBMAGERGADE 55||KOBENHAVN 1150|||DNK",
      "phonetic_key": "K152|KOBENHAVN 1150",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-039",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Västra Hamngatan 10",
      "street2": None,
      "city": "Göteborg",
      "state": None,
      "postal_code": "411 17",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "VÄSTRA HAMNGATAN 10",
      "street2": "",
      "city": "GÖTEBORG",
      "state": "",
      "postal_code": "411 17",
      "country": "SWE",
      "normalized_address_key": "VASTRA HAMNGATAN 10||GOTEBORG||411 17|SWE",
      "building_key": "VASTRA HAMNGATAN 10||GOTEBORG||411 17|SWE",
      "phonetic_key": "V236|411 1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-040",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Malmövägen 13, Malmö 211 18, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MALMÖVÄGEN 13",
      "street2": "",
      "city": "MALMÖ 211 18",
      "state": "",
      "postal_code": "",
      "country": "SWE",
      "normalized_address_key": "MALMOVAGEN 13||MALMO 211 18|||SWE",
      "building_key": "MALMOVAGEN 13||MALMO 211 18|||SWE",
      "phonetic_key": "M451|MALMO 211 18",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-041",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Świętokrzyska 15",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-048",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL ŚWIĘTOKRZYSKA 15",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-048",
      "country": "POL",
      "normalized_address_key": "UL SWIETOKRZYSKA 15||WARSZAWA||00-048|POL",
      "building_key": "UL SWIETOKRZYSKA 15||WARSZAWA||00-048|POL",
      "phonetic_key": "U400|00-04",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-042",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Długa 28, Gdańsk 80-827, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. DŁUGA 28",
      "street2": "",
      "city": "GDAŃSK 80-827",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. DLUGA 28||GDANSK 80-827|||POL",
      "building_key": "UL. DLUGA 28||GDANSK 80-827|||POL",
      "phonetic_key": "U400|GDANSK 80-827",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-043",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Piotrkowska 83",
      "street2": None,
      "city": "Łódź",
      "state": None,
      "postal_code": "90-102",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL PIOTRKOWSKA 83",
      "street2": "",
      "city": "ŁÓDŹ",
      "state": "",
      "postal_code": "90-102",
      "country": "POL",
      "normalized_address_key": "UL PIOTRKOWSKA 83||LODZ||90-102|POL",
      "building_key": "UL PIOTRKOWSKA 83||LODZ||90-102|POL",
      "phonetic_key": "U400|90-10",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-044",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "15 HIGH STREET, FLAT 2, LEEDS LS6 2AA, UNITED KINGDOM",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 HIGH ST",
      "street2": "APT 2",
      "city": "LEEDS",
      "state": "",
      "postal_code": "LS6 2AA",
      "country": "GBR",
      "normalized_address_key": "15 HIGH ST|APT 2|LEEDS||LS6 2AA|GBR",
      "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
      "phonetic_key": "15|H200|LS6 2AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-045",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "100 king st w",
      "street2": "suite 400",
      "city": "toronto",
      "state": "on",
      "postal_code": "m5x 1a9",
      "country": "canada"
    },
    "expected_output": {
      "street1": "100 KING ST W",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "100 KING ST W|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "100 KING ST W||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "100|K520|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-046",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "musterstrasse 15, berlin 10115, germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 15",
      "street2": "",
      "city": "BERLIN 10115",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 15||BERLIN 10115|||DEU",
      "building_key": "MUSTERSTRASSE 15||BERLIN 10115|||DEU",
      "phonetic_key": "M236|BERLIN 10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-047",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 little falls drive",
      "street2": None,
      "city": "wilmington",
      "state": "de",
      "postal_code": "19808",
      "country": "usa"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-048",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 shelton street, london wc2h 9jq, united kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-049",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 51",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 51",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 51||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 51||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-050",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 27, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 27",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 27||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 27||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-051",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 66",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 66",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 66|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 66||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-052",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 24, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 24",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 24||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 24||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-053",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 23",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 23",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 23||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 23||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-054",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-055",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "30 Rue de la République",
      "street2": None,
      "city": "Lyon",
      "state": None,
      "postal_code": "69002",
      "country": "France"
    },
    "expected_output": {
      "street1": "30 RUE DE LA RÉPUBLIQUE",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "building_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "phonetic_key": "30|R000|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-056",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "12 Avenue Foch, Paris 75116, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "12 AV FOCH",
      "street2": "",
      "city": "PARIS 75116",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "12 AV FOCH||PARIS 75116|||FRA",
      "building_key": "12 AV FOCH||PARIS 75116|||FRA",
      "phonetic_key": "12|A100|PARIS 75116",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-057",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "450 Boulevard René-Lévesque Ouest",
      "street2": "Suite 400",
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "450 BD RENÉ-LÉVESQUE O",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "450 BD RENE-LEVESQUE O|STE 400|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "450 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "450|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-058",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "123 Rue Saint-Denis, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "123 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "123|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-059",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Núñez de Balboa 18",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28001",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE NÚÑEZ DE BALBOA 18",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28001",
      "country": "ESP",
      "normalized_address_key": "CALLE NUNEZ DE BALBOA 18|2 B|MADRID||28001|ESP",
      "building_key": "CALLE NUNEZ DE BALBOA 18||MADRID||28001|ESP",
      "phonetic_key": "C400|28001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-060",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 406, Monterrey, NL 64060, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 406",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL 64060",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 406||MONTERREY|NL 64060||MEX",
      "building_key": "AV CONSTITUCION 406||MONTERREY|NL 64060||MEX",
      "phonetic_key": "A100|MONTERREY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-061",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 228",
      "street2": "Piso 5",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 228",
      "street2": "PISO 5",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 228|PISO 5|CIUDAD DE MEXICO|CDMX|06600|MEX",
      "building_key": "PASEO DE LA REFORMA 228||CIUDAD DE MEXICO|CDMX|06600|MEX",
      "phonetic_key": "P200|06600",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-062",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Købmagergade 58, København 1150, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "KØBMAGERGADE 58",
      "street2": "",
      "city": "KØBENHAVN 1150",
      "state": "",
      "postal_code": "",
      "country": "DNK",
      "normalized_address_key": "KOBMAGERGADE 58||KOBENHAVN 1150|||DNK",
      "building_key": "KOBMAGERGADE 58||KOBENHAVN 1150|||DNK",
      "phonetic_key": "K152|KOBENHAVN 1150",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-063",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Västra Hamngatan 13",
      "street2": None,
      "city": "Göteborg",
      "state": None,
      "postal_code": "411 17",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "VÄSTRA HAMNGATAN 13",
      "street2": "",
      "city": "GÖTEBORG",
      "state": "",
      "postal_code": "411 17",
      "country": "SWE",
      "normalized_address_key": "VASTRA HAMNGATAN 13||GOTEBORG||411 17|SWE",
      "building_key": "VASTRA HAMNGATAN 13||GOTEBORG||411 17|SWE",
      "phonetic_key": "V236|411 1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-064",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Malmövägen 16, Malmö 211 18, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MALMÖVÄGEN 16",
      "street2": "",
      "city": "MALMÖ 211 18",
      "state": "",
      "postal_code": "",
      "country": "SWE",
      "normalized_address_key": "MALMOVAGEN 16||MALMO 211 18|||SWE",
      "building_key": "MALMOVAGEN 16||MALMO 211 18|||SWE",
      "phonetic_key": "M451|MALMO 211 18",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-065",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Świętokrzyska 18",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-048",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL ŚWIĘTOKRZYSKA 18",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-048",
      "country": "POL",
      "normalized_address_key": "UL SWIETOKRZYSKA 18||WARSZAWA||00-048|POL",
      "building_key": "UL SWIETOKRZYSKA 18||WARSZAWA||00-048|POL",
      "phonetic_key": "U400|00-04",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-066",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Długa 31, Gdańsk 80-827, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. DŁUGA 31",
      "street2": "",
      "city": "GDAŃSK 80-827",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. DLUGA 31||GDANSK 80-827|||POL",
      "building_key": "UL. DLUGA 31||GDANSK 80-827|||POL",
      "phonetic_key": "U400|GDANSK 80-827",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-067",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Piotrkowska 86",
      "street2": None,
      "city": "Łódź",
      "state": None,
      "postal_code": "90-102",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL PIOTRKOWSKA 86",
      "street2": "",
      "city": "ŁÓDŹ",
      "state": "",
      "postal_code": "90-102",
      "country": "POL",
      "normalized_address_key": "UL PIOTRKOWSKA 86||LODZ||90-102|POL",
      "building_key": "UL PIOTRKOWSKA 86||LODZ||90-102|POL",
      "phonetic_key": "U400|90-10",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-068",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "15 HIGH STREET, FLAT 2, LEEDS LS6 2AA, UNITED KINGDOM",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 HIGH ST",
      "street2": "APT 2",
      "city": "LEEDS",
      "state": "",
      "postal_code": "LS6 2AA",
      "country": "GBR",
      "normalized_address_key": "15 HIGH ST|APT 2|LEEDS||LS6 2AA|GBR",
      "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
      "phonetic_key": "15|H200|LS6 2AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-069",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "100 king st w",
      "street2": "suite 400",
      "city": "toronto",
      "state": "on",
      "postal_code": "m5x 1a9",
      "country": "canada"
    },
    "expected_output": {
      "street1": "100 KING ST W",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "100 KING ST W|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "100 KING ST W||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "100|K520|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-070",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "musterstrasse 18, berlin 10115, germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 18",
      "street2": "",
      "city": "BERLIN 10115",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 18||BERLIN 10115|||DEU",
      "building_key": "MUSTERSTRASSE 18||BERLIN 10115|||DEU",
      "phonetic_key": "M236|BERLIN 10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-071",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 little falls drive",
      "street2": None,
      "city": "wilmington",
      "state": "de",
      "postal_code": "19808",
      "country": "usa"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-072",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 shelton street, london wc2h 9jq, united kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-073",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 54",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 54",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 54||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 54||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-074",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 30, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 30",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 30||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 30||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-075",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 69",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 69",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 69|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 69||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-076",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 27, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 27",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 27||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 27||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-077",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 26",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 26",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 26||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 26||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-078",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-079",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "30 Rue de la République",
      "street2": None,
      "city": "Lyon",
      "state": None,
      "postal_code": "69002",
      "country": "France"
    },
    "expected_output": {
      "street1": "30 RUE DE LA RÉPUBLIQUE",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "building_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "phonetic_key": "30|R000|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-080",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "12 Avenue Foch, Paris 75116, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "12 AV FOCH",
      "street2": "",
      "city": "PARIS 75116",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "12 AV FOCH||PARIS 75116|||FRA",
      "building_key": "12 AV FOCH||PARIS 75116|||FRA",
      "phonetic_key": "12|A100|PARIS 75116",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-081",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "450 Boulevard René-Lévesque Ouest",
      "street2": "Suite 400",
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "450 BD RENÉ-LÉVESQUE O",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "450 BD RENE-LEVESQUE O|STE 400|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "450 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "450|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-082",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "123 Rue Saint-Denis, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "123 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "123|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-083",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Núñez de Balboa 21",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28001",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE NÚÑEZ DE BALBOA 21",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28001",
      "country": "ESP",
      "normalized_address_key": "CALLE NUNEZ DE BALBOA 21|2 B|MADRID||28001|ESP",
      "building_key": "CALLE NUNEZ DE BALBOA 21||MADRID||28001|ESP",
      "phonetic_key": "C400|28001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-084",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 409, Monterrey, NL 64060, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 409",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL 64060",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 409||MONTERREY|NL 64060||MEX",
      "building_key": "AV CONSTITUCION 409||MONTERREY|NL 64060||MEX",
      "phonetic_key": "A100|MONTERREY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-085",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 231",
      "street2": "Piso 5",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 231",
      "street2": "PISO 5",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 231|PISO 5|CIUDAD DE MEXICO|CDMX|06600|MEX",
      "building_key": "PASEO DE LA REFORMA 231||CIUDAD DE MEXICO|CDMX|06600|MEX",
      "phonetic_key": "P200|06600",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-086",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Købmagergade 61, København 1150, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "KØBMAGERGADE 61",
      "street2": "",
      "city": "KØBENHAVN 1150",
      "state": "",
      "postal_code": "",
      "country": "DNK",
      "normalized_address_key": "KOBMAGERGADE 61||KOBENHAVN 1150|||DNK",
      "building_key": "KOBMAGERGADE 61||KOBENHAVN 1150|||DNK",
      "phonetic_key": "K152|KOBENHAVN 1150",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-087",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Västra Hamngatan 16",
      "street2": None,
      "city": "Göteborg",
      "state": None,
      "postal_code": "411 17",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "VÄSTRA HAMNGATAN 16",
      "street2": "",
      "city": "GÖTEBORG",
      "state": "",
      "postal_code": "411 17",
      "country": "SWE",
      "normalized_address_key": "VASTRA HAMNGATAN 16||GOTEBORG||411 17|SWE",
      "building_key": "VASTRA HAMNGATAN 16||GOTEBORG||411 17|SWE",
      "phonetic_key": "V236|411 1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-088",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Malmövägen 19, Malmö 211 18, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MALMÖVÄGEN 19",
      "street2": "",
      "city": "MALMÖ 211 18",
      "state": "",
      "postal_code": "",
      "country": "SWE",
      "normalized_address_key": "MALMOVAGEN 19||MALMO 211 18|||SWE",
      "building_key": "MALMOVAGEN 19||MALMO 211 18|||SWE",
      "phonetic_key": "M451|MALMO 211 18",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-089",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Świętokrzyska 21",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-048",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL ŚWIĘTOKRZYSKA 21",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-048",
      "country": "POL",
      "normalized_address_key": "UL SWIETOKRZYSKA 21||WARSZAWA||00-048|POL",
      "building_key": "UL SWIETOKRZYSKA 21||WARSZAWA||00-048|POL",
      "phonetic_key": "U400|00-04",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-090",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Długa 34, Gdańsk 80-827, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. DŁUGA 34",
      "street2": "",
      "city": "GDAŃSK 80-827",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. DLUGA 34||GDANSK 80-827|||POL",
      "building_key": "UL. DLUGA 34||GDANSK 80-827|||POL",
      "phonetic_key": "U400|GDANSK 80-827",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-091",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Piotrkowska 89",
      "street2": None,
      "city": "Łódź",
      "state": None,
      "postal_code": "90-102",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL PIOTRKOWSKA 89",
      "street2": "",
      "city": "ŁÓDŹ",
      "state": "",
      "postal_code": "90-102",
      "country": "POL",
      "normalized_address_key": "UL PIOTRKOWSKA 89||LODZ||90-102|POL",
      "building_key": "UL PIOTRKOWSKA 89||LODZ||90-102|POL",
      "phonetic_key": "U400|90-10",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-092",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "15 HIGH STREET, FLAT 2, LEEDS LS6 2AA, UNITED KINGDOM",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 HIGH ST",
      "street2": "APT 2",
      "city": "LEEDS",
      "state": "",
      "postal_code": "LS6 2AA",
      "country": "GBR",
      "normalized_address_key": "15 HIGH ST|APT 2|LEEDS||LS6 2AA|GBR",
      "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
      "phonetic_key": "15|H200|LS6 2AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-093",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "100 king st w",
      "street2": "suite 400",
      "city": "toronto",
      "state": "on",
      "postal_code": "m5x 1a9",
      "country": "canada"
    },
    "expected_output": {
      "street1": "100 KING ST W",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "100 KING ST W|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "100 KING ST W||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "100|K520|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-094",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "musterstrasse 21, berlin 10115, germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 21",
      "street2": "",
      "city": "BERLIN 10115",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 21||BERLIN 10115|||DEU",
      "building_key": "MUSTERSTRASSE 21||BERLIN 10115|||DEU",
      "phonetic_key": "M236|BERLIN 10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-095",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 little falls drive",
      "street2": None,
      "city": "wilmington",
      "state": "de",
      "postal_code": "19808",
      "country": "usa"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-096",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 shelton street, london wc2h 9jq, united kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-097",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 57",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 57",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 57||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 57||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-098",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 33, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 33",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 33||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 33||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-099",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 72",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 72",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 72|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 72||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-100",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 30, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 30",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 30||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 30||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-101",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 29",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 29",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 29||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 29||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-102",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-103",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "30 Rue de la République",
      "street2": None,
      "city": "Lyon",
      "state": None,
      "postal_code": "69002",
      "country": "France"
    },
    "expected_output": {
      "street1": "30 RUE DE LA RÉPUBLIQUE",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "building_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "phonetic_key": "30|R000|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-104",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "12 Avenue Foch, Paris 75116, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "12 AV FOCH",
      "street2": "",
      "city": "PARIS 75116",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "12 AV FOCH||PARIS 75116|||FRA",
      "building_key": "12 AV FOCH||PARIS 75116|||FRA",
      "phonetic_key": "12|A100|PARIS 75116",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-105",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "450 Boulevard René-Lévesque Ouest",
      "street2": "Suite 400",
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "450 BD RENÉ-LÉVESQUE O",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "450 BD RENE-LEVESQUE O|STE 400|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "450 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "450|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-106",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "123 Rue Saint-Denis, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "123 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "123|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-107",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Núñez de Balboa 24",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28001",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE NÚÑEZ DE BALBOA 24",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28001",
      "country": "ESP",
      "normalized_address_key": "CALLE NUNEZ DE BALBOA 24|2 B|MADRID||28001|ESP",
      "building_key": "CALLE NUNEZ DE BALBOA 24||MADRID||28001|ESP",
      "phonetic_key": "C400|28001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-108",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 412, Monterrey, NL 64060, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 412",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL 64060",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 412||MONTERREY|NL 64060||MEX",
      "building_key": "AV CONSTITUCION 412||MONTERREY|NL 64060||MEX",
      "phonetic_key": "A100|MONTERREY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-109",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 234",
      "street2": "Piso 5",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 234",
      "street2": "PISO 5",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 234|PISO 5|CIUDAD DE MEXICO|CDMX|06600|MEX",
      "building_key": "PASEO DE LA REFORMA 234||CIUDAD DE MEXICO|CDMX|06600|MEX",
      "phonetic_key": "P200|06600",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-110",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Købmagergade 64, København 1150, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "KØBMAGERGADE 64",
      "street2": "",
      "city": "KØBENHAVN 1150",
      "state": "",
      "postal_code": "",
      "country": "DNK",
      "normalized_address_key": "KOBMAGERGADE 64||KOBENHAVN 1150|||DNK",
      "building_key": "KOBMAGERGADE 64||KOBENHAVN 1150|||DNK",
      "phonetic_key": "K152|KOBENHAVN 1150",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-111",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Västra Hamngatan 19",
      "street2": None,
      "city": "Göteborg",
      "state": None,
      "postal_code": "411 17",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "VÄSTRA HAMNGATAN 19",
      "street2": "",
      "city": "GÖTEBORG",
      "state": "",
      "postal_code": "411 17",
      "country": "SWE",
      "normalized_address_key": "VASTRA HAMNGATAN 19||GOTEBORG||411 17|SWE",
      "building_key": "VASTRA HAMNGATAN 19||GOTEBORG||411 17|SWE",
      "phonetic_key": "V236|411 1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-112",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Malmövägen 22, Malmö 211 18, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MALMÖVÄGEN 22",
      "street2": "",
      "city": "MALMÖ 211 18",
      "state": "",
      "postal_code": "",
      "country": "SWE",
      "normalized_address_key": "MALMOVAGEN 22||MALMO 211 18|||SWE",
      "building_key": "MALMOVAGEN 22||MALMO 211 18|||SWE",
      "phonetic_key": "M451|MALMO 211 18",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-113",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Świętokrzyska 24",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-048",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL ŚWIĘTOKRZYSKA 24",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-048",
      "country": "POL",
      "normalized_address_key": "UL SWIETOKRZYSKA 24||WARSZAWA||00-048|POL",
      "building_key": "UL SWIETOKRZYSKA 24||WARSZAWA||00-048|POL",
      "phonetic_key": "U400|00-04",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-114",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Długa 37, Gdańsk 80-827, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. DŁUGA 37",
      "street2": "",
      "city": "GDAŃSK 80-827",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. DLUGA 37||GDANSK 80-827|||POL",
      "building_key": "UL. DLUGA 37||GDANSK 80-827|||POL",
      "phonetic_key": "U400|GDANSK 80-827",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-115",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Piotrkowska 92",
      "street2": None,
      "city": "Łódź",
      "state": None,
      "postal_code": "90-102",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL PIOTRKOWSKA 92",
      "street2": "",
      "city": "ŁÓDŹ",
      "state": "",
      "postal_code": "90-102",
      "country": "POL",
      "normalized_address_key": "UL PIOTRKOWSKA 92||LODZ||90-102|POL",
      "building_key": "UL PIOTRKOWSKA 92||LODZ||90-102|POL",
      "phonetic_key": "U400|90-10",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-116",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "15 HIGH STREET, FLAT 2, LEEDS LS6 2AA, UNITED KINGDOM",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 HIGH ST",
      "street2": "APT 2",
      "city": "LEEDS",
      "state": "",
      "postal_code": "LS6 2AA",
      "country": "GBR",
      "normalized_address_key": "15 HIGH ST|APT 2|LEEDS||LS6 2AA|GBR",
      "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
      "phonetic_key": "15|H200|LS6 2AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-117",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "100 king st w",
      "street2": "suite 400",
      "city": "toronto",
      "state": "on",
      "postal_code": "m5x 1a9",
      "country": "canada"
    },
    "expected_output": {
      "street1": "100 KING ST W",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "100 KING ST W|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "100 KING ST W||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "100|K520|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-118",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "musterstrasse 24, berlin 10115, germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 24",
      "street2": "",
      "city": "BERLIN 10115",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 24||BERLIN 10115|||DEU",
      "building_key": "MUSTERSTRASSE 24||BERLIN 10115|||DEU",
      "phonetic_key": "M236|BERLIN 10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-119",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 little falls drive",
      "street2": None,
      "city": "wilmington",
      "state": "de",
      "postal_code": "19808",
      "country": "usa"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-120",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 shelton street, london wc2h 9jq, united kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-121",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 60",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 60",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 60||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 60||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-122",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 36, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 36",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 36||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 36||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-123",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 75",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 75",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 75|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 75||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-124",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 33, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 33",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 33||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 33||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-125",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 32",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 32",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 32||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 32||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-126",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-127",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "30 Rue de la République",
      "street2": None,
      "city": "Lyon",
      "state": None,
      "postal_code": "69002",
      "country": "France"
    },
    "expected_output": {
      "street1": "30 RUE DE LA RÉPUBLIQUE",
      "street2": "",
      "city": "LYON",
      "state": "",
      "postal_code": "69002",
      "country": "FRA",
      "normalized_address_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "building_key": "30 RUE DE LA REPUBLIQUE||LYON||69002|FRA",
      "phonetic_key": "30|R000|69002",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-128",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "12 Avenue Foch, Paris 75116, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "12 AV FOCH",
      "street2": "",
      "city": "PARIS 75116",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "12 AV FOCH||PARIS 75116|||FRA",
      "building_key": "12 AV FOCH||PARIS 75116|||FRA",
      "phonetic_key": "12|A100|PARIS 75116",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-129",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "450 Boulevard René-Lévesque Ouest",
      "street2": "Suite 400",
      "city": "Montréal",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "Canada"
    },
    "expected_output": {
      "street1": "450 BD RENÉ-LÉVESQUE O",
      "street2": "STE 400",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "450 BD RENE-LEVESQUE O|STE 400|MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "450 BD RENE-LEVESQUE O||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "450|B300|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-130",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "123 Rue Saint-Denis, Montréal, QC H2X 3J8, Canada",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "123 RUE SAINT-DENIS",
      "street2": "",
      "city": "MONTRÉAL",
      "state": "QC",
      "postal_code": "H2X 3J8",
      "country": "CAN",
      "normalized_address_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "building_key": "123 RUE SAINT-DENIS||MONTREAL|QC|H2X 3J8|CAN",
      "phonetic_key": "123|R000|H2X 3J8",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-131",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "ESP",
    "raw_input": {
      "street1": "Calle Núñez de Balboa 27",
      "street2": "2º B",
      "city": "Madrid",
      "state": None,
      "postal_code": "28001",
      "country": "Spain"
    },
    "expected_output": {
      "street1": "CALLE NÚÑEZ DE BALBOA 27",
      "street2": "2 B",
      "city": "MADRID",
      "state": "",
      "postal_code": "28001",
      "country": "ESP",
      "normalized_address_key": "CALLE NUNEZ DE BALBOA 27|2 B|MADRID||28001|ESP",
      "building_key": "CALLE NUNEZ DE BALBOA 27||MADRID||28001|ESP",
      "phonetic_key": "C400|28001",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-132",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Av. Constitución 415, Monterrey, NL 64060, Mexico",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "AV CONSTITUCIÓN 415",
      "street2": "",
      "city": "MONTERREY",
      "state": "NL 64060",
      "postal_code": "",
      "country": "MEX",
      "normalized_address_key": "AV CONSTITUCION 415||MONTERREY|NL 64060||MEX",
      "building_key": "AV CONSTITUCION 415||MONTERREY|NL 64060||MEX",
      "phonetic_key": "A100|MONTERREY",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-133",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "MEX",
    "raw_input": {
      "street1": "Paseo de la Reforma 237",
      "street2": "Piso 5",
      "city": "Ciudad de México",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "Mexico"
    },
    "expected_output": {
      "street1": "PASEO DE LA REFORMA 237",
      "street2": "PISO 5",
      "city": "CIUDAD DE MÉXICO",
      "state": "CDMX",
      "postal_code": "06600",
      "country": "MEX",
      "normalized_address_key": "PASEO DE LA REFORMA 237|PISO 5|CIUDAD DE MEXICO|CDMX|06600|MEX",
      "building_key": "PASEO DE LA REFORMA 237||CIUDAD DE MEXICO|CDMX|06600|MEX",
      "phonetic_key": "P200|06600",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-134",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DNK",
    "raw_input": {
      "street1": "Købmagergade 67, København 1150, Denmark",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "KØBMAGERGADE 67",
      "street2": "",
      "city": "KØBENHAVN 1150",
      "state": "",
      "postal_code": "",
      "country": "DNK",
      "normalized_address_key": "KOBMAGERGADE 67||KOBENHAVN 1150|||DNK",
      "building_key": "KOBMAGERGADE 67||KOBENHAVN 1150|||DNK",
      "phonetic_key": "K152|KOBENHAVN 1150",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-135",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Västra Hamngatan 22",
      "street2": None,
      "city": "Göteborg",
      "state": None,
      "postal_code": "411 17",
      "country": "Sweden"
    },
    "expected_output": {
      "street1": "VÄSTRA HAMNGATAN 22",
      "street2": "",
      "city": "GÖTEBORG",
      "state": "",
      "postal_code": "411 17",
      "country": "SWE",
      "normalized_address_key": "VASTRA HAMNGATAN 22||GOTEBORG||411 17|SWE",
      "building_key": "VASTRA HAMNGATAN 22||GOTEBORG||411 17|SWE",
      "phonetic_key": "V236|411 1",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-136",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "SWE",
    "raw_input": {
      "street1": "Malmövägen 25, Malmö 211 18, Sweden",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MALMÖVÄGEN 25",
      "street2": "",
      "city": "MALMÖ 211 18",
      "state": "",
      "postal_code": "",
      "country": "SWE",
      "normalized_address_key": "MALMOVAGEN 25||MALMO 211 18|||SWE",
      "building_key": "MALMOVAGEN 25||MALMO 211 18|||SWE",
      "phonetic_key": "M451|MALMO 211 18",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-137",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Świętokrzyska 27",
      "street2": None,
      "city": "Warszawa",
      "state": None,
      "postal_code": "00-048",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL ŚWIĘTOKRZYSKA 27",
      "street2": "",
      "city": "WARSZAWA",
      "state": "",
      "postal_code": "00-048",
      "country": "POL",
      "normalized_address_key": "UL SWIETOKRZYSKA 27||WARSZAWA||00-048|POL",
      "building_key": "UL SWIETOKRZYSKA 27||WARSZAWA||00-048|POL",
      "phonetic_key": "U400|00-04",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-138",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Długa 40, Gdańsk 80-827, Poland",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "UL. DŁUGA 40",
      "street2": "",
      "city": "GDAŃSK 80-827",
      "state": "",
      "postal_code": "",
      "country": "POL",
      "normalized_address_key": "UL. DLUGA 40||GDANSK 80-827|||POL",
      "building_key": "UL. DLUGA 40||GDANSK 80-827|||POL",
      "phonetic_key": "U400|GDANSK 80-827",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-139",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "POL",
    "raw_input": {
      "street1": "ul. Piotrkowska 95",
      "street2": None,
      "city": "Łódź",
      "state": None,
      "postal_code": "90-102",
      "country": "Poland"
    },
    "expected_output": {
      "street1": "UL PIOTRKOWSKA 95",
      "street2": "",
      "city": "ŁÓDŹ",
      "state": "",
      "postal_code": "90-102",
      "country": "POL",
      "normalized_address_key": "UL PIOTRKOWSKA 95||LODZ||90-102|POL",
      "building_key": "UL PIOTRKOWSKA 95||LODZ||90-102|POL",
      "phonetic_key": "U400|90-10",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-140",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "15 HIGH STREET, FLAT 2, LEEDS LS6 2AA, UNITED KINGDOM",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "15 HIGH ST",
      "street2": "APT 2",
      "city": "LEEDS",
      "state": "",
      "postal_code": "LS6 2AA",
      "country": "GBR",
      "normalized_address_key": "15 HIGH ST|APT 2|LEEDS||LS6 2AA|GBR",
      "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
      "phonetic_key": "15|H200|LS6 2AA",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-141",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "CAN",
    "raw_input": {
      "street1": "100 king st w",
      "street2": "suite 400",
      "city": "toronto",
      "state": "on",
      "postal_code": "m5x 1a9",
      "country": "canada"
    },
    "expected_output": {
      "street1": "100 KING ST W",
      "street2": "STE 400",
      "city": "TORONTO",
      "state": "ON",
      "postal_code": "M5X 1A9",
      "country": "CAN",
      "normalized_address_key": "100 KING ST W|STE 400|TORONTO|ON|M5X 1A9|CAN",
      "building_key": "100 KING ST W||TORONTO|ON|M5X 1A9|CAN",
      "phonetic_key": "100|K520|M5X 1A9",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-142",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "musterstrasse 27, berlin 10115, germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "MUSTERSTRASSE 27",
      "street2": "",
      "city": "BERLIN 10115",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "MUSTERSTRASSE 27||BERLIN 10115|||DEU",
      "building_key": "MUSTERSTRASSE 27||BERLIN 10115|||DEU",
      "phonetic_key": "M236|BERLIN 10115",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-143",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "USA",
    "raw_input": {
      "street1": "251 little falls drive",
      "street2": None,
      "city": "wilmington",
      "state": "de",
      "postal_code": "19808",
      "country": "usa"
    },
    "expected_output": {
      "street1": "251 LITTLE FALLS DR",
      "street2": "",
      "city": "WILMINGTON",
      "state": "DE",
      "postal_code": "19808",
      "country": "USA",
      "normalized_address_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "building_key": "251 LITTLE FALLS DR||WILMINGTON|DE|19808|USA",
      "phonetic_key": "251|L340|19808",
      "address_status": "standardized",
      "is_us": True,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-144",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "GBR",
    "raw_input": {
      "street1": "71-75 shelton street, london wc2h 9jq, united kingdom",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "71-75 SHELTON ST",
      "street2": "",
      "city": "LONDON",
      "state": "",
      "postal_code": "WC2H 9JQ",
      "country": "GBR",
      "normalized_address_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "building_key": "71-75 SHELTON ST||LONDON||WC2H 9JQ|GBR",
      "phonetic_key": "71-75|S435|WC2H 9JQ",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": True,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-145",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Münchner Straße 63",
      "street2": None,
      "city": "München",
      "state": None,
      "postal_code": "80331",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "MÜNCHNER STRASSE 63",
      "street2": "",
      "city": "MÜNCHEN",
      "state": "",
      "postal_code": "80331",
      "country": "DEU",
      "normalized_address_key": "MUNCHNER STRASSE 63||MUNCHEN||80331|DEU",
      "building_key": "MUNCHNER STRASSE 63||MUNCHEN||80331|DEU",
      "phonetic_key": "M525|80331",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-146",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Große Bleichen 39, Hamburg 20354, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "GROSSE BLEICHEN 39",
      "street2": "",
      "city": "HAMBURG 20354",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "GROSSE BLEICHEN 39||HAMBURG 20354|||DEU",
      "building_key": "GROSSE BLEICHEN 39||HAMBURG 20354|||DEU",
      "phonetic_key": "G620|HAMBURG 20354",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-147",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Königsallee 78",
      "street2": "Etage 3",
      "city": "Düsseldorf",
      "state": None,
      "postal_code": "40212",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "KÖNIGSALLEE 78",
      "street2": "ETAGE 3",
      "city": "DÜSSELDORF",
      "state": "",
      "postal_code": "40212",
      "country": "DEU",
      "normalized_address_key": "KONIGSALLEE 78|ETAGE 3|DUSSELDORF||40212|DEU",
      "building_key": "KONIGSALLEE 78||DUSSELDORF||40212|DEU",
      "phonetic_key": "K524|40212",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-148",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Nürnberger Straße 36, Nürnberg 90402, Germany",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "NÜRNBERGER STRASSE 36",
      "street2": "",
      "city": "NÜRNBERG 90402",
      "state": "",
      "postal_code": "",
      "country": "DEU",
      "normalized_address_key": "NURNBERGER STRASSE 36||NURNBERG 90402|||DEU",
      "building_key": "NURNBERGER STRASSE 36||NURNBERG 90402|||DEU",
      "phonetic_key": "N651|NURNBERG 90402",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-149",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "DEU",
    "raw_input": {
      "street1": "Lützowplatz 35",
      "street2": None,
      "city": "Berlin",
      "state": None,
      "postal_code": "10785",
      "country": "Germany"
    },
    "expected_output": {
      "street1": "LÜTZOWPLATZ 35",
      "street2": "",
      "city": "BERLIN",
      "state": "",
      "postal_code": "10785",
      "country": "DEU",
      "normalized_address_key": "LUTZOWPLATZ 35||BERLIN||10785|DEU",
      "building_key": "LUTZOWPLATZ 35||BERLIN||10785|DEU",
      "phonetic_key": "L321|10785",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  },
  {
    "test_id": "INTL-06-150",
    "category": "multilingual_diacritics_messy",
    "jurisdiction": "FRA",
    "raw_input": {
      "street1": "80 Rue François 1er, Paris 75008, France",
      "street2": None,
      "city": None,
      "state": None,
      "postal_code": None,
      "country": None
    },
    "expected_output": {
      "street1": "80 RUE FRANÇOIS 1ER",
      "street2": "",
      "city": "PARIS 75008",
      "state": "",
      "postal_code": "",
      "country": "FRA",
      "normalized_address_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "building_key": "80 RUE FRANCOIS 1ER||PARIS 75008|||FRA",
      "phonetic_key": "80|R000|PARIS 75008",
      "address_status": "standardized",
      "is_us": False,
      "is_registered_agent_hub": False,
      "dependent_locality": None,
      "building_name": None,
      "is_private_residence": False
    }
  }
]
