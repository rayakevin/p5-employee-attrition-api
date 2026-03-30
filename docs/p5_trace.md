# Projet P5 - Trace detaillee, mode operatoire et retour d'experience

## 1. Objet du document

Ce document a un role plus large qu'un simple compte-rendu.

Il doit permettre :

- de comprendre ce qui a ete fait sur le projet P5 ;
- de comprendre dans quel ordre les blocs ont ete construits ;
- de comprendre les erreurs rencontrees et leur resolution ;
- de retrouver plus tard la logique generale du projet ;
- de reutiliser la methode sur un autre projet de mise en production ML.

En pratique, ce document doit pouvoir etre rouvert dans plusieurs mois comme un guide de remise en route.

## 2. Comment lire ce document

Le document est structure en quatre niveaux :

1. une vision d'ensemble du projet ;
2. une chronologie detaillee de ce qui a ete construit ;
3. une synthese des erreurs et des points d'attention ;
4. des annexes commentees sur les fichiers les plus importants.

Si l'objectif est de remettre le projet en marche rapidement, il faut lire :

- la section 3 pour la big picture ;
- les sections 4 a 16 pour le deroule ;
- la section 17 pour les erreurs ;
- la section 18 pour la vision macro ;
- la section 21 pour les annexes de code.

## 3. Big picture du projet

Le projet transforme un modele de prediction d'attrition, d'abord entraine en notebook, en application exploitable.

Le resultat final comprend :

- une API FastAPI ;
- un modele exporte avec MLflow ;
- un preprocessing applicatif aligne sur le modele final ;
- une base PostgreSQL locale pour la tracabilite ;
- une interface Streamlit de demonstration et de portfolio ;
- une explication locale du score ;
- un mode batch sur CSV ;
- une CI ;
- deux CD vers Hugging Face Spaces, une pour l'API et une pour le portfolio.

Le point le plus important du projet n'est pas seulement d'avoir "une API qui repond", mais de garantir la coherence entre :

- les donnees d'entrainement ;
- les transformations de preprocessing ;
- le modele exporte ;
- la logique de prediction ;
- la logique d'explication ;
- la base de trace ;
- le frontend Streamlit ;
- le deploiement Docker.

## 4. Chronologie generale du projet

L'ordre theorique du guide P5 et l'ordre reel du projet ne se sont pas parfaitement superposes.

Ordre reel suivi :

1. initialisation du projet et conventions Git ;
2. structuration de l'environnement Python et de l'arborescence ;
3. mise en place CI/CD ;
4. construction de l'API FastAPI ;
5. stabilisation du flux de prediction et des tests ;
6. export du modele avec MLflow ;
7. correction des problemes de chargement, de types et de score ;
8. mise en place de la base et de la tracabilite ;
9. integration PostgreSQL locale et scripts de seed ;
10. tests d'integration ;
11. Dockerisation ;
12. deploiement sur Hugging Face Spaces ;
13. ajout du portfolio Streamlit ;
14. ajout de l'explication locale ;
15. ajout du mode batch ;
16. nettoyage final de la documentation.

Cette chronologie est importante : en pratique, un projet ML de production n'avance pas de facon parfaitement lineaire. Il faut accepter les retours arriere, les corrections, puis la reprise d'un bloc plus tard.

## 5. Etape 1 - Initialiser le repository et les conventions

### Objectif

Poser un cadre de travail propre et lisible.

### Commandes typiques

```powershell
git clone https://github.com/rayakevin/p5-employee-attrition-api.git
cd p5-employee-attrition-api
```

### Conventions retenues

Branches :

- `feature/<sujet>`
- `fix/<sujet>`
- `docs/<sujet>`
- `chore/<sujet>`
- `test/<sujet>`

Commits :

- `feat:`
- `fix:`
- `docs:`
- `chore:`
- `test:`
- `ci:`

### Pourquoi cette etape compte

Si les conventions Git ne sont pas posees au debut :

- l'historique devient vite illisible ;
- les PR sont plus difficiles a relire ;
- la documentation ne peut plus s'appuyer sur les commits ;
- il devient plus difficile de distinguer fonctionnalite, bugfix et maintenance.

