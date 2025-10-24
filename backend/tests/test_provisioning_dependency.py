"""
Test Dependency Validation

Phase 2.3: Upstream connectivity requirements
"""

import pytest

from backend.models.core import DeviceType
from backend.services.provisioning_service import ProvisioningError, ProvisioningService


# ==========================================
# ROOT DEVICES (No upstream required)
# ==========================================


@pytest.mark.asyncio
async def test_backbone_gateway_no_upstream_required(async_session):
    """Test: BACKBONE_GATEWAY can be provisioned without upstream"""
    service = ProvisioningService(async_session)
    
    # Should succeed - no upstream required
    device = await service.provision_device(
        name="backbone1",
        device_type=DeviceType.BACKBONE_GATEWAY,
    )
    
    assert device.id is not None
    assert device.device_type == DeviceType.BACKBONE_GATEWAY


@pytest.mark.asyncio
async def test_core_router_no_upstream_required(async_session):
    """Test: CORE_ROUTER can be provisioned without upstream"""
    service = ProvisioningService(async_session)
    
    # Should succeed - no upstream required
    device = await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    
    assert device.id is not None


@pytest.mark.asyncio
async def test_container_devices_no_upstream_required(async_session):
    """Test: Container devices (POP, CORE_SITE) need no upstream"""
    service = ProvisioningService(async_session)
    
    pop = await service.provision_device(
        name="pop1",
        device_type=DeviceType.POP,
    )
    assert pop.id is not None
    
    core_site = await service.provision_device(
        name="site1",
        device_type=DeviceType.CORE_SITE,
    )
    assert core_site.id is not None


@pytest.mark.asyncio
async def test_passive_devices_no_upstream_required(async_session):
    """Test: Passive devices need no upstream validation"""
    service = ProvisioningService(async_session)
    
    # All passive types should provision without upstream
    odf = await service.provision_device(
        name="odf1",
        device_type=DeviceType.ODF,
    )
    assert odf.id is not None
    
    nvt = await service.provision_device(
        name="nvt1",
        device_type=DeviceType.NVT,
    )
    assert nvt.id is not None
    
    splitter = await service.provision_device(
        name="splitter1",
        device_type=DeviceType.SPLITTER,
    )
    assert splitter.id is not None
    
    hop = await service.provision_device(
        name="hop1",
        device_type=DeviceType.HOP,
    )
    assert hop.id is not None


# ==========================================
# EDGE_ROUTER DEPENDENCY
# ==========================================


@pytest.mark.asyncio
async def test_edge_router_requires_core_router(async_session):
    """Test: EDGE_ROUTER requires CORE_ROUTER upstream"""
    service = ProvisioningService(async_session)
    
    # Try to provision EDGE without CORE - should fail
    with pytest.raises(ProvisioningError, match="No CORE_ROUTER or BACKBONE_GATEWAY"):
        await service.provision_device(
            name="edge1",
            device_type=DeviceType.EDGE_ROUTER,
        )
    
    # Create CORE_ROUTER
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    
    # Now EDGE should succeed
    edge = await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    assert edge.id is not None


@pytest.mark.asyncio
async def test_edge_router_accepts_backbone_gateway(async_session):
    """Test: EDGE_ROUTER can use BACKBONE_GATEWAY as upstream"""
    service = ProvisioningService(async_session)
    
    # Create BACKBONE_GATEWAY
    await service.provision_device(
        name="backbone1",
        device_type=DeviceType.BACKBONE_GATEWAY,
    )
    
    # EDGE should succeed with BACKBONE upstream
    edge = await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    assert edge.id is not None


# ==========================================
# OLT DEPENDENCY
# ==========================================


@pytest.mark.asyncio
async def test_olt_requires_edge_router(async_session):
    """Test: OLT requires EDGE_ROUTER upstream"""
    service = ProvisioningService(async_session)
    
    # Try to provision OLT without EDGE - should fail
    with pytest.raises(ProvisioningError, match="No EDGE_ROUTER exists"):
        await service.provision_device(
            name="olt1",
            device_type=DeviceType.OLT,
        )
    
    # Create CORE → EDGE chain
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    
    # Now OLT should succeed
    olt = await service.provision_device(
        name="olt1",
        device_type=DeviceType.OLT,
    )
    assert olt.id is not None


# ==========================================
# AON_SWITCH DEPENDENCY
# ==========================================


@pytest.mark.asyncio
async def test_aon_switch_requires_edge_router(async_session):
    """Test: AON_SWITCH requires EDGE_ROUTER upstream"""
    service = ProvisioningService(async_session)
    
    # Try to provision AON_SWITCH without EDGE - should fail
    with pytest.raises(ProvisioningError, match="No EDGE_ROUTER exists"):
        await service.provision_device(
            name="aon1",
            device_type=DeviceType.AON_SWITCH,
        )
    
    # Create upstream
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    
    # Now AON_SWITCH should succeed
    aon = await service.provision_device(
        name="aon1",
        device_type=DeviceType.AON_SWITCH,
    )
    assert aon.id is not None


# ==========================================
# ONT DEPENDENCY
# ==========================================


