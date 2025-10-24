# UNOC - Copilot Working Agreement

**Context:** FTTH network emulator, Phase 3.2 complete, Phase 4 (Traffic Engine) in planning  
**Stack:** FastAPI + SQLModel + Socket.IO backend, Vue 3 + Vite + Cytoscape frontend, PostgreSQL 16

## Project Primer
- Backend is authoritative: device status, overrides, provisioning, and upcoming traffic metrics originate from FastAPI services.
- Frontend is a Vue 3 SPA with Pinia stores and Cytoscape for topology rendering; it consumes REST endpoints and Socket.IO events.
- Documentation must stay current-update `README.md`, `ROADMAP.md`, and relevant `docs/*.md` whenever behaviour changes.

## Coding Standards
1. **Type hints everywhere.** SQLModel and Pydantic models require explicit types; Vue components use TypeScript script setup.
2. **Tests before merge.** Add or update pytest cases when touching backend logic; use in-memory SQLite fixtures.
3. **Emit events on state change.** Any CRUD mutation must call `emit_to_all(...)` to keep clients in sync.
4. **Single status field.** Do not reintroduce multiple status flags-use `status_override` and `override_reason` when manual control is required.
5. **Error clarity.** Raise `HTTPException` with descriptive messages; provisioning should prefer structured `ProvisioningError`.

## Workflow
1. Work on feature branches (`feature/<scope>`), rebase on `main`, open PRs with green tests.
2. Use Docker Compose for backend + PostgreSQL; frontend runs via `npm run dev`.
3. Run `pytest -v` and `ruff check backend` before pushing backend changes; `npm run build` before shipping UI changes.
4. Update phase docs (`ROADMAP.md`, `docs/MASTER_ACTION_PLAN.md`) whenever a milestone completes or scope shifts.

## Common Patterns
- **Provisioning:** Use `ProvisioningService` to create devices/interfaces; never hand-roll inserts that bypass upstream validation.
- **Socket.IO:** Import `emit_to_all` via `get_emit_function()` in routes to avoid circular imports.
- **Frontend state:** Leverage Pinia for cross-component state (selected device, filters); rely on Cytoscape instance methods for graph updates.
- **Testing:** Prefer end-to-end API tests with FastAPI's async test client; seed data using helper fixtures.
- **Docs:** Architecture diagrams live in Markdown (`docs/ARCHITECTURE.md`). Update or create diagrams as code evolves.

## Reference Material
- `README.md` - project snapshot, quick start, feature matrix
- `ROADMAP.md` - milestones, dependencies, and phase deliverables
- `docs/ARCHITECTURE.md` - system diagram, data flow, design rationale
- `docs/MASTER_ACTION_PLAN.md` - active initiatives, risks, follow-ups
- `docs/OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md` - optical provisioning details
- `backend/api/routes.py` - canonical list of REST endpoints
- `frontend/src/components/DeviceSidebar.vue` - override UI implementation

When in doubt, keep it simple, document the change, and preserve real-time guarantees.