## 6. Etape 2 - Structurer l'environnement Python

### Objectif

Disposer d'un projet Python reproductible avant d'ecrire le code metier.

### Commandes type

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### Elements structurants

- `pyproject.toml`
- `requirements.txt`
- `.gitignore`
- `.dockerignore`
- arborescence `app/`, `scripts/`, `tests/`, `docs/`, `ui/`, `data/`, `artifacts/`

### Pourquoi cette etape compte

L'arborescence du projet conditionne la qualite du code par la suite.

Une bonne structure evite :

- le melange entre code HTTP, code ML et code BDD ;
- les scripts "perdus" a la racine ;
- les tests qui ne savent plus quoi cibler ;
- une doc eparpillee.

## 7. Etape 3 - Poser la CI/CD

### Objectif

Ne pas attendre la fin du projet pour automatiser les controles.

### Workflows du projet

- [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- [`.github/workflows/cd.yml`](../.github/workflows/cd.yml)
- [`.github/workflows/cd-portfolio.yml`](../.github/workflows/cd-portfolio.yml)

### Ce que fait la CI

- installe les dependances ;
- demarre PostgreSQL ;
- cree le schema ;
- execute le seed ;
- lance les tests.

### Ce que fait la CD

- build les images Docker ;
- prepare un depot minimal pour Hugging Face Spaces ;
- pousse soit l'API, soit le portfolio.

### Pourquoi c'est important

La CI/CD n'est pas un bloc "cosmetique". Elle force a clarifier :

- les dependances reelles ;
- l'ordre d'initialisation ;
- le schema de base ;
- le comportement de l'application dans un vrai runtime.

## 8. Etape 4 - Construire l'API FastAPI

### Objectif

Exposer un service de prediction clair, documente et testable.

### Fichiers importants

- [`app/main.py`](../app/main.py)
- [`app/api/v1/router.py`](../app/api/v1/router.py)
- [`app/api/v1/endpoints/predict.py`](../app/api/v1/endpoints/predict.py)
- [`app/services/prediction_service.py`](../app/services/prediction_service.py)
- [`app/schemas/prediction.py`](../app/schemas/prediction.py)

### Logique de conception

La couche HTTP doit rester fine :

- les endpoints recoivent le payload ;
- les schemas valident les donnees ;
- le service orchestre ;
- le code ML ne doit pas etre dans l'endpoint.

### Endpoints finaux

- `GET /`
- `GET /health`
- `POST /api/v1/predict`
- `POST /api/v1/explain`
- `POST /api/v1/predict/batch`

### Pourquoi cette architecture est bonne

Elle separe :

- la validation d'entree ;
- la logique metier ;
- la logique ML ;
- la persistance.

Cette separation a rendu les corrections ulterieures beaucoup plus simples.

## 9. Etape 5 - Exporter le modele avec MLflow

### Objectif

Rendre le modele du notebook chargeable dans l'API.

### Fichier cle

- [`scripts/export_model_to_mlflow.py`](../scripts/export_model_to_mlflow.py)

### Ce que fait le script

1. charge `df_MODEL.csv` ;
2. prepare `X` et `y` ;
3. entraine le pipeline final ;
4. logge le modele dans MLflow ;
5. recupere l'artefact localement ;
6. cree une metadata applicative.

### Artefacts importants

- `artifacts/model/MLmodel`
- `artifacts/model/model.pkl`
- `artifacts/model/metadata.json`
- `artifacts/model/preprocessing_reference.json`

### Pourquoi `metadata.json` est central

Ce fichier sert de pont entre le monde ML et le monde applicatif. Il conserve :

- le nom du modele ;
- sa version ;
- le seuil de decision ;
- les noms de features ;
- la methode de score attendue ;
- le chemin de chargement du modele.

## 10. Etape 6 - Corriger le branchement du modele dans l'API

### Objectif

Faire fonctionner `/predict` contre le vrai modele exporte.

### Problemes reels rencontres

#### 1. `pytest` non reconnu

Cause :

- environnement Python non pris en compte.

Resolution :

- utiliser `uv run pytest -q`.

#### 2. Variable globale `DEBUG=release`

Cause :

- la machine possedait une variable globale qui polluait la config du projet.

Resolution :

- ajout du prefixe `P5_` dans la configuration Pydantic.

#### 3. Chemin d'artefact MLflow incoherent

Cause :

- le script d'export et le loader ne partageaient pas exactement la meme convention de stockage.

Resolution :

- rendre le loader tolerant ;
- corriger la convention d'export MLflow.

#### 4. Type de `genre` incompatible

Cause :

- le modele attendait une forme encodee, pas le libelle brut tel que fourni a l'API.

Resolution :

- normalisation explicite dans le preprocessing.

#### 5. Dtypes numeriques incoherents

Cause :

- les colonnes reconstruites par l'API ne respectaient pas exactement les types attendus par le schema du modele.

Resolution :

- forcing explicite des dtypes finaux dans le DataFrame de prediction.

### Lecon cle

Mettre un modele en production ne revient pas a appeler `predict()`.
Il faut aligner :

- le payload ;
- le preprocessing ;
- les artefacts MLflow ;
- les types de colonnes ;
- la logique de score.

## 11. Etape 7 - Realigner le preprocessing sur le modele final

### Objectif

Faire en sorte que l'inference reproduise exactement les transformations apprises.

### Fichier principal

- [`app/ml/preprocess.py`](../app/ml/preprocess.py)

### Ajustements importants

- acceptance d'entrees metier en francais ;
- utilisation des categories observees dans les CSV bruts ;
- correction des ratios d'anciennete ;
- correction de `mobilite_interne_potentielle` ;
- correction de `revenu_par_niveau` ;
- correction de `revenu_par_poste` ;
- normalisation correcte de `augementation_salaire_precedente` ;
- usage de `preprocessing_reference.json`.

### Incident important

Les contributions locales semblaient parfois "ecraser" tout le reste.

Cause :

- plusieurs variables derivees ne correspondaient plus aux notebooks.

Resolution :

- recalage complet du preprocessing sur la logique du modele final.

### Test de non-regression ajoute

Le projet reconstruit un individu de reference depuis `df_EDA.csv` et compare les features generees a sa ligne dans `df_MODEL.csv`.

Cette verification est tres importante : elle montre que l'API reconstruit bien les memes variables que l'entrainement.

## 12. Etape 8 - Corriger la logique de score

### Probleme rencontre

L'API renvoyait parfois un score incoherent, en particulier un `0.0` suspect.

### Cause

La logique utilisait `predict()` comme si c'etait un score.

### Fichiers corriges

- [`app/ml/loader.py`](../app/ml/loader.py)
- [`app/ml/predictor.py`](../app/ml/predictor.py)

### Corrections appliquees

- chargement prioritaire du flavor `mlflow.sklearn`
- calcul explicite via `decision_function`
- garde-fous si la methode attendue n'est pas disponible

### Lecon

Il faut distinguer :

- la sortie de classification ;
- la marge ou probabilite ;
- le seuil applique ensuite.

Sinon, l'API peut renvoyer une reponse valide en apparence mais numeriquement fausse.

## 13. Etape 9 - Ajouter la base et la tracabilite

### Objectif

Ne plus se contenter de repondre, mais conserver l'historique des appels.

### Fichiers importants

- [`app/db/base.py`](../app/db/base.py)
- [`app/db/session.py`](../app/db/session.py)
- [`app/db/models/tracking.py`](../app/db/models/tracking.py)
- [`scripts/create_db.py`](../scripts/create_db.py)

### Tables principales

- `employees_source`
- `prediction_requests`
- `prediction_results`
- `api_audit_logs`

### Pourquoi cette couche est essentielle

Elle transforme l'API en service exploitable :

- on sait qui a demande quoi ;
- quel score a ete renvoye ;
- quel statut technique a ete observe ;
- quelles donnees source ont ete chargees.

## 14. Etape 10 - Integrer PostgreSQL local et le seed

### Objectif

Valider la chaine contre une vraie base relationnelle.

### Commandes importantes

```powershell
docker compose up -d postgres
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

### Pourquoi un script de seed

Un script de seed sert a peupler la base avec les donnees initiales utiles au projet.

Ici, `scripts/seed_data.py` :

- charge les trois CSV bruts ;
- les fusionne ;
- normalise certains champs ;
- recharge `employees_source`.

### Incident reel

Echec d'authentification PostgreSQL sur `5432`.

Cause :

- un PostgreSQL local Windows utilisait deja ce port.

Resolution :

- le projet a bascule son conteneur sur `5433`.

## 15. Etape 11 - Ajouter l'explication locale

### Objectif

Expliquer le score d'un individu, pas seulement sa prediction.

### Fichiers importants

- [`app/ml/explainer.py`](../app/ml/explainer.py)
- [`app/api/v1/endpoints/predict.py`](../app/api/v1/endpoints/predict.py)
- [`app/services/prediction_service.py`](../app/services/prediction_service.py)

### Choix retenu

Le projet n'utilise pas SHAP au runtime. Il decompose directement la `decision_function` du pipeline lineaire.

### Pourquoi ce choix est pertinent ici

- le modele final est un `LinearSVC` ;
- l'explication additive locale est exacte ;
- le runtime reste plus simple, plus leger et plus fidele au modele de production.

## 16. Etape 12 - Construire le portfolio Streamlit

### Objectif

Donner un frontend plus demonstratif qu'un simple appel HTTP.

### Fichier principal

- [`ui/streamlit_app.py`](../ui/streamlit_app.py)

### Fonctionnalites principales

- analyse unitaire ;
- profils de demonstration ;
- synthese metier du resultat ;
- explication locale graphique ;
- analyse batch ;
- progression pendant le traitement ;
- zoom individu par individu.

### Choix d'architecture

Streamlit appelle l'API via `P5_API_BASE_URL`.

Cela evite :

- de dupliquer le preprocessing ;
- d'avoir deux logiques de prediction ;
- de desynchroniser backend et frontend.

## 17. Etape 13 - Dockeriser et deployer sur Hugging Face

### Objectif

Construire un runtime reproductible localement et deployable a distance.

### Fichiers importants

- [`Dockerfile`](../Dockerfile)
- [`Dockerfile.streamlit`](../Dockerfile.streamlit)
- [`docker-compose.yml`](../docker-compose.yml)
- [`requirements.runtime.txt`](../requirements.runtime.txt)
- [`requirements.streamlit.txt`](../requirements.streamlit.txt)
- [`deploy/huggingface/README.md`](../deploy/huggingface/README.md)
- [`deploy/huggingface/portfolio.README.md`](../deploy/huggingface/portfolio.README.md)

### Pourquoi deux Spaces

- un pour l'API ;
- un pour le portfolio.

Cela permet :

- des builds plus legers ;
- des responsabilites claires ;
- une maintenance plus simple.

## 18. Incidents majeurs rencontres et resolutions

### 18.1 Variables d'environnement parasites

Symptome :

- configuration instable selon la machine.

Resolution :

- prefixe `P5_`.

### 18.2 Artefacts MLflow mal resolus

Symptome :

- modele introuvable.

Resolution :

- resolution de chemin plus robuste dans le loader.

### 18.3 Score a `0.0`

Symptome :

- reponse apparemment valide mais score faux.

Resolution :

- alignement sur `decision_function`.

### 18.4 Tables absentes sur HF

Symptome :

- `no such table: prediction_requests`.

Resolution :

- creation du schema au demarrage du conteneur.

### 18.5 `unable to open database file` sur HF

Symptome :

- SQLite impossible a ouvrir dans le conteneur.

Cause probable :

- chemin fallback non fiable ou dossier parent absent.

Resolution :

- chemin SQLite explicite ;
- creation du dossier parent dans `app/db/session.py` ;
- preparation du dossier de stockage dans le `Dockerfile`.

### 18.6 Rebuilds Hugging Face tres lents

Symptome :

- build longs et peu confortables.

Resolution :

- reduction du contexte Docker ;
- separation API / portfolio ;
- requirements runtime dedies.

## 19. Vision macro du processus

Le processus global du projet peut se resumer ainsi :

1. structurer proprement le projet ;
2. construire une API fine ;
3. exporter proprement le modele ;
4. reproduire strictement le preprocessing ;
5. verifier la logique de score ;
6. ajouter la tracabilite ;
7. dockeriser ;
8. deployer ;
9. documenter ;
10. rendre le tout demonstrable via un frontend.

Ce schema est reutilisable sur un autre projet.

## 20. Repertoire des outils utilises

### uv

Gestion des dependances et de l'environnement Python.

### FastAPI

Exposition HTTP des services de prediction.

### Pydantic

Validation et documentation des contrats d'API.

### MLflow

Packaging du modele et transport de metadata.

### SQLAlchemy

Couche ORM et acces base.

### PostgreSQL

Base de reference pour la tracabilite locale.

### Streamlit

Frontend de demonstration.

### Docker

Packaging reproductible.

### GitHub Actions

CI et CD.

### Hugging Face Spaces

Preuve de deploiement distant.

## 21. Annexes - Extraits commentes des fichiers principaux

L'objectif des annexes n'est pas de recopier chaque fichier integralement, mais de conserver les blocs qui portent la logique du projet.

### Annexe A - `app/api/v1/endpoints/predict.py`

```python
@router.post("/predict", response_model=PredictionOutput)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),
) -> PredictionOutput:
    """Execute une prediction unitaire a partir d'un payload metier."""
    try:
        result = get_prediction(data.model_dump(), db=db)
        return PredictionOutput(**result)
