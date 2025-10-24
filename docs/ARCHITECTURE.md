# UNOC Architecture

**Last updated:** 24 Oct 2025  
**Context:** Phase 3.2 complete, Phase 4 (Traffic Engine) in planning

UNOC emulates an FTTH access network with a FastAPI backend, SQLModel domain models, and a Vue 3 frontend. This document captures how the system is assembled after the Phase 3.2 milestone.

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Responsibilities](#component-responsibilities)
3. [Data Flow](#data-flow)
4. [Domain Model Snapshot](#domain-model-snapshot)
5. [Technology Rationale](#technology-rationale)
6. [Deployment Topology](#deployment-topology)
7. [Key Design Decisions](#key-design-decisions)
8. [What Changes in Phase 4](#what-changes-in-phase-4)

## System Overview
```
[ Vue 3 + Pinia + Cytoscape SPA ]
      | REST (`/api/*`) + Socket.IO (`/socket.io`)
      v
[ FastAPI backend + ProvisioningService + Socket.IO emitter ]
      | SQLModel ORM
      v
[ PostgreSQL 16 database ]
```
- Frontend renders the topology graph, device sidebar, and live metrics.
- Backend exposes CRUD endpoints, provisioning logic, manual overrides, and WebSocket events.
- PostgreSQL stores devices, interfaces, links, overrides, and optical attributes. Seed data populates an initial topology on first boot.

## Component Responsibilities
| Component | Key Modules | Responsibilities | Outbound Calls |
|-----------|-------------|------------------|----------------|
| FastAPI API | `backend/api/routes.py` | REST CRUD, provisioning endpoint, override endpoints, link management, seed operations | SQLModel sessions, Socket.IO emits |
| Provisioning Service | `backend/services/provisioning_service.py` | Validate upstream dependencies, create device and default interfaces, attach optical attributes, raise structured errors | Database session, WebSocket emitter |
| Socket.IO Layer | `backend/main.py` (`emit_to_all`) | Broadcast create/update/delete/override events to all clients | Frontend listeners |
| Database Layer | `backend/db.py`, `backend/models/core.py` | SQLModel schemas, async session management, seed helper | PostgreSQL |
| Vue UI | `frontend/src/App.vue`, `frontend/src/components/*` | Render topology, manage device sidebar/modal, handle drag-to-position and overrides | REST API, Socket.IO client |
| State Store | `frontend/src/stores` (Pinia) | Track selected device, filters, future traffic metrics | Local only |

## Data Flow
### Provisioning (Phase 1.5)
1. User submits `POST /api/devices/provision`.
2. `ProvisioningService` validates device type, parent container, and upstream dependencies.
3. Device plus default interfaces are persisted in one transaction.
4. Socket.IO broadcasts `device:created` and `interface:created` payloads.
5. Vue subscriber updates the topology graph and sidebar in real time.

### Manual Status Override (Phase 3.2)
1. UI triggers `PATCH /api/devices/{id}/override` with override status and reason.
2. Device row updates `status_override` and `override_reason`.
3. WebSocket event `device:updated` pushes the new payload to all clients.
4. Frontend displays the override badge and disables conflicting actions until cleared.
5. `DELETE /api/devices/{id}/override` removes the override and emits another update.

### Live Topology Updates (Phase 2 and later)
- CRUD operations emit `device:*`, `interface:*`, and `link:*` events.
- Socket.IO keeps all connected clients aligned without polling.
- Frontend listeners update Cytoscape nodes and edges in place.

## Domain Model Snapshot
| Entity | Key Fields | Notes |
|--------|------------|-------|
| `Device` | `id`, `name`, `device_type`, `status`, `status_override`, `override_reason`, `x`, `y`, optical attributes | Single source of truth for status; override metadata records manual intent |
| `Interface` | `id`, `device_id`, `name`, `interface_type`, `status` | Auto-created by provisioning or simple link helper |
| `Link` | `id`, `a_interface_id`, `b_interface_id`, `status`, `link_type` | Must satisfy L1-L9 optical validation rules |

SQLModel uses async sessions with PostgreSQL in runtime environments and in-memory SQLite for tests.

## Technology Rationale
- **FastAPI + SQLModel:** Type-hinted models double as schema and validation, async support underpins WebSockets, and OpenAPI docs come for free.
- **Socket.IO (ASGI):** Mature WebSocket transport with reconnection support, keeping drag operations and overrides responsive.
- **Vue 3 + Cytoscape:** Composition API keeps state modular, and Cytoscape handles graph layout and interaction with minimal custom code.
- **Docker Compose:** Reproducible local setup for PostgreSQL and the backend container; frontend runs separately via Vite.

## Deployment Topology
```
Developer host (Node + npm) runs `npm run dev`
            |
            v
Docker Compose (`docker compose up -d`)
    |- FastAPI backend (port 5001)
    |- PostgreSQL 16 with persistent volume
```
- Backend seeds demo data on first startup via `seed_if_empty`.
- Frontend production build (`npm run build`) outputs static assets for future hosting behind a reverse proxy.

## Key Design Decisions
- **Single status field with optional override:** Prevents V1-style divergence; override metadata sits beside the authoritative status.
- **Provisioning-first strategy:** Backend enforces topology and interface creation, leaving the UI focused on interaction.
- **Event-driven UI:** Every state change emits a WebSocket event so operators never refresh manually.
- **Tests before features:** 92 backend tests guard provisioning, optical rules, overrides, and coordinate persistence.

## What Changes in Phase 4
- Traffic engine introduces simulated throughput per device/interface with tariff-aware behaviour.
- WebSocket payloads will include traffic samples and congestion flags.
- Pinia store and Cytoscape overlays will expand to show traffic heatmaps and alerts.
- Documentation updates will land here and in `docs/11_traffic_engine_and_congestion.md` once designs solidify.
