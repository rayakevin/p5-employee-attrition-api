# P5 - API de prediction d'attrition des employes

## 1. Presentation

Ce depot correspond a la mise en production du modele de prediction d'attrition construit au projet 4, puis industrialise dans le cadre du projet 5.

Le projet ne se limite pas a exposer un `predict()` :

- une API FastAPI sert de point d'entree metier ;
- un preprocessing reconstruit exactement les variables attendues par le modele final ;
- les predictions sont tracees en base ;
- le modele est package via MLflow ;
- une interface Streamlit sert de portfolio et de support de demonstration ;
- une CI et une CD automatisent les controles et le deploiement.

## 2. Ce que fait l'application

L'application permet de :

- recevoir un profil employe en JSON ;
- valider les entrees avec Pydantic ;
- reconstruire les features du modele final ;
- calculer une prediction, un score et une explication locale ;
- enregistrer la requete et le resultat en base ;
- traiter un fichier CSV en batch depuis l'interface Streamlit.

## 3. Architecture

### 3.1 Vue d'ensemble

- `app/api/` : endpoints FastAPI
- `app/schemas/` : schemas Pydantic d'entree et de sortie
- `app/services/` : orchestration metier
- `app/ml/` : chargement du modele, preprocessing, scoring, explication locale
- `app/db/` : SQLAlchemy, sessions et modeles ORM
- `scripts/` : creation de base, seed, export MLflow
- `ui/` : application Streamlit
- `tests/` : tests unitaires et tests d'integration
- `artifacts/model/` : artefacts MLflow et metadata applicative
- `docs/` : documentation de travail, architecture et exploitation

### 3.2 Flux de prediction

1. L'API recoit un payload JSON.
2. Pydantic valide les types et la structure.
3. Le service metier journalise la requete si la persistance est active.
4. Le preprocessing reconstruit les variables du modele.
5. Le modele MLflow est charge.
6. Le score est calcule avec la methode declaree dans la metadata (`decision_function` pour le modele final).
7. La prediction est derivee du score et du seuil.
8. Le resultat et le log technique sont enregistres en base.

### 3.3 Flux d'explication locale

1. L'API recoit le meme payload que pour une prediction.
2. Le preprocessing reconstruit les features finales.
3. Le module d'explication decompose le score du modele lineaire en contributions locales.
4. L'API renvoie les facteurs qui augmentent ou diminuent le risque de depart.

### 3.4 Flux batch

1. Streamlit charge un CSV de type `df_EDA.csv`.
2. Le frontend decoupe les donnees en paquets.
3. Chaque paquet est envoye a `POST /api/v1/predict/batch`.
4. L'application affiche des indicateurs globaux, les profils les plus exposes et une analyse locale par employe.

Documentation complementaire :

- [`docs/architecture/overview.md`](docs/architecture/overview.md)
- [`docs/p5_trace.md`](docs/p5_trace.md)
- [`docs/p5_demo_exploitation.md`](docs/p5_demo_exploitation.md)
- [`docs/maintenance_protocol.md`](docs/maintenance_protocol.md)

## 4. Choix techniques et justifications

### FastAPI

FastAPI a ete choisi pour :

- sa rapidite de mise en place ;
- sa documentation OpenAPI native ;
- la validation directe via Pydantic ;
- sa bonne adequation a une API de prediction.

### Pydantic

Pydantic garantit :

- des contrats d'entree et de sortie explicites ;
- des erreurs propres quand le payload est invalide ;
- une documentation technique alignant code et API.

### MLflow

MLflow sert a :

- exporter le modele dans un format standard ;
- conserver une metadata applicative ;
- dissocier l'entrainement et le runtime de prediction.

### SQLAlchemy et PostgreSQL

Cette pile a ete retenue pour :

- tracer les predictions et les erreurs ;
- stocker les donnees source ;
- garder une couche de persistance explicite, testable et evolutive.

### Streamlit

Streamlit est utilise pour :

- exposer une interface portfolio rapide a iterer ;
- demontrer le projet sans passer uniquement par Swagger ou PowerShell ;
- fournir une vue unitaire et batch du modele.