```

Commentaire :

- le endpoint reste mince ;
- il ne contient pas de logique ML ;
- il transforme le payload en dictionnaire propre ;
- il delegue tout a la couche service.

```python
@router.post("/predict/batch", response_model=BatchPredictionOutput)
def predict_batch(data: BatchPredictionInput) -> BatchPredictionOutput:
    """Execute un scoring batch sans persistance technique."""
```

Commentaire :

- le batch est volontairement sans persistance pour eviter de polluer la tracabilite avec des jeux d'exploration ou de demonstration.

```python
@router.post("/explain", response_model=PredictionExplanationOutput)
def explain(data: PredictionInput) -> PredictionExplanationOutput:
    """Retourne une decomposition locale du score pour un individu."""
```

Commentaire :

- l'explication locale reutilise le meme contrat d'entree que la prediction ;
- cela garantit que prediction et explication portent sur les memes features reconstruites.

### Annexe B - `app/services/prediction_service.py`

```python
def get_prediction(
    payload: dict,
    db: Session,
    endpoint: str = "/api/v1/predict",
) -> dict:
    """Construit les features, appelle le modele et persiste la tracabilite."""
```

Commentaire :

- cette fonction est le coeur orchestral du projet ;
- elle relie payload, preprocessing, modele, resultat et persistance ;
- c'est l'endroit naturel pour journaliser la prediction.

```python
prediction_request = create_prediction_request(db=db, payload=payload)
model_input = build_model_features(payload)
prediction_data = predict_attrition(model_input)
create_prediction_result(...)
create_audit_log(...)
```

Commentaire :

- l'ordre est important ;
- on trace la requete avant le calcul ;
- on enregistre le resultat si tout se passe bien ;
- on conserve aussi une trace technique.

### Annexe C - `app/ml/preprocess.py`

```python
def build_model_features(payload: dict) -> pd.DataFrame:
    """Construit le DataFrame final attendu par le modele exporte."""
