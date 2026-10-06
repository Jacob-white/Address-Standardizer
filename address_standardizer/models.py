"""Data structures for standardized address representations."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass(slots=True)
class SpatialResolutionResult:
    """Standardized geographic coordinate resolution result conforming to Blueprint Section 3.4."""
    latitude: float
    longitude: float
    precision: str  # CONFIRMED_ROOFTOP, RANGE_INTERPOLATED, POSTAL_CENTROID, MUNICIPAL_CENTROID, UNRESOLVED
    accuracy_radius_meters: float
    stage: int  # 1..4 (0 if UNRESOLVED)
    source: str
    h3_res10: str
    parcel_id: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "precision": self.precision,
            "accuracy_radius_meters": self.accuracy_radius_meters,
            "stage": self.stage,
            "source": self.source,
            "h3_res10": self.h3_res10,
            "parcel_id": self.parcel_id,
            "execution_time_ms": self.execution_time_ms,
            "metadata": dict(self.metadata),
        }



class AddressStatus:
    STANDARDIZED = "standardized"
    PENDING = "pending"
    PARSE_FAILED = "parse_failed"
    MANUAL_OVERRIDE = "manual_override"
    LOCALITY_ONLY = "locality_only"
    CITY_LEVEL = "city_level"


class LocalityOnlyStatus(str):
    """String status representing locality-only / city-level standardization."""

    def __eq__(self, other):
        if isinstance(other, str):
            o = other.lower()
            if o in ("locality_only", "city_level"):
                return True
        return super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash("locality_only")


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
    dependent_locality: Optional[str] = None
    building_name: Optional[str] = None
    rooftop_address: Optional[str] = None

    def __post_init__(self):
        if getattr(self, "rooftop_address", None) is None:
            if self.is_private_residence or self.address_status in ("locality_only", "city_level", "parse_failed"):
                self.rooftop_address = None
            else:
                from address_standardizer._patterns import clean_rooftop_address
                self.rooftop_address = clean_rooftop_address(self.street1)
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
        if not hasattr(self, "_spatial_result"):
            self._spatial_result: Optional[SpatialResolutionResult] = None
        if not hasattr(self, "_country_iso3"):
            self._country_iso3: str = getattr(self, "country", "USA") or "USA"
        if not hasattr(self, "_is_locality_only"):
            self._is_locality_only: bool = self.address_status in ("locality_only", "city_level")

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

    @property
    def spatial_result(self) -> Optional[SpatialResolutionResult]:
        return getattr(self, "_spatial_result", None)

    @spatial_result.setter
    def spatial_result(self, value: Optional[SpatialResolutionResult]):
        self._spatial_result = value

    @property
    def country_iso3(self) -> str:
        return getattr(self, "_country_iso3", getattr(self, "country", "USA") or "USA")

    @country_iso3.setter
    def country_iso3(self, value: str):
        self._country_iso3 = value

    @property
    def is_locality_only(self) -> bool:
        return self.address_status in ("locality_only", "city_level") or getattr(self, "_is_locality_only", False)

    @is_locality_only.setter
    def is_locality_only(self, value: bool):
        self._is_locality_only = bool(value)

    @property
    def is_city_level(self) -> bool:
        return self.is_locality_only

    @is_city_level.setter
    def is_city_level(self, value: bool):
        self._is_locality_only = bool(value)

    @property
    def full_rooftop_address(self) -> Optional[str]:
        """Single-line formatted rooftop address (excludes secondary units like suite, apt, fl)."""
        if not self.rooftop_address:
            return None
        parts = [self.rooftop_address]
        if self.city:
            parts.append(self.city)
        if self.state and self.postal_code:
            parts.append(f"{self.state} {self.postal_code}")
        elif self.state:
            parts.append(self.state)
        elif self.postal_code:
            parts.append(self.postal_code)
        if self.country and self.country not in ("USA", "US"):
            parts.append(self.country)
        return ", ".join(parts)

    def as_dict(self, include_metadata: bool = False, include_rooftop: bool = False) -> Dict[str, Any]:
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
        if include_rooftop:
            d["rooftop_address"] = self.rooftop_address
            d["full_rooftop_address"] = self.full_rooftop_address
        if include_metadata:
            d["rooftop_address"] = self.rooftop_address
            d["full_rooftop_address"] = self.full_rooftop_address
            d["is_locality_only"] = self.is_locality_only
            d["is_city_level"] = self.is_city_level
            d["dependent_locality"] = self.dependent_locality
            d["building_name"] = self.building_name
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
            if self.spatial_result is not None:
                d["spatial_result"] = (
                    self.spatial_result.as_dict()
                    if hasattr(self.spatial_result, "as_dict")
                    else self.spatial_result
                )
            else:
                d["spatial_result"] = None
            d["country_iso3"] = self.country_iso3
        return d

    def as_extended_dict(self) -> Dict[str, Any]:
        """Returns comprehensive enterprise dictionary including all risk, confidence, and audit metadata."""
        return self.as_dict(include_metadata=True)

    def format_upu(
        self,
        recipient: Optional[str] = None,
        include_country_name: bool = True,
    ) -> str:
        """Render address in Universal Postal Union (UPU S42) envelope layout."""
        from address_standardizer.international.upu import format_upu_address

        return format_upu_address(
            self,
            recipient=recipient,
            include_country_name=include_country_name,
        )
