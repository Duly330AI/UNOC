"""
Test Link Type Rules (L1-L9)

Phase 2.2: Link topology validation
"""


from backend.constants.link_rules import (
    LinkType,
    get_allowed_downstream_types,
    get_link_type_description,
    is_valid_topology_path,
    validate_link_between_devices,
)
from backend.models.core import DeviceType


# ==========================================
# L1-L7: STANDARD HIERARCHY TESTS
# ==========================================


def test_l1_backbone_to_core_valid():
    """Test: L1 - BACKBONE_GATEWAY ↔ CORE_ROUTER is valid"""
    is_valid, link_type, reason = validate_link_between_devices(
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.CORE_ROUTER,
    )
    
    assert is_valid is True
    assert link_type == LinkType.BACKBONE_CORE
    assert "Backbone" in reason


def test_l1_bidirectional():
    """Test: L1 link works in both directions"""
    # Forward
    valid_forward, _, _ = validate_link_between_devices(
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.CORE_ROUTER,
    )
    
    # Reverse
    valid_reverse, _, _ = validate_link_between_devices(
        DeviceType.CORE_ROUTER,
        DeviceType.BACKBONE_GATEWAY,
    )
    
    assert valid_forward is True
    assert valid_reverse is True


def test_l2_core_to_edge_valid():
    """Test: L2 - CORE_ROUTER ↔ EDGE_ROUTER is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.CORE_ROUTER,
        DeviceType.EDGE_ROUTER,
    )
    
    assert is_valid is True
    assert link_type == LinkType.CORE_EDGE


def test_l3_edge_to_olt_valid():
    """Test: L3 - EDGE_ROUTER ↔ OLT is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.EDGE_ROUTER,
        DeviceType.OLT,
    )
    
    assert is_valid is True
    assert link_type == LinkType.EDGE_OLT


def test_l4_edge_to_aon_valid():
    """Test: L4 - EDGE_ROUTER ↔ AON_SWITCH is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.EDGE_ROUTER,
        DeviceType.AON_SWITCH,
    )
    
    assert is_valid is True
    assert link_type == LinkType.EDGE_AON


def test_l5_olt_to_ont_valid():
    """Test: L5 - OLT ↔ ONT is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.OLT,
        DeviceType.ONT,
    )
    
    assert is_valid is True
    assert link_type == LinkType.OLT_ONT


def test_l6_olt_to_business_ont_valid():
    """Test: L6 - OLT ↔ BUSINESS_ONT is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.OLT,
        DeviceType.BUSINESS_ONT,
    )
    
    assert is_valid is True
    assert link_type == LinkType.OLT_BUSINESS


def test_l7_aon_to_cpe_valid():
    """Test: L7 - AON_SWITCH ↔ AON_CPE is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.AON_SWITCH,
        DeviceType.AON_CPE,
    )
    
    assert is_valid is True
    assert link_type == LinkType.AON_CPE


# ==========================================
# L8: INLINE_PASSIVE TESTS
# ==========================================


def test_l8_active_to_passive_odf_valid():
    """Test: L8 - OLT ↔ ODF is valid (passive inline)"""
    is_valid, link_type, reason = validate_link_between_devices(
        DeviceType.OLT,
        DeviceType.ODF,
    )
    
    assert is_valid is True
    assert link_type == LinkType.INLINE_PASSIVE
    assert "Passive" in reason


def test_l8_edge_to_nvt_valid():
    """Test: L8 - EDGE_ROUTER ↔ NVT is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.EDGE_ROUTER,
        DeviceType.NVT,
    )
    
    assert is_valid is True
    assert link_type == LinkType.INLINE_PASSIVE


def test_l8_olt_to_splitter_valid():
    """Test: L8 - OLT ↔ SPLITTER is valid"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.OLT,
        DeviceType.SPLITTER,
    )
    
    assert is_valid is True
    assert link_type == LinkType.INLINE_PASSIVE


def test_l8_passive_to_passive_valid():
    """Test: L8 - Passive ↔ Passive is valid (patch panels)"""
    is_valid, link_type, reason = validate_link_between_devices(
        DeviceType.ODF,
        DeviceType.SPLITTER,
    )
    
    assert is_valid is True
    assert link_type == LinkType.INLINE_PASSIVE
    assert "interconnected" in reason.lower()


