"""Script d'entraînement et d'export du modèle vers MLflow.

L'objectif est de produire un artefact stable exploitable par l'API, avec
une metadata applicative complémentaire. Ce script rejoue une version
compacte du pipeline de préparation du modèle final du projet.
"""

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
    """Charge le dataset modèle puis sépare les variables explicatives et la cible."""
    df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "df_MODEL.csv")

    target_col = "a_quitte_l_entreprise"
    cols_to_drop = [target_col, "id_employee"]
    X = df.drop(columns=cols_to_drop, errors="ignore")
    y = df[target_col]
    return X, y


def build_model() -> Pipeline:
    """Construit la pipeline scikit-learn exportée dans MLflow."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearSVC(
            random_state=42,
            dual="auto",
            max_iter=100000,
        )),
    ])


def main() -> None:
    """Entraîne, loggue et exporte le modèle au format MLflow."""
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

    # On télécharge d'abord dans un dossier tampon pour éviter de mélanger
    # l'artefact MLflow et les autres fichiers du dossier `artifacts/model`.
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
