"""
Test Provision API Endpoint

Phase 2.4: POST /api/devices/provision
"""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.mark.asyncio
async def test_provision_backbone_gateway_via_api(async_session, override_get_session):
    """Test: Provision BACKBONE_GATEWAY via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "backbone1",
                "device_type": "BACKBONE_GATEWAY",
                "x": 100.0,
                "y": 200.0,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "device" in data
        assert "interfaces" in data
        assert "message" in data
        
        device = data["device"]
        assert device["name"] == "backbone1"
        assert device["device_type"] == "BACKBONE_GATEWAY"
        
        # Check interfaces (mgmt0 + lo0)
        interfaces = data["interfaces"]
        assert len(interfaces) == 2
        interface_names = {iface["name"] for iface in interfaces}
        assert "mgmt0" in interface_names
        assert "lo0" in interface_names


@pytest.mark.asyncio
async def test_provision_olt_with_optical_attributes(async_session, override_get_session):
    """Test: Provision OLT with tx_power via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # First create upstream (CORE → EDGE)
        await client.post(
            "/api/devices/provision",
            json={
                "name": "core1",
                "device_type": "CORE_ROUTER",
            },
        )
        await client.post(
            "/api/devices/provision",
            json={
                "name": "edge1",
                "device_type": "EDGE_ROUTER",
            },
        )
        
        # Now provision OLT with optical attributes
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "olt1",
                "device_type": "OLT",
                "tx_power_dbm": 5.5,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        device = data["device"]
        assert device["tx_power_dbm"] == 5.5
        
        # Check PON interfaces
        interfaces = data["interfaces"]
        assert len(interfaces) == 10  # mgmt0 + lo0 + 8 PON


@pytest.mark.asyncio
async def test_provision_ont_without_upstream_fails(async_session, override_get_session):
    """Test: Provision ONT without OLT fails with 400"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "ont1",
                "device_type": "ONT",
            },
        )
        
        assert response.status_code == 400
        assert "No OLT exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_provision_ont_with_upstream_succeeds(async_session, override_get_session):
    """Test: Provision ONT with OLT upstream succeeds"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Create full chain: CORE → EDGE → OLT
        await client.post(
            "/api/devices/provision",
            json={"name": "core1", "device_type": "CORE_ROUTER"},
        )
        await client.post(
            "/api/devices/provision",
            json={"name": "edge1", "device_type": "EDGE_ROUTER"},
        )
        await client.post(
            "/api/devices/provision",
            json={"name": "olt1", "device_type": "OLT"},
        )
        
        # Now ONT should succeed
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "ont1",
                "device_type": "ONT",
                "sensitivity_min_dbm": -28.0,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        device = data["device"]
        assert device["sensitivity_min_dbm"] == -28.0
        
        # ONT has only 1 interface (eth0)
        interfaces = data["interfaces"]
        assert len(interfaces) == 1
        assert interfaces[0]["name"] == "eth0"


