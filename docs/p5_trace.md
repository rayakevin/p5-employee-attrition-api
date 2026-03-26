# Projet P5 - Trace Detaillee du Travail Realise dans Cette Discussion

## 1. Objet du document

Ce document retrace, de maniere detaillee, le travail effectivement realise sur le projet P5 dans cette discussion. Il s'appuie sur :

- le referentiel pedagogique du projet P5 contenu dans le document principal de 140 pages ;
- l'etat reel du repository au moment de l'intervention ;
- les commandes lancees dans le terminal ;
- les fichiers consultes, modifies ou crees pendant la seance ;
- les erreurs reproduites puis resolues.

Le but est double :

- documenter techniquement les manipulations realisees ;
- expliquer pourquoi chaque etape a ete faite de cette maniere, afin qu'un lecteur comprenne la logique de resolution et le role de chaque outil.

Important : ce document couvre strictement le travail visible dans cette discussion. Il ne pretend pas reconstituer des actions anterieures qui n'apparaissent ni dans le thread ni dans le workspace courant.

## 2. Contexte du projet

Le projet P5 porte sur le deploiement d'un modele de machine learning dans une API exploitable, testable et maintenable. Dans le repository observe ici, le projet prend la forme d'une API FastAPI exposee sur un endpoint de prediction, avec :

- une couche de schemas Pydantic pour valider les donnees d'entree et de sortie ;
- une couche de service pour orchestrer la prediction ;
- une couche ML pour charger un modele MLflow, preparer les features, puis produire un score et une classe ;
- une suite de tests unitaires Pytest.

Le point de depart de cette intervention etait un test qui ne passait pas, avec l'hypothese utilisateur que la cause etait liee a `scripts/export_model_to_mlflow.py`.

## 3. Strategie de travail suivie

La strategie adoptee a ete la suivante :

1. Reproduire l'echec de test dans l'environnement reel.
2. Identifier si l'echec venait effectivement du flux MLflow ou d'une autre couche.
3. Corriger la cause immediate sans ecraser les modifications deja presentes dans le workspace.
4. Relancer les tests pour detecter d'eventuels problemes masques.
5. Stabiliser le pipeline complet : configuration, chargement du modele, preprocessing, et export MLflow.

Cette approche est importante dans un projet de deploiement ML : un premier echec visible en masque souvent un autre. Si l'on corrige uniquement le symptome sans reexecuter la chaine complete, on risque de laisser plusieurs regressions non detectees.

## 4. Inventaire des commandes lancees

Cette section recense les commandes executees pendant la discussion, avec leur objectif.

### 4.1 Inspection initiale du repository

Commande :

```powershell
git status --short
```

Objectif :

- verifier l'etat du workspace avant de toucher au code ;
- identifier les fichiers deja modifies par l'utilisateur ou par des scripts ;
- eviter d'ecraser des changements non lies a l'intervention.

Pourquoi c'est important :

Dans un projet reel, on ne doit jamais partir du principe que le workspace est propre. Ici, cette commande a montre de nombreuses modifications et fichiers non suivis, notamment des artefacts MLflow et des donnees. Cela a conditionne la suite : toute correction devait etre strictement ciblee.

Commande :

```powershell
rg --files
```

Objectif :

- obtenir rapidement l'arborescence des fichiers utiles ;
- localiser les scripts, modules ML, tests et artefacts.

Pourquoi `rg` :

`rg` est plus rapide et plus pratique que des alternatives plus verbeuses pour cartographier un repo.

### 4.2 Reproduction du probleme

Commande :

```powershell
pytest -q
```

Resultat :

- echec immediat car `pytest` n'etait pas disponible sur le `PATH`.

Interet :

- cela a permis d'identifier que l'environnement ne devait pas etre utilise via le binaire global, mais via l'environnement du projet.

Commande :

```powershell
uv run pytest -q
```

Objectif :

- executer Pytest dans l'environnement gere par `uv`, en utilisant les dependances declarees dans le projet.

Pourquoi `uv run` :

- garantit l'utilisation de l'environnement du projet ;
- evite les problemes de versions Python ou de packages systeme ;
- est coherent avec un workflow de projet reproductible.

