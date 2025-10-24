# 🗺️ UNOC V2 - Roadmap

**Project Start:** October 14, 2025  
**Current Status:** Phase 1 ✅ + Phase 1.5 ✅ + Phase 2 ✅  
**Latest Update:** October 15, 2025 - **WebSockets Complete!**  
**Next Phase:** Phase 3 (Management UI)

---

## 📊 Phase Overview

| Phase | Status | Duration | Completion |
|-------|--------|----------|------------|
| Phase 1: Foundation | ✅ Complete | 1 day | Oct 14, 2025 |
| **Phase 1.5: Optical Network** | ✅ **Complete** | **1 day** | **Oct 15, 2025** |
| **Phase 2: Real-Time** | ✅ **Complete** | **1 hour** | **Oct 15, 2025** |
| **Phase 3.1: Core Management** | ✅ **Complete** | **30 min** | **Oct 15, 2025** |
| **Phase 3.2: Status Override** | ✅ **Complete** | **2 hours** | **Oct 15, 2025** |
| Phase 4: Traffic | 📋 Planned | ~5 days | TBD |
| Phase 5: Production | 📋 Planned | ~7 days | TBD |

**Total Estimated:** ~18 days from start to production-ready MVP

---

## ✅ PHASE 1.5: OPTICAL NETWORK FOUNDATION (COMPLETE)

**Goal:** Build complete optical network device provisioning system

**Date:** October 15, 2025

### **Device Types Extended (100%)**
- [x] 14 device types (from original 3)
  - 8 Active: BACKBONE_GATEWAY, CORE_ROUTER, EDGE_ROUTER, OLT, AON_SWITCH, ONT, BUSINESS_ONT, AON_CPE
  - 2 Container: POP, CORE_SITE
  - 4 Passive: ODF, NVT, SPLITTER, HOP
- [x] Optical attributes (tx_power_dbm, sensitivity_min_dbm, insertion_loss_db)
- [x] Parent container support

### **Provisioning Service (100%)**
- [x] ProvisioningService implementation (`backend/services/provisioning_service.py`)
- [x] Auto-create interfaces based on device type
  - OLT: mgmt0 + lo0 + 8 PON ports
  - AON_SWITCH: mgmt0 + lo0 + 24 Ethernet ports
  - ONT: eth0
  - SPLITTER: in0 + 32 out ports
  - All types properly configured
- [x] Upstream dependency validation
  - EDGE requires CORE/BACKBONE
  - OLT/AON requires EDGE
  - ONT requires OLT
  - CPE requires AON
- [x] Validation bypass option (validate_upstream=False)
- [x] Duplicate name prevention

### **Link Type Rules (100%)**
- [x] L1-L9 link validation rules (`backend/constants/link_rules.py`)
  - L1: BACKBONE ↔ CORE
  - L2: CORE ↔ EDGE
  - L3: EDGE ↔ OLT (GPON)
  - L4: EDGE ↔ AON
  - L5: OLT ↔ ONT
  - L6: OLT ↔ BUSINESS_ONT
  - L7: AON ↔ CPE
  - L8: Passive inline
  - L9: Peer-to-peer redundancy
- [x] Validation functions (validate_link_between_devices, etc.)

### **API Integration (100%)**
- [x] POST /api/devices/provision endpoint
- [x] Request model (ProvisionDeviceRequest)
- [x] Response model (device + interfaces + message)
- [x] Error handling (400 for validation failures)
- [x] WebSocket event emission

### **Testing (100%)**
- [x] 92 tests passing (from original 4)
  - 20 tests: Device types & optical attributes
  - 15 tests: Provisioning service
  - 32 tests: Link type rules
  - 14 tests: Dependency validation
  - 11 tests: API endpoint
- [x] 100% test pass rate
- [x] Ruff clean (no lint errors)

### **Documentation (100%)**
- [x] OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md
- [x] Complete usage examples
- [x] API documentation

**Deliverables:**
- ✅ 14 device types with optical attributes
- ✅ Smart provisioning with dependency validation
- ✅ L1-L9 link type rules
- ✅ POST /api/devices/provision endpoint
- ✅ 92 tests passing (100% pass rate)

