# Projet P5 - Mode Operatoire Complet et Retour d'Experience

## 1. Objet du document

Ce document est concu comme un mode operatoire reutilisable. L'idee n'est pas seulement de retracer ce qui a ete fait sur ce projet P5, mais d'en faire un guide pratique que l'on peut rouvrir plus tard pour remettre en production un autre modele de machine learning avec la meme logique de travail.

Le document s'appuie sur :

- le guide P5 ;
- l'etat reel du repository ;
- l'historique Git ;
- les erreurs effectivement rencontrees pendant le travail.

Il doit permettre de repondre a trois besoins :

1. Comprendre quoi faire, dans quel ordre, pour monter un projet similaire.
2. Comprendre pourquoi on fait les choses comme cela.
3. Anticiper les erreurs classiques, y compris celles que nous avons effectivement rencontrees.

## 2. Comment utiliser ce document plus tard

Ce document se lit comme un guide de mise en production progressif.

Pour chaque etape, on y trouve :

- l'objectif ;
- les commandes a lancer ;
- les fichiers a creer ou modifier ;
- l'explication des choix techniques ;
- les points de controle ;
- les erreurs rencontrees ou les pieges frequents.

La logique recommandee est de suivre les etapes dans l'ordre, puis d'utiliser :

- la section des erreurs pour le depannage ;
- la section des outils en fin de document comme aide-memoire ;
- la section d'ouverture pour envisager des variantes selon le type de modele ou de projet.

## 3. Vue d'ensemble du processus

Le processus global de mise en production suivi ici est le suivant :

1. Initialiser le projet et poser les conventions Git.
2. Structurer l'arborescence et l'environnement Python.
3. Mettre en place l'automatisation minimale CI/CD.
4. Construire l'API FastAPI avec validation des entrees.
5. Exporter le modele avec MLflow et le rendre exploitable par l'API.
6. Corriger les problemes de chargement, de preprocessing et de typage.
7. Documenter le projet et formaliser les actions.
8. Poser la couche base de donnees et preparer la tracabilite.
9. Brancher ensuite la persistance dans les endpoints.
10. Ajouter des tests d'integration sur le flux complet et sur le seed.
11. Charger les donnees source dans la base pour preparer la vraie couche PostgreSQL.

Sur ce projet, l'ordre reel des etapes a ete :

- etapes 1, 2, 3, 4 ;
- puis 6 et 7 ;
- puis 5 ;
- puis debut de l'etape base de donnees et tracabilite.

Cette difference est importante : en pratique, l'ordre reel d'un projet n'est pas toujours parfaitement lineaire. Il faut donc savoir revenir en arriere, corriger, stabiliser, puis reprendre la feuille de route.

## 4. Etape 1 - Initialiser le repository et definir les conventions

### Objectif

Partir d'un depot propre, lisible et professionnel.

### Commandes a lancer

```powershell
git clone https://github.com/<ton-compte>/p5-attrition-mlops-api.git
cd p5-attrition-mlops-api
code .
```

### Pourquoi ces commandes

- `git clone` recupere le depot localement.
- `cd` positionne le shell dans le projet.
- `code .` ouvre le projet dans VS Code, qui est pratique pour Python, Git, YAML, Docker et GitHub.

### Conventions Git a adopter

Conventions de branches :

- `feature/<sujet>`
- `fix/<sujet>`
- `docs/<sujet>`
- `refactor/<sujet>`

Convention de commits :

- `chore:` pour l'initialisation et la maintenance
- `ci:` pour la pipeline
- `feat:` pour les fonctionnalites
- `fix:` pour les corrections
- `docs:` pour la documentation
- `test:` pour les tests

### Exemples reels observes dans le projet

- `chore: initialize local project with uv and root configuration`
- `ci: add GitHub Actions workflows and initial API tests`
- `feat: implement prediction API with FastAPI and validation`
- `feat: add MLflow model export, prediction assets and project documentation`

### Point de controle

Avant d'aller plus loin, verifier :

- que le depot est bien clone ;
- que Git fonctionne ;
- que l'historique est lisible ;
- que la branche `main` existe ;
- que le workflow par branches sera respecte.

### Erreurs ou pieges frequents

- travailler directement sur `main` ;
- faire des commits vagues du type `update` ;
- ne pas definir les conventions des le depart.

## 5. Etape 2 - Initialiser l'environnement Python et l'arborescence

### Objectif

Disposer d'un environnement reproductible et d'une structure claire avant d'ecrire de vrai code metier.

### Commandes a lancer

```powershell
uv init
uv venv
.venv\Scripts\Activate.ps1
uv add fastapi uvicorn pydantic pydantic-settings sqlalchemy psycopg[binary] mlflow scikit-learn pandas numpy joblib python-dotenv pytest pytest-cov httpx mkdocs mkdocs-material streamlit
uv export --format requirements-txt > requirements.txt
mkdir -p .github/workflows app/api/v1/endpoints app/core app/db app/ml app/services scripts tests/unit tests/integration tests/functional docs ui data/raw data/processed data/samples artifacts/model artifacts/reports
```

### Pourquoi ces commandes

- `uv init` initialise le projet Python moderne.
- `uv venv` cree l'environnement virtuel.
- l'activation `.venv\Scripts\Activate.ps1` permet d'utiliser l'environnement en local.
- `uv add ...` installe toute la pile attendue pour le projet P5.
- `uv export ...` produit un `requirements.txt`, souvent demande explicitement.
- `mkdir -p ...` force une architecture claire des le depart.

### Fichiers structurants a obtenir

- `pyproject.toml`
- `requirements.txt`
- `.gitignore`
- `.dockerignore`
- `README.md`
- arborescence `app/`, `scripts/`, `tests/`, `docs/`, `ui/`, `data/`, `artifacts/`

### Pourquoi l'arborescence compte autant

Quand on repousse la structuration du projet, on finit souvent avec :

- du code metier melange a du code d'infrastructure ;
- des scripts difficiles a retrouver ;
- une documentation mal rangee ;
- un depot peu lisible pour un evaluateur ou un recruteur.

### Point de controle

Avant de continuer, verifier :

- que `pyproject.toml` contient bien les dependances ;
- que `requirements.txt` existe ;
- que l'environnement virtuel est fonctionnel ;
- que les dossiers principaux sont crees.

### Commits de reference observes

- `2238dde` `chore: initialize local project with uv and root configuration`
- `f0455fd` `chore: pin python version to 3.11 and stabilize project setup`
- `a409451` `chore: create project architecture and initialized uv project structure`

## 6. Etape 3 - Mettre en place CI/CD et le workflow de branches

### Objectif

Automatiser les verifications de base et imposer un workflow Git propre.

### Commandes a lancer

```powershell
git switch -c feature/ci-cd
```

### Fichiers a creer ou completer

- `.github/workflows/ci.yml`
- `.github/workflows/cd.yml`
- `.github/pull_request_template.md`

### Pourquoi cette etape arrive tot

Le guide insiste sur un point important : la tuyauterie CI/CD doit etre posee avant que le projet grossisse trop. Sinon :

- les tests arrivent trop tard ;
- les workflows sont ajoutes en urgence ;
- la qualite devient reactive au lieu d'etre preventive.

### Ce qui a ete observe dans le repository

Commits visibles :

- `a454aee` `ci: add GitHub Actions workflows and initial API tests`
- `d1e3d89` `ci: fix invalid GitHub Actions workflow definition`
- `cb566df` `ci: fix cd workflow with valid job placeholder`
- `46efde1` `ci: remove windows-specific dependency from requirements`
- `003e3ff` merge PR `feature/ci-cd`

### Ce qu'il faut retenir

Une pipeline n'est jamais parfaite du premier coup. Il est normal d'avoir des commits correctifs sur CI/CD. Ce qui compte, c'est :

- d'isoler ces corrections dans des commits clairs ;
- de ne pas les cacher dans un commit applicatif ;
- de conserver un historique explicite.

### Points de controle

