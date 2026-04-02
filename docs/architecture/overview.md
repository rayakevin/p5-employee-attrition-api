# Architecture du projet

## 1. Vue d'ensemble

Le projet suit une architecture en couches simple et explicite :

- `api` : gestion HTTP, routage et codes de réponse ;
- `schemas` : validation Pydantic des contrats d'entrée et de sortie ;
- `services` : orchestration métier ;
- `ml` : preprocessing, chargement du modèle, scoring et explication locale ;
- `db` : persistance SQLAlchemy et modèles ORM ;
- `scripts` : initialisation de base, seed et export MLflow ;
- `ui` : portfolio Streamlit ;
- `tests` : tests unitaires, d'intégration et fonctionnels.

Documents complémentaires :

- [Documentation API](../api/README.md)
- [Documentation de la base de données](../db/README.md)
- [Documentation du modèle](../model/README.md)

## 2. Flux fonctionnel principal

Le système complet peut être résumé ainsi :

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

- le client peut être un appel PowerShell, Swagger ou le portfolio Streamlit ;
- l'API centralise la validation, le preprocessing et le scoring ;
- la persistance est réservée aux prédictions unitaires métier ;
- la base conserve la requête brute, le résultat et l'audit technique.

## 3. Démarrage local de l'API

En local, l'application est démarrée par :

```powershell
uv run uvicorn app.main:app --reload
```

Le démarrage suit la séquence suivante :

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

Ce schéma explique le passage entre une simple commande de terminal et un service HTTP exploitable localement.

## 4. Architecture de production

La production actuellement déployée se compose de deux Spaces Hugging Face et d'une base PostgreSQL distante :

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

Points clés :

- le portfolio n'embarque pas le modèle ;
- le Space API porte toute la logique métier ;
- la base distante de référence en ligne est PostgreSQL via Supabase ;
- les variables runtime des Spaces HF sont distinctes des variables GitHub du pipeline.

## 5. Flux de prédiction détaillé

Le flux métier est le suivant :

1. le client appelle `POST /api/v1/predict` ;
2. `PredictionInput` valide le payload ;
3. `prediction_service.get_prediction()` enregistre la requête ;
4. `build_model_features()` reconstruit les features du modèle final ;
5. `load_mlflow_model()` charge le modèle et sa metadata ;
6. `predict_attrition()` calcule le score puis la classe finale ;
7. le résultat est persisté en base ;
8. un log technique est écrit dans `api_audit_logs` ;
9. l'API renvoie une `PredictionOutput`.

Le portfolio Streamlit ne recalcule jamais le modèle lui-même : il appelle l'API via `P5_API_BASE_URL`. Cela garantit que l'interface affiche exactement le comportement du service réel.

## 6. Données et persistance

Les tables métier du projet sont :

- `employees_source`
- `prediction_requests`
- `prediction_results`
- `api_audit_logs`

La logique de persistance est volontairement simple :

- une requête est créée en premier ;
- un résultat est créé si la prédiction unitaire aboutit ;
- un ou plusieurs logs techniques peuvent être associés à cette requête ;
- le batch et l'explication locale ne sont pas persistés, par choix d'architecture.

## 7. Environnements

Le projet formalise trois environnements :

- `development` pour le travail local ;
- `test` pour la CI et Pytest ;
- `production` pour les runtimes distants.

### Development

- cible recommandée : PostgreSQL local via Docker Compose ou Supabase DEV ;
- usage : développement, démonstration, seed et vérification SQL ;
- configuration attendue : `P5_ENVIRONMENT=development`.

### Test

- cible recommandée : PostgreSQL du job GitHub Actions pour les scripts, plus SQLite mémoire dans certains tests rapides ;
- usage : exécution automatisée du pipeline ;
- configuration attendue : `P5_ENVIRONMENT=test`.

### Production

- cible recommandée : PostgreSQL distant fourni via `P5_DATABASE_URL` ;
- usage : runtime du Space API et environnement démontrable ;
- configuration attendue : `P5_ENVIRONMENT=production`.

Points importants :

- en production, `P5_DATABASE_URL` et `P5_API_KEY` sont obligatoires ;
- SQLite n'est plus la cible normale d'exploitation ;
- il ne reste qu'un filet de sécurité si aucun PostgreSQL distant n'est fourni.

## 8. Pipeline CI/CD

Le pipeline est maintenant clairement séparé :

- `ci.yml` valide le code ;
- `cd.yml` déploie l'API ;
- `cd-portfolio.yml` déploie le portfolio.

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

- `feature/*` sert à la construction et aux PR ;
- `develop` valide l'environnement DEV ;
- `main` publie l'environnement PROD ;
- les workflows CD consomment les variables/secrets des environnements GitHub `dev` et `prod`.

## 9. Choix d'architecture

Cette architecture a été retenue pour :

- garder une séparation claire des responsabilités ;
- faciliter les tests ;
- éviter de dupliquer la logique du modèle entre backend et frontend ;
- garder une base de référence locale solide tout en supportant un déploiement distant propre.

## 10. Réponse au besoin analytique du P5

L'architecture actuelle répond au besoin analytique du projet P5 car elle couvre un cycle complet :

- préparation et seed des données source ;
- prédiction unitaire ;
- analyse batch ;
- explication locale ;
- persistance des appels unitaires ;
- visualisation via le portfolio Streamlit.

Les prolongements naturels, si le projet devait aller plus loin, seraient :

- l'historisation analytique des batchs ;
- des KPI RH agrégés ;
- une rétention/purge structurée des logs ;
- des migrations versionnées avec Alembic.