**Date Completed:** October 15, 2025

---

## ✅ PHASE 1: FOUNDATION (COMPLETE)

**Goal:** Build clean foundation with simplified data model

**Completed Tasks:**

### **Backend (100%)**
- [x] SQLModel models (Device, Interface, Link) with 1 status field
- [x] FastAPI REST API (CRUD endpoints)
- [x] PostgreSQL database setup
- [x] Docker Compose (backend + database)
- [x] Database connection with async support
- [x] CASCADE DELETE constraints
- [x] Seed service (demo topology generator)
- [x] Manual seed endpoint (`POST /api/seed`)
- [x] Auto-seed on startup (if DB empty)
- [x] Health check endpoint (`GET /health`)

### **Testing (100%)**
- [x] Pytest configuration
- [x] SQLite in-memory for tests
- [x] conftest.py fixtures
- [x] 4 integration tests passing:
  - Create device
  - List devices
  - Delete device
  - 404 handling

### **Frontend (100%)**
- [x] Vue 3 + TypeScript + Vite setup
- [x] Cytoscape.js integration
- [x] NetworkGraph component
- [x] API data fetching (devices, interfaces, links)
- [x] Interface-to-device mapping (for link rendering)
- [x] Status color coding (green=UP, orange=DEGRADED, red=DOWN)
- [x] Hierarchical layout visualization
- [x] Hot reload (Vite HMR)

### **Documentation (100%)**
- [x] README.md with Quick Start
- [x] ARCHITECTURE.md with design decisions
- [x] ROADMAP.md (this file)

**Deliverables:**
- ✅ Working REST API (9 devices, 7 links seeded)
- ✅ Working frontend visualization
- ✅ 4 tests passing
- ✅ Docker setup
- ✅ Complete documentation

**Screenshot Evidence:**
- Browser showing 9 devices (Router1-2, Switch1-2, OLT1, ONT1-4)
- 7 green/orange links connecting devices
- Hierarchical topology layout
- Status colors working correctly

**Date Completed:** October 14, 2025

---

## 🚧 PHASE 2: REAL-TIME (COMPLETE ✅)

**Goal:** Add WebSocket support for live updates

**Date:** October 15, 2025  
**Duration:** ~1 hour

### **Backend Tasks**

- [x] Install `python-socketio` (FastAPI integration) ✅
- [x] Create WebSocket server in `backend/main.py` ✅
- [x] Define event types: ✅
  - `device:created` - New device added
  - `device:updated` - Device status/position changed
  - `device:deleted` - Device removed
  - `link:created` - New link added
  - `interface:created` - New interface added
- [x] Emit events on CRUD operations ✅
- [x] CORS configuration for multiple ports ✅
- [x] WebSocket health check ✅

### **Frontend Tasks**

- [x] Install `socket.io-client` ✅
- [x] Create WebSocket connection in `App.vue` ✅
- [x] Listen to events ✅
- [x] Update reactive data on events ✅
- [x] Trigger Cytoscape refresh ✅
- [x] Connection status indicator (connected/disconnected) ✅
- [x] Auto-reconnect on disconnect ✅

### **Testing**

- [x] Test event emission (create device → frontend receives event) ✅
- [x] Test multiple clients (fanout) ✅
- [x] Test reconnection logic ✅
- [x] 8 WebSocket integration tests ✅

### **Deliverables**

- ✅ Create device via API → Frontend updates automatically
- ✅ Update device status → All connected clients see change
- ✅ Delete device → Removed from all frontends instantly
- ✅ Connection indicator in UI (🟢 Live / 🔴 Offline)
- ✅ WebSocket server running on port 5001
- ✅ Multiple clients supported (fanout working)

**Success Criteria:**
- ✅ Zero manual browser refresh needed
- ✅ All clients stay in sync
- ✅ Reconnection works after server restart
- ✅ WebSocket connection established in browser

**Date Completed:** October 15, 2025

---

## 📋 PHASE 3: MANAGEMENT (IN PROGRESS)

**Goal:** Build management UI for devices and links

**Date Started:** October 15, 2025