### 4.3 Lecture des fichiers lies au probleme

Commandes de consultation :

```powershell
Get-Content scripts\export_model_to_mlflow.py
Get-Content app\ml\loader.py
Get-Content pyproject.toml
Get-Content tests\unit\test_predict.py
Get-Content app\core\config.py
Get-Content tests\unit\test_config.py
Get-Content app\main.py
Get-Content app\api\v1\endpoints\predict.py
Get-Content app\services\prediction_service.py
Get-Content app\ml\predictor.py
Get-Content app\ml\preprocess.py
Get-Content artifacts\model\metadata.json
Get-ChildItem -Recurse artifacts\model | Select-Object FullName
Get-Content artifacts\model\MLmodel
Get-Content app\schemas\prediction.py
Get-Content artifacts\model\preprocessing_reference.json
```

Objectif :

- comprendre la chaine complete allant du test HTTP jusqu'au modele MLflow ;
- comparer le chemin attendu par le loader avec les artefacts reellement presents ;
- verifier le schema d'entree du modele exporte ;
- verifier la logique de preprocessing et les types attendus.

Pourquoi lire autant de fichiers :

Dans une application ML en production, le bug n'est presque jamais localise a un seul script. Ici, le test traversait :

- les schemas d'entree ;
- la couche API ;
- la couche service ;
- la transformation des features ;
- le chargement du modele ;
- le modele MLflow lui-meme.

Il fallait donc reconstruire la chaine complete pour corriger la vraie cause.

### 4.4 Analyse de l'environnement et des donnees

Commandes :

```powershell
Get-ChildItem -Force | Where-Object { $_.Name -like '.env*' } | Select-Object -ExpandProperty Name
rg -n "settings\.debug|environment|app_name|Settings\(" app
```

Objectif :

- verifier si une configuration locale `.env` expliquait l'echec des tests ;
- verifier ou `settings` etait utilise dans l'application.

Commandes d'analyse des donnees :

```powershell
uv run python -c "import pandas as pd; df=pd.read_csv('data/processed/df_MODEL.csv'); print(df.columns.tolist())"
uv run python -c "import pandas as pd; df=pd.read_csv('data/processed/df_EDA.csv'); cols=[c for c in ['genre','statut_marital','departement','frequence_deplacement','poste','domaine_etude'] if c in df.columns]; print(df[cols].head().to_string()); print(); [print(c, sorted(df[c].dropna().astype(str).unique().tolist())[:20]) for c in cols]"
uv run python -c "import pandas as pd; df=pd.read_csv('data/processed/df_MODEL.csv'); print(df[['genre']].head().to_string()); print(sorted(df['genre'].dropna().unique().tolist()))"
uv run python -c "import pandas as pd; df=pd.read_csv('data/processed/df_MODEL.csv'); print(df.dtypes.to_string())"
```

Objectif :

- verifier quelles colonnes etaient reelles dans le dataset modele ;
- comprendre l'encodage de `genre` et des categories ;
- recuperer les types exacts des features attendues par le modele exporte.

Pourquoi ces commandes ont ete necessaires :

Le modele MLflow ne juge pas seulement les noms de colonnes, il impose aussi un schema de types. Pour corriger proprement le preprocessing, il fallait repartir du dataset d'entrainement exporte, pas deviner les types "a l'intuition".

### 4.5 Installation d'un outil pour lire le PDF

Commande :

```powershell
python -m pip install --user pypdf
```

Objectif :

- installer une bibliotheque PDF locale afin de lire le document de 140 pages fourni hors repo.

Pourquoi cette installation a ete faite :

- aucune bibliotheque PDF n'etait disponible par defaut ;
- il fallait pouvoir extraire le texte pour lire le document integralement.

Commandes preparatoires et de lecture :

```powershell
@'
import importlib.util
mods = ['PyPDF2', 'fitz', 'pdfplumber', 'pymupdf']
for m in mods:
    print(m, bool(importlib.util.find_spec(m)))
'@ | python -
```

