# Provisioning Flow

**Last updated:** 24 Oct 2025  
**Primary sources:** `backend/api/routes.py:124`, `backend/services/provisioning_service.py:52`

Provisioning automates device creation, interface generation, and upstream validation. This document explains when to call each endpoint and how the service enforces FTTH topology rules.

## Endpoints
| Endpoint | Use case | Notes |
|----------|----------|-------|
| `POST /api/devices/provision` | Standard device onboarding | Generates interfaces, enforces dependencies, emits events. |
| `POST /api/devices` | Low-level insert | Skips provisioning logic. Use only for tests or manual fixes. |
| `GET /api/devices/{id}/interfaces` | Inspect generated interfaces | Returns ordered list of `InterfaceResponse`. |

## Workflow Overview
```
Client (UI/CLI)
      |
      v
POST /api/devices/provision (routes.py:124)
      |
      v
ProvisioningService.provision_device (provisioning_service.py:52)
      |
      +--> _check_name_exists (line 94)
      +--> _validate_upstream_dependency (line 117)
      +--> _create_default_interfaces (line 177)
      |
      v
Socket.IO emit("device_created", {...}) (routes.py:167)
      |
      v
ProvisionDeviceResponse (routes.py:174)
```

## Step-by-Step
1. **Validate uniqueness** - `_check_name_exists` ensures no duplicate names exist; duplicate attempts raise `"Device with name '<name>' already exists"`.
2. **Enforce upstream hierarchy** - `_validate_upstream_dependency` checks for required parent roles (EDGE needs CORE/BACKBONE, OLT needs EDGE, etc).
3. **Persist device** - The device is saved with default status `DOWN` and any optional optical attributes.
4. **Generate interfaces** - `_create_default_interfaces` adds management, loopback, PON, Ethernet, or passive ports depending on `DeviceType`.
5. **Emit WebSocket event** - `device_created` is broadcast with `{device_id, name, device_type, interface_count}` so connected UIs can refresh.
6. **Return response** - The endpoint responds with `ProvisionDeviceResponse` containing the device payload, interface list, and message.

## Error Handling
| Condition | HTTP status | Message source |
|-----------|-------------|----------------|
| Duplicate name | 400 | `ProvisioningError` (`provisioning_service.py:94`) |
| Missing upstream dependency | 400 | One of the error strings defined at lines 140-173 |
| Unsupported status override (legacy path) | 400 | `override_device_status_legacy` (`routes.py:344`) |
| Missing device | 404 | Returned by any path that loads the device (`routes.py:119`, `routes.py:320`) |

Errors bubble up through `ProvisioningError` and are wrapped in `HTTPException` by the route handler (`routes.py:181`).

## When to Use `POST /api/devices`
- Seed scripts that want to create raw records without interface recipes.
- Unit tests that explicitly manage interface/link entities.
- Emergency fixes when provisioning validation is blocking (follow up with manual interface creation).

In all other cases, prefer the provisioning endpoint.

## Interface Inspection
After provisioning, call:
```
GET /api/devices/{device_id}/interfaces  # routes.py:320
```
The response is a list of `InterfaceResponse` objects in creation order (management/loopback first, then PON or Ethernet block).

## Related Tests
- `backend/tests/test_provision_api.py` - Verifies REST contract and payload.
- `backend/tests/test_provisioning_service.py` - Validates provisioning service behaviour and error messaging.
- `backend/tests/test_link_rules.py` - Ensures downstream link validation stays compatible with provisioning output.
