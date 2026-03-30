"""Interface Streamlit portfolio pour la prediction d'attrition.

Cette interface consomme exclusivement l'API FastAPI. Elle ne recharge pas le
modele localement et ne recopie pas la logique de prediction : elle sert de
surcouche de demonstration metier, plus lisible pour un contexte portfolio.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st


DEFAULT_API_BASE_URL = os.getenv(
    "P5_API_BASE_URL",
    "https://rayakevin-p5-employee-attrition-api.hf.space",
)

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
    "augementation_salaire_precedente": 12.0,
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
        "statut_marital": "Marié(e)",
        "poste": "Senior Manager",
        "annee_experience_totale": 22.0,
        "annees_dans_l_entreprise": 14.0,
        "annees_dans_le_poste_actuel": 6.0,
        "niveau_hierarchique_poste": 4,
        "note_evaluation_precedente": 4.0,
        "note_evaluation_actuelle": 4.0,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 16.0,
        "distance_domicile_travail": 7.0,
        "frequence_deplacement": "Aucun",
        "annees_depuis_la_derniere_promotion": 1.0,
        "annes_sous_responsable_actuel": 5.0,
    },
    "Profil exposé au départ": {
        **FORM_DEFAULTS,
        "age": 29,
        "genre": "Homme",
        "revenu_mensuel": 2800.0,
        "statut_marital": "Célibataire",
        "departement": "Commercial",
        "poste": "Cadre Commercial",
        "nombre_experiences_precedentes": 5,
        "annee_experience_totale": 7.0,
        "annees_dans_l_entreprise": 2.0,
        "annees_dans_le_poste_actuel": 1.0,
        "satisfaction_employee_environnement": 2,
        "note_evaluation_precedente": 2.0,
        "satisfaction_employee_nature_travail": 2,
        "satisfaction_employee_equipe": 2,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 4.0,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": 6.0,
        "distance_domicile_travail": 28.0,
        "domaine_etude": "Marketing",
        "frequence_deplacement": "Frequent",
        "annees_depuis_la_derniere_promotion": 2.0,
        "annes_sous_responsable_actuel": 1.0,
    },
}


def configure_page() -> None:
    """Definit la configuration generale de la page."""
    st.set_page_config(
        page_title="Portfolio P5 - Attrition",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_styles() -> None:
    """Ajoute un habillage plus intentionnel que le rendu Streamlit natif."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, #f7f0df 0%, transparent 30%),
                linear-gradient(180deg, #fbf8f1 0%, #f0e7d2 100%);
        }
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero-card, .panel-card {
            background: rgba(255, 252, 245, 0.94);
            border: 1px solid rgba(39, 60, 44, 0.10);
            border-radius: 22px;
            box-shadow: 0 14px 36px rgba(52, 66, 45, 0.08);
        }
        .hero-card {
            padding: 1.5rem 1.7rem;
            margin-bottom: 1rem;
        }
        .panel-card {
            padding: 1rem 1.2rem;
        }
        .status-chip {
            display: inline-block;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: #ede4cf;
            color: #273c2c;
            font-size: 0.84rem;
            margin-right: 0.5rem;
        }
        .risk-low {
            color: #1f6f43;
            font-weight: 700;
        }
        .risk-high {
            color: #9f2f1f;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Initialise explicitement l'etat pour eviter les reruns incoherents."""
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL
    if "selected_profile" not in st.session_state:
        st.session_state.selected_profile = "Profil par défaut"
    if "last_payload" not in st.session_state:
        st.session_state.last_payload = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None

    for field_name, default_value in FORM_DEFAULTS.items():
        state_key = f"field_{field_name}"
        if state_key not in st.session_state:
            st.session_state[state_key] = default_value


def load_profile_into_state(profile_name: str) -> None:
    """Charge un profil de demonstration dans l'etat des widgets."""
    profile = PROFILE_LIBRARY[profile_name]
    for field_name, field_value in profile.items():
        st.session_state[f"field_{field_name}"] = field_value
    st.session_state.selected_profile = profile_name
    st.session_state.last_error = None


@st.cache_data(ttl=20, show_spinner=False)
def check_api_health(api_base_url: str) -> tuple[bool, str]:
    """Teste la disponibilite de l'API.

    Le cache est utile ici car la verification de sante n'a aucun effet de
    bord et ne doit pas relancer un appel HTTP a chaque rerun Streamlit.
    """
    try:
        response = httpx.get(f"{api_base_url}/health", timeout=8.0)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") == "ok":
            return True, "API disponible"
        return False, f"Réponse inattendue : {payload}"
    except Exception as exc:
        return False, str(exc)


def call_prediction_api(api_base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Appelle l'endpoint de prediction.

    Cette fonction n'est volontairement pas cachée : l'endpoint enregistre une
    trace métier en base et l'appel doit donc rester effectif à chaque clic.
    """
    response = httpx.post(
        f"{api_base_url}/api/v1/predict",
        json=payload,
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def render_header() -> None:
    """Affiche l'entete principal de l'application."""
    st.markdown(
        """
        <div class="hero-card">
            <p style="letter-spacing:0.14em;text-transform:uppercase;font-size:0.76rem;color:#7b765f;margin:0;">Portfolio P5</p>
            <h1 style="margin:0.2rem 0 0.8rem 0;">Prédiction du risque d'attrition collaborateur</h1>
            <p style="margin:0;max-width:760px;">
                Cette interface Streamlit présente le modèle final exporté via MLflow
                au travers d'un formulaire métier en français. Le frontend appelle
                l'API FastAPI et ne duplique pas la logique de scoring.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Affiche la barre laterale de supervision et de configuration."""
    st.sidebar.markdown("## Connexion API")
    api_base_url = st.sidebar.text_input(
        "URL de l'API",
        key="api_base_url",
        help="API locale FastAPI ou Space Hugging Face qui expose /health et /api/v1/predict.",
    ).rstrip("/")

    is_healthy, message = check_api_health(api_base_url)
    if is_healthy:
        st.sidebar.success(message)
    else:
        st.sidebar.error(message)

    st.sidebar.markdown("## Profils de démonstration")
    selected_profile = st.sidebar.selectbox(
        "Charger un scénario",
        options=list(PROFILE_LIBRARY.keys()),
        index=list(PROFILE_LIBRARY.keys()).index(st.session_state.selected_profile),
    )
    if st.sidebar.button("Appliquer le profil", use_container_width=True):
        load_profile_into_state(selected_profile)
        st.rerun()

    st.sidebar.markdown("## Référence")
    st.sidebar.write(
        "Le formulaire n'expose que les variables réellement consommées par le preprocessing du modèle final."
    )
    return api_base_url


def render_form() -> tuple[bool, dict[str, Any]]:
    """Affiche le formulaire principal et retourne le payload construit."""
    with st.form("prediction_form", clear_on_submit=False):
        st.subheader("Profil employé")
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.slider("Âge", 16, 65, key="field_age")
            genre = st.selectbox(
                "Genre", GENRES, index=GENRES.index(st.session_state.field_genre)
            )
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
            poste = st.selectbox(
                "Poste",
                POSTES,
                index=POSTES.index(st.session_state.field_poste),
            )
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
                index=FREQUENCES_DEPLACEMENT.index(
                    st.session_state.field_frequence_deplacement
                ),
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
                "Augmentation salariale précédente (%)",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                key="field_augementation_salaire_precedente",
            )

        st.subheader("Satisfaction")
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            satisfaction_employee_environnement = st.slider(
                "Satisfaction environnement",
                min_value=1,
                max_value=4,
                key="field_satisfaction_employee_environnement",
            )
        with col8:
            satisfaction_employee_nature_travail = st.slider(
                "Satisfaction nature du travail",
                min_value=1,
                max_value=4,
                key="field_satisfaction_employee_nature_travail",
            )
        with col9:
            satisfaction_employee_equipe = st.slider(
                "Satisfaction équipe",
                min_value=1,
                max_value=4,
                key="field_satisfaction_employee_equipe",
            )
        with col10:
            satisfaction_employee_equilibre_pro_perso = st.slider(
                "Équilibre pro / perso",
                min_value=1,
                max_value=4,
                key="field_satisfaction_employee_equilibre_pro_perso",
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


def render_context_panel() -> None:
    """Affiche un rappel sur le scope réel du formulaire."""
    st.markdown(
        """
        <div class="panel-card">
            <span class="status-chip">Formulaire aligné sur le modèle final</span>
            <span class="status-chip">Backend FastAPI</span>
            <span class="status-chip">Scoring MLflow</span>
            <p style="margin:0.9rem 0 0 0;">
                Les champs retirés après revue ne sont plus affichés quand ils
                n'influencent pas réellement la reconstruction des features du modèle.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_panel(result: dict[str, Any]) -> None:
    """Affiche le résultat de prediction et ses indicateurs."""
    prediction = int(result["prediction"])
    score = float(result["score"])
    threshold = float(result["threshold"])
    is_risk = prediction == 1
    risk_label = "Risque d'attrition élevé" if is_risk else "Risque d'attrition faible"
    risk_class = "risk-high" if is_risk else "risk-low"

    st.markdown(
        f"""
        <div class="hero-card">
            <h3 style="margin-top:0;">Résultat de la prédiction</h3>
            <p class="{risk_class}" style="font-size:1.2rem;">{risk_label}</p>
            <p style="margin-bottom:0.4rem;">
                La décision est calculée à partir du score brut renvoyé par le modèle
                et du seuil stocké dans la metadata MLflow.
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


def render_last_call(payload: dict[str, Any] | None) -> None:
    """Affiche le dernier payload envoyé pour faciliter le debug."""
    with st.expander("Voir le dernier payload envoyé à l'API"):
        if payload is None:
            st.write("Aucun appel n'a encore été lancé.")
        else:
            st.json(payload)


def run_prediction_flow(api_base_url: str, payload: dict[str, Any]) -> None:
    """Gere l'appel API et stocke explicitement le résultat dans le session state."""
    st.session_state.last_payload = payload
    st.session_state.last_error = None

    try:
        result = call_prediction_api(api_base_url, payload)
    except httpx.HTTPStatusError as exc:
        response_text = exc.response.text if exc.response is not None else str(exc)
        st.session_state.last_result = None
        st.session_state.last_error = (
            f"Erreur HTTP {exc.response.status_code} : {response_text}"
        )
    except Exception as exc:
        st.session_state.last_result = None
        st.session_state.last_error = f"Erreur lors de l'appel à l'API : {exc}"
    else:
        st.session_state.last_result = result


def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""
    configure_page()
    apply_styles()
    initialize_session_state()

    api_base_url = render_sidebar()
    render_header()
    render_context_panel()

    submitted, payload = render_form()

    if submitted:
        run_prediction_flow(api_base_url, payload)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.last_result:
        render_result_panel(st.session_state.last_result)

    render_last_call(st.session_state.last_payload)


if __name__ == "__main__":
    main()
