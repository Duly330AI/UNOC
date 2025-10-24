# Error Handling

**Last updated:** 24 Oct 2025  
**Scope:** Backend API errors exposed during provisioning, overrides, and link operations.

UNOC uses FastAPI `HTTPException` responses with descriptive strings. Most validation originates from domain services (`ProvisioningService`, link rules) and is surfaced to clients without modification.

## Common HTTP Responses
| Status | Scenario | Source | Message |
|--------|----------|--------|---------|
| 400 | Duplicate device name | `ProvisioningService._check_name_exists` (`provisioning_service.py:94`) | `"Device with name '<name>' already exists"` |
| 400 | Missing upstream dependency | `ProvisioningService._validate_upstream_dependency` (`provisioning_service.py:140-173`) | One of the predefined `"Cannot provision ..."` messages |
| 400 | Invalid override value | `PATCH /devices/{id}/override` (`routes.py:229`) | `"status_override must be 'UP' or 'DOWN'"` |
| 400 | Legacy override invalid status | `POST /devices/{id}/override-status` (`routes.py:355`) | `"Invalid status. Must be one of: ['UP', 'DOWN', 'DEGRADED']"` |
| 404 | Device not found | Multiple endpoints (`routes.py:119`, `264`, `301`, `334`, `362`, `399`, `429`, `466`) | `"Device not found"` |
| 404 | Interface not found | `POST /links` (`routes.py:445`) | `"Interface not found"` |
| 404 | Link not found | `DELETE /links/{id}` (`routes.py:458`) | `"Link not found"` |
| 400 | Simple link self-connection | `POST /links/create-simple` (`routes.py:510`) | `"Cannot link device to itself"` |

## Error Propagation Pattern
1. Domain service raises `ProvisioningError` (or returns False from helper).
2. Route wraps it with `HTTPException(status_code=400, detail=str(error))` (`routes.py:165`).
3. FastAPI serialises the detail to a JSON payload: `{"detail": "message"}`.

No additional error codes are currently used; the message string is the contract.

## Client Guidance
- Treat `detail` as user-facing text for now; do not parse it for control flow.
- Retry on 5xx codes only (none are emitted today, but future async work may add them).
- The frontend overlays error toasts with the exact `detail` message.

## Future Enhancements
- Dedicated error codes for traffic engine work (Phase 4) to enable richer UI hints.
- Centralised error catalog for automated documentation (see `docs/MASTER_ACTION_PLAN.md` backlog).

## References
- `backend/services/provisioning_service.py:20` - Core provisioning validations.
- `backend/api/routes.py:98-632` - REST endpoints and error handling.
- `backend/constants/link_rules.py:104` - Link validation messages.
