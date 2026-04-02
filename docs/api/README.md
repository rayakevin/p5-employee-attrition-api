# Documentation de l'API

## 1. Role de l'API

L'API FastAPI constitue le point d'entree unique du projet pour :

- valider les donnees metier envoyees par un client ;
- reconstruire les features attendues par le modele final ;
- executer la prediction, l'explication locale ou le batch ;
- tracer les appels unitaires en base ;
- exposer un contrat clair reutilisable par le portfolio Streamlit, les tests et un client externe.

Le code HTTP principal se trouve dans :

- [`app/api/v1/endpoints/predict.py`](../../app/api/v1/endpoints/predict.py)
- [`app/schemas/prediction.py`](../../app/schemas/prediction.py)
- [`app/services/prediction_service.py`](../../app/services/prediction_service.py)

## 2. Endpoints exposes

Les routes metier `POST` sont protegees par une cle d'API transmise dans l'en-tete `X-API-Key`.

### `GET /`

Route de presence minimale. Elle confirme que l'application FastAPI est demarree.

### `GET /health`

Route de supervision simple.

Usage :

- verifier que le service repond ;
- tester un deploiement local, Docker ou Hugging Face Spaces ;
- servir de point d'entree a un controle de disponibilite.

### `POST /api/v1/predict`

Route de prediction unitaire.

Sortie :

- `prediction` : classe finale, `0` ou `1` ;
- `score` : score brut du modele ;
- `threshold` : seuil de decision du modele ;
- `model_version` ;
- `model_name`.

Cette route ecrit aussi en base :

- la requete recue dans `prediction_requests` ;
- le resultat metier dans `prediction_results` ;
- un log technique dans `api_audit_logs`.

### `POST /api/v1/explain`

Route d'explication locale individuelle.

Elle reprend le meme payload que `/predict`, mais renvoie une decomposition additive du score :

- `base_value` ;
- `positive_sum` ;
- `negative_sum` ;
- `top_positive` ;
- `top_negative`.

Cette route ne persiste pas d'enregistrement supplementaire en base, car son objectif est l'analyse, pas la tracabilite metier.

### `POST /api/v1/predict/batch`

Route de scoring batch.

Entree :

- une liste `rows` de payloads conformes a `PredictionInput`.

Sortie :

- une liste de resultats `PredictionOutput`.

Cette route ne persiste pas les appels en base. Elle sert a l'exploration, au portfolio Streamlit et aux demonstrations, sans polluer la tracabilite technique avec des traitements de masse.

## 3. Contrat d'entree metier

Le contrat d'entree est defini dans [`app/schemas/prediction.py`](../../app/schemas/prediction.py).

Principes importants :

- les entrees sont exprimees en francais cote metier ;
- les valeurs categorielles attendues correspondent aux CSV bruts du projet ;
- certains alias historiques ou formats compatibles restent acceptes pour ne pas casser d'anciens appels.

Exemples de valeurs attendues :

- `genre` : `Homme`, `Femme`
- `statut_marital` : `Celibataire`, `Marie(e)`, `Divorce(e)`
- `departement` : `Commercial`, `Consulting`, `Ressources Humaines`
- `frequence_deplacement` : `Aucun`, `Frequent`, `Occasionnel`
- `heure_supplementaires` : `Oui`, `Non`

## 4. Sequence technique detaillee

### 4.1 Prediction unitaire : local ou runtime generique

```mermaid
sequenceDiagram
    participant C as Client<br/>PowerShell / Streamlit
    participant U as Uvicorn / FastAPI<br/>app/main.py
    participant S as Security<br/>app/core/security.py
    participant P as Pydantic<br/>app/schemas/prediction.py
    participant B as Service metier<br/>app/services/prediction_service.py
    participant F as Preprocessing<br/>app/ml/preprocess.py
    participant L as Loader MLflow<br/>app/ml/loader.py
    participant M as Predictor<br/>app/ml/predictor.py
    participant DB as PostgreSQL / Supabase<br/>app/db/session.py + app/db/models/tracking.py

    C->>U: POST /api/v1/predict + JSON + X-API-Key
    Note over C,U: Local : uv run uvicorn app.main:app --reload\nProd HF : Space API demarre via Dockerfile + uvicorn
    U->>S: Verifier la cle API
    S-->>U: OK / 401
    U->>P: Valider le payload PredictionInput
    P-->>U: OK / 422
    U->>B: get_prediction(payload)
    B->>DB: insert prediction_requests
    B->>F: build_model_features(payload)
    F-->>B: features pretes
    B->>L: load_mlflow_model()
    L-->>B: modele + metadata
    B->>M: predict_attrition(features)
    M-->>B: prediction + score + threshold + model_version
    B->>DB: insert prediction_results
    B->>DB: insert api_audit_logs
    B-->>U: resultat metier
    U-->>C: Reponse JSON

    Note over DB: Schema initialise par scripts/create_db.py\nDonnees source chargees par scripts/seed_data.py
    Note over L,M: Artefacts issus de scripts/export_model_to_mlflow.py\net stockes dans artifacts/model/
```

