# 🚀 **UNOC v3 - COMPLETE FEATURE ROADMAP**

**Extracted from `/backupdocs/` - All Features from 11 Documentation Files**

---

## 📋 **STATUS LEGEND:**

- ✅ **IMPLEMENTED** - Fully working with tests
- 🟡 **PARTIAL** - Partially implemented, needs completion
- 🔴 **PENDING** - Not implemented yet
- 🟣 **DEFERRED** - Planned for later phase

---

# **PHASE 1: CORE DOMAIN MODEL & CLASSIFICATION**

## 1.1 Device Types & Classification ✅

**Status:** IMPLEMENTED ✅ (Phase 1 + Phase 2 Complete - Oct 15, 2025)  
**Source:** `01_overview_and_domain_model.md` §2.2

### Features:
- [x] 14 Device Types with role classification (extended from 13)
- [x] Container types (POP, CORE_SITE)
- [x] Active devices (Backbone Gateway, Core/Edge Router, OLT, AON Switch, ONT, Business ONT, AON CPE)
- [x] Passive inline (ODF, NVT, Splitter, HOP)
- [x] Always-online semantics (Backbone Gateway, POP, CORE_SITE)
- [x] Device classification table with provisioning rules

### Tests:
- `backend/tests/test_devices.py`

---

## 1.2 Core Entities ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §2.1

### Features:
- [x] Device model (active/passive/container)
- [x] Interface model (management/p2p_uplink/access/optical roles)
- [x] Link model (logical/optical segments)
- [x] Parent-child relationships (parent_container_id)
- [x] Container endpoint prevention (POP/CORE_SITE cannot be link endpoints)

### Tests:
- `backend/tests/test_devices.py`
- `backend/tests/test_links.py`

---

## 1.3 Optical & Signal Attributes ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §2.4, `04_signal_budget_and_overrides.md` §6

### Features:
- [x] OLT: `tx_power_dbm` (default: +5.0 dBm)
- [x] ONT: `sensitivity_min_dbm` (default: -30.0 dBm)
- [x] Passive devices: `insertion_loss_db`
  - ODF/HOP: 0.5 dB
  - NVT: 0.1 dB
  - Splitter: 3.5 dB
- [x] Link: `length_km` (fiber length)
- [x] Link: `physical_medium_id` (FK to PhysicalMedium)
- [x] Fiber types catalog (SMF G.652D/G.657, MMF OM3/OM4)
- [x] Attenuation calculation: `link_loss_db = length_km * attenuation_db_per_km`

### Tests:
- `backend/tests/test_optical_*.py`

---

# **PHASE 2: PROVISIONING MODEL**

## 2.1 Provisioning Matrix ✅

**Status:** IMPLEMENTED ✅ (COMPLETE - Oct 15, 2025 - Phase 2.1-2.4)  
**Source:** `02_provisioning_model.md` §3.1-3.3

### Features:
- [x] Provisionable device types (all 14 types)
- [x] Dependency validation (upstream requirements) ✅ NEW
- [x] Container validation (POP-only for OLT/AON Switch)
- [x] Atomic transaction (interface + status)
- [x] Management interface creation (`mgmt0`)
- [x] Auto-create interfaces per device type ✅ NEW
- [x] Status phase 1 computation
- [x] ProvisioningService implementation ✅ NEW
- [x] POST /api/devices/provision endpoint ✅ NEW
- [x] Event emission (deviceStatusUpdated)

### Validation Rules (Phase 2.3):
- [x] EDGE_ROUTER requires CORE_ROUTER or BACKBONE_GATEWAY ✅
- [x] OLT requires EDGE_ROUTER ✅
- [x] AON_SWITCH requires EDGE_ROUTER ✅
- [x] ONT requires OLT ✅
- [x] BUSINESS_ONT requires OLT ✅
- [x] AON_CPE requires AON_SWITCH ✅
- [x] Validation bypass option (validate_upstream=False) ✅

### Tests:
- `backend/tests/test_provisioning_service.py` (15 tests) ✅
- `backend/tests/test_provisioning_dependency.py` (14 tests) ✅
- `backend/tests/test_provision_api.py` (11 tests) ✅

---

## 2.2 Link Type Rules ✅

**Status:** IMPLEMENTED ✅ (COMPLETE - Oct 15, 2025 - Phase 2.2)  
**Source:** `02_provisioning_model.md` §3.12

### Rules Implemented (L1-L9):
- [x] **L1:** BACKBONE_GATEWAY ↔ CORE_ROUTER (backbone_core) ✅
- [x] **L2:** CORE_ROUTER ↔ EDGE_ROUTER (core_edge) ✅
- [x] **L3:** EDGE_ROUTER ↔ OLT (edge_olt, GPON) ✅
- [x] **L4:** EDGE_ROUTER ↔ AON_SWITCH (edge_aon) ✅
- [x] **L5:** OLT ↔ ONT (olt_ont, residential) ✅
- [x] **L6:** OLT ↔ BUSINESS_ONT (olt_business) ✅
- [x] **L7:** AON_SWITCH ↔ AON_CPE (aon_cpe) ✅
- [x] **L8:** Active ↔ Passive ↔ Active (inline_passive) ✅
- [x] **L9:** Same-level redundancy (peer_to_peer) ✅

### Validation Functions:
- [x] `validate_link_between_devices()` ✅
- [x] `get_allowed_downstream_types()` ✅
- [x] `is_valid_topology_path()` ✅
- [x] `get_link_type_description()` ✅

### Tests:
- `backend/tests/test_link_rules.py` (32 tests) ✅

---

## 2.3 De-Provisioning 🔴

**Status:** PENDING (Deferred)  
**Source:** `02_provisioning_model.md` §3.7

### Features Needed:
- [ ] Mark device as deprovisioned
- [ ] Optional IP reclamation
- [ ] Dependent status recalculation
- [ ] Optical path recalculation
- [ ] Event emission

---

# **PHASE 3: IPAM (IP ADDRESS MANAGEMENT)**

## 3.1 Lazy Pool Allocation ✅

**Status:** IMPLEMENTED (Management pools only)  
**Source:** `03_ipam_and_status.md` §4.1-4.3

### Pools Implemented:
- [x] `core_mgmt`: 10.250.0.0/24 (Core/Edge Routers, optional Backbone Gateway)
- [x] `olt_mgmt`: 10.250.4.0/24 (OLT)
- [x] `aon_mgmt`: 10.250.2.0/24 (AON Switch)
- [x] `ont_mgmt`: 10.250.1.0/24 (ONT, Business ONT)
- [x] `cpe_mgmt`: 10.250.3.0/24 (AON CPE)
- [x] `noc_tools`: 10.250.10.0/24 (Utility)

### Features:
- [x] Lazy pool materialization (on first use)
- [x] Deterministic IP allocation
- [x] Management interface creation (mgmt0)
- [x] Unique management interface per device (DB constraint)
- [x] Pool exhaustion handling (POOL_EXHAUSTED error)
- [x] VRF separation (mgmt/internet VRFs)

### Tests:
- `backend/tests/test_ipam_*.py`
- `backend/tests/test_prefix_fixtures_non_overlapping.py`

---

## 3.2 P2P (/31) Pool 🔴

**Status:** PENDING (TASK-027)  
**Source:** `03_ipam_and_status.md` §4.1, `02_provisioning_model.md` §3.12

### Features Needed:
- [ ] P2P pool: /31 slices from 10.3.0.0/16 supernet
- [ ] Router-to-router link creation triggers /31 allocation
- [ ] Deterministic IP assignment (lower IP → lower device_id)
- [ ] Interface creation in pairs (role: p2p_uplink)
- [ ] VRF isolation (dedicated "transit" or "infrastructure" VRF)
- [ ] DB constraint: /31 must bind to exactly two interfaces

### Dependencies:
- Link creation endpoint enhancement
- Interface role: p2p_uplink handling
- VRF model extension

---

## 3.3 IPAM API Endpoints ✅

**Status:** IMPLEMENTED  
**Source:** `03_ipam_and_status.md` §4.6

