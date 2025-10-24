"""
Seed Service - Demo Topology Generator

Creates a realistic network topology for testing.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.core import (
    Device,
    DeviceType,
    Interface,
    InterfaceType,
    Link,
    Status,
)


async def clear_all_data(session: AsyncSession) -> None:
    """Clear all data from database"""
    # Delete in correct order (FK constraints)
    await session.execute(text("DELETE FROM links"))
    await session.execute(text("DELETE FROM interfaces"))
    await session.execute(text("DELETE FROM devices"))
    await session.commit()


async def seed_demo_topology(session: AsyncSession) -> None:
    """
    Seed database with demo topology.
    
    Topology:
        Router1 ─── Switch1 ─── OLT1 ─┬─ ONT1
        Router2 ─── Switch2          ├─ ONT2
                                     ├─ ONT3
                                     └─ ONT4
    """
    print("🌱 Seeding demo topology...")
    
    # Check if data already exists
    result = await session.execute(select(Device))
    if result.scalars().first():
        print("⚠️  Data already exists, skipping seed")
        return
    
    # ===== CREATE DEVICES =====
    
    # Backbone & Core (top layer)
    backbone1 = Device(
        name="BackboneGW1",
        device_type=DeviceType.BACKBONE_GATEWAY,
        status=Status.UP,
        x=200,
        y=50,
    )
    core1 = Device(
        name="CoreRouter1",
        device_type=DeviceType.CORE_ROUTER,
        status=Status.UP,
        x=100,
        y=100,
    )
    core2 = Device(
        name="CoreRouter2",
        device_type=DeviceType.CORE_ROUTER,
        status=Status.UP,
        x=300,
        y=100,
    )
    
    # Edge Routers (middle layer)
    edge1 = Device(
        name="EdgeRouter1",
        device_type=DeviceType.EDGE_ROUTER,
        status=Status.UP,
        x=100,
        y=200,
    )
    edge2 = Device(
        name="EdgeRouter2",
        device_type=DeviceType.EDGE_ROUTER,
        status=Status.UP,
        x=300,
        y=200,
    )
    
    # OLT (distribution)
    olt1 = Device(
        name="OLT1",
        device_type=DeviceType.OLT,
        status=Status.UP,
        x=200,
        y=300,
        tx_power_dbm=5.0,
    )
    
    # ONTs (end devices)
    ont1 = Device(
        name="ONT1",
        device_type=DeviceType.ONT,
        status=Status.UP,
        x=100,
        y=400,
        sensitivity_min_dbm=-28.0,
    )
    ont2 = Device(
        name="ONT2",
        device_type=DeviceType.ONT,
        status=Status.UP,
        x=200,
        y=400,
    )
    ont3 = Device(
        name="ONT3",
        device_type=DeviceType.ONT,
        status=Status.UP,
        x=300,
        y=400,
        sensitivity_min_dbm=-28.0,
    )
    ont4 = Device(
        name="ONT4",
        device_type=DeviceType.ONT,
        status=Status.DEGRADED,  # One degraded device
        x=400,
        y=400,
        sensitivity_min_dbm=-28.0,
    )
    
    # Add all devices
    devices = [backbone1, core1, core2, edge1, edge2, olt1, ont1, ont2, ont3, ont4]
    for device in devices:
        session.add(device)
    
    await session.commit()
    
    # Refresh to get IDs
    for device in devices:
        await session.refresh(device)
    
    print(f"✅ Created {len(devices)} devices")
    
    # ===== CREATE INTERFACES =====
    
    interfaces = []
    
    # Backbone & Core interfaces
    for device in [backbone1, core1, core2]:
        interfaces.append(Interface(
            name="mgmt0",
            interface_type=InterfaceType.ETHERNET,
            device_id=device.id,
            status=Status.UP,
        ))
        interfaces.append(Interface(
            name="eth0",
            interface_type=InterfaceType.ETHERNET,
            device_id=device.id,
            status=Status.UP,
        ))
    
    # Edge routers interfaces
    for device in [edge1, edge2]:
        interfaces.append(Interface(
            name="mgmt0",
            interface_type=InterfaceType.ETHERNET,
            device_id=device.id,
            status=Status.UP,
        ))
        interfaces.append(Interface(
            name="eth0",
            interface_type=InterfaceType.ETHERNET,
            device_id=device.id,
            status=Status.UP,
        ))
    
    # OLT1 interfaces (optical)
    interfaces.append(Interface(
        name="mgmt0",
        interface_type=InterfaceType.ETHERNET,
        device_id=olt1.id,
        status=Status.UP,
    ))
    interfaces.append(Interface(
        name="eth0",  # Uplink to edge
        interface_type=InterfaceType.ETHERNET,
        device_id=olt1.id,
        status=Status.UP,
    ))
    for i in range(4):  # PON ports
        interfaces.append(Interface(
            name=f"pon0/{i}",
            interface_type=InterfaceType.OPTICAL,
            device_id=olt1.id,
            status=Status.UP,
        ))
    
    # ONT interfaces
    for ont in [ont1, ont2, ont3, ont4]:
        interfaces.append(Interface(
            name="pon0",
            interface_type=InterfaceType.OPTICAL,
            device_id=ont.id,
            status=ont.status,  # Match device status
        ))
        interfaces.append(Interface(
            name="eth0",
            interface_type=InterfaceType.ETHERNET,
            device_id=ont.id,
            status=ont.status,
        ))
    
    # Add all interfaces
    for interface in interfaces:
        session.add(interface)
    
    await session.commit()
    
    # Refresh to get IDs
    for interface in interfaces:
        await session.refresh(interface)
    
    print(f"✅ Created {len(interfaces)} interfaces")
    
    # ===== CREATE LINKS =====
    
    # Helper to find interface by device and name
    def find_interface(device: Device, name: str) -> Interface:
        for intf in interfaces:
            if intf.device_id == device.id and intf.name == name:
                return intf
        raise ValueError(f"Interface {name} not found on {device.name}")
    
    links = []
    
    # Backbone <-> Core1
    links.append(Link(
        a_interface_id=find_interface(backbone1, "eth0").id,
        b_interface_id=find_interface(core1, "eth0").id,
        status=Status.UP,
    ))
    
    # Core1 <-> Edge1
    links.append(Link(
        a_interface_id=find_interface(core1, "eth0").id,
        b_interface_id=find_interface(edge1, "eth0").id,
        status=Status.UP,
    ))
    
    # Core2 <-> Edge2
    links.append(Link(
        a_interface_id=find_interface(core2, "eth0").id,
        b_interface_id=find_interface(edge2, "eth0").id,
        status=Status.UP,
    ))
    
    # Edge1 <-> OLT1
    links.append(Link(
        a_interface_id=find_interface(edge1, "eth0").id,
        b_interface_id=find_interface(olt1, "eth0").id,
        status=Status.UP,
    ))
    
    # OLT1 <-> ONT1
    links.append(Link(
        a_interface_id=find_interface(olt1, "pon0/0").id,
        b_interface_id=find_interface(ont1, "pon0").id,
        status=Status.UP,
    ))
    
    # OLT1 <-> ONT2
    links.append(Link(
        a_interface_id=find_interface(olt1, "pon0/1").id,
        b_interface_id=find_interface(ont2, "pon0").id,
        status=Status.UP,
    ))
    
    # OLT1 <-> ONT3
    links.append(Link(
        a_interface_id=find_interface(olt1, "pon0/2").id,
        b_interface_id=find_interface(ont3, "pon0").id,
        status=Status.UP,
    ))
    
    # OLT1 <-> ONT4 (degraded)
    links.append(Link(
        a_interface_id=find_interface(olt1, "pon0/3").id,
        b_interface_id=find_interface(ont4, "pon0").id,
        status=Status.DEGRADED,
    ))
    
    # Add all links
    for link in links:
        session.add(link)
    
    await session.commit()
    
    print(f"✅ Created {len(links)} links")
    print("🌱 Demo topology seeded successfully!")


async def seed_if_empty(session: AsyncSession) -> None:
    """Seed database only if empty"""
    result = await session.execute(select(Device))
    if not result.scalars().first():
        await seed_demo_topology(session)
