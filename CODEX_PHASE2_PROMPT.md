# UNOC Documentation Audit - PHASE 2 Prompt
# Backend API & Services Documentation
# ============================================================================

## CONTEXT

You have successfully completed Phase 1 (README, ROADMAP, ARCHITECTURE, MASTER_ACTION_PLAN, Copilot Guidelines).

Now we move to **PHASE 2: Backend API & Services Documentation**

The backend is the "source of truth" for UNOC. It handles:
- Device provisioning with 14 device types
- Optical link validation (L1-L9 rules)
- Manual status overrides with reason tracking
- Real-time WebSocket event broadcasting
- Future: Traffic simulation & congestion detection

**Goal:** Document the backend services, APIs, and domain logic so developers can:
1. Extend provisioning or add new device types
2. Understand optical link rules and validation
3. Implement new features (e.g., traffic engine in Phase 4)
4. Fix bugs with confidence

---

## PHASE 2 FILES TO AUDIT & UPDATE

### 1. **docs/OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md**

**Current Status:** Exists from Phase 1.5  
**Action:** Review & validate

**Checks:**
- [ ] Explains 14 device types clearly
- [ ] Shows optical attributes (tx_power_dbm, sensitivity_min_dbm, insertion_loss_db)
- [ ] Documents L1-L9 link validation rules
- [ ] Includes code examples from `backend/services/provisioning_service.py`
- [ ] No dead links or outdated references
- [ ] Explains WHY each rule exists (business/network logic)

**If missing or incomplete, add:**
- Device type matrix: name → interfaces → optical attributes
- L1-L9 rules in table format with examples
- Provisioning flow diagram (text/ASCII)
- Error messages developers will encounter

---

### 2. **docs/01_domain_model.md** (Create if missing)

**Purpose:** Explain the core data model (Device, Interface, Link, Status)

**Should include:**
- [ ] Device schema with all fields (id, name, device_type, status, status_override, etc.)
- [ ] Interface schema (id, name, interface_type, status, device_id)
- [ ] Link schema (id, status, a_interface_id, b_interface_id, length_km, physical_medium_id, link_loss_db)
- [ ] Status enum (UP, DOWN, DEGRADED) with clear definitions
- [ ] Relationships & cascading (Device → Interfaces → Links)
- [ ] Code reference: `backend/models/core.py` with line numbers

**Add examples:**
```python
# Example: Create device with interfaces
device = Device(
    name="OLT-001",
    device_type=DeviceType.OLT,
    status=Status.DOWN,  # Initially down until validation
    tx_power_dbm=5.0,
    sensitivity_min_dbm=-30.0
)
# After provision_device(), device gets 8 pon0-pon7 interfaces
```

---

### 3. **docs/02_provisioning_flow.md** (Create if missing)

**Purpose:** Walk through device provisioning end-to-end

**Should explain:**
- [ ] When to use `POST /api/devices` vs. `POST /api/devices/provision`
- [ ] Provisioning logic: validation → device create → interface auto-gen → event emit
- [ ] Upstream dependency rules (why EDGE needs CORE, why ONT needs OLT, etc.)
- [ ] Error cases: invalid parent, upstream missing, name duplicate
- [ ] WebSocket events emitted (device:created, interface:created)
- [ ] Code flow: routes.py → ProvisioningService → models.py → emit_to_all()

**Include code snippet:**
```python
# From backend/api/routes.py - provision endpoint
@api_router.post("/devices/provision")
async def provision_device(request: ProvisionDeviceRequest, ...):
    service = ProvisioningService(session)
    device = await service.provision_device(
        name=request.name,
        device_type=request.device_type,
        validate_upstream=True  # ← Key: enforces dependency rules
    )
    # WebSocket broadcast happens inside provision_device
    return device
```

---

### 4. **docs/03_status_and_overrides.md** (Create if missing)

**Purpose:** Explain status field and manual overrides (Phase 3.2)

**Should cover:**
- [ ] Single `status` field design (why not multiple flags)
- [ ] Status enum: UP, DOWN, DEGRADED meanings
- [ ] `status_override` field: what, when, why
- [ ] `override_reason` field: free text for admin notes
- [ ] API endpoints: PATCH /devices/{id}/override, DELETE /devices/{id}/override
- [ ] WebSocket events: `device:override_changed`
- [ ] UI representation: override badges, manual control buttons

