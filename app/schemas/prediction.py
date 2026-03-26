from __future__ import annotations

"""Schemas Pydantic de l'API de prediction.

Ces schemas servent a la fois a :
- valider les donnees entrantes et sortantes ;
- documenter automatiquement l'API dans OpenAPI/Swagger ;
- garder un contrat metier clair entre le client et l'API.
"""

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
