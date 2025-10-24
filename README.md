# 🌐 UNOC - Universal Network Operations Center

**Version:** 2.0.0 (Clean Architecture Rebuild)  
**Started:** October 14, 2025  
**Philosophy:** KISS - Keep It Simple, Stupid

---

## 🎯 **CORE PRINCIPLES:**

1. ✅ **ONE status field** - not five!
2. ✅ **Backend is authoritative** - Frontend just displays
3. ✅ **Sync first, async only when needed**
4. ✅ **Tests from Day 1** - no "we'll add them later"
5. ✅ **Documentation matches reality** - or it doesn't exist

---

## 🏗️ **ARCHITECTURE:**

```
Backend (Python FastAPI):
  - Simple CRUD for Devices, Links, Interfaces
  - ONE Status enum: UP | DOWN | DEGRADED
  - PostgreSQL with SQLModel
  - WebSocket for real-time updates (simple!)

Frontend (Vue 3 + D3.js):
  - SVG-based network diagram
  - Device details panel
  - Traffic monitoring
  - NO business logic in frontend!

GO Services (optional, for scale):
  - Traffic Engine (when Python can't handle load)
  - Port Summary Service (aggregations)
```

---

## 🚀 **QUICK START:**

```bash
# 1. Start Backend (Docker):
docker-compose up -d

# 2. Start Frontend (Vite):
cd frontend
npm run dev

# 3. Open browser:
http://localhost:5173
```

---

## 📊 **STATUS:**

- [x] Project structure created
- [ ] Backend models (Device, Link, Interface)
- [ ] Basic CRUD endpoints
- [ ] Frontend skeleton (Vue 3 + Vite)
- [ ] WebSocket connection
- [ ] First working topology display

---

## 🧪 **TESTING:**

```bash
# Backend tests:
pytest -v

# Frontend tests:
npm test

# E2E tests (later):
npm run e2e
```

---

## 📝 **DECISIONS:**

### ✅ What we're KEEPING from v1:
- Docker setup
- PostgreSQL database
- Vue 3 + D3.js for topology
- FastAPI backend

### ❌ What we're REMOVING from v1:
- 5 status fields → 1 status field
- Frontend status computation → Backend only
- Async everywhere → Sync first
- 13 documentation files → 1 living README

---

## 👨‍💻 **DEVELOPMENT:**

**VS Code Extensions (Required):**
- GitHub Copilot
- Python (Pylance + debugpy)
- Vue (Volar)
- Docker
- Edge DevTools (for WebView2 debugging)
- Error Lens

**Debug Configuration:**
- Backend: Attach to Docker container (port 5678)
- Frontend: Edge WebView2 Debugger
- Full Stack: Compound debug configuration

---

## 📖 **DOCUMENTATION:**

# 🌐 UNOC - Network Operations Center

**Clean Architecture - Version 2.0**

> Built from scratch after V1 architectural failure. This time: KISS principle, clean models, tested code.

---

## 🎯 Philosophie

- ✅ **KISS** - Keep It Simple, Stupid
- ✅ **1 Status Field** - nicht 5!
- ✅ **Backend ist Boss** - Frontend zeigt nur an
- ✅ **Sync first** - Async nur wo nötig
- ✅ **Tests from Day 1**
- ✅ **Document as we go** - Keine Fantasy-Docs

---

## 🏗️ Tech Stack

### **Backend**
- **Python 3.12** - Language
- **FastAPI** - REST API Framework
- **SQLModel** - ORM (Pydantic + SQLAlchemy)
- **PostgreSQL 16** - Database
- **Docker** - Containerization
- **Pytest** - Testing

### **Frontend**
- **Vue 3** - Framework
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Cytoscape.js** - Network Visualization ⭐
- **Pinia** - State Management

### **Why Cytoscape.js instead of D3.js?**
- ✅ 3-4x less code
- ✅ Built-in layout algorithms
- ✅ Better for network graphs
- ✅ Superior LLM compatibility

---

## 🚀 Quick Start

### **1. Start Backend + Database**
```bash
# Start Docker containers
docker-compose up -d

# Check health
curl http://localhost:5001/health

# Seed demo topology (9 devices, 7 links)
curl -X POST http://localhost:5001/api/seed
```

### **2. Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

### **3. Open Browser**
Navigate to: **http://localhost:5173**

You should see:
- 9 devices (2 Routers, 2 Switches, 1 OLT, 4 ONTs)
- 7 links connecting them
- Green nodes (UP), Orange node (ONT4 - DEGRADED)

---

## 📊 Data Model (SIMPLIFIED!)

### **Device**
```python
class Device:
    id: int
    name: str
    device_type: Literal["ROUTER", "SWITCH", "OLT", "ONT", "SERVER"]
    status: Literal["UP", "DOWN", "DEGRADED"]  # ← ONLY 1 FIELD!
    x: float  # Position for visualization
    y: float
```