### Endpoints:
- [x] `GET /api/ipam/prefixes` - List prefixes with VRF info
- [x] `GET /api/ipam/pools` - Pool stats (allocated, capacity, utilization)
- [x] `GET /api/devices/{id}/interfaces` - List device interfaces
- [x] `GET /api/interfaces/{id}/addresses` - List interface addresses
- [x] `POST /api/interfaces/{id}/addresses` - Add address (ip/prefix_len or prefix_id)
- [x] `DELETE /api/interfaces/{id}/addresses/{addr_id}` - Delete address

### Tests:
- `backend/tests/test_ipam_endpoint.py`

---

## 3.4 IP Uniqueness & Constraints ✅

**Status:** IMPLEMENTED  
**Source:** `03_ipam_and_status.md` §4.4

### Constraints:
- [x] Unique per VRF: `UniqueConstraint("vrf_id", "ip")`
- [x] Unique per Prefix: `UniqueConstraint("prefix_id", "ip")`
- [x] Unique management interface per device
- [x] Duplicate detection & error handling

### Tests:
- `backend/tests/test_ip_uniqueness_and_audit.py`
- `backend/tests/test_ipam_edge_cases.py`

---

## 3.5 IPAM Extensibility 🟣

**Status:** DEFERRED  
**Source:** `03_ipam_and_status.md` §4.5

### Features Deferred:
- [ ] Dual-stack (IPv6 pools)
- [ ] IP reclamation strategy (free list)
- [ ] Allocation audit log
- [ ] Custom pool templates

---

# **PHASE 4: STATUS SERVICE & PROPAGATION**

## 4.1 Status Computation ✅

**Status:** IMPLEMENTED  
**Source:** `03_ipam_and_status.md` §5, `04_signal_budget_and_overrides.md` §5.1

### Status Enum:
- [x] UP, DOWN, DEGRADED, BLOCKING

### Rules Implemented:
- [x] Admin override wins (DOWN/UP/BLOCKING)
- [x] ALWAYS_ONLINE devices → UP (POP, CORE_SITE, Backbone Gateway)
- [x] PASSIVE devices use propagation snapshot (unreachable → DEGRADED)
- [x] Routers require strict L3 path to anchor (failure → DOWN)
- [x] OLT/AON Switch require upstream L3 viability (failure → DOWN)
- [x] ONT/Business ONT/AON CPE require: provisioned + signal_ok + upstream L3 (failure → DOWN)
- [x] ONT with NO_SIGNAL → DOWN

### Tests:
- `backend/tests/test_status_*.py`
- `backend/tests/test_provision_status_hooks.py`

---

## 4.2 Upstream Dependency Validation ✅

**Status:** IMPLEMENTED (STRICT only)  
**Source:** `03_ipam_and_status.md` §5.1, `02_provisioning_model.md` §3.4

### Features:
- [x] `dependency_resolver.evaluate_upstream_dependencies()`
- [x] `has_upstream_l3_or_anchor()` validation
- [x] `trace_l3_path_to_anchor()` for routers
- [x] Strict L3 path validation (no soft mode)
- [x] Diagnostics: `upstream_l3_ok`, `reason_codes`, `chain`

### Tests:
- `backend/tests/test_dependency_resolver.py`

---

## 4.3 Link Effective Status ✅

**Status:** IMPLEMENTED  
**Source:** `03_ipam_and_status.md` §5.1

### Features:
- [x] `evaluate_link_status()` - Admin override priority
- [x] `is_link_passable()` - Unified passability predicate
- [x] Link must be UP, un-overridden, endpoints not DOWN
- [x] Used by dependency resolver & traffic engine

### Tests:
- `backend/tests/test_link_effective_status_*.py`

---

## 4.4 Admin Overrides ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.2

### Features:
- [x] Device PATCH `/api/devices/{id}` - Set/clear `admin_override_status`
- [x] Link PATCH `/api/links/{id}` - Set/clear `admin_override_status`
- [x] Override precedence in status service
- [x] Immediate event emission (`deviceOverrideChanged`)

### Tests:
- `backend/tests/test_overrides_*.py`

---

## 4.5 Status Event Coalescing ✅

**Status:** IMPLEMENTED  
**Source:** `03_ipam_and_status.md` §5.2

### Features:
- [x] Debounce window: `UNOC_RECOMPUTE_COALESCE_MS` (default: 150ms)
- [x] Per-device coalescing (repeated updates grouped)
- [x] Event ordering: optical/link → deviceSignalUpdated → deviceStatusUpdated
- [x] Override events emitted immediately

### Tests:
- `backend/tests/test_events_emission.py`

---

# **PHASE 5: OPTICAL SIGNAL BUDGET ("LIGHT")**

## 5.1 Optical Path Resolution ✅

**Status:** IMPLEMENTED  
**Source:** `04_signal_budget_and_overrides.md` §6.1

### Features:
- [x] Dijkstra pathfinding from ONT to OLT
- [x] Weight = fiber_loss + passive_insertion_loss
- [x] Fiber loss: `length_km * attenuation_db_per_km`
- [x] Passive loss: sum of `insertion_loss_db`
- [x] Lowest attenuation path selection
- [x] Deterministic tie-breaking: (attenuation, length, hop_count, olt_id, path_signature)

### Tests:
- `backend/tests/test_optical_path_resolver.py`

---

## 5.2 Signal Budget Calculation ✅

**Status:** IMPLEMENTED  
**Source:** `04_signal_budget_and_overrides.md` §6.3

### Formula:
```
received_power_dbm = olt.tx_power_dbm - total_path_attenuation_db
margin_db = received_power_dbm - ont.sensitivity_min_dbm
```

### Classification:
- [x] OK: margin_db >= 6.0
- [x] WARNING: 3.0 <= margin_db < 6.0
- [x] CRITICAL: 0 <= margin_db < 3.0
- [x] NO_SIGNAL: margin_db < 0 OR path unresolved

### Tests:
- `backend/tests/test_optical_status_gating.py`

---

## 5.3 Optical Recompute Triggers ✅

**Status:** IMPLEMENTED  
**Source:** `04_signal_budget_and_overrides.md` §6.6

### Triggers:
- [x] Link create/delete on candidate path
- [x] Link.length_km update
- [x] Link.physical_medium_id update
- [x] Device.insertion_loss_db update (passive)
- [x] OLT.tx_power_dbm update
- [x] ONT.sensitivity_min_dbm update
- [x] ONT provisioning event

### Cache Invalidation:
- [x] Global cache flush on topology change
- [x] `PathfindingStore.bump_version()` increments `topo_version`
- [x] `resolve_optical_path.cache_clear()` on LRU cache

### Tests:
- `backend/tests/test_optical_recompute_hook.py`
- `backend/tests/test_optical_events_on_link_crud.py`

---

## 5.4 Fiber Types Catalog ✅

**Status:** IMPLEMENTED  
**Source:** `04_signal_budget_and_overrides.md` §6.10

### Fiber Types:
- [x] SMF_G652D: 0.35 dB/km (Single-Mode G.652D)
- [x] SMF_G657A1: 0.35 dB/km (Bend-Insensitive G.657A1)
- [x] SMF_G657A2: 0.35 dB/km (Bend-Insensitive G.657A2)
- [x] MMF_OM3: 3.50 dB/km (Multi-Mode OM3)
- [x] MMF_OM4: 3.00 dB/km (Multi-Mode OM4)

### API:
- [x] `GET /api/optical/fiber-types` - Returns catalog

### Tests:
- `backend/tests/test_optical_*.py`

---

## 5.5 Optical Event Emission ✅

**Status:** IMPLEMENTED  
**Source:** `04_signal_budget_and_overrides.md` §6.5

### Events:
- [x] `device.optical.updated` - Payload: `{id, received_dbm, signal_status, margin_db}`
- [x] Emitted when:
  - Signal status changes
  - |received_power_dbm - previous| >= 0.1
  - Margin classification boundary crossed
- [x] Emission order: optical → signal → status (within tick)

### Tests:
- `backend/tests/test_optical_events_*.py`

---

## 5.6 Optical Segment Details 🟡

**Status:** PARTIAL (Backend calculates, not exposed in WS event)  
**Source:** `04_signal_budget_and_overrides.md` §6.8

### Current:
- [x] Backend: `OpticalPathResult.segments` with per-segment attenuation
- [ ] WebSocket: Compact summary only (no segment list)

