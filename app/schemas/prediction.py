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
    genre: str = Field(
        ...,
        description="Genre de l'employe. Valeurs conseillees : Homme, Femme. "
        "Les codes bruts M et F sont aussi acceptes.",
    )
    revenu_mensuel: float = Field(..., gt=0, description="Revenu mensuel brut")
    statut_marital: str = Field(
        ...,
        description="Statut marital. Valeurs issues des CSV bruts : "
        "Célibataire, Marié(e), Divorcé(e).",
    )
    departement: str = Field(
        ...,
        description="Departement. Valeurs issues des CSV bruts : "
        "Commercial, Consulting, Ressources Humaines.",
    )
    poste: str = Field(
        ...,
        description="Poste. Valeurs conseillees : Assistant de Direction, "
        "Cadre Commercial, Consultant, Directeur Technique, Manager, "
        "Représentant Commercial, Ressources Humaines, Senior Manager, "
        "Tech Lead.",
    )
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
    heure_supplementaires: str | int | bool = Field(
        ...,
        description="Heures supplementaires. Valeurs conseillees : Oui, Non. "
        "Les formats 1/0 et True/False restent acceptes.",
    )
    augementation_salaire_precedente: float = Field(..., ge=0, le=100)
    nombre_participation_pee: int = Field(..., ge=0, le=20)
    nb_formations_suivies: int = Field(..., ge=0, le=50)
    nombre_employee_sous_responsabilite: int = Field(..., ge=0, le=500)
    distance_domicile_travail: float = Field(..., ge=0, le=500)
    niveau_education: int = Field(..., ge=1, le=10)
    domaine_etude: str = Field(
        ...,
        description="Domaine d'etude. Valeurs issues des CSV bruts : Autre, "
        "Entrepreunariat, Infra & Cloud, Marketing, Ressources Humaines, "
        "Transformation Digitale.",
    )
    ayant_enfants: str | int | bool = Field(
        ...,
        description="Presence d'enfants. Valeurs conseillees : Oui, Non. "
        "Les codes bruts Y/N et les formats 1/0 restent acceptes.",
    )
    frequence_deplacement: str = Field(
        ...,
        description="Frequence de deplacement. Valeurs issues des CSV bruts : "
        "Aucun, Frequent, Occasionnel.",
    )
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

    @field_validator("heure_supplementaires", "ayant_enfants", mode="before")
    @classmethod
    def validate_binary_flags(cls, value: str | int | bool) -> str | int | bool:
        """Accepte les formats metier usuels avant normalisation ulterieure."""
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value not in {0, 1}:
                raise ValueError("La valeur doit etre binaire : 0 ou 1.")
            return value
        if isinstance(value, str):
            cleaned_value = value.strip()
            if not cleaned_value:
                raise ValueError("La valeur ne peut pas etre vide.")
            return cleaned_value
        raise TypeError("La valeur doit etre un booleen, un entier binaire ou une chaine.")


class PredictionOutput(BaseModel):
    """Decrit la reponse metier renvoyee par l'API de prediction."""

    prediction: int = Field(..., description="Classe predite : 0 ou 1")
    score: float = Field(..., description="Score brut du modele")
    threshold: float = Field(..., description="Seuil de decision applique")
    model_version: str = Field(..., description="Version du modele")
    model_name: str = Field(..., description="Nom du modele")
