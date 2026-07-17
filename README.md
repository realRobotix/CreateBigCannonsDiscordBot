# Create Big Cannons Discord Bot

This project now uses:
- `uv` for dependency management and lockfile generation
- a `src/` layout (`src/cbcbot`)
- Docker images published to GHCR from release tags only

## Requirements

- Python 3.12+
- `uv` (`https://docs.astral.sh/uv/`)

## Quick Start

```bash
uv sync
uv run cbcbot
```

## Configuration

Config is loaded from `settings.toml` at the project root if present; otherwise it falls back
to `config/settings.<env>.toml`. Values are overridden by environment variables and `.env`
(prefixed with `CBCBOT_`). Environment selection is automatic but can be forced.

Automatic selection:
- `CBCBOT_ENV=dev` or `CBCBOT_ENV=prod` if set (from env or `.env`)
- otherwise `prod` if running in Docker (`/.dockerenv`), else `dev`

Example `.env`:

```bash
CBCBOT_ENV=dev
CBCBOT_BOT_DISCORD_TOKEN=dev-token
```

Optional Docker secrets:
- `CBCBOT_<FIELD>_FILE=/run/secrets/<name>`
- or `/run/secrets/<field>` by default (field names are lowercased)

## Docker Compose Examples

Development (builds locally):

```bash
docker compose -f compose.dev.yml up --build
```

Production-like (runs a prebuilt image):

```bash
docker compose -f compose.prod.yml up
```

## Smoke Test

```bash
uv run python tests/test_smoke_imports.py
```

## Docker (Local Build)

```bash
docker build -t cbcbot:local .
```

Run with your environment file:

```bash
docker run --rm --env-file .env cbcbot:local
```

## Release Images (GHCR)

Images are only published when a GitHub Release is published with a semantic tag:
- valid: `v1.2.3`
- invalid: `v1.2.3-rc1`, `1.2.3`

Workflow file: `.github/workflows/release-ghcr.yml`

Resulting image tags:
- `ghcr.io/<owner>/<repo>:vX.Y.Z`
- `ghcr.io/<owner>/<repo>:latest`

## Dependency Management

- Edit direct dependencies in `pyproject.toml`
- Refresh lockfile:

```bash
uv lock
```
