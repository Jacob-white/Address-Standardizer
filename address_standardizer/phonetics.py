"""
Phonetic Matching & Fuzzy Blocking Keys.
=========================================
Implements American Soundex and phonetic compound key generation to enable
typo-tolerant entity resolution and address deduplication without third-party C dependencies.
"""

import re
from typing import Optional
from address_standardizer.tables import STREET_SUFFIXES, DIRECTIONALS


def compute_soundex(token: str) -> str:
    """Computes standard American Soundex code for a word token."""
    clean = re.sub(r"[^A-Z]", "", token.upper())
    if not clean:
        return ""
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    first_letter = clean[0]
    encoded = [first_letter]
    prev_code = mapping.get(first_letter, '0')
    for char in clean[1:]:
        code = mapping.get(char, '0')
        if code != '0':
            if code != prev_code:
                encoded.append(code)
            prev_code = code
        elif char in ('A', 'E', 'I', 'O', 'U', 'Y'):
            prev_code = '0'
        # H and W do not reset prev_code in American Soundex
    soundex_code = "".join(encoded)
    return (soundex_code + "0000")[:4]


def generate_phonetic_address_key(street1: str, postal_or_zip: str = "", city: str = "") -> Optional[str]:
    """
    Generates a fuzzy blocking key for deduplication and typo detection:
    Format: {STREET_NUM}|{SOUNDEX_OF_STREET_NAME}|{ZIP5_OR_CITY}
    Example: '555 MONTGOMERY ST', '94111' -> '555|M532|94111'
             '555 MONTGOMERI ST', '94111' -> '555|M532|94111'
    """
    if not street1:
        return None
    st_clean = street1.strip().upper()
    m_pob = re.match(r"^PO BOX\s+([A-Z0-9\-]+)", st_clean)
    if m_pob:
        loc = postal_or_zip[:5] if postal_or_zip else city
        return f"POB {m_pob.group(1)}|{loc}"

    parts = st_clean.split()
    if not parts:
        return None

    # House number is first token if it has digits
    if re.search(r"\d", parts[0]):
        house_num = parts[0]
        name_tokens = [
            p for p in parts[1:]
            if p not in STREET_SUFFIXES.values() and p not in DIRECTIONALS.values()
        ]
        street_word = name_tokens[0] if name_tokens else (parts[1] if len(parts) > 1 else "")
    else:
        house_num = ""
        name_tokens = [
            p for p in parts
            if p not in STREET_SUFFIXES.values() and p not in DIRECTIONALS.values()
        ]
        street_word = name_tokens[0] if name_tokens else parts[0]

    snd = compute_soundex(street_word)
    loc = postal_or_zip[:5] if (postal_or_zip and len(postal_or_zip) >= 5) else city
    res = f"{house_num}|{snd}|{loc}".strip("|")
    return res or None