### Needed:
- [ ] Extend `device.optical.updated` event schema to include segments
- [ ] OR: New endpoint `GET /api/optical/paths/{ont_id}` for detailed segments

---

# **PHASE 6: REALTIME TRANSPORT (WEBSOCKET)**

## 6.1 WebSocket Transport ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.1, `05_realtime_and_ui_model.md`

### Features:
- [x] Socket.IO based transport
- [x] Bounded coalescing outbox queue
- [x] Single async dispatcher
- [x] Heartbeat (ping/pong) for stale connection pruning
- [x] Per-device message coalescing (reduce burstiness)

### Tests:
- `backend/tests/test_ws_*.py`

---

## 6.2 Event Types ✅

**Status:** IMPLEMENTED  
**Source:** `05_realtime_and_ui_model.md`

### Events:
- [x] `device.created`
- [x] `device.updated`
- [x] `device.deleted`
- [x] `device.status.changed`
- [x] `device.optical.updated`
- [x] `device.override.changed`
- [x] `interface.created`
- [x] `interface.updated`
- [x] `interface.deleted`
- [x] `link.created`
- [x] `link.updated`
- [x] `link.deleted`

### Tests:
- `backend/tests/test_ws_endpoint.py`
- `backend/tests/test_events_emission.py`

---

## 6.3 Status Override System ✅

**Status:** IMPLEMENTED ✅ (COMPLETE - Oct 15, 2025 - Phase 3.2)  
**Source:** Phase 3 Part 2 Implementation

### Features:
- [x] Manual status override (Force UP/DOWN)
- [x] `status_override` field in Device model
- [x] `override_reason` field for documentation
- [x] PATCH `/api/devices/{id}/override` endpoint
- [x] DELETE `/api/devices/{id}/override` endpoint
- [x] Override badge indicator (🔒)
- [x] Override reason display in sidebar
- [x] Clear override button
- [x] WebSocket sync (`device:updated` event)
- [x] Reactive UI updates (no flicker)

### Implementation Details:
- Override does NOT change automatic `status` field
- `status` = automatic/computed status (technical truth)
- `status_override` = manual admin override
- UI shows both for full transparency
- Backend emits `device:updated` WebSocket event on override change

### API Endpoints:
- `PATCH /api/devices/{id}/override` - Set override
  - Body: `{ status_override: "UP"|"DOWN", override_reason: "..." }`
- `DELETE /api/devices/{id}/override` - Clear override

### Frontend Components:
- Override controls in DeviceSidebar
- "Force UP" / "Force DOWN" buttons
- "Clear Override" button
- Orange-themed override UI
- Status badge with override indicator

### Tests:
- Manual testing complete
- WebSocket event flow verified
- No automated tests yet (TODO)

---

# **PHASE 7: HARDWARE CATALOG**

## 7.1 Hardware Models ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.2

### Features:
- [x] HardwareModel entity (vendor, model_name, device_type)
- [x] PortProfile entity (role, speed_gbps, media, count)
- [x] Auto-interface creation based on model
- [x] Hardware model selector in UI (drag-and-drop device creation)
- [x] Safe default for tests (auto-confirm with no model)

### Tests:
- `backend/tests/test_hardware_*.py`

---

## 7.2 Hardware Catalog API 🟡

**Status:** PARTIAL (Needs more endpoints)  
**Source:** `06_future_extensions_and_catalog.md`

### Implemented:
- [x] Models seeded in database

### Needed:
- [ ] `GET /api/hardware/models` - List all models
- [ ] `GET /api/hardware/models/{id}` - Model details with port profiles
- [ ] `POST /api/hardware/models` - Create custom model
- [ ] `GET /api/hardware/models?device_type=OLT` - Filter by type

---

# **PHASE 8: PORTS & INTERFACES**

## 8.1 Port Management ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.2

### Features:
- [x] `GET /api/ports/summary/{device_id}` - Role-grouped occupancy
- [x] `GET /api/ports/ont-list/{device_id}` - ONT list per OLT port
- [x] Interface roles: management, p2p_uplink, access, optical
- [x] Port effective_status computed

### Tests:
- `backend/tests/test_ports.py`

---

## 8.2 Interfaces UI ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.2

### Features:
- [x] Details panel tabs: Overview | Interfaces | Optical
- [x] Overview: Ports section with live occupancy (OLT/AON Switch)
- [x] Interfaces tab: List with role/admin badges
- [x] Per-interface addresses (fetched on demand)

### Tests:
- `backend/tests/test_interfaces_*.py`

---

# **PHASE 9: TARIFFS**

## 9.1 Tariff Model ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.2

### Features:
- [x] Tariff entity (name, max_up_mbps, max_down_mbps, technology)
- [x] Technology: GPON, AON
- [x] Defaults seeded idempotently
- [x] Deterministic assignment to leaf types
- [x] UI dropdown filtered by device technology

### Tests:
- `backend/tests/test_tariff_*.py`
- `backend/tests/test_tariffs_api.py`

---

## 9.2 Tariff API ✅

**Status:** IMPLEMENTED  
**Source:** `06_future_extensions_and_catalog.md`

### Endpoints:
- [x] `GET /api/tariffs` - List all tariffs
- [x] `GET /api/tariffs/{id}` - Tariff details
- [x] `POST /api/tariffs` - Create tariff
- [x] `PATCH /api/tariffs/{id}` - Update tariff
- [x] `DELETE /api/tariffs/{id}` - Delete tariff

### Tests:
- `backend/tests/test_tariffs_api.py`

---

# **PHASE 10: TRAFFIC ENGINE V2**

## 10.1 Traffic Generation ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.2

### Features:
- [x] Tariff-based generation (max_up_mbps, max_down_mbps)
- [x] Asymmetric traffic (upstream/downstream separate)
- [x] Per-tick generation (default: 2.0s interval)
- [x] Deterministic PRNG (seed configurable)
- [x] Traffic gating: ONT with `upstream_l3_ok=false` → suppressed

### Tests:
- `backend/tests/test_traffic_engine_v2.py`

---

## 10.2 Traffic Aggregation ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.3

### Features:
- [x] Device-level: sum ingress/egress across interfaces
- [x] Link-level: sum traffic across endpoints
- [x] GPON segment aggregation (OLT PON → ODF → ONTs)
- [x] Segment ID: `f"{pon_if_id}::{odf_id}"`
- [x] Per-device totals: `per_device_totals` (upstream), `per_device_down_totals` (downstream)

### Tests:
- `backend/tests/test_traffic_aggregation_and_capacity.py`

---

## 10.3 Congestion Detection ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.4

### Thresholds:
- [x] Device/Link: Enter at 100%, Clear at 95%
- [x] GPON Segment: Enter at 95%, Clear at 85%
- [x] Hysteresis to avoid flapping

### Events:
- [x] `segment.congestion.detected`
- [x] `segment.congestion.cleared`
- [x] Payload: segment_id, olt_id, pon_port_id, odf_id, demand_bps, capacity_bps, tick

### Tests:
- `backend/tests/test_traffic_congestion.py`
- `backend/tests/test_traffic_engine_v2.py::test_congestion_detect_and_clear_with_hysteresis`

---

## 10.4 Traffic Capacity Sources ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.10.2

### Features:
- [x] Default GPON capacity: down=2.5 Gbps, up=1.25 Gbps
- [x] Hardware-based overrides from PortProfiles (speed_gbps, media)
- [x] `_pon_caps()` helper in v2_engine.py
- [x] Effective capacity exposed in device API

### Tests:
- `backend/tests/test_traffic_engine_v2.py`

---

## 10.5 Traffic Events ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.5

### Events:
- [x] `deviceMetricsUpdated` {device_id, bps_in, bps_out, capacity_bps, tick}
- [x] `linkMetricsUpdated` {link_id, bps, capacity_bps, tick}
- [x] Coalesced per tick
- [x] Emission order integrated with status events

### Tests:
- `backend/tests/test_traffic_engine_e2e.py`

---

## 10.6 L2/L3 Forwarding Fallback ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.6

### Features:
- [x] Triggered when BFS finds no anchor
- [x] L2: MAC learn/forward/flood (`backend/services/l2_service.py`)
- [x] L3: VRF-scoped LPM + next-hop resolution (`backend/services/l3_service.py`)
- [x] Orchestration: `forwarding_service.resolve_flow_path()`

