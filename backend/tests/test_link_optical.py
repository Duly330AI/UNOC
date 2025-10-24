"""
Test Link Optical Attributes

Tests für Link length_km, physical_medium_id, link_loss_db.
"""

import pytest
from sqlmodel import select

from backend.models.core import Device, DeviceType, Interface, InterfaceType, Link


@pytest.mark.asyncio
async def test_link_with_length_km(async_session):
    """Test: Link kann length_km speichern"""
    # Create two devices with interfaces
    dev1 = Device(name="dev1", device_type=DeviceType.CORE_ROUTER)
    dev2 = Device(name="dev2", device_type=DeviceType.EDGE_ROUTER)
    async_session.add(dev1)
    async_session.add(dev2)
    await async_session.commit()
    
    # Create interfaces
    if1 = Interface(name="eth0", interface_type=InterfaceType.ETHERNET, device_id=dev1.id)
    if2 = Interface(name="eth0", interface_type=InterfaceType.ETHERNET, device_id=dev2.id)
    async_session.add(if1)
    async_session.add(if2)
    await async_session.commit()
    
    # Create link with length
    link = Link(
        a_interface_id=if1.id,
        b_interface_id=if2.id,
        length_km=12.5,  # 12.5 km
    )
    async_session.add(link)
    await async_session.commit()
    await async_session.refresh(link)
    
    assert link.length_km == 12.5
    assert link.physical_medium_id is None
    assert link.link_loss_db is None


@pytest.mark.asyncio
async def test_link_with_fiber_type(async_session):
    """Test: Link kann physical_medium_id (fiber type) speichern"""
    # Create devices and interfaces
    olt = Device(name="olt1", device_type=DeviceType.OLT)
    ont = Device(name="ont1", device_type=DeviceType.ONT)
    async_session.add(olt)
    async_session.add(ont)
    await async_session.commit()
    
    olt_if = Interface(name="pon0", interface_type=InterfaceType.OPTICAL, device_id=olt.id)
    ont_if = Interface(name="eth0", interface_type=InterfaceType.OPTICAL, device_id=ont.id)
    async_session.add(olt_if)
    async_session.add(ont_if)
    await async_session.commit()
    
    # Create optical link with fiber type
    link = Link(
        a_interface_id=olt_if.id,
        b_interface_id=ont_if.id,
        length_km=2.0,
        physical_medium_id="G652D",  # Standard single-mode fiber
    )
    async_session.add(link)
    await async_session.commit()
    await async_session.refresh(link)
    
    assert link.length_km == 2.0
    assert link.physical_medium_id == "G652D"
    assert link.link_loss_db is None  # Computed separately


@pytest.mark.asyncio
async def test_link_with_computed_loss(async_session):
    """Test: Link kann link_loss_db speichern (computed value)"""
    # Create devices and interfaces
    odf1 = Device(name="odf1", device_type=DeviceType.ODF, insertion_loss_db=0.5)
    odf2 = Device(name="odf2", device_type=DeviceType.ODF, insertion_loss_db=0.5)
    async_session.add(odf1)
    async_session.add(odf2)
    await async_session.commit()
    
    if1 = Interface(name="port1", interface_type=InterfaceType.OPTICAL, device_id=odf1.id)
    if2 = Interface(name="port1", interface_type=InterfaceType.OPTICAL, device_id=odf2.id)
    async_session.add(if1)
    async_session.add(if2)
    await async_session.commit()
    
    # Create link with computed loss
    fiber_attenuation_db_per_km = 0.35  # Standard for G652D
    length_km = 5.0
    computed_loss = (length_km * fiber_attenuation_db_per_km) + odf1.insertion_loss_db + odf2.insertion_loss_db
    
    link = Link(
        a_interface_id=if1.id,
        b_interface_id=if2.id,
        length_km=length_km,
        physical_medium_id="G652D",
        link_loss_db=computed_loss,  # Pre-computed: 5*0.35 + 0.5 + 0.5 = 2.75 dB
    )
    async_session.add(link)
    await async_session.commit()
    await async_session.refresh(link)
    
    assert link.link_loss_db == computed_loss
    assert link.link_loss_db == pytest.approx(2.75, rel=0.01)


@pytest.mark.asyncio
async def test_link_optical_attributes_default_to_none(async_session):
    """Test: Optical Attributes sind standardmäßig None"""
    # Create simple non-optical link
    dev1 = Device(name="router1", device_type=DeviceType.CORE_ROUTER)
    dev2 = Device(name="router2", device_type=DeviceType.EDGE_ROUTER)
    async_session.add(dev1)
    async_session.add(dev2)
    await async_session.commit()
    
    if1 = Interface(name="eth0", interface_type=InterfaceType.ETHERNET, device_id=dev1.id)
    if2 = Interface(name="eth0", interface_type=InterfaceType.ETHERNET, device_id=dev2.id)
    async_session.add(if1)
    async_session.add(if2)
    await async_session.commit()
    
    link = Link(
        a_interface_id=if1.id,
        b_interface_id=if2.id,
    )
    async_session.add(link)
    await async_session.commit()
    await async_session.refresh(link)
    
    assert link.length_km is None
    assert link.physical_medium_id is None
    assert link.link_loss_db is None


@pytest.mark.asyncio
async def test_multiple_links_with_different_fiber_types(async_session):
    """Test: Verschiedene Links können unterschiedliche Fiber Types haben"""
    fiber_types = ["G652D", "G657A1", "G657A2"]
    
    # Create devices
    devices = []
    for i in range(len(fiber_types) + 1):
        dev = Device(name=f"device_{i}", device_type=DeviceType.OLT)
        async_session.add(dev)
        devices.append(dev)
    await async_session.commit()
    
    # Create interfaces
    interfaces = []
    for idx, dev in enumerate(devices):
        iface = Interface(name=f"pon{idx}", interface_type=InterfaceType.OPTICAL, device_id=dev.id)
        async_session.add(iface)
        interfaces.append(iface)
    await async_session.commit()
    
    # Create links with different fiber types
    links = []
    for idx, fiber_type in enumerate(fiber_types):
        link = Link(
            a_interface_id=interfaces[idx].id,
            b_interface_id=interfaces[idx + 1].id,
            length_km=1.0 + idx,
            physical_medium_id=fiber_type,
        )
        async_session.add(link)
        links.append(link)
    await async_session.commit()
    
    # Verify all links have correct fiber types
    result = await async_session.execute(select(Link))
    db_links = result.scalars().all()
    assert len(db_links) == 3
    
    for link, expected_fiber in zip(db_links, fiber_types):
        assert link.physical_medium_id == expected_fiber
