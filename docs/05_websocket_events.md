# WebSocket Events

**Last updated:** 24 Oct 2025  
**Emitter:** `backend/api/routes.py` via `backend/main.emit_to_all`

UNOC streams topology changes over Socket.IO so the Vue application can stay in sync without polling. This page catalogues every event name, when it fires, and the payload shape.

## Event Catalog
| Event | Trigger | Payload | Notes |
|-------|---------|---------|-------|
| `device_created` | `POST /api/devices/provision` (`routes.py:167`) | `{"device_id": int, "name": str, "device_type": str, "interface_count": int}` | Legacy naming (no colon). Emitted once per provisioning request. |
| `device:created` | `POST /api/devices` (`routes.py:204`) | `{"id": int, "name": str, "device_type": str, "status": str, "x": float, "y": float}` | Direct device creation without provisioning. |
| `device:updated` | Override endpoints and legacy overrides (`routes.py:278`, `311`, `377`, `409`) | `device.model_dump(mode="json")` | Fired whenever a device changes (override set/clear, legacy overrides). Position updates intentionally omit a broadcast. |
| `device:deleted` | `DELETE /api/devices/{id}` (`routes.py:439`) | `{"id": int}` | Downstream clients remove the node. |
| `interface:created` | `POST /api/links/create-simple` (`routes.py:630-631`) | `interface.model_dump(mode="json")` | Emitted twice per simple link (one per new interface). |
| `link:created` | `POST /api/links/create-simple` (`routes.py:632`) | `link.model_dump(mode="json")` | Conveys the new link record. |
| `link:deleted` | `DELETE /api/links/{id}` (`routes.py:531`) | `{"id": int}` | Used when a link is removed. |

## Timing Notes
- Provisioning emits only `device_created`. If the UI needs interface-level events, it should refetch via `GET /api/devices/{id}/interfaces`.
- Manual overrides broadcast `device:updated`, including the override fields so the UI can render the orange badge immediately.
- Drag-and-drop position updates do **not** emit events to avoid multi-client jitter; positions sync on page refresh.

## Socket.IO Server
- Defined in `backend/main.py` with `socketio.AsyncServer`.
- Mounted at `/socket.io`.
- Frontend subscribes via `socket.io-client` with automatic reconnection.

## Verification
- `backend/tests/test_status_override.py` ensures override endpoints return updated device payloads.
- Frontend components (`frontend/src/App.vue`, `frontend/src/components/DeviceSidebar.vue`) subscribe to the events listed above; update those files if event names or payloads change.

Keep this table aligned with any new events added in future phases (traffic updates, congestion alerts, etc.).
