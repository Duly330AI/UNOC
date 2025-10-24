"""
Test Provisioning Service

Phase 2.1: Basic provisioning with interface creation
"""

import pytest

from backend.models.core import DeviceType, InterfaceType
from backend.services.provisioning_service import ProvisioningError, ProvisioningService


@pytest.mark.asyncio
async def test_provision_backbone_gateway(async_session):
    """Test: Provision BACKBONE_GATEWAY creates mgmt0 + lo0"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="backbone_gw1",
        device_type=DeviceType.BACKBONE_GATEWAY,
        x=100.0,
        y=200.0,
    )
    
    assert device.id is not None
    assert device.name == "backbone_gw1"
    assert device.device_type == DeviceType.BACKBONE_GATEWAY
    
    # Check interfaces
    interfaces = await service.get_device_interfaces(device.id)
    assert len(interfaces) == 2
    
    interface_names = {i.name for i in interfaces}
    assert "mgmt0" in interface_names
    assert "lo0" in interface_names
    
    # Verify loopback is UP
    lo0 = next(i for i in interfaces if i.name == "lo0")
    assert lo0.status.value == "UP"


@pytest.mark.asyncio
async def test_provision_olt_creates_pon_interfaces(async_session):
    """Test: Provision OLT creates mgmt0 + lo0 + 8 PON interfaces"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="olt1",
        device_type=DeviceType.OLT,
        validate_upstream=False,
        tx_power_dbm=5.0,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    # mgmt0 + lo0 + 8 PON = 10 interfaces
    assert len(interfaces) == 10
    
    interface_names = {i.name for i in interfaces}
    assert "mgmt0" in interface_names
    assert "lo0" in interface_names
    
    # Check all 8 PON interfaces
    for i in range(8):
        assert f"pon{i}" in interface_names
    
    # Verify PON interfaces are OPTICAL type
    pon_interfaces = [i for i in interfaces if i.name.startswith("pon")]
    assert len(pon_interfaces) == 8
    for pon in pon_interfaces:
        assert pon.interface_type == InterfaceType.OPTICAL


@pytest.mark.asyncio
async def test_provision_aon_switch_creates_24_ethernet_ports(async_session):
    """Test: Provision AON_SWITCH creates mgmt0 + lo0 + 24 Ethernet"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="aon_sw1",
        device_type=DeviceType.AON_SWITCH,
        validate_upstream=False,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    # mgmt0 + lo0 + 24 eth = 26 interfaces
    assert len(interfaces) == 26
    
    eth_interfaces = [i for i in interfaces if i.name.startswith("eth")]
    assert len(eth_interfaces) == 24
    
    for eth in eth_interfaces:
        assert eth.interface_type == InterfaceType.ETHERNET


@pytest.mark.asyncio
async def test_provision_ont_creates_single_eth(async_session):
    """Test: Provision ONT creates only eth0"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="ont1",
        device_type=DeviceType.ONT,
        validate_upstream=False,
        sensitivity_min_dbm=-28.0,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    assert len(interfaces) == 1
    
    eth0 = interfaces[0]
    assert eth0.name == "eth0"
    assert eth0.interface_type == InterfaceType.ETHERNET


@pytest.mark.asyncio
async def test_provision_business_ont_creates_4_eth(async_session):
    """Test: Provision BUSINESS_ONT creates eth0-eth3"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="bont1",
        device_type=DeviceType.BUSINESS_ONT,
        validate_upstream=False,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    assert len(interfaces) == 4
    
    interface_names = {i.name for i in interfaces}
    for i in range(4):
        assert f"eth{i}" in interface_names


@pytest.mark.asyncio
async def test_provision_aon_cpe_creates_wan_and_lan(async_session):
    """Test: Provision AON_CPE creates wan0 + lan0-lan3"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="cpe1",
        device_type=DeviceType.AON_CPE,
        validate_upstream=False,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    # wan0 + 4 lan = 5 interfaces
    assert len(interfaces) == 5
    
    interface_names = {i.name for i in interfaces}
    assert "wan0" in interface_names
    
    for i in range(4):
        assert f"lan{i}" in interface_names


@pytest.mark.asyncio
async def test_provision_odf_creates_48_optical_ports(async_session):
    """Test: Provision ODF creates port1-port48"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="odf1",
        device_type=DeviceType.ODF,
        insertion_loss_db=0.5,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    assert len(interfaces) == 48
    
    # Verify all are OPTICAL and status UP (passive device)
    for i in interfaces:
        assert i.interface_type == InterfaceType.OPTICAL
        assert i.status.value == "UP"
    
    # Check naming (port1 to port48)
    interface_names = {i.name for i in interfaces}
    for i in range(1, 49):
        assert f"port{i}" in interface_names


@pytest.mark.asyncio
async def test_provision_nvt_creates_12_ports(async_session):
    """Test: Provision NVT creates port1-port12"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="nvt1",
        device_type=DeviceType.NVT,
        insertion_loss_db=0.3,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    assert len(interfaces) == 12


