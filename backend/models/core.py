"""
UNOC Backend - Clean Architecture V2

Core Models - Single Source of Truth
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# ==========================================
# ENUMS - Keep it Simple!
# ==========================================


class Status(str, Enum):
    """Device/Link Status - ONLY 3 VALUES!"""

    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"


class DeviceType(str, Enum):
    """
    Device Types - 13 Total
    
    ACTIVE DEVICES:
    - BACKBONE_GATEWAY: Always-online root anchor
    - CORE_ROUTER: Core network router
    - EDGE_ROUTER: Edge/distribution router
    - OLT: Optical Line Terminal (GPON)
    - AON_SWITCH: Active Optical Network switch
    - ONT: Optical Network Terminal (residential)
    - BUSINESS_ONT: Business-grade ONT
    - AON_CPE: AON Customer Premise Equipment
    
    CONTAINER DEVICES:
    - POP: Point of Presence (physical enclosure)
    - CORE_SITE: Core site container
    
    PASSIVE DEVICES:
    - ODF: Optical Distribution Frame
    - NVT: Network Termination Vault
    - SPLITTER: Optical splitter (1:N)
    - HOP: Handhole Optical Point
    """
    
    # Active Devices
    BACKBONE_GATEWAY = "BACKBONE_GATEWAY"
    CORE_ROUTER = "CORE_ROUTER"
    EDGE_ROUTER = "EDGE_ROUTER"
    OLT = "OLT"
    AON_SWITCH = "AON_SWITCH"
    ONT = "ONT"
    BUSINESS_ONT = "BUSINESS_ONT"
    AON_CPE = "AON_CPE"
    
    # Container Devices
    POP = "POP"
    CORE_SITE = "CORE_SITE"
    
    # Passive Devices (inline)
    ODF = "ODF"
    NVT = "NVT"
    SPLITTER = "SPLITTER"
    HOP = "HOP"


class InterfaceType(str, Enum):
    """Interface Types"""

    ETHERNET = "ETHERNET"
    OPTICAL = "OPTICAL"
    LOOPBACK = "LOOPBACK"


# ==========================================
# CORE MODELS
# ==========================================


class Device(SQLModel, table=True):
    """
    Device Model - Extended with Optical Attributes
    
    ONE status field. Optical attributes for signal budget calculation.
    """

    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    device_type: DeviceType
    status: Status = Field(default=Status.DOWN)
    
    # Status Override (manual override by admin)
    status_override: Optional[Status] = Field(default=None)
    override_reason: Optional[str] = Field(default=None, max_length=255)
    
    # Optical Attributes (nullable - only for relevant types)
    tx_power_dbm: Optional[float] = Field(default=None)  # OLT transmit power
    sensitivity_min_dbm: Optional[float] = Field(default=None)  # ONT minimum sensitivity
    insertion_loss_db: Optional[float] = Field(default=None)  # Passive device loss
    
    # Container relationship (nullable - for containment hierarchy)
    parent_container_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    
    # Location
    x: float = Field(default=0.0)
    y: float = Field(default=0.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    interfaces: list["Interface"] = Relationship(
        back_populates="device",
        cascade_delete=True,
    )


class Interface(SQLModel, table=True):
    """Network Interface - Ports on Devices"""

    __tablename__ = "interfaces"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g. "eth0", "ge-0/0/0"
    interface_type: InterfaceType
    status: Status = Field(default=Status.DOWN)
    
    # Foreign Keys
    device_id: int = Field(foreign_key="devices.id", ondelete="CASCADE")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    device: Device = Relationship(back_populates="interfaces")
    
    # Links (as endpoint A or B)
    links_as_a: list["Link"] = Relationship(
        back_populates="interface_a",
        sa_relationship_kwargs={"foreign_keys": "[Link.a_interface_id]"},
    )
    links_as_b: list["Link"] = Relationship(
        back_populates="interface_b",
        sa_relationship_kwargs={"foreign_keys": "[Link.b_interface_id]"},
    )


class Link(SQLModel, table=True):
    """
    Link between two Interfaces
    
    Extended with optical attributes for signal budget calculation.
    """

    __tablename__ = "links"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: Status = Field(default=Status.DOWN)
    
    # Optical Attributes
    length_km: Optional[float] = Field(default=None)  # Physical length in kilometers
    physical_medium_id: Optional[str] = Field(default=None)  # Fiber type code (e.g., "G652D")
    link_loss_db: Optional[float] = Field(default=None)  # Computed total loss
    
    # Endpoints
    a_interface_id: int = Field(foreign_key="interfaces.id", ondelete="CASCADE")
    b_interface_id: int = Field(foreign_key="interfaces.id", ondelete="CASCADE")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    interface_a: Interface = Relationship(
        back_populates="links_as_a",
        sa_relationship_kwargs={"foreign_keys": "[Link.a_interface_id]"},
    )
    interface_b: Interface = Relationship(
        back_populates="links_as_b",
        sa_relationship_kwargs={"foreign_keys": "[Link.b_interface_id]"},
    )


# ==========================================
# RESPONSE MODELS (for API)
# ==========================================


class DeviceResponse(SQLModel):
    """Device Response - What Frontend Gets"""

    id: int
    name: str
    device_type: DeviceType
    status: Status  # ← ONLY ONE!
    x: float
    y: float
    
    # Optical Attributes (nullable)
    tx_power_dbm: Optional[float] = None
    sensitivity_min_dbm: Optional[float] = None
    insertion_loss_db: Optional[float] = None
    parent_container_id: Optional[int] = None


class InterfaceResponse(SQLModel):
    """Interface Response"""

    id: int
    name: str
    interface_type: InterfaceType
    status: Status
    device_id: int


class LinkResponse(SQLModel):
    """Link Response"""

    id: int
    status: Status
    a_interface_id: int
    b_interface_id: int
    
    # Optical Attributes
    length_km: Optional[float] = None
    physical_medium_id: Optional[str] = None
    link_loss_db: Optional[float] = None


# ==========================================
# CREATE MODELS (for API)
# ==========================================


class DeviceCreate(SQLModel):
    """Create Device Request"""

    name: str
    device_type: DeviceType
    x: float = 0.0
    y: float = 0.0
    
    # Optional Optical Attributes
    tx_power_dbm: Optional[float] = None
    sensitivity_min_dbm: Optional[float] = None
    insertion_loss_db: Optional[float] = None
    parent_container_id: Optional[int] = None


class InterfaceCreate(SQLModel):
    """Create Interface Request"""

    name: str
    interface_type: InterfaceType
    device_id: int


class LinkCreate(SQLModel):
    """Create Link Request"""

    a_interface_id: int
    b_interface_id: int
    
    # Optional Optical Attributes
    length_km: Optional[float] = None
    physical_medium_id: Optional[str] = None
