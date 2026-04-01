"""Interface Streamlit portfolio pour la prediction d'attrition.

Le frontend reste volontairement léger :
- il collecte un profil métier ;
- il appelle l'API FastAPI pour la prediction ;
- il appelle ensuite l'endpoint d'explication locale du score ;
- il affiche les résultats dans une présentation plus portfolio.
"""

from __future__ import annotations

import os
from typing import Any, Callable

import altair as alt
import httpx
import pandas as pd
import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

APP_ENVIRONMENT = os.getenv("P5_ENVIRONMENT", "development").lower()
DEFAULT_API_BASE_URL = os.getenv(
    "P5_API_BASE_URL",
    "http://127.0.0.1:8000" if APP_ENVIRONMENT == "development"
    else "https://rayakevin-p5-employee-attrition-api.hf.space",
)
DEFAULT_API_KEY = os.getenv("P5_API_KEY")
if not DEFAULT_API_KEY and APP_ENVIRONMENT == "development":
    DEFAULT_API_KEY = "p5-dev-local-key"

GENRES = ["Homme", "Femme"]
STATUTS_MARITAUX = ["Célibataire", "Marié(e)", "Divorcé(e)"]
DEPARTEMENTS = ["Commercial", "Consulting", "Ressources Humaines"]
POSTES = [
    "Assistant de Direction",
    "Cadre Commercial",
    "Consultant",
    "Directeur Technique",
    "Manager",
    "Représentant Commercial",
    "Ressources Humaines",
    "Senior Manager",
    "Tech Lead",
]
DOMAINES_ETUDE = [
    "Autre",
    "Entrepreunariat",
    "Infra & Cloud",
    "Marketing",
    "Ressources Humaines",
    "Transformation Digitale",
]
FREQUENCES_DEPLACEMENT = ["Aucun", "Frequent", "Occasionnel"]
CHOIX_OUI_NON = ["Oui", "Non"]

FORM_DEFAULTS: dict[str, Any] = {
    "age": 35,
    "genre": "Homme",
    "revenu_mensuel": 4500.0,
    "statut_marital": "Marié(e)",
    "departement": "Consulting",
    "poste": "Consultant",
    "nombre_experiences_precedentes": 3,
    "annee_experience_totale": 12.0,
    "annees_dans_l_entreprise": 7.0,
    "annees_dans_le_poste_actuel": 4.0,
    "satisfaction_employee_environnement": 3,
    "note_evaluation_precedente": 3.0,
    "niveau_hierarchique_poste": 2,
    "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_equilibre_pro_perso": 2,
    "note_evaluation_actuelle": 4.0,
    "heure_supplementaires": "Oui",
    "augementation_salaire_precedente": 0.12,
    "nombre_participation_pee": 1,
    "nb_formations_suivies": 3,
    "nombre_employee_sous_responsabilite": 0,
    "distance_domicile_travail": 12.0,
    "niveau_education": 3,
    "domaine_etude": "Infra & Cloud",
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 2.0,
    "annes_sous_responsable_actuel": 3.0,
}

PROFILE_LIBRARY: dict[str, dict[str, Any]] = {
    "Profil par défaut": FORM_DEFAULTS,
    "Profil senior stable": {
        **FORM_DEFAULTS,
        "age": 46,
        "genre": "Femme",
        "revenu_mensuel": 6900.0,
        "poste": "Senior Manager",
        "annee_experience_totale": 22.0,
        "annees_dans_l_entreprise": 14.0,
        "annees_dans_le_poste_actuel": 6.0,
        "niveau_hierarchique_poste": 4,
        "note_evaluation_precedente": 4.0,
        "note_evaluation_actuelle": 4.0,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 0.16,
        "distance_domicile_travail": 7.0,
        "frequence_deplacement": "Aucun",
        "annees_depuis_la_derniere_promotion": 1.0,
        "annes_sous_responsable_actuel": 5.0,
    },
    "Profil junior instable": {
        **FORM_DEFAULTS,
        "age": 24,
        "genre": "Femme",
        "revenu_mensuel": 3202.0,
        "statut_marital": "Célibataire",
        "departement": "Commercial",
        "poste": "Représentant Commercial",
        "nombre_experiences_precedentes": 1,
        "annee_experience_totale": 6.0,
        "annees_dans_l_entreprise": 5.0,
        "annees_dans_le_poste_actuel": 3.0,
        "satisfaction_employee_environnement": 1,
        "note_evaluation_precedente": 3.0,
        "satisfaction_employee_nature_travail": 2,
        "satisfaction_employee_equipe": 2,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3.0,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": 0.16,
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 4,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 1.0,
        "niveau_education": 1,
        "domaine_etude": "Entrepreunariat",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 1.0,
        "annes_sous_responsable_actuel": 4.0,
    },
}

BATCH_REQUIRED_COLUMNS = list(FORM_DEFAULTS.keys())


