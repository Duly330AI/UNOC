# UNOC Documentation Audit & Cleanup - Codex Prompt
# ============================================================================
# This is the master prompt to give Codex for documentation cleanup
# Execute Phase by Phase, with review between phases
# ============================================================================

## CONTEXT

You are auditing and cleaning up documentation for **UNOC** - a FTTH (Fiber-to-the-Home) Network Emulator built with:
- **Backend:** FastAPI + PostgreSQL + WebSockets
- **Frontend:** Vue 3 + Vite
- **Current Phase:** 3.2 Complete (Status Override), Phase 4 (Traffic) incoming
- **Test Coverage:** 92+ tests in provisioning/optical, variable coverage overall
- **Git Repo:** https://github.com/Duly330AI/UNOC (just pushed Oct 24, 2025)

**Goal:** Systematically audit, update, and complete all documentation in 5 phases.

---

## PHASE 1: CORE DOCUMENTATION (START HERE)

### Files to Audit & Update

1. **README.md** - Main project overview
   - [ ] Check: Feature status (Provisioning implemented, Traffic planned)
   - [ ] Check: Architecture overview is current
   - [ ] Check: Quick start guide still works
   - [ ] Check: All links valid (no 404s)
   - [ ] Update: Tech stack section (FastAPI, Vue 3, PostgreSQL, WebSockets)
   - [ ] Update: Feature matrix (show Phase 3.2 complete, Phase 4 coming)
   - [ ] Ensure: Test count & coverage metrics current (was 92+ tests, coverage variable)

2. **ROADMAP.md** - Feature roadmap & implementation status
   - [ ] Check: Phase 1-3.2 marked ✅ COMPLETE
   - [ ] Check: Phase 4 (Traffic) scope documented
   - [ ] Check: Phase 5 (Production) placeholder exists
   - [ ] Update: Completion dates (Phase 3.2 was Oct 15, 2025)
   - [ ] Update: Dependencies between phases
   - [ ] Ensure: Estimated durations realistic
   - [ ] Add: Recent completions (Provisioning Service, Status Override, WebSockets)

3. **docs/ARCHITECTURE.md** (or create if missing)
   - [ ] Create/Update: System architecture diagram (ASCII or table)
   - [ ] Document: Component interactions (Frontend ↔ Backend ↔ Database)
   - [ ] Explain: Data flow (Provisioning → Interfaces → IPs → Status)
   - [ ] Show: Technology stack & why each choice (FastAPI for speed, Vue 3 for reactivity)
   - [ ] Include: Deployment architecture (Docker Compose setup)
   - [ ] Document: Key design decisions (Single status field, WebSocket events, etc.)

4. **docs/MASTER_ACTION_PLAN.md** (or MASTER_ACTION_PLAN_DONE.md)
   - [ ] Check: Reflects completed work (Phase 3.2 done)
   - [ ] Update: Next steps (Phase 4 Traffic Engine)
   - [ ] Document: Known issues & technical debt
   - [ ] Link: To relevant implementation files
   - [ ] Include: Recent architectural decisions

5. **.github/copilot-instructions.md** (or create)
   - [ ] Update: Current project context (FTTH Emulator, Phase 3.2 complete)
   - [ ] Document: Coding standards & conventions
   - [ ] Document: Git workflow (main branch, feature branches)
   - [ ] Include: Common patterns (Services, Models, API routes)
   - [ ] Add: Links to key architecture docs

### Phase 1 Deliverables

After Phase 1, we should have:
- ✅ Current project status visible in README
- ✅ Roadmap showing progress through Phase 3.2
- ✅ Architecture documented with diagrams/tables
- ✅ Clear action plan for Phase 4
- ✅ Copilot instructions updated

### Phase 1 Review Checklist

- [ ] README accurately reflects current project state
- [ ] ROADMAP shows realistic timeline
- [ ] ARCHITECTURE is clear & complete
- [ ] All links in docs are valid
- [ ] No outdated information remains
- [ ] Prose is clear, jargon explained

---

## PHASE 2: BACKEND API & SERVICES (After Phase 1 approval)

### Files to Audit & Update

1. **docs/OPTICAL_NETWORK_IMPLEMENTATION_SUMMARY.md**
   - Review: Completeness & accuracy
   - Ensure: Code examples match current implementation
   - Add: Link to provisioning_service.py

2. **docs/01_domain_model.md through 04_signal_budget_and_overrides.md**
   - Review: Each domain concept (Devices, Interfaces, Links, Optical)
   - Check: Examples & code snippets current
   - Ensure: Cross-references work
   - Add: Recent changes (Status Override, Provisioning)

3. **docs/11_traffic_engine_and_congestion.md**
   - Review: Traffic generation algorithm explained
   - Add: Traffic v2 engine documentation (tariff-based)
   - Document: Congestion detection & hysteresis