**Add example flow:**
```
User clicks "Force UP" in sidebar
  ↓
Frontend: PATCH /api/devices/{id}/override with { status_override: "UP", override_reason: "Testing" }
  ↓
Backend: device.status_override = "UP"; device.override_reason = "Testing"
  ↓
WebSocket: emit_to_all("device:override_changed", { id, status_override, override_reason })
  ↓
All clients: Update device card with 🔒 badge
```

---

### 5. **docs/04_link_validation.md** (Create if missing)

**Purpose:** Explain L1-L9 link validation rules

**Should document:**
- [ ] Complete L1-L9 rule matrix
  - L1: BACKBONE ↔ CORE
  - L2: CORE ↔ EDGE
  - L3: EDGE ↔ OLT (GPON)
  - L4: EDGE ↔ AON
  - L5: OLT ↔ ONT
  - L6: OLT ↔ BUSINESS_ONT
  - L7: AON ↔ CPE
  - L8: Passive inline (ODF, NVT, SPLITTER, HOP)
  - L9: Peer-to-peer redundancy

- [ ] Why each rule exists (network topology constraints)
- [ ] Error messages when rule violated
- [ ] Code reference: `backend/constants/link_rules.py` (or where link validation lives)
- [ ] Example: "Why can't you link ONT directly to AON_SWITCH?"

---

### 6. **docs/05_websocket_events.md** (Create if missing)

**Purpose:** Document all Socket.IO events backend emits

**Format: Event → Payload → When**

Examples:
```
EVENT: device:created
PAYLOAD: { id, name, device_type, status, x, y, ... }
WHEN: After POST /api/devices/provision succeeds

EVENT: interface:created
PAYLOAD: { id, name, interface_type, device_id, status }
WHEN: Auto-generated during provisioning

EVENT: device:override_changed
PAYLOAD: { id, status_override, override_reason }
WHEN: PATCH /devices/{id}/override succeeds

EVENT: link:created
PAYLOAD: { id, a_interface_id, b_interface_id, status, ... }
WHEN: POST /api/links succeeds
```

- [ ] List all events
- [ ] Show payload structure (JSON)
- [ ] When each is emitted (trigger)
- [ ] How frontend should react
- [ ] Code reference: `backend/main.py` - `emit_to_all()` calls

---

### 7. **docs/06_error_handling.md** (Create if missing)

**Purpose:** Document error codes and recovery strategies

**Should include:**
- [ ] HTTPException 400 - Invalid request (e.g., duplicate name, invalid device type)
- [ ] HTTPException 404 - Resource not found (e.g., device does not exist)
- [ ] HTTPException 422 - Validation error (from Pydantic)
- [ ] ProvisioningError - Custom provisioning failures with messages
- [ ] Error message templates developers will see
- [ ] How to test error cases (fixtures, examples)

**Example:**
```json
// Trying to create ONT without OLT upstream
{
  "detail": "Cannot provision ONT: No OLT exists for PON connection"
}
```

---

### 8. **backend/api/routes.py** (Audit & add docstrings)

**Current state:** Has endpoints but may lack comprehensive docstrings

**Check each endpoint:**
- [ ] GET /api/devices - list all devices
- [ ] GET /api/devices/{id} - get one device
- [ ] POST /api/devices - create device (basic)
- [ ] POST /api/devices/provision - create with provisioning logic
- [ ] PATCH /api/devices/{id} - update device
- [ ] DELETE /api/devices/{id} - delete device
- [ ] PATCH /api/devices/{id}/override - set override
- [ ] DELETE /api/devices/{id}/override - clear override
- [ ] GET /api/interfaces - list interfaces
- [ ] POST /api/links - create link
- [ ] DELETE /api/links/{id} - delete link
- [ ] ... (any others)

**For each endpoint add:**
```python
@api_router.post("/devices/provision")
async def provision_device(request: ProvisionDeviceRequest, ...):
    """
    Provision a device with automatic interface creation.
    
    Args:
        request: ProvisionDeviceRequest with name, device_type, optional parent_container_id
    
    Returns:
        ProvisionDeviceResponse with device and interfaces list
    
    Raises:
        HTTPException 400: If name already exists or upstream validation fails
        HTTPException 422: If request validation fails (Pydantic)
    
    Example:
        POST /api/devices/provision
        {
          "name": "OLT-001",
          "device_type": "OLT",
          "parent_container_id": 1,
          "validate_upstream": true
        }
        
        Response:
        {
          "id": 10,
          "device": { ... },
          "interfaces": [ ... ],
          "message": "Device provisioned successfully"
        }
    
    WebSocket Events Emitted:
        - device:created
        - interface:created (8 times for OLT)
    """
```

