"""
Provisioning Service - Core Logic for Device Provisioning

PHASE 2: PROVISIONING
=====================

CONCEPT:
--------
Provisioning = Process of preparing a device for active operation:
1. Create device in DB with required attributes
2. Create default interfaces (mgmt0, etc.)
3. Assign management IP from pool (IPAM Phase 3)
4. Validate dependencies (upstream connectivity)
5. Set initial status

PROVISIONING MATRIX:
-------------------
Device Type          | Requires Parent? | Auto Interfaces  | Management IP
---------------------|------------------|------------------|---------------
BACKBONE_GATEWAY     | No               | mgmt0, lo0       | Yes
CORE_ROUTER          | No               | mgmt0, lo0       | Yes
EDGE_ROUTER          | Yes (CORE)       | mgmt0, lo0       | Yes
OLT                  | Yes (POP/EDGE)   | mgmt0, pon0-7    | Yes
AON_SWITCH           | Yes (POP/EDGE)   | mgmt0, eth0-23   | Yes
ONT                  | Yes (OLT)        | eth0             | No (uses OLT)
BUSINESS_ONT         | Yes (OLT)        | eth0-3           | Optional
AON_CPE              | Yes (AON_SWITCH) | wan0, lan0-3     | No
POP                  | No               | -                | No (container)
CORE_SITE            | No               | -                | No (container)
ODF                  | Optional         | port1-48         | No (passive)
NVT                  | Optional         | port1-12         | No (passive)
SPLITTER             | Optional         | in0, out0-31     | No (passive)
HOP                  | Optional         | port1-8          | No (passive)

LINK TYPE RULES (L1-L9):
------------------------
Will be implemented in Phase 2.2 - constants/link_rules.py
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.core import Device, DeviceType, Interface, InterfaceType, Status


class ProvisioningError(Exception):
    """Raised when provisioning fails"""
    pass


class ProvisioningService:
    """
    Service for provisioning devices with proper configuration.
    
    Phase 2.1: Basic skeleton with interface creation
    Phase 2.2: Link type validation
    Phase 2.3: Dependency validation (upstream connectivity)
    Phase 2.4: IPAM integration (Phase 3)
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def provision_device(
        self,
        name: str,
        device_type: DeviceType,
        parent_container_id: Optional[int] = None,
        validate_upstream: bool = True,
        x: float = 0.0,
        y: float = 0.0,
        **optical_attrs,
    ) -> Device:
        """
        Provision a device with proper initialization.
        
        Args:
            name: Device name (must be unique)
            device_type: Type of device
            parent_container_id: Optional parent container (POP, CORE_SITE)
            validate_upstream: Whether to validate upstream dependency (default True)
            x, y: Coordinates
            **optical_attrs: tx_power_dbm, sensitivity_min_dbm, insertion_loss_db
        
        Returns:
            Provisioned device with interfaces
        
        Raises:
            ProvisioningError: If provisioning fails
        """
        # Check if name already exists
        existing = await self._check_name_exists(name)
        if existing:
            raise ProvisioningError(f"Device with name '{name}' already exists")
        
        # Phase 2.3: Validate upstream dependency
        if validate_upstream:
            await self._validate_upstream_dependency(device_type)
        
        # Create device
        device = Device(
            name=name,
            device_type=device_type,
            status=Status.DOWN,  # Will be set to UP after validation in Phase 2.3
            parent_container_id=parent_container_id,
            x=x,
            y=y,
            **optical_attrs,
        )
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        
        # Create default interfaces based on device type
        await self._create_default_interfaces(device)
        
        return device
    
    async def _check_name_exists(self, name: str) -> bool:
        """Check if device name already exists"""
        result = await self.session.execute(
            select(Device).where(Device.name == name)
        )
        return result.scalar_one_or_none() is not None
    
    async def _validate_upstream_dependency(self, device_type: DeviceType) -> None:
        """
        Validate that required upstream devices exist.
        
        Phase 2.3: Dependency Validation
        
        Rules:
        - EDGE_ROUTER requires at least one CORE_ROUTER or BACKBONE_GATEWAY
        - OLT requires at least one EDGE_ROUTER
        - AON_SWITCH requires at least one EDGE_ROUTER
        - ONT requires at least one OLT
        - BUSINESS_ONT requires at least one OLT
        - AON_CPE requires at least one AON_SWITCH
        
        Args:
            device_type: Type of device being provisioned
        
        Raises:
            ProvisioningError: If required upstream device does not exist
        """
        # Define upstream requirements
        upstream_requirements = {
            DeviceType.EDGE_ROUTER: {
                "required_types": {DeviceType.CORE_ROUTER, DeviceType.BACKBONE_GATEWAY},
                "error_message": "Cannot provision EDGE_ROUTER: No CORE_ROUTER or BACKBONE_GATEWAY exists",
            },
            DeviceType.OLT: {
                "required_types": {DeviceType.EDGE_ROUTER},
                "error_message": "Cannot provision OLT: No EDGE_ROUTER exists for upstream connectivity",
            },
            DeviceType.AON_SWITCH: {
                "required_types": {DeviceType.EDGE_ROUTER},
                "error_message": "Cannot provision AON_SWITCH: No EDGE_ROUTER exists for upstream connectivity",
            },
            DeviceType.ONT: {
                "required_types": {DeviceType.OLT},
                "error_message": "Cannot provision ONT: No OLT exists for PON connection",
            },
            DeviceType.BUSINESS_ONT: {
                "required_types": {DeviceType.OLT},
                "error_message": "Cannot provision BUSINESS_ONT: No OLT exists for PON connection",
            },
            DeviceType.AON_CPE: {
                "required_types": {DeviceType.AON_SWITCH},
                "error_message": "Cannot provision AON_CPE: No AON_SWITCH exists for upstream connectivity",
            },
        }
        
        # Check if this device type has upstream requirements
        if device_type not in upstream_requirements:
            return  # No upstream validation needed
        
        requirement = upstream_requirements[device_type]
        required_types = requirement["required_types"]
        error_message = requirement["error_message"]
        
        # Check if at least one required upstream device exists
        for required_type in required_types:
            result = await self.session.execute(
                select(Device).where(Device.device_type == required_type).limit(1)
            )
            if result.scalar_one_or_none() is not None:
                return  # Found at least one upstream device
        
        # No upstream device found
        raise ProvisioningError(error_message)
    
    async def _create_default_interfaces(self, device: Device) -> list[Interface]:
        """
        Create default interfaces based on device type.
        
        Phase 2.1: Basic implementation
        Phase 2.3: Will add validation for upstream connectivity
        """
        interfaces = []
        
        # Active devices get management interface
        if device.device_type in {
            DeviceType.BACKBONE_GATEWAY,
            DeviceType.CORE_ROUTER,
            DeviceType.EDGE_ROUTER,
            DeviceType.OLT,
            DeviceType.AON_SWITCH,
        }:
            # Management interface
            mgmt = Interface(
                name="mgmt0",
                interface_type=InterfaceType.ETHERNET,
                device_id=device.id,
                status=Status.DOWN,
            )
            self.session.add(mgmt)
            interfaces.append(mgmt)
            
            # Loopback interface
            loopback = Interface(
                name="lo0",
                interface_type=InterfaceType.LOOPBACK,
                device_id=device.id,
                status=Status.UP,  # Loopback always UP
            )
            self.session.add(loopback)
            interfaces.append(loopback)
        
        # OLT gets PON interfaces
        if device.device_type == DeviceType.OLT:
            for i in range(8):  # 8 PON ports
                pon = Interface(
                    name=f"pon{i}",
                    interface_type=InterfaceType.OPTICAL,
                    device_id=device.id,
                    status=Status.DOWN,
                )
                self.session.add(pon)
                interfaces.append(pon)
        
        # AON Switch gets Ethernet interfaces
        if device.device_type == DeviceType.AON_SWITCH:
            for i in range(24):  # 24 Ethernet ports
                eth = Interface(
                    name=f"eth{i}",
                    interface_type=InterfaceType.ETHERNET,
                    device_id=device.id,
                    status=Status.DOWN,
                )
                self.session.add(eth)
                interfaces.append(eth)
        
        # ONT gets single Ethernet interface
        if device.device_type == DeviceType.ONT:
            eth = Interface(
                name="eth0",
                interface_type=InterfaceType.ETHERNET,
                device_id=device.id,
                status=Status.DOWN,
            )
            self.session.add(eth)
            interfaces.append(eth)
        
        # Business ONT gets 4 Ethernet interfaces
        if device.device_type == DeviceType.BUSINESS_ONT:
            for i in range(4):
                eth = Interface(
                    name=f"eth{i}",
                    interface_type=InterfaceType.ETHERNET,
                    device_id=device.id,
                    status=Status.DOWN,
                )
                self.session.add(eth)
                interfaces.append(eth)
        
        # AON CPE gets WAN + LAN interfaces
        if device.device_type == DeviceType.AON_CPE:
            # WAN interface
            wan = Interface(
                name="wan0",
                interface_type=InterfaceType.ETHERNET,
                device_id=device.id,
                status=Status.DOWN,
            )
            self.session.add(wan)
            interfaces.append(wan)
            
            # LAN interfaces
            for i in range(4):
                lan = Interface(
                    name=f"lan{i}",
                    interface_type=InterfaceType.ETHERNET,
                    device_id=device.id,
                    status=Status.DOWN,
                )
                self.session.add(lan)
                interfaces.append(lan)
        
        # Passive devices get standard ports
        if device.device_type == DeviceType.ODF:
            for i in range(1, 49):  # 48 ports (1-48)
                port = Interface(
                    name=f"port{i}",
                    interface_type=InterfaceType.OPTICAL,
                    device_id=device.id,
                    status=Status.UP,  # Passive always UP
                )
                self.session.add(port)
                interfaces.append(port)
        
        if device.device_type == DeviceType.NVT:
            for i in range(1, 13):  # 12 ports
                port = Interface(
                    name=f"port{i}",
                    interface_type=InterfaceType.OPTICAL,
                    device_id=device.id,
                    status=Status.UP,
                )
                self.session.add(port)
                interfaces.append(port)
        
        if device.device_type == DeviceType.SPLITTER:
            # Input port
            in_port = Interface(
                name="in0",
                interface_type=InterfaceType.OPTICAL,
                device_id=device.id,
                status=Status.UP,
            )
            self.session.add(in_port)
            interfaces.append(in_port)
            
            # Output ports (1:32 splitter)
            for i in range(32):
                out_port = Interface(
                    name=f"out{i}",
                    interface_type=InterfaceType.OPTICAL,
                    device_id=device.id,
                    status=Status.UP,
                )
                self.session.add(out_port)
                interfaces.append(out_port)
        
        if device.device_type == DeviceType.HOP:
            for i in range(1, 9):  # 8 ports
                port = Interface(
                    name=f"port{i}",
                    interface_type=InterfaceType.OPTICAL,
                    device_id=device.id,
                    status=Status.UP,
                )
                self.session.add(port)
                interfaces.append(port)
        
        # Commit interfaces
        await self.session.commit()
        
        return interfaces
    
    async def get_device_interfaces(self, device_id: int) -> list[Interface]:
        """Get all interfaces for a device"""
        result = await self.session.execute(
            select(Interface).where(Interface.device_id == device_id)
        )
        return list(result.scalars().all())
