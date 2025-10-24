# UNOC Master Action Plan

**Last updated:** 24 Oct 2025  
**Owner:** Core engineering team (backend + frontend)  
**Current stage:** Phase 4 planning (Traffic Engine)

This plan tracks what is done, what is next, and the open risks as UNOC moves beyond Phase 3.2 (Status Override).

## Delivery Status
| Phase | Status | Date | Primary Deliverables |
|-------|--------|------|----------------------|
| 1. Foundation | Done Complete | 14 Oct 2025 | CRUD API, Docker Compose, base Vue UI, seed pipeline |
| 1.5 Optical Network | Done Complete | 15 Oct 2025 | Provisioning service, optical rules, 14 device templates |
| 2. Real-Time | Done Complete | 15 Oct 2025 | Socket.IO pipeline, live topology updates |
| 3.1 Management UI | Done Complete | 15 Oct 2025 | Drag-and-drop positioning, device modal overhaul |
| 3.2 Status Override | Done Complete | 15 Oct 2025 | Override API + UI, reason tracking, websocket broadcasts |
| 4. Traffic Engine | Planned In Planning | Target: 24 Oct 2025 | Tariff-based simulation, congestion alerts, UI overlays |
| 5. Production Hardening | Note Pending | Target: Nov 2025 | AuthNZ, audit logging, monitoring, CI/CD |

## Completed Work (Phase 3.2 Snapshot)
- **Backend**
  - `backend/models/core.py`: `status_override` and `override_reason` fields.
  - `backend/api/routes.py`: PATCH/DELETE override endpoints, drag-to-position handler, provisioning enhancements.
  - `backend/services/provisioning_service.py`: Validated dependencies, interface auto-generation, optical metadata.
  - `backend/main.py`: Socket.IO server and `emit_to_all` helper.
- **Frontend**
  - `frontend/src/components/DeviceSidebar.vue`: Override controls, status badges, optical tabs.
  - `frontend/src/components/DeviceModal.vue`: Extended device detail tabs, position editor.
  - `frontend/src/App.vue`: Global event wiring for overrides, provisioning, and link updates.
- **Quality**
  - 92 pytest cases spanning provisioning, optical rules, overrides, and coordinate persistence.
  - Ruff linting baseline for backend modules.

## Phase 4 - Traffic Engine (Next Up)
- **Objectives**
  1. Simulate downstream/upstream throughput per device based on tariff tiers.
  2. Detect congestion using configurable thresholds + hysteresis to avoid flapping.
  3. Surface live traffic metrics in the UI (sidebar + topology overlays).
  4. Broadcast traffic updates via WebSockets with throttling.
- **Key Tasks**
  - Finalise traffic data model (`TrafficSample`, `TariffProfile`) and persistence approach.
  - Implement traffic simulation service (likely within `backend/services/traffic_service.py`).
  - Expand API + Socket.IO contracts for traffic payloads.
  - Update Vue components and Pinia store to render traffic charts and congestion banners.
  - Extend documentation (`docs/11_traffic_engine_and_congestion.md`) with algorithms and payload specs.
- **Exit Criteria**
  - Traffic engine produces deterministic results for seeded topology.
  - UI highlights congested nodes/links and exposes traffic charts.
  - Regression tests cover tariff mapping, hysteresis, and websocket broadcasting.

## Known Issues & Technical Debt
| Area | Description | Impact | Mitigation |
|------|-------------|--------|-----------|
| API Documentation | `/api/devices/{id}/interfaces` lacks formal docs | Medium | Cover in Phase 2 doc refresh; add OpenAPI examples |
| Status Propagation | Automatic status roll-up for child devices not yet implemented | High for traffic phase | Design alongside traffic engine; document algorithm |
| MAC/IP Allocation | Strategy not documented or enforced | Medium | Add to provisioning backlog and documentation |
| WebSocket Throughput | No batching/back-pressure | Medium | Introduce rate limiting before traffic engine ships |
| Testing | Frontend automated tests missing | Medium | Add component tests during Phase 4 UI work |

## Reference Links
- `README.md` - project snapshot and onboarding
- `ROADMAP.md` - timeline and dependencies
- `docs/ARCHITECTURE.md` - system design and data flow
- `docs/OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md` - optical provisioning reference
- `backend/api/routes.py` - authoritative list of REST endpoints
- `frontend/src/components/DeviceSidebar.vue` - latest override UI implementation

## Recent Architectural Decisions
- **Single status field with optional override:** Avoids conflicting state machines; override intent is explicit metadata.
- **Socket.IO for live updates:** Keeps topology synchronised across clients without refresh loops.
- **Provisioning-first approach:** Backend enforces hierarchy and interface creation so the UI remains thin.
- **Phase gates:** Each phase ships with updated docs and tests before moving forward; prevents Phase 4 from building on shaky ground.

## Open Questions
1. What persistence strategy should Phase 4 use for historical traffic (rolling window in memory vs. PostgreSQL table)?
2. Do we need per-device tariff configuration in the UI or can Phase 4 rely on seed data only?
3. Should congestion alerts trigger additional notifications (email/webhooks) in Phase 4 or wait for Phase 5?

Document answers in this file as decisions are made to keep the team aligned.