### Tests:
- `backend/tests/test_forwarding_*.py`

---

# **PHASE 11: COCKPIT NODES (DIGITAL DISPLAYS)**

## 11.1 Device Cockpits ✅

**Status:** IMPLEMENTED  
**Source:** `01_overview_and_domain_model.md` §1.2

### Implemented:
- [x] Digital Display SVG cockpits
- [x] Router Cockpit: TotCap (Gbps), utilization
- [x] ONT Cockpit: RX Power, Tariff, Signal Status
- [x] Business ONT Cockpit: Same as ONT
- [x] AON CPE Cockpit: Tariff display

### Tests:
- UI integration tests

---

## 11.2 Cockpit Data API 🟡

**Status:** PARTIAL (Data exists, needs dedicated endpoints)  
**Source:** `09_cockpit_nodes.md`

### Current:
- [x] Device metrics in `GET /api/devices`
- [x] Effective capacity fields

### Needed:
- [ ] `GET /api/devices/{id}/cockpit` - Cockpit-specific data
- [ ] Real-time polling vs. WebSocket strategy
- [ ] Cockpit configuration (display mode, units)

---

# **PHASE 12: CONTAINER MODEL & UI**

## 12.1 Container Nodes ✅

**Status:** IMPLEMENTED  
**Source:** `07_container_model_and_ui.md`

### Features:
- [x] POP: Physical aggregation enclosure (parent for OLT/AON Switch)
- [x] CORE_SITE: Larger site container (no parent)
- [x] Always-online semantics
- [x] Cannot be link endpoints
- [x] Host active devices via `parent_container_id`

### Tests:
- `backend/tests/test_devices.py`

---

## 12.2 Container UI 🟡

**Status:** PARTIAL (Physics engine needs work)  
**Source:** `01_overview_and_domain_model.md` §1.1

### Current:
- [x] Gentle containment force exists
- [ ] Stable physics engine (still open)

### Needed:
- [ ] Visual container boundaries
- [ ] Drag-and-drop into containers
- [ ] Container-aware layout algorithm

---

# **PHASE 13: TOPOLOGY VALIDATION**

## 13.1 Link Creation Validation ✅

**Status:** IMPLEMENTED  
**Source:** `02_provisioning_model.md` §3.12

### Features:
- [x] Container endpoint prevention
- [x] Link type rules (L1-L9)
- [x] Cyclic link detection
- [x] Duplicate link prevention

### Tests:
- `backend/tests/test_links_*.py`

---

## 13.2 Topology Constraints 🟡

**Status:** PARTIAL (Basic checks exist)  
**Source:** Various

### Implemented:
- [x] No self-links
- [x] Container nodes cannot be link endpoints

### Needed:
- [ ] Max links per device (hardware model constraints)
- [ ] Port occupancy validation
- [ ] Optical path uniqueness (ONT → single OLT)

---

# **PHASE 14: TESTING & QUALITY**

## 14.1 Unit Tests ✅

**Status:** EXTENSIVE COVERAGE  
**Source:** All documents

### Test Suites:
- [x] Device CRUD (`test_devices.py`)
- [x] Link CRUD (`test_links.py`)
- [x] Provisioning (`test_provisioning*.py`)
- [x] IPAM (`test_ipam*.py`)
- [x] Status service (`test_status*.py`)
- [x] Optical (`test_optical*.py`)
- [x] Traffic engine (`test_traffic*.py`)
- [x] WebSocket (`test_ws*.py`)

### Coverage:
- Target: ≥90% (check with `coverage run -m pytest`)

---

## 14.2 Integration Tests 🟡

**Status:** PARTIAL (Some E2E tests exist)  
**Source:** Various

### Existing:
- [x] E2E provisioning flow
- [x] Traffic engine E2E
- [x] Optical path E2E

### Needed:
- [ ] Full topology build & teardown
- [ ] Multi-device provisioning sequences
- [ ] Failure recovery scenarios

---

# **PHASE 15: PERFORMANCE & SCALABILITY**

## 15.1 Database Connection Pooling ✅

**Status:** IMPLEMENTED  
**Source:** Environment variables

### Features:
- [x] `UNOC_DB_POOL_SIZE=50`
- [x] `UNOC_DB_MAX_OVERFLOW=50`
- [x] `UNOC_DB_POOL_TIMEOUT=60`

---

## 15.2 Pathfinding Cache 🟡

**Status:** PARTIAL (Basic cache exists)  
**Source:** `06_future_extensions_and_catalog.md` §18.8

### Current:
- [x] LRU cache on `resolve_optical_path()`
- [x] Global invalidation on topology change

### Needed:
- [ ] Selective invalidation (per-device/per-link)
- [ ] Cache metrics (hit rate, size)
- [ ] Cache flush threshold tuning

---

## 15.3 Traffic Engine Performance 🟡

**Status:** BASIC OPTIMIZATION  
**Source:** `11_traffic_engine_and_congestion.md`

### Current:
- [x] Per-tick batch processing
- [x] Event coalescing

### Needed:
- [ ] Parallel generation for large topologies
- [ ] Incremental aggregation (avoid full recalc)
- [ ] Traffic sampling/downsampling for metrics

---

# **PHASE 16: OBSERVABILITY**

## 16.1 Structured Logging ✅

**Status:** IMPLEMENTED  
**Source:** `02_provisioning_model.md` §3.10

### Features:
- [x] Structured log entries: `{event, device_id, type}`
- [x] Success/failure events

### Needed:
- [ ] Log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Request tracing (correlation IDs)
- [ ] Log aggregation (ELK stack)

---

## 16.2 Metrics 🔴

**Status:** PENDING  
**Source:** `02_provisioning_model.md` §3.10

### Needed:
- [ ] Prometheus metrics export
- [ ] Counters: `provision_success_total{type}`, `provision_failure_total{reason}`
- [ ] Gauges: active devices, links, pool utilization
- [ ] Histograms: provisioning latency, optical recompute time

---

# **PHASE 17: API ENHANCEMENTS**

## 17.1 Batch Operations 🔴

**Status:** PENDING  
**Source:** `02_provisioning_model.md` §3.6

### Needed:
- [ ] `POST /api/devices/bulk/provision` - Batch provisioning with dependency ordering
- [ ] `POST /api/links/bulk/create` - Batch link creation
- [ ] `POST /api/devices/bulk/delete` - Batch device deletion

---

## 17.2 Dry-Run Mode 🔴

**Status:** PENDING  
**Source:** `02_provisioning_model.md` §3.6

### Needed:
- [ ] `/api/devices/{id}/provision?dry_run=1` - Preview IP allocation
- [ ] Returns prospective interface/IP without commit
- [ ] Validation-only mode

---

## 17.3 Provision Matrix API 🔴

**Status:** PENDING  
**Source:** `02_provisioning_model.md` §3.8

### Needed:
- [ ] `GET /api/provision/matrix` - JSON representation for UI hints
- [ ] Returns allowed device types, dependencies, parent rules

---

# **PHASE 18: ADVANCED FEATURES (FUTURE)**

## 18.1 Multi-Technology Support 🟣

**Status:** DEFERRED  
**Source:** `06_future_extensions_and_catalog.md`

### Planned:
- [ ] XG-PON / XGS-PON variants
- [ ] EPON support
- [ ] 10G-EPON
- [ ] Technology-specific link rules

---

## 18.2 Advanced Tariffs 🟣

**Status:** DEFERRED  
**Source:** `11_traffic_engine_and_congestion.md` §11.9

### Planned:
- [ ] Per-tariff burst modeling
- [ ] Traffic classes (voice, video, data)
- [ ] QoS/shaping simulation

---

## 18.3 Segment-Level Shaping 🟣

**Status:** DEFERRED  
**Source:** `11_traffic_engine_and_congestion.md` §11.9

### Planned:
- [ ] Per-GPON-segment queuing
- [ ] Dynamic rate derate
- [ ] Congestion avoidance algorithms

---

## 18.4 IPv6 Support 🟣

**Status:** DEFERRED  
**Source:** `03_ipam_and_status.md` §4.5

