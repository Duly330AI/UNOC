# WebSocket Integration

**Last updated:** 24 Oct 2025  
**Scope:** Socket.IO client setup in the Vue application and how events update UI state.

## Client Bootstrapping
- Socket.IO client is created inside `setupWebSocket()` (`frontend/src/App.vue:282-343`).
- Connection points to the same origin (`io()` with no explicit URL) so Vite dev proxy (`vite.config.ts:6-14`) forwards to FastAPI at `http://localhost:5001`.
- Connection flags:
  - `wsConnected` ref tracks session status (`frontend/src/App.vue:126-132`).
  - `wsStatus` computed class toggles the header badge (`frontend/src/App.vue:163-170`).

```ts
import { io } from 'socket.io-client'

let socket = io()
socket.on('connect', () => { wsConnected.value = true })
socket.on('disconnect', () => { wsConnected.value = false })
```

## Event Handlers
| Event | Handler location | Effect |
|-------|-----------------|--------|
| `device_created` | `frontend/src/App.vue:300-307` | Pushes new device into `devices` array (provisioning response broadcast). |
| `device:created` | `frontend/src/App.vue:309-316` | Adds direct `POST /api/devices` records. |
| `device:updated` | `frontend/src/App.vue:318-331` | Replaces device entry, matching by id. |
| `device:deleted` | `frontend/src/App.vue:333-339` | Removes device and clears selection if needed. |
| `interface:created` | `frontend/src/App.vue:341-344` | Pushes new interface for topology mapping. |
| `link:created` | `frontend/src/App.vue:346-349` | Appends Cytoscape edge descriptor. |
| `link:deleted` | `frontend/src/App.vue:351-354` | Filters removed link out of `links`. |

Each handler mutates local refs today. When Pinia stores replace these refs, convert the handlers to `deviceStore.upsertDevice(payload)` style actions (see `docs/08_pinia_store_design.md`).

## Error Handling and Reconnects
- Socket.IO automatically retries; the `disconnect` callback flips the header badge to red so operators notice (`App.vue:121-132`).
- Console logs are present to aid debugging; keep them until a toast mechanism is available.
- Add-on strategy (Phase 4) for noisy traffic events: throttle `interface:created` and `link:created` inserts using requestAnimationFrame or a mutation buffer when traffic updates ship.

## Testing the Stream
1. Start backend (`docker compose up -d`) so the Socket.IO endpoint is reachable.
2. Run frontend dev server (`npm run dev`) and open the browser.
3. Perform an action that emits events (for example, override a device or provision a new one).
4. Watch the console logs tagged with emojis (e.g., `?? Device created`) to verify receipt.
5. Toggle the backend container to observe `disconnect`/`connect` transitions.

For unit testing, mock Socket.IO using a stub emitter and assert that handlers update the refs (or Pinia state) as expected. Wrapping the socket instance in a composable (`useSocket`) will make this easier once stores are introduced.

## Related Docs
- `docs/05_websocket_events.md` - Canonical event names and payload shapes.
- `docs/07_frontend_architecture.md` - Component hierarchy consuming these events.
- `docs/08_pinia_store_design.md` - How stores will react to incoming payloads.
