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
    st_raw = street1.strip().upper()
    m_pob = re.match(r"^(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\s+([A-Z0-9\-]+)", st_raw)
    if m_pob:
        loc = (
            postal_or_zip.strip()[:5]
            if postal_or_zip and len(postal_or_zip.strip()) >= 5
            else (postal_or_zip.strip() if postal_or_zip else city.strip())
        )
        return f"POB {m_pob.group(1)}|{loc}".strip("|")

    st_clean = re.sub(r"[,\.;:#]+", " ", st_raw).strip()
    st_clean = re.sub(r"\s+", " ", st_clean)
    parts = st_clean.split()
    if not parts:
        return None

    if re.search(r"\d", parts[0]):
        house_num = parts[0]
        words = parts[1:]
    else:
        house_num = ""
        words = parts[:]

    # Strip pre-directional
    if len(words) > 1 and (words[0] in DIRECTIONALS or words[0] in DIRECTIONALS.values()):
        words = words[1:]

    # Strip post-directional
    if len(words) > 1 and (words[-1] in DIRECTIONALS or words[-1] in DIRECTIONALS.values()):
        words = words[:-1]

    # Strip street suffix at end
    if len(words) > 1 and (words[-1] in STREET_SUFFIXES or words[-1] in STREET_SUFFIXES.values()):
        words = words[:-1]

    street_word = words[0] if words else (parts[1] if len(parts) > 1 else parts[0])
    snd = compute_soundex(street_word)
    loc = (
        postal_or_zip.strip()[:5]
        if (postal_or_zip and len(postal_or_zip.strip()) >= 5)
        else city.strip()
    )
    res = f"{house_num}|{snd}|{loc}".strip("|")
    return res or None