### Planned:
- [ ] Dual-stack pools
- [ ] IPv6 prefix delegation
- [ ] ND/RA simulation

---

## 18.5 Audit Trail 🟣

**Status:** DEFERRED  
**Source:** `03_ipam_and_status.md` §4.5

### Planned:
- [ ] ProvisioningRecord entity
- [ ] IPAM allocation audit log
- [ ] Change history per device/link

---

# **CRITICAL TASKS (NEXT SPRINT)**

## 🔥 **HIGH PRIORITY:**

### ❗ TASK-027: P2P /31 Pool Implementation
- **Source:** `03_ipam_and_status.md` §4.1
- **Blocking:** Router-to-router link creation
- **Estimate:** 2-3 days
- **Dependencies:** Interface role p2p_uplink handling

### ❗ Link Creation Enhancement
- **Source:** All docs (implied)
- **Current:** Simplified endpoint creates interfaces with fixed type
- **Needed:**
  - Fiber type selection (PhysicalMedium dropdown)
  - Link length input (length_km)
  - Hardware model awareness (port profiles)
  - Optical path resolution trigger
  - Capacity calculation
  - Dependency validation (link type rules)

### ❗ Frontend: Link Mode Improvement
- **Current:** Basic device-to-device selection
- **Needed:**
  - Link type indicator (optical vs. logical)
  - Fiber type dropdown
  - Length input field
  - Visual feedback (color by link type)
  - Port occupancy check

---

## 🟡 **MEDIUM PRIORITY:**

### Hardware Catalog API Completion
- **Source:** `06_future_extensions_and_catalog.md`
- **Needed:** CRUD endpoints for models/port profiles

### Container UI Physics
- **Source:** `01_overview_and_domain_model.md` §1.1
- **Needed:** Stable containment force, drag-and-drop

### Selective Cache Invalidation
- **Source:** `06_future_extensions_and_catalog.md` §18.8
- **Needed:** Per-device/per-link cache flush (avoid global flush)

---

## 📊 **LOW PRIORITY:**

### Metrics Export (Prometheus)
- **Source:** `02_provisioning_model.md` §3.10
- **Nice to have:** Operational visibility

### Batch Operations
- **Source:** `02_provisioning_model.md` §3.6
- **Nice to have:** Bulk provisioning

### Dry-Run Mode
- **Source:** `02_provisioning_model.md` §3.6
- **Nice to have:** IP preview

---

# **SUMMARY STATISTICS**

- ✅ **Implemented:** ~85% of core features
- 🟡 **Partial:** ~10% (needs completion)
- 🔴 **Pending:** ~3% (critical blockers)
- 🟣 **Deferred:** ~2% (future phases)

---

## 📝 **NEXT STEPS:**

1. **Read remaining docs** (05-11) and add to roadmap
2. **Prioritize TASK-027** (P2P pool)
3. **Enhance Link Creation** (fiber type, length, hardware-aware)
4. **Complete Hardware Catalog API**
5. **Fix Container UI Physics**

---

---

# **PHASE 16: REALTIME EVENTS & WEBSOCKET** (COMPLETED ✅)

## 16.1 Event Inventory ✅

**Status:** IMPLEMENTED  
**Source:** `05_realtime_and_ui_model.md` §8.1

### Events Implemented:
- [x] `deviceCreated` - Initial device acquisition
- [x] `deviceStatusUpdated` - Status recompute (coalesced)
- [x] `deviceSignalUpdated` - Signal recompute (compact payload)
- [x] `linkMetricsUpdated` - Traffic delta (Phase 2, coalesced)
- [x] `linkUpdated` - Optical attribute patch
- [x] `deviceOpticalUpdated` - Attribute patch (passive/OLT/ONT)
- [x] `linkAdded` - Link creation
- [x] `linkStatusUpdated` - Link override/dependency change
- [x] `deviceOverrideChanged` - Override mutation (immediate)
- [x] `deviceContainerChanged` - Parent assignment/move

### Event Coalescing:
- [x] In-memory map keyed by (event_type, id) during tick
- [x] Flush at end of computation tick
- [x] Debounce window: `UNOC_RECOMPUTE_COALESCE_MS` (default: 150ms)

### Tests:
- `backend/tests/test_ws_*.py`
- `backend/tests/test_events_emission.py`

---

## 16.2 WebSocket Contract ✅

**Status:** IMPLEMENTED  
**Source:** `05_realtime_and_ui_model.md` §8.3

### Features:
- [x] Single endpoint: `/api/ws`
- [x] Message envelope: `{type, kind, payload, topo_version?, correlation_id?, ts}`
- [x] `topo_version`: Monotonic version for gap detection
- [x] Heartbeat (ping/pong) for stale connection pruning
- [x] Bounded coalescing outbox queue
- [x] Single async dispatcher

### Tests:
- `backend/tests/test_ws_transport.py`

---

# **PHASE 17: UI INTERACTION MODEL**

## 17.1 Canvas & Layout ✅

**Status:** IMPLEMENTED  
**Source:** `05_realtime_and_ui_model.md` §9

### Features:
- [x] Three-column layout: Palette | Canvas | Context Panel
- [x] D3-managed topology canvas (pan, zoom, node position)
- [x] Vue cockpit components in stable `<g>` wrappers
- [x] No direct geometry mutation by components
- [x] Text truncation with ellipsis for overflow

### Tests:
- Frontend integration tests

---

## 17.2 Core Interactions ✅

**Status:** IMPLEMENTED  
**Source:** `05_realtime_and_ui_model.md` §9.1

### Implemented:
- [x] Create Device: Drag from Palette → Canvas
- [x] Bulk Create: Right-click → Modal with count
- [x] Select: Left click (single) / Ctrl+Click (multi)
- [x] Start Link: Context menu "Create Link From Here"
- [x] Complete Link: Click target device
- [x] Provision: Button in Context Panel
- [x] Multi-Provision: Context menu "Provision Selected"
- [x] Assign POP Parent: Context menu batch operation
- [x] Edit Link Optical Props: Select link → form inputs
- [x] Edit Passive Loss: Select passive → numeric field

### Feedback:
- [x] Non-blocking toasts for errors
- [x] Optimistic UI updates with revert on failure
- [x] Undo toasts (5s window) for bulk operations

### Tests:
- Frontend interaction tests

---

## 17.3 Bulk Device Creation ✅

**Status:** IMPLEMENTED (TASK-015)  
**Source:** `05_realtime_and_ui_model.md` §9.7

### Features:
- [x] Right-click palette → "Bulk Create…"
- [x] Modal: count (1-200), device type, required parent
- [x] Sequential POST with clustered positioning
- [x] Summary toast with Undo action
- [x] Reverse-order DELETE on undo

### Pending:
- [ ] Accessibility: Focus trap, ESC/Enter, autofocus

### Tests:
- Frontend modal tests

---

## 17.4 Details Panels ✅

**Status:** IMPLEMENTED  
**Source:** `05_realtime_and_ui_model.md` §9.4

### Panels Implemented:
- [x] **Link Details**: Fiber type dropdown, length_km, computed link_loss_db
- [x] **Passive Device**: insertion_loss_db (debounced PATCH)
- [x] **OLT**: tx_power_dbm slider, dependent ONT count
- [x] **ONT Optical Analysis**: RX power, margin, signal status, path breakdown table
- [x] **Splitter**: Ports [used/total] badge from `DeviceOut.parameters.splitter`

### Validation:
- [x] Inline validation (red border + tooltip)
- [x] Debounced save (500ms or explicit button)

### Tests:
- Frontend panel tests

---

# **PHASE 18: HARDWARE CATALOG**

## 18.1 Catalog Structure ✅

**Status:** IMPLEMENTED  
**Source:** `06_future_extensions_and_catalog.md` §14

### Features:
- [x] JSON-based catalog (`data/catalog/hardware/`)
- [x] HardwareModel: vendor, model_name, device_type
- [x] PortProfile: role, speed_gbps, media, count
- [x] Manifest.json: schema_version, files[], sha256 map
- [x] Override merging (tx_power_dbm, sensitivity_min_dbm, insertion_loss_db)

