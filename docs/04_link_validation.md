# Link Validation (L1-L9)

**Last updated:** 24 Oct 2025  
**Source file:** `backend/constants/link_rules.py:40`

The FTTH topology is constrained by nine link types (L1-L9). These rules help provisioning and link creation detect invalid connections before they are persisted.

## Link Rules
| Link type | Allowed devices | Bidirectional | Description |
|-----------|-----------------|---------------|-------------|
| L1 `L1_BACKBONE_CORE` | BACKBONE_GATEWAY <-> CORE_ROUTER | Yes | Core backbone fan-out. |
| L2 `L2_CORE_EDGE` | CORE_ROUTER <-> EDGE_ROUTER | Yes | Core to distribution. |
| L3 `L3_EDGE_OLT` | EDGE_ROUTER <-> OLT | Yes | GPON uplink. |
| L4 `L4_EDGE_AON` | EDGE_ROUTER <-> AON_SWITCH | Yes | Active optical uplink. |
| L5 `L5_OLT_ONT` | OLT <-> ONT | Yes | Residential last mile. |
| L6 `L6_OLT_BUSINESS_ONT` | OLT <-> BUSINESS_ONT | Yes | Business GPON service. |
| L7 `L7_AON_CPE` | AON_SWITCH <-> AON_CPE | Yes | Active optical last mile. |
| L8 `L8_INLINE_PASSIVE` | Active-passive or passive-passive | Yes | Inline passive components (ODF, NVT, SPLITTER, HOP). |
| L9 `L9_PEER_TO_PEER` | BACKBONE_GATEWAY, CORE_ROUTER, EDGE_ROUTER (same type) | Yes | Redundant mesh within same layer. |

The registry lives in `LINK_RULES` (`link_rules.py:64` onwards) via `LinkRule` dataclasses.

## Validation Helpers
- `validate_link_between_devices(a_type, b_type)` (`link_rules.py:104`) - Returns `(is_valid, link_type, message)`. Invalid pairs receive `False, None, "No valid link rule between <A> and <B>"`.
- `get_allowed_downstream_types(device_type)` (`link_rules.py:150`) - Computes allowed downstream device types, including passive devices and peer redundancy.
- `is_valid_topology_path(path)` (`link_rules.py:190`) - Verifies multi-hop paths by chaining `validate_link_between_devices`.

## Passive Inline Handling (L8)
L8 is applied when one or both devices are passive. Rules:
- Active <-> Passive - always allowed (e.g., OLT -> SPLITTER).
- Passive <-> Passive - allowed to support patch panels.

The helper returns `LinkType.INLINE_PASSIVE` with description `"Passive device can be inline in any active connection"` or `"Passive devices can be interconnected (patch panels, splicing)"`.

## Peer Redundancy (L9)
Peer redundancy allows same-level devices (BACKBONE_GATEWAY/CORE_ROUTER/EDGE_ROUTER) to connect. The helper returns:
```
(True, LinkType.PEER_TO_PEER, "Peer-to-peer connection allowed for <type> redundancy")
```

## Example
```python
from backend.constants.link_rules import validate_link_between_devices, LinkType
from backend.models.core import DeviceType

is_valid, link_type, reason = validate_link_between_devices(
    DeviceType.EDGE_ROUTER,
    DeviceType.OLT,
)

assert is_valid
assert link_type == LinkType.EDGE_OLT
print(reason)  # "Edge router provides upstream for OLT"
```

## Related API Behaviour
`POST /api/links` (`backend/api/routes.py:434`) should call `validate_link_between_devices` before committing a link (future enhancement). The helper is already covered by `backend/tests/test_link_rules.py`.

## References
- `backend/constants/link_rules.py:40` - Enum and rule definitions.
- `backend/constants/link_rules.py:104` - Main validation helper.
- `backend/constants/link_rules.py:150` - Downstream assistance.
- `backend/constants/link_rules.py:190` - Path validation utility.
