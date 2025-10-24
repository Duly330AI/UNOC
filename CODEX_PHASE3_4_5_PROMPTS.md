# UNOC Documentation Audit - PHASE 3, 4 & 5 Combined Prompts
# Frontend, Deployment, and Quality Documentation
# ============================================================================

## CONTEXT

You have successfully completed Phases 1-2:
- ✅ **Phase 1:** Core docs (README, ROADMAP, ARCHITECTURE, MASTER_ACTION_PLAN, Copilot guidelines)
- ✅ **Phase 2:** Backend API & Services (7 domain/provisioning/override/link/WebSocket/error docs + enhanced backend docstrings)

Now we move to the **final three phases:**
- **Phase 3:** Frontend & UI Documentation
- **Phase 4:** Deployment & Operations  
- **Phase 5:** Tests, Coverage & Quality Metrics

These three phases are **non-overlapping** and can run **in parallel** or **sequentially**. We recommend sequential for clarity, but Phases 3 and 4 are independent.

---

# PHASE 3: FRONTEND & UI DOCUMENTATION

## Overview

Frontend is the **user-facing layer**. It consumes the REST API and WebSocket events from the backend to render the topology, device management, and real-time updates.

**Key Components:**
- Vue 3 SPA with Vite bundler
- Pinia for state management
- Cytoscape.js for topology graph rendering
- Socket.IO client for real-time events
- TypeScript for type safety

**Goal:** Document how the UI works so developers can:
1. Add new UI features (tabs, overlays, modals)
2. Extend component hierarchy
3. Integrate new WebSocket events
4. Manage state correctly

---

## PHASE 3 FILES TO CREATE/UPDATE

### 1. **docs/07_frontend_architecture.md** (Create)

**Purpose:** Explain Vue 3 component structure and state management

**Should include:**
- [ ] Project structure: `frontend/src/` layout (components/, stores/, App.vue, etc.)
- [ ] Vite build process & hot module reload
- [ ] Pinia store pattern for shared state (selected device, filters, etc.)
- [ ] Component hierarchy: App → DeviceView → DeviceSidebar → tabs
- [ ] TypeScript setup & conventions
- [ ] Build output location and Docker integration

**Example sections:**
```markdown
## Component Hierarchy

App.vue (root)
├── TopologyCanvas.vue (Cytoscape graph)
├── DeviceSidebar.vue (selected device details)
│   ├── OverviewTab.vue
│   ├── InterfacesTab.vue
│   └── OpticalTab.vue
├── DeviceModal.vue (create/edit device)
└── LinkModal.vue (create/edit link)

### Data Flow
1. User selects device on canvas
2. Cytoscape fires `select` event
3. App.vue updates Pinia store (selected device)
4. DeviceSidebar watches store and renders tabs
5. User changes override → API call → WebSocket event → all clients update
```

---

### 2. **docs/08_pinia_store_design.md** (Create)

**Purpose:** Document the state management pattern

**Should document:**
- [ ] Current stores (list each one)
- [ ] Each store's state fields, getters, actions
- [ ] When state changes (user action, WebSocket event)
- [ ] Why Pinia vs. other solutions (composition API, reactivity, devtools)
- [ ] Example: selecting a device, adding a link

**Example:**
```markdown
## Store: DeviceStore

### State
```typescript
interface DeviceState {
  devices: Device[]
  selectedDeviceId: number | null
  loading: boolean
  error: string | null
}
```

### Getters
- `selectedDevice`: Returns the current device or null
- `deviceCount`: Total device count

### Actions
- `fetchDevices()`: GET /api/devices
- `selectDevice(id)`: Update selectedDeviceId
- `deleteDevice(id)`: DELETE /api/devices/{id} → update store
- ... (others)

### Example Usage
```vue
<script setup>
import { useDeviceStore } from '@/stores/deviceStore'
const store = useDeviceStore()

const device = computed(() => store.selectedDevice)
const onSelect = (id) => store.selectDevice(id)
</script>
```
```

---

### 3. **docs/09_websocket_integration.md** (Create)

**Purpose:** Explain how Vue listens to Socket.IO events

