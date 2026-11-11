# Development and validation

## Version sources

- Python 3.14 is the project's target runtime. [`.python-version`](../.python-version) selects it for Render, and CI is configured to use Python 3.14 in [`.github/workflows/django.yml`](../.github/workflows/django.yml).
- Python package versions are pinned in [`requirements.txt`](../requirements.txt); Django is 6.1.3.
- TypeScript is declared as `^5.8.3` in [`package.json`](../package.json) and locked to 5.8.3 in [`package-lock.json`](../package-lock.json). The project does not pin a Node version.

Use the manifests as the source of truth rather than copying version numbers into application code.
For a repeatable checklist and lessons from the Python 3.14/Django 6 upgrade, see the [Python and Django upgrade guide](upgrading-python-django.md).

## Typical local commands

Configure database and Redis variables for the selected settings branch before starting Django. This project uses `python3.14` in the supported environment; if your shell only exposes `python3`, use `python3.14` explicitly for the venv and Django commands. Then:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm ci
npm run build
python manage.py migrate
python manage.py runserver
```

Run the backend tests with:

```bash
python manage.py test
```

When the environment does not provide a `python` shim, use the explicit interpreter command instead:

```bash
python3.14 manage.py test
```

Build the browser code with `npm run build`; `npm run watch` runs the TypeScript compiler in watch mode. The build writes to `static/js/`, which is currently tracked. Make source edits in `src/` and review any generated output changes.

## Settings and environment variables

Read [`mywebsite/settings.py`](../mywebsite/settings.py) before changing deployment or local setup:

- `DJANGO_ENV` only controls `.env` loading; `ENVIRONMENT` selects the database and Redis configuration.
- `ENVIRONMENT=development` expects `DATABASE_URL`; other values use the individual `DB_*` fields, except for the special `github_actions` branch.
- The Redis URL selection also depends on `ENVIRONMENT`. The default cache backend requires a configured Redis location.
- Django reads `SECRET_KEY`. Do not assume a differently named deployment variable is consumed.

These settings currently have important production and CI gaps documented in [known issues](known-issues.md). The checked-in CI and Render configurations should not be treated as proof that production-like settings are tested.

## Data safety

Do not run [`populate_categories`](../recipes/management/commands/populate_categories.py) as a harmless repeatable seed command: its current implementation deletes all categories and tags before recreating preset values. Review the data impact and take an appropriate backup before running it against any database with user data.

## Test limitations

`python manage.py test` is the backend test entry point, but the current test command discovers zero tests; many existing test modules are empty or commented out. There is no frontend test runner or `npm test` command, and `tsconfig.json` excludes `*.spec.ts`. Add tests that are executable and included in the relevant runner; do not count an uncollected spec file as validation.
