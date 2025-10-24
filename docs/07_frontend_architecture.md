# Frontend Architecture

**Last updated:** 24 Oct 2025  
**Scope:** Vue 3 application structure, build toolchain, and component interactions.

The UNOC frontend is a Vite-powered Vue 3 SPA written in TypeScript. It renders the fibre topology, device forms, and management sidebar while staying in sync with the backend via REST and Socket.IO.

## Project Layout
```
frontend/
|-- package.json
|-- vite.config.ts
`-- src/
    |-- App.vue
    |-- main.ts
    |-- style.css
    |-- components/
    |   |-- ConfirmDialog.vue
    |   |-- DeviceModal.vue
    |   |-- DeviceSidebar.vue
    |   |-- LinkModal.vue
    |   `-- NetworkGraph.vue
    `-- stores/        (planned Pinia modules)
```

- `main.ts` wires Vue, Pinia, and global styles (`frontend/src/main.ts:5-8`).
- `vite.config.ts` proxies `/api/*` calls to the FastAPI server and serves the dev app on port 5173.
- Components live under `components/` and use `<script setup lang="ts">` for concise TypeScript syntax.

## Build and Dev Tooling
| Command | Description |
|---------|-------------|
| `npm install` | Install frontend dependencies (Node 20+ recommended). |
| `npm run dev` | Start Vite dev server with hot module replacement. |
| `npm run build` | Produce production bundle in `frontend/dist`. |
| `npm run preview` | Serve the production bundle locally for smoke tests. |

Vite handles TypeScript transpilation, CSS preprocessing, and static asset bundling. The build artefacts can be served by any static server (for example, nginx in a future Docker image). The current `docker-compose.yml` focuses on the backend; the frontend runs separately during development.

## Component Hierarchy
```
App.vue
|-- NetworkGraph.vue        (topology canvas)
|-- DeviceModal.vue         (create/update form)
|-- LinkModal.vue           (link creation wizard)
`-- DeviceSidebar.vue       (details + overrides)
    |-- Tab: Overview       (inline in component)
    |-- Tab: Interfaces     (fetches /api/devices/{id}/interfaces)
    `-- Tab: Optical        (conditional for optical roles)
```

- `App.vue` owns application state (`devices`, `links`, `interfaces`, `selectedDevice`) using Vue refs (`frontend/src/App.vue:94-145`).
- `NetworkGraph.vue` renders Cytoscape nodes/edges and emits `deviceClick` and `positionUpdated` events (`frontend/src/components/NetworkGraph.vue:22-47`, `66-132`).
- `DeviceModal.vue` and `LinkModal.vue` expose forms with `v-model` bindings that emit `submit` events to `App.vue`.
- `DeviceSidebar.vue` manages tab state, fetches interfaces, and performs override API calls (`frontend/src/components/DeviceSidebar.vue:241-324`).

## Data Flow
1. `App.vue` fetches devices, interfaces, and links on mount (`frontend/src/App.vue:266-276`).
2. `NetworkGraph.vue` receives these collections as props and renders Cytoscape nodes/edges (`frontend/src/components/NetworkGraph.vue:190-237`).
3. When a user taps a node, `NetworkGraph` emits `deviceClick`; `App.vue` updates `selectedDevice` (`frontend/src/App.vue:172-198`).
4. `DeviceSidebar.vue` reacts to the new `device` prop, allows overrides, and emits `overrideUpdated` to trigger `fetchData`.
5. WebSocket events keep the lists hot without manual refresh, appending or removing entities as they arrive.

## TypeScript Conventions
- All components use `<script setup lang="ts">` with inline interfaces to type props, emits, and local state.
- Refs are declared with explicit generics when storing arrays (`const devices = ref<Device[]>([])`).
- Props are typed via `defineProps` and event contracts via `defineEmits` (for example, `LinkModal.vue:33-53`).
- Keep shared interfaces in future Pinia stores (`frontend/src/stores`) to avoid duplication as the app grows.

## Pinia Integration Strategy
Pinia is initialised globally (`frontend/src/main.ts:5-8`), but state currently lives in `App.vue`. Phase 4 will move shared state into modules under `frontend/src/stores/`:
- `deviceStore` for device collections and selection.
- `linkStore` for link list and link-mode toggles.
- `uiStore` for modal visibility and transient flags.

When those stores are introduced, inject them in `App.vue` and pass computed values to child components instead of raw refs.

## Deployment Notes
- `npm run build` writes to `frontend/dist`; copy that folder into a static server image or reverse-proxy through the backend.
- During development, run the frontend with `npm run dev` and the backend via `docker compose up -d`. Vite's proxy forwards `/api` calls to FastAPI on `http://localhost:5001`.
- For containerised builds, ensure the production server honours the same `/api` prefix so the proxy configuration remains valid.

## Related Documents
- `docs/08_pinia_store_design.md` - State management blueprint.
- `docs/09_websocket_integration.md` - Socket.IO setup and event contracts.
- `docs/10_ui_patterns_and_examples.md` - Component extension patterns.