- le workflow CI lance bien les tests ;
- le workflow CD est au moins structure ;
- la PR template existe ;
- les branches suivent la convention.

## 7. Etape 4 - Construire l'API FastAPI

### Objectif

Exposer un service de prediction lisible, documente et testable.

### Commande de depart

```powershell
git switch -c feature/api-fastapi
```

### Fichiers structurant l'API

- `app/main.py` ; voir [Annexe A](#annexe-a---appmainpy)
- `app/api/v1/router.py` ; voir [Annexe B](#annexe-b---appapiv1routerpy)
- `app/api/v1/endpoints/predict.py` ; voir [Annexe C](#annexe-c---appapiv1endpointspredictpy)
- `app/services/prediction_service.py` ; voir [Annexe E](#annexe-e---appservicesprediction_servicepy)
- `app/schemas/prediction.py` ; voir [Annexe D](#annexe-d---appschemaspredictionpy)
- `tests/unit/test_app.py`
- `tests/unit/test_predict.py`

### Logique de mise en oeuvre

#### `app/main.py`

Ce fichier doit rester simple. Son role est de :

- creer l'application FastAPI ;
- declarer le titre, la version et la description ;
- inclure les routes versionnees.

Pourquoi :

- plus `main.py` reste mince, plus l'application est lisible ;
- l'intelligence metier doit etre ailleurs.

#### `app/api/v1/endpoints/predict.py`

Ce fichier porte la responsabilite HTTP :

- recevoir le payload ;
- appeler le service ;
- transformer le resultat en reponse de schema ;
- gerer les erreurs avec des codes adaptes.

Pourquoi :

- on separe l'API du metier ;
- cela rend les tests plus simples.

#### `app/services/prediction_service.py`

Ce fichier orchestre :

- la preparation des features ;
- l'appel au modele.

Pourquoi :

- c'est la bonne couche pour brancher plus tard la persistance en base ;
- cela evite de surcharger le endpoint.

#### `app/schemas/prediction.py`

Ce fichier valide les entrees et sorties.

Pourquoi :

- le contrat d'API doit etre explicite ;
- les schemas deviennent aussi la base de la doc Swagger.

### Commit de reference observe

- `88426a5` `feat: implement prediction API with FastAPI and validation`

### Point de controle

Avant de passer a MLflow, il faut verifier :

- que l'API demarre ;
- que `/health` repond ;
- que `/predict` existe ;
- que les schemas sont stricts ;
- que les tests unitaires de base existent.

## 8. Etape 5 - Exporter le modele avec MLflow et le rendre exploitable

### Objectif

Passer d'un modele du P4 a un artefact versionnable, chargeable et exploitable dans l'API.

### Fichier cle

- `scripts/export_model_to_mlflow.py` ; voir [Annexe J](#annexe-j---scriptsexport_model_to_mlflowpy)

### Ce que ce script doit faire

1. Charger les donnees d'entrainement.
2. Reconstituer `X` et `y`.
3. Construire le pipeline de modele.
4. Entrainer le modele.
5. Inferer la signature d'entree/sortie.
6. Logger le modele dans MLflow.
7. Recuperer l'artefact exporte.
8. Le stabiliser dans `artifacts/model/current`.
9. Produire une metadata locale exploitable par l'API.

### Pourquoi MLflow est utile ici

MLflow ne sert pas uniquement a stocker un `pkl`. Il apporte :

- une signature de modele ;
- un environnement Python associe ;
- une structure d'artefact standard ;
- une meilleure lisibilite du packaging.

### Artefacts obtenus

Dans `artifacts/model/`, on retrouve notamment :

- `MLmodel`
- `model.pkl`
- `metadata.json`
- `requirements.txt`
- `python_env.yaml`
- `conda.yaml`
- `input_example.json`
- `serving_input_example.json`
- `preprocessing_reference.json`

### Pourquoi `metadata.json` est important

Ce fichier sert de pont entre :

- le monde MLflow ;
- et le monde applicatif de l'API.

Il y stocke par exemple :

- le nom du modele ;
- sa version ;
- le seuil de decision ;
- la liste des features ;
- le chemin local vers l'artefact.

### Commit de reference observe

- `43ebe7d` `feat: add MLflow model export, prediction assets and project documentation`

## 9. Etape 6 - Brancher le modele a l'API et corriger les erreurs reelles

Cette etape a ete particulierement importante, car elle montre ce qui se passe en pratique quand on branche un modele a une API : les erreurs ne sont pas seulement dans le modele, elles sont souvent dans le contrat entre toutes les couches.

### 9.1 Reproduire le probleme

Commandes executees :

```powershell
pytest -q
uv run pytest -q
uv run pytest tests/unit/test_predict.py -q -s
```

Pourquoi :

- il fallait partir du symptome reel, pas d'une supposition.

### 9.2 Erreur 1 : `pytest` non reconnu

Symptome :

- `pytest -q` ne fonctionne pas.

Cause :

- l'environnement du projet n'etait pas utilise.

Resolution :

- utiliser `uv run pytest -q`.

### 9.3 Erreur 2 : la configuration absorbe `DEBUG=release`

Symptome :

- les tests ne demarrent pas ;
- `Settings()` echoue car `debug` recoit une valeur non interpretable en booleen.

Cause :

- la machine possedait une variable globale `DEBUG=release` ;
- le projet lisait trop largement l'environnement.

Resolution :

- ajout de `env_prefix="P5_"` dans `app/core/config.py` ; voir [Annexe F](#annexe-f---appcoreconfigpy).

Pourquoi cette correction est propre :

- elle isole la configuration du projet ;
- elle evite les collisions avec l'environnement du poste de travail.

### 9.4 Erreur 3 : modele MLflow introuvable

Symptome :

- `/predict` renvoie 500 ;
- la metadata pointe vers `artifacts/model/current`, mais le dossier reel n'est pas conforme.

Cause :

- le script d'export et le loader ne partageaient plus la meme convention de stockage.

Resolution :

- rendre `app/ml/loader.py` tolerant ; voir [Annexe G](#annexe-g---appmlloaderpy)
- ajouter une resolution de chemin robuste ;
- corriger en parallele `scripts/export_model_to_mlflow.py` pour rendre l'export plus deterministe ; voir [Annexe J](#annexe-j---scriptsexport_model_to_mlflowpy).

### 9.5 Erreur 4 : incompatibilite de type sur `genre`

Symptome :

- le modele refuse la colonne `genre`.

Cause :

- l'API envoyait `Male` ou `Female` ;
- le modele attendait `0` ou `1`.

Resolution :

- ajout d'une normalisation explicite dans `app/ml/preprocess.py` ; voir [Annexe I](#annexe-i---appmlpreprocesspy).

### 9.6 Erreur 5 : incompatibilites de types numeriques

Symptome :

- certaines colonnes numeriques du payload ne matchent pas le schema MLflow.

Cause :

- les dtypes reels du dataset modele n'etaient pas reconstitues a l'identique.

Resolution :

- inspection explicite des types dans `df_MODEL.csv` ;
- cast final du DataFrame genere pour aligner les colonnes sur les types attendus ; voir [Annexe I](#annexe-i---appmlpreprocesspy).

### 9.7 Pourquoi cette etape est la plus formatrice

Elle montre que mettre un modele en production, ce n'est pas seulement "appeler `predict()`". Il faut aligner :

- le schema du payload API ;
- le preprocessing ;
- la metadata de modele ;
- les artefacts MLflow ;
- les types de colonnes ;
- la configuration runtime.

## 10. Etape 7 - Documenter, tester avant commit et committer proprement

### Objectif

Stabiliser l'etat du projet, produire une trace claire, puis committer avec un message conforme aux conventions.

### Commandes executees

```powershell
uv run pytest -q
git status --short
git diff --cached --stat
git commit -m "feat: add MLflow model export, prediction assets and project documentation"
```

### Pourquoi ces commandes

- `uv run pytest -q` est le minimum a executer avant commit ;
- `git status --short` permet de voir l'etat indexe ;
- `git diff --cached --stat` permet de verifier le perimetre reel du commit ;
- `git commit -m ...` cree un commit explicite et lisible.

### Pourquoi le message de commit est important

Un bon message :

- dit ce qu'on a ajoute ;
- reste coherént avec l'historique ;
- facilite la lecture future du projet ;
- prepare des PR plus claires.

### Point de controle

Avant commit :

- les tests passent ;
- on comprend ce qu'on commit ;
- le message est propre ;
- le commit ne melange pas plusieurs sujets sans lien.

## 11. Etape 8 - Poser la couche base de donnees et la tracabilite

### Objectif

Preparer la persistance des requetes et des resultats de prediction, sans encore casser le flux existant.

### Premiere decision importante : comment gerer les secrets

Question soulevee :

- comment gerer les mots de passe et informations sensibles comme l'URL de base ?

Decision prise :

- ne jamais ecrire d'identifiants en dur dans le code ;
- stocker l'URL de connexion dans `P5_DATABASE_URL` ;
- utiliser une valeur par defaut locale non sensible pour le travail initial, ici une base SQLite locale ;
- ne jamais logger la chaine complete de connexion.

Pourquoi ce choix est bon :

- il respecte les bonnes pratiques ;
- il reste simple a expliquer ;
- il prepare la transition future vers PostgreSQL sans introduire de secret dans Git.

### Commande de depart

```powershell
git switch -c feature/postgres-tracking
```

### Fichiers a creer ou modifier

- `app/core/config.py` ; voir [Annexe F](#annexe-f---appcoreconfigpy)
- `app/db/base.py` ; voir [Annexe K](#annexe-k---appdbbasepy)
- `app/db/session.py` ; voir [Annexe L](#annexe-l---appdbsessionpy)
- `app/db/models/tracking.py` ; voir [Annexe M](#annexe-m---appdbmodelstrackingpy)
- `app/db/models/__init__.py`
- `scripts/create_db.py` ; voir [Annexe N](#annexe-n---scriptscreate_dbpy)

### Role de chaque fichier

#### `app/core/config.py`

But :

- ajouter `database_url`.

Pourquoi :

- la base doit etre configurable par environnement ;
- la valeur ne doit pas etre codee en dur ailleurs.

#### `app/db/base.py`

But :

- definir la base declarative SQLAlchemy.

Pourquoi :

- tous les modeles ORM doivent partager la meme `metadata`.

#### `app/db/session.py`

But :

- creer l'engine SQLAlchemy ;
- definir `SessionLocal` ;
- preparer `get_db()`.

Pourquoi :

- on centralise la connexion et la creation de sessions ;
- on prepare l'injection future dans FastAPI.

#### `app/db/models/tracking.py`

But :

- definir les tables :
  - `prediction_requests`
  - `prediction_results`
  - `api_audit_logs`

Pourquoi :

- tracer la requete ;
- tracer le resultat produit ;
- tracer les evenements techniques.

#### `scripts/create_db.py`

But :

- creer physiquement les tables a partir des modeles SQLAlchemy.

### Commande de verification

```powershell
uv run python scripts/create_db.py
```

### Erreur reelle rencontree

Symptome :

- `ModuleNotFoundError: No module named 'app'`

Cause :

- le script est lance depuis `scripts/` et ne retrouve pas automatiquement la racine du projet.

Resolution :

- ajout d'un bootstrap `PROJECT_ROOT` dans `sys.path`.

### Verification de non-regression

Commande executee :

```powershell
uv run pytest -q
```

Resultat :

- les 5 tests existants passent encore.

### Ce qu'il reste a faire juste apres

- brancher effectivement la base dans `/predict` ;
- enregistrer une ligne dans `prediction_requests` ;
- enregistrer une ligne dans `prediction_results` ;
- enregistrer les erreurs techniques dans `api_audit_logs` ;
- ajouter les tests d'integration associes.

## 12. Liste de controle reutilisable avant mise en production d'un autre modele

Quand tu reutiliseras ce guide plus tard, voici l'ordre court a suivre :

1. Initialiser le repo et les conventions Git.
2. Initialiser `uv`, l'environnement virtuel et l'arborescence.
3. Poser CI/CD tres tot.
4. Construire une API mince et bien validee.
5. Exporter le modele dans un format standard, ici MLflow.
6. Verifier la coherence entre payload API, preprocessing et schema du modele.
7. Ecrire des tests simples puis relancer les tests apres chaque bloc.
8. Documenter ce qui est fait avant d'oublier.
9. Poser la couche de persistance et de tracabilite.
10. Brancher la persistance seulement quand la structure ORM est propre.

## 13. Erreurs frequentes a anticiper sur un autre projet

### 13.1 Variables d'environnement parasites

Exemple :

- `DEBUG`, `DATABASE_URL` ou `PORT` deja definies sur la machine.

Reflexe :

- utiliser un prefixe projet ;
- verifier la config des le debut.

### 13.2 Drift entre entrainement et inference

Exemple :

- le notebook prepare les donnees d'une facon que l'API ne reproduit pas.

Reflexe :

- centraliser les mappings ;
- preferer une pipeline serialisee la plus complete possible.

### 13.3 Artefact de modele mal package

Exemple :

- le chemin de modele annonce n'est pas le bon ;
- l'artefact ne contient pas tout ce qu'attend l'API.

Reflexe :

- verifier les artefacts juste apres export ;
- ne pas supposer la structure des dossiers.

### 13.4 Type mismatch en inference

Exemple :

- le payload est "logiquement correct" mais les types ne matchent pas le schema attendu.

Reflexe :

- verifier les dtypes reels du dataset d'entrainement ;
- caster explicitement si necessaire.

### 13.5 Script d'administration non executable

Exemple :

- un script comme `create_db.py` fonctionne dans l'IDE mais pas depuis le terminal.

Reflexe :

- le tester comme un vrai outil CLI des sa creation.

## 14. Aide-memoire des outils utilises

### 14.1 Git et GitHub

A quoi ca sert ici :

- versionner le code ;
- travailler en branches ;
- faire des PR ;
- garder un historique lisible.

Ce qu'on a utilise :

- `git switch -c ...`
- `git status`
- `git log`
- commits prefixees
- merges de PR

Ce qu'on pourrait reutiliser plus tard :

- tags de release ;
- protections de branches ;
- templates d'issues ;
- revues de code plus formalisees.

### 14.2 uv

A quoi ca sert ici :

- initialiser le projet Python ;
- gerer l'environnement ;
- executer les commandes Python et Pytest dans le bon contexte.

Ce qu'on a utilise :

- `uv init`
- `uv venv`
- `uv add`
- `uv run pytest`
- `uv run python`

### 14.3 FastAPI

A quoi ca sert ici :

- exposer l'API de prediction ;
- documenter le contrat via Swagger/OpenAPI.

Ce qu'on a utilise :

- `FastAPI(...)`
- router versionne ;
- endpoint `/predict`
- endpoint `/health`

Ce qu'on n'a pas encore utilise mais qui peut servir :

- middleware ;
- securite par header ;
- dependencies avancees ;
- endpoints batch ;
- endpoint `/model/info`.

### 14.4 Pydantic et Pydantic Settings

A quoi ca sert ici :

- valider les payloads ;
- typer les reponses ;
- gerer la config par environnement.

Ce qu'on a utilise :

- `BaseModel`
- `Field`
- `field_validator`
- `BaseSettings`
- `SettingsConfigDict`

### 14.5 scikit-learn

A quoi ca sert ici :

- construire la pipeline de prediction ;
- standardiser les donnees ;
- entrainer le classifieur.

Ce qu'on a utilise :

- `Pipeline`
- `StandardScaler`
- `LinearSVC`

Ce qu'on pourrait utiliser plus tard :

- `ColumnTransformer`
- `OneHotEncoder`
- `LogisticRegression`
- calibration
- model selection

### 14.6 MLflow

A quoi ca sert ici :

- tracer le modele ;
- emballer l'artefact ;
- charger le modele proprement.

Ce qu'on a utilise :

- experiment
- run
- `log_model`
- `infer_signature`
- `download_artifacts`
- `pyfunc.load_model`

Ce qu'on pourrait utiliser plus tard :

- registry distant ;
- aliases ou stages ;
- serving natif ;
- comparaison d'experiences.

### 14.7 Pandas

A quoi ca sert ici :

- lire les datasets ;
- fabriquer le DataFrame de prediction ;
- inspecter les types et les categories.

Ce qu'on a utilise :

- `read_csv`
- `DataFrame`
- `astype`

### 14.8 SQLAlchemy

A quoi ca sert ici :

- decrire le schema ORM ;
- centraliser la metadata ;
- creer l'engine et les sessions.

Ce qu'on a utilise :

- `DeclarativeBase`
- `create_engine`
- `sessionmaker`
- `Mapped`
- `mapped_column`
- `relationship`
- `metadata.create_all`

Ce qu'on pourrait utiliser plus tard :

- Alembic ;
- transactions metier plus poussees ;
- requetes complexes ;
- patterns repository.

### 14.9 psycopg

A quoi ca sert ici :

- fournir le driver PostgreSQL cible pour SQLAlchemy.

Ce qu'on a utilise :

- la dependance `psycopg[binary]`
- la compatibilite avec `postgresql+psycopg://...`

### 14.10 Pytest

A quoi ca sert ici :

- tester l'application ;
- verifier la non-regression.

Ce qu'on a utilise :

- tests unitaires
- `TestClient`
- execution globale
- execution ciblee

Ce qu'on pourrait utiliser plus tard :

- tests d'integration base de donnees ;
- couverture plus detaillee ;
- parametrisation ;
- fixtures plus riches.

## 15. Ouvertures et variantes possibles

### 15.1 Si le modele n'est pas un `LinearSVC`

Pour un autre type de modele, la logique reste la meme :

- pipeline ;
- export ;
- metadata ;
- chargement ;
- contrat d'API ;
- tests ;
- persistance.

Ce qui change :

- la maniere de calculer le score ;
- la notion de probabilite ou non ;
- les besoins d'explicabilite ;
- les besoins de preprocessing.

### 15.2 Si le modele inclut deja tout le preprocessing

C'est souvent preferable :

- moins de logique reimplementee dans l'API ;
- moins de risque de divergence.

### 15.3 Si le projet doit etre plus industriel

On peut aller plus loin avec :

- Docker strict ;
- deploiement cloud ;
- Alembic ;
- observabilite ;
- monitoring de derive ;
- API securisee ;
- registry de modele distant ;
- separation API et UI en services distincts.

### 15.4 Si le projet est plus simple

Pour un projet moins ambitieux, on peut aussi simplifier :

- pas de base au debut ;
- pas de CI/CD complet ;
- un seul endpoint ;
- un seul script d'export ;
- documentation minimale mais propre.

L'important est de garder la logique de separation des responsabilites :

- configuration ;
- API ;
- service ;
- modele ;
- persistence ;
- tests ;
- documentation.

## 16. Conclusion

Le projet P5 montre qu'une mise en production de modele n'est pas un simple emballage d'un notebook. Il faut construire un systeme coherent.

Ce qui est deja stabilise :

- la structure du projet ;
- le workflow Git ;
- la couche API ;
- le packaging MLflow ;
- le preprocessing d'inference ;
- les tests unitaires existants ;
- la base ORM initiale pour la tracabilite.

Ce qui a ete le plus instructif :

- les erreurs sont venues de l'interface entre les couches ;
- la configuration, le chemin d'artefact, le typage et le preprocessing sont aussi importants que le modele lui-meme ;
- il faut documenter au fur et a mesure, sinon on oublie tres vite pourquoi certaines decisions ont ete prises.

Si tu rouvres ce document dans 6 mois, la bonne facon de l'utiliser est simple :

1. reprendre les etapes dans l'ordre ;
2. relire la section erreurs avant de commencer ;
3. utiliser le memo outils comme aide-memoire ;
4. adapter la partie "ouvertures" au type de modele que tu devras deployer.

Le prochain bloc logique sur ce projet est :

- brancher la persistance SQLAlchemy a `/predict` ;
- enregistrer les requetes, resultats et logs techniques ;
- ajouter les tests d'integration qui valident cette tracabilite.

## 17. Annexes code

Cette annexe regroupe le code des fichiers qui portent la logique actuelle du projet. Les liens internes places dans les etapes precedentes pointent vers ces sections afin que, lors d'un export en PDF, on puisse naviguer directement du process vers le code concerne.

### Table des annexes

- [Annexe A - `app/main.py`](#annexe-a---appmainpy)
- [Annexe B - `app/api/v1/router.py`](#annexe-b---appapiv1routerpy)
- [Annexe C - `app/api/v1/endpoints/predict.py`](#annexe-c---appapiv1endpointspredictpy)
- [Annexe D - `app/schemas/prediction.py`](#annexe-d---appschemaspredictionpy)
- [Annexe E - `app/services/prediction_service.py`](#annexe-e---appservicesprediction_servicepy)
- [Annexe F - `app/core/config.py`](#annexe-f---appcoreconfigpy)
- [Annexe G - `app/ml/loader.py`](#annexe-g---appmlloaderpy)
- [Annexe H - `app/ml/predictor.py`](#annexe-h---appmlpredictorpy)
- [Annexe I - `app/ml/preprocess.py`](#annexe-i---appmlpreprocesspy)
- [Annexe J - `scripts/export_model_to_mlflow.py`](#annexe-j---scriptsexport_model_to_mlflowpy)
- [Annexe K - `app/db/base.py`](#annexe-k---appdbbasepy)
- [Annexe L - `app/db/session.py`](#annexe-l---appdbsessionpy)
- [Annexe M - `app/db/models/tracking.py`](#annexe-m---appdbmodelstrackingpy)
- [Annexe N - `scripts/create_db.py`](#annexe-n---scriptscreate_dbpy)

### Annexe A - `app/main.py`

```python
"""Point d'entree principal de l'API FastAPI.

Ce module instancie l'application, branche le routeur versionne et expose
des endpoints simples de disponibilite. L'objectif est de garder ici un
code tres mince : la logique HTTP complexe reste dans les endpoints, et la
logique metier dans les services.
"""

from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="Employee Attrition Prediction API",
    version="0.1.0",
    description="API for employee attrition prediction"
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """Retourne un message simple pour verifier que l'application repond."""
    return {"message": "API is running"}


@app.get("/health")
def health():
    """Retourne un statut minimal de sante du service."""
    return {"status": "ok"}
```

### Annexe B - `app/api/v1/router.py`

```python
"""Aggregation des routes de l'API versionnee.

Ce module centralise l'enregistrement des endpoints de la version `v1`.
Il permet de faire evoluer l'API par version sans melanger toutes les
routes dans `main.py`.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import predict

api_router = APIRouter()

# Chaque sous-route apporte sa propre responsabilite metier.
api_router.include_router(predict.router, tags=["Prediction"])
```

### Annexe C - `app/api/v1/endpoints/predict.py`

```python
from __future__ import annotations

"""Endpoint HTTP de prediction.

Ce module transforme un appel API en appel metier. Il valide l'entree via
Pydantic, delegue la preparation des features et la prediction au service,
puis reconstruit une reponse typee.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.prediction_service import get_prediction

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput) -> PredictionOutput:
    """Execute une prediction unitaire a partir d'un payload metier."""
    try:
        result = get_prediction(data.model_dump())
        return PredictionOutput(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de la prediction : {exc}",
        ) from exc
```

### Annexe D - `app/schemas/prediction.py`

```python
from __future__ import annotations

"""Schemas Pydantic de l'API de prediction."""

from pydantic import BaseModel, Field, field_validator


class PredictionInput(BaseModel):
    """Decrit le payload metier attendu pour une prediction unitaire."""

    age: int = Field(..., ge=16, le=100, description="Age de l'employe")
    genre: str = Field(..., description="Genre de l'employe")
    revenu_mensuel: float = Field(..., gt=0, description="Revenu mensuel brut")
    statut_marital: str = Field(..., description="Statut marital")
    departement: str = Field(..., description="Departement")
    poste: str = Field(..., description="Poste")
    nombre_experiences_precedentes: int = Field(..., ge=0, le=50)
    nombre_heures_travailless: float = Field(..., ge=0, le=100)
    annee_experience_totale: float = Field(..., ge=0, le=80)
    annees_dans_l_entreprise: float = Field(..., ge=0, le=80)
    annees_dans_le_poste_actuel: float = Field(..., ge=0, le=80)
    satisfaction_employee_environnement: int = Field(..., ge=1, le=4)
    note_evaluation_precedente: float = Field(..., ge=1, le=5)
    niveau_hierarchique_poste: int = Field(..., ge=1, le=10)
    satisfaction_employee_nature_travail: int = Field(..., ge=1, le=4)
    satisfaction_employee_equipe: int = Field(..., ge=1, le=4)
    satisfaction_employee_equilibre_pro_perso: int = Field(..., ge=1, le=4)
    note_evaluation_actuelle: float = Field(..., ge=1, le=5)
    heure_supplementaires: int = Field(..., ge=0, le=1)
    augementation_salaire_precedente: float = Field(..., ge=0, le=100)
    nombre_participation_pee: int = Field(..., ge=0, le=20)
    nb_formations_suivies: int = Field(..., ge=0, le=50)
    nombre_employee_sous_responsabilite: int = Field(..., ge=0, le=500)
    distance_domicile_travail: float = Field(..., ge=0, le=500)
    niveau_education: int = Field(..., ge=1, le=10)
    domaine_etude: str = Field(..., description="Domaine d'etude")
    ayant_enfants: int = Field(..., ge=0, le=1)
    frequence_deplacement: str = Field(..., description="Frequence de deplacement")
    annees_depuis_la_derniere_promotion: float = Field(..., ge=0, le=80)
    annes_sous_responsable_actuel: float = Field(..., ge=0, le=80)
    
    @field_validator(
        "genre",
        "statut_marital",
        "departement",
        "poste",
        "domaine_etude",
        "frequence_deplacement",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value: str) -> str:
        """Nettoie les chaines metier avant validation approfondie."""
        if not isinstance(value, str):
            raise TypeError("La valeur doit etre une chaine de caracteres.")
        value = value.strip()
        if not value:
            raise ValueError("La valeur ne peut pas etre vide.")
        return value


class PredictionOutput(BaseModel):
    """Decrit la reponse metier renvoyee par l'API de prediction."""

    prediction: int = Field(..., description="Classe predite : 0 ou 1")
    score: float = Field(..., description="Score brut du modele")
    threshold: float = Field(..., description="Seuil de decision applique")
    model_version: str = Field(..., description="Version du modele")
    model_name: str = Field(..., description="Nom du modele")
```

### Annexe E - `app/services/prediction_service.py`

```python
from __future__ import annotations

"""Orchestration metier de la prediction."""

from app.ml.predictor import predict_attrition
from app.ml.preprocess import build_model_features


def get_prediction(payload: dict) -> dict:
    """Construit les features puis renvoie le resultat de prediction."""
    model_input = build_model_features(payload)
    return predict_attrition(model_input)
```

### Annexe F - `app/core/config.py`

```python
"""Configuration centralisee de l'application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Decrit les parametres de configuration attendus par l'application."""

    app_name: str = "Employee Attrition Prediction API"
    environment: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./p5_attrition.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="P5_",
    )


settings = Settings()
```

### Annexe G - `app/ml/loader.py`

```python
from __future__ import annotations

"""Chargement de la metadata et du modele MLflow."""

import json
from pathlib import Path

import mlflow.pyfunc

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "model"
METADATA_PATH = ARTIFACTS_DIR / "metadata.json"


def load_model_metadata() -> dict:
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_model_path(model_uri: str) -> Path:
    model_path = Path(model_uri)
    if model_path.exists():
        return model_path

    for candidate in (ARTIFACTS_DIR, ARTIFACTS_DIR / "current"):
        if (candidate / "MLmodel").exists():
            return candidate

    raise FileNotFoundError(
        f"Le modele MLflow local est introuvable a l'emplacement : {model_uri}"
    )


def load_mlflow_model():
    metadata = load_model_metadata()
    model_path = resolve_model_path(metadata["mlflow_model_uri"])
    metadata["mlflow_model_uri"] = str(model_path.resolve())

    model = mlflow.pyfunc.load_model(str(model_path))
    return model, metadata
```

### Annexe H - `app/ml/predictor.py`

```python
from __future__ import annotations

"""Prediction metier a partir du modele MLflow charge."""

import pandas as pd

from app.ml.loader import load_mlflow_model

_MODEL = None
_MODEL_METADATA = None


def get_loaded_model():
    global _MODEL, _MODEL_METADATA

    if _MODEL is None or _MODEL_METADATA is None:
        _MODEL, _MODEL_METADATA = load_mlflow_model()

    return _MODEL, _MODEL_METADATA


def predict_attrition(model_input: pd.DataFrame) -> dict:
    model, metadata = get_loaded_model()
    threshold = metadata["threshold"]

    raw_pred = model.predict(model_input)
    score = float(raw_pred[0])
    prediction = int(score >= threshold)

    return {
        "prediction": prediction,
        "score": score,
        "threshold": threshold,
        "model_version": metadata["model_version"],
        "model_name": metadata["model_name"],
    }
```

### Annexe I - `app/ml/preprocess.py`

```python
from __future__ import annotations

"""Preparation des features avant l'appel au modele."""

import json
import math
from pathlib import Path

import pandas as pd

from app.ml.loader import load_model_metadata

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "model"
PREPROCESSING_REFERENCE_PATH = ARTIFACTS_DIR / "preprocessing_reference.json"

GENRE_MAPPING = {"M": 1, "MALE": 1, "HOMME": 1, "F": 0, "FEMALE": 0, "FEMME": 0}
STATUT_MARITAL_MAPPING = {
    "SINGLE": "Celibataire",
    "CELIBATAIRE": "Celibataire",
    "MARRIED": "Marie(e)",
    "MARIE(E)": "Marie(e)",
    "DIVORCED": "Divorce(e)",
    "DIVORCE(E)": "Divorce(e)",
}
DEPARTEMENT_MAPPING = {
    "SALES": "Commercial",
    "RESEARCH & DEVELOPMENT": "Consulting",
    "HUMAN RESOURCES": "Ressources Humaines",
}
FREQUENCE_DEPLACEMENT_MAPPING = {
    "NON-TRAVEL": "Aucun",
    "TRAVEL_FREQUENTLY": "Frequent",
    "TRAVEL_RARELY": "Occasionnel",
}
POSTE_MAPPING = {
    "SALES EXECUTIVE": "Cadre Commercial",
    "MANAGER": "Manager",
    "RESEARCH SCIENTIST": "Autre",
    "LABORATORY TECHNICIAN": "Tech Lead",
    "HUMAN RESOURCES": "Autre",
    "HEALTHCARE REPRESENTATIVE": "Autre",
    "MANUFACTURING DIRECTOR": "Manager",
    "SALES REPRESENTATIVE": "Cadre Commercial",
    "RESEARCH DIRECTOR": "Senior Manager",
}
DOMAINE_ETUDE_MAPPING = {
    "LIFE SCIENCES": "Autre",
    "MEDICAL": "Autre",
    "MARKETING": "Marketing",
    "TECHNICAL DEGREE": "Infra & Cloud",
    "HUMAN RESOURCES": "Autre",
    "OTHER": "Autre",
}
```

Suite de l'annexe I :

```python
def safe_log1p(value: float) -> float:
    return math.log1p(max(value, 0.0))


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def load_preprocessing_reference() -> dict:
    if PREPROCESSING_REFERENCE_PATH.exists():
        with open(PREPROCESSING_REFERENCE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "poste_mapping": {},
        "domaine_etude_mapping": {},
        "mediane_revenu_par_niveau": {},
        "mediane_revenu_par_poste_regroupe": {},
    }


def regroup_poste(raw_poste: str, poste_mapping: dict[str, str]) -> str:
    mapped_poste = poste_mapping.get(raw_poste, raw_poste)
    return POSTE_MAPPING.get(mapped_poste.strip().upper(), mapped_poste)


def regroup_domaine_etude(raw_domain: str, domain_mapping: dict[str, str]) -> str:
    mapped_domain = domain_mapping.get(raw_domain, raw_domain)
    return DOMAINE_ETUDE_MAPPING.get(mapped_domain.strip().upper(), mapped_domain)


def normalize_string_category(value: str, mapping: dict[str, str]) -> str:
    return mapping.get(value.strip().upper(), value.strip())


def normalize_genre(value: str | int) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    normalized = GENRE_MAPPING.get(value.strip().upper())
    if normalized is None:
        raise ValueError(f"Genre non supporte pour la prediction: {value}")
    return normalized
```

Suite finale de l'annexe I :

```python
def compute_distance_class(distance: float) -> int:
    if distance < 10:
        return 0
    if distance < 30:
        return 1
    return 2


def build_model_features(payload: dict) -> pd.DataFrame:
    metadata = load_model_metadata()
    expected_features: list[str] = metadata["feature_names"]

    refs = load_preprocessing_reference()
    poste_mapping = refs.get("poste_mapping", {})
    domaine_mapping = refs.get("domaine_etude_mapping", {})
    mediane_revenu_par_niveau = refs.get("mediane_revenu_par_niveau", {})
    mediane_revenu_par_poste_regroupe = refs.get("mediane_revenu_par_poste_regroupe", {})

    statut_marital = normalize_string_category(payload["statut_marital"], STATUT_MARITAL_MAPPING)
    departement = normalize_string_category(payload["departement"], DEPARTEMENT_MAPPING)
    frequence_deplacement = normalize_string_category(
        payload["frequence_deplacement"], FREQUENCE_DEPLACEMENT_MAPPING
    )
    poste_regroupe = regroup_poste(payload["poste"], poste_mapping)
    domaine_etude_regroupe = regroup_domaine_etude(payload["domaine_etude"], domaine_mapping)

    poste_col = f"poste_regroupe_{poste_regroupe}"
    if poste_col not in expected_features:
        poste_regroupe = "Autre"
        poste_col = f"poste_regroupe_{poste_regroupe}"

    domain_col = f"domaine_etude_regroupe_{domaine_etude_regroupe}"
    if domain_col not in expected_features:
        domaine_etude_regroupe = "Autre"
        domain_col = f"domaine_etude_regroupe_{domaine_etude_regroupe}"

    niveau_key = str(payload["niveau_hierarchique_poste"])
    mediane_niveau = float(mediane_revenu_par_niveau.get(niveau_key, payload["revenu_mensuel"]))
    mediane_poste = float(
        mediane_revenu_par_poste_regroupe.get(poste_regroupe, payload["revenu_mensuel"])
    )

    ratio_anciennete_poste = safe_divide(
        payload["annees_dans_le_poste_actuel"], payload["annees_dans_l_entreprise"]
    )
    ratio_anciennete_manager = safe_divide(
        payload["annes_sous_responsable_actuel"], payload["annees_dans_l_entreprise"]
    )
    ratio_experience_entreprise = safe_divide(
        payload["annees_dans_l_entreprise"], payload["annee_experience_totale"]
    )

    evolution_evaluation = payload["note_evaluation_actuelle"] - payload["note_evaluation_precedente"]
    jamais_promu = int(payload["annees_depuis_la_derniere_promotion"] == 0)
    progression_salariale_faible = int(payload["augementation_salaire_precedente"] < 10)
    bonne_perf_peu_augmente = int(
        payload["note_evaluation_actuelle"] >= 4
        and payload["augementation_salaire_precedente"] < 10
    )
    sous_remunere_niveau = int(payload["revenu_mensuel"] < mediane_niveau)
    mobilite_interne_potentielle = int(
        payload["annees_dans_le_poste_actuel"] >= 3
        and payload["annees_depuis_la_derniere_promotion"] >= 2
    )

    retard_promotion_relatif = safe_divide(
        payload["annees_depuis_la_derniere_promotion"], payload["annees_dans_l_entreprise"]
    )
    revenu_par_niveau = safe_divide(payload["revenu_mensuel"], max(payload["niveau_hierarchique_poste"], 1))
    revenu_par_poste = safe_divide(
        payload["revenu_mensuel"], max(payload["nombre_employee_sous_responsabilite"] + 1, 1)
    )

    row = {
        "age": payload["age"],
        "genre": normalize_genre(payload["genre"]),
        "nombre_experiences_precedentes": payload["nombre_experiences_precedentes"],
        "satisfaction_employee_environnement": payload["satisfaction_employee_environnement"],
        "note_evaluation_precedente": payload["note_evaluation_precedente"],
        "niveau_hierarchique_poste": payload["niveau_hierarchique_poste"],
        "satisfaction_employee_nature_travail": payload["satisfaction_employee_nature_travail"],
        "satisfaction_employee_equipe": payload["satisfaction_employee_equipe"],
        "satisfaction_employee_equilibre_pro_perso": payload["satisfaction_employee_equilibre_pro_perso"],
        "note_evaluation_actuelle": payload["note_evaluation_actuelle"],
        "heure_supplementaires": payload["heure_supplementaires"],
        "augementation_salaire_precedente": payload["augementation_salaire_precedente"],
        "nombre_participation_pee": payload["nombre_participation_pee"],
        "nb_formations_suivies": payload["nb_formations_suivies"],
        "distance_domicile_travail": payload["distance_domicile_travail"],
        "niveau_education": payload["niveau_education"],
        "revenu_mensuel_log": safe_log1p(payload["revenu_mensuel"]),
        "annee_experience_totale_log": safe_log1p(payload["annee_experience_totale"]),
        "annees_dans_l_entreprise_log": safe_log1p(payload["annees_dans_l_entreprise"]),
        "annees_dans_le_poste_actuel_log": safe_log1p(payload["annees_dans_le_poste_actuel"]),
        "annees_depuis_la_derniere_promotion_log": safe_log1p(payload["annees_depuis_la_derniere_promotion"]),
        "annes_sous_responsable_actuel_log": safe_log1p(payload["annes_sous_responsable_actuel"]),
        "distance_domicile_travail_classe": compute_distance_class(payload["distance_domicile_travail"]),
        "ratio_anciennete_poste": ratio_anciennete_poste,
        "ratio_anciennete_manager": ratio_anciennete_manager,
        "ratio_experience_entreprise": ratio_experience_entreprise,
        "mobilite_interne_potentielle": mobilite_interne_potentielle,
        "jamais_promu": jamais_promu,
        "retard_promotion_relatif": retard_promotion_relatif,
        "progression_salariale_faible": progression_salariale_faible,
        "evolution_evaluation": evolution_evaluation,
        "bonne_perf_peu_augmente": bonne_perf_peu_augmente,
        "mediane_revenu_par_niveau": mediane_niveau,
        "revenu_par_niveau": revenu_par_niveau,
        "sous_remunere_niveau": sous_remunere_niveau,
        "mediane_revenu_par_poste": mediane_poste,
        "revenu_par_poste": revenu_par_poste,
    }

    for feature in expected_features:
        if feature.startswith("statut_marital_") or feature.startswith("departement_") \
           or feature.startswith("frequence_deplacement_") or feature.startswith("poste_regroupe_") \
           or feature.startswith("domaine_etude_regroupe_"):
            row.setdefault(feature, 0)

    marital_col = f"statut_marital_{statut_marital}"
    department_col = f"departement_{departement}"
    travel_col = f"frequence_deplacement_{frequence_deplacement}"

    if marital_col in expected_features:
        row[marital_col] = 1
    if department_col in expected_features:
        row[department_col] = 1
    if travel_col in expected_features:
        row[travel_col] = 1
    if poste_col in expected_features:
        row[poste_col] = 1
    if domain_col in expected_features:
        row[domain_col] = 1

    final_row = {feature: row.get(feature, 0) for feature in expected_features}
    df = pd.DataFrame([final_row], columns=expected_features)

    for feature in expected_features:
        if feature in INTEGER_FEATURES:
            df[feature] = df[feature].astype("int64")
        else:
            df[feature] = df[feature].astype("float64")

    return df
```

### Annexe J - `scripts/export_model_to_mlflow.py`

```python
"""Script d'entrainement et d'export du modele vers MLflow."""

from pathlib import Path
import json
import shutil

import mlflow
import mlflow.sklearn
from mlflow.artifacts import download_artifacts
from mlflow.models import infer_signature
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "model"
LOCAL_MODEL_DIR = ARTIFACTS_DIR / "current"
METADATA_PATH = ARTIFACTS_DIR / "metadata.json"
```

Suite de l'annexe J :

```python
def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "df_MODEL.csv")
    target_col = "a_quitte_l_entreprise"
    cols_to_drop = [target_col, "id_employee"]
    X = df.drop(columns=cols_to_drop, errors="ignore")
    y = df[target_col]
    return X, y


def build_model() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearSVC(random_state=42, dual="auto", max_iter=100000)),
    ])
```

Suite finale de l'annexe J :

```python
def main() -> None:
    X, y = load_training_data()
    model = build_model()
    model.fit(X, y)

    input_example = X.head(3)
    raw_scores = model.decision_function(X.head(20))
    signature = infer_signature(input_example, raw_scores)

    mlflow.set_tracking_uri(f"sqlite:///{PROJECT_ROOT / 'mlflow.db'}")
    mlflow.set_experiment("p5_employee_attrition")

    with mlflow.start_run(run_name="export_p5_model"):
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            signature=signature,
            input_example=input_example,
        )
        model_uri = model_info.model_uri

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    export_tmp_dir = ARTIFACTS_DIR / "_download"
    if export_tmp_dir.exists():
        shutil.rmtree(export_tmp_dir)
    if LOCAL_MODEL_DIR.exists():
        shutil.rmtree(LOCAL_MODEL_DIR)

    export_tmp_dir.mkdir(parents=True, exist_ok=True)
    downloaded_path = Path(download_artifacts(
        artifact_uri=model_uri,
        dst_path=str(export_tmp_dir),
    ))

    shutil.move(str(downloaded_path), str(LOCAL_MODEL_DIR))
    shutil.rmtree(export_tmp_dir)

    metadata = {
        "model_name": "linear_svc_attrition",
        "model_version": "0.1.0",
        "threshold": 0.1138,
        "feature_names": list(X.columns),
        "mlflow_model_uri": str(LOCAL_MODEL_DIR.resolve()),
        "score_method": "decision_function",
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
```

## 18. Mise a jour de l'etat du projet

Depuis la redaction initiale de ce mode operatoire, les points suivants ont ete realises :

- branchement effectif de la persistance SQLAlchemy sur l'endpoint `/predict` ;
- enregistrement en base de `prediction_requests`, `prediction_results` et `api_audit_logs` ;
- ajout de tests d'integration sur le flux complet de prediction et de tracabilite ;
- ajout d'une table `employees_source` pour preparer la couche PostgreSQL reelle ;
- implementation d'un script `scripts/seed_data.py` qui fusionne les trois extraits metier puis les charge en base ;
- ajout de tests d'integration sur la fusion des CSV et sur l'insertion des donnees source ;
- validation reelle du flux PostgreSQL local avec Docker Compose, creation du schema, chargement de `1470` lignes source et appel HTTP reel sur `/api/v1/predict`.

En pratique, le projet couvre maintenant :

- l'API de prediction ;
- le packaging du modele via MLflow ;
- la tracabilite applicative ;
- la preparation de la couche base de donnees source ;
- une premiere base de tests unitaires et d'integration.

La prochaine suite logique est :

- documenter la procedure d'exploitation locale validee ;
- relancer les tests avant commit ;
- figer un commit propre de cette etape ;
- puis poursuivre avec les scenarios de deploiement, d'authentification et de portfolio.

### 18.1 Validation reelle de PostgreSQL en local

Objectif :
prouver que la chaine complete fonctionne contre une vraie base PostgreSQL, et pas seulement contre SQLite en memoire dans les tests.

Commandes lancees :

```powershell
docker compose up -d postgres
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Pourquoi ces commandes :

- `docker compose up -d postgres` demarre l'instance PostgreSQL locale du projet ;
- `P5_DATABASE_URL` force explicitement l'application a utiliser cette base plutot que la valeur SQLite par defaut ;
- `create_db.py` cree les tables ORM reelles ;
- `seed_data.py` charge les donnees source fusionnees ;
- `uvicorn` permet de tester le vrai endpoint HTTP avec la vraie persistance.

Verification realisee :

- connexion TCP validee vers PostgreSQL sur `127.0.0.1:5433` ;
- schema cree avec les tables `employees_source`, `prediction_requests`, `prediction_results`, `api_audit_logs` ;
- `1470` lignes inserees dans `employees_source` ;
- appel HTTP reel `POST /api/v1/predict` retourne une reponse JSON valide ;
- une ligne de requete, une ligne de resultat et une ligne de log HTTP sont bien visibles en base.

Exemple de reponse API obtenue :

```json
{"prediction":0,"score":0.0,"threshold":0.1138,"model_version":"0.1.0","model_name":"linear_svc_attrition"}
```

Exemple de verification SQL :

```sql
SELECT count(*) FROM employees_source;
SELECT count(*) FROM prediction_requests;
SELECT count(*) FROM prediction_results;
SELECT count(*) FROM api_audit_logs;
```

### 18.2 Erreurs rencontrees pendant la validation locale

#### Erreur 1 : echec d'authentification PostgreSQL sur `127.0.0.1:5432`

Symptome :

- `psycopg.OperationalError`
- message de type `password authentication failed for user "postgres"`

Cause reelle :

- un autre serveur PostgreSQL natif etait deja lance sur Windows et occupait le port `5432` ;
- les commandes Python visaient donc cette instance locale, et non le conteneur Docker du projet.

Resolution :

- verification du processus a l'ecoute sur `5432` ;
- changement du mapping de port Docker du projet de `5432:5432` vers `5433:5432` dans `docker-compose.yml` ;
- mise a jour de `P5_DATABASE_URL` vers `127.0.0.1:5433`.

Lecon a retenir :

- quand une connexion base echoue alors que le conteneur est sain, il faut verifier immediatement quel processus ecoute vraiment sur le port cible.

#### Erreur 2 : conflit sur le port API `8000`

Symptome :

- `uvicorn` ne pouvait pas binder `127.0.0.1:8000` ;
- une ancienne API locale repondait deja sur ce port, avec un comportement code plus ancien.

Cause :

- une instance precedente de l'API etait deja lancee sur la machine.

Resolution :

- verification du port `8000` ;
- lancement de l'API de validation sur `8001` pour isoler le test reel.

Lecon a retenir :

- en validation locale, il faut toujours verifier que l'on parle bien a la bonne instance HTTP avant d'interpreter un resultat metier.

## 19. Mise a jour - Deploiement Docker et Hugging Face Spaces

Cette section ajoute le retour d'experience de la phase de conteneurisation et de deploiement distant.

L'objectif n'etait plus seulement de faire fonctionner l'API en local, mais :

- de construire une image Docker de l'API ;
- de la lancer localement avec la base PostgreSQL ;
- de remplacer le faux CD par un vrai deploiement vers Hugging Face Spaces ;
- puis de debugger les ecarts entre local et distant.

### 19.1 Packaging Docker de l'API

Objectif :

fabriquer un conteneur autonome capable de lancer l'API en dehors du poste de developpement.

Fichiers crees ou modifies :

- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml`
- `requirements.runtime.txt`
- `README.md`

Commandes utiles :

```powershell
docker compose build api
docker compose up -d --build postgres api
docker compose ps
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
docker compose down
```

Pourquoi ce packaging :

- `Dockerfile` permet de reproduire le runtime sur une machine distante ;
- `.dockerignore` evite d'envoyer des fichiers inutiles dans le contexte de build ;
- `docker-compose.yml` permet de valider rapidement le couple `api + postgres` ;
- `requirements.runtime.txt` separe les dependances de production des dependances de dev et de test.

Resultat obtenu :

- l'image Docker de l'API est bien construite ;
- le conteneur API demarre correctement ;
- le endpoint `/health` repond ;
- l'API conteneurisee repond aussi sur `/api/v1/predict`.

### 19.2 Remplacement du CD placeholder

Au depart, le workflow CD ne faisait qu'un `echo`.

Le CD a ete remplace par un vrai pipeline qui :

- valide le build Docker ;
- prepare un depot compatible Hugging Face Spaces ;
- pousse le contenu vers un Space Docker cible.

Fichiers importants :

- `.github/workflows/cd.yml`
- `deploy/huggingface/README.md`

Configuration GitHub necessaire :

- secret `HF_TOKEN`
- variable `HF_USERNAME`
- variable `HF_SPACE_NAME`

Lecon a retenir :

- un "CD" qui ne fait que reserver une place dans le depot n'est pas un vrai deploiement ;
- un vrai workflow de deploiement doit au minimum construire, publier ou synchroniser, puis permettre un controle du resultat.

### 19.3 Choix de Hugging Face Spaces

Le choix retenu pour le deploiement distant a ete :

- un Space Hugging Face de type `Docker`
- et non un Space `Streamlit`

Pourquoi :

- le projet expose avant tout une API FastAPI ;
- le runtime doit rester librement parametrable ;
- la cible HF sert ici de preuve de deploiement distant plus que d'interface front.

Point important :

- le P5 reste valide techniquement avec PostgreSQL local ;
- le Space HF ne peut pas utiliser la base PostgreSQL locale du poste de developpement.

### 19.4 Premiere erreur distante : base non initialisee

Symptome :

- le Space repondait sur `/` ;
- mais `/api/v1/predict` echouait avec une erreur SQLite du type `no such table: prediction_requests`.

Cause :

- le conteneur demarrait bien l'API ;
- mais aucun schema n'etait cree au boot dans l'environnement distant.

Resolution :

- le `Dockerfile` a ete modifie pour executer `python scripts/create_db.py` avant `uvicorn`.

Lecon a retenir :

- une API qui persiste en base doit initialiser son schema dans l'environnement de deploiement si aucune migration ou base preexistante n'est garantie.

### 19.5 Deuxieme erreur distante : score incoherent a `0.0`

Symptome :

- l'API repondait ;
- mais le retour ressemblait a :

```json
{"prediction":0,"score":0.0,"threshold":0.1138,"model_version":"0.1.0","model_name":"linear_svc_attrition"}
```

Pourquoi ce resultat etait suspect :

- la metadata du modele indiquait `score_method = decision_function` ;
- mais un score fixe a `0.0` ressemblait plutot a une classe binaire issue de `predict()`.

Cause reelle identifiee :

- la logique de prediction utilisait initialement `model.predict()` pour calculer le `score` ;
- on comparait donc un seuil continu a une sortie binaire ;
- localement, la vraie sortie `decision_function` du modele pour le payload de test etait en fait voisine de `-18.58`.

Corrections appliquees :

- chargement prioritaire du flavor `mlflow.sklearn` ;
- ajout d'une fonction `compute_model_score()` ;
- prise en charge explicite de `decision_function`, `predict_proba`, puis repli `predict` ;
- ajout de tests unitaires dedies.

Lecon a retenir :

- la methode de score du modele doit etre alignee avec la metadata exportee ;
- il ne faut pas confondre une classe predite et un score de decision.

### 19.6 Troisieme etape de debug : ne plus masquer les erreurs de flavor

Une fois le code corrige, le Space continuait encore parfois a renvoyer un score incoherent pendant les rebuilds.

L'analyse a montre qu'il fallait distinguer deux cas :

- le bon code n'est pas encore servi parce que Hugging Face affiche l'ancienne version pendant le build ;
- ou le bon code est bien present, mais le chargement du modele retombe silencieusement sur le flavor `pyfunc`.

Corrections de debug ajoutees :

- logs explicites dans `app/ml/loader.py` pour savoir si le flavor charge est `sklearn` ou `pyfunc` ;
- erreur explicite dans `app/ml/predictor.py` si la metadata exige `decision_function` alors que le modele charge ne l'expose pas.

Pourquoi cette correction est importante :

- un mauvais fallback silencieux peut produire une reponse fausse mais "propre" ;
- une erreur explicite est preferable a un resultat metier trompeur.

### 19.7 Problemes de rebuild Hugging Face

Retour d'experience concret :

- les rebuilds Hugging Face Spaces peuvent etre tres longs ;
- il est arrive de devoir attendre des durees anormalement longues avant un retour a l'etat `Running` ;
- pendant la phase `building`, HF sert encore l'ancienne version ;
- l'heure visible dans l'interface n'est pas toujours un indicateur fiable de la revision effectivement servie.

Actions entreprises pour limiter ce probleme :

- creation de `requirements.runtime.txt` pour ne garder que les dependances utiles au runtime de l'API ;
- suppression des dependances de test et de `streamlit` du conteneur de production ;
- conservation de `requirements.txt` pour la CI et le developpement.

Lecon a retenir :

- une cible de deploiement lente peut rester acceptable pour une preuve de deploiement, mais pas pour une boucle de dev rapide ;
- il faut donc conserver un environnement local robuste pour les validations serieuses.

### 19.8 Positionnement final de Hugging Face dans le projet

Dans le cadre du P5, la bonne lecture est la suivante :

- PostgreSQL local reste la reference pour la demonstration technique complete ;
- Hugging Face Spaces sert de preuve de deploiement distant ;
- l'environnement distant n'est pas la reference principale pour l'audit, la persistance ou le debug fin.

En pratique :

- le local sert a valider la chaine complete ;
- le Space sert a montrer que l'application est deployable et accessible a distance.

### Annexe K - `app/db/base.py`

```python
"""Base declarative SQLAlchemy du projet."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe mere des modeles ORM SQLAlchemy."""

    pass
```

### Annexe L - `app/db/session.py`

```python
from __future__ import annotations

"""Gestion de l'engine et des sessions SQLAlchemy."""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings


def _engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(
    settings.database_url,
    **_engine_kwargs(settings.database_url),
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Annexe M - `app/db/models/tracking.py`

```python
from __future__ import annotations

"""Modeles ORM dedies a la tracabilite des predictions."""

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PredictionRequest(Base):
    __tablename__ = "prediction_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_channel: Mapped[str] = mapped_column(String(50), default="api", nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prediction_result: Mapped["PredictionResult | None"] = relationship(
        back_populates="prediction_request", cascade="all, delete-orphan", uselist=False
    )
    audit_logs: Mapped[list["ApiAuditLog"]] = relationship(
        back_populates="prediction_request", cascade="all, delete-orphan"
    )


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_requests.id"), nullable=False, unique=True
    )
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prediction_request: Mapped["PredictionRequest"] = relationship(back_populates="prediction_result")


class ApiAuditLog(Base):
    __tablename__ = "api_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("prediction_requests.id"), nullable=True
    )
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prediction_request: Mapped["PredictionRequest | None"] = relationship(back_populates="audit_logs")
```

### Annexe N - `scripts/create_db.py`

```python
"""Script de creation du schema de base de donnees."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base
from app.db.models import ApiAuditLog, PredictionRequest, PredictionResult
from app.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database schema created successfully.")


if __name__ == "__main__":
    main()
```
