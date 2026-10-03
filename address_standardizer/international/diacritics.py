"""Unicode diacritic normalization and deterministic ASCII key folding."""

import unicodedata
from typing import Dict, Optional

LIGATURE_MAP: Dict[str, str] = {
    "ß": "SS",
    "ẞ": "SS",
    "æ": "AE",
    "Æ": "AE",
    "œ": "OE",
    "Œ": "OE",
    "ø": "O",
    "Ø": "O",
    "đ": "D",
    "Đ": "D",
    "ł": "L",
    "Ł": "L",
    "ð": "D",
    "Ð": "D",
    "þ": "TH",
    "Þ": "TH",
}


def normalize_to_canonical_unicode(text: Optional[str]) -> str:
    """Normalize whitespace and apply canonical NFC Unicode representation."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", " ".join(text.split()))


def fold_to_ascii_key(text: Optional[str]) -> str:
    """Deterministic ASCII key folding for normalized_address_key and building_key.

    1. Explicit ligature replacements (ß -> SS, æ -> AE, etc.).
    2. NFKD decomposition to separate base characters from combining marks.
    3. Filter non-spacing combining marks (category != 'Mn').
    4. Encode to ASCII, decode to uppercase string.
    5. Clean redundant whitespace.
    """
    if not text:
        return ""

    folded = text
    for lig, replacement in LIGATURE_MAP.items():
        if lig in folded:
            folded = folded.replace(lig, replacement)

    decomposed = unicodedata.normalize("NFKD", folded)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    ascii_clean = stripped.encode("ascii", "ignore").decode("ascii").upper()
    return " ".join(ascii_clean.split())
