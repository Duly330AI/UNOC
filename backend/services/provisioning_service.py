"""
Provisioning service responsible for creating devices with the correct
relationships, interfaces, and optical metadata. The logic lives behind
`POST /api/devices/provision` and keeps upstream dependencies, interface
layouts, and unique naming guarantees consistent across the topology.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.core import Device, DeviceType, Interface, InterfaceType, Status


class ProvisioningError(Exception):
    """Raised when provisioning cannot proceed (validation or dependency failure)."""


class ProvisioningService:
    """
    Provision a device and its default interfaces while enforcing topology rules.

    Design notes
    ------------
    * Validates device name uniqueness before persisting.
    * Enforces upstream dependencies (for example an OLT requires an EDGE router).
    * Applies optional optical attributes directly to the `Device` row.
    * Auto-generates interface sets that match hardware expectations (PON, Ethernet).
    * Returns SQLModel entities so API responses can reuse the same schema.

    Usage
    -----
        service = ProvisioningService(session)
        device = await service.provision_device(
            name="olt-001",
            device_type=DeviceType.OLT,
            validate_upstream=True,
            tx_power_dbm=5.0,
        )

    Error handling
    --------------
    Raises :class:`ProvisioningError` when a name already exists, an upstream
    prerequisite is missing (if `validate_upstream=True`), or a provisioning
    recipe is undefined for the requested device type.
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
        Persist a device row and create its default interfaces.

        Args:
            name: Unique device name.
            device_type: Enum describing the hardware role.
            parent_container_id: Optional POP/CORE_SITE container relationship.
            validate_upstream: Enforce upstream dependencies when True.
            x: Initial X coordinate for the topology canvas.
            y: Initial Y coordinate for the topology canvas.
            **optical_attrs: Optional optical fields (`tx_power_dbm`,
                `sensitivity_min_dbm`, `insertion_loss_db`) forwarded to the model.

        Returns:
            Device: Persisted SQLModel instance (interfaces committed as well).

        Raises:
            ProvisioningError: When the name already exists or upstream validation
                fails.
        """
        # Check if name already exists
        existing = await self._check_name_exists(name)
        if existing:
            raise ProvisioningError(f"Device with name '{name}' already exists")
        
        # Enforce upstream dependency rules when requested
        if validate_upstream:
            await self._validate_upstream_dependency(device_type)
        
        # Create device
        device = Device(
            name=name,
            device_type=device_type,
            status=Status.DOWN,  # Devices start DOWN until operational checks promote them
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
        """Return True when a device with the provided name already exists."""
        result = await self.session.execute(
            select(Device).where(Device.name == name)
        )
        return result.scalar_one_or_none() is not None
    
    async def _validate_upstream_dependency(self, device_type: DeviceType) -> None:
        """
        Ensure the required upstream device types exist before provisioning.

        Examples:
        * EDGE routers require an upstream CORE router or BACKBONE gateway.
        * OLT devices require at least one EDGE router.
        * ONT/BUSINESS_ONT devices require an OLT.
        * AON_SWITCH devices require an EDGE router; AON_CPE devices require an AON switch.

        Raises:
            ProvisioningError: When no qualifying upstream device is present.
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
        Populate the standard interface layout for the given device type.

        Returns:
            list[Interface]: Interfaces committed for this device in creation order.
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
        """Return every interface attached to the provided device ID."""
        result = await self.session.execute(
            select(Interface).where(Interface.device_id == device_id)
        )
        return list(result.scalars().all())
