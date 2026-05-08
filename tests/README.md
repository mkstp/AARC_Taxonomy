# Tests

Language: Python 3.11+
Test runner: `pytest`

## Running Tests

```bash
# Full suite
pytest tests/

# By category
pytest tests/unit/
pytest tests/validation/
pytest tests/deliverables/
pytest tests/integration/

# Single file
pytest tests/unit/test_window_extractor.py

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Structure

```
tests/
├── manifest.json          — traceability map (VCs, DELs, MODs → test files)
├── conftest.py            — shared fixtures
├── validation/            — tests derived from VC-NNN conditions
├── deliverables/          — tests verifying DEL-NNN outputs exist and function
├── unit/                  — module-level tests (one file per MOD-NNN)
└── integration/           — cross-module pipeline tests
```

## Manual Checklist

VC-02 (practitioner review) cannot be automated. See `manifest.json` → `manual_checklist` for steps.

## Notes

- Tests that make live API calls (Anthropic, OpenAI) are skipped by default. Set `RUN_LIVE_API_TESTS=1` to enable.
- Reward model tests require a GPU or will be slow on CPU; mark with `@pytest.mark.slow` and skip with `pytest -m "not slow"`.
