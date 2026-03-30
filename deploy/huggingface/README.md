---
title: P5 API Attrition Employes
emoji: "🧠"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---

# P5 API Attrition Employes

Ce Space Docker expose l'API FastAPI de prediction d'attrition.

## Notes de runtime

- l'application ecoute sur le port `8000`
- si `P5_DATABASE_URL` n'est pas defini, l'API utilise un fallback SQLite local au conteneur
- pour conserver une vraie persistance PostgreSQL, il faut definir `P5_DATABASE_URL` dans les secrets ou variables du Space

## Endpoints utiles

- `GET /`
- `GET /health`
- `POST /api/v1/predict`
- `POST /api/v1/explain`
- `POST /api/v1/predict/batch`

## Role de ce Space

Ce Space sert surtout de preuve de deploiement distant.

La reference technique du projet P5 reste :

- le fonctionnement local avec PostgreSQL ;
- les tests automatises ;
- la verification locale du preprocessing et du score.
