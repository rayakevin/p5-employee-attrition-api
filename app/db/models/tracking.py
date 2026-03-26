from __future__ import annotations

"""Modèles ORM dédiés à la traçabilité des prédictions.

Ces tables séparent la requête métier, le résultat du modèle et les logs
techniques. Cette séparation est utile pour auditer l'usage de l'API et
préparer une vraie traçabilité applicative.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeSource(Base):
    """Stocke une vision fusionnee des donnees source employees du projet."""

    __tablename__ = "employees_source"

    id_employee: Mapped[int] = mapped_column(Integer, primary_key=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    genre: Mapped[str] = mapped_column(String(20), nullable=False)
    revenu_mensuel: Mapped[float] = mapped_column(Float, nullable=False)
    statut_marital: Mapped[str] = mapped_column(String(50), nullable=False)
    departement: Mapped[str] = mapped_column(String(100), nullable=False)
    poste: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre_experiences_precedentes: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_heures_travailless: Mapped[float] = mapped_column(Float, nullable=False)
    annee_experience_totale: Mapped[float] = mapped_column(Float, nullable=False)
    annees_dans_l_entreprise: Mapped[float] = mapped_column(Float, nullable=False)
    annees_dans_le_poste_actuel: Mapped[float] = mapped_column(Float, nullable=False)
    satisfaction_employee_environnement: Mapped[int] = mapped_column(Integer, nullable=False)
    note_evaluation_precedente: Mapped[float] = mapped_column(Float, nullable=False)
    niveau_hierarchique_poste: Mapped[int] = mapped_column(Integer, nullable=False)
    satisfaction_employee_nature_travail: Mapped[int] = mapped_column(Integer, nullable=False)
    satisfaction_employee_equipe: Mapped[int] = mapped_column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso: Mapped[int] = mapped_column(Integer, nullable=False)
    eval_number: Mapped[str] = mapped_column(String(50), nullable=False)
    note_evaluation_actuelle: Mapped[float] = mapped_column(Float, nullable=False)
    heure_supplementaires: Mapped[bool] = mapped_column(nullable=False)
    augementation_salaire_precedente: Mapped[float] = mapped_column(Float, nullable=False)
    a_quitte_l_entreprise: Mapped[bool] = mapped_column(nullable=False)
    nombre_participation_pee: Mapped[int] = mapped_column(Integer, nullable=False)
    nb_formations_suivies: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_employee_sous_responsabilite: Mapped[int] = mapped_column(Integer, nullable=False)
    code_sondage: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_domicile_travail: Mapped[float] = mapped_column(Float, nullable=False)
    niveau_education: Mapped[int] = mapped_column(Integer, nullable=False)
    domaine_etude: Mapped[str] = mapped_column(String(100), nullable=False)
    ayant_enfants: Mapped[bool] = mapped_column(nullable=False)
    frequence_deplacement: Mapped[str] = mapped_column(String(50), nullable=False)
    annees_depuis_la_derniere_promotion: Mapped[float] = mapped_column(Float, nullable=False)
    annes_sous_responsable_actuel: Mapped[float] = mapped_column(Float, nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class PredictionRequest(Base):
    """Stocke le payload brut reçu par l'API et son contexte d'appel."""

    __tablename__ = "prediction_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_channel: Mapped[str] = mapped_column(String(50), default="api", nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    prediction_result: Mapped["PredictionResult | None"] = relationship(
        back_populates="prediction_request",
        cascade="all, delete-orphan",
        uselist=False,
    )
    audit_logs: Mapped[list["ApiAuditLog"]] = relationship(
        back_populates="prediction_request",
        cascade="all, delete-orphan",
    )


class PredictionResult(Base):
    """Stocke la sortie produite par le modèle pour une requête donnée."""

    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_requests.id"),
        nullable=False,
        unique=True,
    )
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    prediction_request: Mapped["PredictionRequest"] = relationship(
        back_populates="prediction_result"
    )


class ApiAuditLog(Base):
    """Conserve les événements techniques associés à un appel API."""

    __tablename__ = "api_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("prediction_requests.id"),
        nullable=True,
    )
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    prediction_request: Mapped["PredictionRequest | None"] = relationship(
        back_populates="audit_logs"
    )
