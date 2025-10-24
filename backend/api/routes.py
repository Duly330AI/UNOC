"""
API Routes - Clean CRUD Operations
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.db import get_session
from backend.models.core import (
    Device,
    DeviceCreate,
    DeviceResponse,
    DeviceType,
    Interface,
    InterfaceCreate,
    InterfaceResponse,
    Link,
    LinkCreate,
    LinkResponse,
)
from backend.services.provisioning_service import ProvisioningError, ProvisioningService
from backend.services.seed import clear_all_data, seed_demo_topology

api_router = APIRouter()

# Import emit_to_all from main (circular import workaround via late import)
def get_emit_function():
    """Get emit_to_all function (lazy import to avoid circular dependency)"""
    from backend.main import emit_to_all
    return emit_to_all


# ==========================================
# PYDANTIC MODELS - PROVISIONING
# ==========================================


class ProvisionDeviceRequest(BaseModel):
    """Request model for provisioning a device"""
    
    name: str = Field(..., description="Unique device name")
    device_type: DeviceType = Field(..., description="Type of device to provision")
    parent_container_id: Optional[int] = Field(None, description="Optional parent container (POP, CORE_SITE)")
    validate_upstream: bool = Field(True, description="Validate upstream dependency (default: True)")
    x: float = Field(0.0, description="X coordinate for layout")
    y: float = Field(0.0, description="Y coordinate for layout")
    
    # Optical attributes (optional)
    tx_power_dbm: Optional[float] = Field(None, description="Transmit power in dBm (for OLT)")
    sensitivity_min_dbm: Optional[float] = Field(None, description="Minimum sensitivity in dBm (for ONT)")
    insertion_loss_db: Optional[float] = Field(None, description="Insertion loss in dB (for passive devices)")


class UpdateDevicePositionRequest(BaseModel):
    """Request model for updating device position (drag & drop)"""
    
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")


class SetStatusOverrideRequest(BaseModel):
    """Request model for setting manual status override"""
    
    status_override: str = Field(..., description="Override status: UP or DOWN")
    override_reason: str | None = Field(None, description="Optional reason for override")


class StatusOverrideRequest(BaseModel):
    """Request model for status override"""
    
    status: str = Field(..., description="Override status: UP, DOWN, or DEGRADED")
    reason: Optional[str] = Field(None, description="Optional reason for override")
    
    # Optical attributes (optional)
    tx_power_dbm: Optional[float] = Field(None, description="Transmit power in dBm (for OLT)")
    sensitivity_min_dbm: Optional[float] = Field(None, description="Minimum sensitivity in dBm (for ONT)")
    insertion_loss_db: Optional[float] = Field(None, description="Insertion loss in dB (for passive devices)")


class ProvisionDeviceResponse(BaseModel):
    """Response model for provisioned device with interfaces"""
    
    device: DeviceResponse
    interfaces: list[InterfaceResponse]
    message: str = Field(..., description="Success message")


# ==========================================
# DEVICES
# ==========================================


@api_router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(session: AsyncSession = Depends(get_session)):
    """List all devices"""
    result = await session.execute(select(Device))
    devices = result.scalars().all()
    return devices


@api_router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int, session: AsyncSession = Depends(get_session)):
    """Get single device"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@api_router.post("/devices/provision", response_model=ProvisionDeviceResponse, status_code=201)
async def provision_device(
    request: ProvisionDeviceRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Provision a device with proper initialization.
    
    This endpoint:
    1. Validates unique name
    2. Validates upstream dependency (if enabled)
    3. Creates device with optical attributes
    4. Auto-creates default interfaces based on device type
    5. Emits WebSocket event
    
    Phase 2.4: Provision API Endpoint
    """
    service = ProvisioningService(session)
    
    try:
        # Provision device using ProvisioningService
        device = await service.provision_device(
            name=request.name,
            device_type=request.device_type,
            parent_container_id=request.parent_container_id,
            validate_upstream=request.validate_upstream,
            x=request.x,
            y=request.y,
            tx_power_dbm=request.tx_power_dbm,
            sensitivity_min_dbm=request.sensitivity_min_dbm,
            insertion_loss_db=request.insertion_loss_db,
        )
        
        # Get interfaces
        interfaces = await service.get_device_interfaces(device.id)
        
        # Emit WebSocket event
        emit = get_emit_function()
        await emit("device_created", {
            "device_id": device.id,
            "name": device.name,
            "device_type": device.device_type.value,
            "interface_count": len(interfaces),
        })
        
        return ProvisionDeviceResponse(
            device=DeviceResponse.model_validate(device),
            interfaces=[InterfaceResponse.model_validate(iface) for iface in interfaces],
            message=f"Device '{device.name}' provisioned successfully with {len(interfaces)} interfaces",
        )
    
    except ProvisioningError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/devices", response_model=DeviceResponse, status_code=201)
async def create_device(
    device_data: DeviceCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create new device"""
    device = Device(**device_data.model_dump())
    session.add(device)
    await session.commit()
    await session.refresh(device)
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:created", {
        "id": device.id,
        "name": device.name,
        "device_type": device.device_type,
        "status": device.status,
        "x": device.x,
        "y": device.y,
    })
    
    return device


