"""Script de peuplement de la table source employees.

Le but est de fusionner les trois extraits metier du projet P4 puis
d'insérer un dataset source cohérent dans la base. Le script est compatible
avec SQLite en local et PostgreSQL via `P5_DATABASE_URL`.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import delete, func, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.models import EmployeeSource
from app.db.session import SessionLocal


RAW_DIR = PROJECT_ROOT / "data" / "raw"
SIRH_PATH = RAW_DIR / "extrait_sirh.csv"
EVAL_PATH = RAW_DIR / "extrait_eval.csv"
SONDAGE_PATH = RAW_DIR / "extrait_sondage.csv"


def parse_bool(value: str, truthy: set[str]) -> bool:
    """Convertit une representation textuelle simple en booleen."""
    return str(value).strip().upper() in truthy


def parse_percentage(value: str) -> float:
    """Transforme une valeur de type `11 %` en flottant exploitable."""
    cleaned = str(value).replace("%", "").strip()
    return float(cleaned)


def load_raw_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Charge les trois extraits metier sources du projet."""
    sirh = pd.read_csv(SIRH_PATH)
    eval_df = pd.read_csv(EVAL_PATH)
    sondage = pd.read_csv(SONDAGE_PATH)
    return sirh, eval_df, sondage


def build_employee_source_dataframe() -> pd.DataFrame:
    """Fusionne et normalise les trois sources dans un DataFrame unique."""
    sirh, eval_df, sondage = load_raw_sources()

    if not (len(sirh) == len(eval_df) == len(sondage)):
        raise ValueError(
            "Les trois extraits sources n'ont pas le meme nombre de lignes. "
            "La fusion par index ne peut pas etre garantie."
        )

    merged = pd.concat(
        [
            sirh.reset_index(drop=True),
            eval_df.reset_index(drop=True),
            sondage.reset_index(drop=True),
        ],
        axis=1,
    )

    merged["heure_supplementaires"] = merged["heure_supplementaires"].map(
        lambda value: parse_bool(value, {"OUI", "YES", "TRUE", "1"})
    )
    merged["a_quitte_l_entreprise"] = merged["a_quitte_l_entreprise"].map(
        lambda value: parse_bool(value, {"OUI", "YES", "TRUE", "1"})
    )
    merged["ayant_enfants"] = merged["ayant_enfants"].map(
        lambda value: parse_bool(value, {"Y", "YES", "TRUE", "1"})
    )
    merged["augementation_salaire_precedente"] = merged[
        "augementation_salaire_precedente"
    ].map(parse_percentage)

    return merged


def seed_employee_source() -> int:
    """Recharge la table `employees_source` a partir des CSV bruts."""
    dataset = build_employee_source_dataframe()
    records = dataset.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(delete(EmployeeSource))
        db.bulk_insert_mappings(EmployeeSource, records)
        db.commit()

        inserted_rows = db.scalar(select(func.count()).select_from(EmployeeSource))

    return len(records) if inserted_rows is None else int(inserted_rows)


def main() -> None:
    """Charge les donnees source dans la base configuree."""
    inserted_rows = seed_employee_source()
    print(f"Employee source dataset loaded successfully: {inserted_rows} rows.")


if __name__ == "__main__":
    main()