@pytest.mark.asyncio
async def test_ont_requires_olt(async_session):
    """Test: ONT requires OLT upstream"""
    service = ProvisioningService(async_session)
    
    # Try to provision ONT without OLT - should fail
    with pytest.raises(ProvisioningError, match="No OLT exists"):
        await service.provision_device(
            name="ont1",
            device_type=DeviceType.ONT,
        )
    
    # Create full chain: CORE → EDGE → OLT
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    await service.provision_device(
        name="olt1",
        device_type=DeviceType.OLT,
    )
    
    # Now ONT should succeed
    ont = await service.provision_device(
        name="ont1",
        device_type=DeviceType.ONT,
    )
    assert ont.id is not None


@pytest.mark.asyncio
async def test_business_ont_requires_olt(async_session):
    """Test: BUSINESS_ONT requires OLT upstream"""
    service = ProvisioningService(async_session)
    
    # Try to provision BUSINESS_ONT without OLT - should fail
    with pytest.raises(ProvisioningError, match="No OLT exists"):
        await service.provision_device(
            name="bont1",
            device_type=DeviceType.BUSINESS_ONT,
        )
    
    # Create upstream
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    await service.provision_device(
        name="olt1",
        device_type=DeviceType.OLT,
    )
    
    # Now BUSINESS_ONT should succeed
    bont = await service.provision_device(
        name="bont1",
        device_type=DeviceType.BUSINESS_ONT,
    )
    assert bont.id is not None


# ==========================================
# AON_CPE DEPENDENCY
# ==========================================


@pytest.mark.asyncio
async def test_aon_cpe_requires_aon_switch(async_session):
    """Test: AON_CPE requires AON_SWITCH upstream"""
    service = ProvisioningService(async_session)
    
    # Try to provision AON_CPE without AON_SWITCH - should fail
    with pytest.raises(ProvisioningError, match="No AON_SWITCH exists"):
        await service.provision_device(
            name="cpe1",
            device_type=DeviceType.AON_CPE,
        )
    
    # Create full chain: CORE → EDGE → AON_SWITCH
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    await service.provision_device(
        name="aon1",
        device_type=DeviceType.AON_SWITCH,
    )
    
    # Now AON_CPE should succeed
    cpe = await service.provision_device(
        name="cpe1",
        device_type=DeviceType.AON_CPE,
    )
    assert cpe.id is not None


# ==========================================
# BYPASS VALIDATION
# ==========================================


@pytest.mark.asyncio
async def test_bypass_upstream_validation(async_session):
    """Test: Can bypass upstream validation with validate_upstream=False"""
    service = ProvisioningService(async_session)
    
    # Provision OLT without upstream - should fail normally
    with pytest.raises(ProvisioningError):
        await service.provision_device(
            name="olt1",
            device_type=DeviceType.OLT,
        )
    
    # Bypass validation - should succeed
    olt = await service.provision_device(
        name="olt1",
        device_type=DeviceType.OLT,
        validate_upstream=False,
    )
    assert olt.id is not None


# ==========================================
# FULL TOPOLOGY TEST
# ==========================================


@pytest.mark.asyncio
async def test_full_topology_provisioning_order(async_session):
    """Test: Provision complete topology in correct order"""
    service = ProvisioningService(async_session)
    
    # 1. Root: BACKBONE_GATEWAY
    backbone = await service.provision_device(
        name="backbone1",
        device_type=DeviceType.BACKBONE_GATEWAY,
    )
    assert backbone.id is not None
    
    # 2. CORE_ROUTER
    core = await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    assert core.id is not None
    
    # 3. EDGE_ROUTER
    edge = await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    assert edge.id is not None
    
    # 4a. OLT
    olt = await service.provision_device(
        name="olt1",
        device_type=DeviceType.OLT,
    )
    assert olt.id is not None
    
    # 4b. AON_SWITCH
    aon = await service.provision_device(
        name="aon1",
        device_type=DeviceType.AON_SWITCH,
    )
    assert aon.id is not None
    
    # 5a. ONT
    ont = await service.provision_device(
        name="ont1",
        device_type=DeviceType.ONT,
    )
    assert ont.id is not None
    
    # 5b. AON_CPE
    cpe = await service.provision_device(
        name="cpe1",
        device_type=DeviceType.AON_CPE,
    )
    assert cpe.id is not None
    
    # All 7 devices provisioned successfully
    assert True


@pytest.mark.asyncio
async def test_multiple_upstreams_of_same_type(async_session):
    """Test: Multiple EDGE routers can exist with single CORE"""
    service = ProvisioningService(async_session)
    
    # Create CORE
    await service.provision_device(
        name="core1",
        device_type=DeviceType.CORE_ROUTER,
    )
    
    # Create multiple EDGE routers
    edge1 = await service.provision_device(
        name="edge1",
        device_type=DeviceType.EDGE_ROUTER,
    )
    edge2 = await service.provision_device(
        name="edge2",
        device_type=DeviceType.EDGE_ROUTER,
    )
    edge3 = await service.provision_device(
        name="edge3",
        device_type=DeviceType.EDGE_ROUTER,
    )
    
    assert edge1.id is not None
    assert edge2.id is not None
    assert edge3.id is not None
