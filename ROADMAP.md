# UNOC V2 Roadmap

**Last updated:** 24 Oct 2025  
**Current focus:** Phase 4 - Traffic Engine preparation  
**Latest milestone:** Phase 3.2 (Status Override) completed 15 Oct 2025

UNOC V2 targets a production-ready FTTH emulator across five major phases. Phases 1 through 3.2 are delivered; the next push is building the tariff-aware traffic engine and congestion tooling.

## Phase Overview
| Phase | Status | Duration | Completion | Notes |
|-------|--------|----------|------------|-------|
| 1. Foundation | Done Complete | 1 day | 14 Oct 2025 | Core CRUD API, Docker Compose, seed service, baseline Vue UI |
| 1.5 Optical Network | Done Complete | 1 day | 15 Oct 2025 | 14 device types, optical attributes, provisioning rules, link validation |
| 2. Real-Time | Done Complete | 1 day | 15 Oct 2025 | Socket.IO integration, live device/link events, frontend listeners |
| 3.1 Management UI | Done Complete | 0.5 day | 15 Oct 2025 | Drag-to-position, device/link management screens, safe updates |
| 3.2 Status Override | Done Complete | 0.25 day | 15 Oct 2025 | Manual override API/UI, override reason tracking, websocket broadcasts |
| 4. Traffic Engine | Planned Planned | ~5 days | Target: 24 Oct 2025 | Tariff-based traffic simulation, congestion detection, UI overlays |
| 5. Production Hardening | Note Planned | ~7 days | Target: Nov 2025 | AuthNZ, audit logging, monitoring, CI/CD, deployment guides |

## Dependency Graph
- Phase 4 builds on provisioning (Phase 1.5) and live updates (Phase 2) to stream simulated traffic.
- Phase 5 requires the observability hooks and usage telemetry introduced during Phase 4.
- Management UI investments from Phase 3.x feed directly into traffic visualisation overlays in Phase 4.

## Completed Phases (Highlights)
### Phase 1 - Foundation
- SQLModel models for devices, interfaces, and links with cascading relationships.
- FastAPI REST endpoints for CRUD operations plus `/api/seed` bootstrapper.
- Docker Compose stack (PostgreSQL 16 + backend) with automatic seeding.
- Vue 3 + Cytoscape topology canvas and seed topology explorer.

### Phase 1.5 - Optical Network
- Provisioning service (`backend/services/provisioning_service.py`) with 14 device templates and dependency enforcement.
- Optical link validation (L1-L9 rules) and structured error messaging.
- Expanded test suite (92 pytest cases) for provisioning, optical validation, and API responses.
- Documentation: `OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md`.

### Phase 2 - Real-Time
- Socket.IO server embedded in FastAPI (`backend/main.py`) with event helpers.
- WebSocket clients in Vue components, syncing create/update/delete events.
- Automatic device/interface/link broadcasts for CRUD flows and provisioning events.

### Phase 3.1 - Management UI
- Drag-and-drop device positioning persisted via `/api/devices/{id}/position`.
- Device modal refactor with tabs for interfaces, optical details, and actions.
- Link management improvements, including simple link creation endpoint.

### Phase 3.2 - Status Override (Completed 15 Oct 2025)
- Override fields (`status_override`, `override_reason`) added to the `Device` model.
- PATCH/DELETE override endpoints with validation and WebSocket notifications.
- Sidebar/manual override UI with clear state cues and undo support.

## Phase 4 - Traffic Engine (Planned)
- **Scope:** Tariff-based traffic simulation (downstream/upstream), congestion detection with hysteresis, traffic metrics overlay in UI.
- **Deliverables:** Traffic engine service module, websocket events for traffic updates, UI charts, persistence for historical samples (rolling window).
- **Dependencies:** Accurate device hierarchy (Phase 1.5), WebSocket streaming (Phase 2), device modal extensibility (Phase 3.1).
- **Risks:** Performance of traffic calculations under large topologies; need for batching events. Mitigation includes async tasks and throttled emits.
- **Exit Criteria:** Realistic traffic visualisation across the topology, congestion alerts exposed via sidebar, regression test coverage for tariff rules.

## Phase 5 - Production Hardening (Planned)
- **Scope:** Authentication (JWT), role-based authorization, audit logging, observability stack (Prometheus/Grafana), automated CI/CD pipeline, deployment runbooks.
- **Prerequisites:** Traffic engine metrics to feed monitoring dashboards, consolidated API schema from earlier phases.
- **Exit Criteria:** Production deployment guide complete, security checks in place, uptime targets defined, monitoring dashboards populated.

## Recent Deliverables (Oct 2025)
- Provisioning service (backend/services/provisioning_service.py)
- Status override API and UI (backend/api/routes.py, frontend/src/components/DeviceSidebar.vue)
- Socket.IO event pipeline (backend/main.py, frontend/src/App.vue)

## Forecast & Next Steps
1. Finalise Phase 4 design docs (traffic data model, websocket payloads).
2. Implement traffic simulation service and persistence.
3. Extend Vue UI with congestion badges and traffic charts.
4. Backfill tests and docs (`docs/11_traffic_engine_and_congestion.md`) before locking the phase.

## Risk Register
- **Performance:** Traffic engine may need batching to avoid websocket flooding.
- **Data Freshness:** Override and traffic updates must stay coherent; consider event ordering guarantees.
- **Documentation Drift:** Ensure traffic engine implementation updates all affected docs before release.

## References
- `docs/ARCHITECTURE.md` - System design and component responsibilities.
- `docs/MASTER_ACTION_PLAN.md` - Active tasks, owners, and technical debt.
- `docs/OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md` - Optical provisioning reference.