```powershell
Get-Item 'C:\Users\kevin\Desktop\Formation IA engineer Openclassrooms - Projet 5 Déploiement ML.pdf' | Select-Object FullName,Length
```

Puis une lecture du PDF via Python et `pypdf` en iterant sur le dossier Desktop, afin d'eviter un probleme d'encodage sur le caractere accentue du nom de fichier.

## 5. Chronologie des erreurs rencontrees et leur resolution

### 5.1 Erreur 1 : `pytest` non reconnu

Symptome :

- la commande `pytest -q` echouait car `pytest` n'etait pas disponible comme commande globale.

Cause :

- l'environnement Python utilise pour le projet n'etait pas expose via le `PATH` global du shell.

Resolution :

- utilisation de `uv run pytest -q`.

Explication :

Dans un projet moderne, il est preferable d'utiliser l'environnement du projet plutot qu'un Python global. Cela reduit les ecarts entre machines et limite les erreurs de dependances.

### 5.2 Erreur 2 : echec de collecte des tests dans la configuration

Symptome :

- Pytest ne demarrait pas les tests fonctionnels car l'import de `app.core.config` echouait ;
- l'erreur indiquait que `debug` recevait la valeur `"release"`, non interpretable comme booleen.

Cause :

- `Settings()` lisait une variable d'environnement globale `DEBUG=release` de la machine ;
- le projet n'avait pas de prefixe de variables d'environnement, donc il absorbait trop facilement des variables externes sans rapport.

Resolution :

- modification de `app/core/config.py` pour ajouter `env_prefix="P5_"`.

Pourquoi cette correction est saine :

- elle isole les variables d'environnement du projet ;
- elle evite des conflits avec des variables generiques du poste de travail ;
- elle est coherente avec les bonnes pratiques de deploiement.

### 5.3 Erreur 3 : modele MLflow introuvable

Symptome :

- le test `/predict` renvoyait une erreur 500 avec un message indiquant que le modele etait introuvable a `artifacts/model/current`.

Cause :

- `metadata.json` pointait vers `artifacts/model/current` ;
- mais les artefacts MLflow presents dans le repo se trouvaient directement dans `artifacts/model/`.

Autrement dit :

- le loader et l'export n'etaient plus alignes sur la meme convention de stockage.

Resolution :

- ajout d'une resolution de chemin robuste dans `app/ml/loader.py` ;
- le loader essaye d'abord le chemin de la metadata, puis des emplacements de repli coherents (`artifacts/model` et `artifacts/model/current`) ;
- la metadata chargee en memoire est ensuite synchronisee avec le chemin reel resolu.

Pourquoi cette correction est utile :

- elle rend le runtime plus tolerant a un artefact deja exporte sous une structure voisine ;
- elle evite une panne de service pour une simple divergence de convention de dossier.

### 5.4 Erreur 4 : incompatibilite du type de la colonne `genre`

Symptome :

- une fois le modele charge, MLflow rejetait l'entree car la colonne `genre` etait de type `object` alors que le modele attendait un `int64`.

Cause :

- le payload HTTP du test utilisait une valeur metier de type `"Male"` ;
- le dataset d'entrainement, lui, contenait `genre` encode en `0` ou `1`.

Resolution :

- ajout d'une normalisation explicite de `genre` dans `app/ml/preprocess.py` ;
- prise en charge de variantes telles que `Male`, `Female`, `M`, `F`, `Homme`, `Femme`.

Pourquoi cette correction est importante :

- elle reconnecte l'API metier a la representation attendue par le modele ;
- elle evite de faire porter aux clients de l'API un format interne d'entrainement.

### 5.5 Erreur 5 : incompatibilite de type sur `note_evaluation_precedente`

Symptome :

- apres correction de `genre`, MLflow rejetait encore l'entree car certaines colonnes numeriques etaient envoyees en `float64` alors que le modele attendait des `int64`.

Cause :

- le preprocessing construisait un DataFrame valide en apparence, mais non conforme au schema exact de types impose par MLflow ;
- certaines valeurs fournies par le payload etaient des flottants, alors que le dataset d'entrainement avait stocke ces colonnes en entiers.

Resolution :