@pytest.mark.asyncio
async def test_provision_with_validation_bypass(async_session, override_get_session):
    """Test: Provision OLT without upstream using validate_upstream=False"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Provision OLT with validation bypass
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "olt1",
                "device_type": "OLT",
                "validate_upstream": False,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["device"]["name"] == "olt1"


@pytest.mark.asyncio
async def test_provision_duplicate_name_fails(async_session, override_get_session):
    """Test: Provision device with duplicate name fails"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Create first device
        response1 = await client.post(
            "/api/devices/provision",
            json={"name": "router1", "device_type": "CORE_ROUTER"},
        )
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = await client.post(
            "/api/devices/provision",
            json={"name": "router1", "device_type": "EDGE_ROUTER"},
        )
        
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_provision_with_parent_container(async_session, override_get_session):
    """Test: Provision device inside parent container"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Create POP container
        pop_response = await client.post(
            "/api/devices/provision",
            json={"name": "pop1", "device_type": "POP"},
        )
        pop_id = pop_response.json()["device"]["id"]
        
        # Create CORE with upstream
        await client.post(
            "/api/devices/provision",
            json={"name": "core1", "device_type": "CORE_ROUTER"},
        )
        await client.post(
            "/api/devices/provision",
            json={"name": "edge1", "device_type": "EDGE_ROUTER"},
        )
        
        # Create OLT inside POP
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "olt1",
                "device_type": "OLT",
                "parent_container_id": pop_id,
            },
        )
        
        assert response.status_code == 201
        device = response.json()["device"]
        assert device["parent_container_id"] == pop_id


@pytest.mark.asyncio
async def test_provision_passive_device_with_insertion_loss(async_session, override_get_session):
    """Test: Provision passive device (SPLITTER) with insertion_loss"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/devices/provision",
            json={
                "name": "splitter1",
                "device_type": "SPLITTER",
                "insertion_loss_db": 18.0,  # 1:32 splitter typical loss
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        device = data["device"]
        assert device["insertion_loss_db"] == 18.0
        
        # SPLITTER has 33 interfaces (in0 + out0-out31)
        interfaces = data["interfaces"]
        assert len(interfaces) == 33


@pytest.mark.asyncio
async def test_provision_full_topology_via_api(async_session, override_get_session):
    """Test: Provision complete topology via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # 1. BACKBONE_GATEWAY
        r1 = await client.post(
            "/api/devices/provision",
            json={"name": "backbone1", "device_type": "BACKBONE_GATEWAY"},
        )
        assert r1.status_code == 201
        
        # 2. CORE_ROUTER
        r2 = await client.post(
            "/api/devices/provision",
            json={"name": "core1", "device_type": "CORE_ROUTER"},
        )
        assert r2.status_code == 201
        
        # 3. EDGE_ROUTER
        r3 = await client.post(
            "/api/devices/provision",
            json={"name": "edge1", "device_type": "EDGE_ROUTER"},
        )
        assert r3.status_code == 201
        
        # 4. OLT
        r4 = await client.post(
            "/api/devices/provision",
            json={"name": "olt1", "device_type": "OLT"},
        )
        assert r4.status_code == 201
        
        # 5. AON_SWITCH
        r5 = await client.post(
            "/api/devices/provision",
            json={"name": "aon1", "device_type": "AON_SWITCH"},
        )
        assert r5.status_code == 201
        
        # 6. ONT
        r6 = await client.post(
            "/api/devices/provision",
            json={"name": "ont1", "device_type": "ONT"},
        )
        assert r6.status_code == 201
        
        # 7. AON_CPE
        r7 = await client.post(
            "/api/devices/provision",
            json={"name": "cpe1", "device_type": "AON_CPE"},
        )
        assert r7.status_code == 201
        
        # All 7 devices provisioned successfully


@pytest.mark.asyncio
async def test_provision_response_includes_message(async_session, override_get_session):
    """Test: Provision response includes success message"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/devices/provision",
            json={"name": "core1", "device_type": "CORE_ROUTER"},
        )
        
        data = response.json()
        assert "message" in data
        assert "provisioned successfully" in data["message"]
        assert "core1" in data["message"]
        assert "2 interfaces" in data["message"]  # mgmt0 + lo0


@pytest.mark.asyncio
async def test_provision_all_14_device_types(async_session, override_get_session):
    """Test: All 14 device types can be provisioned via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Create upstream dependencies first
        await client.post(
            "/api/devices/provision",
            json={"name": "core1", "device_type": "CORE_ROUTER"},
        )
        await client.post(
            "/api/devices/provision",
            json={"name": "edge1", "device_type": "EDGE_ROUTER"},
        )
        await client.post(
            "/api/devices/provision",
            json={"name": "olt1", "device_type": "OLT"},
        )
        await client.post(
            "/api/devices/provision",
            json={"name": "aon1", "device_type": "AON_SWITCH"},
        )
        
        # Now provision all types
        device_types = [
            "BACKBONE_GATEWAY",
            # "CORE_ROUTER",  # Already created
            # "EDGE_ROUTER",  # Already created
            # "OLT",  # Already created
            # "AON_SWITCH",  # Already created
            "ONT",
            "BUSINESS_ONT",
            "AON_CPE",
            "POP",
            "CORE_SITE",
            "ODF",
            "NVT",
            "SPLITTER",
            "HOP",
        ]
        
        for idx, device_type in enumerate(device_types):
            response = await client.post(
                "/api/devices/provision",
                json={
                    "name": f"test_{device_type.lower()}_{idx}",
                    "device_type": device_type,
                },
            )
            assert response.status_code == 201, f"Failed to provision {device_type}"
