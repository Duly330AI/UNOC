# Testing Guide

**Last updated:** 24 Oct 2025  
**Audience:** Developers and QA engineers working on UNOC.

## Test Suite Overview
```
backend/tests/
├─ conftest.py                 # Shared fixtures (in-memory SQLite engine, async session)
├─ test_api_responses.py       # Verifies REST responses and schemas
├─ test_device_types.py        # Ensures device catalog & attributes behave as expected
├─ test_link_optical.py        # Optical loss calculations and validations
├─ test_link_rules.py          # L1-L9 link validation matrix
├─ test_provision_api.py       # Provisioning endpoint end-to-end flow
├─ test_provisioning_dependency.py # Upstream dependency rules
├─ test_provisioning_service.py    # ProvisioningService internals
└─ test_status_override.py     # Manual override API behaviour
```

- All tests run against an in-memory SQLite database configured in `backend/tests/conftest.py`.
- Async endpoints use `pytest.mark.asyncio` to execute with the event loop.
- As of Oct 2025 the frontend relies on manual smoke testing; Vitest scaffolding will follow the Pinia migration (Phase 6 backlog).

## Running Tests
```bash
# From repository root
pytest                 # Run entire suite (async + integration)

# Verbose output, short trace (default from pytest.ini)
pytest -vv

# Run specific file
pytest backend/tests/test_provisioning_service.py

# Run single test
pytest backend/tests/test_provisioning_service.py::test_duplicate_name_rejected

# Skip slow tests (future markers)
pytest -m "not slow"
```

### Coverage
```bash
pytest --cov=backend --cov-report=term-missing
pytest --cov=backend --cov-report=html   # Generates htmlcov/index.html
```
Open `htmlcov/index.html` in your browser to inspect per-file coverage. Update the `--cov-fail-under` threshold in `pytest.ini` when the team agrees on a minimum target (currently manual enforcement).

## Fixture Notes
- `conftest.py` exposes `async_session` and overrides `get_session` dependency for FastAPI so tests operate against SQLite memory (`backend/tests/conftest.py:20-90`).
- Use `client` fixture (FastAPI TestClient) for synchronous endpoint testing inside async loops.
- For new fixtures, declare them in `conftest.py` to keep reuse high.

## Frontend Testing (Roadmap)
- Planned tool: **Vitest** with Vue Test Utils.
- Test location: `frontend/src/__tests__/`.
- Commands (once wired):
  ```bash
  npm run test
  npm run test:coverage
  ```
- Track backlog items in `docs/MASTER_ACTION_PLAN.md` to implement component-level tests after Pinia stores land.

## When to Run Tests
| Scenario | Command |
|----------|---------|
| Before commit | `pytest --cov=backend` |
| Before opening PR | `ruff check backend` + `pytest --cov` + (future) `npm run lint` |
| Before deployment | Full suite on CI (see `docs/CI_CD.md`) |

## Adding New Tests
1. Place backend tests under `backend/tests/test_<feature>.py`.
2. Use descriptive function names (`test_<case>_<expected>`).
3. Prefer fixtures for reusable setup; keep hard-coded IDs minimal.
4. For new marker categories (e.g., `@pytest.mark.integration`), update `pytest.ini` so markers are recognized.

## Common Issues
| Symptom | Resolution |
|---------|------------|
| `ModuleNotFoundError` | Ensure virtualenv is active; run `pip install -e .` or `pip install -r requirements.txt`. |
| `sqlite3.OperationalError: database is locked` | Tests use in-memory DB; ensure no long-running blocking operations or convert to transactional fixtures. |
| `RuntimeError: Event loop is closed` | Use `pytest.mark.asyncio` on async tests; avoid nested loops. |
| Coverage below threshold | Inspect `htmlcov/index.html`, write missing unit tests, raise `--cov-fail-under` once coverage improves. |

## References
- `pytest.ini` – global configuration and markers.
- `docs/QUALITY_GATES.md` – linting, coverage, and pre-commit requirements.
- `docs/CI_CD.md` – pipeline running the commands above.
