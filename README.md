# P5 - API de prediction d'attrition des employes

## 1. Presentation du projet

Ce projet correspond a la mise en production d'un modele de machine learning construit dans le cadre du Projet 4, puis industrialise dans le cadre du Projet 5 du parcours OpenClassrooms.

L'objectif n'est pas seulement d'exposer un modele, mais de construire un systeme exploitable :

- une API FastAPI pour exposer la prediction ;
- une validation forte des entrees avec Pydantic ;
- un packaging du modele avec MLflow ;
- une base PostgreSQL pour la tracabilite ;
- des scripts d'initialisation et de seed ;
- une suite de tests ;
- une CI GitHub Actions ;
- un CD vers Hugging Face Spaces ;
- une documentation technique reutilisable.

## 2. Objectifs fonctionnels

L'application permet de :

- recevoir un profil employe sous forme de payload JSON ;
- reconstruire les variables attendues par le modele ;
- calculer une prediction d'attrition ;
- renvoyer une sortie contenant la prediction, le score, le seuil, le nom et la version du modele ;
- enregistrer en base la requete, le resultat et un log technique associe.

## 3. Architecture du projet

Le projet est structure autour de plusieurs couches :

- `app/api/` : endpoints HTTP et routage FastAPI ;
- `app/schemas/` : contrats d'entree et de sortie ;
- `app/services/` : orchestration metier de la prediction ;
- `app/ml/` : chargement du modele, preprocessing et calcul du score ;
- `app/db/` : configuration SQLAlchemy, sessions et modeles ORM ;
- `scripts/` : initialisation, export et seed ;
- `tests/` : tests unitaires et d'integration ;
- `artifacts/model/` : artefacts MLflow du modele ;
- `docs/` : documentation projet, mode operatoire et support de demonstration.

Flux de prediction :

1. l'API recoit un payload JSON ;
2. Pydantic valide les entrees ;
3. le service cree une trace de la requete ;
4. le preprocessing reconstruit les features du modele ;
5. le modele MLflow est charge ;
6. le score est calcule selon la methode declaree dans la metadata ;
7. la prediction est renvoyee ;
8. le resultat et le log technique sont persistés en base.

Documentation d'architecture complementaire :

- [`docs/architecture/overview.md`](docs/architecture/overview.md)
- [`docs/p5_trace.md`](docs/p5_trace.md)
- [`docs/p5_demo_exploitation.md`](docs/p5_demo_exploitation.md)

## 4. Choix techniques et justifications

### FastAPI

FastAPI a ete retenu pour :

- sa rapidite de mise en place ;
- la validation native avec Pydantic ;
- la clarte des schemas ;
- son adequation a une API de prediction.

### Pydantic

Pydantic sert a :

- valider les payloads entrants ;
- expliciter les types attendus ;
- refuser rapidement les donnees incoherentes.

### MLflow

MLflow est utilise pour :

- exporter le modele sous une forme standardisee ;
- conserver une metadata applicative associee ;
- decoupler l'entrainement du runtime de prediction.

### SQLAlchemy + PostgreSQL

Ce choix permet :

- de persister la tracabilite des predictions ;
- d'unifier l'acces base en local et en environnement distant ;
- de garder un modele de donnees explicite et testable.

### Docker

Docker est utilise pour :

- figer l'environnement de runtime ;
- tester localement un packaging proche du deploiement ;
- fournir une cible compatible avec Hugging Face Spaces.

### GitHub Actions

GitHub Actions permet :

- de securiser la qualite avec la CI ;
- de factoriser le deploiement vers Hugging Face Spaces ;
- de garder une trace automatique des validations.

## 5. Prerequis

Pour travailler localement sur le projet, il faut :

- Python `3.11`
- `uv`
- Docker Desktop
- Git

## 6. Installation locale

### 6.1 Cloner le projet

```powershell
git clone https://github.com/rayakevin/p5-employee-attrition-api.git
cd p5-employee-attrition-api
```

### 6.2 Installer l'environnement Python

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### 6.3 Variables de configuration

La configuration est centralisee via le prefixe `P5_`.

Variable principale :

```env
P5_DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition
```

Par defaut, l'application peut retomber sur SQLite pour un environnement minimal, mais le fonctionnement de reference du P5 repose sur PostgreSQL.

## 7. Lancement local avec PostgreSQL

### 7.1 Demarrer PostgreSQL

```powershell
docker compose up -d postgres
```

Point d'attention :

- si un PostgreSQL local utilise deja `5432`, le projet expose son conteneur sur `5433`.

