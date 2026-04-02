# Architecture du projet

## 1. Vue d'ensemble

Le projet suit une architecture en couches simple et explicite :

- `api` : gestion HTTP, routage et codes de reponse ;
- `schemas` : validation Pydantic des contrats d'entree et de sortie ;
- `services` : orchestration metier ;
- `ml` : preprocessing, chargement du modele, scoring et explication locale ;
- `db` : persistance SQLAlchemy et modeles ORM ;
- `scripts` : initialisation de base, seed et export MLflow ;
- `ui` : portfolio Streamlit ;
- `tests` : tests unitaires, d'integration et fonctionnels.

Documents complementaires :

- [Documentation API](../api/README.md)
- [Documentation de la base de donnees](../db/README.md)
- [Documentation du modele](../model/README.md)

## 2. Flux fonctionnel principal

Le systeme complet peut etre resume ainsi :

```mermaid
flowchart LR
    U[Utilisateur / Client HTTP] --> S[PowerShell ou Streamlit]
    S --> A[API FastAPI<br/>Uvicorn local ou HF Space]
    A --> V[Validation Pydantic]
    V --> P[Preprocessing]
    P --> M[Modele MLflow]
    M --> R[Reponse JSON<br/>prediction, score, threshold, version]
    A --> D[(PostgreSQL / Supabase)]
    D --> T1[prediction_requests]
    D --> T2[prediction_results]
    D --> T3[api_audit_logs]
```

Lecture :

- le client peut etre un appel PowerShell, Swagger ou le portfolio Streamlit ;
- l'API centralise la validation, le preprocessing et le scoring ;
- la persistance est reservee aux predictions unitaires metier ;
- la base conserve la requete brute, le resultat et l'audit technique.

## 3. Demarrage local de l'API

En local, l'application est demarree par :

```powershell
uv run uvicorn app.main:app --reload
```

Le demarrage suit la sequence suivante :

```mermaid
flowchart TD
    C[uv run uvicorn app.main:app --reload] --> U[Uvicorn demarre]
    U --> F[Charge app.main:app]
    F --> G[FastAPI est instanciee]
    G --> H[Le routeur /api/v1 est branche]
    H --> I[La config P5_* est lue]
    I --> J[SQLAlchemy prepare la connexion DB]
    J --> K[Le serveur ecoute sur http://127.0.0.1:8000]
    K --> L[L'API est accessible]
```

Ce schema explique le passage entre une simple commande de terminal et un service HTTP exploitable localement.

## 4. Architecture de production

La production actuellement deployee se compose de deux Spaces Hugging Face et d'une base PostgreSQL distante :

```mermaid
flowchart TD
    U[Utilisateur final]

    subgraph HF1[Hugging Face Space - Portfolio PROD]
        PF[Streamlit]
        CFGPF[Variables runtime<br/>P5_ENVIRONMENT=production<br/>P5_API_BASE_URL<br/>P5_API_KEY]
    end

    subgraph HF2[Hugging Face Space - API PROD]
        API[FastAPI + Uvicorn]
        CFGAPI[Variables runtime<br/>P5_ENVIRONMENT=production<br/>P5_API_KEY<br/>P5_DATABASE_URL]
        PREP[Preprocessing]
        MODEL[Modele MLflow]
    end

    subgraph DB1[Supabase PROD]
        DB[(PostgreSQL)]
        T1[prediction_requests]
        T2[prediction_results]
        T3[api_audit_logs]
    end

    U --> PF
    PF --> API
    API --> PREP
    PREP --> MODEL
    API --> DB
    DB --> T1
    DB --> T2
    DB --> T3
    API --> PF
    PF --> U
```

Points clefs :

- le portfolio n'embarque pas le modele ;
- le Space API porte toute la logique metier ;
- la base distante de reference en ligne est PostgreSQL via Supabase ;
- les variables runtime des Spaces HF sont distinctes des variables GitHub du pipeline.

## 5. Flux de prediction detaille

Le flux metier est le suivant :

1. le client appelle `POST /api/v1/predict` ;
2. `PredictionInput` valide le payload ;
3. `prediction_service.get_prediction()` enregistre la requete ;
4. `build_model_features()` reconstruit les features du modele final ;
5. `load_mlflow_model()` charge le modele et sa metadata ;
6. `predict_attrition()` calcule le score puis la classe finale ;
7. le resultat est persiste en base ;
8. un log technique est ecrit dans `api_audit_logs` ;
9. l'API renvoie une `PredictionOutput`.