**Should cover:**
- [ ] Socket.IO client initialization (where, how, reconnection)
- [ ] Event listeners registered in App.vue (which events, which components)
- [ ] Payload unpacking and store updates
- [ ] Error handling (event listener failures, connection loss)
- [ ] Throttling/batching for high-frequency events (future: traffic updates)
- [ ] Testing WebSocket listeners

**Example:**
```markdown
## Socket.IO Integration

### Client Setup (App.vue or boot script)
```javascript
import io from 'socket.io-client'

const socket = io('http://localhost:5001', {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5,
})

// Subscribe to key events
socket.on('device:created', (payload) => {
  const store = useDeviceStore()
  store.devices.push(payload)
})

socket.on('device:updated', (payload) => {
  const store = useDeviceStore()
  const idx = store.devices.findIndex(d => d.id === payload.id)
  if (idx >= 0) store.devices[idx] = payload
})
```

### Events Subscribed
| Event | Handler | Store Update |
|-------|---------|--------------|
| `device:created` | Add to devices list | DeviceStore.devices.push(...) |
| `device:updated` | Replace device in list | DeviceStore.devices[idx] = ... |
| `device:deleted` | Remove from list | DeviceStore.devices.splice(...) |
| `link:created` | Add to links list | LinkStore.links.push(...) |
| `link:deleted` | Remove from list | LinkStore.links.splice(...) |
```

---

### 4. **docs/10_ui_patterns_and_examples.md** (Create)

**Purpose:** Show common UI patterns and component usage

**Should include:**
- [ ] How to add a new tab to DeviceSidebar
- [ ] How to create a new modal for editing links
- [ ] How to handle loading & error states
- [ ] How to bind form data to v-model
- [ ] How to make API calls and show spinners
- [ ] How to use Cytoscape for graph interactions

**Example:**
```markdown
## Pattern: Add a New Tab to DeviceSidebar

### Step 1: Create component
\`\`\`vue
<!-- frontend/src/components/DeviceSidebar/NewTab.vue -->
<template>
  <div class="tab-content">
    <p>{{ device.name }} - New Tab</p>
  </div>
</template>

<script setup>
defineProps({
  device: Object,
})
</script>
\`\`\`

### Step 2: Register in DeviceSidebar
\`\`\`vue
<template>
  <div class="tabs">
    <button @click="activeTab = 'overview'">Overview</button>
    <button @click="activeTab = 'interfaces'">Interfaces</button>
    <button @click="activeTab = 'newtab'">New Tab</button>
    
    <div v-if="activeTab === 'newtab'">
      <NewTab :device="device" />
    </div>
  </div>
</template>
\`\`\`
```

---

### 5. **frontend/src/README.md** (Create or enhance)

**Purpose:** Quick reference for frontend developers

**Should include:**
- [ ] How to run frontend locally (`npm run dev`)
- [ ] Project structure overview
- [ ] Main entry points (main.ts, App.vue)
- [ ] Build & deployment (`npm run build`)
- [ ] IDE setup (VS Code, Volar extension)
- [ ] Common dev tasks (add component, add store, run tests)

---

## PHASE 3 DELIVERABLES

✅ **docs/07_frontend_architecture.md** - Component structure & Vite build  
✅ **docs/08_pinia_store_design.md** - State management patterns  
✅ **docs/09_websocket_integration.md** - Socket.IO listeners  
✅ **docs/10_ui_patterns_and_examples.md** - Component usage examples  
✅ **frontend/src/README.md** - Frontend quick reference  

---

## PHASE 3 REVIEW CHECKLIST

- [ ] Component hierarchy is clear with ASCII tree
- [ ] Pinia stores documented with examples
- [ ] WebSocket event handling shows actual code
- [ ] UI patterns are concrete, not abstract
- [ ] All code examples are tested/realistic
- [ ] Links between frontend and backend docs work
- [ ] TypeScript conventions match existing code

---

---

# PHASE 4: DEPLOYMENT & OPERATIONS

## Overview

Deployment is the **production readiness** layer. It covers:
- Docker Compose setup (local dev + production)
- Environment variables & secrets
- Database initialization & migrations
- Monitoring & logging
- Troubleshooting common issues

**Goal:** Document how to deploy, operate, and troubleshoot UNOC so:
1. New teams can get running in 10 minutes
2. Operators know how to restart, backup, debug
3. Scaling strategies are understood

