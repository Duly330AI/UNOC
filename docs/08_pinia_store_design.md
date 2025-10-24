# Pinia Store Design

**Last updated:** 24 Oct 2025  
**Scope:** Current state management approach and the planned Pinia modules.

Pinia is registered globally in `frontend/src/main.ts:5-8`, but Phase 3 still keeps the primary state inside `App.vue`. This document captures the existing reactive refs and maps them to the Pinia stores that will ship next.

## Current Reactive State (App.vue)
| Ref | Type | Purpose | Source |
|-----|------|---------|--------|
| `devices` | `Device[]` | Canvas nodes and sidebar listings | `frontend/src/App.vue:94-111` |
| `interfaces` | `Interface[]` | Lookup for topology edges | `frontend/src/App.vue:112-118` |
| `links` | `Link[]` | Cytoscape edges | `frontend/src/App.vue:119-125` |
| `selectedDevice` | `Device \| null` | Drives `DeviceSidebar` | `frontend/src/App.vue:137-142` |
| `isLinkMode` | `boolean` | Toggles link creation overlay | `frontend/src/App.vue:146-152` |
| `isAddModalOpen` | `boolean` | Controls `DeviceModal` | `frontend/src/App.vue:133-135` |
| `isLinkModalOpen` | `boolean` | Controls `LinkModal` | `frontend/src/App.vue:153-160` |
| `wsConnected` | `boolean` | Socket status flag | `frontend/src/App.vue:126-132` |

These refs are mutated by REST helpers (`fetchData`, `handleCreateDevice`, etc.) and by WebSocket listeners (`setupWebSocket` at `frontend/src/App.vue:282-343`).

## Planned Store Modules
| Store | State | Key Actions |
|-------|-------|-------------|
| `useDeviceStore` | `devices`, `selectedDeviceId`, `loading`, `error` | `fetchDevices`, `selectDevice`, `upsertDevice`, `removeDevice`, `setOverride` |
| `useLinkStore` | `links`, `interfaces`, `linkMode`, `pendingLink` | `fetchLinks`, `fetchInterfaces`, `beginLinkMode`, `createLink`, `deleteLink` |
| `useUiStore` | `isDeviceModalOpen`, `isLinkModalOpen`, `wsConnected` | `openDeviceModal`, `openLinkModal`, `setWsStatus`, `resetModals` |

Stores live under `frontend/src/stores/`. Each module exports a factory `useXStore` created via `defineStore`.

### Example: Device Store Skeleton
```ts
// frontend/src/stores/deviceStore.ts
import { defineStore } from 'pinia'
import type { Device } from '@/types'

export const useDeviceStore = defineStore('device', {
  state: () => ({
    devices: [] as Device[],
    selectedDeviceId: null as number | null,
    loading: false,
    error: '' as string | null,
  }),

  getters: {
    selectedDevice(state) {
      return state.devices.find(d => d.id === state.selectedDeviceId) ?? null
    },
    deviceCount: state => state.devices.length,
  },

  actions: {
    async fetchDevices() {
      this.loading = true
      try {
        const res = await fetch('/api/devices')
        this.devices = await res.json()
      } finally {
        this.loading = false
      }
    },
    selectDevice(id: number | null) {
      this.selectedDeviceId = id
    },
    upsertDevice(payload: Device) {
      const idx = this.devices.findIndex(d => d.id === payload.id)
      if (idx >= 0) this.devices[idx] = payload
      else this.devices.push(payload)
    },
    removeDevice(id: number) {
      this.devices = this.devices.filter(d => d.id !== id)
    },
  },
})
```

### Wiring the Store
Replace the refs in `App.vue` with Pinia getters/actions:
```ts
import { useDeviceStore } from '@/stores/deviceStore'
const deviceStore = useDeviceStore()

const devices = computed(() => deviceStore.devices)
const selectedDevice = computed(() => deviceStore.selectedDevice)

await deviceStore.fetchDevices()
```

Socket event handlers should call store actions instead of mutating refs directly:
```ts
socket.on('device:updated', (payload) => {
  deviceStore.upsertDevice(payload)
})
```

## Store Interaction with Components
- `NetworkGraph.vue` consumes device/link arrays as props. When Pinia lands, keep the prop interface intact and map getters in `App.vue`.
- `DeviceSidebar.vue` emits `overrideUpdated` (line `frontend/src/components/DeviceSidebar.vue:283-324`); the store action `setOverride` should perform the PATCH request then refresh the device locally.
- `LinkModal.vue` already emits a structured payload (`frontend/src/components/LinkModal.vue:57-80`); `useLinkStore.createLink` can handle the POST and store mutation.

## Why Pinia
- Shared state: avoids prop drilling as more components are introduced.
- DevTools: inspect actions and time-travel state, invaluable during link-mode debugging.
- Type support: `defineStore` integrates with TypeScript without manual typings.

## Migration Checklist
1. Create `frontend/src/stores/deviceStore.ts`, `linkStore.ts`, and `uiStore.ts` based on the tables above.
2. Replace refs in `App.vue` with store getters/actions.
3. Update `DeviceSidebar.vue` to import the device store (so it can call `setOverride` directly instead of emitting up).
4. Add unit tests for critical actions (e.g., `upsertDevice`, `removeDevice`).
5. Document the store APIs and update this file with final state after implementation.

## Related Reading
- Pinia documentation: https://pinia.vuejs.org/core-concepts/
- `docs/07_frontend_architecture.md` - overall component structure.
- `docs/09_websocket_integration.md` - event handlers that feed store updates.
