"""Tests d'integration du chargement des donnees source."""

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import EmployeeSource
import scripts.seed_data as seed_data


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)
Base.metadata.create_all(bind=engine)


def reset_employee_source() -> None:
    """Vide la table employees_source avant chaque test."""
    with TestingSessionLocal() as db:
        db.execute(delete(EmployeeSource))
        db.commit()


def test_build_employee_source_dataframe_merges_and_normalizes_sources() -> None:
    """Verifie la fusion des trois fichiers bruts et les principales conversions."""
    dataset = seed_data.build_employee_source_dataframe()

    assert dataset.shape[0] == 1470
    assert "id_employee" in dataset.columns
    assert "heure_supplementaires" in dataset.columns
    assert "a_quitte_l_entreprise" in dataset.columns
    assert "ayant_enfants" in dataset.columns

    first_row = dataset.iloc[0]
    second_row = dataset.iloc[1]

    assert first_row["id_employee"] == 1
    assert bool(first_row["heure_supplementaires"]) is True
    assert bool(first_row["a_quitte_l_entreprise"]) is True
    assert bool(first_row["ayant_enfants"]) is True
    assert first_row["augementation_salaire_precedente"] == 11.0
    assert bool(second_row["heure_supplementaires"]) is False


def test_seed_employee_source_inserts_rows_in_database(monkeypatch) -> None:
    """Verifie que le script de seed recharge completement la table source."""
    reset_employee_source()
    monkeypatch.setattr(seed_data, "SessionLocal", TestingSessionLocal)

    inserted_rows = seed_data.seed_employee_source()

    assert inserted_rows == 1470

    with TestingSessionLocal() as db:
        rows = db.scalars(select(EmployeeSource)).all()

    assert len(rows) == 1470
    assert rows[0].id_employee == 1
    assert rows[0].heure_supplementaires is True
    assert rows[0].a_quitte_l_entreprise is True
    assert rows[0].augementation_salaire_precedente == 11.0