```

Commentaire :

- c'est le fichier le plus critique du projet ;
- il transforme un payload metier humain en vecteur numerique pour le modele ;
- la moindre incoherence ici casse la prediction ou l'interprete mal.

```python
statut_marital = normalize_string_category(...)
departement = normalize_string_category(...)
frequence_deplacement = normalize_string_category(...)
poste_regroupe = regroup_poste(...)
domaine_etude_regroupe = regroup_domaine_etude(...)
```

Commentaire :

- premiere etape : normaliser les categories ;
- cela permet d'accepter des valeurs metier francaises tout en restant compatible avec le schema du modele.

```python
ratio_anciennete_poste = safe_divide(
    payload["annees_dans_le_poste_actuel"],
    payload["annees_dans_l_entreprise"] + 1,
)
```

Commentaire :

- les ratios ont ete corriges pour retrouver la logique du notebook ;
- le `+1` evite les divisions par zero et respecte l'entrainement.

```python
augmentation_salaire_precedente = normalize_salary_increase(
    payload["augementation_salaire_precedente"]
)
```

Commentaire :

- l'API accepte `0.12` comme `12` ;
- le preprocessing reconvertit tout au format attendu par le modele.

### Annexe D - `app/ml/explainer.py`

```python
score = float(linear_model.decision_function(scaled_input)[0])
contributions = scaled_row * coefficients
```

Commentaire :

- l'explication locale repose sur la decomposition du score lineaire ;
- chaque contribution correspond a l'effet d'une feature standardisee sur le score final ;
- c'est une explication fidele au modele deploye.

```python
top_positive = explanation_df.head(top_n).to_dict(orient="records")
top_negative = (
    explanation_df.sort_values("contribution", ascending=True)
    .head(top_n)
    .to_dict(orient="records")
)
```

Commentaire :

- on renvoie separement les facteurs qui augmentent et diminuent le risque ;
- cela rend l'interpretation plus claire dans Streamlit.

### Annexe E - `app/db/session.py`

```python
def _prepare_sqlite_path(database_url: str) -> None:
    """Cree le dossier parent du fichier SQLite quand il est local."""