@pytest.mark.asyncio
async def test_provision_splitter_creates_in_and_32_out(async_session):
    """Test: Provision SPLITTER creates in0 + out0-out31 (1:32 splitter)"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="splitter1",
        device_type=DeviceType.SPLITTER,
        insertion_loss_db=18.0,  # Typical 1:32 splitter loss
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    # 1 input + 32 outputs = 33 interfaces
    assert len(interfaces) == 33
    
    interface_names = {i.name for i in interfaces}
    assert "in0" in interface_names
    
    for i in range(32):
        assert f"out{i}" in interface_names


@pytest.mark.asyncio
async def test_provision_hop_creates_8_ports(async_session):
    """Test: Provision HOP creates port1-port8"""
    service = ProvisioningService(async_session)
    
    device = await service.provision_device(
        name="hop1",
        device_type=DeviceType.HOP,
        insertion_loss_db=0.2,
    )
    
    interfaces = await service.get_device_interfaces(device.id)
    assert len(interfaces) == 8


@pytest.mark.asyncio
async def test_provision_container_devices_no_interfaces(async_session):
    """Test: Container devices (POP, CORE_SITE) get NO interfaces"""
    service = ProvisioningService(async_session)
    
    # Test POP
    pop = await service.provision_device(
        name="pop1",
        device_type=DeviceType.POP,
    )
    pop_interfaces = await service.get_device_interfaces(pop.id)
    assert len(pop_interfaces) == 0
    
    # Test CORE_SITE
    core_site = await service.provision_device(
        name="core_site1",
        device_type=DeviceType.CORE_SITE,
    )
    site_interfaces = await service.get_device_interfaces(core_site.id)
    assert len(site_interfaces) == 0


@pytest.mark.asyncio
async def test_provision_duplicate_name_raises_error(async_session):
    """Test: Provisioning device with duplicate name raises error"""
    service = ProvisioningService(async_session)
    
    # Create first device
    await service.provision_device(
        name="router1",
        device_type=DeviceType.CORE_ROUTER,
    )
    
    # Try to create duplicate
    with pytest.raises(ProvisioningError, match="already exists"):
        await service.provision_device(
            name="router1",
            device_type=DeviceType.EDGE_ROUTER,
        )


@pytest.mark.asyncio
async def test_provision_with_parent_container(async_session):
    """Test: Device can be provisioned inside parent container"""
    service = ProvisioningService(async_session)
    
    # Create POP container
    pop = await service.provision_device(
        name="pop_main",
        device_type=DeviceType.POP,
    )
    
    # Create OLT inside POP
    olt = await service.provision_device(
        name="olt_in_pop",
        device_type=DeviceType.OLT,
        validate_upstream=False,
        parent_container_id=pop.id,
    )
    
    assert olt.parent_container_id == pop.id


@pytest.mark.asyncio
async def test_provision_with_optical_attributes(async_session):
    """Test: Optical attributes are correctly stored during provisioning"""
    service = ProvisioningService(async_session)
    
    # Provision OLT with tx_power
    olt = await service.provision_device(
        name="olt_with_power",
        device_type=DeviceType.OLT,
        validate_upstream=False,
        tx_power_dbm=5.5,
    )
    
    assert olt.tx_power_dbm == 5.5
    assert olt.sensitivity_min_dbm is None
    assert olt.insertion_loss_db is None
    
    # Provision ONT with sensitivity
    ont = await service.provision_device(
        name="ont_with_sensitivity",
        device_type=DeviceType.ONT,
        validate_upstream=False,
        sensitivity_min_dbm=-28.0,
    )
    
    assert ont.sensitivity_min_dbm == -28.0
    assert ont.tx_power_dbm is None


@pytest.mark.asyncio
async def test_all_device_types_provisionable(async_session):
    """Test: All 14 device types can be provisioned"""
    service = ProvisioningService(async_session)
    
    device_types = [
        DeviceType.BACKBONE_GATEWAY,
        DeviceType.CORE_ROUTER,
        DeviceType.EDGE_ROUTER,
        DeviceType.OLT,
        DeviceType.AON_SWITCH,
        DeviceType.ONT,
        DeviceType.BUSINESS_ONT,
        DeviceType.AON_CPE,
        DeviceType.POP,
        DeviceType.CORE_SITE,
        DeviceType.ODF,
        DeviceType.NVT,
        DeviceType.SPLITTER,
        DeviceType.HOP,
    ]
    
    for idx, device_type in enumerate(device_types):
        device = await service.provision_device(
            name=f"test_{device_type.value.lower()}_{idx}",
            device_type=device_type,
        )
        assert device.id is not None
        assert device.device_type == device_type