Lecture :

- l'authentification est verifiee avant toute logique metier ;
- la validation Pydantic arrete les payloads invalides avec `422` ;
- la persistance concerne seulement la prediction unitaire ;
- le service metier orchestre preprocessing, chargement du modele, scoring et audit.

### 4.2 Prediction et usage en production HF

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant PF as HF Space Portfolio PROD<br/>ui/streamlit_app.py
    participant API as HF Space API PROD<br/>app/main.py
    participant S as Security<br/>app/core/security.py
    participant P as Pydantic<br/>app/schemas/prediction.py
    participant B as Service metier<br/>app/services/prediction_service.py
    participant F as Preprocessing<br/>app/ml/preprocess.py
    participant L as Loader MLflow<br/>app/ml/loader.py
    participant M as Predictor<br/>app/ml/predictor.py
    participant DB as Supabase PostgreSQL PROD

    U->>PF: Saisie formulaire / upload CSV
    PF->>API: POST /predict ou /predict/batch ou /explain
    Note over PF,API: Appels HTTP avec P5_API_BASE_URL + X-API-Key
    API->>S: Verifier la cle API
    S-->>API: OK / 401
    API->>P: Valider le payload
    P-->>API: OK / 422
    API->>B: get_prediction(...) / get_batch_predictions(...) / get_prediction_explanation(...)
    B->>DB: insert prediction_requests (predict unitaire)
    B->>F: build_model_features(payload)
    F-->>B: features pretes
    B->>L: load_mlflow_model()
    L-->>B: modele + metadata
    B->>M: predict_attrition(features)
    M-->>B: prediction + score + threshold + version
    B->>DB: insert prediction_results (predict unitaire)
    B->>DB: insert api_audit_logs (predict unitaire)
    B-->>API: resultat metier
    API-->>PF: Reponse JSON
    PF-->>U: Visualisation resultat / explication / batch
```

Ce schema montre que le portfolio n'embarque ni le modele ni le preprocessing : il delegue toute la logique a l'API.

## 5. Gestion de la base de donnees

### Local

En local, le projet est pense pour fonctionner avec PostgreSQL via `P5_DATABASE_URL`.

Cette base sert a :

- la tracabilite des appels ;
- le stockage des donnees source dans `employees_source` ;
- les tests d'integration autour du flux complet.

### Production / Hugging Face Spaces

La cible effectivement deployee est un PostgreSQL distant fourni via `P5_DATABASE_URL` et heberge sur Supabase.

Points importants :

- en production, `P5_DATABASE_URL` et `P5_API_KEY` doivent etre fournis explicitement ;
- SQLite n'est plus la cible normale d'exploitation ;
- un fallback SQLite ne reste acceptable que pour un runtime de demonstration non configure.

## 6. Gestion des erreurs

Le comportement d'erreur suit la logique suivante :

- erreur de validation FastAPI : `422` ;
- erreur metier ou de validation complementaire : `400` ;
- authentification absente ou invalide : `401` ;
- route inexistante : `404` ;
- methode HTTP non supportee : `405` ;
- erreur interne : `500`.

Les tests fonctionnels couvrent explicitement `404`, `405`, `422` et le parcours nominal protege par cle d'API.

## 7. Authentification et secrets

Le projet implemente une authentification simple par cle d'API.

Choix retenu :

- adapte a un projet pedagogique ;
- simple a deployer sur FastAPI et Hugging Face Spaces ;
- visible dans la documentation OpenAPI ;
- facile a tester automatiquement.

Bonnes pratiques :

- stocker `P5_API_KEY` en variable d'environnement ;
- utiliser les secrets GitHub pour piloter le deploiement ;
- definir aussi les secrets et variables runtime directement dans les Spaces Hugging Face ;
- ne jamais committer une vraie cle de production ;
- separer autant que possible les secrets locaux, CI/CD et production.

## 8. Exemples d'utilisation

### Exemple de prediction unitaire

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
} | ConvertTo-Json -Depth 5 -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/predict" `
  -Headers @{ "X-API-Key" = $env:P5_API_KEY } `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))
```

### Exemple d'explication locale

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/explain" `
  -Headers @{ "X-API-Key" = $env:P5_API_KEY } `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))
```

### Exemple batch

```powershell
$batch = @{
    rows = @(
        (ConvertFrom-Json $payload)
    )
} | ConvertTo-Json -Depth 5 -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/predict/batch" `
  -Headers @{ "X-API-Key" = $env:P5_API_KEY } `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($batch))
```

## 9. Liens utiles

- Vue architecture : [`../architecture/overview.md`](../architecture/overview.md)
- Documentation BDD : [`../db/README.md`](../db/README.md)
- Preprocessing : [`../../app/ml/preprocess.py`](../../app/ml/preprocess.py)
- Chargement du modele : [`../../app/ml/loader.py`](../../app/ml/loader.py)
- Scoring : [`../../app/ml/predictor.py`](../../app/ml/predictor.py)
