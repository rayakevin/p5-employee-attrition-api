# Rapport de couverture de tests

## 1. Commande utilisee

La couverture de reference a ete generee avec :

```powershell
$env:P5_RUN_POSTGRES_INTEGRATION="1"
uv run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
```

## 2. Resultats globaux

- Tests executes : `29`
- Tests reussis : `29 passed`
- Couverture totale sur le package `app` : `89%`

Artifacts produits :

- [`../../coverage.xml`](../../coverage.xml) : rapport XML exploitable par la CI et par des outils d'analyse ;
- `htmlcov/index.html` : rapport HTML local pour lecture detaillee.

## 3. Lecture synthetique

Les composants les mieux couverts sont les zones critiques du projet :

- `app/core/config.py` : `97%`
- `app/ml/predictor.py` : `97%`
- `app/ml/explainer.py` : `94%`
- `app/services/prediction_service.py` : `94%`
- `app/schemas/prediction.py` : `91%`
- `app/core/security.py` : `91%`
- `app/db/models/tracking.py` : `100%`

Le preprocessing, qui reste une zone sensible, atteint :

- `app/ml/preprocess.py` : `84%`

Les zones un peu moins couvertes sont :

- `app/api/v1/endpoints/predict.py` : `75%`
- `app/db/session.py` : `79%`
- `app/ml/loader.py` : `82%`

## 4. Interpretation

Cette couverture est solide pour un projet de niveau P5, car elle securise bien les flux qui portent le plus de risque :

- validation des entrees ;
- prediction unitaire ;
- explication locale ;
- batch scoring ;
- authentification par cle API ;
- persistance et audit log ;
- seed des donnees source ;
- verification PostgreSQL reelle des contraintes `FK` / `UNIQUE` ;
- verification des index de tracabilite sur le moteur cible ;
- contrat OpenAPI expose par FastAPI ;
- comportement par environnement.

Le reliquat non couvert correspond surtout a :

- des chemins secondaires ;
- du code de demarrage ;
- certaines branches d'infrastructure moins critiques que le coeur metier.

## 5. Conclusion

La strategie de tests ne cherche pas uniquement a faire monter un pourcentage global : elle vise d'abord a securiser les comportements critiques du systeme.

Le niveau actuel de couverture est donc coherent avec l'objectif du projet :

- prouver la robustesse du service ;
- verifier l'integrite des donnees manipulees ;
- couvrir les cas nominaux et les scenarios d'erreur principaux ;
- demontrer que le modele est bien industrialise dans une application testee.
