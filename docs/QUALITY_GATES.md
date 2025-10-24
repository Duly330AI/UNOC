# Quality Gates

**Last updated:** 24 Oct 2025  
**Audience:** Developers and reviewers ensuring the UNOC codebase meets quality bar before merge or deployment.

## Backend Requirements
- **Linting:** `ruff check backend`
- **Formatting (optional):** `ruff format backend`
- **Type hints:** Enforced via IDE (Pylance / MyPy pending). Avoid suppressing type errors in PRs.
- **Tests:** `pytest`
- **Coverage:** Aim for ≥80% (current enforcement manual; update `pytest.ini` `--cov-fail-under` when threshold is agreed).

## Frontend Requirements
- **Linting:** `npm run lint` (ESLint/Vue configuration to be added; treat warnings as blockers).
- **Type checking:** TypeScript in `--strict` mode (configure `tsconfig.json` accordingly).
- **Tests:** `npm run test` (planned Vitest suite).
- **Bundle check:** `npm run build` must succeed before release.

## Pull Request Checklist
Before requesting review:
1. `ruff check backend`
2. `pytest --cov=backend`
3. `npm run lint` (if frontend touched)
4. `npm run build` (if frontend touched)
5. Update relevant docs (README, architecture, runbooks)
6. Ensure coverage does not decrease (compare to current baseline)

Reviewers should verify:
- Tests and lint checks succeeded in CI.
- No disabled lint rules without justification.
- All new modules have tests or rationale for deferring.
- Documentation updated for user-facing changes.

## Pre-Commit Hook (Recommended)
Create `.pre-commit-config.yaml` (future task) with:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.3
    hooks:
      - id: ruff
      - id: ruff-format
```
Run `pre-commit install` to enforce linting locally.

## Coverage Targets
- Backend: maintain ≥80%; revisit after traffic engine work.
- Frontend: set initial goal once Vitest suite lands.
- Integration tests: ensure critical provisioning/override flows remain covered.

Track progress in `docs/TESTING.md` and update this file whenever gates change.
