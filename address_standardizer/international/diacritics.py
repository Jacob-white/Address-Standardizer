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

CYRILLIC_GREEK_MAP: Dict[str, str] = {
    # Cyrillic uppercase
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Ґ": "G", "Д": "D", "Ђ": "DJ", "Ѓ": "GJ",
    "Е": "E", "Ё": "E", "Є": "YE", "Ж": "ZH", "З": "Z", "Ѕ": "DZ", "И": "I", "І": "I",
    "Ї": "YI", "Й": "Y", "Ј": "J", "К": "K", "Л": "L", "Љ": "LJ", "М": "M", "Н": "N",
    "Њ": "NJ", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "Ћ": "C", "Ќ": "KJ",
    "У": "U", "Ў": "U", "Ф": "F", "Х": "KH", "Ц": "TS", "Ч": "CH", "Џ": "DZH", "Ш": "SH",
    "Щ": "SHCH", "Ъ": "", "Ы": "Y", "Ь": "", "Э": "E", "Ю": "YU", "Я": "YA",
    # Cyrillic lowercase
    "а": "A", "б": "B", "в": "V", "г": "G", "ґ": "G", "д": "D", "ђ": "DJ", "ѓ": "GJ",
    "е": "E", "ё": "E", "є": "YE", "ж": "ZH", "з": "Z", "ѕ": "DZ", "и": "I", "і": "I",
    "ї": "YI", "й": "Y", "ј": "J", "к": "K", "л": "L", "љ": "LJ", "м": "M", "н": "N",
    "њ": "NJ", "о": "O", "п": "P", "р": "R", "с": "S", "т": "T", "ћ": "C", "ќ": "KJ",
    "у": "U", "ў": "U", "ф": "F", "х": "KH", "ц": "TS", "ч": "CH", "џ": "DZH", "ш": "SH",
    "щ": "SHCH", "ъ": "", "ы": "Y", "ь": "", "э": "E", "ю": "YU", "я": "YA",
    # Greek uppercase
    "Α": "A", "Β": "V", "Γ": "G", "Δ": "D", "Ε": "E", "Ζ": "Z", "Η": "I", "Θ": "TH",
    "Ι": "I", "Κ": "K", "Λ": "L", "Μ": "M", "Ν": "N", "Ξ": "X", "Ο": "O", "Π": "P",
    "Ρ": "R", "Σ": "S", "Τ": "T", "Υ": "Y", "Φ": "F", "Χ": "CH", "Ψ": "PS", "Ω": "O",
    # Greek lowercase
    "α": "A", "β": "V", "γ": "G", "δ": "D", "ε": "E", "ζ": "Z", "η": "I", "θ": "TH",
    "ι": "I", "κ": "K", "λ": "L", "μ": "M", "ν": "N", "ξ": "X", "ο": "O", "π": "P",
    "ρ": "R", "σ": "S", "ς": "S", "τ": "T", "υ": "Y", "φ": "F", "χ": "CH", "ψ": "PS",
    "ω": "O",
}


def normalize_to_canonical_unicode(text: Optional[str]) -> str:
    """Normalize whitespace and apply canonical NFC Unicode representation."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", " ".join(text.split()))


def fold_to_ascii_key(text: Optional[str]) -> str:
    """Deterministic ASCII key folding for normalized_address_key and building_key.

    1. Explicit ligature replacements (ß -> SS, æ -> AE, etc.).
    2. Cyrillic and Greek character transliteration to deterministic ASCII.
    3. NFKD decomposition to separate base characters from combining marks.
    4. Filter non-spacing combining marks (category != 'Mn').
    5. Second-pass transliteration for decomposed base characters.
    6. Encode to ASCII, decode to uppercase string.
    7. Clean redundant whitespace.
    """
    if not text:
        return ""

    folded = text
    for lig, replacement in LIGATURE_MAP.items():
        if lig in folded:
            folded = folded.replace(lig, replacement)

    # First pass: transliterate direct Cyrillic and Greek characters
    chars = [CYRILLIC_GREEK_MAP.get(ch, ch) for ch in folded]
    folded = "".join(chars)

    # NFKD decomposition separates accents from letters
    decomposed = unicodedata.normalize("NFKD", folded)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")

    # Second pass: transliterate any base letters exposed after accent decomposition
    chars2 = [CYRILLIC_GREEK_MAP.get(ch, ch) for ch in stripped]
    stripped = "".join(chars2)

    ascii_clean = stripped.encode("ascii", "ignore").decode("ascii").upper()
    return " ".join(ascii_clean.split())
