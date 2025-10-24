# Status and Overrides

**Last updated:** 24 Oct 2025  
**Primary references:** `backend/models/core.py:86`, `backend/api/routes.py:247`

UNOC uses a single `status` field to represent device health. Manual interventions are layered on top via `status_override` and `override_reason`. This section explains how overrides work from API to UI.

## Status Model
- `status` - Authoritative value computed by backend logic (enum `Status`).
- `status_override` - Optional manual value that replaces `status` for presentation.
- `override_reason` - Optional text explaining why the override is in place.

Fields live on the `Device` model (`backend/models/core.py:86`) and persist through restarts.

## Canonical Endpoints
| Endpoint | Description | Event | Notes |
|----------|-------------|-------|-------|
| `PATCH /api/devices/{id}/override` (`routes.py:247`) | Apply override (`UP` or `DOWN`) | `device:updated` | Validates presence of the device and allowed values. |
| `DELETE /api/devices/{id}/override` (`routes.py:287`) | Clear override | `device:updated` | Removes override fields and reverts to computed status. |
| `POST /api/devices/{id}/override-status` (`routes.py:344`) | Legacy endpoint (accepts `DEGRADED`) | `device:updated` | Retained for backward compatibility. |
| `DELETE /api/devices/{id}/override-status` (`routes.py:386`) | Legacy clear route | `device:updated` | Use only for older clients. |

## Flow
```
User selects device in UI
      |
      v
PATCH /api/devices/{id}/override with {"status_override": "UP", "override_reason": "Testing"}
      |
      v
Device updated in DB (routes.py:270) -> commit/refresh
      |
      v
Socket.IO emit("device:updated", device.model_dump(mode="json"))
      |
      v
Frontend highlights override badge and disables conflicting actions
```

Clearing the override follows the same pattern with `DELETE /override`.

## Validation Rules
- Allowed override values for the canonical endpoint: `UP`, `DOWN`.
- Requests with other values receive `HTTP 400` (`routes.py:267`).
- Non-existent devices return `HTTP 404` with `"Device not found"`.

Legacy endpoints (`override-status`) still accept `DEGRADED` to support older tooling. Document this when integrating CLI scripts.

## UI Considerations
- The Vue sidebar reads `status_override` to display orange "override" chips.
- `override_reason` is surfaced in the details pane for operator clarity.
- Live updates rely on the `device:updated` Socket.IO event (same event as other device edits).

## References
- `backend/models/core.py:86` - Device status and override fields.
- `backend/api/routes.py:247` - Canonical override route.
- `backend/api/routes.py:287` - Clear override route.
- `frontend/src/components/DeviceSidebar.vue` - UI controls and badges.