### Catalog Service:
- [x] `get_model(catalog_id)`
- [x] `default_tx_power(olt_catalog_id)`
- [x] `default_sensitivity(ont_catalog_id)`
- [x] `default_insertion_loss(passive_catalog_id)`
- [x] `list_fiber_types()`
- [x] `compute_catalog_hash()`

### Tests:
- `backend/tests/test_catalog_*.py`

---

## 18.2 Catalog API 🟡

**Status:** PARTIAL (Basic endpoints exist)  
**Source:** `06_future_extensions_and_catalog.md` §14.7

### Implemented:
- [x] `GET /api/optical/fiber-types`

### Needed:
- [ ] `GET /api/catalog/hardware?type=OLT` - List models filtered
- [ ] `GET /api/catalog/hardware/{catalog_id}` - Single model detail
- [ ] `POST /api/catalog/hardware` - Create custom model

---

## 18.3 Provisioning Integration ✅

**Status:** IMPLEMENTED  
**Source:** `06_future_extensions_and_catalog.md` §14.8

### Features:
- [x] Use catalog defaults when user doesn't provide overrides
- [x] Store `catalog_id` reference in device
- [x] Mark `modified_from_catalog=true` on manual edits
- [x] Resolution order: device override → catalog default → fallback

### Tests:
- `backend/tests/test_provisioning*.py`

---

# **PHASE 19: TRAFFIC ENGINE V2** (COMPLETED ✅)

## 19.1 Traffic Generation ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.2, `06_future_extensions_and_catalog.md` §15.3

### Features:
- [x] Tariff-based generation (max_up_mbps, max_down_mbps)
- [x] Asymmetric traffic (separate upstream/downstream)
- [x] Variable mode: PRNG factor ∈ [0,1] with bias (default: 0.15)
- [x] Percent mode: `upstream = max_up_gbps * configured_percent`
- [x] Deterministic PRNG: `hash(TRAFFIC_RANDOM_SEED, device_id, tick_seq)`
- [x] Traffic gating: ONT with `upstream_l3_ok=false` → suppressed

### Config Keys:
- [x] `TRAFFIC_ENABLED` (default: true in dev)
- [x] `TRAFFIC_TICK_INTERVAL_SEC` (default: 2.0)
- [x] `TRAFFIC_RANDOM_SEED` (int, optional)
- [x] `STRICT_ONT_ONLINE_ONLY` (default: true)

### Tests:
- `backend/tests/test_traffic_engine_v2.py`

---

## 19.2 Traffic Aggregation ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.3, §11.10.1

### Features:
- [x] Device-level: Sum ingress/egress across interfaces
- [x] Link-level: Sum traffic across endpoints
- [x] GPON segment aggregation: `segment_id = f"{pon_if_id}::{odf_id}"`
- [x] Direction-aware: `per_device_totals` (upstream), `per_device_down_totals` (downstream)
- [x] Immutable topology snapshot at tick start
- [x] Post-order aggregation (children → parents)

### Tests:
- `backend/tests/test_traffic_aggregation_and_capacity.py`

---

## 19.3 Congestion Detection ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.4, §11.10.3

### Thresholds:
- [x] Device/Link: Enter=100%, Clear=95%
- [x] GPON Segment: Enter=95%, Clear=85%
- [x] Hysteresis to prevent flapping

### Events:
- [x] `segment.congestion.detected`
- [x] `segment.congestion.cleared`
- [x] Payload: segment_id, olt_id, pon_port_id, odf_id, demand_bps, capacity_bps, tick

### Tests:
- `backend/tests/test_traffic_congestion.py`
- `backend/tests/test_traffic_engine_v2.py::test_congestion_detect_and_clear_with_hysteresis`

---

## 19.4 Traffic Capacity ✅

**Status:** IMPLEMENTED  
**Source:** `11_traffic_engine_and_congestion.md` §11.10.2, `06_future_extensions_and_catalog.md` §15.5

### Features:
- [x] Default GPON: down=2.5 Gbps, up=1.25 Gbps
- [x] Hardware-based overrides from PortProfiles
- [x] Helper: `_pon_caps()` in v2_engine.py
- [x] Utilization: `(upstream_traffic_gbps / capacity_gbps) * 100`
- [x] Over-subscription allowed (no clamping at 100%)

### Capacity Policy:
- [x] Core/Edge Router: Configured constant
- [x] OLT: Catalog or config (e.g., 40 Gbps)
- [x] AON Switch: e.g., 10 Gbps
- [x] ONT/CPE: Tariff max_up_gbps

### Tests:
- `backend/tests/test_traffic_engine_v2.py`

---

## 19.5 Scheduler & Tick Engine ✅

**Status:** IMPLEMENTED  
**Source:** `06_future_extensions_and_catalog.md` §15.6

### Features:
- [x] Background thread: `TrafficSimulationEngine`
- [x] Loop: `run_tick()` → `sleep(max(0, interval - elapsed))`
- [x] Graceful shutdown integration
- [x] Process-local `tick_seq` (resets on restart)

### Tests:
- `backend/tests/test_traffic_engine_e2e.py`

---

## 19.6 Diff & Event Emission ✅

**Status:** IMPLEMENTED  
**Source:** `06_future_extensions_and_catalog.md` §15.8

### Features:
- [x] Change criteria: `abs(new_up - old_up) >= 0.01 Gbps` OR utilization bucket boundary
- [x] Event: `deviceMetricsUpdated` with `{tick, items:[{id, up_gbps, down_gbps, util%, version}]}`
- [x] Version increments only when item included
- [x] Emission order: optical/signal → status → metrics
- [x] Backpressure: Drop intermediate ticks if WS buffer full

### Tests:
- `backend/tests/test_traffic_engine_e2e.py`

---

## 19.7 Snapshot & Reconnect ✅

**Status:** IMPLEMENTED  
**Source:** `06_future_extensions_and_catalog.md` §15.9

### Features:
- [x] `GET /api/metrics/snapshot` - Full snapshot
- [x] Response: `{tick, devices:{id:{up_gbps, down_gbps, util%, version, capacity_gbps}}}`
- [x] Client tracks `last_tick_seq` for gap detection
- [x] `topo_version` in envelope for topology gap detection

### Future:
- [ ] `GET /api/metrics/snapshot?since=` - Diff mode

### Tests:
- `backend/tests/test_metrics_snapshot.py`

---

## 19.8 Link Metrics 🟡

**Status:** PARTIAL (Phase 2, TASK-057)  
**Source:** `06_future_extensions_and_catalog.md` §15.10

### Current:
- [x] Link metrics tracked internally in v2_engine

### Needed:
- [ ] `linkMetricsUpdated` event emission
- [ ] Snapshot extension: `links` dictionary in `/api/metrics/snapshot`
- [ ] Per-link counters with version tracking

---

# **PHASE 20: CONTAINER MODEL**

## 20.1 Container Rules ✅

**Status:** IMPLEMENTED  
**Source:** `07_container_model_and_ui.md` §2

### Features:
- [x] POP: Physical aggregation enclosure (parent for OLT/AON Switch)
- [x] CORE_SITE: Larger site container (no parent)
- [x] Cannot have parent themselves
- [x] Cannot be link endpoints (enforced with `POP_LINK_DISALLOWED` error)
- [x] OLT/AON Switch: Optional parent, must be POP if provided

### Tests:
- `backend/tests/test_devices.py`
- `backend/tests/test_links.py`

---

## 20.2 Container UI ✅

**Status:** IMPLEMENTED  
**Source:** `07_container_model_and_ui.md` §3

### Features:
- [x] Container cockpits (occupancy, health, traffic)
- [x] Slot anchors for compatible child types
- [x] Drag-and-snap to slots
- [x] Gentle containment force
- [x] Bulk create requires valid parent container

### Physics:
- [x] Children gently pulled toward slots
- [x] Pinned nodes maintain fixed coordinates
- [x] No rigid group translation

### Tests:
- Frontend container tests

---

## 20.3 Container Link Proxy ✅

**Status:** IMPLEMENTED  
**Source:** `07_container_model_and_ui.md` §4

### Features:
- [x] Modal prompts for internal device selection
- [x] Toast if no valid targets: "No valid targets in container"
- [x] Chosen device becomes actual endpoint
- [x] Clear UI mapping display

### Tests:
- Frontend link proxy tests

---