- ajout d'un cast explicite des colonnes finales dans `app/ml/preprocess.py` ;
- separation entre features entieres et features flottantes ;
- coercition du DataFrame final selon la realite du dataset modele.

Pourquoi cette correction est la bonne :

- elle s'aligne sur la source de verite, a savoir `df_MODEL.csv` et le schema exporte par MLflow ;
- elle rend la prediction stable et reproductible.

### 5.6 Probleme annexe : chemin PDF avec accent mal gere

Symptome :

- certaines tentatives d'ouverture du fichier PDF depuis Python echouaient a cause du nom du fichier contenant `Déploiement`.

Cause :

- probleme de transmission du chemin accentue entre le shell et Python dans ce contexte.

Resolution :

- iteration directe du contenu du dossier Desktop depuis Python ;
- recuperation du bon objet `Path` sans reconstruire manuellement le chemin.

Pourquoi cela merite d'etre note :

- les problemes d'encodage de chemins Windows sont tres frequents ;
- cela illustre qu'il vaut mieux souvent enumerer un repertoire que copier-coller un chemin encode de travers.

## 6. Fichiers modifies ou crees

### 6.1 `app/core/config.py`

Role du fichier :

- centraliser les parametres de configuration applicative via Pydantic Settings.

Modification apportee :

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Employee Attrition Prediction API"
    environment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="P5_",
    )


settings = Settings()
```

Explication :

- `env_file=".env"` permet de charger une configuration locale si elle existe ;
- `env_prefix="P5_"` force le projet a n'accepter que des variables comme `P5_DEBUG`, `P5_ENVIRONMENT`, etc. ;
- cela evite qu'une variable generique du poste de travail perturbe le projet.

### 6.2 `app/ml/loader.py`

Role du fichier :

- charger la metadata du modele ;
- localiser l'artefact MLflow ;
- charger le modele en runtime via `mlflow.pyfunc`.

Contenu final :

```python
from __future__ import annotations

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

Explication des points importants :

- `load_model_metadata()` lit la configuration du modele exporte ;
- `resolve_model_path()` ajoute de la robustesse : on n'echoue pas tout de suite si le chemin de metadata n'est plus parfaitement coherent ;
- le test `(candidate / "MLmodel").exists()` est pertinent car `MLmodel` est le fichier signature standard d'un artefact MLflow ;
- `mlflow.pyfunc.load_model()` charge le modele sous une interface de prediction uniforme.

### 6.3 `scripts/export_model_to_mlflow.py`

Role du fichier :

- entrainer un modele `LinearSVC` ;
- le logger dans MLflow ;
- telecharger l'artefact ;
- produire une metadata locale pour le runtime.

Contenu final :

```python
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
        ("model", LinearSVC(
            random_state=42,
            dual="auto",
            max_iter=100000,
        )),
    ])


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

    # Download into a staging directory to avoid mixing model files
    # with metadata and preprocessing artifacts stored in artifacts/model.
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

    print("Model exported to MLflow.")
    print(f"Local model available at: {LOCAL_MODEL_DIR}")
    print(f"Metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    main()
```

Explications importantes :

- `load_training_data()` reconstruit les donnees d'entree du modele en retirant la cible ;
- `LinearSVC` est encapsule dans une `Pipeline` avec `StandardScaler`, ce qui est une bonne pratique pour serialiser preprocessing + modele ensemble ;
- `infer_signature()` capture le schema de l'entree et de la sortie pour MLflow ;
- l'utilisation d'un dossier tampon `_download` evite de melanger l'artefact du modele avec les autres fichiers deja presents dans `artifacts/model` ;
- `metadata.json` sert de pont entre l'export et le runtime de l'API.

Pourquoi le dossier tampon etait necessaire :

Avant correction, le telechargement dans `artifacts/model` pouvait produire une structure incoherente avec la valeur `current` attendue par la metadata. Le staging rend le processus deterministe.

### 6.4 `app/ml/preprocess.py`

Role du fichier :

- transformer un payload metier en vecteur final de features aligne sur le modele exporte.

Modifications apportees :