### 7.2 Initialiser le schema et les donnees source

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

Explication :

- `scripts/create_db.py` cree les tables du projet ;
- `scripts/seed_data.py` charge les donnees source issues des fichiers CSV metier.

Un **script de seed** est un script qui peuple une base avec des donnees de depart utiles au fonctionnement ou aux demonstrations du projet.
Ici, il sert a charger `employees_source` a partir des trois extractions metier.

### 7.3 Demarrer l'API

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run uvicorn app.main:app --reload
```

### 7.4 Verifier que l'API repond

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

Reponse attendue :

```json
{"status":"ok"}
```

### 7.5 Arreter l'environnement

```powershell
docker compose down
```

## 8. Utilisation de l'API

### 8.1 Endpoints principaux

- `GET /`
- `GET /health`
- `POST /api/v1/predict`

### 8.2 Valeurs admissibles pour les champs categoriels et binaires

Les valeurs ci-dessous reprennent les libelles observes dans les CSV bruts du projet. C'est ce jeu de valeurs qu'il faut privilegier dans les appels a l'API.

- `genre` :
  - valeurs utilisateur conseillees : `Homme`, `Femme`
  - codes bruts egalement acceptes : `M`, `F`
- `statut_marital` :
  - `Célibataire`
  - `Marié(e)`
  - `Divorcé(e)`
- `departement` :
  - `Commercial`
  - `Consulting`
  - `Ressources Humaines`
- `poste` :
  - `Assistant de Direction`
  - `Cadre Commercial`
  - `Consultant`
  - `Directeur Technique`
  - `Manager`
  - `Représentant Commercial`
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
- `frequence_deplacement` :
  - `Aucun`
  - `Frequent`
  - `Occasionnel`
- `heure_supplementaires` :
  - valeurs conseillees : `Oui`, `Non`
  - formats historiques acceptes : `1`, `0`, `true`, `false`
- `ayant_enfants` :
  - valeurs conseillees : `Oui`, `Non`
  - codes sources egalement acceptes : `Y`, `N`

Le preprocessing conserve quelques alias anglais pour compatibilite ascendante, mais le contrat documentaire du projet repose sur ces libelles metier francises.

### 8.3 Exemple de payload en francais

```powershell
$payload = @{
    age = 35
    genre = "Homme"
    revenu_mensuel = 4500
    statut_marital = "Marié(e)"
    departement = "Consulting"
    poste = "Consultant"
    nombre_experiences_precedentes = 3
    nombre_heures_travailless = 40
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
    augementation_salaire_precedente = 12
    nombre_participation_pee = 1
    nb_formations_suivies = 3
    nombre_employee_sous_responsabilite = 0
    distance_domicile_travail = 12
    niveau_education = 3
    domaine_etude = "Infra & Cloud"
    ayant_enfants = "Oui"
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

Exemple de reponse attendue :

```json
{
  "prediction": 0,
  "score": -18.58866414724979,
  "threshold": 0.1138,
  "model_version": "0.1.0",
  "model_name": "linear_svc_attrition"
}
```

## 9. Base de donnees et tracabilite

Le projet persiste :

- `prediction_requests` : payload brut recu ;
- `prediction_results` : prediction calculee, score, seuil, version et nom du modele ;
- `api_audit_logs` : statut technique de l'appel ;
- `employees_source` : donnees source chargees depuis les CSV metier.

Cette partie est essentielle dans le P5, car elle montre que la prediction est integree dans un vrai flux applicatif et non seulement exposee en sortie console.

## 10. Tests

### 10.1 Lancer toute la suite

```powershell
uv run pytest -q
```

### 10.2 Ce que couvrent les tests

- validation de l'API ;
- schemas d'entree ;
- persistance en base ;
- seed des donnees source ;
- logique de score ;
- comportement de la prediction en cas de succes et d'erreur.

## 11. Lancement local avec Docker

### 11.1 Build et lancement

```powershell
docker compose up -d --build postgres api
```

### 11.2 Verification

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

### 11.3 Point d'attention

Si le volume PostgreSQL est vierge, il faut initialiser la base avant ou juste apres le demarrage du stack local :

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

## 12. CI/CD

### 12.1 CI

La CI GitHub Actions :

- installe les dependances ;
- lance PostgreSQL ;
- cree le schema ;
- seed les donnees ;
- execute les tests et la couverture.

Workflow :

- [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

### 12.2 CD

Le CD deploye le projet vers un Hugging Face Space Docker.

Il :

- valide le build Docker ;
- prepare le contenu compatible avec le Space ;
- pousse le depot vers Hugging Face.

Workflow :

- [`.github/workflows/cd.yml`](.github/workflows/cd.yml)

Configuration GitHub requise :

- secret `HF_TOKEN`
- variable `HF_USERNAME`
- variable `HF_SPACE_NAME`

Documentation de deploiement :

- [`deploy/huggingface/README.md`](deploy/huggingface/README.md)

## 13. Deploiement distant

Le deploiement distant retenu dans ce projet est Hugging Face Spaces en mode Docker.

Point important :

- le Space sert de preuve de deploiement distant ;
- la reference technique du P5 reste l'environnement local avec PostgreSQL ;
- les rebuilds Hugging Face peuvent etre longs, ce qui en fait une cible de demonstration plus qu'un environnement de boucle rapide.

Exemples de verification a distance :

```powershell
Invoke-RestMethod -Method Get -Uri "https://rayakevin-p5-employee-attrition-api.hf.space/"
Invoke-RestMethod -Method Get -Uri "https://rayakevin-p5-employee-attrition-api.hf.space/health"
```

## 14. Protocole de mise a jour reguliere

Le protocole de maintenance recommande est documente ici :

- [`docs/maintenance_protocol.md`](docs/maintenance_protocol.md)

En resume, a chaque mise a jour significative :

1. mettre a jour les dependances et verifier la compatibilite ;
2. relancer les tests ;
3. verifier la prediction locale ;
4. verifier la base ;
5. verifier le build Docker ;
6. verifier le deploiement distant ;
7. mettre a jour la documentation si le comportement ou l'architecture changent.

## 15. Documents utiles

- [`docs/p5_trace.md`](docs/p5_trace.md) : journal technique detaille et mode operatoire complet
- [`docs/p5_demo_exploitation.md`](docs/p5_demo_exploitation.md) : fiche courte de demonstration et d'exploitation
- [`docs/architecture/overview.md`](docs/architecture/overview.md) : vue d'architecture
- [`docs/maintenance_protocol.md`](docs/maintenance_protocol.md) : protocole de maintenance et de mise a jour

## 16. Conventions Git

### 16.1 Conventions de branches

- `feature/<sujet>` : ajout d'une fonctionnalite ou d'un bloc de travail principal
- `fix/<sujet>` : correction d'un bug fonctionnel ou technique
- `docs/<sujet>` : travail centre sur la documentation
- `chore/<sujet>` : maintenance, configuration, nettoyage, packaging
- `test/<sujet>` : ajout ou reprise de tests

### 16.2 Conventions de commits

- `feat:` : nouvelle fonctionnalite
- `fix:` : correction de bug
- `docs:` : documentation
- `chore:` : maintenance ou tache transversale
- `test:` : ajout ou adaptation de tests
- `ci:` : integration ou automatisation GitHub Actions

Exemples :

- `feat: implement prediction API with FastAPI and validation`
- `fix: initialize database schema on container startup`
- `docs: finalize project documentation and operating guides`
- `ci: add GitHub Actions workflows and initial API tests`

## 17. Dependances

### 17.1 `requirements.txt`

Ce fichier contient les dependances du projet pour le developpement, les tests et les usages complets.

Etat actuel :

- il est coherent avec le projet ;
- il contient bien les dependances necessaires a l'API, au modele, a la base, aux tests et a l'interface Streamlit.

### 17.2 `requirements.runtime.txt`

Ce fichier contient uniquement les dependances necessaires au conteneur de production.

Il est utilise par le `Dockerfile` pour alleger le runtime deploye.

## 18. Etat du projet

A date, le projet dispose :

- d'une API de prediction fonctionnelle ;
- d'un modele exporte via MLflow ;
- d'une persistance de tracabilite ;
- d'un environnement PostgreSQL local ;
- d'une suite de tests ;
- d'un packaging Docker ;
- d'une CI et d'un CD ;
- d'une documentation de projet exploitable.

## 19. Limites connues

- Hugging Face Spaces est fonctionnel mais lent a rebuild ;
- PostgreSQL local ne se transpose pas automatiquement sur le Space distant ;
- le deploiement distant est pertinent pour la demonstration, mais la validation technique de reference reste locale.

## 20. Auteurs et contexte

Projet realise dans le cadre du Projet 5 du parcours OpenClassrooms, avec un objectif pedagogique de mise en production d'un modele de machine learning dans un environnement structure, testable et documente.
