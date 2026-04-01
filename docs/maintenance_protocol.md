# Protocole de mise à jour régulière

## 1. Objectif

Ce protocole sert de check-list pour maintenir le projet dans un état fiable au fil du temps.

## 2. Quand appliquer ce protocole

Il doit être rejoué :

- avant une démonstration importante ;
- avant un merge vers `develop` ou `main` ;
- après une mise à jour de dépendances ;
- après une modification du modèle ;
- après une modification du preprocessing ;
- après une modification du déploiement Docker ou du CD.

## 3. Étapes de vérification

### 3.1 Vérifier l'état Git

```powershell
git status
git log --oneline -n 5
```

### 3.2 Vérifier les dépendances

```powershell
uv pip install -r requirements.txt
```

Si le runtime change, vérifier aussi :

```powershell
Get-Content requirements.runtime.txt
Get-Content requirements.streamlit.txt
```

### 3.3 Vérifier la base locale

```powershell
docker compose up -d postgres
$env:P5_ENVIRONMENT="development"
$env:P5_API_KEY="change-me-local-dev-key"
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

### 3.4 Vérifier les tests

```powershell
uv run pytest -q
```

### 3.5 Vérifier l'API localement

```powershell
$env:P5_ENVIRONMENT="development"
$env:P5_API_KEY="change-me-local-dev-key"
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run uvicorn app.main:app --reload
```

Puis tester :

- `/health`
- `/docs`
- `/api/v1/predict`

### 3.6 Vérifier la persistance

Vérifier que les tables suivantes sont bien alimentées après une prédiction :

- `prediction_requests`
- `prediction_results`
- `api_audit_logs`

### 3.7 Vérifier le packaging Docker

```powershell
docker compose build api
docker compose up -d --build postgres api
```

Puis tester :

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/v1/predict`

### 3.8 Vérifier le déploiement distant

Après merge sur `develop` ou `main` :

- vérifier la CI ;
- vérifier la CD ;
- vérifier le build du Space Hugging Face ;
- vérifier `/health` ;
- vérifier `/openapi.json` ;
- vérifier `/api/v1/predict`.

## 4. Règle de mise à jour de la documentation

La documentation doit être mise à jour si un changement modifie :

- l'architecture ;
- les commandes de lancement ;
- les variables d'environnement ;
- le format des payloads ;
- la logique de score ;
- le déploiement ;
- le protocole de maintenance.

## 5. Règle de maintenance recommandée

Fréquence minimale conseillée :

- vérification rapide avant chaque merge important ;
- vérification complète avant démonstration ;
- vérification complète après tout changement de runtime ou de modèle.
