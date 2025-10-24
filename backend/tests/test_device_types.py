"""
Test Device Types and Optical Attributes

Tests für alle 13 Device Types und ihre spezifischen Optical Attributes.
"""

import pytest
from sqlmodel import select

from backend.models.core import Device, DeviceType, Status


@pytest.mark.asyncio
async def test_all_13_device_types_createable(async_session):
    """Test: Alle 14 Device Types können erstellt werden"""
    device_types = [
        # Active Devices
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.CORE_ROUTER,
        DeviceType.EDGE_ROUTER,
        DeviceType.OLT,
        DeviceType.AON_SWITCH,
        DeviceType.ONT,
        DeviceType.BUSINESS_ONT,
        DeviceType.AON_CPE,
        # Container Devices
        DeviceType.POP,
        DeviceType.CORE_SITE,
        # Passive Devices
        DeviceType.ODF,
        DeviceType.NVT,
        DeviceType.SPLITTER,
        DeviceType.HOP,
    ]
    
    created_devices = []
    for idx, device_type in enumerate(device_types):
        device = Device(
            name=f"test_{device_type.value.lower()}_{idx}",
            device_type=device_type,
            status=Status.UP,
        )
        async_session.add(device)
        created_devices.append(device)
    
    await async_session.commit()
    
    # Verify all created
    assert len(created_devices) == 14
    
    # Verify in DB
    result = await async_session.execute(select(Device))
    devices = result.scalars().all()
    assert len(devices) == 14


@pytest.mark.asyncio
async def test_olt_tx_power_attribute(async_session):
    """Test: OLT kann tx_power_dbm speichern"""
    olt = Device(
        name="test_olt_with_tx_power",
        device_type=DeviceType.OLT,
        tx_power_dbm=5.0,  # 5 dBm transmit power
    )
    async_session.add(olt)
    await async_session.commit()
    await async_session.refresh(olt)
    
    assert olt.tx_power_dbm == 5.0
    assert olt.sensitivity_min_dbm is None  # ONT attribute
    assert olt.insertion_loss_db is None  # Passive attribute


@pytest.mark.asyncio
async def test_ont_sensitivity_attribute(async_session):
    """Test: ONT kann sensitivity_min_dbm speichern"""
    ont = Device(
        name="test_ont_with_sensitivity",
        device_type=DeviceType.ONT,
        sensitivity_min_dbm=-28.0,  # -28 dBm minimum sensitivity
    )
    async_session.add(ont)
    await async_session.commit()
    await async_session.refresh(ont)
    
    assert ont.sensitivity_min_dbm == -28.0
    assert ont.tx_power_dbm is None  # OLT attribute
    assert ont.insertion_loss_db is None  # Passive attribute


@pytest.mark.asyncio
async def test_passive_device_insertion_loss(async_session):
    """Test: Passive Devices können insertion_loss_db speichern"""
    passive_types = [
        DeviceType.ODF,
        DeviceType.NVT,
        DeviceType.SPLITTER,
        DeviceType.HOP,
    ]
    
    for idx, device_type in enumerate(passive_types):
        device = Device(
            name=f"test_{device_type.value.lower()}_{idx}",
            device_type=device_type,
            insertion_loss_db=0.5 + (idx * 0.1),  # Varying loss
        )
        async_session.add(device)
    
    await async_session.commit()
    
    # Verify all passive devices have insertion_loss_db
    result = await async_session.execute(
        select(Device).where(Device.device_type.in_(passive_types))
    )
    devices = result.scalars().all()
    assert len(devices) == 4
    
    for device in devices:
        assert device.insertion_loss_db is not None
        assert device.insertion_loss_db > 0
        assert device.tx_power_dbm is None
        assert device.sensitivity_min_dbm is None


@pytest.mark.asyncio
async def test_container_device_hierarchy(async_session):
    """Test: Container Devices (POP, CORE_SITE) können parent_container_id haben (None)"""
    pop = Device(
        name="test_pop_container",
        device_type=DeviceType.POP,
        parent_container_id=None,  # Containers haben keine Parents
    )
    core_site = Device(
        name="test_core_site_container",
        device_type=DeviceType.CORE_SITE,
        parent_container_id=None,
    )
    
    async_session.add(pop)
    async_session.add(core_site)
    await async_session.commit()
    
    await async_session.refresh(pop)
    await async_session.refresh(core_site)
    
    assert pop.parent_container_id is None
    assert core_site.parent_container_id is None


@pytest.mark.asyncio
async def test_device_can_have_parent_container(async_session):
    """Test: Devices können parent_container_id haben"""
    # Create POP container first
    pop = Device(
        name="test_pop_parent",
        device_type=DeviceType.POP,
    )
    async_session.add(pop)
    await async_session.commit()
    await async_session.refresh(pop)
    
    # Create OLT inside POP
    olt = Device(
        name="test_olt_child",
        device_type=DeviceType.OLT,
        parent_container_id=pop.id,
    )
    async_session.add(olt)
    await async_session.commit()
    await async_session.refresh(olt)
    
    assert olt.parent_container_id == pop.id


@pytest.mark.asyncio
async def test_device_type_classification(async_session):
    """Test: Device Types sind korrekt klassifiziert"""
    active_types = {
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.CORE_ROUTER,
        DeviceType.EDGE_ROUTER,
        DeviceType.OLT,
        DeviceType.AON_SWITCH,
        DeviceType.ONT,
        DeviceType.BUSINESS_ONT,
        DeviceType.AON_CPE,
    }
    
    container_types = {
        DeviceType.POP,
        DeviceType.CORE_SITE,
    }
    
    passive_types = {
        DeviceType.ODF,
        DeviceType.NVT,
        DeviceType.SPLITTER,
        DeviceType.HOP,
    }
    
    # Verify all types are unique
    all_types = active_types | container_types | passive_types
    assert len(all_types) == 14
    
    # Verify no overlap
    assert len(active_types & container_types) == 0
    assert len(active_types & passive_types) == 0
    assert len(container_types & passive_types) == 0


@pytest.mark.asyncio
async def test_optical_attributes_default_to_none(async_session):
    """Test: Optical Attributes sind standardmäßig None"""
    router = Device(
        name="test_router_no_optical",
        device_type=DeviceType.CORE_ROUTER,
    )
    async_session.add(router)
    await async_session.commit()
    await async_session.refresh(router)
    
    assert router.tx_power_dbm is None
    assert router.sensitivity_min_dbm is None
    assert router.insertion_loss_db is None
