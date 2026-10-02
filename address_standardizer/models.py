"""Data structures for standardized address representations."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


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

    def __post_init__(self):
        if not hasattr(self, "_confidence_score"):
            self._confidence_score: Optional[float] = None
        if not hasattr(self, "_routing_tier"):
            self._routing_tier: Optional[str] = None
        if not hasattr(self, "_failure_reason_codes"):
            self._failure_reason_codes: Optional[List[str]] = None
        if not hasattr(self, "_audit_record"):
            self._audit_record: Optional[Any] = None
        if not hasattr(self, "_cascade_result"):
            self._cascade_result: Optional[Any] = None
        if not hasattr(self, "_rdi"):
            self._rdi: str = "Unknown"
        if not hasattr(self, "_cmra"):
            self._cmra: bool = False
        if not hasattr(self, "_vacant"):
            self._vacant: bool = False
        if not hasattr(self, "_dpv_footnotes"):
            self._dpv_footnotes: Optional[List[str]] = None
        if not hasattr(self, "_corporate_risk_score"):
            self._corporate_risk_score: float = 0.0
        if not hasattr(self, "_corporate_risk_flags"):
            self._corporate_risk_flags: Optional[List[str]] = None

    @property
    def confidence_score(self) -> Optional[float]:
        return getattr(self, "_confidence_score", None)

    @confidence_score.setter
    def confidence_score(self, value: Optional[float]):
        self._confidence_score = value

    @property
    def routing_tier(self) -> Optional[str]:
        return getattr(self, "_routing_tier", None)

    @routing_tier.setter
    def routing_tier(self, value: Optional[str]):
        self._routing_tier = value

    @property
    def failure_reason_codes(self) -> List[str]:
        val = getattr(self, "_failure_reason_codes", None)
        return list(val) if val is not None else []

    @failure_reason_codes.setter
    def failure_reason_codes(self, value: List[str]):
        self._failure_reason_codes = list(value)

    @property
    def audit_record(self) -> Optional[Any]:
        return getattr(self, "_audit_record", None)

    @audit_record.setter
    def audit_record(self, value: Optional[Any]):
        self._audit_record = value

    @property
    def cascade_result(self) -> Optional[Any]:
        return getattr(self, "_cascade_result", None)

    @cascade_result.setter
    def cascade_result(self, value: Optional[Any]):
        self._cascade_result = value

    @property
    def rdi(self) -> str:
        return getattr(self, "_rdi", "Unknown")

    @rdi.setter
    def rdi(self, value: str):
        self._rdi = value

    @property
    def cmra(self) -> bool:
        return getattr(self, "_cmra", False)

    @cmra.setter
    def cmra(self, value: bool):
        self._cmra = bool(value)

    @property
    def is_cmra(self) -> bool:
        return self.cmra

    @is_cmra.setter
    def is_cmra(self, value: bool):
        self.cmra = value

    @property
    def vacant(self) -> bool:
        return getattr(self, "_vacant", False)

    @vacant.setter
    def vacant(self, value: bool):
        self._vacant = bool(value)

    @property
    def is_vacant(self) -> bool:
        return self.vacant

    @is_vacant.setter
    def is_vacant(self, value: bool):
        self.vacant = value

    @property
    def dpv_footnotes(self) -> List[str]:
        val = getattr(self, "_dpv_footnotes", None)
        return list(val) if val is not None else []

    @dpv_footnotes.setter
    def dpv_footnotes(self, value: List[str]):
        self._dpv_footnotes = list(value)

    @property
    def corporate_risk_score(self) -> float:
        return getattr(self, "_corporate_risk_score", 0.0)

    @corporate_risk_score.setter
    def corporate_risk_score(self, value: float):
        self._corporate_risk_score = float(value)

    @property
    def corporate_risk_flags(self) -> List[str]:
        val = getattr(self, "_corporate_risk_flags", None)
        return list(val) if val is not None else []

    @corporate_risk_flags.setter
    def corporate_risk_flags(self, value: List[str]):
        self._corporate_risk_flags = list(value)

    def as_dict(self, include_metadata: bool = False) -> Dict[str, Any]:
        d = {
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
        if include_metadata:
            d["confidence_score"] = self.confidence_score
            d["routing_tier"] = self.routing_tier
            d["failure_reason_codes"] = self.failure_reason_codes
            d["rdi"] = self.rdi
            d["cmra"] = self.cmra
            d["is_cmra"] = self.is_cmra
            d["vacant"] = self.vacant
            d["is_vacant"] = self.is_vacant
            d["dpv_footnotes"] = self.dpv_footnotes
            d["corporate_risk_score"] = self.corporate_risk_score
            d["corporate_risk_flags"] = self.corporate_risk_flags
            if self.audit_record is not None:
                d["audit_id"] = getattr(self.audit_record, "audit_id", None)
            if self.cascade_result is not None:
                d["cascade"] = (
                    self.cascade_result.as_dict()
                    if hasattr(self.cascade_result, "as_dict")
                    else self.cascade_result
                )
        return d

    def as_extended_dict(self) -> Dict[str, Any]:
        """Returns comprehensive enterprise dictionary including all risk, confidence, and audit metadata."""
        return self.as_dict(include_metadata=True)