### **Part 1: Core Management** ✅ COMPLETE

**Features:**
- [x] Delete confirmation dialog ✅
- [x] Drag & drop device positioning ✅
- [x] Position auto-save to database ✅
- [x] Click link to delete ✅
- [x] WebSocket sync for position updates ✅
- [x] WebSocket sync for link deletion ✅

**Deliverables:**
- ✅ Safe device deletion with modal
- ✅ Interactive graph (drag devices)
- ✅ Link management (click to delete)
- ✅ Real-time multi-client sync

**Date Completed:** October 15, 2025

### **Part 2: Status Override** ✅ COMPLETE

**Features:**
- [x] Manual status override button ✅
- [x] Override indicator badge (visual) ✅
- [x] Override reason display ✅
- [x] Clear override button ✅
- [x] WebSocket sync for overrides ✅

**Deliverables:**
- ✅ Status override panel in sidebar
- ✅ Visual indicator (🔒 badge)
- ✅ Admin force UP/DOWN capability
- ✅ Override reason tracking
- ✅ Real-time updates via WebSocket

**Date Completed:** October 15, 2025

---

## 📋 PHASE 4: TRAFFIC (FUTURE)

### **Frontend Tasks**

- [ ] Install `socket.io-client`
- [ ] Create WebSocket connection in `App.vue`
- [ ] Listen to events
- [ ] Update Pinia store on events
- [ ] Trigger Cytoscape refresh
- [ ] Connection status indicator (connected/disconnected)
- [ ] Auto-reconnect on disconnect

### **Testing**

- [ ] Test event emission (create device → frontend receives event)
- [ ] Test multiple clients (fanout)
- [ ] Test reconnection logic
- [ ] Test correlation_id passthrough

### **Deliverables**

- ✅ Create device via API → Frontend updates automatically
- ✅ Update device status → All connected clients see change
- ✅ Delete device → Removed from all frontends instantly
- ✅ Connection indicator in UI

**Success Criteria:**
- Zero manual browser refresh needed
- All clients stay in sync
- Reconnection works after server restart

---

## 📋 PHASE 3: MANAGEMENT (PLANNED)

**Goal:** Add UI for managing devices and links

**Estimated Duration:** 3 days (~10-12 hours coding)

### **Device Management**

- [ ] Device creation form (modal)
- [ ] Device type selector (ROUTER, SWITCH, OLT, ONT, SERVER)
- [ ] Position picker (click on canvas)
- [ ] Delete confirmation dialog
- [ ] Bulk device import (CSV/JSON)

### **Link Management**

- [ ] Visual link creation:
  - Click device A
  - Click device B
  - Auto-create interfaces if needed
  - Create link
- [ ] Link deletion (click link → delete button)
- [ ] Interface selection (if device has multiple ports)
- [ ] Hardware catalog integration (optional):
  - Define device models (Cisco ASR9k, Juniper MX, etc.)
  - Auto-create interfaces based on model

### **Status Override**

- [ ] Manual status override (Admin can force device UP/DOWN)
- [ ] Override indicator (visual badge: "Manual Override")
- [ ] Override history (who changed what when)
- [ ] Clear override (revert to computed status)

### **Bulk Operations**

- [ ] Multi-select devices (Ctrl+Click, drag-to-select)
- [ ] Bulk status change
- [ ] Bulk delete
- [ ] Bulk move (drag multiple devices)

### **Deliverables**

- ✅ Create network topology entirely from UI (no API calls)
- ✅ Drag & drop interface for link creation
- ✅ Hardware catalog (optional, if time permits)
- ✅ Status override working

**Success Criteria:**
- Non-technical user can build topology in UI
- No need to use `curl` or Postman

---

## 📋 PHASE 4: TRAFFIC (PLANNED)

**Goal:** Simulate network traffic and detect congestion

**Estimated Duration:** 5 days (~16-20 hours coding)

### **Tariff System**

- [ ] Tariff model (name, upload_kbps, download_kbps)
- [ ] CRUD API for tariffs
- [ ] Assign tariff to ONT (FK: tariff_id)
- [ ] Default tariffs seeded (100Mbps, 500Mbps, 1Gbps)

