"""
Address Standardizer
====================
High-performance, zero-external-service address standardization and entity resolution engine.
Adheres to USPS Publication 28 and ISO-3166 standards.
"""

from address_standardizer.models import StandardizedAddress
from address_standardizer.standardizer import (
    standardize_address,
    generate_normalized_address_key,
    generate_building_key,
    is_registered_agent_hub_address,
    normalize_country_code,
    normalize_country,
    normalize_us_state,
    normalize_us_postal_code,
    get_state_from_zip3,
    num_to_ordinal,
    _split_international_secondary_unit,
)
from address_standardizer.phonetics import (
    compute_soundex,
    generate_phonetic_address_key,
)
from address_standardizer.geocoder import (
    CensusGeocoder,
    get_fallback_centroid,
)

__version__ = "1.0.0"

__all__ = [
    "StandardizedAddress",
    "standardize_address",
    "generate_normalized_address_key",
    "generate_building_key",
    "generate_phonetic_address_key",
    "compute_soundex",
    "is_registered_agent_hub_address",
    "normalize_country_code",
    "normalize_country",
    "normalize_us_state",
    "normalize_us_postal_code",
    "get_state_from_zip3",
    "num_to_ordinal",
    "_split_international_secondary_unit",
    "CensusGeocoder",
    "get_fallback_centroid",
    "__version__",
]