- ajout de mappings de normalisation pour `genre`, `statut_marital`, `departement`, `frequence_deplacement`, `poste`, `domaine_etude` ;
- ajout d'une logique de repli vers `Autre` pour les categories inconnues ;
- ajout d'un cast final des colonnes vers les bons types `int64` ou `float64`.

Exemple des ajouts structurants :

```python
GENRE_MAPPING = {
    "M": 1,
    "MALE": 1,
    "HOMME": 1,
    "F": 0,
    "FEMALE": 0,
    "FEMME": 0,
}
```

```python
def normalize_genre(value: str | int) -> int:
    if isinstance(value, (int, float)):
        return int(value)

    normalized = GENRE_MAPPING.get(value.strip().upper())
    if normalized is None:
        raise ValueError(f"Genre non supporte pour la prediction: {value}")
    return normalized
```

```python
df = pd.DataFrame([final_row], columns=expected_features)

for feature in expected_features:
    if feature in INTEGER_FEATURES:
        df[feature] = df[feature].astype("int64")
    else:
        df[feature] = df[feature].astype("float64")

return df
```

Pourquoi ces parties sont importantes :

- elles assurent que l'API accepte un vocabulaire metier plus naturel ;
- elles rendent la prediction compatible avec le schema MLflow ;
- elles limitent les erreurs de production dues aux categories ou types inattendus.

### 6.5 `docs/p5_trace.md`

Role du fichier :

- formaliser la trace detaillee du travail realise dans cette discussion ;
- servir de document de synthese technique et pedagogique.

## 7. Interfaces tierces et manipulations externes

Dans cette discussion precise, aucune manipulation n'a ete realisee sur :

- GitHub ;
- une plateforme cloud ;
- une interface MLflow web ;
- Docker Desktop ;
- Render, Heroku, Azure, AWS ou GCP ;
- une base de donnees via interface graphique.

Les interactions externes ont ete limitees a :

- l'installation locale d'un package Python (`pypdf`) via `pip` ;
- la lecture d'un PDF local situe sur le Bureau.

Il est important de l'ecrire explicitement pour rester fidele a la realite de la seance.

## 8. Resultat obtenu

Commande de verification finale :

```powershell
uv run pytest -q
```

Resultat :

```text
5 passed in 13.69s
```

Interpretation :

- la configuration ne bloque plus la collecte des tests ;
- l'endpoint de prediction renvoie a nouveau une reponse 200 sur le cas valide ;
- le modele MLflow est charge correctement ;
- le preprocessing produit des donnees compatibles avec le schema exporte.

## 9. Erreurs courantes du meme type qui auraient pu se produire

Cette section ouvre sur des erreurs frequentes en deploiement ML, meme si elles n'ont pas toutes ete observees ici.

### 9.1 Derive entre preprocessing d'entrainement et preprocessing d'inference

Exemple :

- le notebook transforme une variable categorielle ;
- l'API reproduit cette logique "a la main" mais oublie une categorie.

Effet :

- predictions incoherentes ;
- erreur de schema ;
- performance degradee.

Bonne pratique :

- embarquer le preprocessing directement dans la pipeline serialisee quand c'est possible ;
- ou stocker explicitement les mappings de reference de maniere versionnee.

### 9.2 Artefacts MLflow incomplets

Exemple :

- `MLmodel` absent ;
- chemin de `model.pkl` incorrect ;
- metadata de projet non synchronisee avec le vrai dossier exporte.

Effet :

- l'API ne peut plus charger le modele ;
- le deploiement echoue malgre un entrainement reussi.

Bonne pratique :

- verifier l'artefact exporte juste apres generation ;
- fixer une convention stable de stockage.

### 9.3 Incoherence entre test payload et vocabulaire attendu

Exemple :

- les tests envoient `Travel_Rarely` ;
- le preprocessing attend `Occasionnel`.

Effet :

- colonnes one-hot jamais activees ;
- prediction degradee ou schema invalide.

Bonne pratique :

- documenter le contrat d'API ;
- centraliser les mappings de valeurs ;
- tester plusieurs variantes d'entree.

### 9.4 Variables d'environnement parasites

Exemple :

