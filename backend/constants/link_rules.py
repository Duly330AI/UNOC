"""
Link Type Rules (L1-L9) - Network Topology Constraints

PHASE 2.2: LINK TYPE RULES
===========================

NETWORK HIERARCHY:
-----------------
BACKBONE_GATEWAY (Always-Online Root)
    ↓ L1: BACKBONE-CORE
CORE_ROUTER (Core Network)
    ↓ L2: CORE-EDGE
EDGE_ROUTER (Distribution)
    ↓ L3: EDGE-OLT (GPON)
    ↓ L4: EDGE-AON (Active Optical)
OLT (Optical Line Terminal)
    ↓ L5: OLT-ONT (GPON last mile)
    ↓ L6: OLT-BUSINESS_ONT (Business GPON)
AON_SWITCH (Active Optical Network)
    ↓ L7: AON-CPE (Active Optical last mile)
ONT/BUSINESS_ONT (Customer Premise)

PASSIVE DEVICE LINKS:
---------------------
L8: INLINE_PASSIVE - Any active ↔ Passive ↔ Active
    Examples: OLT ↔ ODF ↔ SPLITTER ↔ ONT
              EDGE ↔ NVT ↔ OLT
L9: PEER_TO_PEER - Same-level devices
    Examples: CORE ↔ CORE (mesh)
              EDGE ↔ EDGE (redundancy)

LINK TYPE DEFINITIONS:
----------------------
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from backend.models.core import DeviceType


class LinkType(str, Enum):
    """Link types in network hierarchy"""
    
    # Core hierarchy
    BACKBONE_CORE = "L1_BACKBONE_CORE"  # BACKBONE_GATEWAY ↔ CORE_ROUTER
    CORE_EDGE = "L2_CORE_EDGE"  # CORE_ROUTER ↔ EDGE_ROUTER
    
    # Access hierarchy
    EDGE_OLT = "L3_EDGE_OLT"  # EDGE_ROUTER ↔ OLT (GPON)
    EDGE_AON = "L4_EDGE_AON"  # EDGE_ROUTER ↔ AON_SWITCH (Active Optical)
    
    # Last mile
    OLT_ONT = "L5_OLT_ONT"  # OLT ↔ ONT (Residential)
    OLT_BUSINESS = "L6_OLT_BUSINESS_ONT"  # OLT ↔ BUSINESS_ONT
    AON_CPE = "L7_AON_CPE"  # AON_SWITCH ↔ AON_CPE
    
    # Special links
    INLINE_PASSIVE = "L8_INLINE_PASSIVE"  # Any ↔ Passive Device ↔ Any
    PEER_TO_PEER = "L9_PEER_TO_PEER"  # Same-level redundancy


@dataclass
class LinkRule:
    """
    Rule defining valid link between two device types.
    
    Attributes:
        link_type: Type of link (L1-L9)
        device_a_type: Type of first device
        device_b_type: Type of second device
        bidirectional: Whether link can be reversed (A↔B vs A→B)
        description: Human-readable description
    """
    
    link_type: LinkType
    device_a_type: DeviceType
    device_b_type: DeviceType
    bidirectional: bool = True
    description: str = ""


# ==========================================
# LINK RULES REGISTRY
# ==========================================

LINK_RULES: list[LinkRule] = [
    # L1: BACKBONE → CORE
    LinkRule(
        link_type=LinkType.BACKBONE_CORE,
        device_a_type=DeviceType.BACKBONE_GATEWAY,
        device_b_type=DeviceType.CORE_ROUTER,
        bidirectional=True,
        description="Backbone gateway connects to core routers",
    ),
    
    # L2: CORE → EDGE
    LinkRule(
        link_type=LinkType.CORE_EDGE,
        device_a_type=DeviceType.CORE_ROUTER,
        device_b_type=DeviceType.EDGE_ROUTER,
        bidirectional=True,
        description="Core router connects to edge routers",
    ),
    
    # L3: EDGE → OLT (GPON)
    LinkRule(
        link_type=LinkType.EDGE_OLT,
        device_a_type=DeviceType.EDGE_ROUTER,
        device_b_type=DeviceType.OLT,
        bidirectional=True,
        description="Edge router provides upstream for OLT",
    ),
    
    # L4: EDGE → AON SWITCH
    LinkRule(
        link_type=LinkType.EDGE_AON,
        device_a_type=DeviceType.EDGE_ROUTER,
        device_b_type=DeviceType.AON_SWITCH,
        bidirectional=True,
        description="Edge router provides upstream for AON switch",
    ),
    
    # L5: OLT → ONT (Residential)
    LinkRule(
        link_type=LinkType.OLT_ONT,
        device_a_type=DeviceType.OLT,
        device_b_type=DeviceType.ONT,
        bidirectional=True,
        description="OLT connects to residential ONT via PON",
    ),
    
    # L6: OLT → BUSINESS ONT
    LinkRule(
        link_type=LinkType.OLT_BUSINESS,
        device_a_type=DeviceType.OLT,
        device_b_type=DeviceType.BUSINESS_ONT,
        bidirectional=True,
        description="OLT connects to business ONT with enhanced SLA",
    ),
    
    # L7: AON SWITCH → CPE
    LinkRule(
        link_type=LinkType.AON_CPE,
        device_a_type=DeviceType.AON_SWITCH,
        device_b_type=DeviceType.AON_CPE,
        bidirectional=True,
        description="AON switch connects to customer premise equipment",
    ),
]

# L8: INLINE_PASSIVE - Defined dynamically (any active ↔ passive)
PASSIVE_DEVICE_TYPES = {
    DeviceType.ODF,
    DeviceType.NVT,
    DeviceType.SPLITTER,
    DeviceType.HOP,
}

ACTIVE_DEVICE_TYPES = {
    DeviceType.BACKBONE_GATEWAY,
    DeviceType.CORE_ROUTER,
    DeviceType.EDGE_ROUTER,
    DeviceType.OLT,
    DeviceType.AON_SWITCH,
    DeviceType.ONT,
    DeviceType.BUSINESS_ONT,
    DeviceType.AON_CPE,
}

# L9: PEER_TO_PEER - Same-level redundancy
PEER_TO_PEER_ALLOWED = {
    DeviceType.BACKBONE_GATEWAY,  # Backbone mesh
    DeviceType.CORE_ROUTER,  # Core mesh
    DeviceType.EDGE_ROUTER,  # Edge redundancy
}


# ==========================================
# VALIDATION FUNCTIONS
# ==========================================

def validate_link_between_devices(
    device_a_type: DeviceType,
    device_b_type: DeviceType,
) -> tuple[bool, Optional[LinkType], Optional[str]]:
    """
    Validate if a link between two device types is allowed.
    
    Args:
        device_a_type: Type of first device
        device_b_type: Type of second device
    
    Returns:
        Tuple of (is_valid, link_type, reason)
        - is_valid: Whether link is allowed
        - link_type: Type of link (if valid)
        - reason: Error message (if invalid) or description (if valid)
    """
    # Check standard rules (L1-L7)
    for rule in LINK_RULES:
        if rule.bidirectional:
            # Check both directions
            if (device_a_type == rule.device_a_type and device_b_type == rule.device_b_type) or \
               (device_a_type == rule.device_b_type and device_b_type == rule.device_a_type):
                return (True, rule.link_type, rule.description)
        else:
            # Check only A→B direction
            if device_a_type == rule.device_a_type and device_b_type == rule.device_b_type:
                return (True, rule.link_type, rule.description)
    
    # Check L8: INLINE_PASSIVE (Active ↔ Passive)
    if (device_a_type in ACTIVE_DEVICE_TYPES and device_b_type in PASSIVE_DEVICE_TYPES) or \
       (device_a_type in PASSIVE_DEVICE_TYPES and device_b_type in ACTIVE_DEVICE_TYPES):
        return (
            True,
            LinkType.INLINE_PASSIVE,
            "Passive device can be inline in any active connection",
        )
    
    # Check L8: Passive ↔ Passive (splicing, patching)
    if device_a_type in PASSIVE_DEVICE_TYPES and device_b_type in PASSIVE_DEVICE_TYPES:
        return (
            True,
            LinkType.INLINE_PASSIVE,
            "Passive devices can be interconnected (patch panels, splicing)",
        )
    
    # Check L9: PEER_TO_PEER (same-level redundancy)
    if device_a_type == device_b_type and device_a_type in PEER_TO_PEER_ALLOWED:
        return (
            True,
            LinkType.PEER_TO_PEER,
            f"Peer-to-peer connection allowed for {device_a_type.value} redundancy",
        )
    
    # Invalid link
    return (
        False,
        None,
        f"No valid link rule between {device_a_type.value} and {device_b_type.value}",
    )


def get_allowed_downstream_types(device_type: DeviceType) -> set[DeviceType]:
    """
    Get all device types that can be connected downstream from this device.
    
    Args:
        device_type: Source device type
    
    Returns:
        Set of allowed downstream device types
    """
    allowed = set()
    
    # Check standard rules
    for rule in LINK_RULES:
        if rule.device_a_type == device_type:
            allowed.add(rule.device_b_type)
        elif rule.bidirectional and rule.device_b_type == device_type:
            allowed.add(rule.device_a_type)
    
    # Add passive devices (always allowed)
    if device_type in ACTIVE_DEVICE_TYPES:
        allowed.update(PASSIVE_DEVICE_TYPES)
    
    # Add peer-to-peer if allowed
    if device_type in PEER_TO_PEER_ALLOWED:
        allowed.add(device_type)
    
    return allowed


def get_link_type_description(link_type: LinkType) -> str:
    """Get human-readable description of link type"""
    descriptions = {
        LinkType.BACKBONE_CORE: "Backbone Gateway ↔ Core Router",
        LinkType.CORE_EDGE: "Core Router ↔ Edge Router",
        LinkType.EDGE_OLT: "Edge Router ↔ OLT (GPON)",
        LinkType.EDGE_AON: "Edge Router ↔ AON Switch",
        LinkType.OLT_ONT: "OLT ↔ ONT (Residential)",
        LinkType.OLT_BUSINESS: "OLT ↔ Business ONT",
        LinkType.AON_CPE: "AON Switch ↔ CPE",
        LinkType.INLINE_PASSIVE: "Active/Passive Inline Connection",
        LinkType.PEER_TO_PEER: "Same-Level Redundancy",
    }
    return descriptions.get(link_type, "Unknown link type")


def is_valid_topology_path(path: list[DeviceType]) -> bool:
    """
    Validate if a path through multiple devices follows valid link rules.
    
    Args:
        path: List of device types forming a path
    
    Returns:
        True if all consecutive links are valid
    """
    if len(path) < 2:
        return True
    
    for i in range(len(path) - 1):
        is_valid, _, _ = validate_link_between_devices(path[i], path[i + 1])
        if not is_valid:
            return False
    
    return True
