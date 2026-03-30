# Architecture du projet

## 1. Vue d'ensemble

Le projet suit une architecture en couches simple, lisible et adaptee a une API de prediction.

Les couches principales sont :

- `api` : gestion HTTP, routage et codes de reponse ;
- `schemas` : validation des contrats d'entree et de sortie ;
- `services` : orchestration metier ;
- `ml` : chargement du modele, preprocessing et calcul du score ;
- `db` : persistance SQLAlchemy et modeles ORM ;
- `scripts` : initialisation, export et seed ;
- `tests` : verification du comportement.

Documents complementaires :

- [Documentation API](../api/README.md)
- [Documentation du modele](../model/README.md)

## 2. Flux de prediction

1. le client appelle `/api/v1/predict`
2. `PredictionInput` valide le payload
3. `prediction_service.get_prediction()` enregistre la requete
4. `build_model_features()` reconstruit les features attendues par le modele
5. `load_mlflow_model()` charge le modele et sa metadata
6. `predict_attrition()` calcule le score puis la classe finale
7. le resultat est persisté en base
8. un log technique est conserve dans `api_audit_logs`
9. l'API renvoie une `PredictionOutput`

Le portfolio Streamlit ne recalcule pas le modele lui-meme : il appelle l'API via `P5_API_BASE_URL`. Cela permet d'afficher dans l'interface exactement le comportement du service reel.

## 3. Flux base de donnees

Les tables metier du projet sont :

- `prediction_requests`
- `prediction_results`
- `api_audit_logs`
- `employees_source`

La logique de persistance est volontairement simple :

- une requete est creee en premier ;
- un resultat est cree si la prediction aboutit ;
- un log est ecrit dans tous les cas.

En local, la cible recommandee est PostgreSQL.

Sur Hugging Face Spaces, si `P5_DATABASE_URL` n'est pas fournie, l'API utilise un fallback SQLite local au conteneur pour rester executable. Cette base sert au fonctionnement minimal et a la tracabilite simple, pas a une persistance metier durable.

## 4. Flux modele

Le modele est exporte avec MLflow puis charge au runtime depuis `artifacts/model/`.

La metadata associee permet de conserver :

- le nom du modele ;
- la version du modele ;
- le seuil de decision ;
- la liste des features attendues ;
- la methode de score attendue.

Le feature engineering ne depend plus de la base de donnees pour fonctionner au runtime : les references utiles sont embarquees dans `artifacts/model/preprocessing_reference.json`.

## 5. Choix d'architecture

Cette architecture a ete retenue pour :

- garder une separation claire des responsabilites ;
- faciliter les tests ;
- pouvoir remplacer plus tard un composant sans reecrire tout le projet ;
- limiter la confusion entre logique HTTP, logique metier et logique modele.
