# Architecture du projet

## 1. Vue d'ensemble

Le projet suit une architecture en couches simple, lisible et adaptée à une API de prédiction.

Les couches principales sont :

- `api` : gestion HTTP, routage et codes de réponse ;
- `schemas` : validation des contrats d'entrée et de sortie ;
- `services` : orchestration métier ;
- `ml` : chargement du modèle, preprocessing et calcul du score ;
- `db` : persistance SQLAlchemy et modèles ORM ;
- `scripts` : initialisation, export et seed ;
- `tests` : vérification du comportement.

Documents complémentaires :

- [Documentation API](../api/README.md)
- [Documentation de la base de données](../db/README.md)
- [Documentation du modèle](../model/README.md)

## 2. Flux de prédiction

1. le client appelle `/api/v1/predict` ;
2. `PredictionInput` valide le payload ;
3. `prediction_service.get_prediction()` enregistre la requête ;
4. `build_model_features()` reconstruit les features attendues par le modèle ;
5. `load_mlflow_model()` charge le modèle et sa metadata ;
6. `predict_attrition()` calcule le score puis la classe finale ;
7. le résultat est persisté en base ;
8. un log technique est conservé dans `api_audit_logs` ;
9. l'API renvoie une `PredictionOutput`.

Le portfolio Streamlit ne recalcule pas le modèle lui-même : il appelle l'API via `P5_API_BASE_URL`. Cela permet d'afficher dans l'interface exactement le comportement du service réel.

## 3. Flux base de données

Les tables métier du projet sont :

- `prediction_requests`
- `prediction_results`
- `api_audit_logs`
- `employees_source`

La logique de persistance est volontairement simple :

- une requête est créée en premier ;
- un résultat est créé si la prédiction aboutit ;
- un log est écrit dans tous les cas.

En local, la cible recommandée est PostgreSQL.

Sur Hugging Face Spaces, si `P5_DATABASE_URL` n'est pas fournie, l'API bascule automatiquement sur une base SQLite embarquée dans le conteneur. Cette base est stockée sur un chemin explicitement écrivable par le runtime du Space. Son rôle est de permettre à l'API de démarrer, de créer son schéma et de conserver une traçabilité minimale des appels unitaires.

Il faut toutefois bien distinguer ce fallback d'une vraie base métier :

- cette SQLite n'est pas pensée pour une persistance durable ;
- son contenu peut être perdu lors d'un rebuild, d'un redémarrage ou d'un redéploiement du Space ;
- elle ne remplace pas PostgreSQL pour un usage local sérieux, des tests d'intégration complets ou une exploitation stable ;
- elle sert surtout à éviter qu'un déploiement de démonstration distant échoue faute de base disponible.

Autrement dit, le projet repose sur deux logiques de persistance :

- PostgreSQL local comme référence technique du P5 ;
- SQLite conteneurisée comme solution de fonctionnement minimal sur Hugging Face Spaces.

## 4. Flux modèle

Le modèle est exporté avec MLflow puis chargé au runtime depuis `artifacts/model/`.

La metadata associée permet de conserver :

- le nom du modèle ;
- la version du modèle ;
- le seuil de décision ;
- la liste des features attendues ;
- la méthode de score attendue.

Le feature engineering ne dépend plus de la base de données pour fonctionner au runtime : les références utiles sont embarquées dans `artifacts/model/preprocessing_reference.json`.

## 5. Choix d'architecture

Cette architecture a été retenue pour :

- garder une séparation claire des responsabilités ;
- faciliter les tests ;
- pouvoir remplacer plus tard un composant sans réécrire tout le projet ;
- limiter la confusion entre logique HTTP, logique métier et logique modèle.

## 6. Réponse au besoin analytique du P5

L'architecture actuelle répond, à notre sens, au besoin analytique attendu dans le cadre du P5.

Pourquoi :

- elle structure un cycle complet de traitement de la donnée, depuis les sources brutes jusqu'au scoring ;
- elle formalise le stockage des données métier et des traces applicatives ;
- elle permet une analyse unitaire et une analyse batch ;
- elle propose une visualisation exploitable via le portfolio Streamlit.

Il ne s'agit pas encore d'une plateforme décisionnelle complète, mais d'un dispositif analytique cohérent avec le périmètre du projet : préparation des données, scoring, restitution, exploration et audit.

Les prolongements naturels, si le projet devait être poussé plus loin, seraient :

- l'historisation analytique des batchs ;
- la production de KPI RH agrégés ;
- l'ajout d'une base distante durable ;
- l'enrichissement du portfolio avec des indicateurs plus décisionnels.
