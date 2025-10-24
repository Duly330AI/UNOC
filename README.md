# UNOC - Universal Network Operations Center

UNOC is a Fiber-to-the-Home (FTTH) network emulator that pairs a FastAPI backend with a Vue 3 frontend to model provisioning, optical behaviour, and live device management for large access networks.

## Project Snapshot (Oct 2025)
- Phase 3.2 (Manual Status Override) delivered on 15 Oct 2025; Phase 4 (Traffic Engine) is in planning.
- Provisioning service supports 14 device types with upstream dependency validation and optical attributes.
- Real-time topology updates flow through Socket.IO (backend) and Pinia-managed Vue components.
- 92 backend pytest cases cover provisioning, optical link rules, drag-and-drop positioning, and status overrides.

## Feature Roadmap
| Phase | Scope | Status | Completion |
|-------|-------|--------|------------|
| 1. Foundation | Core models, CRUD API, seed data, base UI | Done | 14 Oct 2025 |
| 1.5 Optical | Optical device catalog, provisioning rules, link validation | Done | 15 Oct 2025 |
| 2. Real-Time | Socket.IO integration, live topology updates | Done | 15 Oct 2025 |
| 3.1 Management UI | Device/link management tools, drag-to-position | Done | 15 Oct 2025 |
| 3.2 Status Override | Manual overrides with full UI + API support | Done | 15 Oct 2025 |
| 4. Traffic | Tariff-based traffic engine, congestion detection | Planned | Est. 5 days |
| 5. Production | Auth, audit, monitoring, CI/CD | Planned | Est. 7 days |

Detailed scope and dependencies live in `ROADMAP.md`.

## Tech Stack
- **Backend:** FastAPI 0.115, SQLModel, PostgreSQL 16, Socket.IO (ASGI), pytest, Ruff
- **Frontend:** Vue 3 + Vite, TypeScript, Pinia, Cytoscape.js, Socket.IO client
- **Infrastructure:** Docker Compose (backend + PostgreSQL), Node.js 20+ for frontend tooling

## Architecture Overview
```
+----------------+  REST & WebSockets  +-------------------+  SQLModel ORM  +-------------+
| Vue 3 + Pinia  |-------------------->| FastAPI backend   |--------------->| PostgreSQL  |
| Network UI     |<--------------------| Provisioning svc  |<---------------| 16          |
+----------------+  Live device events | Status overrides  |                +-------------+
                     (Socket.IO)       +-------------------+       Seed svc
```
- Devices, interfaces, and links are persisted in PostgreSQL via SQLModel.
- Provisioning service enforces device hierarchy, auto-creates interfaces, and emits WebSocket events.
- Frontend consumes `/api/*` endpoints for CRUD and listens to Socket.IO events to update the topology instantly.
- A single `status` field flows end-to-end; optional overrides are stored alongside the device and surfaced in the UI.

See `docs/ARCHITECTURE.md` for component responsibilities, data flow, and deployment notes.

## Quick Start
### 1. Run the backend and database
```bash
docker compose up -d
```
- Starts PostgreSQL (`postgres:16-alpine`) and FastAPI on `http://localhost:5001`.
- The backend seeds a demo topology the first time the database is empty.

### 2. Install and run the frontend
```bash
cd frontend
npm install
npm run dev
```
- Opens the Vite dev server at `http://localhost:5173`.
- The Vue UI connects to the backend REST API and Socket.IO gateway automatically.

## Testing & Quality
- **Backend:** `pytest -v` (92 tests as of Oct 2025) with in-memory SQLite fixtures and async-aware FastAPI clients.
- **Linting:** `ruff check backend` keeps style and import order consistent.
- **Frontend:** `npm run build` serves as the smoke-test prior to deployment; component tests will be added in Phase 4.
- Track coverage goals and outstanding work in `docs/MASTER_ACTION_PLAN.md`.

## Key Phase 3.2 Capabilities
- Manual status override API (`PATCH /api/devices/{id}/override`, `DELETE /api/devices/{id}/override`) with reason tracking.
- Device modal and sidebar expose override controls, optical attributes, and live link updates.
- Drag-to-position persists device coordinates (with dedupe safeguards) via `/api/devices/{id}/position`.
- Provisioning endpoint (`POST /api/devices/provision`) returns the created device, interfaces, and a broadcast message.

## Documentation
- `ROADMAP.md` - detailed timelines, dependencies, and phase scope
- `docs/ARCHITECTURE.md` - system diagram, data flow, and design rationale
- `docs/MASTER_ACTION_PLAN.md` - current priorities, risks, and ownership
- `docs/OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md` - deep dive into optical provisioning rules

## Development Guidelines
1. Keep the backend authoritative; frontend only renders API results.
2. Extending data models? Update SQLModel definitions, Pydantic responses, and tests together.
3. Emit Socket.IO events for every state-changing action so the UI stays live.
4. Document new behaviour before merging; start with the relevant doc listed above.
5. Stick to feature branches (`feature/<scope>`), open PRs against `main`, and require tests to pass.

Contributions that stay true to these principles keep UNOC predictable and easy to evolve. If documentation drifts, fix it alongside your code change.
