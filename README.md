# P5 - API de prediction d'attrition des employes

## 1. Présentation

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

### 3.2 Flux de prédiction

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
- [`docs/api/README.md`](docs/api/README.md)
- [`docs/model/README.md`](docs/model/README.md)
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

## 5. Prérequis

Pour travailler localement sur le projet :

- Python `3.11`
- `uv`
- Docker Desktop
- Git

## 6. Installation locale

### 6.1 Cloner le dépôt

```powershell
git clone https://github.com/rayakevin/p5-employee-attrition-api.git
cd p5-employee-attrition-api
```

### 6.2 Créer l'environnement Python

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### 6.3 Variables de configuration

La configuration du projet est préfixée par `P5_`.

Le projet distingue désormais trois environnements :

- `development` : travail local ;
- `test` : CI et Pytest ;
- `production` : déploiement distant.

En local, le plus simple est de partir du fichier [`.env.example`](.env.example) puis de créer un `.env` non versionné.

Variables importantes :

```env
P5_ENVIRONMENT=development
P5_DEBUG=true
P5_API_KEY=change-me-local-dev-key
P5_API_BASE_URL=http://127.0.0.1:8000

POSTGRES_DB=p5_attrition
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me-postgres-password
```

Chaîne de connexion locale recommandée pour l'API :

```env
P5_DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition
```

Règles importantes :

- en `development`, une configuration locale de secours existe pour accélérer le démarrage ;
- en `test`, la CI impose explicitement sa configuration ;
- en `production`, `P5_DATABASE_URL` et `P5_API_KEY` doivent être fournis explicitement.

## 7. Lancement local avec PostgreSQL

### 7.1 Démarrer PostgreSQL

```powershell
docker compose up -d postgres
```

Le projet utilise `5433` pour eviter les collisions avec une installation PostgreSQL locale deja presente sur `5432`.

### 7.2 Créer le schéma et charger les données source

```powershell
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
$env:P5_API_KEY="change-me-local-dev-key"
uv run python scripts/create_db.py
uv run python scripts/seed_data.py
```

Explication :

- `scripts/create_db.py` cree les tables SQLAlchemy ;
- `scripts/seed_data.py` fusionne les trois fichiers CSV metier et recharge `employees_source`.

Un script de `seed` est un script qui peuple une base avec des donnees initiales utiles a l'application, aux demonstrations ou aux tests.

### 7.3 Démarrer l'API

```powershell
$env:P5_ENVIRONMENT="development"
$env:P5_DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5433/p5_attrition"
$env:P5_API_KEY="change-me-local-dev-key"
uv run uvicorn app.main:app --reload
```

### 7.4 Vérifier le service

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

Les routes metier `POST` sont protegees par une cle d'API transmise dans l'en-tete `X-API-Key`.

### 8.2 Valeurs conseillées pour les champs catégoriels

Les valeurs ci-dessous reprennent les libellés francisés documentés par le projet et normalisés par le preprocessing.

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

Pour savoir quelles valeurs renseigner :

- la référence métier la plus simple est le formulaire Streamlit, qui ne propose que des valeurs compatibles ;
- les exemples Swagger/OpenAPI exposent également des payloads valides ;
- les valeurs proviennent des modalités réellement observées dans les données sources brutes (`data/raw/`) puis normalisées par [`app/ml/preprocess.py`](app/ml/preprocess.py) ;
- les schémas d'entrée documentés dans [`app/schemas/prediction.py`](app/schemas/prediction.py) servent de contrat de référence.

Le projet conserve quelques alias pour compatibilité, mais le contrat documentaire à privilégier est repris ci-avant.

### 8.3 Exemple de payload de prédiction

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
  -Headers @{ "X-API-Key" = $env:P5_API_KEY } `
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

### 8.4 Exemple de requête d'explication locale

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/explain" `
  -Headers @{ "X-API-Key" = $env:P5_API_KEY } `
  -ContentType "application/json" `
  -Body $payload
