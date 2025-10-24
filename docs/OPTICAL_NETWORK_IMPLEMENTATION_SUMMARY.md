# Optical Network Implementation Summary

**Last updated:** 24 Oct 2025  
**Scope:** Provisioning service, optical attributes, and device catalog after Phase 3.2.

UNOC models fourteen FTTH device types with automatic interface creation and upstream validation. This file captures the rules enforced by `backend/services/provisioning_service.py` and the REST layer that invokes it.

## Device Catalog
| Device type | Category | Default interfaces | Optical fields used | Notes |
|-------------|----------|--------------------|---------------------|-------|
| BACKBONE_GATEWAY | Active | `mgmt0`, `lo0` | None | Top-most anchor, no upstream requirement |
| CORE_ROUTER | Active | `mgmt0`, `lo0` | None | Feeds EDGE routers |
| EDGE_ROUTER | Active | `mgmt0`, `lo0` | None | Requires CORE or BACKBONE upstream (see service line 117) |
| OLT | Active | `mgmt0`, `lo0`, `pon0`-`pon7` | `tx_power_dbm` | Requires EDGE upstream |
| AON_SWITCH | Active | `mgmt0`, `lo0`, `eth0`-`eth23` | None | Requires EDGE upstream |
| ONT | Active | `eth0` | `sensitivity_min_dbm` | Requires OLT upstream |
| BUSINESS_ONT | Active | `eth0`-`eth3` | `sensitivity_min_dbm` | Requires OLT upstream |
| AON_CPE | Active | `wan0`, `lan0`-`lan3` | None | Requires AON_SWITCH upstream |
| POP | Container | None | None | Parent container for active devices |
| CORE_SITE | Container | None | None | Coarse-grained container |
| ODF | Passive | `port1`-`port48` | `insertion_loss_db` | Ports default to `UP` |
| NVT | Passive | `port1`-`port12` | `insertion_loss_db` | Ports default to `UP` |
| SPLITTER | Passive | `in0`, `out0`-`out31` | `insertion_loss_db` | 1x32 splitter map |
| HOP | Passive | `port1`-`port8` | `insertion_loss_db` | Inline passive hub |

Refer to `backend/models/core.py:27` for enum definitions and `backend/services/provisioning_service.py:177` for the concrete interface recipes.

## Provisioning Flow (API)
```
POST /api/devices/provision (routes.py:124)
      |
      v
ProvisioningService.provision_device (provisioning_service.py:52)
      |
      v
Persistence -> interface generation -> Socket.IO emit("device_created", {...})
      |
      v
ProvisionDeviceResponse (device + interfaces + message)
```
- Request schema: `ProvisionDeviceRequest` (`backend/api/routes.py:52`)
- Response schema: `ProvisionDeviceResponse` (`backend/api/routes.py:88`)
- Socket.IO payload: `{"device_id": int, "name": str, "device_type": str, "interface_count": int}` (routes.py:167)
- Errors map to `ProvisioningError` and surface as HTTP 400 with the original message.

## Upstream Dependency Rules
`ProvisioningService._validate_upstream_dependency` (`backend/services/provisioning_service.py:117`) enforces:
- EDGE_ROUTER requires a CORE_ROUTER or BACKBONE_GATEWAY.
- OLT requires an EDGE_ROUTER.
- AON_SWITCH requires an EDGE_ROUTER.
- ONT and BUSINESS_ONT require an OLT.
- AON_CPE requires an AON_SWITCH.

Violations raise one of the following messages:
- `"Cannot provision EDGE_ROUTER: No CORE_ROUTER or BACKBONE_GATEWAY exists"`
- `"Cannot provision OLT: No EDGE_ROUTER exists for upstream connectivity"`
- `"Cannot provision AON_SWITCH: No EDGE_ROUTER exists for upstream connectivity"`
- `"Cannot provision ONT: No OLT exists for PON connection"`
- `"Cannot provision BUSINESS_ONT: No OLT exists for PON connection"`
- `"Cannot provision AON_CPE: No AON_SWITCH exists for upstream connectivity"`

Duplicate names trigger `"Device with name '<name>' already exists"` (provisioning_service.py:94).

## Link Validation Overview
Detailed rules live in `docs/04_link_validation.md`. For quick reference:
- L1-L7 encode active hierarchy (BACKBONE->CORE->EDGE->OLT/AON->ONT/CPE).
- L8 allows inline passive devices (active-passive and passive-passive).
- L9 allows peer redundancy for BACKBONE_GATEWAY, CORE_ROUTER, and EDGE_ROUTER.
Implementation: `backend/constants/link_rules.py:40`.

## Testing Touchpoints
- `backend/tests/test_provisioning_service.py` (device templates, duplicates)
- `backend/tests/test_link_rules.py` (L1-L9 validation)
- `backend/tests/test_provision_api.py` (endpoint contract)

## References
- `backend/models/core.py:27` - device enum and optical fields
- `backend/services/provisioning_service.py:20` - provisioning service entry point
- `backend/services/provisioning_service.py:177` - interface generation matrix
- `backend/api/routes.py:124` - REST provisioning endpoint
- `backend/constants/link_rules.py:40` - link rules registry
