# Protocole de mise a jour reguliere

## 1. Objectif

Ce protocole sert de check-list pour maintenir le projet dans un etat fiable au fil du temps.

## 2. Quand appliquer ce protocole

Il doit etre rejoue :

- avant une demonstration importante ;
- avant un merge vers `main` ;
- apres une mise a jour de dependances ;
- apres une modification du modele ;
- apres une modification du preprocessing ;
- apres une modification du deploiement Docker ou du CD.

## 3. Etapes de verification

### 3.1 Verifier l'etat Git

```powershell
git status
git log --oneline -n 5
```

### 3.2 Verifier les dependances

```powershell
uv pip install -r requirements.txt
```

Si le runtime change, verifier aussi :

```powershell
Get-Content requirements.runtime.txt
```

### 3.3 Verifier la base locale

```powershell
docker compose up -d postgres
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

### 3.4 Verifier les tests

```powershell
uv run pytest -q
```

### 3.5 Verifier l'API localement

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run uvicorn app.main:app --reload
```

Puis tester :

- `/health`
- `/api/v1/predict`

### 3.6 Verifier la persistance

Verifier que les tables suivantes sont bien alimentees apres une prediction :

- `prediction_requests`
- `prediction_results`
- `api_audit_logs`

### 3.7 Verifier le packaging Docker

```powershell
docker compose build api
docker compose up -d --build postgres api
```

Puis tester :

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/v1/predict`

### 3.8 Verifier le deploiement distant

Apres merge sur `main` :

- verifier la CI ;
- verifier la CD ;
- verifier le build du Space Hugging Face ;
- verifier `/health` ;
- verifier `/api/v1/predict`.

## 4. Regle de mise a jour de la documentation

La documentation doit etre mise a jour si un changement modifie :

- l'architecture ;
- les commandes de lancement ;
- les variables d'environnement ;
- le format des payloads ;
- la logique de score ;
- le deploiement ;
- le protocole de maintenance.

## 5. Regle de maintenance recommandee

Frequence minimale conseillee :

- verification rapide avant chaque merge important ;
- verification complete avant soutenance ou demonstration ;
- verification complete apres tout changement de runtime ou de modele.
