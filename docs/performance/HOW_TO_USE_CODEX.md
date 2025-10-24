# How to Use Codex for Performance Audit

This guide explains how to leverage the VS Code Codex extension to conduct a comprehensive performance audit of the UNOC project.

---

## Prerequisites

1. **VS Code with Codex Extension installed**
2. **UNOC project open in VS Code** (`c:\noc_project\UNOC\unoc`)
3. **Performance audit config created:** `~/.codex/performance_audit_config.toml`

---

## Step 1: Prepare Baseline Profiling Data (Optional but Recommended)

Before invoking Codex, gather baseline performance data to give it concrete numbers to analyze:

### Backend Profiling

```powershell
# From project root (c:\noc_project\UNOC\unoc)
cd c:\noc_project\UNOC\unoc

# Run tests with duration reporting
python -m pytest --durations=10 > backend/profiling/test_durations.txt

# Profile backend startup (if needed)
python -m cProfile -o backend/profiling/backend.prof run.py

# Check slow database queries (if database is running)
# Connect to PostgreSQL and run:
# SELECT query, calls, total_exec_time, mean_exec_time
# FROM pg_stat_statements
# ORDER BY total_exec_time DESC LIMIT 20;
```

### Frontend Profiling

```powershell
cd unoc-frontend-v2

# Build and generate bundle analysis
npm run build -- --report

# Use Chrome DevTools:
# 1. Open http://localhost:5173 in Chrome
# 2. Open DevTools → Performance tab
# 3. Record 10-20 seconds of interaction (click around, update devices, etc.)
# 4. Save profile as frontend/profiling/chrome_performance.json
```

### Database Profiling

```sql
-- In psql or pgAdmin:
-- Enable slow query logging
ALTER DATABASE unocdb SET log_min_duration_statement = 100;

-- Check for missing indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE tablename IN ('devices', 'interfaces', 'links')
ORDER BY tablename, indexname;

-- Analyze a slow query
EXPLAIN (ANALYZE, BUFFERS)
SELECT d.*, i.*
FROM devices d
LEFT JOIN interfaces i ON d.id = i.device_id
LIMIT 100;
```

---

## Step 2: Invoke Codex with Performance Audit Config

### Method A: Direct Prompt in VS Code

1. Open VS Code in the UNOC project root
2. Open Codex chat panel (Ctrl+Shift+I or Cmd+Shift+I)
3. Type the following prompt:

```
Use the performance_audit_config.toml to conduct a full performance audit of the UNOC project. 

Analyze backend (Python), frontend (Vue/TS), database queries, and WebSocket communication.

Populate the template files in docs/performance/ with your findings:
- 01_BACKEND_PERFORMANCE.md
- 02_FRONTEND_PERFORMANCE.md
- 03_REALTIME_PERFORMANCE.md
- 04_MEMORY_RESOURCES.md
- 05_RECOMMENDATIONS.md
- FINAL_REPORT.md

For each issue found:
1. Provide file path and line number
2. Include code snippet showing the problem
3. Suggest a specific fix with code example
4. Estimate effort (hours) and impact (% improvement)

Prioritize findings by severity (Critical > High > Medium > Low) and identify at least 10 "quick wins" (< 1 hour effort, high impact).

If you need profiling data that I haven't provided, tell me what command to run.
```

### Method B: Phase-by-Phase Approach

If Codex response is too long or times out, run each phase separately:

**Phase 1: Backend**
```
Using performance_audit_config.toml, analyze Phase 1 (backend performance). Focus on:
- backend/api/routes.py (API endpoints)
- backend/services/provisioning_service.py
- backend/db.py (database sessions)
- backend/models/core.py (SQLModel relationships)

Look for:
- N+1 query problems
- Missing database indexes
- Synchronous operations in async endpoints
- Slow provisioning logic

Populate docs/performance/01_BACKEND_PERFORMANCE.md with findings.
```

**Phase 2: Frontend**
```
Using performance_audit_config.toml, analyze Phase 2 (frontend performance). Focus on:
- unoc-frontend-v2/src/components/*.vue
- unoc-frontend-v2/src/stores/*.ts (Pinia)
- Cytoscape rendering

Look for:
- Unnecessary re-renders
- Missing v-memo optimizations
- Large bundle size
- Memory leaks

Populate docs/performance/02_FRONTEND_PERFORMANCE.md with findings.
```

**Phase 3: WebSocket**
```
Using performance_audit_config.toml, analyze Phase 3 (WebSocket/real-time). Focus on:
- backend/main.py (Socket.IO setup)
- backend/api/routes.py (emit_to_all calls)

Look for:
- Broadcast overhead
- Large message payloads
- Missing debouncing

Populate docs/performance/03_REALTIME_PERFORMANCE.md with findings.
```