- `DEBUG`, `ENV`, `DATABASE_URL` ou `PORT` deja definies sur la machine.

Effet :

- comportement local incomprehensible ;
- tests qui passent chez une personne et echouent chez une autre.

Bonne pratique :

- prefixer les variables du projet ;
- definir un `.env.example` ;
- documenter les variables obligatoires.

### 9.5 Encodage et accents

Exemple :

- valeurs `Marié(e)` ou chemins de fichiers avec caracteres accentues.

Effet :

- erreurs de comparaison de chaines ;
- problemes de lecture/chargement selon le shell ou la plateforme.

Bonne pratique :

- utiliser UTF-8 explicitement ;
- centraliser la normalisation ;
- tester les chemins et categories accentues sur Windows.

## 10. Big picture du processus

La vue d'ensemble du travail realise peut se resumer ainsi :

1. On part d'un symptome visible : un test ne passe pas.
2. On reproduit l'erreur dans l'environnement reel.
3. On remonte la chaine complete du endpoint jusqu'au modele.
4. On corrige d'abord les blocages de configuration.
5. On corrige ensuite l'alignement entre export MLflow et chargement runtime.
6. On corrige enfin le contrat entre payload API et schema strict du modele.
7. On revalide l'ensemble par les tests.

Ce processus est typique d'un projet de deploiement ML : la qualite du systeme ne depend pas seulement du modele, mais de tout l'ecosysteme autour :

- configuration ;
- serialisation ;
- convention de stockage ;
- contrat d'API ;
- tests ;
- robustesse des transformations.

## 11. Repertoire des outils utilises et de leur role

### 11.1 FastAPI

Role dans le projet :

- exposer les endpoints HTTP ;
- offrir une interface de prediction exploitable.

Elements utilises ici :

- route `/api/v1/predict` ;
- `TestClient` pour les tests d'API.

Elements frequents non utilises ici :

- dependencies injection avancee ;
- middleware custom ;
- auth ;
- background tasks ;
- OpenAPI personnalisee.

### 11.2 Pydantic / Pydantic Settings

Role dans le projet :

- valider les payloads ;
- typer les sorties ;
- charger la configuration.

Elements utilises ici :

- `BaseModel` ;
- `Field` ;
- `field_validator` ;
- `BaseSettings` ;
- `SettingsConfigDict`.

Elements frequents non utilises ici :

- validateurs de modele globaux ;
- alias complexes ;
- secret management ;
- settings multi-environnements plus pousses.

### 11.3 Pandas

Role dans le projet :

- charger les datasets ;
- construire le DataFrame de prediction ;
- verifier colonnes et types.

Elements utilises ici :

- `read_csv` ;
- `DataFrame` ;
- `astype`.

Elements frequents non utilises ici :

- merges ;
- pipelines de transformation plus complexes ;
- serialisation parquet.

### 11.4 scikit-learn

Role dans le projet :

- entrainer le modele ;
- organiser le preprocessing simple et le classifieur dans une pipeline.

Elements utilises ici :

- `Pipeline` ;
- `StandardScaler` ;
- `LinearSVC`.

Elements frequents non utilises ici :

- `ColumnTransformer` ;
- encoders dedies ;
- cross-validation ;
- calibration des scores ;
- model selection ;
- persistence hors MLflow.

### 11.5 MLflow

Role dans le projet :

- logger le modele ;
- enregistrer sa signature ;
- fournir un format standard de chargement.

Elements utilises ici :

- `mlflow.set_tracking_uri` ;
- `mlflow.set_experiment` ;
- `mlflow.start_run` ;
- `mlflow.sklearn.log_model` ;
- `infer_signature` ;
- `download_artifacts` ;
- `mlflow.pyfunc.load_model`.

Elements frequents non utilises ici :

- model registry distant ;
- stages ou aliases ;
- tracking server distant ;
- comparaison d'experiences ;
- serving MLflow.

### 11.6 Pytest

Role dans le projet :

- verifier la non regression de l'application.

Elements utilises ici :

- execution simple de suite de tests ;
- test endpoint HTTP ;
- test configuration.

Elements frequents non utilises ici :