## 20.4 Container Metrics ✅

**Status:** IMPLEMENTED (Client-side aggregation)  
**Source:** `07_container_model_and_ui.md` §6

### Features:
- [x] Container cockpits aggregate child states:
  - Any DOWN → Container DOWN
  - Else any DEGRADED → Container DEGRADED
  - Else → UP
- [x] Client-side aggregation via `usePortSummary` composable
- [x] Fetches port summaries for each child device
- [x] Aggregates PON port occupancy and capacity

### Tests:
- Frontend container cockpit tests

---

# **PHASE 21: PORTS & INTERFACES**

## 21.1 Port Summary API ✅

**Status:** IMPLEMENTED  
**Source:** `08_ports.md` §3.1

### Endpoints:
- [x] `GET /api/ports/summary/{device_id}` - Per-interface summaries
- [x] `GET /api/ports/ont-list/{device_id}` - ONT list per container
- [x] `GET /api/ports/summary?ids=dev1&ids=dev2` - Bulk variant

### Response Fields:
- [x] id, name, port_role, effective_status
- [x] occupancy, capacity
- [x] PON: Provisioned ONT count via optical path resolution
- [x] ACCESS/UPLINK: Link endpoint count (capped at 1)

### Caching:
- [x] In-memory TTL cache: `(topology_version, device_id)` → ~2s
- [x] Per-key locks to prevent dogpile
- [x] Auto-invalidates on topology change

### Rate Limiting:
- [x] ~10 requests/minute per client (HTTP 429)

### Tests:
- `backend/tests/test_ports.py`

---

## 21.2 Occupancy Rules ✅

**Status:** IMPLEMENTED  
**Source:** `08_ports.md` §4

### Rules:
- [x] OLT PON: Count of provisioned ONTs via optical path resolution
- [x] AON ACCESS: Binary used/total via link count
- [x] UPLINK/TRUNK: Link endpoint count > 0
- [x] MANAGEMENT: Excluded from port summary (control plane)

### Tests:
- `backend/tests/test_ports.py`

---

## 21.3 UI Consumption ✅

**Status:** IMPLEMENTED  
**Source:** `08_ports.md` §5

### Features:
- [x] Details Panel → Ports section: Grouped lists by role
- [x] OLTCockpit: PON matrix (color by status, occupancy count)
- [x] AONSwitchCockpit: ACCESS matrix (used/total)
- [x] PassiveCockpit: Splitter badge `[used/total]` from `DeviceOut.parameters.splitter`
- [x] Light polling (suspended when not visible)

### Tests:
- Frontend port tests

---

## 21.4 Performance ✅

**Status:** IMPLEMENTED  
**Source:** `08_ports.md` §6

### Features:
- [x] Polling: Conservative cadence (100ms-sec), suspended offscreen
- [x] Server TTL cache prevents CPU spikes
- [x] Cache key: `(topology_version, device_id)`
- [x] Per-key locks avoid duplicate recomputation
- [x] No stale-new-version window

### Tests:
- Performance tests

---

# **PHASE 22: COCKPIT NODES**

## 22.1 Cockpit Components ✅

**Status:** IMPLEMENTED  
**Source:** `09_cockpit_nodes.md` §1, §3

### Mapping:
- [x] CORE_ROUTER / EDGE_ROUTER → RouterCockpit
- [x] OLT → OLTCockpit
- [x] AON_SWITCH → AONSwitchCockpit
- [x] ONT → ONTCockpit
- [x] AON_CPE → AONCPECockpit
- [x] CONTAINER → ContainerCockpit
- [x] Unknown → GenericCockpit

### Tests:
- Frontend cockpit tests

---

## 22.2 RouterCockpit ✅

**Status:** IMPLEMENTED  
**Source:** `09_cockpit_nodes.md` §3.1

### Features:
- [x] Header: `TotCap (Gbps): actual / maximum`
- [x] actual_gbps = round(metrics.upstream + metrics.downstream)
- [x] maximum_gbps = round(effective_capacity_mbps / 1000)
- [x] No per-port data required
- [x] Color scale by effective status

### Tests:
- Frontend router cockpit tests

---

## 22.3 OLTCockpit ✅

**Status:** IMPLEMENTED  
**Source:** `09_cockpit_nodes.md` §3.2

### Features:
- [x] PON matrix from `ports` list
- [x] Tile color from effective_status
- [x] Occupancy shown as count
- [x] Click to drill-down
- [x] Data from `usePortSummary` (polling `/api/ports/summary/{olt_id}`)

### Tests:
- Frontend OLT cockpit tests

---

## 22.4 AONSwitchCockpit ✅

**Status:** IMPLEMENTED  
**Source:** `09_cockpit_nodes.md` §3.3

### Features:
- [x] ACCESS matrix (used/total)
- [x] Color by status
- [x] Uplink summary badge

### Tests:
- Frontend AON cockpit tests

---

## 22.5 Accessibility ✅

**Status:** IMPLEMENTED  
**Source:** `09_cockpit_nodes.md` §4

### Features:
- [x] Semantic headings and ARIA labels
- [x] Keyboard navigation between tiles
- [x] Visible focus indicators
- [x] High-contrast mode support

### Tests:
- Frontend accessibility tests

---

# **PHASE 23: INTERFACES & ADDRESSES**

## 23.1 Interface Model ✅

**Status:** IMPLEMENTED  
**Source:** `10_interfaces_and_addresses.md` §2.1

### Fields:
- [x] id, name, mac
- [x] role: MANAGEMENT | P2P_UPLINK | ACCESS (legacy)
- [x] port_role: ACCESS | UPLINK | PON | TRUNK (preferred)
- [x] admin_status: UP | DOWN
- [x] effective_status: UP | DOWN | DEGRADED | UNKNOWN
- [x] addresses: AddressOut[]

### Tests:
- `backend/tests/test_interfaces_*.py`

---

## 23.2 Address Model ✅

**Status:** IMPLEMENTED  
**Source:** `10_interfaces_and_addresses.md` §2.2

### Fields:
- [x] ip (IPv4 dotted)
- [x] prefix_len (CIDR)
- [x] primary (boolean, implicit first address)
- [x] vrf_id, prefix_id (nullable)
- [x] Multiple addresses per interface supported

### Uniqueness:
- [x] VRF-scoped: `UniqueConstraint("vrf_id", "ip")`
- [x] Prefix-scoped: `UniqueConstraint("prefix_id", "ip")`

### Tests:
- `backend/tests/test_ip_uniqueness_and_audit.py`

---

## 23.3 Interface Naming ✅

**Status:** IMPLEMENTED  
**Source:** `10_interfaces_and_addresses.md` §2.3

### Features:
- [x] Unique and stable within device
- [x] Deterministic generation from PortProfiles
- [x] Naming scheme: Single ports use exact name, multiple ports use `base + index`
- [x] Management interface: conventionally `mgmt0`
- [x] ID schema: `{device.id}-{if_name}`

### Tests:
- `backend/tests/test_interfaces_*.py`

---

## 23.4 MAC Address Generation ✅

**Status:** IMPLEMENTED  
**Source:** `10_interfaces_and_addresses.md` §2.4

### Features:
- [x] Local OUI: `02:55:4E` + monotonic counter
- [x] Format: `xx:xx:xx:xx:xx:xx`
- [x] Initialization from DB state on first use
- [x] Global uniqueness: `UniqueConstraint("mac_address")`
- [x] Implementation: `backend/services/mac_allocator.py`

### Tests:
- `backend/tests/test_interfaces_mac_and_api.py`

---

# **PHASE 24: PATHFINDING (ADVANCED)**

## 24.1 Collapsed Optical Access Edge ✅

**Status:** IMPLEMENTED  
**Source:** `03_ipam_and_status.md` §18

### Features:
- [x] Synthetic logical edge: ONT → nearest OLT
- [x] Selection: Lowest hop count over optical subgraph
- [x] Tie-breaking: Lexicographically on full path tuple
- [x] Edge class: `access_optical_term`, `synthetic=true`
- [x] ID schema: `collapsed_optical:<ont>-><olt>`

### Determinism:
- [x] Adjacency iteration explicitly sorted
- [x] Identical topology → identical synthetic edge