```

La reponse contient :

- la `base_value` ;
- les sommes positives et negatives ;
- les facteurs principaux qui augmentent le risque ;
- les facteurs principaux qui diminuent le risque.

### 8.5 Exemple de requête batch

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
        },
        @{
            age = 46
            genre = "Femme"
            revenu_mensuel = 6900
            statut_marital = "Marie(e)"
            departement = "Consulting"
            poste = "Senior Manager"
            nombre_experiences_precedentes = 3
            annee_experience_totale = 22
            annees_dans_l_entreprise = 14
            annees_dans_le_poste_actuel = 5
            satisfaction_employee_environnement = 4
            note_evaluation_precedente = 4.0
            niveau_hierarchique_poste = 4
            satisfaction_employee_nature_travail = 4
            satisfaction_employee_equipe = 4
            satisfaction_employee_equilibre_pro_perso = 4
            note_evaluation_actuelle = 4.0
            heure_supplementaires = "Non"
            augementation_salaire_precedente = 0.15
            nombre_participation_pee = 1
            nb_formations_suivies = 3
            nombre_employee_sous_responsabilite = 0
            distance_domicile_travail = 7
            niveau_education = 3
            domaine_etude = "Infra & Cloud"
            frequence_deplacement = "Aucun"
            annees_depuis_la_derniere_promotion = 1
            annes_sous_responsable_actuel = 5
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/predict/batch" `
  -Headers @{ "X-API-Key" = $env:P5_API_KEY } `
  -ContentType "application/json" `
  -Body $batch
```

## 8.6 Authentification et sécurité

Le projet implémente une authentification simple par clé d'API.

Principe :

- les routes publiques `GET /` et `GET /health` restent ouvertes ;
- les routes métier `/predict`, `/explain` et `/predict/batch` exigent un en-tête `X-API-Key` ;
- la valeur attendue est lue depuis `P5_API_KEY`.

Pourquoi ce choix :

- il répond au besoin pédagogique de contrôle d'accès ;
- il reste facile à tester, à documenter et à déployer ;
- il est compatible avec FastAPI et Swagger/OpenAPI.

Bonnes pratiques retenues :

- stocker `P5_API_KEY` en variable d'environnement ;
- utiliser les secrets GitHub pour les déploiements ;
- ne jamais committer une vraie clé de production ;
- séparer autant que possible les secrets locaux, CI/CD et production ;
- limiter l'exposition de la base et des variables de configuration.

Le portfolio Streamlit consomme lui aussi l'API protégée. En pratique, il lit la variable `P5_API_KEY` et transmet automatiquement cette valeur dans l'en-tête `X-API-Key` lors des appels HTTP vers l'API. L'utilisateur du portfolio n'a donc pas à saisir la clé manuellement dans l'interface, mais elle doit être configurée dans l'environnement d'exécution.

## 9. Base de données et traçabilité

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
- endpoints batch ;
- protection par cle d'API ;
- contrat OpenAPI ;
- parcours fonctionnels principaux.

### 11.3 Générer un rapport de couverture

Commande utilisée en local :

```powershell
uv run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
```

Résultats obtenus sur l'état actuel du dépôt :

- `27 passed` ;
- couverture totale `89%` sur le package `app` ;
- génération d'un rapport terminal détaillé ;
- génération de `htmlcov/index.html` pour une lecture visuelle ;
- génération de [`coverage.xml`](coverage.xml) pour la CI.

Interprétation :

- la couverture est solide pour un projet P5 et sécurise bien les flux critiques ;
- les zones les mieux couvertes sont les endpoints, le preprocessing, le scoring, l'explication locale et les parcours batch ;
- le reliquat non couvert correspond surtout à du code de démarrage, de configuration ou à des chemins secondaires moins risqués.

Rapports disponibles :

- [`coverage.xml`](coverage.xml) : rapport machine exploitable par la CI et les outils d'analyse ;
- [`docs/tests/coverage_report.md`](docs/tests/coverage_report.md) : rapport écrit et interprété.

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

Variables CI imposees :

- `P5_ENVIRONMENT=test`
- `P5_API_KEY=p5-test-key`
- `P5_DATABASE_URL` pointe vers le service PostgreSQL du job GitHub Actions.

### 13.2 CD API

Workflow :

- [`.github/workflows/cd.yml`](.github/workflows/cd.yml)

Configuration GitHub requise :

- deux environnements GitHub : `development` et `production`
- dans chaque environnement :
  - secret `HF_TOKEN`
  - variable `HF_USERNAME`
  - variable `HF_SPACE_NAME`

Comment configurer ces éléments :

1. créer le Space API sur Hugging Face en mode `Docker` ;
2. récupérer votre nom d'utilisateur Hugging Face, par exemple `rayakevin` ;
3. relever le nom exact du Space, par exemple `p5-employee-attrition-api` ;
4. dans GitHub, créer les environnements `development` et `production` ;
5. dans chaque environnement, ouvrir `Secrets and variables` ;
6. créer le secret `HF_TOKEN` dans `Secrets` ;
7. créer `HF_USERNAME` et `HF_SPACE_NAME` dans `Variables`.

Comment obtenir `HF_TOKEN` :

1. ouvrir `https://huggingface.co/settings/tokens` ;
2. créer un `User Access Token` ;
3. choisir au minimum un droit d'écriture sur le Space cible ;
4. copier la valeur `hf_...` générée puis la coller dans le secret GitHub `HF_TOKEN`.

