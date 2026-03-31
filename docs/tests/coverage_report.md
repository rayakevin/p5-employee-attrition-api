# Rapport de couverture de tests

## 1. Commande utilisée

La couverture a été générée avec :

```powershell
uv run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
```

## 2. Résultats globaux

- Tests exécutés : `22`
- Tests réussis : `22 passed`
- Couverture totale sur le package `app` : `89%`

Artifacts produits :

- [`../../coverage.xml`](../../coverage.xml) : rapport XML exploitable par la CI et par des outils d'analyse ;
- `htmlcov/index.html` : rapport HTML local pour lecture détaillée.

## 3. Lecture synthétique

Les éléments les mieux couverts sont les composants critiques du projet :

- `app/ml/predictor.py` : `97%`
- `app/ml/explainer.py` : `94%`
- `app/services/prediction_service.py` : `94%`
- `app/schemas/prediction.py` : `91%`
- `app/core/security.py` : `91%`

Le preprocessing, qui est une zone sensible du projet, atteint :

- `app/ml/preprocess.py` : `84%`

Les zones un peu moins couvertes sont :

- `app/api/v1/endpoints/predict.py` : `75%`
- `app/db/session.py` : `75%`
- `app/ml/loader.py` : `82%`

## 4. Interprétation

Cette couverture est solide pour un projet de niveau P5, car elle sécurise bien les flux qui portent le plus de risque :

- validation des entrées ;
- prédiction unitaire ;
- explication locale ;
- batch scoring ;
- authentification par clé API ;
- persistance et audit log ;
- seed des données source ;
- contrat OpenAPI exposé par FastAPI.

Le reliquat non couvert correspond surtout à :

- des chemins secondaires ;
- du code de démarrage ;
- certaines branches d'infrastructure moins critiques que le cœur métier.

## 5. Conclusion

La stratégie de tests ne cherche pas uniquement à faire monter un pourcentage global : elle vise d'abord à sécuriser les comportements critiques du système.

Le niveau actuel de couverture est donc cohérent avec l'objectif du projet :

- prouver la robustesse du service ;
- vérifier l'intégrité des données manipulées ;
- couvrir les cas nominaux et les scénarios d'erreur principaux ;
- démontrer que le modèle est bien industrialisé dans une application testée.
