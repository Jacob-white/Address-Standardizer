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
    VerificationCascade,
    CascadeResult,
    CascadePrecision,
    resolve_verification_cascade,
)
from address_standardizer.batch import (
    chunk_generator,
    process_chunk,
    stream_standardize_csv,
)
from address_standardizer.confidence import (
    RoutingTier,
    ConfidenceResult,
    ConfidenceScorer,
    compute_confidence_score,
)
from address_standardizer.audit import (
    StewardshipAuditRecord,
    StewardshipAuditLedger,
    AUDIT_LEDGER_DDL,
    get_audit_ledger,
    ActionType,
    ReviewStatus,
)
from address_standardizer.cache import (
    MultiTierCache,
    LRUCache,
    SQLiteCache,
    get_default_cache,
    configure_cache,
    clear_cache,
    get_cache_stats,
    make_cache_key,
)
from address_standardizer.delivery import (
    DPVFootnote,
    RDI,
    DeliveryIntelligenceResult,
    evaluate_delivery_intelligence,
)
from address_standardizer.fuzzy import (
    damerau_levenshtein_distance,
    heal_street_suffix,
    heal_city_token,
    heal_street_name,
    heal_postal_code_transposition,
    heal_street_number_transposition,
    PROTECTED_STREET_WORDS,
)
from address_standardizer.registry import (
    RegistryCategory,
    CorporateRiskFlag,
    CorporateRegistryEntry,
    CURATED_CORPORATE_REGISTRY,
    lookup_corporate_registry,
    can_safely_merge_corporate_entities,
    evaluate_corporate_risk,
)
from address_standardizer.autocomplete import (
    AutocompleteSuggestion,
    AutocompleteEngine,
    autocomplete_address,
)
from address_standardizer.offline_index import (
    RooftopRecord,
    ParcelValidationResult,
    OfflineReferenceIndex,
    get_default_offline_index,
    resolve_offline_coordinates,
    validate_parcel_offline,
)

__version__ = "2.1.0"

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
    "chunk_generator",
    "process_chunk",
    "stream_standardize_csv",
    # Confidence scoring
    "RoutingTier",
    "ConfidenceResult",
    "ConfidenceScorer",
    "compute_confidence_score",
    # Audit ledger
    "StewardshipAuditRecord",
    "StewardshipAuditLedger",
    "AUDIT_LEDGER_DDL",
    "get_audit_ledger",
    "ActionType",
    "ReviewStatus",
    # Caching
    "MultiTierCache",
    "LRUCache",
    "SQLiteCache",
    "get_default_cache",
    "configure_cache",
    "clear_cache",
    "get_cache_stats",
    "make_cache_key",
    # Verification cascade
    "CascadePrecision",
    "CascadeResult",
    "VerificationCascade",
    "resolve_verification_cascade",
    # Phase 1: Delivery Intelligence
    "DPVFootnote",
    "RDI",
    "DeliveryIntelligenceResult",
    "evaluate_delivery_intelligence",
    # Phase 2: Typo Recovery & Fuzzy Correction
    "damerau_levenshtein_distance",
    "heal_street_suffix",
    "heal_city_token",
    "heal_street_name",
    "heal_postal_code_transposition",
    "heal_street_number_transposition",
    "PROTECTED_STREET_WORDS",
    # Phase 3: Corporate Registry & Transparency
    "RegistryCategory",
    "CorporateRiskFlag",
    "CorporateRegistryEntry",
    "CURATED_CORPORATE_REGISTRY",
    "lookup_corporate_registry",
    "can_safely_merge_corporate_entities",
    "evaluate_corporate_risk",
    # Phase 4: Autocomplete Engine
    "AutocompleteSuggestion",
    "AutocompleteEngine",
    "autocomplete_address",
    # Phase 5: Offline Rooftop Reference Index
    "RooftopRecord",
    "ParcelValidationResult",
    "OfflineReferenceIndex",
    "get_default_offline_index",
    "resolve_offline_coordinates",
    "validate_parcel_offline",
    "__version__",
]