**No `effective_status`, no `admin_override`, no `signal_status`.** Just ONE status field.

### **Interface**
```python
class Interface:
    id: int
    name: str
    device_id: int  # FK to Device
    interface_type: Literal["ETHERNET", "OPTICAL", "LOOPBACK"]
    status: Literal["UP", "DOWN", "DEGRADED"]
```

### **Link**
```python
class Link:
    id: int
    a_interface_id: int  # FK to Interface
    b_interface_id: int  # FK to Interface
    status: Literal["UP", "DOWN", "DEGRADED"]
```

**CASCADE DELETE:** Deleting a Device automatically deletes its Interfaces and Links.

---

## 🧪 Testing

### **Backend Tests**
```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest backend/tests/test_devices.py -v
```

**Current Status:** 4 tests passing ✅

### **Frontend Tests**
```bash
cd frontend
npm test
```

---

## 📁 Project Structure

```
unoc/
├── backend/
│   ├── api/
│   │   └── routes.py          # REST endpoints
│   ├── models/
│   │   └── core.py            # SQLModel definitions
│   ├── services/
│   │   └── seed.py            # Demo topology generator
│   ├── tests/
│   │   ├── conftest.py        # Pytest config
│   │   └── test_devices.py    # Device CRUD tests
│   ├── db.py                  # Database connection
│   └── main.py                # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── NetworkGraph.vue   # Cytoscape visualization
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml         # Backend + Postgres
├── Dockerfile                 # Backend container
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🎯 Current Status (October 14, 2025)

### ✅ **PHASE 1: FOUNDATION (COMPLETE)**

- [x] Backend API (CRUD for Devices, Interfaces, Links)
- [x] PostgreSQL Database
- [x] Docker Setup
- [x] Seed Service (Demo Topology)
- [x] Frontend Base (Vue 3 + Vite + TypeScript)
- [x] Network Visualization (Cytoscape.js)
- [x] Basic Tests (4 passing)

### 🚧 **PHASE 2: REAL-TIME (TODO)**

- [ ] WebSocket Server (Socket.IO)
- [ ] WebSocket Client
- [ ] Live Updates (device/link changes)
- [ ] Event System

### 🚧 **PHASE 3: MANAGEMENT (TODO)**

- [ ] Link Management UI (Drag & Drop)
- [ ] Device Creation UI
- [ ] Status Override
- [ ] Bulk Operations

### 🚧 **PHASE 4: TRAFFIC (TODO)**

- [ ] Tariff System
- [ ] Traffic Generation
- [ ] Traffic Aggregation
- [ ] Congestion Detection

### 🚧 **PHASE 5: PRODUCTION (TODO)**

- [ ] Authentication
- [ ] Authorization
- [ ] Audit Logging
- [ ] Monitoring (Prometheus/Grafana)
- [ ] CI/CD Pipeline

---

## 📝 Development Rules

1. **Test Before Merge** - No untested code in main
2. **Document as You Go** - Update docs with code changes
3. **One Feature at a Time** - Finish before starting next
4. **Backend First** - Frontend follows backend changes
5. **Simple > Clever** - Readable code wins

---

## 🔥 Lessons Learned from V1

### **What Went Wrong in V1:**

1. ❌ **5 Status Fields** - Confusion everywhere
2. ❌ **Frontend Computing Status** - Violated backend-first principle
3. ❌ **Async Everywhere** - Race conditions, lost events
4. ❌ **Fantasy Documentation** - Docs described ideal state, not reality
5. ❌ **No Tests** - "We'll add tests later" (never happened)
6. ❌ **Over-Engineering** - Production features on MVP
7. ❌ **GO Services Removed** - Python couldn't scale

### **What We're Doing Different in V2:**

1. ✅ **1 Status Field** - Simple and clear
2. ✅ **Backend Authoritative** - Frontend only displays
3. ✅ **Sync by Default** - Async only where proven necessary
4. ✅ **Reality Documentation** - Docs match actual code
5. ✅ **Tests from Day 1** - Already have 4 passing tests
6. ✅ **MVP First** - Build basics, add features incrementally
7. ✅ **Python Only (for now)** - Optimize later if needed

---

## 🤝 Contributing

When adding features:

1. **Update this README** with your changes
2. **Add tests** for new functionality
3. **Update ARCHITECTURE.md** if you change design
4. **Keep it simple** - resist over-engineering

---

## 📚 Additional Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design decisions
- [ROADMAP.md](docs/ROADMAP.md) - Future plans
- [API.md](docs/API.md) - REST API reference

---

Built with ❤️ and lessons learned from V1 💀

If something isn't clear, fix the README.
