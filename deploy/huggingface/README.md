---
title: P5 Employee Attrition API
emoji: "\U0001F9E0"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---

# P5 Employee Attrition API

Docker Space exposing the FastAPI service for employee attrition prediction.

## Runtime notes

- the application listens on port `8000`
- if `P5_DATABASE_URL` is not defined, the API falls back to local SQLite
- to keep prediction tracking in PostgreSQL, define `P5_DATABASE_URL` in the Space settings

## Main endpoint

- `GET /health`
- `POST /api/v1/predict`
