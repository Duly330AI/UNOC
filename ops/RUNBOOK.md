# UNOC Operations Runbook

**Last updated:** 24 Oct 2025  
**Maintainers:** Core engineering team (update contact list quarterly)

This runbook captures day-to-day operational duties, escalation paths, and recovery procedures for the UNOC stack.

## Contact Matrix
| Role | Primary | Backup |
|------|---------|--------|
| Backend on-call | @backend-oncall | @backend-backup |
| Frontend on-call | @frontend-oncall | @frontend-backup |
| Database administrator | @dba-oncall | @dba-backup |

Update aliases in the on-call rota each sprint.

## Daily Checklist
- [ ] Review `docker logs --tail 100 unoc-backend` for errors.
- [ ] Check `/health` endpoint (curl or monitoring alert review).
- [ ] Confirm WebSocket indicator is green in the UI.
- [ ] Ensure overnight backups completed (check backup directory timestamp).

## Weekly Checklist
- [ ] Run synthetic provisioning test (POST `/api/devices/provision`) against staging.
- [ ] Restore most recent backup to staging to validate recovery procedure.
- [ ] Prune Docker images/volumes older than two weeks (`docker system prune -f`).
- [ ] Review database size (`SELECT pg_size_pretty(pg_database_size('unocdb'));`).

## Monthly Checklist
- [ ] Capacity review: CPU, memory, disk, network metrics.
- [ ] Security audit: update base images, regenerate secrets if required.
- [ ] Incident drill: simulate backend outage and verify alerting/escalation works.
- [ ] Update this runbook with any process changes.

## Incident Response Playbooks
### Backend API Down
1. Acknowledge alert (PagerDuty/Slack).
2. Check logs: `docker logs unoc-backend`.
3. If configuration issue, update `.env` and redeploy container.
4. If dependency issue (database offline), follow **Database outage** playbook.
5. Post-mortem required for outages longer than 15 minutes.

### Database Outage
1. Verify container status: `docker ps | grep unoc-postgres`.
2. Attempt restart: `docker compose restart postgres`.
3. If volume corruption suspected, restore from latest backup:
   ```bash
   docker compose stop backend
   cat backups/unoc_latest.sql | docker exec -i unoc-postgres psql -U unoc unocdb
   docker compose start backend
   ```
4. Document recovery action in incident log.

### WebSocket Flood / Performance Degradation
1. Check backend CPU usage (`docker stats unoc-backend`).
2. Temporarily disable traffic-intensive features (toggle env flags, redeploy).
3. Inspect recent commits for traffic engine changes; roll back if needed.
4. Schedule follow-up to implement batching/throttling (see Phase 4 design notes).

### Frontend UI Outage
1. Verify static assets served correctly (check CDN or nginx logs).
2. Ensure reverse proxy forwards `/api` and `/socket.io`.
3. Redeploy `frontend/dist` artefact if corrupted.

## Backup & Restore
- Backups stored under `backups/` on the host runner by cron job (`pg_dump` nightly).
- Offsite copies uploaded to secure storage (S3 bucket `s3://unoc-backups/`).
- Verify checksum after upload (MD5 or SHA256).

## Monitoring & Alerting
- **Health endpoint**: 1-minute interval HTTP check.
- **Database metrics**: track connections, replication lag (if introduced), disk.
- **Socket.IO**: monitor connection counts; set threshold alerts for sudden drops.
- **Logs**: forward stdout/stderr to log aggregation. Alert on patterns (e.g., "ProvisioningError").

## Change Management
- Deployments must pass automated tests (Phase 5 docs) before promotion.
- Use feature flags (`UNOC_DEV_FEATURES`, `USE_GO_TRAFFIC`) for gradual roll-outs.
- Record changes in the change log (link to internal wiki ticket).

## Escalation
1. If incident unresolved after 15 minutes, escalate to engineering manager.
2. If data integrity compromised, involve DBA immediately and turn off write operations until resolved.
3. For security incidents, notify security team and follow corporate incident response policy.

Keep this runbook in sync with `docs/OPERATIONS.md`; use this file for operational cadence and escalation details, while `docs/OPERATIONS.md` remains the quick command reference.
