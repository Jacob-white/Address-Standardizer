"""Input coercion and guard helpers shared by the standardization pipeline."""

import math
import re
from typing import Any

from address_standardizer._patterns import RE_PRIVATE_RESIDENCE

# No real address line is anywhere near this long; longer inputs would only feed quadratic regexes and parsers.
MAX_FIELD_LENGTH = 600

_PO_BOX_VARIANT = re.compile(
    r"(?<![A-Za-z0-9])(?:P\.?\s?O\.?\s?B(?:OX)?\.?|POST\s+OFFICE\s+BOX)\s*#?\s*(?=[A-Za-z]?\d+(?!\d|(?:ST|ND|RD|TH)\b))",
    re.IGNORECASE,
)


def coerce_text(value: Any) -> str:
    """Turn a caller-supplied value into text: None/NaN become empty, integral floats lose their '.0'."""
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        text = str(int(value)) if value.is_integer() else str(value)
    elif isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = str(value)
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:  # lone surrogates (e.g. from JSON "\ud800") cannot be stored or logged
        text = text.encode("utf-8", errors="replace").decode("utf-8")
    return text


def normalize_po_box_spelling(text: str) -> str:
    """'P.O. Box #5', 'P O Box 5', 'PO Box5', 'P.O.B. 5' and 'Post Office Box 5' all become 'PO BOX 5'."""
    return _PO_BOX_VARIANT.sub("PO BOX ", text)


_STRONG_PRIVACY_PHRASE = re.compile(
    r"\b(?:PRIVATE\s+RESIDENCE|PRIVATE\s+ADDRESS|PERSONAL\s+RESIDENCE|RESIDENTIAL\s+ADDRESS|CONFIDENTIAL\s+(?:ADDRESS|RESIDENCE))\b", re.IGNORECASE
)


def is_privacy_placeholder(*fields: str) -> bool:
    """True when a street field marks a private residence.

    Explicit phrases ("Private Residence", "Personal Residence") count anywhere in the field. Weaker words
    ("Confidential", "Residence Only", "Residential") only count when they *are* the field (optionally followed by
    a comma-separated city), so "Confidential Data Inc" and "100 Residential Dr" are left alone.
    """
    for field in fields:
        if _STRONG_PRIVACY_PHRASE.search(field):
            return True
        first_part = field.split(",")[0].strip(" .-")
        if first_part and RE_PRIVATE_RESIDENCE.fullmatch(first_part):
            return True
    return False
