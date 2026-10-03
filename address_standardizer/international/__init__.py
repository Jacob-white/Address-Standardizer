"""Universal International Address Parsing and Normalization Subsystem."""

from address_standardizer.international.base import (
    CountryGrammar,
    CountryGrammarRegistry,
    ParsedAddressComponents,
    UniversalInternationalGrammar,
    split_intl_secondary_unit,
)
from address_standardizer.international.canada import (
    CanadaGrammar,
    is_valid_canadian_postal_code,
)
from address_standardizer.international.diacritics import (
    LIGATURE_MAP,
    fold_to_ascii_key,
    normalize_to_canonical_unicode,
)
from address_standardizer.international.germanic import (
    GermanicGrammar,
    is_valid_dutch_postcode,
)
from address_standardizer.international.offshore import OffshoreGrammar
from address_standardizer.international.romance import RomanceGrammar
from address_standardizer.international.uk import (
    UKGrammar,
    is_valid_uk_postcode,
)


def register_default_grammars() -> None:
    """Register all standard international localized grammars into CountryGrammarRegistry."""
    CountryGrammarRegistry.register(UKGrammar())
    CountryGrammarRegistry.register(CanadaGrammar())
    CountryGrammarRegistry.register(GermanicGrammar())
    CountryGrammarRegistry.register(RomanceGrammar())
    CountryGrammarRegistry.register(OffshoreGrammar())


# Initialize default registry upon module import
register_default_grammars()

__all__ = [
    "CountryGrammar",
    "CountryGrammarRegistry",
    "ParsedAddressComponents",
    "UniversalInternationalGrammar",
    "split_intl_secondary_unit",
    "UKGrammar",
    "is_valid_uk_postcode",
    "CanadaGrammar",
    "is_valid_canadian_postal_code",
    "GermanicGrammar",
    "is_valid_dutch_postcode",
    "RomanceGrammar",
    "OffshoreGrammar",
    "LIGATURE_MAP",
    "fold_to_ascii_key",
    "normalize_to_canonical_unicode",
    "register_default_grammars",
]