def configure_page() -> None:
    """Configure la page Streamlit."""
    st.set_page_config(
        page_title="Portfolio P5 - Attrition",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_styles() -> None:
    """Ajoute un style dashboard inspiré des démos Streamlit modernes."""
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            display: none;
        }
        .stAppToolbar {
            display: none;
        }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(84, 112, 198, 0.10) 0%, transparent 28%),
                radial-gradient(circle at top left, rgba(43, 179, 150, 0.08) 0%, transparent 24%),
                linear-gradient(180deg, #0f172a 0%, #111827 45%, #172033 100%);
            color: #e5eefb;
        }
        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(13, 22, 40, 0.98) 0%, rgba(17, 24, 39, 0.98) 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.14);
        }
        section[data-testid="stSidebar"] * {
            color: #e5eefb;
        }
        .block-container {
            max-width: 1280px;
            padding-top: 0.75rem;
            padding-bottom: 2rem;
        }
        .hero-card, .panel-card, .metric-panel {
            background: linear-gradient(180deg, rgba(21, 31, 53, 0.96) 0%, rgba(17, 24, 39, 0.96) 100%);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 24px;
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.30);
            color: #e5eefb;
        }
        .hero-card {
            padding: 1.7rem 1.8rem;
            margin-bottom: 1rem;
        }
        .panel-card {
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .metric-panel {
            padding: 1rem 1.2rem;
            min-height: 118px;
        }
        .eyebrow {
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.72rem;
            color: #93c5fd;
            margin: 0 0 0.4rem 0;
        }
        .hero-title {
            margin: 0 0 0.75rem 0;
            font-size: 2.35rem;
            line-height: 1.02;
            color: white;
        }
        .hero-copy {
            margin: 0;
            max-width: 860px;
            color: #c9d7ee;
            font-size: 1.03rem;
            line-height: 1.65;
        }
        .status-chip {
            display: inline-block;
            padding: 0.42rem 0.82rem;
            border-radius: 999px;
            background: rgba(96, 165, 250, 0.12);
            border: 1px solid rgba(96, 165, 250, 0.24);
            color: #dbeafe;
            font-size: 0.84rem;
            font-weight: 700;
            margin-right: 0.45rem;
            margin-bottom: 0.45rem;
        }
        .risk-low {
            color: #34d399;
            font-weight: 800;
        }
        .risk-high {
            color: #f97316;
            font-weight: 800;
        }
        .caption-soft {
            color: #a7b6d0;
            font-size: 0.92rem;
        }
        .explain-card {
            background: linear-gradient(180deg, rgba(18, 26, 45, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 22px;
            padding: 1rem 1.15rem;
            min-height: 220px;
        }
        .section-title {
            color: #f8fafc;
            margin: 0 0 0.35rem 0;
            font-size: 1.08rem;
            font-weight: 700;
        }
        .section-copy {
            color: #cbd5e1;
            margin: 0 0 0.75rem 0;
            font-size: 0.92rem;
        }
        div[data-testid="stMetricValue"] {
            color: white;
        }
        div[data-testid="stMetricLabel"] {
            color: #93a3bf;
        }
        div[data-testid="stTabs"] {
            margin-top: 0.35rem;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px;
            background: rgba(20, 31, 52, 0.96);
            color: #cbd5e1;
            border: 1px solid rgba(96, 165, 250, 0.18);
            font-weight: 700;
            padding: 0.55rem 1rem;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, rgba(30, 58, 138, 0.78) 0%, rgba(29, 78, 216, 0.38) 100%);
            color: #f8fafc;
            border-color: rgba(147, 197, 253, 0.45);
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.18);
        }
        div[data-testid="stTabs"] button[role="tab"]:hover {
            color: #f8fafc;
            border-color: rgba(147, 197, 253, 0.34);
        }
        [data-testid="stWidgetLabel"] p,
        label,
        .stSlider label,
        .stNumberInput label,
        .stSelectbox label {
            color: #dbe7fb !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] .stTextInput input,
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
            background: rgba(15, 23, 42, 0.9);
            color: #f8fafc;
            border: 1px solid rgba(96, 165, 250, 0.25);
        }
        div[data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {
            background: rgba(20, 31, 52, 0.96) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(96, 165, 250, 0.22) !important;
        }
        [data-testid="stNumberInput"] button,
        [data-testid="stNumberInput"] button:hover,
        [data-testid="stNumberInput"] button:focus {
            background: rgba(20, 31, 52, 0.96) !important;
            color: #dbeafe !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stSelectbox"] svg,
        [data-testid="stNumberInput"] svg {
            fill: #dbeafe !important;
        }
        .stButton > button,
        .stFormSubmitButton > button {
            background: linear-gradient(180deg, #193258 0%, #142846 100%) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(96, 165, 250, 0.28) !important;
            border-radius: 12px !important;
        }
        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            background: linear-gradient(180deg, #22406d 0%, #183152 100%) !important;
            color: #ffffff !important;
            border-color: rgba(147, 197, 253, 0.38) !important;
        }
        .impact-list {
            margin-top: 0.85rem;
        }
        .impact-row {
            margin-bottom: 0.8rem;
        }
        .impact-head {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            font-size: 0.92rem;
            margin-bottom: 0.28rem;
            color: #e2e8f0;
        }
        .impact-label {
            font-weight: 600;
        }
        .impact-value {
            color: #cbd5e1;
            white-space: nowrap;
        }
        .impact-track {
            width: 100%;
            height: 10px;
            background: rgba(148, 163, 184, 0.16);
            border-radius: 999px;
            overflow: hidden;
        }
        .impact-fill-positive,
        .impact-fill-negative {
            height: 10px;
            border-radius: 999px;
        }
        .impact-fill-positive {
            background: linear-gradient(90deg, #fb923c 0%, #f97316 100%);
        }
        .impact-fill-negative {
            background: linear-gradient(90deg, #34d399 0%, #10b981 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Initialise explicitement l'état pour éviter les reruns incohérents."""
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL
    if "selected_profile" not in st.session_state:
        st.session_state.selected_profile = "Profil par défaut"
    if "last_payload" not in st.session_state:
        st.session_state.last_payload = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_explanation" not in st.session_state:
        st.session_state.last_explanation = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "batch_error" not in st.session_state:
        st.session_state.batch_error = None
    if "batch_source_df" not in st.session_state:
        st.session_state.batch_source_df = None
    if "batch_results_df" not in st.session_state:
        st.session_state.batch_results_df = None
    if "batch_payloads" not in st.session_state:
        st.session_state.batch_payloads = None
    if "batch_selected_employee_id" not in st.session_state:
        st.session_state.batch_selected_employee_id = None
    if "batch_selected_explanation" not in st.session_state:
        st.session_state.batch_selected_explanation = None

    for field_name, default_value in FORM_DEFAULTS.items():
        state_key = f"field_{field_name}"
        if state_key not in st.session_state:
            st.session_state[state_key] = default_value


def load_profile_into_state(profile_name: str) -> None:
    """Charge un profil de démonstration dans l'état des widgets."""
    profile = PROFILE_LIBRARY[profile_name]
    for field_name, field_value in profile.items():
        st.session_state[f"field_{field_name}"] = field_value
    st.session_state.selected_profile = profile_name
    st.session_state.last_error = None


@st.cache_data(ttl=20, show_spinner=False)
def check_api_health(api_base_url: str) -> tuple[bool, str]:
    """Teste la disponibilité de l'API cible."""
    try:
        response = httpx.get(f"{api_base_url}/health", timeout=8.0)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") == "ok":
            return True, "API disponible"
        return False, f"Réponse inattendue : {payload}"
    except Exception as exc:
        return False, str(exc)


def build_auth_headers() -> dict[str, str]:
    """Construit les en-tetes HTTP pour appeler l'API protegee."""
    if not DEFAULT_API_KEY:
        raise RuntimeError(
            "P5_API_KEY est obligatoire pour appeler l'API protegee."
        )
    return {"X-API-Key": DEFAULT_API_KEY}


def call_prediction_api(api_base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Appelle l'endpoint de prediction."""
    response = httpx.post(
        f"{api_base_url}/api/v1/predict",
        json=payload,
        headers=build_auth_headers(),
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def call_explain_api(api_base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Appelle l'endpoint d'explication locale du score."""
    response = httpx.post(
        f"{api_base_url}/api/v1/explain",
        json=payload,
        headers=build_auth_headers(),
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def call_batch_prediction_api(
    api_base_url: str,
    payloads: list[dict[str, Any]],
    chunk_size: int = 200,
    progress_callback: Callable[[int, int, int], None] | None = None,
) -> list[dict[str, Any]]:
    """Appelle l'endpoint batch en plusieurs paquets."""
    results: list[dict[str, Any]] = []
    total_payloads = len(payloads)
    with httpx.Client(timeout=120.0) as client:
        for start in range(0, len(payloads), chunk_size):
            chunk = payloads[start : start + chunk_size]
            response = client.post(
                f"{api_base_url}/api/v1/predict/batch",
                json={"rows": chunk},
                headers=build_auth_headers(),
            )
            response.raise_for_status()
            results.extend(response.json()["results"])
            if progress_callback is not None:
                progress_callback(min(start + len(chunk), total_payloads), total_payloads, len(chunk))
    return results


def render_header() -> None:
    """Affiche l'entête principal."""
    st.markdown(
        """
        <div class="hero-card">
            <p class="eyebrow">Portfolio P5 · Analyse du risque de départ</p>
            <h1 class="hero-title">Explorer le risque d'attrition employé</h1>
            <p class="hero-copy">
                Testez le modèle final sur des profils individuels ou sur un fichier
                complet, obtenez une décision immédiatement exploitable et visualisez
                les facteurs qui renforcent ou réduisent le risque de départ.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Affiche la barre latérale de pilotage."""
    st.sidebar.markdown("## Connexion API")
    api_base_url = st.sidebar.text_input(
        "URL de l'API",
        key="api_base_url",
        help="API locale FastAPI ou Space Hugging Face.",
    ).rstrip("/")

    is_healthy, message = check_api_health(api_base_url)
    if is_healthy:
        st.sidebar.success(message)
    else:
        st.sidebar.error(message)

    st.sidebar.markdown("## Profils de démonstration")
    if st.session_state.selected_profile not in PROFILE_LIBRARY:
        st.session_state.selected_profile = "Profil par défaut"

    selected_profile = st.sidebar.selectbox(
        "Charger un scénario",
        options=list(PROFILE_LIBRARY.keys()),
        index=list(PROFILE_LIBRARY.keys()).index(st.session_state.selected_profile),
    )
    if st.sidebar.button("Appliquer le profil", use_container_width=True):
        load_profile_into_state(selected_profile)
        st.rerun()

    st.sidebar.markdown("## Référence")
    st.sidebar.caption(
        "Le formulaire et l'explication locale restent strictement alignés sur le modèle final déployé."
    )
    return api_base_url


def render_context_panel() -> None:
    """Affiche un rappel sur le scope fonctionnel de l'écran."""
    st.markdown(
        """
        <div class="panel-card">
            <span class="status-chip">Simulation de profils</span>
            <span class="status-chip">Scoring en temps réel</span>
            <span class="status-chip">Modèle final déployé</span>
            <span class="status-chip">Lecture locale des facteurs</span>
            <p class="caption-soft" style="margin-top:0.7rem;">
                Le portfolio n'exécute pas le modèle lui-même. Il envoie les données
                à l'API du projet, qui applique le vrai preprocessing, calcule la
                prédiction et produit l'explication locale. Les résultats affichés ici
                correspondent donc au comportement réel du service déployé, sans
                décalage entre la démonstration visuelle et le moteur de scoring.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_batch_dataframe(uploaded_df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Prepare un fichier type df_EDA pour un scoring batch."""
    missing_columns = [
        column for column in BATCH_REQUIRED_COLUMNS if column not in uploaded_df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Colonnes manquantes pour le batch : " + ", ".join(missing_columns)
        )

    working_df = uploaded_df.copy()
    if "id_employee" not in working_df.columns:
        working_df["id_employee"] = range(1, len(working_df) + 1)

    payloads = working_df[BATCH_REQUIRED_COLUMNS].to_dict(orient="records")
    return working_df, payloads


def render_form() -> tuple[bool, dict[str, Any]]:
    """Affiche le formulaire principal et retourne le payload construit."""
    with st.form("prediction_form", clear_on_submit=False):
        st.subheader("Profil employé")
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.slider("Âge", 16, 65, key="field_age")
            genre = st.selectbox("Genre", GENRES, index=GENRES.index(st.session_state.field_genre))
            statut_marital = st.selectbox(
                "Statut marital",
                STATUTS_MARITAUX,
                index=STATUTS_MARITAUX.index(st.session_state.field_statut_marital),
            )
            niveau_education = st.slider("Niveau d'éducation", 1, 5, key="field_niveau_education")
            domaine_etude = st.selectbox(
                "Domaine d'étude",
                DOMAINES_ETUDE,
                index=DOMAINES_ETUDE.index(st.session_state.field_domaine_etude),
            )

        with col2:
            departement = st.selectbox(
                "Département",
                DEPARTEMENTS,
                index=DEPARTEMENTS.index(st.session_state.field_departement),
            )
            poste = st.selectbox("Poste", POSTES, index=POSTES.index(st.session_state.field_poste))
            revenu_mensuel = st.number_input(
                "Revenu mensuel brut",
                min_value=500.0,
                max_value=30000.0,
                step=100.0,
                key="field_revenu_mensuel",
            )
            nombre_experiences_precedentes = st.number_input(
                "Nombre d'expériences précédentes",
                min_value=0,
                max_value=20,
                step=1,
                key="field_nombre_experiences_precedentes",
            )
            nombre_employee_sous_responsabilite = st.number_input(
                "Nombre d'employés sous responsabilité",
                min_value=0,
                max_value=100,
                step=1,
                key="field_nombre_employee_sous_responsabilite",
            )
            niveau_hierarchique_poste = st.slider(
                "Niveau hiérarchique du poste",
                min_value=1,
                max_value=5,
                key="field_niveau_hierarchique_poste",
            )

        with col3:
            frequence_deplacement = st.selectbox(
                "Fréquence de déplacement",
                FREQUENCES_DEPLACEMENT,
                index=FREQUENCES_DEPLACEMENT.index(st.session_state.field_frequence_deplacement),
            )
            distance_domicile_travail = st.number_input(
                "Distance domicile-travail",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                key="field_distance_domicile_travail",
            )
            heure_supplementaires = st.selectbox(
                "Heures supplémentaires",
                CHOIX_OUI_NON,
                index=CHOIX_OUI_NON.index(st.session_state.field_heure_supplementaires),
            )
            nb_formations_suivies = st.number_input(
                "Nombre de formations suivies",
                min_value=0,
                max_value=20,
                step=1,
                key="field_nb_formations_suivies",
            )
            nombre_participation_pee = st.number_input(
                "Nombre de participations PEE",
                min_value=0,
                max_value=10,
                step=1,
                key="field_nombre_participation_pee",
            )

        st.subheader("Ancienneté et performance")
        col4, col5, col6 = st.columns(3)

        with col4:
            annee_experience_totale = st.number_input(
                "Années d'expérience totale",
                min_value=0.0,
                max_value=45.0,
                step=1.0,
                key="field_annee_experience_totale",
            )
            annees_dans_l_entreprise = st.number_input(
                "Années dans l'entreprise",
                min_value=0.0,
                max_value=45.0,
                step=1.0,
                key="field_annees_dans_l_entreprise",
            )
            annees_dans_le_poste_actuel = st.number_input(
                "Années dans le poste actuel",
                min_value=0.0,
                max_value=30.0,
                step=1.0,
                key="field_annees_dans_le_poste_actuel",
            )

        with col5:
            annees_depuis_la_derniere_promotion = st.number_input(
                "Années depuis la dernière promotion",
                min_value=0.0,
                max_value=20.0,
                step=1.0,
                key="field_annees_depuis_la_derniere_promotion",
            )
            annes_sous_responsable_actuel = st.number_input(
                "Années sous le responsable actuel",
                min_value=0.0,
                max_value=20.0,
                step=1.0,
                key="field_annes_sous_responsable_actuel",
            )

        with col6:
            note_evaluation_precedente = st.slider(
                "Note d'évaluation précédente",
                min_value=1.0,
                max_value=5.0,
                key="field_note_evaluation_precedente",
            )
            note_evaluation_actuelle = st.slider(
                "Note d'évaluation actuelle",
                min_value=1.0,
                max_value=5.0,
                key="field_note_evaluation_actuelle",
            )
            augementation_salaire_precedente = st.number_input(
                "Augmentation salariale précédente (fraction, ex. 0.12 = 12 %)",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                key="field_augementation_salaire_precedente",
            )

        st.subheader("Satisfaction")
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            satisfaction_employee_environnement = st.slider(
                "Satisfaction environnement", min_value=1, max_value=4, key="field_satisfaction_employee_environnement"
            )
        with col8:
            satisfaction_employee_nature_travail = st.slider(
                "Satisfaction nature du travail", min_value=1, max_value=4, key="field_satisfaction_employee_nature_travail"
            )
        with col9:
            satisfaction_employee_equipe = st.slider(
                "Satisfaction équipe", min_value=1, max_value=4, key="field_satisfaction_employee_equipe"
            )
        with col10:
            satisfaction_employee_equilibre_pro_perso = st.slider(
                "Équilibre pro / perso", min_value=1, max_value=4, key="field_satisfaction_employee_equilibre_pro_perso"
            )

        submitted = st.form_submit_button(
            "Lancer la prédiction",
            type="primary",
            use_container_width=True,
        )

    payload = {
        "age": age,
        "genre": genre,
        "revenu_mensuel": revenu_mensuel,
        "statut_marital": statut_marital,
        "departement": departement,
        "poste": poste,
        "nombre_experiences_precedentes": nombre_experiences_precedentes,
        "annee_experience_totale": annee_experience_totale,
        "annees_dans_l_entreprise": annees_dans_l_entreprise,
        "annees_dans_le_poste_actuel": annees_dans_le_poste_actuel,
        "satisfaction_employee_environnement": satisfaction_employee_environnement,
        "note_evaluation_precedente": note_evaluation_precedente,
        "niveau_hierarchique_poste": niveau_hierarchique_poste,
        "satisfaction_employee_nature_travail": satisfaction_employee_nature_travail,
        "satisfaction_employee_equipe": satisfaction_employee_equipe,
        "satisfaction_employee_equilibre_pro_perso": satisfaction_employee_equilibre_pro_perso,
        "note_evaluation_actuelle": note_evaluation_actuelle,
        "heure_supplementaires": heure_supplementaires,
        "augementation_salaire_precedente": augementation_salaire_precedente,
        "nombre_participation_pee": nombre_participation_pee,
        "nb_formations_suivies": nb_formations_suivies,
        "nombre_employee_sous_responsabilite": nombre_employee_sous_responsabilite,
        "distance_domicile_travail": distance_domicile_travail,
        "niveau_education": niveau_education,
        "domaine_etude": domaine_etude,
        "frequence_deplacement": frequence_deplacement,
        "annees_depuis_la_derniere_promotion": annees_depuis_la_derniere_promotion,
        "annes_sous_responsable_actuel": annes_sous_responsable_actuel,
    }
    return submitted, payload


def _contribution_frame(items: list[dict[str, Any]]) -> pd.DataFrame:
    """Convertit une liste de contributions en tableau lisible et trié."""
    if not items:
        return pd.DataFrame(columns=["Facteur", "Impact", "Contribution", "Valeur"])

    frame = pd.DataFrame(
        {
            "Facteur": [item["label"] for item in items],
            "Impact": [abs(float(item["contribution"])) for item in items],
            "Contribution": [float(item["contribution"]) for item in items],
            "Valeur": [float(item["value"]) for item in items],
        }
    )
    return frame.sort_values("Impact", ascending=False).reset_index(drop=True)


def render_contribution_bars(frame: pd.DataFrame, positive: bool) -> None:
    """Affiche un barchart horizontal trié par impact décroissant."""
    if frame.empty:
        return

    color = "#f97316" if positive else "#10b981"
    chart_data = frame.copy()
    chart_data["Contribution affichee"] = chart_data["Contribution"].map(
        lambda value: f"{value:+.3f}"
    )
    chart_data["Impact affiche"] = chart_data["Impact"].map(lambda value: f"{value:.3f}")

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X(
                "Impact:Q",
                title="Niveau de contribution",
                axis=alt.Axis(labelColor="#cbd5e1", titleColor="#e2e8f0", gridColor="#314158"),
            ),
            y=alt.Y(
                "Facteur:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelColor="#f8fafc", labelLimit=320),
            ),
            color=alt.value(color),
            tooltip=[
                alt.Tooltip("Facteur:N", title="Facteur"),
                alt.Tooltip("Impact affiche:N", title="Impact"),
                alt.Tooltip("Contribution affichee:N", title="Contribution"),
                alt.Tooltip("Valeur:Q", title="Valeur", format=".3f"),
            ],
        )
        .properties(height=max(260, 34 * len(chart_data)))
        .configure_axis(
            labelColor="#dbe7fb",
            titleColor="#dbe7fb",
            tickColor="#51617b",
            domainColor="#51617b",
            gridColor="#314158",
        )
        .configure_view(fill="#172033", strokeOpacity=0)
        .configure(background="#172033")
    )

    st.altair_chart(chart, use_container_width=True)


def render_summary(result: dict[str, Any], explanation: dict[str, Any] | None) -> None:
    """Affiche le bloc de synthese principal."""
    prediction = int(result["prediction"])
    score = float(result["score"])
    threshold = float(result["threshold"])
    is_risk = prediction == 1
    risk_label = "Risque d'attrition élevé" if is_risk else "Risque d'attrition faible"
    risk_class = "risk-high" if is_risk else "risk-low"

    st.markdown(
        f"""
        <div class="hero-card">
            <p class="eyebrow">Decision du modele final</p>
            <h2 style="margin:0 0 0.7rem 0;color:white;">Résultat individuel</h2>
            <p class="{risk_class}" style="font-size:1.18rem;margin:0 0 0.5rem 0;">{risk_label}</p>
            <p class="caption-soft" style="margin:0;">
                Le score est calculé par le pipeline final puis comparé au seuil
                appris pendant la phase de sélection du modèle.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prédiction", "1" if is_risk else "0")
    col2.metric("Score brut", f"{score:.4f}")
    col3.metric("Seuil", f"{threshold:.4f}")
    col4.metric("Modèle", result["model_name"])
    st.caption(f"Version du modèle : {result['model_version']}")

    if explanation is not None:
        col5, col6, col7 = st.columns(3)
        col5.metric("Base value", f"{float(explanation['base_value']):.4f}")
        col6.metric("Somme positive", f"{float(explanation['positive_sum']):.4f}")
        col7.metric("Somme négative", f"{float(explanation['negative_sum']):.4f}")


def render_explanation(explanation: dict[str, Any] | None) -> None:
    """Affiche l'explication locale du score de manière visuelle."""
    if explanation is None:
        st.info("Aucune explication disponible pour l'instant.")
        return

    top_positive = _contribution_frame(explanation["top_positive"])
    top_negative = _contribution_frame(explanation["top_negative"])

    st.markdown(
        """
        <div class="panel-card">
            <p class="eyebrow">Explication locale</p>
            <h3 style="margin-top:0;color:white;">Variables qui poussent le score</h3>
            <p class="caption-soft" style="margin-bottom:0;">
                Pour ce modèle linéaire, l'explication correspond à la décomposition additive
                du score individuel après standardisation des features.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="explain-card">
                <p class="section-title">Facteurs qui augmentent le risque de départ</p>
                <p class="section-copy">
                    Triés par impact décroissant sur le score du modèle.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not top_positive.empty:
            render_contribution_bars(top_positive, positive=True)
            st.dataframe(
                top_positive.style.format(
                    {"Impact": "{:.3f}", "Contribution": "{:+.3f}", "Valeur": "{:.3f}"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.write("Aucune contribution positive notable.")

    with col2:
        st.markdown(
            """
            <div class="explain-card">
                <p class="section-title">Facteurs qui diminuent le risque de départ</p>
                <p class="section-copy">
                    Triés par impact décroissant sur le score du modèle.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not top_negative.empty:
            render_contribution_bars(top_negative, positive=False)
            st.dataframe(
                top_negative.style.format(
                    {"Impact": "{:.3f}", "Contribution": "{:+.3f}", "Valeur": "{:.3f}"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.write("Aucune contribution négative notable.")


def render_payload(payload: dict[str, Any] | None) -> None:
    """Affiche le dernier payload envoyé."""
    if payload is None:
        st.write("Aucun appel n'a encore été lancé.")
    else:
        st.json(payload)


def render_batch_summary(batch_results_df: pd.DataFrame) -> None:
    """Affiche les indicateurs globaux issus du scoring batch."""
    total_rows = len(batch_results_df)
    total_risk = int(batch_results_df["prediction"].sum())
    risk_rate = (total_risk / total_rows) if total_rows else 0.0
    average_score = float(batch_results_df["score"].mean()) if total_rows else 0.0
    threshold = float(batch_results_df["threshold"].iloc[0]) if total_rows else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Employés scorés", total_rows)
    col2.metric("Départs prédits", total_risk)
    col3.metric("Taux de risque", f"{risk_rate:.1%}")
    col4.metric("Score moyen", f"{average_score:.3f}", delta=f"Seuil {threshold:.3f}")

    chart_data = (
        batch_results_df["prediction"]
        .map({0: "Risque faible", 1: "Risque élevé"})
        .value_counts()
        .rename_axis("Classe")
        .reset_index(name="Volume")
    )
    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Classe:N", axis=alt.Axis(labelColor="#dbe7fb", title=None)),
            y=alt.Y(
                "Volume:Q",
                axis=alt.Axis(labelColor="#dbe7fb", titleColor="#dbe7fb"),
            ),
            color=alt.Color(
                "Classe:N",
                scale=alt.Scale(
                    domain=["Risque faible", "Risque élevé"],
                    range=["#10b981", "#f97316"],
                ),
                legend=None,
            ),
            tooltip=["Classe:N", "Volume:Q"],
        )
        .configure_axis(
            labelColor="#dbe7fb",
            titleColor="#dbe7fb",
            tickColor="#51617b",
            domainColor="#51617b",
            gridColor="#314158",
        )
        .configure_view(fill="#172033", strokeOpacity=0)
        .configure(background="#172033")
    )
    st.altair_chart(chart, use_container_width=True)

    top_risk_df = (
        batch_results_df.sort_values("score", ascending=False)
        .loc[:, ["id_employee", "prediction", "score", "model_name"]]
        .head(10)
        .copy()
    )
    top_risk_df["prediction"] = top_risk_df["prediction"].map(
        {0: "Risque faible", 1: "Risque élevé"}
    )

    st.markdown("#### Employés les plus exposés")
    st.dataframe(
        top_risk_df.style.format({"score": "{:.3f}"}),
        use_container_width=True,
        hide_index=True,
    )


def render_batch_section(api_base_url: str) -> None:
    """Affiche le flux d'upload et d'analyse batch."""
    st.subheader("Analyse batch")
    st.caption(
        "Chargez un fichier CSV contenant les colonnes attendues par le modèle pour "
        "scorer un ensemble d'employés, visualiser les résultats globaux puis analyser "
        "plus finement un individu."
    )
    st.info(
        "Format attendu : un fichier CSV avec une ligne par employé et les mêmes colonnes "
        "que le formulaire individuel, par exemple `age`, `genre`, `revenu_mensuel`, "
        "`departement`, `poste`, `frequence_deplacement`, `heure_supplementaires`, "
        "`annees_dans_l_entreprise`, `note_evaluation_actuelle`. "
        "La colonne `id_employee` est facultative : si elle est absente, elle est générée automatiquement."
    )

    uploaded_file = st.file_uploader(
        "Fichier CSV à scorer",
        type=["csv"],
        accept_multiple_files=False,
        key="batch_csv_uploader",
    )

    if st.button("Lancer le scoring batch", use_container_width=True):
        if uploaded_file is None:
            st.session_state.batch_error = "Aucun fichier CSV n'a été fourni."
        else:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                working_df, payloads = prepare_batch_dataframe(uploaded_df)
                progress_container = st.container()
                progress_bar = progress_container.progress(
                    0.0, text="Préparation du traitement batch..."
                )
                progress_caption = progress_container.empty()

                def update_batch_progress(processed: int, total: int, chunk_len: int) -> None:
                    """Met à jour l'avancement visible du scoring batch."""
                    ratio = (processed / total) if total else 1.0
                    progress_bar.progress(
                        ratio,
                        text=f"Traitement batch en cours... {processed}/{total} employés",
                    )
                    progress_caption.caption(
                        f"Dernier paquet traité : {chunk_len} employés."
                    )

                batch_results = call_batch_prediction_api(
                    api_base_url,
                    payloads,
                    progress_callback=update_batch_progress,
                )
                batch_results_df = pd.DataFrame(batch_results)
                batch_results_df.insert(
                    0, "id_employee", working_df["id_employee"].tolist()
                )

                progress_bar.progress(
                    1.0,
                    text=f"Traitement terminé : {len(batch_results_df)}/{len(payloads)} employés scorés",
                )
                progress_caption.caption(
                    "Le scoring batch est terminé. Vous pouvez maintenant explorer les résultats."
                )

                st.session_state.batch_source_df = working_df
                st.session_state.batch_payloads = payloads
                st.session_state.batch_results_df = batch_results_df
                st.session_state.batch_selected_employee_id = int(
                    batch_results_df.iloc[0]["id_employee"]
                )
                st.session_state.batch_selected_explanation = None
                st.session_state.batch_error = None
            except httpx.HTTPStatusError as exc:
                response_text = exc.response.text if exc.response is not None else str(exc)
                status_code = exc.response.status_code if exc.response is not None else "?"
                st.session_state.batch_error = f"Erreur HTTP {status_code} : {response_text}"
            except Exception as exc:
                st.session_state.batch_error = str(exc)

    if st.session_state.batch_error:
        st.error(st.session_state.batch_error)

    if st.session_state.batch_results_df is None:
        return

    batch_results_df = st.session_state.batch_results_df
    render_batch_summary(batch_results_df)
    display_df = batch_results_df.copy()
    display_df["prediction_label"] = display_df["prediction"].map(
        {0: "Risque faible", 1: "Risque élevé"}
    )
    ordered_columns = [
        "id_employee",
        "prediction_label",
        "score",
        "threshold",
        "model_name",
        "model_version",
    ]
    st.markdown("#### Vue détaillée du batch")
    st.dataframe(
        display_df[ordered_columns].sort_values("score", ascending=False).style.format(
            {"score": "{:.3f}", "threshold": "{:.3f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    employee_ids = batch_results_df["id_employee"].tolist()
    top_risk_df = (
        batch_results_df.sort_values("score", ascending=False)
        .head(5)
        .loc[:, ["id_employee", "score", "prediction"]]
        .copy()
    )
    top_risk_df["prediction_label"] = top_risk_df["prediction"].map(
        {0: "Risque faible", 1: "Risque élevé"}
    )
    top_risk_options = [
        f"ID {int(row.id_employee)} · score {row.score:.3f} · {row.prediction_label}"
        for row in top_risk_df.itertuples(index=False)
    ]
    top_risk_map = {
        option: int(employee_id)
        for option, employee_id in zip(top_risk_options, top_risk_df["id_employee"].tolist())
    }

    st.markdown("#### Analyse locale d'un employé")
    st.caption(
        "Choisissez un identifiant précis ou utilisez un raccourci vers les profils les plus risqués."
    )

    selection_col, action_col = st.columns([3, 1])
    with selection_col:
        default_index = (
            employee_ids.index(st.session_state.batch_selected_employee_id)
            if st.session_state.batch_selected_employee_id in employee_ids
            else 0
        )
        selected_employee_id = st.selectbox(
            "Employé à analyser",
            options=employee_ids,
            index=default_index,
            help="Liste complète des identifiants disponibles dans le batch.",
        )
    with action_col:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        explain_clicked = st.button("Afficher l'analyse", use_container_width=True)

    quick_col, quick_action_col = st.columns([3, 1])
    with quick_col:
        quick_pick = st.selectbox(
            "Raccourci : profils les plus risqués",
            options=top_risk_options,
            index=0,
            help="Sélection rapide des scores les plus élevés du batch.",
        )
    with quick_action_col:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        if st.button("Charger ce profil", use_container_width=True):
            selected_employee_id = top_risk_map[quick_pick]
            st.session_state.batch_selected_employee_id = int(selected_employee_id)
            explain_clicked = True

    if explain_clicked:
        try:
            selected_index = batch_results_df.index[
                batch_results_df["id_employee"] == selected_employee_id
            ][0]
            selected_payload = st.session_state.batch_payloads[selected_index]
            explanation = call_explain_api(api_base_url, selected_payload)
            result = batch_results_df.iloc[selected_index].to_dict()
            st.session_state.batch_selected_employee_id = int(selected_employee_id)
            st.session_state.batch_selected_explanation = {
                "payload": selected_payload,
                "result": result,
                "explanation": explanation,
            }
            st.session_state.batch_error = None
        except httpx.HTTPStatusError as exc:
            response_text = exc.response.text if exc.response is not None else str(exc)
            status_code = exc.response.status_code if exc.response is not None else "?"
            st.session_state.batch_error = f"Erreur HTTP {status_code} : {response_text}"
        except Exception as exc:
            st.session_state.batch_error = str(exc)

    batch_selected = st.session_state.batch_selected_explanation
    if batch_selected is not None:
        st.markdown("---")
        st.subheader(
            f"Analyse locale de l'employé {st.session_state.batch_selected_employee_id}"
        )
        render_summary(batch_selected["result"], batch_selected["explanation"])
        render_explanation(batch_selected["explanation"])
        render_payload(batch_selected["payload"])


def run_prediction_flow(api_base_url: str, payload: dict[str, Any]) -> None:
    """Lance la prédiction puis l'explication locale."""
    st.session_state.last_payload = payload
    st.session_state.last_error = None
    st.session_state.last_result = None
    st.session_state.last_explanation = None

    try:
        result = call_prediction_api(api_base_url, payload)
        explanation = call_explain_api(api_base_url, payload)
    except httpx.HTTPStatusError as exc:
        response_text = exc.response.text if exc.response is not None else str(exc)
        status_code = exc.response.status_code if exc.response is not None else "?"
        st.session_state.last_error = f"Erreur HTTP {status_code} : {response_text}"
    except Exception as exc:
        st.session_state.last_error = f"Erreur lors de l'appel à l'API : {exc}"
    else:
        st.session_state.last_result = result
        st.session_state.last_explanation = explanation


def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""
    configure_page()
    apply_styles()
    initialize_session_state()

    api_base_url = render_sidebar()
    render_header()
    render_context_panel()

    mode_tabs = st.tabs(["Analyse unitaire", "Analyse batch"])

    with mode_tabs[0]:
        submitted, payload = render_form()
        if submitted:
            run_prediction_flow(api_base_url, payload)

        if st.session_state.last_error:
            st.error(st.session_state.last_error)

        if st.session_state.last_result is not None:
            tabs = st.tabs(["Synthèse", "Interprétation locale", "Payload"])
            with tabs[0]:
                render_summary(
                    st.session_state.last_result,
                    st.session_state.last_explanation,
                )
            with tabs[1]:
                render_explanation(st.session_state.last_explanation)
            with tabs[2]:
                render_payload(st.session_state.last_payload)
        else:
            render_payload(st.session_state.last_payload)

    with mode_tabs[1]:
        render_batch_section(api_base_url)


if __name__ == "__main__":
    main()