- fixtures plus riches ;
- parametrization avancee ;
- mocks ;
- couverture detaillee ;
- tests d'integration multi-services.

### 11.7 uv

Role dans le projet :

- executer les commandes dans l'environnement du projet.

Elements utilises ici :

- `uv run pytest ...` ;
- `uv run python -c ...`.

Elements frequents non utilises ici :

- verrouillage plus poussee des dependances ;
- gestion d'environnements multiples ;
- workflows CI complets bases sur `uv`.

### 11.8 pip

Role dans cette discussion :

- installation ponctuelle de `pypdf`.

Elements utilises ici :

- `python -m pip install --user pypdf`.

Elements frequents non utilises ici :

- requirements dedies doc ;
- environnement virtuel separe pour l'analyse documentaire.

## 12. Ouvertures : autres manieres de faire et pistes d'amelioration

### 12.1 Emballer tout le preprocessing dans la pipeline de modele

Ici, une partie importante du preprocessing d'inference est codee dans l'API. Une alternative plus robuste serait :

- serialiser une pipeline scikit-learn complete incluant les transformations categorielles et numeriques ;
- reduire au minimum la logique de reconstruction de features dans l'API.

Avantage :

- moins de derive entre entrainement et inference ;
- moins de logique metier dupliquee.

### 12.2 Utiliser un encodeur explicite des categories

Au lieu d'ecrire des mappings manuels, on pourrait :

- apprendre les categories avec un `OneHotEncoder` ;
- versionner ses categories ;
- exposer un contrat d'entree plus stable.

Cela serait particulierement pertinent si le modele evolue ou si le nombre de categories augmente.

### 12.3 Mieux versionner la metadata du modele

La metadata actuelle contient :

- un nom ;
- une version ;
- un seuil ;
- une liste de features ;
- un chemin local.

On pourrait enrichir cela avec :

- hash d'artefact ;
- date d'entrainement ;
- metriques principales ;
- version du preprocessing ;
- schema d'entree metier.

### 12.4 Ajouter des tests plus representatifs

Tests supplementaires utiles :

- prediction avec categories inconnues ;
- prediction avec accents ;
- test d'absence du dossier MLflow ;
- test du script d'export lui-meme ;
- test de non regression sur les types du DataFrame final.

### 12.5 Passer a un modele probabiliste ou calibrer le score

Le `LinearSVC` fournit ici un `decision_function`, pas une probabilite naturelle. Pour d'autres usages, on pourrait preferer :

- `LogisticRegression` ;
- calibration de score ;
- gradient boosting ;
- modele arbre interpretable ;
- modele plus complexe si la performance le justifie.

Le bon choix depend du besoin :

- score interpretable ;
- probabilite exploitable ;
- performance maximale ;
- explicabilite ;
- contraintes de latence.

### 12.6 Industrialiser davantage le deploiement

Hors contraintes pedagogiques, on pourrait ajouter :

- conteneurisation Docker ;
- CI/CD ;
- registry de modele distant ;
- observabilite ;
- monitoring de derive ;
- journalisation des predictions ;
- gestion de secrets ;
- documentation d'API plus complete.

## 13. Conclusion

Cette discussion a permis de remettre en etat la chaine complete de prediction du projet P5, non pas par un correctif unique, mais par une remise en coherence de plusieurs couches :

- la configuration applicative ;
- le chargement du modele MLflow ;
- le script d'export ;
- la transformation des donnees d'entree ;
- la conformite stricte des types de features.

Le point essentiel a retenir est le suivant : dans un projet de deploiement ML, un modele "fonctionnel" ne suffit pas. Il faut aussi que l'API parle le bon langage metier, que les artefacts soient au bon endroit, que la configuration soit stable, et que les tests couvrent reellement la chaine complete.

Le resultat final est concret :

- les tests passent ;
- le flux de prediction est de nouveau operationnel ;
- la structure du projet est plus robuste ;
- les causes des erreurs sont comprises et documentees.

Ce type de trace detaillee est utile pour la soutenance, pour la redaction du portfolio, et pour montrer une comprehension complete du cycle de deploiement d'un modele de machine learning.