### **Traffic Generation**

- [ ] Generate upload/download traffic per ONT based on tariff
- [ ] Randomization (±10% variance for realism)
- [ ] Time-of-day variation (peak hours = higher usage)
- [ ] Asymmetric traffic (download > upload for residential)

### **Traffic Aggregation**

- [ ] Sum child traffic to parent:
  - ONT1-4 → OLT1
  - OLT1 → Switch1
  - Switch1 → Router1
- [ ] Device traffic = sum of all child traffic
- [ ] Link traffic = sum of traffic flowing through link

### **Congestion Detection**

- [ ] Define capacity per link (e.g., 1Gbps, 10Gbps)
- [ ] Utilization = (traffic / capacity) * 100
- [ ] Congestion threshold: 80% utilization
- [ ] Hysteresis: Alert at 80%, clear at 70%
- [ ] Congestion status: Link changes to DEGRADED

### **Traffic Visualization**

- [ ] Show utilization % on links (tooltip or label)
- [ ] Color code by utilization:
  - 0-50%: Green
  - 50-80%: Yellow
  - 80-100%: Red
- [ ] Animated traffic flow (particles moving along links)

### **Traffic Metrics**

- [ ] Total network throughput
- [ ] Per-device throughput
- [ ] Per-link utilization
- [ ] Congestion alerts (list of congested links)

### **Deliverables**

- ✅ Tariff system working
- ✅ Traffic generated based on tariffs
- ✅ Traffic aggregation correct (parent = sum of children)
- ✅ Congestion detection with hysteresis
- ✅ Visual indicators on links

**Success Criteria:**
- Create ONT with 1Gbps tariff → See traffic generated
- Traffic aggregates correctly to OLT → Switch → Router
- Link hits 80% utilization → Changes to DEGRADED
- Visual traffic flow animation working

---

## 📋 PHASE 5: PRODUCTION (PLANNED)

**Goal:** Make UNOC production-ready

**Estimated Duration:** 7 days (~24-30 hours coding)

### **Authentication**

- [ ] JWT token-based auth
- [ ] Login endpoint (`POST /api/auth/login`)
- [ ] Token refresh endpoint
- [ ] Password hashing (bcrypt)
- [ ] User model (username, password_hash, role)

### **Authorization**

- [ ] Role-based access control (RBAC):
  - `admin` - Full access
  - `operator` - Read-only + status override
  - `viewer` - Read-only
- [ ] Endpoint permissions (decorator: `@require_role("admin")`)
- [ ] Frontend permission checks (hide buttons for viewers)

### **Audit Logging**

- [ ] Audit model (user, action, timestamp, details)
- [ ] Log all mutations:
  - Device created/updated/deleted
  - Link created/deleted
  - Status override
  - Tariff changes
- [ ] Audit log viewer (filterable table)

### **Monitoring**

- [ ] Prometheus metrics:
  - Request count by endpoint
  - Response time (p50, p95, p99)
  - Error rate
  - Active WebSocket connections
  - Database connection pool usage
- [ ] Grafana dashboards:
  - API performance
  - Traffic statistics
  - Congestion alerts
  - System health (CPU, memory, disk)

### **CI/CD Pipeline**

- [ ] GitHub Actions:
  - Run tests on PR
  - Lint code (ruff, eslint)
  - Build Docker images
  - Push to registry (Docker Hub or GHCR)
- [ ] Deployment script (Kubernetes YAML):
  - Backend deployment
  - Frontend deployment (Nginx)
  - PostgreSQL StatefulSet
  - Redis deployment (session storage)
  - Ingress (HTTPS with cert-manager)

### **Observability**

- [ ] Structured logging (JSON format)
- [ ] Log aggregation (Loki or ELK)
- [ ] Error tracking (Sentry)
- [ ] Distributed tracing (Jaeger, optional)

### **Performance**

- [ ] Database indexing (on frequently queried fields)
- [ ] Query optimization (EXPLAIN ANALYZE)
- [ ] Redis caching (for expensive queries)
- [ ] Frontend bundle optimization (lazy loading)
- [ ] CDN for static assets

### **Deliverables**

