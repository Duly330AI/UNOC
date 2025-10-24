"""
Test API Responses - Verify all new fields are returned

Phase 1.6: API Response Models Testing
"""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.models.core import Device, DeviceType, Interface, InterfaceType, Link


@pytest.mark.asyncio
async def test_device_response_includes_optical_attributes(async_session, override_get_session):
    """Test: GET /devices/{id} includes all optical attributes"""
    # Create OLT with tx_power_dbm
    olt = Device(
        name="test_olt_api",
        device_type=DeviceType.OLT,
        tx_power_dbm=5.5,
        x=100.0,
        y=200.0,
    )
    async_session.add(olt)
    await async_session.commit()
    await async_session.refresh(olt)
    
    # Test API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/devices/{olt.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all fields present
    assert data["id"] == olt.id
    assert data["name"] == "test_olt_api"
    assert data["device_type"] == "OLT"
    assert data["status"] == "DOWN"
    assert data["x"] == 100.0
    assert data["y"] == 200.0
    
    # Verify optical attributes
    assert "tx_power_dbm" in data
    assert data["tx_power_dbm"] == 5.5
    assert "sensitivity_min_dbm" in data
    assert data["sensitivity_min_dbm"] is None
    assert "insertion_loss_db" in data
    assert data["insertion_loss_db"] is None
    assert "parent_container_id" in data
    assert data["parent_container_id"] is None


@pytest.mark.asyncio
async def test_device_list_includes_optical_attributes(async_session, override_get_session):
    """Test: GET /devices includes optical attributes for all devices"""
    # Create diverse devices
    devices_data = [
        ("olt1", DeviceType.OLT, {"tx_power_dbm": 5.0}),
        ("ont1", DeviceType.ONT, {"sensitivity_min_dbm": -28.0}),
        ("odf1", DeviceType.ODF, {"insertion_loss_db": 0.5}),
        ("pop1", DeviceType.POP, {}),
    ]
    
    created_ids = []
    for name, dev_type, attrs in devices_data:
        device = Device(name=name, device_type=dev_type, **attrs)
        async_session.add(device)
        await async_session.commit()
        await async_session.refresh(device)
        created_ids.append(device.id)
    
    # Test API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/devices")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    
    # Verify OLT has tx_power_dbm
    olt_data = next(d for d in data if d["name"] == "olt1")
    assert olt_data["tx_power_dbm"] == 5.0
    assert olt_data["sensitivity_min_dbm"] is None
    
    # Verify ONT has sensitivity_min_dbm
    ont_data = next(d for d in data if d["name"] == "ont1")
    assert ont_data["sensitivity_min_dbm"] == -28.0
    assert ont_data["tx_power_dbm"] is None
    
    # Verify ODF has insertion_loss_db
    odf_data = next(d for d in data if d["name"] == "odf1")
    assert odf_data["insertion_loss_db"] == 0.5


@pytest.mark.asyncio
async def test_device_create_accepts_optical_attributes(async_session, override_get_session):
    """Test: POST /devices accepts optical attributes"""
    # Create OLT with tx_power_dbm via API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/devices",
            json={
                "name": "olt_via_api",
                "device_type": "OLT",
                "x": 50.0,
                "y": 75.0,
                "tx_power_dbm": 6.0,
            },
        )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["name"] == "olt_via_api"
    assert data["tx_power_dbm"] == 6.0
    assert data["sensitivity_min_dbm"] is None


@pytest.mark.asyncio
async def test_link_response_includes_optical_attributes(async_session, override_get_session):
    """Test: GET /links/{id} includes all optical attributes"""
    # Create devices and interfaces
    dev1 = Device(name="dev1", device_type=DeviceType.OLT)
    dev2 = Device(name="dev2", device_type=DeviceType.ONT)
    async_session.add(dev1)
    async_session.add(dev2)
    await async_session.commit()
    
    if1 = Interface(name="pon0", interface_type=InterfaceType.OPTICAL, device_id=dev1.id)
    if2 = Interface(name="eth0", interface_type=InterfaceType.OPTICAL, device_id=dev2.id)
    async_session.add(if1)
    async_session.add(if2)
    await async_session.commit()
    
    # Create link with optical attributes
    link = Link(
        a_interface_id=if1.id,
        b_interface_id=if2.id,
        length_km=2.5,
        physical_medium_id="G652D",
        link_loss_db=1.25,
    )
    async_session.add(link)
    await async_session.commit()
    await async_session.refresh(link)
    
    # Test API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/links/{link.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all fields
    assert data["id"] == link.id
    assert data["status"] == "DOWN"
    assert data["a_interface_id"] == if1.id
    assert data["b_interface_id"] == if2.id
    
    # Verify optical attributes
    assert "length_km" in data
    assert data["length_km"] == 2.5
    assert "physical_medium_id" in data
    assert data["physical_medium_id"] == "G652D"
    assert "link_loss_db" in data
    assert data["link_loss_db"] == 1.25


@pytest.mark.asyncio
async def test_link_list_includes_optical_attributes(async_session, override_get_session):
    """Test: GET /links includes optical attributes"""
    # Create devices and interfaces
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
    
    # Create link
    link = Link(
        a_interface_id=if1.id,
        b_interface_id=if2.id,
        length_km=10.0,
        physical_medium_id="G657A2",
    )
    async_session.add(link)
    await async_session.commit()
    
    # Test API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/links")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    link_data = data[0]
    assert link_data["length_km"] == 10.0
    assert link_data["physical_medium_id"] == "G657A2"


@pytest.mark.asyncio
async def test_link_create_accepts_optical_attributes(async_session, override_get_session):
    """Test: POST /links accepts optical attributes"""
    # Create devices and interfaces
    dev1 = Device(name="olt_create", device_type=DeviceType.OLT)
    dev2 = Device(name="ont_create", device_type=DeviceType.ONT)
    async_session.add(dev1)
    async_session.add(dev2)
    await async_session.commit()
    
    if1 = Interface(name="pon0", interface_type=InterfaceType.OPTICAL, device_id=dev1.id)
    if2 = Interface(name="eth0", interface_type=InterfaceType.OPTICAL, device_id=dev2.id)
    async_session.add(if1)
    async_session.add(if2)
    await async_session.commit()
    
    # Create link via API with optical attributes
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/links",
            json={
                "a_interface_id": if1.id,
                "b_interface_id": if2.id,
                "length_km": 3.5,
                "physical_medium_id": "G652D",
            },
        )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["length_km"] == 3.5
    assert data["physical_medium_id"] == "G652D"
    assert data["link_loss_db"] is None  # Not computed yet


@pytest.mark.asyncio
async def test_container_hierarchy_in_device_response(async_session, override_get_session):
    """Test: parent_container_id is included in device response"""
    # Create POP container
    pop = Device(name="pop_parent", device_type=DeviceType.POP)
    async_session.add(pop)
    await async_session.commit()
    await async_session.refresh(pop)
    
    # Create OLT inside POP via API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/devices",
            json={
                "name": "olt_in_pop",
                "device_type": "OLT",
                "parent_container_id": pop.id,
            },
        )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["name"] == "olt_in_pop"
    assert data["parent_container_id"] == pop.id
    
    # Verify GET also returns parent_container_id
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        get_response = await client.get(f"/api/devices/{data['id']}")
    
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["parent_container_id"] == pop.id