---

## PHASE 4 FILES TO CREATE/UPDATE

### 1. **docs/DEPLOYMENT.md** (Create or completely refresh)

**Purpose:** Step-by-step deployment guide

**Should cover:**

#### Local Development
```markdown
## Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend)
- Python 3.10+ (for backend)
- Git

### Quick Start
1. Clone repo
2. \`cd unoc\`
3. \`docker compose up -d\`
4. \`npm run dev\` (in frontend/)
5. Visit http://localhost:5173

### What's Running
- PostgreSQL 16 on localhost:5432
- FastAPI backend on localhost:5001
- Vue dev server on localhost:5173
```

#### Production Deployment
- Environment variables (DATABASE_URL, UNOC_PORT, etc.)
- Docker image builds
- Nginx reverse proxy setup (optional)
- SSL/TLS certificates (optional)
- Database backups

#### Troubleshooting
- "Connection refused" → PostgreSQL not running
- "Port already in use" → Kill existing process or use different port
- "Module not found" → Missing Python dependency, run pip install
- Database migrations → How to initialize/reset

---

### 2. **docs/OPERATIONS.md** (Create)

**Purpose:** Operational runbook for live systems

**Should include:**
- [ ] Health checks (curl endpoints)
- [ ] How to restart services (docker compose restart)
- [ ] How to view logs (docker logs, tail)
- [ ] How to backup database (pg_dump)
- [ ] How to restore from backup
- [ ] How to add new devices/interfaces programmatically
- [ ] How to reset/clear demo data
- [ ] Performance tuning tips

**Example:**
```markdown
## Common Operations

### Check System Health
\`\`\`bash
# Backend health
curl http://localhost:5001/api/health

# Database connection
docker exec -it unoc-postgres psql -U unoc -d unocdb -c "SELECT COUNT(*) FROM devices;"
\`\`\`

### View Logs
\`\`\`bash
# Backend logs
docker logs -f unoc-backend

# Database logs
docker logs -f unoc-postgres
\`\`\`

### Backup Database
\`\`\`bash
docker exec unoc-postgres pg_dump -U unoc unocdb > backup.sql
\`\`\`

### Restore Database
\`\`\`bash
docker exec -i unoc-postgres psql -U unoc unocdb < backup.sql
\`\`\`
```

---

### 3. **docker-compose.yml** (Audit & document)

**Action:** Add comments to explain each service

```yaml
version: "3.8"

services:
  # PostgreSQL 16 - Data store for devices, interfaces, links, status overrides
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: unoc          # Database user
      POSTGRES_PASSWORD: unocpw    # Password (change in production!)
      POSTGRES_DB: unocdb          # Initial database name
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist across restarts
    ports:
      - "5432:5432"

  # FastAPI backend - API, provisioning, WebSocket, optional traffic simulation
  backend:
    build: .  # Builds using Dockerfile
    environment:
      DATABASE_URL: postgresql+psycopg://unoc:unocpw@postgres:5432/unocdb
      UNOC_PORT: 5001
      # Add other env vars here
    ports:
      - "5001:5001"
    depends_on:
      - postgres
```

---

### 4. **.env.example** (Create if missing)

**Purpose:** Document all environment variables

```env
# Database
DATABASE_URL=postgresql+psycopg://unoc:unocpw@localhost:5432/unocdb

# Backend
UNOC_PORT=5001
UNOC_ASYNC_MODE=threading
UNOC_SHUTDOWN_TOKEN=dev
UNOC_DEV_FEATURES=1

# Optional: Traffic engine
USE_GO_TRAFFIC=0
USE_PORT_SUMMARY_SERVICE=1

# Optional: Seed data
AUTO_ASSIGN_DEFAULT_HARDWARE=1
```

---

### 5. **ops/RUNBOOK.md** (Create)

**Purpose:** Day-to-day operations guide

**Include:**
- Daily health checks
- Weekly maintenance (logs cleanup, backup verification)
- Monthly scaling review
- Incident response (database down, backend crashed, etc.)
- Backup/restore procedures
- Performance monitoring (CPU, memory, disk)

---

## PHASE 4 DELIVERABLES