Le portfolio Streamlit ne recalcule jamais le modele lui-meme : il appelle l'API via `P5_API_BASE_URL`. Cela garantit que l'interface affiche exactement le comportement du service reel.

## 6. Donnees et persistance

Les tables metier du projet sont :

- `employees_source`
- `prediction_requests`
- `prediction_results`
- `api_audit_logs`

La logique de persistance est volontairement simple :

- une requete est creee en premier ;
- un resultat est cree si la prediction unitaire aboutit ;
- un ou plusieurs logs techniques peuvent etre associes a cette requete ;
- le batch et l'explication locale ne sont pas persistes, par choix d'architecture.

## 7. Environnements

Le projet formalise trois environnements :

- `development` pour le travail local ;
- `test` pour la CI et Pytest ;
- `production` pour les runtimes distants.

### Development

- cible recommandee : PostgreSQL local via Docker Compose ou Supabase DEV ;
- usage : developpement, demonstration, seed et verification SQL ;
- configuration attendue : `P5_ENVIRONMENT=development`.

### Test

- cible recommandee : PostgreSQL du job GitHub Actions pour les scripts, plus SQLite memoire dans certains tests rapides ;
- usage : execution automatisee du pipeline ;
- configuration attendue : `P5_ENVIRONMENT=test`.

### Production

- cible recommandee : PostgreSQL distant fourni via `P5_DATABASE_URL` ;
- usage : runtime du Space API et environnement demonstrable ;
- configuration attendue : `P5_ENVIRONMENT=production`.

Points importants :

- en production, `P5_DATABASE_URL` et `P5_API_KEY` sont obligatoires ;
- SQLite n'est plus la cible normale d'exploitation ;
- il ne reste qu'un filet de securite si aucun PostgreSQL distant n'est fourni.

## 8. Pipeline CI/CD

Le pipeline est maintenant clairement separe :

- `ci.yml` valide le code ;
- `cd.yml` deploie l'API ;
- `cd-portfolio.yml` deploie le portfolio.

```mermaid
sequenceDiagram
    participant DEV as Developpeur
    participant BR as Branches Git<br/>feature/* / develop / main
    participant CI as CI<br/>.github/workflows/ci.yml
    participant ENVDEV as GitHub Environment<br/>dev
    participant ENVPROD as GitHub Environment<br/>prod
    participant CDA as CD API<br/>.github/workflows/cd.yml
    participant CDP as CD Portfolio<br/>.github/workflows/cd-portfolio.yml
    participant HFDEV as HF Spaces DEV
    participant HFPROD as HF Spaces PROD

    DEV->>BR: Travail sur feature/*
    BR->>CI: Push / PR
    CI->>CI: Installer dependances
    CI->>CI: Demarrer PostgreSQL
    CI->>CI: create_db.py + seed_data.py
    CI->>CI: pytest --cov=app
    CI-->>BR: Validation technique

    DEV->>BR: Merge vers develop
    BR->>ENVDEV: Selection environnement dev
    ENVDEV->>CDA: Secrets/variables DEV
    ENVDEV->>CDP: Secrets/variables DEV
    CDA->>HFDEV: Deploiement Space API DEV
    CDP->>HFDEV: Deploiement Space Portfolio DEV

    DEV->>BR: Merge develop vers main
    BR->>ENVPROD: Selection environnement prod
    ENVPROD->>CDA: Secrets/variables PROD
    ENVPROD->>CDP: Secrets/variables PROD
    CDA->>HFPROD: Deploiement Space API PROD
    CDP->>HFPROD: Deploiement Space Portfolio PROD
```

Lecture :

- `feature/*` sert a la construction et aux PR ;
- `develop` valide l'environnement DEV ;
- `main` publie l'environnement PROD ;
- les workflows CD consomment les variables/secrets des environnements GitHub `dev` et `prod`.

## 9. Choix d'architecture

Cette architecture a ete retenue pour :

- garder une separation claire des responsabilites ;
- faciliter les tests ;
- eviter de dupliquer la logique du modele entre backend et frontend ;
- garder une base de reference locale solide tout en supportant un deploiement distant propre.

## 10. Reponse au besoin analytique du P5

L'architecture actuelle repond au besoin analytique du projet P5 car elle couvre un cycle complet :

- preparation et seed des donnees source ;
- prediction unitaire ;
- analyse batch ;
- explication locale ;
- persistance des appels unitaires ;
- visualisation via le portfolio Streamlit.

Les prolongements naturels, si le projet devait aller plus loin, seraient :

- l'historisation analytique des batchs ;
- des KPI RH agreges ;
- une retention/purge structuree des logs ;
- des migrations versionnees avec Alembic.