### Docker

Docker permet :

- de figer l'environnement d'execution ;
- de reproduire localement une stack proche du deploiement ;
- de deployer sur Hugging Face Spaces en mode Docker.

### GitHub Actions

GitHub Actions est utilise pour :

- valider les tests automatiquement ;
- separer CI et CD ;
- pousser les Spaces Hugging Face depuis le repository.

## 5. Prerequis

Pour travailler localement sur le projet :

- Python `3.11`
- `uv`
- Docker Desktop
- Git

## 6. Installation locale

### 6.1 Cloner le depot

```powershell
git clone https://github.com/rayakevin/p5-employee-attrition-api.git
cd p5-employee-attrition-api
```

### 6.2 Creer l'environnement Python

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### 6.3 Variables de configuration

La configuration du projet est prefixee par `P5_`.

Variable principale :

```env
P5_DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition
```

Variable utile pour le portfolio Streamlit :

```env
P5_API_BASE_URL=http://127.0.0.1:8000
```

En deploiement distant, si `P5_DATABASE_URL` n'est pas defini, l'API utilise un fallback SQLite local au conteneur. Le projet configure ce fallback sur un chemin ecrivable pour Hugging Face Spaces.

## 7. Lancement local avec PostgreSQL

### 7.1 Demarrer PostgreSQL

```powershell
docker compose up -d postgres
```

Le projet utilise `5433` pour eviter les collisions avec une installation PostgreSQL locale deja presente sur `5432`.

### 7.2 Creer le schema et charger les donnees source

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

Explication :

- `scripts/create_db.py` cree les tables SQLAlchemy ;
- `scripts/seed_data.py` fusionne les trois fichiers CSV metier et recharge `employees_source`.

Un script de `seed` est un script qui peuple une base avec des donnees initiales utiles a l'application, aux demonstrations ou aux tests.

