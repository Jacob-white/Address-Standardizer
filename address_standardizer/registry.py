"""
Corporate Transparency (BOI) Registry & Formation Hub Intelligence.
===================================================================
Comprehensive curated registry of commercial registered agents, mail drops,
virtual office providers, and offshore secrecy jurisdictions.

Enforces FinCEN Corporate Transparency Act (CTA), Beneficial Ownership Information (BOI),
and KYC/AML entity co-location isolation invariants.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from address_standardizer.tables import US_STATES


class RegistryCategory:
    COMMERCIAL_REGISTERED_AGENT = "COMMERCIAL_REGISTERED_AGENT"
    FORMATION_AGENT = "FORMATION_AGENT"
    VIRTUAL_OFFICE = "VIRTUAL_OFFICE"
    MAIL_DROP_CMRA = "MAIL_DROP_CMRA"
    OFFSHORE_SECRECY = "OFFSHORE_SECRECY"


class CorporateRiskFlag:
    RISK_CRA_CO_LOCATION = "RISK_CRA_CO_LOCATION"
    RISK_VIRTUAL_OFFICE = "RISK_VIRTUAL_OFFICE"
    RISK_CMRA_MAIL_DROP = "RISK_CMRA_MAIL_DROP"
    RISK_OFFSHORE_SECRECY_HUB = "RISK_OFFSHORE_SECRECY_HUB"
    RISK_MISSING_SECONDARY_AT_HUB = "RISK_MISSING_SECONDARY_AT_HUB"
    RISK_DISGUISED_PMB = "RISK_DISGUISED_PMB"
    RISK_RESIDENTIAL_COMMERCIAL = "RISK_RESIDENTIAL_COMMERCIAL"


@dataclass
class CorporateRegistryEntry:
    """Detailed metadata for a curated formation hub, registered agent, or virtual office."""
    provider_name: str
    category: str
    street_patterns: List[str]
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    base_risk_score: float = 0.85
    estimated_entities: int = 10000
    notes: str = ""
    aliases: List[str] = field(default_factory=list)
    requires_secondary_match: bool = False
    mandatory_unit_patterns: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "category": self.category,
            "street_patterns": list(self.street_patterns),
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "base_risk_score": self.base_risk_score,
            "estimated_entities": self.estimated_entities,
            "notes": self.notes,
            "aliases": list(self.aliases),
            "requires_secondary_match": self.requires_secondary_match,
            "mandatory_unit_patterns": list(self.mandatory_unit_patterns),
        }


# ---------------------------------------------------------------------------
# Master Curated Corporate Registry
# ---------------------------------------------------------------------------

CURATED_CORPORATE_REGISTRY: List[CorporateRegistryEntry] = [
    # 1. Corporation Trust Center (CT Corporation / Wolters Kluwer) - Premier DE Hub
    CorporateRegistryEntry(
        provider_name="Corporation Trust Center (CT Corporation)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["1209 N ORANGE", "1209 NORTH ORANGE"],
        city="WILMINGTON",
        state="DE",
        postal_code="19801",
        country="USA",
        base_risk_score=0.95,
        estimated_entities=300000,
        notes="Primary US registered agent corporate secrecy hub.",
        aliases=["CT CORPORATION", "CORPORATION TRUST CO"],
    ),
    # 2. National Registered Agents, Inc. (NRAI / CT Corp) - Dover DE
    CorporateRegistryEntry(
        provider_name="National Registered Agents, Inc. (NRAI)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["160 GREENTREE"],
        city="DOVER",
        state="DE",
        postal_code="19904",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=50000,
        notes="Major Delaware commercial formation hub.",
    ),
    # 3. Corporation Service Company (CSC Global HQ) - Wilmington DE
    CorporateRegistryEntry(
        provider_name="Corporation Service Company (CSC Global HQ)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["251 LITTLE FALLS"],
        city="WILMINGTON",
        state="DE",
        postal_code="19808",
        country="USA",
        base_risk_score=0.90,
        estimated_entities=200000,
        notes="Global headquarters of Corporation Service Company.",
        aliases=["CSC", "CSC GLOBAL"],
    ),
    # 4. Corporation Service Company (CSC Legacy) - Wilmington DE
    CorporateRegistryEntry(
        provider_name="Corporation Service Company (CSC Centerville)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["2711 CENTERVILLE"],
        city="WILMINGTON",
        state="DE",
        postal_code="19808",
        country="USA",
        base_risk_score=0.90,
        estimated_entities=150000,
        notes="CSC Centerville Road corporate office hub.",
        aliases=["CSC"],
    ),
    # 5. Cogency Global (formerly National Corporate Research) - Dover DE
    CorporateRegistryEntry(
        provider_name="Cogency Global",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["850 NEW BURTON"],
        city="DOVER",
        state="DE",
        postal_code="19904",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=40000,
        notes="Major commercial registered agent hub.",
    ),
    # 6. The Corporation Trust Company - West Trenton NJ
    CorporateRegistryEntry(
        provider_name="The Corporation Trust Company (NJ)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["820 BEAR TAVERN"],
        city="TRENTON",
        state="NJ",
        postal_code="08628",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=25000,
        notes="New Jersey corporate filing and registered agent hub.",
    ),
    # 7. Harvard Business Services - Lewes DE
    CorporateRegistryEntry(
        provider_name="Harvard Business Services",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["16192 COASTAL"],
        city="LEWES",
        state="DE",
        postal_code="19958",
        country="USA",
        base_risk_score=0.90,
        estimated_entities=250000,
        notes="High-volume online Delaware incorporation mill and registered agent.",
    ),
    # 8. Registered Agents Inc. - Sheridan WY
    CorporateRegistryEntry(
        provider_name="Registered Agents Inc. (Wyoming Privacy Hub)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["30 N GOULD", "30 NORTH GOULD"],
        city="SHERIDAN",
        state="WY",
        postal_code="82801",
        country="USA",
        base_risk_score=0.95,
        estimated_entities=100000,
        notes="Premier Wyoming privacy formation hub hosting crypto, LLCs, and shells.",
    ),
    # 9. Registered Agents Inc. - Dover DE
    CorporateRegistryEntry(
        provider_name="Registered Agents Inc. (Delaware)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["3500 S DUPONT", "3500 SOUTH DUPONT"],
        city="DOVER",
        state="DE",
        postal_code="19901",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=60000,
        notes="High-volume Delaware registered agent hub.",
    ),
    # 10. Incorp Services - Las Vegas NV
    CorporateRegistryEntry(
        provider_name="Incorp Services",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["3773 HOWARD HUGHES"],
        city="LAS VEGAS",
        state="NV",
        postal_code="89169",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=35000,
        notes="Nevada corporate formation and registered agent center.",
    ),
    # 11. Northwest Registered Agent - Spokane WA
    CorporateRegistryEntry(
        provider_name="Northwest Registered Agent (HQ)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["522 W RIVERSIDE", "522 WEST RIVERSIDE"],
        city="SPOKANE",
        state="WA",
        postal_code="99201",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=75000,
        notes="Northwest Registered Agent national headquarters.",
    ),
    # 12. Northwest Registered Agent - St Petersburg FL
    CorporateRegistryEntry(
        provider_name="Northwest Registered Agent (Florida)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["7901 4TH ST N", "7901 4TH STREET N"],
        city="ST PETERSBURG",
        state="FL",
        postal_code="33702",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=45000,
        notes="Florida high-volume corporate registered agent hub.",
    ),
    # 13. Northwest Registered Agent - Wilmington DE
    CorporateRegistryEntry(
        provider_name="Northwest Registered Agent (Delaware)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["300 DELAWARE"],
        city="WILMINGTON",
        state="DE",
        postal_code="19801",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=40000,
        notes="Delaware corporate office hub.",
    ),
    # 14. CT Corporation - New York NY (Fosun Plaza / 28 Liberty)
    CorporateRegistryEntry(
        provider_name="CT Corporation (New York)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["28 LIBERTY"],
        city="NEW YORK",
        state="NY",
        postal_code="10005",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=60000,
        notes="Major commercial registered agent hub in Manhattan financial district.",
        requires_secondary_match=True,
        mandatory_unit_patterns=["FL 42", "STE 4200", "42ND FL", "42 FL", "FLOOR 42", "SUITE 4200", "#4200"],
    ),
    # 15. CT Corporation - Chicago IL
    CorporateRegistryEntry(
        provider_name="CT Corporation (Illinois)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["208 S LASALLE", "208 SOUTH LASALLE"],
        city="CHICAGO",
        state="IL",
        postal_code="60604",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=40000,
        notes="Illinois commercial registered agent hub.",
    ),
    # 16. CT Corporation - Plantation FL
    CorporateRegistryEntry(
        provider_name="CT Corporation (Florida)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["1200 S PINE ISLAND", "1200 SOUTH PINE ISLAND"],
        city="PLANTATION",
        state="FL",
        postal_code="33324",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=50000,
        notes="Florida commercial registered agent hub.",
    ),
    # 17. CT Corporation - Glendale CA
    CorporateRegistryEntry(
        provider_name="CT Corporation (California)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["330 N BRAND", "330 NORTH BRAND"],
        city="GLENDALE",
        state="CA",
        postal_code="91203",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=45000,
        notes="California commercial registered agent hub.",
    ),
    # 18. CSC Global - Albany NY
    CorporateRegistryEntry(
        provider_name="Corporation Service Company (Albany NY)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["80 STATE"],
        city="ALBANY",
        state="NY",
        postal_code="12207",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=70000,
        notes="CSC New York state capital corporate hub.",
    ),
    # 19. Registered Agents Inc. - Albany NY
    CorporateRegistryEntry(
        provider_name="Registered Agents Inc. (Albany NY)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["90 STATE"],
        city="ALBANY",
        state="NY",
        postal_code="12207",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=50000,
        notes="Registered Agents Inc. New York corporate hub.",
    ),
    # 20. Registered Agents Inc. - Buffalo WY
    CorporateRegistryEntry(
        provider_name="Registered Agents Inc. (Buffalo WY)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["412 N MAIN", "412 NORTH MAIN"],
        city="BUFFALO",
        state="WY",
        postal_code="82834",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=25000,
        notes="Wyoming secondary registered agent and formation hub.",
    ),
    # 21. LegalZoom / Business Filings Inc. - Glendale CA
    CorporateRegistryEntry(
        provider_name="LegalZoom (Corporate Headquarters)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["101 N BRAND", "101 NORTH BRAND"],
        city="GLENDALE",
        state="CA",
        postal_code="91203",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=150000,
        notes="LegalZoom headquarters and registered agent center.",
    ),
    # 22. LegalZoom - Austin TX
    CorporateRegistryEntry(
        provider_name="LegalZoom / Incorp (Austin TX)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["9900 SPECTRUM"],
        city="AUSTIN",
        state="TX",
        postal_code="78717",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=80000,
        notes="Texas corporate formation and registered agent center.",
    ),
    # 23. Cogency Global - New York NY
    CorporateRegistryEntry(
        provider_name="Cogency Global (New York HQ)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["10 E 40TH", "10 EAST 40TH"],
        city="NEW YORK",
        state="NY",
        postal_code="10016",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=30000,
        notes="Manhattan registered agent headquarters.",
    ),
    # 24. NRAI - Columbus OH
    CorporateRegistryEntry(
        provider_name="National Registered Agents (Ohio)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["4400 EASTON COMMONS"],
        city="COLUMBUS",
        state="OH",
        postal_code="43219",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=25000,
        notes="Ohio commercial registered agent center.",
    ),
    # 25. NRAI - Dallas TX
    CorporateRegistryEntry(
        provider_name="National Registered Agents (Texas)",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["1999 BRYAN"],
        city="DALLAS",
        state="TX",
        postal_code="75201",
        country="USA",
        base_risk_score=0.80,
        estimated_entities=35000,
        notes="Texas commercial registered agent hub.",
    ),
    # 26. Regus Virtual Office - 245 Park Ave NY
    CorporateRegistryEntry(
        provider_name="Regus / IWG (245 Park Ave)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["245 PARK"],
        city="NEW YORK",
        state="NY",
        postal_code="10167",
        country="USA",
        base_risk_score=0.70,
        estimated_entities=15000,
        notes="Commercial virtual office mail drop hosting thousands of shell businesses.",
        requires_secondary_match=True,
        mandatory_unit_patterns=["FL 39", "STE 3900", "39TH FL", "39 FL", "FLOOR 39", "SUITE 3900", "#3900"],
    ),
    # 27. Regus Virtual Office - 100 Park Ave NY
    CorporateRegistryEntry(
        provider_name="Regus / IWG (100 Park Ave)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["100 PARK"],
        city="NEW YORK",
        state="NY",
        postal_code="10017",
        country="USA",
        base_risk_score=0.70,
        estimated_entities=12000,
        notes="Commercial virtual office and corporate mail drop.",
        requires_secondary_match=True,
        mandatory_unit_patterns=["FL 16", "STE 1600", "16TH FL", "16 FL", "FLOOR 16", "SUITE 1600", "#1600"],
    ),
    # 28. Regus Virtual Office - 100 S Biscayne Blvd Miami FL
    CorporateRegistryEntry(
        provider_name="Regus Virtual Office (Miami Financial District)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["100 S BISCAYNE", "100 SOUTH BISCAYNE"],
        city="MIAMI",
        state="FL",
        postal_code="33131",
        country="USA",
        base_risk_score=0.75,
        estimated_entities=18000,
        notes="Downtown Miami virtual office hosting offshore and LATAM corporate entities.",
    ),
    # 29. Regus Virtual Office - 101 California St San Francisco CA
    CorporateRegistryEntry(
        provider_name="Regus / IWG (101 California St)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["101 CALIFORNIA"],
        city="SAN FRANCISCO",
        state="CA",
        postal_code="94111",
        country="USA",
        base_risk_score=0.70,
        estimated_entities=10000,
        notes="Financial district corporate virtual office.",
        requires_secondary_match=True,
        mandatory_unit_patterns=["FL 27", "STE 2700", "27TH FL", "27 FL", "FLOOR 27", "SUITE 2700", "#2700"],
    ),
    # 30. Regus Virtual Office - 200 S Wacker Dr Chicago IL
    CorporateRegistryEntry(
        provider_name="Regus / IWG (200 S Wacker)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["200 S WACKER", "200 SOUTH WACKER"],
        city="CHICAGO",
        state="IL",
        postal_code="60606",
        country="USA",
        base_risk_score=0.70,
        estimated_entities=12000,
        notes="Chicago financial center virtual office.",
        requires_secondary_match=True,
        mandatory_unit_patterns=["FL 31", "STE 3100", "31ST FL", "31 FL", "FLOOR 31", "SUITE 3100", "#3100"],
    ),
    # 31. WeWork Corporate Mail Drop - 115 W 18th St NY
    CorporateRegistryEntry(
        provider_name="WeWork Corporate Mail Drop (Chelsea)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["115 W 18TH", "115 WEST 18TH"],
        city="NEW YORK",
        state="NY",
        postal_code="10011",
        country="USA",
        base_risk_score=0.65,
        estimated_entities=8000,
        notes="WeWork corporate business address and mail handling center.",
    ),
    # 32. WeWork Corporate Mail Drop - 500 7th Ave NY
    CorporateRegistryEntry(
        provider_name="WeWork Corporate Mail Drop (Midtown)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["500 7TH", "500 SEVENTH"],
        city="NEW YORK",
        state="NY",
        postal_code="10018",
        country="USA",
        base_risk_score=0.65,
        estimated_entities=9000,
        notes="Multi-tenant commercial shared workspace and corporate address.",
    ),
    # 33. WeWork Corporate Mail Drop - 600 California St SF
    CorporateRegistryEntry(
        provider_name="WeWork Corporate Mail Drop (San Francisco)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["600 CALIFORNIA"],
        city="SAN FRANCISCO",
        state="CA",
        postal_code="94108",
        country="USA",
        base_risk_score=0.65,
        estimated_entities=7500,
        notes="San Francisco financial hub mail forwarding facility.",
    ),
    # 34. DaVinci Virtual Office Solutions - 275 Madison Ave NY
    CorporateRegistryEntry(
        provider_name="DaVinci Virtual Offices (275 Madison Ave)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["275 MADISON"],
        city="NEW YORK",
        state="NY",
        postal_code="10016",
        country="USA",
        base_risk_score=0.75,
        estimated_entities=14000,
        notes="Dedicated virtual office mail drop and telephone answering provider.",
    ),
    # 35. Opus Virtual Offices - 777 Yamato Rd Boca Raton FL
    CorporateRegistryEntry(
        provider_name="Opus Virtual Offices (Headquarters)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["777 YAMATO"],
        city="BOCA RATON",
        state="FL",
        postal_code="33431",
        country="USA",
        base_risk_score=0.75,
        estimated_entities=16000,
        notes="National virtual office headquarters and corporate mail forwarder.",
    ),
    # 36. Alliance Virtual Offices - 1221 Brickell Ave Miami FL
    CorporateRegistryEntry(
        provider_name="Alliance Virtual Offices (Brickell)",
        category=RegistryCategory.VIRTUAL_OFFICE,
        street_patterns=["1221 BRICKELL"],
        city="MIAMI",
        state="FL",
        postal_code="33131",
        country="USA",
        base_risk_score=0.75,
        estimated_entities=11000,
        notes="International virtual office and business address solution.",
        requires_secondary_match=True,
        mandatory_unit_patterns=["FL 9", "STE 900", "9TH FL", "9 FL", "FLOOR 9", "SUITE 900", "#900"],
    ),
    # 37. Nevada Corporate Headquarters - Las Vegas NV
    CorporateRegistryEntry(
        provider_name="Nevada Corporate Headquarters",
        category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["4730 S FORT APACHE", "4730 SOUTH FORT APACHE"],
        city="LAS VEGAS",
        state="NV",
        postal_code="89147",
        country="USA",
        base_risk_score=0.85,
        estimated_entities=20000,
        notes="Nevada asset protection and incorporation service hub.",
    ),
    # 38. Ugland House - Grand Cayman (World's Most Famous Offshore Secrecy Hub)
    CorporateRegistryEntry(
        provider_name="Ugland House (Maples and Calder)",
        category=RegistryCategory.OFFSHORE_SECRECY,
        street_patterns=["UGLAND HOUSE", "SOUTH CHURCH ST", "PO BOX 309"],
        city="GEORGE TOWN",
        state="",
        postal_code="KY1-1104",
        country="CYM",
        base_risk_score=0.98,
        estimated_entities=18000,
        notes="Ugland House: Premier Cayman offshore hedge fund and shell company hub.",
        aliases=["MAPLES AND CALDER", "UGLAND"],
    ),
    # 39. Clifton House - Grand Cayman
    CorporateRegistryEntry(
        provider_name="Clifton House (Appleby)",
        category=RegistryCategory.OFFSHORE_SECRECY,
        street_patterns=["CLIFTON HOUSE", "75 FORT ST", "PO BOX 190"],
        city="GEORGE TOWN",
        state="",
        postal_code="KY1-1104",
        country="CYM",
        base_risk_score=0.95,
        estimated_entities=12000,
        notes="Appleby global offshore legal and corporate service hub.",
    ),
    # 40. 190 Elgin Ave - Grand Cayman (Walkers)
    CorporateRegistryEntry(
        provider_name="190 Elgin Avenue (Walkers)",
        category=RegistryCategory.OFFSHORE_SECRECY,
        street_patterns=["190 ELGIN"],
        city="GEORGE TOWN",
        state="",
        postal_code="KY1-9001",
        country="CYM",
        base_risk_score=0.95,
        estimated_entities=15000,
        notes="Walkers law firm offshore fund and corporate secrecy center.",
    ),
    # 41. Craigmuir Chambers - British Virgin Islands (Tortola)
    CorporateRegistryEntry(
        provider_name="Craigmuir Chambers (Harneys)",
        category=RegistryCategory.OFFSHORE_SECRECY,
        street_patterns=["CRAIGMUIR CHAMBERS", "PO BOX 71"],
        city="ROAD TOWN",
        state="",
        postal_code="VG1110",
        country="VGB",
        base_risk_score=0.98,
        estimated_entities=25000,
        notes="BVI Harneys offshore formation hub hosting tens of thousands of IBCs.",
    ),
    # 42. Wickhams Cay - British Virgin Islands (Tortola)
    CorporateRegistryEntry(
        provider_name="Wickhams Cay (Trident / Offshore Hub)",
        category=RegistryCategory.OFFSHORE_SECRECY,
        street_patterns=["WICKHAMS CAY", "TRIDENT CHAMBERS"],
        city="ROAD TOWN",
        state="",
        postal_code="VG1110",
        country="VGB",
        base_risk_score=0.98,
        estimated_entities=30000,
        notes="Major BVI commercial secrecy and registered agent hub.",
    ),
    # 43. Calle 50 / Mossack Fonseca - Panama City, Panama
    CorporateRegistryEntry(
        provider_name="Calle 50 Corporate Financial Center (Panama)",
        category=RegistryCategory.OFFSHORE_SECRECY,
        street_patterns=["CALLE 50", "EDIFICIO ARANGO ORILLAC"],
        city="PANAMA CITY",
        state="",
        postal_code="",
        country="PAN",
        base_risk_score=0.95,
        estimated_entities=20000,
        notes="Historic Panamanian secrecy and offshore corporate formation district.",
    ),
    CorporateRegistryEntry(
        provider_name="Earth Class Mail Digital Hub",
        category=RegistryCategory.MAIL_DROP_CMRA,
        street_patterns=["277 4TH AVE"],
        city="BROOKLYN",
        state="NY",
        postal_code="11215",
        base_risk_score=0.75,
        estimated_entities=15000,
        notes="High-volume commercial mail receiving agency and scanning service.",
    ),
    CorporateRegistryEntry(
        provider_name="iPostal1 / Anytime Mailbox Hub",
        category=RegistryCategory.MAIL_DROP_CMRA,
        street_patterns=["1321 UPLAND DR"],
        city="HOUSTON",
        state="TX",
        postal_code="77043",
        base_risk_score=0.75,
        estimated_entities=25000,
        notes="Nationwide virtual mailbox and re-mailing commercial facility.",
    ),
]


def _fold_ascii(s: str) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8").upper()


def lookup_corporate_registry(
    street1: str,
    street2: str = "",
    city: str = "",
    state: str = "",
    postal_code: str = "",
    country: str = "USA",
    raw_street: str = "",
) -> Optional[CorporateRegistryEntry]:
    """
    Looks up an address against the comprehensive curated corporate registry.
    Returns the matching CorporateRegistryEntry if found, else None.
    """
    combined_raw = f"{street1} {street2} {city} {state} {postal_code} {raw_street}"
    combined = _fold_ascii(combined_raw)
    norm_st = _fold_ascii(street1)
    norm_c = _fold_ascii(country)

    # Fast check for offshore secrecy keywords
    if norm_c in ("CYM", "CAYMAN ISLANDS", "VGB", "VIRGIN ISLANDS, BRITISH", "PAN", "PANAMA") or any(
        k in combined for k in ["CAYMAN", "TORTOLA", "UGLAND HOUSE", "ROAD TOWN", "CRAIGMUIR", "WICKHAMS CAY"]
    ):
        for entry in CURATED_CORPORATE_REGISTRY:
            if entry.category == RegistryCategory.OFFSHORE_SECRECY:
                if any(_fold_ascii(pat) in combined for pat in entry.street_patterns):
                    return entry

    # Domestic US check
    st_clean = (state or "").strip().upper()
    st_norm = US_STATES.get(st_clean, st_clean)
    city_clean = _fold_ascii(city)
    zip_digits = re.sub(r"[^\d]", "", postal_code)

    for entry in CURATED_CORPORATE_REGISTRY:
        if entry.category == RegistryCategory.OFFSHORE_SECRECY:
            continue

        # If state was explicitly provided and does not match entry.state, skip
        if st_norm and entry.state and st_norm != entry.state:
            continue

        # Match street pattern
        matched_street = any(
            _fold_ascii(pat) in combined or _fold_ascii(pat) in norm_st
            for pat in entry.street_patterns
        )
        if not matched_street:
            continue

        # Match secondary unit if entry requires it
        if entry.requires_secondary_match:
            sec_candidates = f" {street2} {street1} {raw_street} ".upper()
            sec_candidates_clean = re.sub(r"[,\.#;:]+", " ", sec_candidates)
            matched_sec = False
            for pat in entry.mandatory_unit_patterns:
                pat_upper = pat.upper()
                esc_pat = re.escape(pat_upper)
                pattern_re = (
                    r"(?:\b|#)" + esc_pat.lstrip("#") + r"\b"
                    if pat_upper.startswith("#")
                    else r"\b" + esc_pat + r"\b"
                )
                if re.search(pattern_re, sec_candidates) or re.search(pattern_re, sec_candidates_clean):
                    matched_sec = True
                    break
            if not matched_sec:
                continue

        # Match jurisdiction (state, city, or postal prefix)
        state_match = False
        if entry.state:
            if st_norm == entry.state:
                state_match = True
            elif not st_norm:
                state_match = bool(re.search(r"\b" + re.escape(entry.state) + r"\b", combined))

        city_match = False
        if entry.city:
            entry_city_norm = _fold_ascii(entry.city)
            if city_clean and city_clean == entry_city_norm:
                city_match = True
            elif not city_clean:
                city_match = bool(re.search(r"\b" + re.escape(entry_city_norm) + r"\b", combined))

        zip_match = False
        if entry.postal_code:
            if zip_digits and zip_digits.startswith(entry.postal_code[:3]):
                zip_match = True
            elif not zip_digits:
                zip_match = entry.postal_code in combined

        if state_match or city_match or zip_match:
            return entry

    return None



def is_registered_agent_hub_address(
    street1: str,
    street2: str = "",
    city: str = "",
    state: str = "",
    postal_code: str = "",
    country: str = "USA",
    raw_street: str = "",
) -> bool:
    """
    Detects whether an address corresponds to a known corporate service or formation hub.
    Only COMMERCIAL_REGISTERED_AGENT, FORMATION_AGENT, and OFFSHORE_SECRECY set is_registered_agent_hub=True.
    Virtual offices and CMRA mail drops populate corporate_risk_score and flags, but do not set is_registered_agent_hub=True.
    """
    entry = lookup_corporate_registry(
        street1=street1,
        street2=street2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        raw_street=raw_street,
    )
    if entry is None:
        return False
    return entry.category in (
        RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        RegistryCategory.FORMATION_AGENT,
        RegistryCategory.OFFSHORE_SECRECY,
    )


def can_safely_merge_corporate_entities(addr1: Any, addr2: Any) -> Tuple[bool, str]:
    """
    Enforces the critical Enterprise Entity Resolution Invariant (CRA Co-Location Rule):
    If two business entities share an identical building_key, but the location is a
    commercial registered agent hub, MDM systems MUST NEVER automatically merge them.
    """
    # 0. Empty street isolation check
    s1_1 = addr1.get("street1") if isinstance(addr1, dict) else getattr(addr1, "street1", None)
    s1_2 = addr2.get("street1") if isinstance(addr2, dict) else getattr(addr2, "street1", None)
    if not s1_1 or not str(s1_1).strip() or not s1_2 or not str(s1_2).strip():
        return False, "EMPTY_STREET_ISOLATION: Cannot safely merge entities when an address lacks a valid street line."

    # 1. Private residence isolation check
    is_priv1 = addr1.get("is_private_residence", False) if isinstance(addr1, dict) else getattr(addr1, "is_private_residence", False)
    is_priv2 = addr2.get("is_private_residence", False) if isinstance(addr2, dict) else getattr(addr2, "is_private_residence", False)
    b1 = (addr1.get("building_key") if isinstance(addr1, dict) else getattr(addr1, "building_key", "")) or ""
    b2 = (addr2.get("building_key") if isinstance(addr2, dict) else getattr(addr2, "building_key", "")) or ""
    k1 = (addr1.get("normalized_address_key") if isinstance(addr1, dict) else getattr(addr1, "normalized_address_key", "")) or ""
    k2 = (addr2.get("normalized_address_key") if isinstance(addr2, dict) else getattr(addr2, "normalized_address_key", "")) or ""
    if (
        is_priv1
        or is_priv2
        or b1.startswith("PRIVATE RESIDENCE||")
        or b2.startswith("PRIVATE RESIDENCE||")
        or k1.startswith("PRIVATE RESIDENCE||")
        or k2.startswith("PRIVATE RESIDENCE||")
        or str(s1_1).strip().upper() == "PRIVATE RESIDENCE"
        or str(s1_2).strip().upper() == "PRIVATE RESIDENCE"
    ):
        return (
            False,
            "PRIVATE_RESIDENCE_ISOLATION: Entity resolution prohibited at private residential locations.",
        )

    if not b1 or not b2 or b1 != b2:
        return False, "DISTINCT_BUILDINGS: Addresses do not share an identical building_key."

    # Check for CRA hub
    is_hub1 = addr1.get("is_registered_agent_hub", False) if isinstance(addr1, dict) else getattr(addr1, "is_registered_agent_hub", False)
    is_hub2 = addr2.get("is_registered_agent_hub", False) if isinstance(addr2, dict) else getattr(addr2, "is_registered_agent_hub", False)
    flags1 = addr1.get("corporate_risk_flags", []) if isinstance(addr1, dict) else getattr(addr1, "corporate_risk_flags", [])
    flags2 = addr2.get("corporate_risk_flags", []) if isinstance(addr2, dict) else getattr(addr2, "corporate_risk_flags", [])

    if (
        is_hub1
        or is_hub2
        or CorporateRiskFlag.RISK_CRA_CO_LOCATION in flags1
        or CorporateRiskFlag.RISK_CRA_CO_LOCATION in flags2
        or CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB in flags1
        or CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB in flags2
    ):
        return (
            False,
            "CO_LOCATION_ISOLATION_INVARIANT: Both entities share a registered agent / formation hub "
            "building_key. Corporate profile consolidation is strictly prohibited.",
        )

    # Check for Virtual Office / Mail Drop
    is_cmra1 = getattr(addr1, "is_cmra", False) or getattr(addr1, "cmra", False)
    is_cmra2 = getattr(addr2, "is_cmra", False) or getattr(addr2, "cmra", False)
    if (
        is_cmra1
        or is_cmra2
        or CorporateRiskFlag.RISK_VIRTUAL_OFFICE in flags1
        or CorporateRiskFlag.RISK_VIRTUAL_OFFICE in flags2
        or CorporateRiskFlag.RISK_CMRA_MAIL_DROP in flags1
        or CorporateRiskFlag.RISK_CMRA_MAIL_DROP in flags2
    ):
        return (
            False,
            "CO_LOCATION_ISOLATION_INVARIANT: Shared virtual office or CMRA mail drop location. "
            "Corporate profile consolidation is prohibited without independent EIN or SOS verification.",
        )

    # Compare secondary units
    s2_1 = (getattr(addr1, "street2", "") or "").strip().upper()
    s2_2 = (getattr(addr2, "street2", "") or "").strip().upper()

    if s2_1 and s2_2:
        if s2_1 == s2_2:
            return True, "MATCHING_SECONDARY_UNIT: Co-located entities share building and exact secondary unit."
        return False, "SECONDARY_UNIT_MISMATCH: Distinct suites/units within the same parcel."

    if not s2_1 and not s2_2:
        return True, "SINGLE_TENANT_BUILDING: Both entities occupy the same parcel without secondary units."

    return False, "SECONDARY_UNIT_ASYMMETRY: One entity supplied a suite/unit while the other omitted it."


def evaluate_corporate_risk(
    std_address: Any,
    raw_input: Optional[Dict[str, Any]] = None,
) -> Tuple[float, List[str]]:
    """
    Computes a normalized corporate risk score in [0.0, 1.0] and returns KYC/AML
    corporate transparency risk flags based on FinCEN CTA/BOI criteria.
    """
    raw = raw_input or {}
    raw_combined = f"{raw.get('street1', '')} {raw.get('street2', '')} {getattr(std_address, 'raw_street_address', '')}".upper()

    flags: List[str] = []

    def _add_flag(flag: str):
        if flag not in flags:
            flags.append(flag)

    base_score = 0.0

    # 1. Lookup in curated registry
    entry = lookup_corporate_registry(
        street1=getattr(std_address, "street1", ""),
        street2=getattr(std_address, "street2", ""),
        city=getattr(std_address, "city", ""),
        state=getattr(std_address, "state", ""),
        postal_code=getattr(std_address, "postal_code", ""),
        country=getattr(std_address, "country", "USA"),
        raw_street=getattr(std_address, "raw_street_address", ""),
    )

    if entry is not None:
        base_score = max(base_score, entry.base_risk_score)
        if entry.category in (RegistryCategory.COMMERCIAL_REGISTERED_AGENT, RegistryCategory.FORMATION_AGENT):
            _add_flag(CorporateRiskFlag.RISK_CRA_CO_LOCATION)
        elif entry.category == RegistryCategory.VIRTUAL_OFFICE:
            _add_flag(CorporateRiskFlag.RISK_VIRTUAL_OFFICE)
        elif entry.category == RegistryCategory.OFFSHORE_SECRECY:
            _add_flag(CorporateRiskFlag.RISK_OFFSHORE_SECRECY_HUB)
        elif entry.category == RegistryCategory.MAIL_DROP_CMRA:
            _add_flag(CorporateRiskFlag.RISK_CMRA_MAIL_DROP)
    elif getattr(std_address, "is_registered_agent_hub", False):
        base_score = max(base_score, 0.85)
        _add_flag(CorporateRiskFlag.RISK_CRA_CO_LOCATION)

    # 2. Check for missing secondary unit at commercial hub
    has_sec = bool(getattr(std_address, "street2", "").strip())
    if (
        CorporateRiskFlag.RISK_CRA_CO_LOCATION in flags
        or CorporateRiskFlag.RISK_VIRTUAL_OFFICE in flags
    ) and not has_sec:
        _add_flag(CorporateRiskFlag.RISK_MISSING_SECONDARY_AT_HUB)
        base_score = min(1.0, base_score + 0.05)

    # 3. Check for disguised PMB (e.g., 'PMB' in raw, but formatted as 'Suite' in standardized)
    raw_has_pmb = "PMB" in raw_combined or "PRIVATE MAILBOX" in raw_combined
    std_sec = (getattr(std_address, "street2", "") or "").upper()
    std_has_ste = any(t in std_sec for t in ["STE", "SUITE", "APT", "UNIT", "FL"])
    std_has_pmb = "PMB" in std_sec

    if (raw_has_pmb and std_has_ste) or (not raw_has_pmb and std_has_pmb):
        _add_flag(CorporateRiskFlag.RISK_DISGUISED_PMB)
        _add_flag(CorporateRiskFlag.RISK_CMRA_MAIL_DROP)
        base_score = max(base_score, 0.65)
    elif raw_has_pmb or std_has_pmb:
        _add_flag(CorporateRiskFlag.RISK_CMRA_MAIL_DROP)
        base_score = max(base_score, 0.60)

    # 4. Check for private residence commercial risk
    if getattr(std_address, "is_private_residence", False):
        _add_flag(CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL)
        base_score = max(base_score, 0.40)

    final_score = round(max(0.0, min(1.0, base_score)), 4)
    return final_score, flags
