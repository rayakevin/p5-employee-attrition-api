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

Project setup instructions will be completed as the repository is structured.

## Branching strategy

Main branches and feature branches will follow a naming convention such as:

- `main`
- `feature/ci-cd`
- `feature/api-fastapi`
- `feature/postgresql-logging`
- `feature/tests`
- `docs/project-documentation`

## Project status

Project initialization in progress.

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
