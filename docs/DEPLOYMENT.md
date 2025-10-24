# Deployment Guide

**Last updated:** 24 Oct 2025  
**Audience:** DevOps / engineers deploying UNOC in local, staging, or production environments.

UNOC ships as a FastAPI backend with a Vue 3 frontend. This guide explains how to run the stack locally with Docker Compose and how to promote the same containers to production with environment-specific configuration.

## Prerequisites
| Tool | Version | Notes |
|------|---------|-------|
| Docker Desktop / Engine | 24+ | Includes Docker Compose v2. |
| Node.js | 20+ | Required only if you run the frontend dev server. |
| Python | 3.10+ | Optional when using Compose (backend runs in container). |
| Git | Latest | Clone the repository. |

## Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/Duly330AI/UNOC.git
   cd UNOC/unoc
   ```
2. Copy the environment template (create `.env` once Phase 4 `.env.example` exists):
   ```bash
   cp .env.example .env
   ```
3. Start backend + database:
   ```bash
   docker compose up -d
   ```
   - PostgreSQL: `localhost:5432`
   - FastAPI backend: `http://localhost:5001`
4. Start the frontend dev server in a second terminal:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. Visit `http://localhost:5173` and interact with the topology. The frontend proxies `/api` calls to the backend automatically (`frontend/vite.config.ts`).

### Services Started by Compose
| Service | Container | Purpose |
|---------|-----------|---------|
| postgres | `unoc-postgres` | Stores devices, interfaces, links, overrides. |
| backend | `unoc-backend` | FastAPI API + Socket.IO server. |

### Populating Data
On first run the backend seeds a demo topology if the database is empty (`backend/main.py:36-47`). To reset the seed, stop Compose and run:
```bash
docker compose down -v     # drops volumes, data erased
docker compose up -d
```

## Wiring `.env` into CI/CD and Deployment Pipelines

The Compose configuration now supports reading environment variables from a `.env` file. Copy the provided template:

```bash
cp .env.example .env
```

In local development this file is consumed by `docker compose` (we added `env_file: - .env` to the services). For pipeline/staging deployments, do not commit `.env` — instead map values into your CI secrets and inject them as environment variables during the workflow run. Example GitHub Actions template: `.github/workflows/deploy_staging.yml` shows how to map GitHub Secrets into job-level environment variables (e.g. `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`).

Example (high level):

```yaml
env:
   POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
   POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
   DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

When running `docker compose` on your staging/host machine, create `/opt/unoc/.env` from your secret store or copy from CI securely — avoid committing secrets to the repository.

## Automated Backups (Staging)

We provide a small optional backup pattern you can enable in staging. The `docker-compose.yml` contains a commented `db-backup` service which runs periodic `pg_dump` to a mounted `backups:` volume. To enable it:

1. Create a backups volume in `docker-compose.yml` (uncomment the `backups:` volume entry).
2. Uncomment the `db-backup` service block.
3. Ensure your `.env` contains `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.

Alternatively, run backups from the host or a scheduled job using the included script `scripts/backup_db.sh`:

```bash
# Run one-off backup to local folder
POSTGRES_HOST=localhost POSTGRES_USER=unoc POSTGRES_DB=unocdb POSTGRES_PASSWORD=unocpw ./scripts/backup_db.sh ./backups
```

Crontab example on a Linux host to run nightly at 02:15:

```cron
15 2 * * * /usr/bin/env POSTGRES_HOST=localhost POSTGRES_USER=unoc POSTGRES_DB=unocdb POSTGRES_PASSWORD="$SECRET_PW" /opt/unoc/scripts/backup_db.sh /var/backups/unoc
```

Place backups on durable storage (S3, NFS, or off-host archive) and test restore procedures regularly (see `ops/RUNBOOK.md`).

## Monitoring & Alerting (Staging)

Basic monitoring checklist to implement in staging:

- Export backend metrics (if instrumented) to Prometheus and add Grafana dashboards.
- Monitor PostgreSQL health (`pg_isready`) and disk usage.
- Alert on high CPU, memory, or WebSocket disconnect rates.
- Add synthetic tests that call `/api/health` and perform a sample provisioning flow; failing tests should raise an alert.