**Phase 4: Memory**
```
Using performance_audit_config.toml, analyze Phase 4 (memory and resources). Focus on:
- Unreleased database sessions
- Vue component lifecycle issues
- Growing memory over time

Populate docs/performance/04_MEMORY_RESOURCES.md with findings.
```

**Phase 5: Recommendations**
```
Using performance_audit_config.toml, synthesize all findings from phases 1-4.

Generate:
- Top 10 quick wins (< 1 hour, high impact)
- Implementation roadmap (Week 1, Week 2, Month 1, Quarter)
- Monitoring recommendations

Populate docs/performance/05_RECOMMENDATIONS.md and FINAL_REPORT.md.
```

---

## Step 3: Review Codex Output

After Codex completes each phase:

1. **Review the generated markdown files** in `docs/performance/`
2. **Validate findings** — check if code locations are accurate
3. **Add your own notes** — Codex may miss context-specific issues
4. **Prioritize with your team** — not all recommendations may apply

---

## Step 4: Implement Quick Wins

Start with the quick wins from `05_RECOMMENDATIONS.md`:

1. Pick top 3 quick wins with highest impact
2. Implement each fix
3. Run profiling again to measure improvement
4. Document actual impact in the report

Example workflow:
```powershell
# Before fix
pytest --durations=10 > before.txt

# Apply fix (e.g., add database index)
# ...

# After fix
pytest --durations=10 > after.txt

# Compare
diff before.txt after.txt
```

---

## Step 5: Measure Improvement

After implementing fixes, re-run profiling to validate:

### Backend
```powershell
python -m pytest --durations=10
python -m pytest --cov=backend --cov-report=term-missing
```

### Frontend
```powershell
cd unoc-frontend-v2
npm run build
# Run Lighthouse audit in Chrome DevTools
```

### Database
```sql
-- Re-run slow query with EXPLAIN ANALYZE
-- Compare execution time before/after index
```

Update the report files with actual measured improvements.

---

## Step 6: Set Up Monitoring (Optional)

Follow recommendations in `FINAL_REPORT.md` to set up:

1. **Prometheus + Grafana** for metrics
2. **Sentry** for error tracking and performance monitoring
3. **Lighthouse CI** for continuous frontend audits

---

## Tips for Working with Codex

### Do:
- ✅ Provide specific file paths when possible
- ✅ Ask Codex to focus on one area at a time if responses are too long
- ✅ Request code snippets for every finding
- ✅ Ask for effort estimates and impact predictions
- ✅ Validate Codex findings with actual profiling data

### Don't:
- ❌ Accept all recommendations blindly — validate with your team
- ❌ Skip the profiling step — Codex needs data to be accurate
- ❌ Implement all fixes at once — measure incrementally
- ❌ Forget to commit changes after each fix

---

## Troubleshooting

**Problem:** Codex times out or gives incomplete responses  
**Solution:** Break down into smaller phases (use Method B above)

**Problem:** Codex suggests fixes that don't apply  
**Solution:** Provide more context in your prompt (e.g., "We use SQLModel, not raw SQLAlchemy")

**Problem:** Can't verify Codex findings  
**Solution:** Run the profiling commands in the config to get concrete data

**Problem:** Codex output is too generic  
**Solution:** Provide file paths and profiling data in your prompt

---

## Example Full Workflow

```powershell
# 1. Gather baseline data
cd c:\noc_project\UNOC\unoc
pytest --durations=10 > backend/profiling/baseline_durations.txt
python -m cProfile -o backend/profiling/baseline.prof run.py

# 2. Open VS Code and invoke Codex
# (Use prompt from Step 2 above)

# 3. Review generated reports in docs/performance/

# 4. Implement top 3 quick wins
# Example: Add database index
psql -U unoc -d unocdb -c "CREATE INDEX idx_interfaces_device_id ON interfaces(device_id);"

# 5. Measure improvement
pytest --durations=10 > backend/profiling/after_index.txt
diff backend/profiling/baseline_durations.txt backend/profiling/after_index.txt

# 6. Update report with actual results
# Edit docs/performance/01_BACKEND_PERFORMANCE.md
# Add measured improvement percentage

# 7. Commit changes
git add docs/performance/
git commit -m "perf: implement quick wins from Codex audit (add DB index, optimize query)"
git push
```

---

## Next Steps

1. ✅ Copy `performance_audit_config.toml` to `~/.codex/`
2. ⏳ Run baseline profiling (Step 1)
3. ⏳ Invoke Codex (Step 2)
4. ⏳ Review generated reports (Step 3)
5. ⏳ Implement quick wins (Step 4)
6. ⏳ Measure and document improvements (Step 5)
7. ⏳ Set up monitoring (Step 6)

---

**Questions?** Add them to the performance report and ask Codex for clarification.

**Found a bottleneck Codex missed?** Add it manually to the appropriate phase report.

**Need help with a specific optimization?** Ask Codex: "How do I optimize [specific issue] in [file path]?"
