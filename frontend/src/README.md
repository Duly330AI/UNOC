# UNOC Frontend Guide

**Last updated:** 24 Oct 2025  
**Tech stack:** Vue 3, Vite, TypeScript, Pinia, Cytoscape.js, Socket.IO client

## Quick Start
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Backend must be running on `http://localhost:5001` (use `docker compose up -d`). Vite proxies `/api/*` requests to the backend according to `vite.config.ts`.

## Build and Preview
```bash
npm run build      # emits dist/
npm run preview    # serve the production bundle locally
```

The `dist/` folder can be copied into a static web server image during deployment.

## Project Structure
```
src/
|-- App.vue                # Root component, sockets, data fetching
|-- main.ts                # Vue + Pinia bootstrap
|-- style.css              # Global styles
|-- components/
|   |-- NetworkGraph.vue   # Cytoscape canvas
|   |-- DeviceSidebar.vue  # Device details + overrides
|   |-- DeviceModal.vue    # Device create/update form
|   |-- LinkModal.vue      # Link creation workflow
|   `-- ConfirmDialog.vue  # Generic confirmation modal
`-- stores/                # (planned Pinia modules)
```

## Key Entry Points
- **App.vue** - orchestrates REST calls, socket listeners, and modal visibility.
- **NetworkGraph.vue** - renders nodes/edges with Cytoscape and emits selection/drag events.
- **DeviceSidebar.vue** - shows tabs, calls override APIs, and manages interface fetches.
- **DeviceModal.vue** & **LinkModal.vue** - emit structured payloads for create/submit actions.

## IDE Setup
- Install **Volar** (Vue language features) and **TypeScript Vue Plugin** in VS Code.
- Enable **TypeScript > Strict** for better type checking on `ref` values.
- Recommended extensions: ESLint, Prettier (optional), Vue Language Features (Volar).

## Common Tasks
| Task | Steps |
|------|-------|
| Add a component | Create file in `src/components/`, import into the parent component, register inside `<script setup>`. |
| Add a sidebar tab | Follow the pattern in `DeviceSidebar.vue:200-239` (see `docs/10_ui_patterns_and_examples.md`). |
| Call the API | Use `fetch` inside `async` helpers, mirror the request models exposed by FastAPI (`App.vue:209-252`). |
| Listen to sockets | Extend `setupWebSocket()` in `App.vue:282-343` or move listeners into a Pinia action. |
| Manage state | Until Pinia stores are in place, use refs in `App.vue`; see `docs/08_pinia_store_design.md` for the planned module layout. |

## Testing Status
The frontend currently relies on manual verification while backend pytest coverage guards server contracts. Component/unit tests will be introduced alongside the Pinia migration. When adding tests, colocate them under `src/__tests__` and run them with Vitest.

## Helpful Documentation
- `docs/07_frontend_architecture.md` - Component hierarchy and data flow.
- `docs/08_pinia_store_design.md` - State management blueprint.
- `docs/09_websocket_integration.md` - Socket event handling.
- `docs/10_ui_patterns_and_examples.md` - Step-by-step UI patterns.
