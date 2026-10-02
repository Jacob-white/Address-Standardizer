"""Data structures for standardized address representations."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class StandardizedAddress:
    """Standardized representation of a physical or mailing address."""
    street1: str
    street2: str
    city: str
    state: str
    postal_code: str
    country: str
    normalized_address_key: Optional[str]
    address_status: str  # 'standardized', 'pending', 'parse_failed', 'manual_override'
    raw_street_address: str
    is_us: bool
    is_private_residence: bool = False
    building_key: Optional[str] = None
    phonetic_key: Optional[str] = None
    is_registered_agent_hub: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "street1": self.street1,
            "street2": self.street2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "normalized_address_key": self.normalized_address_key,
            "building_key": self.building_key,
            "phonetic_key": self.phonetic_key,
            "address_status": self.address_status,
            "raw_street_address": self.raw_street_address,
            "is_us": self.is_us,
            "is_private_residence": self.is_private_residence,
            "is_registered_agent_hub": self.is_registered_agent_hub,
        }
