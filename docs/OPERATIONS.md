# Operations Runbook (Quick Reference)

**Last updated:** 24 Oct 2025  
**Audience:** Operators responsible for keeping UNOC healthy in staging/production.

This document covers routine tasks: health checks, restarts, logs, backups, and emergency procedures.

## Health Checks
| Check | Command | Expected |
|-------|---------|----------|
| Backend health | `curl http://localhost:5001/health` | `{"status":"healthy","service":"unoc-backend","version":"2.0.0"}` |
| API list devices | `curl http://localhost:5001/api/devices` | JSON array of devices (HTTP 200). |
| Database connectivity | `docker exec -it unoc-postgres psql -U unoc -d unocdb -c "SELECT COUNT(*) FROM devices;"` | Row count returned. |
| WebSocket status | Inspect UI header indicator (green for live) or tail backend logs for `Client connected`. |

Automate these checks via cron or monitoring agents.

## Restart Procedures
| Scope | Command |
|-------|---------|
| Restart backend only | `docker compose restart backend` |
| Restart database | `docker compose restart postgres` |
| Full stack recycle | `docker compose down && docker compose up -d` |

After restart, re-run health checks and confirm the UI reconnects.

## Viewing Logs
```bash
# Backend (FastAPI + Socket.IO)
docker logs -f unoc-backend

# PostgreSQL
docker logs -f unoc-postgres
```

For production, pipe logs into a centralized system (CloudWatch, ELK, etc.).

## Database Maintenance
### Backup
```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec unoc-postgres pg_dump -U unoc unocdb > backups/unoc_${TIMESTAMP}.sql
```
Store backups securely (encrypt and copy off-host).

### Restore
```bash
cat backups/unoc_YYYYMMDD_HHMMSS.sql | docker exec -i unoc-postgres psql -U unoc unocdb
```
Ensure the backend is stopped before restoring to avoid inconsistent reads (`docker compose stop backend`).

## Data Operations
- **Clear demo data**: `docker compose down -v` wipes volumes; re-run `docker compose up -d` to reseed.
- **Programmatic provisioning**: use `POST /api/devices/provision` (see `docs/02_provisioning_flow.md`). Scripts can run inside a maintenance container with access to the API.
- **Manual overrides**: `PATCH /api/devices/{id}/override` and `DELETE /api/devices/{id}/override` (see `docs/03_status_and_overrides.md`).

## Performance Tuning
- Monitor PostgreSQL resource usage (CPU, memory, storage). Scale storage or move to managed DB if usage grows.
- Enable SQL logging by setting `DATABASE_URL` parameter `?echo=true` temporarily or use `pg_stat_statements`.
- Add caching / connection pooling (e.g., pgbouncer) when concurrent connections approach PostgreSQL limits.
- For heavy traffic simulations (Phase 4+) consider offloading to GO services (future `USE_GO_TRAFFIC` flag).

## Incident Response
| Incident | Response |
|----------|----------|
| Database unavailable | Check container status (`docker ps`), restart postgres service, restore from latest backup if required. |
| Backend crash loop | `docker logs unoc-backend` to identify stack trace (common causes: invalid env vars, migration mismatch). Fix config and redeploy. |
| WebSocket storm | Temporarily disable offending feature, restart backend, throttle event emission (see planned traffic batching). |
| UI not loading | Verify `frontend/dist` deployment or Vite dev server; ensure reverse proxy forwards `/api` and `/socket.io`. |

Escalate issues by attaching logs, steps taken, and timestamped health check outputs. Keep the latest contact list in `ops/RUNBOOK.md`.

## Scheduled Tasks
| Frequency | Task |
|-----------|------|
| Daily | Review backend logs, confirm health endpoint. |
| Weekly | Verify backups restore on staging, prune old Docker images/volumes. |
| Monthly | Review capacity (DB size, CPU), evaluate scaling plan, test disaster recovery. |

## Useful References
- `docs/DEPLOYMENT.md` - Full deployment steps and environment variable documentation.
- `docs/10_ui_patterns_and_examples.md` - UI operations (overrides, tab extensions).
- `ops/RUNBOOK.md` - Long-form operations guide with escalation paths (to be maintained by on-call rotation).