Valeurs à renseigner :

- `HF_TOKEN` : votre token Hugging Face ;
- `HF_USERNAME` : votre nom de compte Hugging Face ;
- `HF_SPACE_NAME` : le nom exact du Space API.

Logique de branche recommandée :

- `develop` deploie l'environnement `development` ;
- `main` deploie l'environnement `production`.

Important :

- les variables GitHub pilotent le workflow de publication ;
- les secrets et variables du runtime Hugging Face doivent aussi etre definis dans le Space lui-meme pour l'execution du conteneur ;
- pour une production propre, le Space API doit recevoir au minimum `P5_ENVIRONMENT=production`, `P5_API_KEY` et `P5_DATABASE_URL`.

### 13.3 CD portfolio Streamlit

Workflow :

- [`.github/workflows/cd-portfolio.yml`](.github/workflows/cd-portfolio.yml)

Configuration GitHub requise :

- deux environnements GitHub : `development` et `production`
- dans chaque environnement :
  - secret `HF_TOKEN`
  - variable `HF_USERNAME`
  - variable `HF_PORTFOLIO_SPACE_NAME`

Logique de configuration :

- le secret `HF_TOKEN` peut être réutilisé si le même compte pousse aussi le portfolio ;
- `HF_USERNAME` reste le compte propriétaire des Spaces ;
- `HF_PORTFOLIO_SPACE_NAME` doit contenir le nom exact du Space portfolio, par exemple `p5-employee-attrition-portfolio`.

Procédure :

1. créer un second Space Hugging Face dédié au portfolio, lui aussi en mode `Docker` ;
2. dans GitHub, ouvrir l'environnement `development` ou `production` selon la cible ;
3. vérifier que `HF_TOKEN` existe déjà ;
4. ajouter ou mettre à jour `HF_USERNAME` ;
5. ajouter `HF_PORTFOLIO_SPACE_NAME` dans `Variables`.

Documentation de deploiement :

- [`deploy/huggingface/README.md`](deploy/huggingface/README.md)
- [`deploy/huggingface/portfolio.README.md`](deploy/huggingface/portfolio.README.md)

## 14. Déploiement distant

Le projet utilise Hugging Face Spaces en mode Docker.

Important :

- le Space API sert de preuve de deploiement distant ;
- la reference technique pour le P5 reste l'environnement local avec PostgreSQL ;
- les rebuilds HF peuvent etre longs, donc le debug principal reste local ;
- la cible recommandee en production reste un PostgreSQL distant fourni via `P5_DATABASE_URL` ;
- SQLite ne doit plus etre considere comme la cible normale d'exploitation.