@api_router.patch("/devices/{device_id}")
async def update_device_position(
    device_id: int,
    data: UpdateDevicePositionRequest,
    session: AsyncSession = Depends(get_session)
):
    """Update device position (for drag & drop) - NO WebSocket broadcast to avoid conflicts"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.x = data.x
    device.y = data.y
    
    await session.commit()
    
    # NOTE: No WebSocket event emitted for position updates to prevent
    # conflicting drag operations between clients. Each client maintains
    # its own visual position, synced only on page reload.
    
    return {"message": f"Device position updated to ({data.x}, {data.y})"}


@api_router.patch("/devices/{device_id}/override")
async def set_device_status_override(
    device_id: int,
    data: SetStatusOverrideRequest,
    session: AsyncSession = Depends(get_session)
):
    """Set manual status override for a device"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Validate status override value
    if data.status_override not in ["UP", "DOWN"]:
        raise HTTPException(status_code=400, detail="status_override must be 'UP' or 'DOWN'")
    
    device.status_override = data.status_override
    device.override_reason = data.override_reason
    
    await session.commit()
    await session.refresh(device)
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:updated", device.model_dump(mode='json'))
    
    return {
        "message": f"Status override set to {data.status_override}",
        "device": device.model_dump()
    }


@api_router.delete("/devices/{device_id}/override")
async def clear_device_status_override(
    device_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Clear manual status override for a device"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.status_override = None
    device.override_reason = None
    
    await session.commit()
    await session.refresh(device)
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:updated", device.model_dump(mode='json'))
    
    return {
        "message": "Status override cleared",
        "device": device.model_dump()
    }


@api_router.get("/devices/{device_id}/interfaces", response_model=list[InterfaceResponse])
async def get_device_interfaces(
    device_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all interfaces for a specific device"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    result = await session.execute(
        select(Interface).where(Interface.device_id == device_id)
    )
    interfaces = result.scalars().all()
    return interfaces
    
    await session.commit()
    await session.refresh(device)
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:updated", device.model_dump(mode='json'))
    
    return {
        "message": "Status override cleared",
        "device": device.model_dump()
    }


@api_router.post("/devices/{device_id}/override-status")
async def override_device_status(
    device_id: int,
    data: StatusOverrideRequest,
    session: AsyncSession = Depends(get_session)
):
    """Set manual status override for a device"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Validate status
    valid_statuses = ["UP", "DOWN", "DEGRADED"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    device.status_override = data.status
    device.override_reason = data.reason
    
    await session.commit()
    await session.refresh(device)
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:updated", device.model_dump(mode='json'))
    
    return {
        "message": f"Status override set to {data.status}",
        "device": device.model_dump()
    }


@api_router.delete("/devices/{device_id}/override-status")
async def clear_device_status_override(
    device_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Clear manual status override"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.status_override = None
    device.override_reason = None
    
    await session.commit()
    await session.refresh(device)
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:updated", device.model_dump(mode='json'))
    
    return {
        "message": "Status override cleared",
        "device": device.model_dump()
    }


@api_router.delete("/devices/{device_id}", status_code=204)
async def delete_device(device_id: int, session: AsyncSession = Depends(get_session)):
    """Delete device (CASCADE deletes interfaces and links)"""
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Store ID before deleting
    deleted_id = device.id
    
    await session.delete(device)
    await session.commit()
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("device:deleted", {"id": deleted_id})
    
    return None


# ==========================================
# INTERFACES
# ==========================================


@api_router.get("/interfaces", response_model=list[InterfaceResponse])
async def list_interfaces(session: AsyncSession = Depends(get_session)):
    """List all interfaces"""
    result = await session.execute(select(Interface))
    interfaces = result.scalars().all()
    return interfaces


@api_router.post("/interfaces", response_model=InterfaceResponse, status_code=201)
async def create_interface(
    interface_data: InterfaceCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create new interface"""
    # Check device exists
    device = await session.get(Device, interface_data.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    interface = Interface(**interface_data.model_dump())
    session.add(interface)
    await session.commit()
    await session.refresh(interface)
    return interface


# ==========================================
# LINKS
# ==========================================


@api_router.get("/links", response_model=list[LinkResponse])
async def list_links(session: AsyncSession = Depends(get_session)):
    """List all links"""
    result = await session.execute(select(Link))
    links = result.scalars().all()
    return links


@api_router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(link_id: int, session: AsyncSession = Depends(get_session)):
    """Get single link"""
    link = await session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@api_router.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(
    link_data: LinkCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create new link"""
    # Check interfaces exist
    intf_a = await session.get(Interface, link_data.a_interface_id)
    intf_b = await session.get(Interface, link_data.b_interface_id)
    
    if not intf_a or not intf_b:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    link = Link(**link_data.model_dump())
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link


@api_router.delete("/links/{link_id}", status_code=204)
async def delete_link(link_id: int, session: AsyncSession = Depends(get_session)):
    """Delete link"""
    link = await session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    deleted_id = link.id
    
    await session.delete(link)
    await session.commit()
    
    # Emit WebSocket event
    emit = get_emit_function()
    await emit("link:deleted", {"id": deleted_id})
    
    return None


# ==========================================
# SIMPLE LINK CREATION (with auto-interface)
# ==========================================


class SimpleLinkCreate(BaseModel):
    device_a_id: int
    device_b_id: int
    link_type: str  # "fiber", "copper", "wireless"
    status: str = "UP"


@api_router.post("/links/create-simple")
async def create_simple_link(
    data: SimpleLinkCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a link between two devices with automatic interface creation.
    
    This is a convenience endpoint that:
    1. Creates an interface on device A
    2. Creates an interface on device B
    3. Creates a link between those interfaces
    4. Emits WebSocket events for real-time updates
    """
    # Validate devices exist
    device_a = await session.get(Device, data.device_a_id)
    device_b = await session.get(Device, data.device_b_id)
    
    if not device_a:
        raise HTTPException(status_code=404, detail=f"Device A (id={data.device_a_id}) not found")
    if not device_b:
        raise HTTPException(status_code=404, detail=f"Device B (id={data.device_b_id}) not found")
    
    # Don't allow linking device to itself
    if device_a.id == device_b.id:
        raise HTTPException(status_code=400, detail="Cannot link device to itself")
    
    # Map link_type to interface_type
    # Available types: ETHERNET, OPTICAL, LOOPBACK
    interface_type_map = {
        "fiber": "OPTICAL",
        "copper": "ETHERNET",
        "wireless": "ETHERNET"  # Wireless doesn't exist, map to ETHERNET
    }
    interface_type = interface_type_map.get(data.link_type, "ETHERNET")
    
    # Create interface on device A
    result_a = await session.execute(
        select(Interface).where(Interface.device_id == device_a.id)
    )
    existing_interfaces_a = result_a.scalars().all()
    next_port_a = len(existing_interfaces_a) + 1
    
    interface_a = Interface(
        name=f"port{next_port_a}",
        device_id=device_a.id,
        interface_type=interface_type,
        status="UP"
    )
    session.add(interface_a)
    await session.flush()  # Get ID without committing
    
    # Create interface on device B
    result_b = await session.execute(
        select(Interface).where(Interface.device_id == device_b.id)
    )
    existing_interfaces_b = result_b.scalars().all()
    next_port_b = len(existing_interfaces_b) + 1
    
    interface_b = Interface(
        name=f"port{next_port_b}",
        device_id=device_b.id,
        interface_type=interface_type,
        status="UP"
    )
    session.add(interface_b)
    await session.flush()  # Get ID without committing
    
    # Create link
    link = Link(
        a_interface_id=interface_a.id,
        b_interface_id=interface_b.id,
        status=data.status
    )
    session.add(link)
    await session.commit()
    await session.refresh(link)
    await session.refresh(interface_a)
    await session.refresh(interface_b)
    
    # Emit WebSocket events (use mode='json' to serialize datetime)
    emit = get_emit_function()
    await emit("interface:created", interface_a.model_dump(mode='json'))
    await emit("interface:created", interface_b.model_dump(mode='json'))
    await emit("link:created", link.model_dump(mode='json'))
    
    return {
        "link": link.model_dump(),
        "interface_a": interface_a.model_dump(),
        "interface_b": interface_b.model_dump(),
        "message": f"Link created: {device_a.name} ({interface_a.name}) <-> {device_b.name} ({interface_b.name})"
    }


# ==========================================
# SEED / DEMO DATA
# ==========================================


@api_router.post("/seed", status_code=201)
async def seed_database(session: AsyncSession = Depends(get_session)):
    """Clear database and seed with demo topology"""
    await clear_all_data(session)
    await seed_demo_topology(session)
    return {"message": "Database seeded successfully"}