- ✅ Production-ready authentication
- ✅ RBAC working
- ✅ Audit log complete
- ✅ Prometheus + Grafana setup
- ✅ CI/CD pipeline working
- ✅ HTTPS with Let's Encrypt
- ✅ Kubernetes deployment

**Success Criteria:**
- Deploy to production cluster
- Handle 100+ concurrent users
- 99.9% uptime
- All metrics visible in Grafana
- Security audit passed

---

## 🎯 Milestone Summary

| Milestone | Date | Status |
|-----------|------|--------|
| Phase 1: Foundation Complete | Oct 14, 2025 | ✅ Done |
| Phase 2: WebSockets Complete | TBD | 🚧 Next |
| Phase 3: Management Complete | TBD | 📋 Planned |
| Phase 4: Traffic Complete | TBD | 📋 Planned |
| Phase 5: Production Ready | TBD | 📋 Planned |
| **V2.0 Launch** | **TBD (~18 days)** | 📋 **Target** |

---

## 🚀 Post-Launch (FUTURE)

### **Advanced Features (After V2.0)**

- [ ] Topology auto-discovery (SNMP/LLDP)
- [ ] Alerting system (email, Slack, PagerDuty)
- [ ] Historical data (time-series DB like TimescaleDB)
- [ ] Topology comparison (diff between states)
- [ ] Automated testing (topology validation)
- [ ] Multi-tenancy (separate topologies per customer)
- [ ] REST API v2 (GraphQL for complex queries)
- [ ] Mobile app (React Native)

### **Scalability (If Needed)**

- [ ] Migrate to GO for traffic engine (if Python too slow)
- [ ] Event sourcing (store all events, rebuild state)
- [ ] CQRS (separate read/write models)
- [ ] Horizontal scaling (multiple backend instances)
- [ ] Database sharding (if single DB too slow)

---

## 📝 Decision Log

### **Decisions Made**

| Date | Decision | Rationale |
|------|----------|-----------|
| Oct 14, 2025 | Use Cytoscape.js instead of D3.js | 4x less code, better for network graphs, superior LLM compatibility |
| Oct 14, 2025 | 1 status field (not 5) | Simplicity, avoid V1 confusion |
| Oct 14, 2025 | Auto-create interfaces (not hardware catalog) | MVP speed, catalog can be added in Phase 3 |
| Oct 14, 2025 | API-first for links (not drag & drop) | Backend foundation first, UI later |
| Oct 14, 2025 | No traffic system in Phase 1 | Foundation first, features later |
| Oct 14, 2025 | Documentation before next phase | Learn from V1, avoid rushing |

### **Decisions Pending**

| Question | Options | Target Phase |
|----------|---------|--------------|
| Hardware catalog? | A) Build in Phase 3, B) Skip for MVP | Phase 3 |
| GO traffic engine? | A) Keep Python, B) Rewrite in GO if needed | Post-launch |
| GraphQL? | A) Add in Phase 5, B) Stick with REST | Post-launch |

---

## 🏆 Success Metrics

### **Phase 1 (Foundation) - ✅ Achieved**
- ✅ Backend API working
- ✅ Frontend visualization working
- ✅ 4 tests passing
- ✅ Docker setup
- ✅ Documentation complete

### **Phase 2 (WebSockets)**
- ✅ Zero manual refresh needed
- ✅ All clients stay in sync
- ✅ Reconnection works

### **Phase 3 (Management)**
- ✅ Non-technical user can build topology in UI
- ✅ No curl/Postman needed

### **Phase 4 (Traffic)**
- ✅ Traffic generation realistic
- ✅ Congestion detection accurate
- ✅ Aggregation correct

### **Phase 5 (Production)**
- ✅ 99.9% uptime
- ✅ Handle 100+ users
- ✅ Security audit passed

---

## 📚 References

- [ARCHITECTURE.md](ARCHITECTURE.md) - Design decisions
- [README.md](README.md) - Quick start guide
- [V1 Post-Mortem](docs/archive/V1_POSTMORTEM.md) - What went wrong

---

**Last Updated:** October 14, 2025  
**Next Update:** When Phase 2 begins

