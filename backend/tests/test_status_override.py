"""
Tests for Status Override functionality
Phase 3 Part 2 - Oct 15, 2025
"""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.mark.asyncio
async def test_set_status_override_up(async_session, override_get_session):
    """Test setting status override to UP"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Create a device first
        device_data = {
            "name": "TestDevice",
            "device_type": "EDGE_ROUTER",
            "status": "DOWN",
            "x": 100,
            "y": 100
        }
        resp = await client.post("/api/devices", json=device_data)
        assert resp.status_code == 201
        device = resp.json()
        device_id = device["id"]
        
        # Set override to UP
        override_data = {
            "status_override": "UP",
            "override_reason": "Manual override for testing"
        }
        resp = await client.patch(f"/api/devices/{device_id}/override", json=override_data)
        assert resp.status_code == 200
        result = resp.json()
        
        assert result["message"] == "Status override set to UP"
        assert result["device"]["status_override"] == "UP"
        assert result["device"]["override_reason"] == "Manual override for testing"


@pytest.mark.asyncio
async def test_set_status_override_down(async_session, override_get_session):
    """Test setting status override to DOWN"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        device_data = {
            "name": "TestDevice2",
            "device_type": "OLT",
            "status": "UP",
            "x": 200,
            "y": 200
        }
        resp = await client.post("/api/devices", json=device_data)
        assert resp.status_code == 201
        device = resp.json()
        device_id = device["id"]
        
        # Set override to DOWN
        override_data = {
            "status_override": "DOWN",
            "override_reason": "Maintenance window"
        }
        resp = await client.patch(f"/api/devices/{device_id}/override", json=override_data)
        assert resp.status_code == 200
        result = resp.json()
        
        assert result["message"] == "Status override set to DOWN"
        assert result["device"]["status_override"] == "DOWN"
        assert result["device"]["override_reason"] == "Maintenance window"


@pytest.mark.asyncio
async def test_clear_status_override(async_session, override_get_session):
    """Test clearing status override"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # Create device with override
        device_data = {
            "name": "TestDevice3",
            "device_type": "ONT",
            "status": "UP",
            "x": 300,
            "y": 300
        }
        resp = await client.post("/api/devices", json=device_data)
        device_id = resp.json()["id"]
        
        # Set override
        override_data = {
            "status_override": "DOWN",
            "override_reason": "Test override"
        }
        await client.patch(f"/api/devices/{device_id}/override", json=override_data)
        
        # Clear override
        resp = await client.delete(f"/api/devices/{device_id}/override")
        assert resp.status_code == 200
        result = resp.json()
        
        assert result["message"] == "Status override cleared"
        assert result["device"]["status_override"] is None
        assert result["device"]["override_reason"] is None


@pytest.mark.asyncio
async def test_override_invalid_status(async_session, override_get_session):
    """Test that invalid status override is rejected"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        device_data = {
            "name": "TestDevice4",
            "device_type": "CORE_ROUTER",
            "status": "UP",
            "x": 400,
            "y": 400
        }
        resp = await client.post("/api/devices", json=device_data)
        device_id = resp.json()["id"]
        
        # Try invalid override
        override_data = {
            "status_override": "INVALID",
            "override_reason": "Test"
        }
        resp = await client.patch(f"/api/devices/{device_id}/override", json=override_data)
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_override_nonexistent_device(async_session, override_get_session):
    """Test override on non-existent device returns 404"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        override_data = {
            "status_override": "UP",
            "override_reason": "Test"
        }
        resp = await client.patch("/api/devices/99999/override", json=override_data)
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_clear_override_nonexistent_device(async_session, override_get_session):
    """Test clear override on non-existent device returns 404"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.delete("/api/devices/99999/override")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_override_without_reason(async_session, override_get_session):
    """Test that override works without reason (optional field)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        device_data = {
            "name": "TestDevice5",
            "device_type": "ONT",
            "status": "UP",
            "x": 500,
            "y": 500
        }
        resp = await client.post("/api/devices", json=device_data)
        device_id = resp.json()["id"]
        
        # Set override without reason
        override_data = {
            "status_override": "DOWN"
        }
        resp = await client.patch(f"/api/devices/{device_id}/override", json=override_data)
        assert resp.status_code == 200
        result = resp.json()
        
        assert result["device"]["status_override"] == "DOWN"
        assert result["device"]["override_reason"] is None


@pytest.mark.asyncio
async def test_override_preserves_other_fields(async_session, override_get_session):
    """Test that override doesn't modify other device fields"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        device_data = {
            "name": "TestDevice6",
            "device_type": "OLT",
            "status": "UP",
            "x": 600,
            "y": 600
        }
        resp = await client.post("/api/devices", json=device_data)
        device = resp.json()
        device_id = device["id"]
        
        original_name = device["name"]
        original_type = device["device_type"]
        original_x = device["x"]
        original_y = device["y"]
        
        # Set override
        override_data = {
            "status_override": "DOWN",
            "override_reason": "Test"
        }
        resp = await client.patch(f"/api/devices/{device_id}/override", json=override_data)
        updated_device = resp.json()["device"]
        
        # Check other fields unchanged
        assert updated_device["name"] == original_name
        assert updated_device["device_type"] == original_type
        assert updated_device["x"] == original_x
        assert updated_device["y"] == original_y
        assert updated_device["status_override"] == "DOWN"
