---
title: P5 API Attrition Employés
emoji: "🧠"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---

# P5 API Attrition Employés

Ce Space Docker expose l'API FastAPI de prédiction d'attrition.

## Notes de runtime

- l'application écoute sur le port `8000`
- le runtime cible attend `P5_ENVIRONMENT=production`
- pour fonctionner proprement, le Space doit recevoir `P5_API_KEY` et `P5_DATABASE_URL`
- PostgreSQL distant reste la cible normale d'exploitation du Space API

## Endpoints utiles

- `GET /`
- `GET /health`
- `POST /api/v1/predict`
- `POST /api/v1/explain`
- `POST /api/v1/predict/batch`

## Role de ce Space

Ce Space sert surtout de preuve de déploiement distant.

La référence technique du projet P5 reste :

- le fonctionnement local avec PostgreSQL ;
- les tests automatisés ;
- la vérification locale du preprocessing et du score.
