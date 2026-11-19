# Contributing

Thanks for considering a contribution.

## Development setup
```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Before opening a pull request
```bash
ruff check .
ruff format --check .
python -m compileall -q platform_api url_shortener tests
pytest -q
```

You may run `ruff format .` to apply consistent formatting before committing.\n\n## Pull request expectations
- Keep changes focused and explain the problem being solved.
- Add or update tests for behavior changes.
- Update README or `docs/` when setup, APIs, architecture or operational behavior changes.
- Never commit credentials, `.env` files, local databases, customer data or generated secrets.
- Do not add production permissions or deployment automation without explicit review.
