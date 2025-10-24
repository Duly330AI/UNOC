## Quick Testing Reference

### Backend
```bash
ruff check backend              # Lint
pytest --cov=backend            # Tests + coverage
pytest backend/tests/test_provisioning_service.py::test_duplicate_name_rejected
pytest --cov=backend --cov-report=html && open htmlcov/index.html
```

### Frontend (planned)
```bash
cd frontend
npm run lint
npm run test
npm run build
```

### Common Issues
- `ModuleNotFoundError`: run `pip install -r requirements.txt` (and activate venv).
- `Database locked`: ensure no external process is using the SQLite file; tests use in-memory DB.
- `Coverage dropped`: inspect `htmlcov/index.html` and add missing tests.
- `npm ERR!`: delete `frontend/node_modules` and rerun `npm install`.
