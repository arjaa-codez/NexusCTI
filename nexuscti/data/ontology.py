"""
Ontology definitions, entity schemas, and relationship types for NexusCTI.
Aligned with MITRE ATT&CK and STIX 2.1 specifications.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    THREAT_ACTOR = "ThreatActor"       # e.g., APT28, APT29, Lazarus Group, Sandworm, FIN7, Volt Typhoon
    MALWARE = "Malware"                 # e.g., Cobalt Strike, SUNBURST, BlackEnergy, Industroyer, TrickBot
    INDICATOR = "Indicator"             # e.g., IP address, domain, C2 URL, SHA256 hash
    TTP = "TTP"                         # MITRE ATT&CK technique e.g. T1059, T1071, T1190, T1566
    VULNERABILITY = "Vulnerability"     # CVE ID e.g., CVE-2021-44228, CVE-2020-1472, CVE-2021-26855


class EdgeType(str, Enum):
    USES = "uses"                       # ThreatActor -> Malware
    EXECUTES = "executes"               # ThreatActor -> TTP
    TARGETS = "targets"                 # ThreatActor -> Vulnerability
    CONTROLS = "controls"               # ThreatActor -> Indicator
    COMMUNICATES_WITH = "communicates_with" # Malware -> Indicator
    EXPLOITS = "exploits"               # Malware -> Vulnerability
    MAPS_TO = "maps_to"                 # Malware -> TTP
    RESOLVES_TO = "resolves_to"         # Indicator (Domain) -> Indicator (IP)
    SHARES_INFRA = "shares_infra"       # Indicator -> Indicator
    ASSOCIATED_WITH = "associated_with" # General relationship


class IndicatorType(str, Enum):
    IPV4 = "ipv4"
    DOMAIN = "domain"
    FILE_HASH = "file_hash"
    URL = "url"
    MUTEX = "mutex"


class Node(BaseModel):
    id: str
    name: str
    type: NodeType
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "metadata": self.metadata,
        }


class Edge(BaseModel):
    source: str
    target: str
    type: EdgeType
    confidence: float = 1.0
    source_citation: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.value,
            "confidence": self.confidence,
            "source_citation": self.source_citation,
            "metadata": self.metadata,
        }