```

Commentaire :

- cette fonction a ete ajoutee pour fiabiliser le runtime Hugging Face ;
- SQLite ne cree pas le dossier parent ;
- sans ce point, le Space pouvait demarrer sans pouvoir ouvrir sa base locale.

### Annexe F - `app/db/models/tracking.py`

```python
class PredictionRequest(Base):
    __tablename__ = "prediction_requests"
```

Commentaire :

- conserve le payload brut ;
- constitue la premiere brique de tracabilite.

```python
class PredictionResult(Base):
    __tablename__ = "prediction_results"
```

Commentaire :

- conserve prediction, score, seuil et version du modele.

```python
class ApiAuditLog(Base):
    __tablename__ = "api_audit_logs"
```

Commentaire :

- conserve la trace technique ;
- utile pour depannage et audit.

### Annexe G - `scripts/create_db.py`

```python
from app.db.base import Base
from app.db.models import ApiAuditLog, EmployeeSource, PredictionRequest, PredictionResult
from app.db.session import engine

Base.metadata.create_all(bind=engine)
```

Commentaire :

- ce script charge la metadata SQLAlchemy puis cree les tables ;
- il est simple volontairement ;
- son role est de fournir une initialisation rapide du schema.

### Annexe H - `scripts/seed_data.py`

Role du script :

- charger `extrait_sirh.csv`, `extrait_eval.csv` et `extrait_sondage.csv` ;
- fusionner les donnees ;
- normaliser certains champs ;
- recharger `employees_source`.

Pourquoi il est important :

- il alimente la base de reference ;
- il rend possible les demonstrations locales ;
- il montre que le projet integre aussi un vrai flux de donnees source.

### Annexe I - `ui/streamlit_app.py`

Blocs importants :

- formulaire unitaire ;
- appel API ;
- rendu de la synthese ;
- rendu de l'explication locale ;
- upload CSV ;
- progression du batch ;
- selection d'un employe pour zoom local.

Pourquoi ce fichier est important :

- il montre comment transformer une API technique en interface de demonstration ;
- il reste volontairement client de l'API, ce qui evite de dupliquer la logique de prediction.

## 22. Ouvertures et ameliorations futures

Sans contrainte stricte de projet pedagogique, les suites naturelles seraient :

- ajout d'Alembic pour les migrations ;
- vraie base distante pour les Spaces ;
- authentification de l'API ;
- monitoring plus pousse ;
- suivi versionne des modeles ;
- comparaisons de cohortes dans le batch ;
- pipeline de retrain et de promotion de modele.

## 23. Conclusion

Le projet a evolue d'un modele de notebook vers une application complete :

- prediction ;
- explication ;
- persistance ;
- frontend ;
- tests ;
- Docker ;
- deploiement.

Le point essentiel a retenir est le suivant :

la qualite d'une mise en production ML ne vient pas seulement du modele, mais de la coherence entre toutes les couches du systeme. C'est cette coherence qui a demande le plus de travail sur ce P5, et c'est elle qu'il faudra conserver sur tout futur projet similaire.
