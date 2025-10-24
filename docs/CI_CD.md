# CI/CD Pipeline

**Last updated:** 24 Oct 2025  
**Goal:** Describe how UNOC code is validated and deployed automatically.

## Current Status (Oct 2025)
- GitHub Actions workflow planned but not yet committed.
- CI should run on every pull request and push to `main`.
- This document will guide initial workflow and future enhancements.

## Proposed GitHub Actions Workflow
Create `.github/workflows/test.yml` with the following steps:
```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: unoc
          POSTGRES_PASSWORD: unocpw
          POSTGRES_DB: unocdb
        ports: ['5432:5432']
        options: >-
          --health-cmd="pg_isready -U unoc"
          --health-interval=5s
          --health-timeout=5s
          --health-retries=5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install backend deps
        run: pip install -r requirements.txt
      - name: Install frontend deps
        run: |
          cd frontend
          npm ci
      - name: Lint backend
        run: ruff check backend
      - name: Run backend tests
        env:
          DATABASE_URL: postgresql+asyncpg://unoc:unocpw@localhost:5432/unocdb
        run: pytest --cov=backend --cov-report=term-missing
      - name: Build frontend
        run: |
          cd frontend
          npm run build
      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: htmlcov
```

Add status badge to `README.md` once workflow exists:
```markdown
![Tests](https://github.com/Duly330AI/UNOC/actions/workflows/test.yml/badge.svg)
```

## Deployment Automation (Future)
- Tag releases with `vX.Y.Z`, trigger build and push of Docker images to container registry (GitHub Container Registry or Docker Hub).
- Publish frontend `dist/` artefacts to CDN or object storage (S3).
- Use environments (`staging`, `production`) with manual approvals.

## Secrets Management
- Store secrets (`DATABASE_URL`, registry credentials) in GitHub Action secrets.
- Avoid committing `.env` with real creds; only `.env.example` is tracked.

## Monitoring Workflow Health
- Enable branch protection requiring workflow success before merge.
- Configure Slack/Teams notifications for failed runs.

## Next Steps
1. Commit `test.yml` using the template above.
2. Set coverage thresholds in workflow when backend reaches agreed target.
3. Create deployment workflow (`deploy.yml`) that runs on tags/releases.
4. Update this document as pipelines evolve (include diagrams if multiple stages are added).