4. **backend/api/routes.py** (Add docstrings/inline docs)
   - Document: All /api/devices/* endpoints
   - Add: POST /devices/provision endpoint details
   - Include: Request/response schemas
   - Add: Error codes & handling

5. **backend/services/provisioning_service.py** (Review & document)
   - Ensure: Class docstrings complete
   - Document: provision_device() flow
   - Explain: Upstream dependency validation
   - Add: Interface creation logic

### Phase 2 Deliverables

- ✅ All API endpoints documented with examples
- ✅ Service layer architecture clear
- ✅ Provisioning flow explained end-to-end
- ✅ Domain models (Device, Interface, Link, Optical) documented
- ✅ Code examples validated & current

---

## PHASE 3: FRONTEND & UI DOCUMENTATION (After Phase 2 approval)

### Files to Audit & Update

1. **docs/05_realtime_and_ui_model.md**
   - Review: WebSocket integration documented
   - Update: UI component examples current
   - Add: State management patterns

2. **frontend/src/README.md** (Create if missing)
   - Document: Project structure
   - Explain: Build process (npm run build)
   - Add: Common development tasks

3. **frontend/src/components/README.md** (Create if missing)
   - Document: Component hierarchy
   - List: Available components & usage
   - Add: Props & events for key components
   - Include: Examples for common patterns

### Phase 3 Focus Areas

- DeviceSidebar component (new Interfaces tab, Optical tab)
- WebSocket event handling
- Real-time updates pattern
- State management (Vue 3 Composition API)

---

## PHASE 4: DEPLOYMENT & OPERATIONS (After Phase 3 approval)

### Files to Audit & Update

1. **docs/DEPLOYMENT.md**
   - Review: Local development setup still valid
   - Update: Environment variables list
   - Add: Docker Compose documentation
   - Include: Database initialization
   - Add: Troubleshooting section

2. **docker-compose.yml**
   - Review: Services configuration (PostgreSQL, Backend, Frontend)
   - Document: Environment variables
   - Add: Volume mounts explained

3. **ops/RUNBOOK.md** (Create if missing)
   - Common operations (restart, backup, logs)
   - Troubleshooting guide
   - Performance tuning tips
   - Monitoring setup

---

## PHASE 5: TESTS & QUALITY (After Phase 4 approval)

### Files to Audit & Update

1. **docs/TESTING.md** (Create if missing)
   - Document: Test structure (unit, integration, e2e)
   - Explain: Running tests (pytest)
   - Coverage reporting setup
   - CI/CD pipeline

2. **pytest.ini & test config**
   - Review: Test configuration current
   - Document: Test markers & categories

3. **Coverage Reports**
   - Generate: Current coverage stats
   - Document: Coverage targets per module
   - Identify: Low-coverage areas needing attention

---

## KNOWN ISSUES TO ADDRESS

### Documentation Gaps (Critical)
1. Missing docs for `/api/devices/{id}/interfaces` endpoint
2. Status propagation algorithm not explained
3. MAC allocation strategy not documented
4. IPAM pool design not explained
5. Link properties modal UI not documented
6. Optical path resolution algorithm not detailed

### Outdated Information (High)
1. README shows Phase 1 only (should show Phase 3.2 complete)
2. ROADMAP missing recent completions (Oct 15 updates)
3. Architecture diagram missing optical simulation details
4. API docs don't mention /devices/provision endpoint

### Missing Documentation (Medium)
1. API Error Codes Reference
2. Database Schema Documentation
3. Provisioning Flow Diagram
4. WebSocket Message Format Reference
5. Frontend Component Library
6. Performance Tuning Guide
7. Security Best Practices

---

## EXECUTION STRATEGY

### Per-Phase Process

1. **Audit:** Review all files in the phase
2. **Update:** Fix outdated info, add missing content
3. **Validate:** Check all code examples work
4. **Cross-Reference:** Ensure links between docs work
5. **Review:** Human review before moving to next phase

### Quality Checks

- ✅ No broken links
- ✅ Code examples match current implementation
- ✅ Terminology consistent across docs
- ✅ Prose is clear & jargon is explained
- ✅ All files have TOC & clear structure
- ✅ Recent changes (Oct 2025) reflected

### Output Format

For each phase, provide:
1. **Summary** of what was found & fixed
2. **Files Modified** with before/after highlights
3. **Issues Found** with severity & fix status
4. **Checklist** of what was verified
5. **Next Steps** recommendation

---

## TONE & AUDIENCE

- **Tone:** Technical, clear, direct (developers ≠ non-technical)
- **Audience:** Backend devs, frontend devs, DevOps engineers, architects
- **Code Examples:** Real, tested code from repo (not pseudocode)
- **Diagrams:** ASCII tables or markdown (not external images)
- **Cross-References:** Link relevant docs, code, GitHub issues

---

## SUCCESS CRITERIA

By end of all 5 phases:

- ✅ 95%+ documentation coverage
- ✅ 0 broken links in docs
- ✅ All code examples validated & current
- ✅ Terminology consistent throughout
- ✅ Recent changes (Oct 2025) reflected
- ✅ Readability score >= 8/10 (Flesch-Kincaid)
- ✅ Clear upgrade path for new developers
- ✅ Production deployment guide complete

---

## READY TO START?

**Start with PHASE 1** and follow the checklist above.

For each file:
1. State current status (✅ good / ⚠️ needs update / ❌ missing)
2. List specific issues found
3. Show updated content (or note: "No changes needed")
4. Provide reason for each change

After completing Phase 1, we'll review & decide whether to proceed to Phase 2.

---

**Let's make UNOC documentation excellent! 🚀**