✅ **docs/DEPLOYMENT.md** - Complete deployment guide (local + production)  
✅ **docs/OPERATIONS.md** - Operational runbook  
✅ **docker-compose.yml** - Commented & clear  
✅ **.env.example** - All env vars documented  
✅ **ops/RUNBOOK.md** - Day-to-day operations  

---

## PHASE 4 REVIEW CHECKLIST

- [ ] Deployment steps are copy-paste-able (tested on clean machine)
- [ ] All environment variables documented with defaults
- [ ] Docker Compose setup is clear
- [ ] Troubleshooting covers 90% of common issues
- [ ] Backup/restore procedures documented
- [ ] Health check commands provided
- [ ] No hardcoded secrets (use env vars)
- [ ] Production checklist included (SSL, backups, monitoring)

---

---

# PHASE 5: TESTS, COVERAGE & QUALITY METRICS

## Overview

Quality assurance is the **confidence layer**. It covers:
- Test strategy and structure
- Running tests locally
- Coverage reporting
- CI/CD pipeline documentation
- Quality gates (linting, type checking)

**Goal:** Document testing practices so:
1. Developers know how to run tests
2. CI/CD pipeline is clear
3. Coverage gaps are identified
4. Quality standards are enforced

---

## PHASE 5 FILES TO CREATE/UPDATE

### 1. **docs/TESTING.md** (Create)

**Purpose:** Complete testing guide

**Should cover:**

#### Test Structure
```markdown
## Backend Test Organization

backend/tests/
├── test_provisioning.py        # Provisioning service & API
├── test_status_override.py     # Status override functionality
├── test_link_validation.py     # Link rules (L1-L9)
├── test_websocket_events.py    # WebSocket broadcasting
├── conftest.py                 # Shared fixtures (in-memory SQLite, etc.)
└── ... (others)

### Test Categories
- **Unit tests:** Individual functions (provisioning_service methods)
- **Integration tests:** API endpoints with database
- **E2E tests:** Full workflows (provision → override → delete)
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific file
pytest backend/tests/test_provisioning.py

# Run with coverage
pytest --cov=backend --cov-report=term-missing

# Run specific test
pytest backend/tests/test_provisioning.py::test_provision_device_success
```

#### Frontend Tests
```markdown
## Frontend Testing (if applicable)

\`\`\`bash
npm run test          # Run vitest
npm run test:coverage # Coverage report
\`\`\`

Test files: \`frontend/src/__tests__/\`
```

---

### 2. **docs/QUALITY_GATES.md** (Create)

**Purpose:** Document quality standards and CI/CD

