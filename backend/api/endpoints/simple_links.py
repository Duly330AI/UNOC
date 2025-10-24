"""
Simple link creation endpoint that handles interface auto-creation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from backend.db import get_session
from backend.models import Device, Interface, Link
from backend.events import emit_event

router = APIRouter()


class SimpleLinkCreate(BaseModel):
    device_a_id: int
    device_b_id: int
    link_type: str  # "fiber", "copper", "wireless"
    status: str = "UP"


@router.post("/links/create-simple")
def create_simple_link(
    data: SimpleLinkCreate,
    session: Session = Depends(get_session)
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
    device_a = session.get(Device, data.device_a_id)
    device_b = session.get(Device, data.device_b_id)
    
    if not device_a:
        raise HTTPException(status_code=404, detail=f"Device A (id={data.device_a_id}) not found")
    if not device_b:
        raise HTTPException(status_code=404, detail=f"Device B (id={data.device_b_id}) not found")
    
    # Don't allow linking device to itself
    if device_a.id == device_b.id:
        raise HTTPException(status_code=400, detail="Cannot link device to itself")
    
    # Map link_type to interface_type
    interface_type_map = {
        "fiber": "FIBER",
        "copper": "ETHERNET",
        "wireless": "WIRELESS"
    }
    interface_type = interface_type_map.get(data.link_type, "ETHERNET")
    
    # Create interface on device A
    # Find next available port number
    existing_interfaces_a = session.exec(
        select(Interface).where(Interface.device_id == device_a.id)
    ).all()
    next_port_a = len(existing_interfaces_a) + 1
    
    interface_a = Interface(
        name=f"port{next_port_a}",
        device_id=device_a.id,
        interface_type=interface_type,
        status="UP"
    )
    session.add(interface_a)
    session.flush()  # Get ID without committing
    
    # Create interface on device B
    existing_interfaces_b = session.exec(
        select(Interface).where(Interface.device_id == device_b.id)
    ).all()
    next_port_b = len(existing_interfaces_b) + 1
    
    interface_b = Interface(
        name=f"port{next_port_b}",
        device_id=device_b.id,
        interface_type=interface_type,
        status="UP"
    )
    session.add(interface_b)
    session.flush()  # Get ID without committing
    
    # Create link
    link = Link(
        a_interface_id=interface_a.id,
        b_interface_id=interface_b.id,
        status=data.status
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    session.refresh(interface_a)
    session.refresh(interface_b)
    
    # Emit WebSocket events
    emit_event("interface:created", interface_a.model_dump())
    emit_event("interface:created", interface_b.model_dump())
    emit_event("link:created", link.model_dump())
    
    return {
        "link": link.model_dump(),
        "interface_a": interface_a.model_dump(),
        "interface_b": interface_b.model_dump(),
        "message": f"Link created: {device_a.name} ({interface_a.name}) <-> {device_b.name} ({interface_b.name})"
    }
