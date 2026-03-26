# P5 Employee Attrition API

Production deployment project for a machine learning model predicting employee attrition.

## Project goals

This project aims to put into production a machine learning model developed during Project 4 of the OpenClassrooms AI Engineer path.

The application will include:

- a REST API built with FastAPI
- robust input validation with Pydantic
- model tracking with MLflow
- a PostgreSQL database for logging inputs and predictions
- automated tests with Pytest
- CI/CD pipelines with GitHub Actions
- containerization with Docker
- deployment to a remote environment
- technical and user documentation

## Main stack

- Python
- FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy
- Psycopg
- MLflow
- Pytest
- Docker
- GitHub Actions

## Installation

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

## Local PostgreSQL setup

Start PostgreSQL with Docker Compose:

```powershell
docker compose up -d postgres
```

Use this connection string locally:

```env
P5_DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition
```

Note:
if a local PostgreSQL server is already running on your machine, port `5432` may already be occupied. This project exposes the Docker PostgreSQL instance on port `5433` to avoid that conflict.

Create the schema and load the source data:

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

Run the API locally with the same database:

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run uvicorn app.main:app --reload
```

Stop PostgreSQL when finished:

```powershell
docker compose down
```

## Branching strategy

Main branches and feature branches will follow a naming convention such as:

- `main`
- `feature/ci-cd`
- `feature/api-fastapi`
- `feature/postgresql-logging`
- `feature/tests`
- `docs/project-documentation`

## Project status

API, MLflow packaging, local tracing and source-data seeding are in place.

## Git workflow

### Branch naming convention

Branches follow this naming pattern:

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `chore/<short-description>`
- `test/<short-description>`

Examples:
- `feature/api-fastapi`
- `feature/postgresql-logging`
- `feature/ci-cd`

---

### Commit convention

Commits follow a simplified Conventional Commits format:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `chore:` maintenance
- `test:` tests

Examples:
- `feat: add prediction endpoint`
- `fix: handle invalid input data`
- `test: add API unit tests`
