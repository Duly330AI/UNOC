# 🏗️ UNOC V2 - Architecture Documentation

**Last Updated:** October 14, 2025  
**Status:** Phase 1 Complete (Foundation)

---

## 📋 Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Tech Stack Decisions](#tech-stack-decisions)
3. [Data Model](#data-model)
4. [API Design](#api-design)
5. [Frontend Architecture](#frontend-architecture)
6. [Testing Strategy](#testing-strategy)
7. [Deployment](#deployment)
8. [Lessons from V1](#lessons-from-v1)

---

## 🎯 Design Philosophy

### **Core Principles**

1. **KISS - Keep It Simple, Stupid**
   - No premature optimization
   - No "maybe we'll need this later" features
   - Build for today's requirements

2. **Backend Authoritative**
   - Backend computes all statuses
   - Frontend only displays data
   - No business logic in UI

3. **Synchronous by Default**
   - Async only where proven necessary
   - Avoid race conditions
   - Easier debugging

4. **Test From Day 1**
   - Tests before features
   - Integration tests preferred
   - No "we'll test later"

5. **Reality Documentation**
   - Docs describe actual code
   - Update docs with code changes
   - No aspirational documentation

---

## 🔧 Tech Stack Decisions

### **Backend: Python + FastAPI**

**Why Python?**
- ✅ Excellent async support (when needed)
- ✅ Rich ecosystem (SQLModel, Pydantic)
- ✅ Fast development
- ✅ Easy to test
- ❌ Slower than GO (but fast enough for MVP)

**Why FastAPI?**
- ✅ Automatic OpenAPI docs
- ✅ Pydantic validation built-in
- ✅ WebSocket support
- ✅ Async support (for Phase 2)
- ✅ Type hints everywhere

**Alternative Considered:** GO + Fiber
- ❌ Rejected: Higher complexity for MVP
- ⚠️ Revisit: If we hit 1000+ devices and need microsecond response

### **Database: PostgreSQL**

**Why PostgreSQL?**
- ✅ ACID compliance
- ✅ JSON support (for future flexibility)
- ✅ Full-text search built-in
- ✅ Mature and stable
- ✅ Great with SQLAlchemy

**Why NOT MongoDB?**
- ❌ Overkill for structured network data
- ❌ No foreign key constraints
- ❌ Schema validation harder

**Why NOT SQLite?**
- ❌ Used only for tests (fast, in-memory)
- ❌ Not for production (no concurrent writes)

### **ORM: SQLModel**

**Why SQLModel?**
- ✅ Pydantic models = SQLAlchemy tables
- ✅ No duplicate definitions
- ✅ Type hints for IDE autocomplete
- ✅ FastAPI integration out-of-box

```python
# ONE definition, works as:
# 1. SQLAlchemy table
# 2. Pydantic model for API
# 3. Type hints for IDE
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    status: Status
```

### **Frontend: Vue 3 + Cytoscape.js**

**Why Vue 3 instead of React?**
- ✅ Simpler syntax (less boilerplate)
- ✅ Better TypeScript integration
- ✅ Composition API (clean state management)
- ❌ React considered but rejected (more complex for our use case)

**Why Cytoscape.js instead of D3.js?**

**Critical Decision - Backed by Data:**

| Metric | D3.js | Cytoscape.js | Winner |
|--------|-------|--------------|--------|
| Lines of Code | ~200 | ~50 | ⭐ Cytoscape (4x less) |
| Built-in Layout | ❌ Manual | ✅ Auto | ⭐ Cytoscape |
| Event Handling | ❌ Manual | ✅ Built-in | ⭐ Cytoscape |
| Zoom/Pan | ❌ Manual | ✅ Built-in | ⭐ Cytoscape |
| LLM Compatibility | ⚠️ Complex | ✅ Declarative | ⭐ Cytoscape |
| Network Graphs | General purpose | Specialized | ⭐ Cytoscape |

**Example:**
```javascript
// Cytoscape: 10 lines
cy.add([
  { data: { id: 'device-1', label: 'Router1' } },
  { data: { source: 'device-1', target: 'device-2' } }
])
cy.layout({ name: 'preset' }).run()

// D3.js: ~50 lines (force simulation, drag, tick updates, etc.)
```

**Recommendation Source:** Another LLM analyzed our requirements and strongly recommended Cytoscape for:
- Network topology visualization
- LLM-assisted development
- Rapid MVP development

**Decision:** ✅ Cytoscape.js - Proven correct after implementation (working visualization in 1 day!)

---

## 📊 Data Model

### **Design Decision: 1 Status Field**

**V1 Mistake:**
```python
class Device:
    status: Status
    effective_status: str | None
    admin_override_status: str | None
    signal_status: str | None
    upstream_l3_ok: bool | None
```
❌ **Result:** Confusion, bugs, inconsistent state

**V2 Fix:**
```python
class Device:
    status: Status  # UP | DOWN | DEGRADED
```
✅ **Result:** Simple, clear, single source of truth

### **Entities**

#### **Device**
```python
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    device_type: DeviceType  # ROUTER | SWITCH | OLT | ONT | SERVER
    status: Status = Field(default=Status.DOWN)
    x: float = Field(default=0.0)  # Visualization position
    y: float = Field(default=0.0)
```

**Design Notes:**
- `x`, `y` stored in DB (not recomputed on every load)
- `device_type` is enum (prevents typos like "router" vs "ROUTER")
- `status` defaults to DOWN (explicit, not UP by default)

#### **Interface**
```python
class Interface(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # eth0, ge-0/0/1, pon-1/1/1, etc.
    device_id: int = Field(foreign_key="device.id", ondelete="CASCADE")
    interface_type: InterfaceType  # ETHERNET | OPTICAL | LOOPBACK
    status: Status = Field(default=Status.DOWN)
```

**Design Notes:**
- `ondelete="CASCADE"` - Deleting Device deletes Interfaces automatically
- `name` is not globally unique (Router1.eth0 vs Router2.eth0 is OK)

#### **Link**
```python
class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    a_interface_id: int = Field(foreign_key="interface.id", ondelete="CASCADE")
    b_interface_id: int = Field(foreign_key="interface.id", ondelete="CASCADE")
    status: Status = Field(default=Status.DOWN)
```

**Design Notes:**
- Links connect **Interfaces**, not Devices
- `a_` and `b_` are symmetric (no "source" vs "target")
- CASCADE DELETE: Deleting Interface deletes Links

### **Relationships**

```
Device (1) ──────── (*) Interface
                        │
                        │ (1)
                        │
                        (*) Link
```

**Example:**
```
Router1
├── eth0 ────── Link1 ────── eth0 (Switch1)
└── eth1 ────── Link2 ────── eth0 (Router2)
```

---

## 🔌 API Design

### **Principles**

1. **RESTful** - Standard HTTP methods (GET, POST, DELETE)
2. **Status Codes** - 201 (Created), 204 (No Content), 404 (Not Found)
3. **JSON** - All requests and responses
4. **Validation** - Pydantic models enforce schema

### **Endpoints (Phase 1)**

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| GET | `/api/devices` | List all devices | 200 |
| POST | `/api/devices` | Create device | 201 |
| DELETE | `/api/devices/{id}` | Delete device | 204 |
| GET | `/api/interfaces` | List all interfaces | 200 |
| POST | `/api/interfaces` | Create interface | 201 |
| DELETE | `/api/interfaces/{id}` | Delete interface | 204 |
| GET | `/api/links` | List all links | 200 |
| POST | `/api/links` | Create link | 201 |
| DELETE | `/api/links/{id}` | Delete link | 204 |
| POST | `/api/seed` | Seed demo topology | 201 |

### **Example: Create Device**

**Request:**
```bash
POST /api/devices
Content-Type: application/json

{
  "name": "Router3",
  "device_type": "ROUTER",
  "status": "UP",
  "x": 500.0,
  "y": 100.0
}
```

**Response:**
```json
{
  "id": 11,
  "name": "Router3",
  "device_type": "ROUTER",
  "status": "UP",
  "x": 500.0,
  "y": 100.0
}
```
**Status:** 201 Created

### **Error Handling**

**404 Not Found:**
```json
{
  "detail": "Device with ID 999 not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "device_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

---

## 🖼️ Frontend Architecture

### **Structure**

```
src/
├── main.ts              # App initialization
├── App.vue              # Root component, data fetching
├── components/
│   └── NetworkGraph.vue # Cytoscape visualization
└── stores/
    └── network.ts       # Pinia store (future)
```

### **Data Flow**

```
1. App.vue fetches data (devices, interfaces, links)
2. Pass via props to NetworkGraph.vue
3. NetworkGraph renders with Cytoscape
4. User interactions → Events → Pinia Store → API
```

### **Cytoscape Integration**

**Key Implementation Detail: Interface-to-Device Mapping**

```typescript
// Problem: Links connect Interfaces, but Cytoscape renders Devices
// Solution: Map interface IDs to device IDs

const interfaceToDevice = new Map<number, number>()
props.interfaces.forEach((intf: Interface) => {
  interfaceToDevice.set(intf.id, intf.device_id)
})

// Convert Links to Cytoscape Edges
const edges = props.links.map((link: Link) => {
  const sourceDeviceId = interfaceToDevice.get(link.a_interface_id)
  const targetDeviceId = interfaceToDevice.get(link.b_interface_id)
  return {
    data: {
      source: `device-${sourceDeviceId}`,
      target: `device-${targetDeviceId}`,
      status: link.status
    }
  }
})
```

**Why This Matters:**
- Links stored in DB as `interface ↔ interface`
- Cytoscape renders `device ↔ device`
- Mapping bridges the gap without changing data model

### **Styling**

```typescript
{
  selector: 'node',
  style: {
    'background-color': (ele) => {
      switch (ele.data('status')) {
        case 'UP': return '#4caf50'      // Green
        case 'DOWN': return '#f44336'    // Red
        case 'DEGRADED': return '#ff9800' // Orange
      }
    },
    'label': 'data(label)',
    'width': 40,
    'height': 40
  }
}
```

**Color Coding:**
- 🟢 Green: UP
- 🟠 Orange: DEGRADED
- 🔴 Red: DOWN

---

## 🧪 Testing Strategy

### **Backend Tests**

**Framework:** Pytest with pytest-asyncio

**Fixtures (conftest.py):**
```python
@pytest.fixture
async def session():
    # SQLite in-memory for fast tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
```

**Test Structure:**
```python
@pytest.mark.asyncio
async def test_create_device(session, override_get_session):
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post("/api/devices", json={...})
    assert response.status_code == 201
    assert response.json()["name"] == "TestDevice"
```

**Current Tests (Phase 1):**
- ✅ `test_create_device` - POST /api/devices
- ✅ `test_list_devices` - GET /api/devices
- ✅ `test_delete_device` - DELETE /api/devices/{id}
- ✅ `test_device_not_found` - 404 handling

**Status:** All 4 tests passing ✅

### **Frontend Tests (Planned Phase 2)**

- Vitest for unit tests
- Playwright for E2E tests
- Component tests for NetworkGraph

---

## 🚀 Deployment

### **Phase 1: Development**

**Current Setup:**
```bash
# Backend + Database
docker-compose up -d

# Frontend
cd frontend
npm run dev
```

**Services:**
- Backend: http://localhost:5001
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432

### **Phase 5: Production (Future)**

**Planned:**
- Docker images pushed to registry
- Kubernetes deployment
- HTTPS with Let's Encrypt
- PostgreSQL with persistent volumes
- Redis for session storage
- Prometheus + Grafana monitoring

---

## 💀 Lessons from V1

### **What Killed V1**

#### **1. Five Status Fields**
```python
# V1 (WRONG):
status: Status
effective_status: str | None      # ← What is this?
admin_override_status: str | None # ← Wait, what?
signal_status: str | None         # ← Seriously?
upstream_l3_ok: bool | None       # ← WTF?
```

**Problem:** Nobody understood which field was "truth"

**V2 Solution:** ONE field. That's it.

#### **2. Frontend Computing Status**

**V1 Mistake:**
```javascript
// Frontend computed effective_status from multiple fields
const effectiveStatus = device.admin_override_status 
  || device.signal_status 
  || device.status
```

**Problem:** Business logic in two places (backend + frontend)

**V2 Solution:** Backend computes everything, frontend only displays

#### **3. Async Everywhere**

**V1 Mistake:**
```python
# Every function was async
async def get_device(device_id: int) -> Device:
    async with get_session() as session:
        result = await session.execute(select(Device)...)
        return result.scalar_one()
```

**Problem:** Race conditions, lost events, hard to debug

**V2 Solution:** Sync by default, async only where necessary (WebSockets in Phase 2)

#### **4. Fantasy Documentation**

**V1 Mistake:**
```markdown
## Status Propagation (PLANNED)
When OLT goes down, all ONTs will automatically mark as UNREACHABLE...
```

**Problem:** Docs described ideal future state, not current reality

**V2 Solution:** Docs describe actual working code. Update docs WITH code changes.

#### **5. No Tests**

**V1 Reality:**
```bash
$ pytest
ERROR: No tests found
```

**Problem:** "We'll add tests later" (never happened)

**V2 Solution:** Tests from Day 1. Already have 4 passing tests before first feature.

---

## 🔮 Future Considerations

### **Phase 2: WebSockets**
- Socket.IO for real-time updates
- Events: `device:created`, `device:updated`, `link:updated`
- Frontend listens and updates Cytoscape live

### **Phase 3: Link Management**
- Drag & drop interface creation
- Visual link creation (click device A → device B)
- Interface auto-creation or hardware catalog

### **Phase 4: Traffic System**
- Tariff-based traffic generation (asymmetric upload/download)
- Traffic aggregation (sum child traffic to parent)
- Congestion detection (threshold + hysteresis)

### **Phase 5: Production**
- Authentication (JWT)
- Authorization (RBAC)
- Audit logging
- Metrics (Prometheus)
- Dashboards (Grafana)

---

## 📚 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Cytoscape.js Docs](https://js.cytoscape.org/)
- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

**Last Updated:** October 14, 2025  
**Next Update:** When Phase 2 (WebSockets) begins