See `ops/RUNBOOK.md` for daily/weekly checklists and incident playbooks.

## Production Deployment
1. **Prepare environment variables** (`.env` or secret manager):
   - `DATABASE_URL` (e.g., `postgresql+asyncpg://unoc:strongpw@postgres:5432/unocdb`)
   - `UNOC_PORT` (default `5001`)
   - `UNOC_SHUTDOWN_TOKEN` (optional token for graceful shutdown endpoints)
   - Any feature toggles used by upcoming traffic modules.
2. **Build backend image** (from repository root):
   ```bash
   docker build -t ghcr.io/your-org/unoc-backend:latest .
   ```
3. **Build frontend bundle** and serve via nginx or another static host:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   Deploy the contents of `frontend/dist` to an object store, CDN, or nginx container (for example, mount to `/usr/share/nginx/html`).
4. **Provision infrastructure**:
   - PostgreSQL: managed service or container.
   - Backend: run container with `DATABASE_URL` pointing at managed database.
   - Frontend: serve static bundle, configure reverse proxy to point `/api` and `/socket.io` to backend.
5. **Configure TLS**: terminate HTTPS at nginx/ingress controller using Let's Encrypt or your certificate authority.
6. **Set up monitoring**:
   - Use container logs (stdout) for backend.
   - Track PostgreSQL metrics (connections, storage).
   - Add custom probes using `/health` endpoint (`GET http://backend-host:5001/health`).

### Example Production `docker-compose.prod.yml`
```yaml
services:
  backend:
    image: ghcr.io/your-org/unoc-backend:latest
    environment:
      DATABASE_URL: ${DATABASE_URL}
      UNOC_PORT: 5001
    ports:
      - "5001:5001"
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```
Run with `docker compose -f docker-compose.prod.yml --env-file prod.env up -d`.

## Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://unoc:unocpw@postgres:5432/unocdb` | SQLModel connection string. Update credentials in production. |
| `UNOC_PORT` | `5001` | Backend listen port. |
| `UNOC_SHUTDOWN_TOKEN` | empty | Optional token for future admin endpoints. |
| `USE_GO_TRAFFIC` | `0` | Placeholder for future traffic engine toggle. |
| `UNOC_DEV_FEATURES` | `1` | Enables seed/demo logic; set to `0` in prod when implementing. |

## Database Administration
| Task | Command |
|------|---------|
| Open psql shell | `docker exec -it unoc-postgres psql -U unoc -d unocdb` |
| Dump database | `docker exec unoc-postgres pg_dump -U unoc unocdb > backup.sql` |
| Restore dump | `docker exec -i unoc-postgres psql -U unoc unocdb < backup.sql` |
| List tables | `\dt` inside psql shell |

## Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| `psycopg` connection refused | PostgreSQL container not healthy | Run `docker compose ps`; inspect logs `docker logs unoc-postgres`. |
| Backend exits immediately | Bad `DATABASE_URL` | Confirm env var matches running database; verify credentials. |
| `Port already in use` | Existing process on port 5001/5432 | Stop conflicting service or change `ports` in Compose. |
| Frontend cannot reach API | Proxy mismatch | Ensure Vite dev server (`5173`) or prod reverse proxy forwards `/api` and `/socket.io` to backend. |
| Seed not applied | Database already populated | Drop volume (`docker compose down -v`) or run `POST /api/seed` if a management endpoint is added. |

## Deployment Checklist
- [ ] Secrets managed via environment variables or secret store (no defaults in production).
- [ ] Database backups scheduled (e.g., cron job using `pg_dump`).
- [ ] Monitoring configured (logs, metrics, uptime checks).
- [ ] Frontend bundle deployed behind HTTPS.
- [ ] Health endpoint monitored.
- [ ] Restore procedure tested on staging.

For day-to-day operations and incident response, follow `docs/OPERATIONS.md` and `ops/RUNBOOK.md`.
