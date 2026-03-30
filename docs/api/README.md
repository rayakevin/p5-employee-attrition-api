# Documentation de l'API

## 1. Rôle de l'API

L'API FastAPI constitue le point d'entrée unique du projet pour :

- valider les données métier envoyées par un client ;
- reconstruire les features attendues par le modèle final ;
- exécuter la prédiction ou l'explication locale ;
- tracer les appels unitaires en base ;
- exposer un contrat clair réutilisable par le portfolio Streamlit, les tests et un éventuel client externe.

Le code HTTP principal se trouve dans :

- [`app/api/v1/endpoints/predict.py`](../../app/api/v1/endpoints/predict.py)
- [`app/schemas/prediction.py`](../../app/schemas/prediction.py)
- [`app/services/prediction_service.py`](../../app/services/prediction_service.py)

## 2. Endpoints exposés

### `GET /`

Route de présence minimale. Elle confirme que l'application FastAPI est démarrée.

### `GET /health`

Route de supervision simple.

Usage :

- vérifier que le service répond ;
- tester un déploiement local, Docker ou Hugging Face Spaces ;
- servir de point d'entrée à un contrôle de disponibilité.

Réponse attendue :

```json
{
  "status": "ok"
}
```

### `POST /api/v1/predict`

Route de prédiction unitaire.

Entrée :

- un payload métier validé par `PredictionInput` ;
- des valeurs en français alignées sur les CSV bruts du projet.

Sortie :

- `prediction` : classe finale, `0` ou `1` ;
- `score` : score brut du modèle ;
- `threshold` : seuil de décision du modèle ;
- `model_version` ;
- `model_name`.

Cette route écrit aussi en base :

- la requête reçue dans `prediction_requests` ;
- le résultat métier dans `prediction_results` ;
- un log technique dans `api_audit_logs`.

### `POST /api/v1/explain`

Route d'explication locale individuelle.

Elle reprend exactement le même payload que `/predict`, mais renvoie une décomposition additive du score :

- `base_value` ;
- `positive_sum` ;
- `negative_sum` ;
- `top_positive` ;
- `top_negative`.

Cette route est utilisée en particulier par le portfolio Streamlit. Elle ne persiste pas d'enregistrement supplémentaire en base, car son objectif est l'analyse, pas la traçabilité métier.

### `POST /api/v1/predict/batch`

Route de scoring batch.

Entrée :

- une liste `rows` de payloads conformes à `PredictionInput`.

Sortie :

- une liste de résultats `PredictionOutput`.

Cette route ne persiste pas les appels en base. Elle sert à l'exploration, au portfolio Streamlit et aux démonstrations, sans polluer la traçabilité technique avec des traitements de masse.

## 3. Contrat d'entrée métier

Le contrat d'entrée est défini dans [`app/schemas/prediction.py`](../../app/schemas/prediction.py).

Quelques principes importants :

- les entrées sont exprimées en français côté métier ;
- les valeurs catégorielles attendues correspondent aux CSV bruts du projet ;
- certains alias historiques ou formats compatibles restent acceptés pour ne pas casser d'anciens appels.

Exemples de valeurs attendues :

- `genre` : `Homme`, `Femme`
- `statut_marital` : `Célibataire`, `Marié(e)`, `Divorcé(e)`
- `departement` : `Commercial`, `Consulting`, `Ressources Humaines`
- `frequence_deplacement` : `Aucun`, `Frequent`, `Occasionnel`
- `heure_supplementaires` : `Oui`, `Non`

## 4. Flux technique détaillé

### 4.1. Prédiction unitaire

1. FastAPI reçoit la requête HTTP.
2. `PredictionInput` valide et nettoie les données.
3. [`app/services/prediction_service.py`](../../app/services/prediction_service.py) crée un enregistrement de requête.
4. [`app/ml/preprocess.py`](../../app/ml/preprocess.py) reconstruit les features finales attendues par le modèle.
5. [`app/ml/predictor.py`](../../app/ml/predictor.py) charge le modèle MLflow et calcule le score.
6. Le score est comparé au seuil défini dans la metadata du modèle.
7. Le résultat est persisté.
8. Un audit log est écrit.
9. La réponse HTTP est renvoyée au client.

### 4.2. Explication locale

1. Le payload est validé comme pour une prédiction normale.
2. Le même preprocessing est appliqué.
3. [`app/ml/explainer.py`](../../app/ml/explainer.py) récupère le pipeline linéaire.
4. La `decision_function` est décomposée en contributions feature par feature.
5. L'API renvoie les variables qui augmentent et diminuent le plus le score.

### 4.3. Batch

1. Le client envoie une liste de lignes.
2. Chaque ligne est préprocessée puis scorée individuellement.
3. Les résultats sont renvoyés en liste.
4. Aucune persistance n'est effectuée.

## 5. Gestion de la base de données

### Local

En local, le projet est pensé pour fonctionner avec PostgreSQL via `P5_DATABASE_URL`.

Cette base sert à :

- la traçabilité des appels ;
- le stockage des données sources dans `employees_source` ;
- les tests d'intégration autour du flux complet.

### Hugging Face Spaces

Sur le Space API, si `P5_DATABASE_URL` n'est pas fournie, l'application utilise un fallback SQLite local au conteneur.

Point important :

- cette base SQLite sert uniquement à garder l'API fonctionnelle ;
- elle n'a pas vocation à remplacer une vraie base de persistance durable ;
- le feature engineering ne dépend plus de cette base.

## 6. Gestion des erreurs

Le comportement d'erreur suit la logique suivante :

- erreur métier ou de validation complémentaire : `400`
- erreur interne : `500`

Exemples :

- catégorie non supportée ;
- valeur binaire invalide ;
- problème de chargement du modèle ;
- erreur technique lors d'un appel base ou d'une prédiction.

## 7. Exemples d'utilisation

### Exemple de prédiction unitaire

```powershell
$payload = @{
    age = 35
    genre = "Homme"
    revenu_mensuel = 4500
    statut_marital = "Marié(e)"
    departement = "Consulting"
    poste = "Consultant"
    nombre_experiences_precedentes = 3
    annee_experience_totale = 12
    annees_dans_l_entreprise = 7
    annees_dans_le_poste_actuel = 4
    satisfaction_employee_environnement = 3
    note_evaluation_precedente = 3
    niveau_hierarchique_poste = 2
    satisfaction_employee_nature_travail = 4
    satisfaction_employee_equipe = 3
    satisfaction_employee_equilibre_pro_perso = 2
    note_evaluation_actuelle = 4
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

### Exemple d'explication locale

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/explain" `
  -ContentType "application/json" `
  -Body $payload
```

## 8. Points de vigilance

- Le portfolio Streamlit n'exécute pas le modèle lui-même : il passe par l'API.
- Le batch n'écrit pas en base par conception.
- Le score renvoyé est un score brut de modèle, pas une probabilité.
- La cohérence de l'API repose sur l'alignement strict entre :
  - schéma Pydantic ;
  - preprocessing ;
  - metadata MLflow ;
  - modèle exporté.
