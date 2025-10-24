# UI Patterns and Examples

**Last updated:** 24 Oct 2025  
**Scope:** Common UI changes in the Vue 3 application and how to implement them safely.

## Add a Tab to DeviceSidebar
1. **Create the tab component** under `frontend/src/components/` (for example, `DeviceSidebarHealthTab.vue`). Accept the `device` prop so the parent can pass the selected device.
2. **Import and register** the component near the top of `DeviceSidebar.vue`.
3. **Extend the tab navigation**:
   ```vue
   <button
     :class="['tab-btn', { active: activeTab === 'health' }]"
     @click="activeTab = 'health'"
   >
     Health
   </button>
   ```
4. **Render the tab body** inside the tab switcher (`frontend/src/components/DeviceSidebar.vue:200-239`):
   ```vue
   <div v-else-if="activeTab === 'health'" class="tab-content">
     <DeviceSidebarHealthTab :device="device" />
   </div>
   ```
5. If the tab needs backend data, mirror the `loadInterfaces()` pattern (`DeviceSidebar.vue:261-280`) with its own loading flag and fetch helper.

## Trigger Device Overrides
- Use the provided helpers (`setOverride` and `clearOverride` at `DeviceSidebar.vue:283-324`).
- Emit `overrideUpdated` so `App.vue` refreshes the device list (`frontend/src/App.vue:209-223`).
- When adding new override buttons, follow the existing `btn-override` styling block near `DeviceSidebar.vue:417-466`.

## Create or Update a Modal
1. Copy structure from `DeviceModal.vue` or `LinkModal.vue`:
   - Overlay listens to `@click.self` to close when the background is clicked (`DeviceModal.vue:4-11`).
   - All fields bind via `v-model` to a `ref` object (`DeviceModal.vue:26-85`).
   - Emit `close` and `submit` events explicitly (`DeviceModal.vue:101-128`).
2. Reset form data with a `watch` on the `isOpen` prop (`LinkModal.vue:69-78`).
3. Expose a `handleSubmit` that validates input and emits the payload (`LinkModal.vue:82-99`).

## Manage Loading and Empty States
- Use a tri-state pattern: loading, empty, populated (`DeviceSidebar.vue:206-238`).
  ```vue
  <div v-if="loadingInterfaces" class="loading">Loading interfaces...</div>
  <div v-else-if="interfaces.length === 0" class="empty-state">No interfaces found</div>
  <div v-else class="interfaces-list">...</div>
  ```
- For new lists, create matching CSS blocks for `.loading` and `.empty-state` following the existing styles (`DeviceSidebar.vue:342-416`).

## Bind Forms to API Calls
- Keep the payload shape identical to the backend request model. Example from `DeviceModal.vue:146-190`:
  ```ts
  emit('submit', {
    name: form.name,
    device_type: form.device_type,
    status: form.status,
    x: form.x ?? 0,
    y: form.y ?? 0,
    tx_power_dbm: form.tx_power_dbm,
    sensitivity_min_dbm: form.sensitivity_min_dbm,
    insertion_loss_db: form.insertion_loss_db,
  })
  ```
- Wrap `fetch` calls in `try/catch` and surface errors through console logs or future toast notifications (`App.vue:209-252`).

## Work with the Network Graph
- Cytoscape initialisation lives in `NetworkGraph.vue:50-137`.
- Adding new visuals:
  - Extend the style array with selectors for custom device types or edge emphasis.
  - Use `cy.on('tap', ...)` to capture interactions (`NetworkGraph.vue:103-132`).
- Device drag handling emits `positionUpdated`; consume it in `App.vue` (`frontend/src/App.vue:199-223`) to persist coordinates.
- When adding overlays (e.g., traffic heatmaps), leverage `updateGraph()` (`NetworkGraph.vue:190-274`) to inject extra data fields (`node.data('load')`) and render them with custom styles.

## Coding Conventions Recap
- Prefer `<script setup lang="ts">`.
- Keep TypeScript interfaces close to the component unless they are shared across multiple files (future `@/types` module).
- Style blocks are `scoped`; utilities should go into `frontend/src/style.css` or a new unscoped stylesheet if they are reused.

## Related References
- `docs/07_frontend_architecture.md` - High-level component relationships.
- `docs/09_websocket_integration.md` - Real-time updates that drive UI changes.
- `frontend/src/App.vue` - Canonical patterns for forms, API calls, and socket listeners.