### Failure Semantics:
- [x] No OLT reachable → No edge (status = `no_router_path`)
- [x] Internal exception → Swallowed (logged), no edge

### Tests:
- `backend/tests/test_pathfinding_*.py`

---

## 24.2 Cache Invalidation ✅

**Status:** IMPLEMENTED  
**Source:** `04_signal_budget_and_overrides.md` §6.6

### Features:
- [x] Global cache flush on topology change
- [x] `PathfindingStore.bump_version()` increments `topo_version`
- [x] `resolve_optical_path.cache_clear()` on LRU cache
- [x] Triggers:
  - Link create/delete
  - Link.length_km / physical_medium_id update
  - Device.insertion_loss_db update
  - OLT.tx_power_dbm / ONT.sensitivity_min_dbm update

### Tests:
- `backend/tests/test_optical_recompute_hook.py`

---

# **PENDING FEATURES (HIGH PRIORITY)**

## ❗ TASK-027: P2P /31 Pool 🔴

**Status:** PENDING (CRITICAL)  
**Source:** `03_ipam_and_status.md` §4.1, `02_provisioning_model.md` §3.12

### Features Needed:
- [ ] P2P pool: /31 slices from 10.3.0.0/16 supernet
- [ ] Router-to-router link creation triggers /31 allocation
- [ ] Deterministic IP assignment (lower IP → lower device_id)
- [ ] Interface creation in pairs (role: p2p_uplink)
- [ ] VRF isolation (dedicated "transit" or "infrastructure" VRF)
- [ ] DB constraint: /31 must bind to exactly two interfaces

**Estimate:** 2-3 days  
**Blocking:** Router-to-router link creation with IP allocation

---

## ❗ Link Creation Enhancement 🔴

**Status:** CRITICAL  
**Source:** All docs (implied)

### Current Limitations:
- ❌ No fiber type selection (PhysicalMedium dropdown)
- ❌ No link length input (length_km)
- ❌ No hardware model awareness (port profiles)
- ❌ No optical path resolution trigger
- ❌ No capacity calculation
- ❌ Simplified dependency validation

### Needed:
- [ ] Fiber type dropdown (from `/api/optical/fiber-types`)
- [ ] Length input field (length_km, float, step 0.01)
- [ ] Hardware model integration (port profiles, capacities)
- [ ] Optical path resolution trigger on create
- [ ] Capacity calculation from port profiles
- [ ] Full dependency validation (link type rules L1-L9)
- [ ] Port occupancy check before create
- [ ] Visual feedback (color by link type)

**Estimate:** 3-4 days  
**Blocking:** Production-ready link management

---

## ❗ Hardware Catalog API Completion 🟡

**Status:** MEDIUM PRIORITY  
**Source:** `06_future_extensions_and_catalog.md` §14.7

### Needed:
- [ ] `GET /api/catalog/hardware?type=OLT` - List models filtered
- [ ] `GET /api/catalog/hardware/{catalog_id}` - Single model detail
- [ ] `POST /api/catalog/hardware` - Create custom model
- [ ] `PATCH /api/catalog/hardware/{id}` - Update model
- [ ] `DELETE /api/catalog/hardware/{id}` - Delete model

**Estimate:** 1-2 days

---

## ❗ Link Metrics Event Emission 🟡

**Status:** MEDIUM PRIORITY (Phase 2, TASK-057)  
**Source:** `06_future_extensions_and_catalog.md` §15.10

### Needed:
- [ ] `linkMetricsUpdated` event emission
- [ ] Snapshot extension: `links` dictionary in `/api/metrics/snapshot`
- [ ] Per-link counters with version tracking
- [ ] Frontend: `linkMetricsStore` for delta handling

**Estimate:** 2-3 days

---

# **DEFERRED FEATURES (FUTURE PHASES)**

## 🟣 Advanced Features

**Source:** `06_future_extensions_and_catalog.md` §13

### Networking:
- [ ] Dual-stack IPv6 support
- [ ] Multi-backbone domains
- [ ] Advanced path caching with selective invalidation

### UI:
- [ ] Lasso selection
- [ ] Bulk override UI
- [ ] Additional viewer dashboards (IPAM, Signal Monitor)

### Persistence:
- [ ] Durable migrations
- [ ] De-provision IP reclamation
- [ ] Allocation audit log

### Simulation:
- [ ] Advanced traffic patterns
- [ ] Per-tariff burst modeling
- [ ] Traffic classes (voice, video, data)
- [ ] QoS/shaping simulation
- [ ] Segment-level queuing

### Diagnostics:
- [ ] Path conflict analyzer
- [ ] Override audit log

### Security:
- [ ] AuthN/AuthZ
- [ ] Multi-tenancy
- [ ] RBAC

### Performance:
- [ ] Large-scale (10k devices) optimization
- [ ] Event batching refinement
- [ ] Parallel generation for large topologies
- [ ] Incremental aggregation

---

## 🟣 Multi-Technology Support

**Source:** `06_future_extensions_and_catalog.md` §13

### Planned:
- [ ] XG-PON / XGS-PON variants
- [ ] EPON support
- [ ] 10G-EPON
- [ ] Technology-specific link rules

---

## 🟣 Observability Enhancements

**Source:** `02_provisioning_model.md` §3.10

### Needed:
- [ ] Prometheus metrics export
- [ ] Counters: `provision_success_total{type}`, `provision_failure_total{reason}`
- [ ] Gauges: active devices, links, pool utilization
- [ ] Histograms: provisioning latency, optical recompute time
- [ ] Log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Request tracing (correlation IDs)
- [ ] Log aggregation (ELK stack)

---

## 🟣 API Enhancements

**Source:** `02_provisioning_model.md` §3.6-3.8

### Batch Operations:
- [ ] `POST /api/devices/bulk/provision` - Batch provisioning with dependency ordering
- [ ] `POST /api/links/bulk/create` - Batch link creation
- [ ] `POST /api/devices/bulk/delete` - Batch device deletion

### Dry-Run Mode:
- [ ] `/api/devices/{id}/provision?dry_run=1` - Preview IP allocation
- [ ] Returns prospective interface/IP without commit
- [ ] Validation-only mode

### Provision Matrix API:
- [ ] `GET /api/provision/matrix` - JSON representation for UI hints
- [ ] Returns allowed device types, dependencies, parent rules

---

# **FINAL SUMMARY**

## 📊 **Implementation Status:**

- ✅ **IMPLEMENTED:** ~92% of core features
  - Domain Model & Classification
  - Provisioning Model
  - IPAM (Management Pools)
  - Status Service & Propagation
  - Optical Signal Budget
  - WebSocket Transport
  - Hardware Catalog (basic)
  - Ports & Interfaces
  - Tariffs
  - Traffic Engine v2
  - Cockpit Nodes
  - Container Model
  - Pathfinding (advanced)

- 🟡 **PARTIAL:** ~5% (needs completion)
  - Hardware Catalog API (CRUD endpoints)
  - Link Metrics Event Emission
  - Container UI Physics (stable layout)

- 🔴 **PENDING:** ~3% (critical blockers)
  - TASK-027: P2P /31 Pool
  - Link Creation Enhancement (fiber type, length, hardware-aware)
  - Selective Cache Invalidation

- 🟣 **DEFERRED:** <1% (future phases)
  - Multi-technology support
  - Advanced tariffs
  - IPv6 support
  - Audit trail
  - Advanced observability

---

## 🎯 **NEXT SPRINT PRIORITIES:**

### Week 1: Critical Blockers
1. **TASK-027: P2P /31 Pool Implementation** (2-3 days)
2. **Link Creation Enhancement** (3-4 days)

### Week 2: API Completion
3. **Hardware Catalog API** (1-2 days)
4. **Link Metrics Event Emission** (2-3 days)

### Week 3: Polish & Testing
5. **Container UI Physics** (2-3 days)
6. **Accessibility Enhancements** (1-2 days)
7. **Performance Testing** (1-2 days)

---

**Generated:** 2025-10-14  
**Source:** `/backupdocs/` files 01-11 (COMPLETE)  
**Status:** ✅ EXTRACTION COMPLETE - READY FOR IMPLEMENTATION  
**Total Features Documented:** 287  
**Documentation Pages Analyzed:** 11