### 7.3 Demarrer l'API

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run uvicorn app.main:app --reload
```

### 7.4 Verifier le service

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

Reponse attendue :

```json
{"status":"ok"}
```

## 8. Utilisation de l'API

### 8.1 Endpoints principaux

- `GET /`
- `GET /health`
- `POST /api/v1/predict`
- `POST /api/v1/explain`
- `POST /api/v1/predict/batch`

### 8.2 Valeurs conseillees pour les champs categoriels

Les valeurs ci-dessous reprennent les libelles francises documentes par le projet et normalises par le preprocessing.

- `genre` : `Homme`, `Femme`
- `statut_marital` : `Celibataire`, `Marie(e)`, `Divorce(e)`
- `departement` : `Commercial`, `Consulting`, `Ressources Humaines`
- `poste` :
  - `Assistant de Direction`
  - `Cadre Commercial`
  - `Consultant`
  - `Directeur Technique`
  - `Manager`
  - `Representant Commercial`
  - `Ressources Humaines`
  - `Senior Manager`
  - `Tech Lead`
- `domaine_etude` :
  - `Autre`
  - `Entrepreunariat`
  - `Infra & Cloud`
  - `Marketing`
  - `Ressources Humaines`
  - `Transformation Digitale`
- `frequence_deplacement` : `Aucun`, `Frequent`, `Occasionnel`
- `heure_supplementaires` : `Oui`, `Non`

Le projet conserve quelques alias historiques pour compatibilite, mais le contrat documentaire a privilegier est francais.

### 8.3 Exemple de payload de prediction

```powershell
$payload = @{
    age = 35
    genre = "Homme"
    revenu_mensuel = 4500
    statut_marital = "Marie(e)"
    departement = "Consulting"
    poste = "Consultant"
    nombre_experiences_precedentes = 3
    annee_experience_totale = 12
    annees_dans_l_entreprise = 7
    annees_dans_le_poste_actuel = 4
    satisfaction_employee_environnement = 3
    note_evaluation_precedente = 3.0
    niveau_hierarchique_poste = 2
    satisfaction_employee_nature_travail = 4
    satisfaction_employee_equipe = 3
    satisfaction_employee_equilibre_pro_perso = 2
    note_evaluation_actuelle = 4.0
    heure_supplementaires = "Oui"
    augementation_salaire_precedente = 0.12
    nombre_participation_pee = 1
    nb_formations_suivies = 3
    nombre_employee_sous_responsabilite = 0
    distance_domicile_travail = 12
    niveau_education = 3
    domaine_etude = "Infra & Cloud"
    frequence_deplacement = "Occasionnel"
    annees_depuis_la_derniere_promotion = 2
    annes_sous_responsable_actuel = 3
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/predict" `
  -ContentType "application/json" `
  -Body $payload
```

Exemple de reponse :

```json
{
  "prediction": 0,
  "score": -18.58866414724979,
  "threshold": 0.1138,
  "model_version": "0.1.0",
  "model_name": "linear_svc_attrition"
}
```

### 8.4 Exemple de requete d'explication locale

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/explain" `
  -ContentType "application/json" `
  -Body $payload
```

La reponse contient :

- la `base_value` ;
- les sommes positives et negatives ;
- les facteurs principaux qui augmentent le risque ;
- les facteurs principaux qui diminuent le risque.

### 8.5 Exemple de requete batch

```powershell
$batch = @{
    rows = @(
        @{
            age = 35
            genre = "Homme"
            revenu_mensuel = 4500
            statut_marital = "Marie(e)"
            departement = "Consulting"
            poste = "Consultant"
            nombre_experiences_precedentes = 3
            annee_experience_totale = 12
            annees_dans_l_entreprise = 7
            annees_dans_le_poste_actuel = 4
            satisfaction_employee_environnement = 3
            note_evaluation_precedente = 3.0
            niveau_hierarchique_poste = 2
            satisfaction_employee_nature_travail = 4
            satisfaction_employee_equipe = 3
            satisfaction_employee_equilibre_pro_perso = 2
            note_evaluation_actuelle = 4.0
            heure_supplementaires = "Oui"
            augementation_salaire_precedente = 0.12
            nombre_participation_pee = 1
            nb_formations_suivies = 3
            nombre_employee_sous_responsabilite = 0
            distance_domicile_travail = 12
            niveau_education = 3
            domaine_etude = "Infra & Cloud"
            frequence_deplacement = "Occasionnel"
            annees_depuis_la_derniere_promotion = 2
            annes_sous_responsable_actuel = 3
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/predict/batch" `
  -ContentType "application/json" `
  -Body $batch
```

## 9. Base de donnees et tracabilite

Tables principales :

- `employees_source` : donnees source fusionnees depuis les CSV bruts
- `prediction_requests` : payload brut recu
- `prediction_results` : prediction, score, seuil et metadata du modele
- `api_audit_logs` : trace technique de l'appel

Cette couche est essentielle pour le P5 car elle montre que le modele est integre dans un vrai flux applicatif.

## 10. Interface Streamlit

L'interface portfolio se trouve dans [`ui/streamlit_app.py`](ui/streamlit_app.py).

Elle propose :

- une analyse unitaire ;
- une explication locale visuelle ;
- une analyse batch sur CSV ;
- une selection employe par employe apres scoring global.

### Lancer Streamlit en local

```powershell
$env:P5_API_BASE_URL="http://127.0.0.1:8000"
uv run streamlit run ui/streamlit_app.py
```

## 11. Tests

### 11.1 Lancer toute la suite

```powershell
uv run pytest -q
```

### 11.2 Ce qui est couvert

- endpoints API ;
- validation des schemas ;
- logique de score ;
- explication locale ;
- preprocessing ;
- persistance en base ;
- seed des donnees source ;
- endpoints batch.

## 12. Docker

### 12.1 Stack locale API + PostgreSQL

```powershell
docker compose up -d --build postgres api
```

Verification :

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

### 12.2 Portfolio Streamlit local

```powershell
docker compose up -d --build portfolio
```

Le portfolio consomme l'API via `P5_API_BASE_URL`.

## 13. CI/CD

### 13.1 CI

Workflow :

- [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

La CI :

- installe les dependances ;
- demarre PostgreSQL ;
- cree le schema ;
- charge les donnees source ;
- execute les tests.

### 13.2 CD API

Workflow :

- [`.github/workflows/cd.yml`](.github/workflows/cd.yml)

Configuration GitHub requise :

- secret `HF_TOKEN`
- variable `HF_USERNAME`
- variable `HF_SPACE_NAME`

### 13.3 CD portfolio Streamlit

Workflow :

- [`.github/workflows/cd-portfolio.yml`](.github/workflows/cd-portfolio.yml)

Configuration GitHub requise :

- secret `HF_TOKEN`
- variable `HF_USERNAME`
- variable `HF_PORTFOLIO_SPACE_NAME`

Documentation de deploiement :

- [`deploy/huggingface/README.md`](deploy/huggingface/README.md)
- [`deploy/huggingface/portfolio.README.md`](deploy/huggingface/portfolio.README.md)

## 14. Deploiement distant

Le projet utilise Hugging Face Spaces en mode Docker.

Important :

- le Space API sert de preuve de deploiement distant ;
- la reference technique pour le P5 reste l'environnement local avec PostgreSQL ;
- les rebuilds HF peuvent etre longs, donc le debug principal reste local ;
- le fallback SQLite du Space API est prevu pour un chemin de fichier ecrivable dans le conteneur.

Exemples de verification distante :

```powershell
Invoke-RestMethod -Method Get -Uri "https://rayakevin-p5-employee-attrition-api.hf.space/health"
```

## 15. Protocole de mise a jour

Le protocole detaille est documente dans [`docs/maintenance_protocol.md`](docs/maintenance_protocol.md).

Resume pratique :

1. mettre a jour le code et les dependances ;
2. relancer `uv run pytest -q` ;
3. verifier la prediction locale ;
4. verifier la base et la tracabilite ;
5. verifier les builds Docker ;
6. verifier les deploiements distants ;
7. mettre a jour la documentation si le comportement change.

## 16. Conventions Git

### 16.1 Branches

- `feature/<sujet>` : nouvelle fonctionnalite
- `fix/<sujet>` : correction de bug
- `docs/<sujet>` : documentation
- `chore/<sujet>` : maintenance, packaging, nettoyage
- `test/<sujet>` : ajout ou reprise de tests

### 16.2 Commits

- `feat:` : nouvelle fonctionnalite
- `fix:` : correction
- `docs:` : documentation
- `chore:` : maintenance
- `test:` : tests
- `ci:` : pipeline GitHub Actions

## 17. Dependances

- `requirements.txt` : environnement complet de dev, tests et usage local
- `requirements.runtime.txt` : runtime API allege pour Docker et le Space API
- `requirements.streamlit.txt` : runtime portfolio Streamlit

## 18. Documents utiles

- [`docs/p5_trace.md`](docs/p5_trace.md) : mode operatoire detaille et retour d'experience
- [`docs/p5_demo_exploitation.md`](docs/p5_demo_exploitation.md) : fiche de demonstration
- [`docs/architecture/overview.md`](docs/architecture/overview.md) : architecture
- [`docs/maintenance_protocol.md`](docs/maintenance_protocol.md) : maintenance

## 19. Etat du projet

A date, le projet dispose :

- d'une API FastAPI fonctionnelle ;
- d'un modele final exporte et charge via MLflow ;
- d'une explication locale additive ;
- d'une base PostgreSQL locale avec seed ;
- d'une tracabilite applicative ;
- d'un portfolio Streamlit avec traitement batch ;
- d'une CI et de deux CD distinctes ;
- d'une documentation exploitable.

## 20. Limites connues

- les rebuilds Hugging Face Spaces peuvent etre tres longs ;
- PostgreSQL local n'est pas automatiquement disponible dans les Spaces ;
- la cible distante sert surtout de vitrine et de preuve de deploiement.

## 21. Contexte

Projet realise dans le cadre du Projet 5 OpenClassrooms, avec l'objectif de transformer un modele de machine learning en application exploitable, testable, tracable et documentee.