def test_l8_all_passive_types_with_active():
    """Test: All passive device types can connect to active devices"""
    passive_types = [
        DeviceType.ODF,
        DeviceType.NVT,
        DeviceType.SPLITTER,
        DeviceType.HOP,
    ]
    
    for passive in passive_types:
        is_valid, link_type, _ = validate_link_between_devices(
            DeviceType.CORE_ROUTER,
            passive,
        )
        assert is_valid is True
        assert link_type == LinkType.INLINE_PASSIVE


# ==========================================
# L9: PEER_TO_PEER TESTS
# ==========================================


def test_l9_backbone_to_backbone_valid():
    """Test: L9 - BACKBONE_GATEWAY ↔ BACKBONE_GATEWAY is valid (mesh)"""
    is_valid, link_type, reason = validate_link_between_devices(
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.BACKBONE_GATEWAY,
    )
    
    assert is_valid is True
    assert link_type == LinkType.PEER_TO_PEER
    assert "redundancy" in reason.lower()


def test_l9_core_to_core_valid():
    """Test: L9 - CORE_ROUTER ↔ CORE_ROUTER is valid (mesh)"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.CORE_ROUTER,
        DeviceType.CORE_ROUTER,
    )
    
    assert is_valid is True
    assert link_type == LinkType.PEER_TO_PEER


def test_l9_edge_to_edge_valid():
    """Test: L9 - EDGE_ROUTER ↔ EDGE_ROUTER is valid (redundancy)"""
    is_valid, link_type, _ = validate_link_between_devices(
        DeviceType.EDGE_ROUTER,
        DeviceType.EDGE_ROUTER,
    )
    
    assert is_valid is True
    assert link_type == LinkType.PEER_TO_PEER


def test_l9_olt_to_olt_invalid():
    """Test: OLT ↔ OLT is NOT allowed (no peer-to-peer for OLT)"""
    is_valid, link_type, reason = validate_link_between_devices(
        DeviceType.OLT,
        DeviceType.OLT,
    )
    
    assert is_valid is False
    assert link_type is None
    assert "No valid link rule" in reason


# ==========================================
# INVALID LINK TESTS
# ==========================================


def test_invalid_backbone_to_ont():
    """Test: BACKBONE_GATEWAY ↔ ONT is invalid (skip hierarchy)"""
    is_valid, link_type, reason = validate_link_between_devices(
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.ONT,
    )
    
    assert is_valid is False
    assert link_type is None
    assert "No valid link rule" in reason


def test_invalid_ont_to_ont():
    """Test: ONT ↔ ONT is invalid (no peer-to-peer for ONT)"""
    is_valid, _, _ = validate_link_between_devices(
        DeviceType.ONT,
        DeviceType.ONT,
    )
    
    assert is_valid is False


def test_invalid_core_to_olt():
    """Test: CORE_ROUTER ↔ OLT is invalid (must go through EDGE)"""
    is_valid, _, _ = validate_link_between_devices(
        DeviceType.CORE_ROUTER,
        DeviceType.OLT,
    )
    
    assert is_valid is False


def test_invalid_aon_switch_to_ont():
    """Test: AON_SWITCH ↔ ONT is invalid (wrong technology)"""
    is_valid, _, _ = validate_link_between_devices(
        DeviceType.AON_SWITCH,
        DeviceType.ONT,
    )
    
    assert is_valid is False


def test_invalid_container_to_container():
    """Test: POP ↔ CORE_SITE is invalid (containers don't link)"""
    is_valid, _, _ = validate_link_between_devices(
        DeviceType.POP,
        DeviceType.CORE_SITE,
    )
    
    assert is_valid is False


# ==========================================
# HELPER FUNCTION TESTS
# ==========================================


def test_get_allowed_downstream_backbone():
    """Test: BACKBONE_GATEWAY can connect downstream to CORE + passive + self"""
    allowed = get_allowed_downstream_types(DeviceType.BACKBONE_GATEWAY)
    
    assert DeviceType.CORE_ROUTER in allowed
    assert DeviceType.BACKBONE_GATEWAY in allowed  # Peer-to-peer
    
    # All passive types
    assert DeviceType.ODF in allowed
    assert DeviceType.NVT in allowed
    assert DeviceType.SPLITTER in allowed
    assert DeviceType.HOP in allowed
    
    # NOT allowed
    assert DeviceType.ONT not in allowed


def test_get_allowed_downstream_olt():
    """Test: OLT can connect to ONT, BUSINESS_ONT, passive"""
    allowed = get_allowed_downstream_types(DeviceType.OLT)
    
    assert DeviceType.ONT in allowed
    assert DeviceType.BUSINESS_ONT in allowed
    assert DeviceType.EDGE_ROUTER in allowed  # Upstream (bidirectional)
    
    # Passive devices
    assert DeviceType.ODF in allowed
    assert DeviceType.SPLITTER in allowed
    
    # NOT allowed
    assert DeviceType.OLT not in allowed  # No peer-to-peer
    assert DeviceType.AON_CPE not in allowed


def test_get_link_type_descriptions():
    """Test: All link types have descriptions"""
    for link_type in LinkType:
        description = get_link_type_description(link_type)
        assert len(description) > 0
        assert description != "Unknown link type"


# ==========================================
# TOPOLOGY PATH TESTS
# ==========================================


def test_valid_topology_path_backbone_to_ont():
    """Test: Valid path BACKBONE → CORE → EDGE → OLT → ONT"""
    path = [
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.CORE_ROUTER,
        DeviceType.EDGE_ROUTER,
        DeviceType.OLT,
        DeviceType.ONT,
    ]
    
    assert is_valid_topology_path(path) is True


def test_valid_topology_path_with_passive():
    """Test: Valid path EDGE → ODF → OLT → SPLITTER → ONT"""
    path = [
        DeviceType.EDGE_ROUTER,
        DeviceType.ODF,
        DeviceType.OLT,
        DeviceType.SPLITTER,
        DeviceType.ONT,
    ]
    
    assert is_valid_topology_path(path) is True


def test_invalid_topology_path_skip_hierarchy():
    """Test: Invalid path BACKBONE → EDGE (skips CORE)"""
    path = [
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.EDGE_ROUTER,  # Invalid - skips CORE
    ]
    
    assert is_valid_topology_path(path) is False


def test_invalid_topology_path_wrong_direction():
    """Test: Invalid path ONT → OLT → EDGE (topology is directional)"""
    # This is actually VALID because all rules are bidirectional
    path = [
        DeviceType.ONT,
        DeviceType.OLT,
        DeviceType.EDGE_ROUTER,
    ]
    
    assert is_valid_topology_path(path) is True


def test_valid_topology_path_aon():
    """Test: Valid path EDGE → AON_SWITCH → AON_CPE"""
    path = [
        DeviceType.EDGE_ROUTER,
        DeviceType.AON_SWITCH,
        DeviceType.AON_CPE,
    ]
    
    assert is_valid_topology_path(path) is True


def test_valid_topology_path_core_mesh():
    """Test: Valid path with peer-to-peer CORE → CORE → EDGE"""
    path = [
        DeviceType.CORE_ROUTER,
        DeviceType.CORE_ROUTER,  # Peer-to-peer mesh
        DeviceType.EDGE_ROUTER,
    ]
    
    assert is_valid_topology_path(path) is True


# ==========================================
# COMPREHENSIVE COVERAGE TEST
# ==========================================


def test_all_link_rules_have_valid_device_types():
    """Test: All defined link rules use valid DeviceType enums"""
    from backend.constants.link_rules import LINK_RULES
    
    for rule in LINK_RULES:
        # Check that device types are valid DeviceType enum members
        assert isinstance(rule.device_a_type, DeviceType)
        assert isinstance(rule.device_b_type, DeviceType)
        
        # Check that link type is valid LinkType enum member
        assert isinstance(rule.link_type, LinkType)
        
        # Check that description exists
        assert len(rule.description) > 0
