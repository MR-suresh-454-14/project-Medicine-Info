# Project Medicine Info

## Local development

This project requires Python 3.12 or newer. Use `uv` for dependency management
and to run project commands:

```powershell
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Run the test suite with `uv run python manage.py test`.

## Database configuration

Set `DATABASE_URL` to the PostgreSQL connection URL in deployed environments.
The legacy `PGURL` variable is accepted only when `DATABASE_URL` is not set.
If neither is set, the app uses the local SQLite database. Keep database
credentials and other secrets in environment variables (or a local `.env`
file); do not commit them.