Exemples de verification distante :

```powershell
Invoke-RestMethod -Method Get -Uri "https://rayakevin-p5-employee-attrition-api.hf.space/health"
```

## 15. Protocole de mise à jour

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

Le projet suit une logique simple inspiree de GitFlow :

- `main` : branche de reference pour la production ;
- `develop` : branche d'integration continue pour l'environnement de developpement ;
- `feature/<sujet>` : nouvelle fonctionnalite ;
- `fix/<sujet>` : correction de bug ;
- `docs/<sujet>` : documentation ;
- `chore/<sujet>` : maintenance, packaging, nettoyage ;
- `test/<sujet>` : ajout ou reprise de tests.

Flux recommande :

1. developper sur `feature/*` ;
2. merger dans `develop` pour valider l'environnement de developpement ;
3. merger `develop` dans `main` pour publier en production.

### 16.2 Commits

- `feat:` : nouvelle fonctionnalite
- `fix:` : correction
- `docs:` : documentation
- `chore:` : maintenance
- `test:` : tests
- `ci:` : pipeline GitHub Actions

### 16.3 Tags

Le projet utilise des tags Git pour figer des états stables, présentables et facilement retrouvables dans l'historique.

Logique retenue :

- un tag est posé uniquement sur un état validé par les tests et la documentation ;
- le premier chiffre représente une étape majeure du produit ;
- le deuxième chiffre représente une évolution fonctionnelle importante sans rupture complète ;
- le troisième chiffre représente un correctif ou un ajustement stabilisé.

Exemples :

- `v0.1.0` : première version stable du projet industrialisé ;
- `v0.2.0` : ajout important de fonctionnalités sans changement de socle ;
- `v0.2.1` : correctif stabilisé sur une version déjà livrée ;
- `v1.0.0` : version considérée comme aboutie pour une livraison de référence.

Le dépôt contient actuellement le tag `v0.1.0`, utilisé pour marquer un état cohérent du projet avec API sécurisée, tests, documentation et pipeline de déploiement.

## 17. Dépendances

Les trois fichiers de dépendances sont à jour par rapport à l'état actuel du dépôt.

- `requirements.txt` : environnement complet de développement, de tests et d'usage local. Il inclut notamment FastAPI, SQLAlchemy, MLflow, Pytest, Streamlit et HTTPX.
- `requirements.runtime.txt` : runtime API allégé pour Docker et le Space API. Il conserve uniquement les dépendances nécessaires à l'API, au modèle et à la base.
- `requirements.streamlit.txt` : runtime dédié au portfolio Streamlit. Il contient uniquement Streamlit, Pandas et HTTPX pour consommer l'API.

Cette séparation permet :

- d'éviter d'embarquer des dépendances inutiles dans les images de déploiement ;
- de réduire le poids des builds Docker ;
- de garder un environnement de développement plus riche que les runtimes de production.

## 18. Documents utiles

- [`docs/api/README.md`](docs/api/README.md) : documentation detaillee de l'API
- [`docs/db/README.md`](docs/db/README.md) : documentation detaillee de la base de donnees
- [`docs/model/README.md`](docs/model/README.md) : documentation du modele final et du preprocessing
- [`docs/tests/coverage_report.md`](docs/tests/coverage_report.md) : rapport écrit de couverture de tests
- [`docs/p5_demo_exploitation.md`](docs/p5_demo_exploitation.md) : fiche de demonstration
- [`docs/architecture/overview.md`](docs/architecture/overview.md) : architecture
- [`docs/maintenance_protocol.md`](docs/maintenance_protocol.md) : maintenance

## 19. État du projet

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
- PostgreSQL local n'est pas disponible dans les Spaces ;
- la cible distante sert surtout de vitrine et de preuve de déploiement.

## 21. Contexte

Projet realise dans le cadre du Projet 5 OpenClassrooms, avec l'objectif de transformer un modele de machine learning en application exploitable, testable, tracable et documentee.