**Should include:**
- [ ] Linting rules (Ruff for Python, ESLint for JS)
- [ ] Type checking (Pylance for Python, TypeScript for frontend)
- [ ] Coverage minimums (e.g., 80% for backend)
- [ ] PR checklist (tests pass, linting passes, coverage doesn't drop)
- [ ] Pre-commit hooks (optional)

**Example:**
```markdown
## Quality Gates

### Backend
- **Linting:** \`ruff check backend\` must pass
- **Type checking:** \`pylance --strict\` (enforced via IDE)
- **Testing:** All tests must pass (\`pytest\`)
- **Coverage:** Minimum 80% (\`pytest --cov\`)

### Frontend
- **Linting:** \`npm run lint\` must pass
- **Type checking:** TypeScript strict mode
- **Testing:** All tests pass (\`npm run test\`)

### Pre-Commit
\`\`\`bash
# Run before committing
ruff check backend
pytest --cov=backend
npm run lint (in frontend/)
\`\`\`
```

---

### 3. **pytest.ini** (Audit & document)

**Action:** Add comments explaining configuration

```ini
[pytest]
# Run tests from backend/tests/
testpaths = backend/tests

# Required Python version
python_files = test_*.py

# Markers for categorizing tests
markers =
    unit: Unit tests (single function)
    integration: Integration tests (API + database)
    e2e: End-to-end tests (full workflows)
    slow: Slow tests (may skip with -m "not slow")

# Coverage minimum
addopts = --cov=backend --cov-fail-under=80
```

---

### 4. **docs/CI_CD.md** (Create)

**Purpose:** Document the CI/CD pipeline

**Should cover:**
- [ ] GitHub Actions workflow (if using)
- [ ] When tests run (on PR, on merge, nightly)
- [ ] Deployment triggers
- [ ] Status badges
- [ ] Secrets management (API keys, etc.)

**Example:**
```markdown
## CI/CD Pipeline

### GitHub Actions Workflow
File: \`.github/workflows/test.yml\`

Triggers:
- On every push to main
- On every PR

Steps:
1. Checkout code
2. Set up Python & Node
3. Install dependencies
4. Run linting (\`ruff check\`)
5. Run tests (\`pytest\`)
6. Report coverage
7. (Optional) Deploy on success

### Status Badges
\`\`\`markdown
![Tests](https://github.com/Duly330AI/UNOC/actions/workflows/test.yml/badge.svg)
\`\`\`
```

---

### 5. **README_TESTING.md** (Create - optional, quick ref)

**Purpose:** One-page quick reference for testing

```markdown
## Quick Testing Reference

### Before Committing
\`\`\`bash
cd backend
ruff check .
pytest --cov=backend
\`\`\`

### Run Specific Test
\`\`\`bash
pytest backend/tests/test_provisioning.py::test_provision_device_success
\`\`\`

### View Coverage Report
\`\`\`bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
\`\`\`

### Common Issues
- **"ModuleNotFoundError"** → Run \`pip install -e .\`
- **"Database locked"** → Tests use in-memory SQLite, no conflicts
- **"Import failed"** → Check Python venv is activated
```

---

## PHASE 5 DELIVERABLES

✅ **docs/TESTING.md** - Complete testing guide (unit, integration, E2E)  
✅ **docs/QUALITY_GATES.md** - Linting, coverage, type checking standards  
✅ **docs/CI_CD.md** - Pipeline documentation  
✅ **pytest.ini** - Annotated with explanations  
✅ **README_TESTING.md** - Quick reference  

---

## PHASE 5 REVIEW CHECKLIST

- [ ] All test files are discoverable in docs
- [ ] Running tests locally is copy-paste-able
- [ ] Coverage minimum is realistic & enforced
- [ ] CI/CD pipeline is documented
- [ ] Quality gates are clear (what passes/fails)
- [ ] Pre-commit checklist included
- [ ] Examples for common test patterns
- [ ] Coverage reports are accessible (HTML, etc.)

---

---

# EXECUTION STRATEGY FOR PHASES 3, 4, 5

## Option A: Sequential
1. Execute Phase 3 fully (5 docs created/enhanced)
2. Review & confirm
3. Execute Phase 4 (5 docs created/enhanced)
4. Review & confirm
5. Execute Phase 5 (5 docs created)

**Pros:** Clear, structured, easier to review  
**Cons:** Longer total time (~6-8h)

## Option B: Parallel
1. Execute Phase 3, 4, and 5 simultaneously (3 Codex runs)
2. All complete ~4-5h
3. One review pass for all three

**Pros:** Faster overall  
**Cons:** Harder to review, potential confusion

## Option C: Recommended
Execute **Phase 3 first** (frontend is user-visible, stakeholder interest).  
Then execute **Phase 4 + 5 together** (deployment & quality are backend-focused).

---

# SUCCESS CRITERIA FOR ALL THREE PHASES

By end of Phases 3-5:
- ✅ All Vue 3 components documented
- ✅ Pinia state management patterns clear
- ✅ WebSocket integration fully explained
- ✅ Deployment is repeatable on any machine
- ✅ Operations runbook is comprehensive
- ✅ Tests are discoverable & runnable
- ✅ Coverage is measured & gates enforced
- ✅ CI/CD pipeline is transparent

**Total documentation files created:** 15+  
**Total documentation coverage:** ~95%  
**Audience satisfaction:** New dev can be productive in 1 day

---

# READY TO PROCEED?

**Choose your approach:**

**A)** Start Phase 3 (Frontend), then 4+5  
**B)** Run all three in parallel  
**C)** Skip to specific phase (which one?)

Copy the **relevant section** above and give to Codex for execution.

Example:
```
"Please execute PHASE 3 of UNOC documentation audit.
Focus on Frontend & UI documentation.
Create/update the 5 files listed in PHASE 3 FILES section.
Follow the Phase 3 review checklist.
Report in the format specified."
```

---

**You're now at 95% documentation completion! Just a few more hours.** 🚀