---

### 9. **backend/services/provisioning_service.py** (Audit & enhance)

**Current state:** Service exists, may need doc refinement

**Checks:**
- [ ] Class docstring explains the purpose
- [ ] `provision_device()` method is well-documented
- [ ] `_validate_upstream_dependency()` explains each rule
- [ ] `_create_default_interfaces()` shows device-type mappings
- [ ] Error handling clear (when ProvisioningError is raised)
- [ ] Code comments explain non-obvious logic

**If missing, add to class docstring:**
```python
class ProvisioningService:
    """
    Service for provisioning devices with validation, auto-interface generation.
    
    Design:
    - Validates upstream dependencies before creating device
    - Auto-generates interfaces based on device_type (e.g., OLT → 8 PON ports)
    - Emits WebSocket events for real-time UI sync
    
    Usage:
        service = ProvisioningService(session)
        device = await service.provision_device(
            name="OLT-001",
            device_type=DeviceType.OLT,
            validate_upstream=True
        )
    
    Error Handling:
        Raises ProvisioningError if:
        - name is not unique
        - upstream device types don't exist (if validate_upstream=True)
        - device_type is unsupported
    """
```

---

## PHASE 2 DELIVERABLES

After Phase 2, we should have:

✅ **docs/01_domain_model.md** - Clear data model explanation  
✅ **docs/02_provisioning_flow.md** - End-to-end provisioning walkthrough  
✅ **docs/03_status_and_overrides.md** - Status field & override logic  
✅ **docs/04_link_validation.md** - L1-L9 rules documented  
✅ **docs/05_websocket_events.md** - All WebSocket events cataloged  
✅ **docs/06_error_handling.md** - Error codes & recovery strategies  
✅ **OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md** - Updated & validated  
✅ **backend/api/routes.py** - All endpoints have docstrings  
✅ **backend/services/provisioning_service.py** - Methods well-documented  

---

## PHASE 2 REVIEW CHECKLIST

- [ ] All 7+ new docs exist and are complete
- [ ] Code examples are real (copied from repo, not pseudocode)
- [ ] Line numbers match current code (e.g., "see line 42 in routes.py")
- [ ] Error messages are actual strings developers will see
- [ ] WebSocket payloads match actual implementation
- [ ] All links between docs are valid
- [ ] Provisioning service logic is fully explained
- [ ] L1-L9 rules are clear with examples
- [ ] No contradictions with Phase 1 docs (ARCHITECTURE, ROADMAP)
- [ ] Prose is clear, terminology consistent, jargon explained

---

## KNOWN GAPS (From Phase 1 Codex Report)

**To fix in Phase 2:**
1. "3) Schedule the /api/devices/{id}/interfaces documentation gap for Phase 2 follow-up"
   - Need docs for GET /api/devices/{id}/interfaces endpoint (returning interface list)

2. Missing docs for:
   - MAC address allocation strategy (currently manual/unimplemented)
   - IPAM pool design (coming in future phase)
   - Optical path resolution algorithm (future: Phase 4 Traffic)

**Phase 2 can note these as "Phase 3+ scope" without blocking completion.**

---

## INTERACTION GUIDELINES

- **Code examples:** Copy from actual files, include file path and line range
- **Diagrams:** Use Markdown tables or ASCII art (no external images)
- **Prose style:** Technical but readable; explain "why" not just "what"
- **Audience:** Backend developers who need to extend or debug the system
- **References:** Link to specific files/functions in the repo

---

## SUCCESS CRITERIA FOR PHASE 2

1. **Completeness:** Every backend service and public API documented
2. **Accuracy:** All code examples are current and correct
3. **Clarity:** Developers can understand provisioning → status → overrides → links flow
4. **Traceability:** Each doc links to source code (file paths, line ranges)
5. **Consistency:** Terminology matches ARCHITECTURE.md and README.md
6. **Readability:** No jargon without explanation; prose scores >= 8/10

---

## READY TO START?

Execute Phase 2 following the file-by-file checks above.

**Report format:**
```
### File: docs/01_domain_model.md
- Status: ✅ CREATED / ⚠️ UPDATED / ❌ MISSING
- Issues found: (if any)
- Changes made: (summary)
- Code examples: (count & source)
- Links verified: (yes/no)

---
```

After Phase 2, we'll review and move to **Phase 3: Frontend & UI Documentation**.

---

**Let's build rock-solid backend documentation! 🚀**
