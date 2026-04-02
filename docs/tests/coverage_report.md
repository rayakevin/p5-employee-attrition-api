# Rapport de couverture de tests

## 1. Commandes de référence

### Exécution locale standard

La couverture locale standard est générée avec :

```powershell
uv run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
```

### Variante PostgreSQL cible

Quand on veut activer explicitement la campagne PostgreSQL cible, il faut en plus fournir un PostgreSQL compatible et activer :

```powershell
$env:P5_ENVIRONMENT="test"
$env:P5_API_KEY="p5-test-key"
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5432/p5_attrition"
$env:P5_RUN_POSTGRES_INTEGRATION="1"
uv run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
```

En CI GitHub Actions, cette variante est activée automatiquement.

## 2. Résultats globaux

### Résultat local standard constaté

- Tests réussis : `27 passed, 2 skipped`
- Couverture totale sur le package `app` : `89%`

Les 2 tests ignorés correspondent aux tests PostgreSQL réels, réservés à la CI ou à une exécution locale explicite avec base PostgreSQL compatible.

### Ce que la variante PostgreSQL ajoute

La campagne PostgreSQL cible ajoute un contrôle réel sur le moteur cible pour vérifier :

- le seed sur PostgreSQL ;
- les contraintes `FK` / `UNIQUE` ;
- l'audit log applicatif ;
- les index de traçabilité sur le moteur cible.

Quand cette variante est activée et que le PostgreSQL cible est disponible, elle porte la campagne complète à `29` tests au total.

Artifacts produits :

- [`../../coverage.xml`](../../coverage.xml) : rapport XML exploitable par la CI et par des outils d'analyse ;
- `htmlcov/index.html` : rapport HTML local pour lecture détaillée.

## 3. Lecture synthétique

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
- `app/db/session.py` : `64%`
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
- contrat OpenAPI exposé par FastAPI ;
- comportement par environnement.

Le reliquat non couvert correspond surtout à :

- des chemins secondaires ;
- du code de démarrage ;
- certaines branches d'infrastructure moins critiques que le coeur métier.

## 5. Conclusion

La stratégie de tests ne cherche pas uniquement à faire monter un pourcentage global : elle vise d'abord à sécuriser les comportements critiques du système.

Le niveau actuel de couverture est donc cohérent avec l'objectif du projet :

- prouver la robustesse du service ;
- vérifier l'intégrité des données manipulées ;
- couvrir les cas nominaux et les scénarios d'erreur principaux ;
- démontrer que le modèle est bien industrialisé dans une application testée ;
- compléter les tests rapides SQLite par un contrôle PostgreSQL réel dans la CI.
