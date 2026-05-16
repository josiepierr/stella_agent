"""
app.py
Interface Streamlit de Stella — Agent Mobilité Stellantis
Version 3 onglets : présentation, démo agent, dashboard ROI.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import json
import html
import time

# ──────────────────────────────────────────────
# IMPORTS PROJET
# ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT_DIR = os.path.join(BASE_DIR, "agent")

if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)

from stella import StellaAgent


# ──────────────────────────────────────────────
# VOIX OPTIONNELLE
# ──────────────────────────────────────────────

VOICE_AVAILABLE = False

try:
    if os.getenv("OPENAI_API_KEY"):
        from voice import render_voice_input, speak_response, render_audio_player
        VOICE_AVAILABLE = True
except Exception:
    VOICE_AVAILABLE = False


# ──────────────────────────────────────────────
# CONFIGURATION PAGE
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Stella — Stellantis",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ──────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

:root {
    --blue-deep:#003DA5;
    --blue-mid:#1A56C4;
    --blue-light:#E8EEF8;
    --blue-pale:#F0F4FC;
    --green:#1B8A4B;
    --orange:#FF8A3D;
    --red:#E54B4B;
    --grey-1:#1A1A2E;
    --grey-2:#444466;
    --grey-3:#888899;
    --grey-bg:#F7F8FC;
    --white:#FFFFFF;
    --shadow:0 4px 24px rgba(0,61,165,0.10);
    --shadow-sm:0 2px 8px rgba(0,61,165,0.08);
    --radius:16px;
    --radius-sm:10px;
}

* { font-family:'DM Sans', sans-serif; box-sizing:border-box; }
.stApp { background:var(--grey-bg); }
.block-container { padding:1.4rem 2rem 2rem !important; max-width:100% !important; }

/* SIDEBAR */
[data-testid="stSidebar"] {
    background:var(--blue-deep) !important;
    min-width:280px !important;
}
[data-testid="stSidebar"] > div {
    background:var(--blue-deep) !important;
    overflow-y:auto !important;
    height:100vh !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color:rgba(255,255,255,0.9) !important;
}

.stella-brand {
    text-align:center;
    padding:1rem 0 0.8rem;
    border-bottom:1px solid rgba(255,255,255,0.15);
    margin-bottom:1.2rem;
}
.stella-name {
    font-family:'DM Serif Display', serif !important;
    font-size:1.55rem;
    color:white !important;
    display:block;
}
.stella-tagline {
    font-size:0.68rem;
    color:rgba(255,255,255,0.55) !important;
    letter-spacing:1.5px;
    text-transform:uppercase;
}

.profile-card {
    background:rgba(255,255,255,0.10);
    border-radius:var(--radius-sm);
    padding:0.9rem;
    margin-bottom:0.8rem;
    border:1px solid rgba(255,255,255,0.15);
}
.profile-name { font-size:1rem; font-weight:700; color:white !important; margin:0 0 2px; }
.profile-sub { font-size:0.78rem; color:rgba(255,255,255,0.7) !important; margin:0 0 6px; }
.profile-badge {
    display:inline-block;
    background:rgba(255,255,255,0.2);
    border-radius:20px;
    padding:2px 10px;
    font-size:0.7rem;
    font-weight:700;
    color:white !important;
}
.profile-pts { font-size:0.76rem; color:rgba(255,255,255,0.82) !important; margin-top:5px; }

.veh-box {
    background:rgba(255,255,255,0.08);
    border-radius:var(--radius-sm);
    padding:0.75rem 0.9rem;
    margin-bottom:0.75rem;
    font-size:0.78rem;
}
.veh-label {
    font-size:0.65rem;
    text-transform:uppercase;
    letter-spacing:1px;
    color:rgba(255,255,255,0.45) !important;
    margin-bottom:5px;
}
.veh-row {
    display:flex;
    justify-content:space-between;
    gap:8px;
    margin-bottom:3px;
    color:rgba(255,255,255,0.85) !important;
}
.veh-alert {
    background:rgba(255,87,51,0.2);
    border:1px solid rgba(255,87,51,0.35);
    border-radius:6px;
    padding:5px 8px;
    font-size:0.73rem;
    color:#FFB3A3 !important;
    margin-top:6px;
}
.veh-celebrate {
    background:rgba(255,210,0,0.15);
    border:1px solid rgba(255,210,0,0.3);
    border-radius:6px;
    padding:5px 8px;
    font-size:0.73rem;
    color:#FFE580 !important;
    margin-top:6px;
}

.metric-row { display:flex; gap:8px; margin:4px 0; }
.metric-box {
    flex:1;
    background:rgba(255,255,255,0.08);
    border-radius:8px;
    padding:6px 8px;
    text-align:center;
}
.metric-val { font-size:1rem; font-weight:800; color:white !important; }
.metric-lbl {
    font-size:0.60rem;
    color:rgba(255,255,255,0.45) !important;
    text-transform:uppercase;
    letter-spacing:0.6px;
}

[data-testid="stSidebar"] .stSelectbox > div > div {
    background:rgba(255,255,255,0.12) !important;
    border:1px solid rgba(255,255,255,0.25) !important;
    border-radius:10px !important;
    color:white !important;
}
[data-testid="stSidebar"] .stButton > button {
    background:rgba(255,255,255,0.12) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,0.2) !important;
    border-radius:10px !important;
    font-weight:600 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(255,255,255,0.22) !important;
}

/* HEADER CHAT */
.chat-header {
    display:flex;
    align-items:center;
    gap:12px;
    padding:1rem 1.25rem;
    background:white;
    border-radius:var(--radius);
    box-shadow:var(--shadow-sm);
    margin-bottom:1rem;
}
.chat-avatar-hdr {
    width:46px;
    height:46px;
    background:linear-gradient(135deg,var(--blue-deep),var(--blue-mid));
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}
.chat-hdr-title {
    font-family:'DM Serif Display', serif;
    font-size:1.25rem;
    color:var(--grey-1);
    margin:0;
}
.chat-hdr-sub { font-size:0.76rem; color:var(--grey-3); margin:0; }
.online-dot {
    display:inline-block;
    width:7px;
    height:7px;
    background:var(--green);
    border-radius:50%;
    margin-right:4px;
    animation:pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* MESSAGES */
.messages-zone {
    background:white;
    border-radius:var(--radius);
    padding:1.15rem;
    margin-bottom:0.75rem;
    box-shadow:var(--shadow-sm);
    min-height:300px;
    max-height:58vh;
    overflow-y:auto;
}
.msg-row { display:flex; align-items:flex-end; gap:8px; margin-bottom:12px; }
.msg-row.user { flex-direction:row-reverse; }
.msg-ico {
    width:30px;
    height:30px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:13px;
    flex-shrink:0;
}
.msg-ico.stella { background:linear-gradient(135deg,var(--blue-deep),var(--blue-mid)); color:white; }
.msg-ico.user { background:var(--blue-light); color:var(--blue-deep); }
.bubble {
    max-width:76%;
    padding:0.72rem 0.95rem;
    border-radius:16px;
    font-size:0.88rem;
    line-height:1.55;
    box-shadow:var(--shadow-sm);
}
.bubble.stella {
    background:var(--blue-pale);
    color:var(--grey-1);
    border-bottom-left-radius:4px;
}
.bubble.user {
    background:var(--blue-deep);
    color:white;
    border-bottom-right-radius:4px;
}

/* CARTES */
.cards-grid {
    display:grid;
    grid-template-columns:repeat(3, minmax(0, 1fr));
    gap:12px;
    margin:0.8rem 0 1rem;
}
.action-card {
    background:white;
    border-radius:16px;
    padding:1rem;
    box-shadow:var(--shadow-sm);
    border:1px solid var(--blue-light);
    min-height:132px;
}
.action-card h4 {
    margin:0 0 6px;
    color:var(--grey-1);
    font-size:0.95rem;
}
.action-card p {
    margin:4px 0;
    color:var(--grey-2);
    font-size:0.78rem;
}
.card-tag {
    display:inline-block;
    padding:3px 8px;
    border-radius:999px;
    font-size:0.65rem;
    font-weight:800;
    margin-top:6px;
}
.tag-blue { background:var(--blue-pale); color:var(--blue-deep); }
.tag-green { background:#E8F5EE; color:var(--green); }
.tag-orange { background:#FFF1E7; color:var(--orange); }

/* INPUT */
.input-wrapper {
    position:sticky;
    bottom:0;
    background:var(--grey-bg);
    padding-top:8px;
    padding-bottom:4px;
    z-index:20;
}
.stTextInput > div > div > input {
    background:#FFFFFF !important;
    color:#1A1A2E !important;
    -webkit-text-fill-color:#1A1A2E !important;
    border:2px solid var(--blue-light) !important;
    border-radius:12px !important;
    padding:0.65rem 1rem !important;
    font-size:0.9rem !important;
    caret-color:var(--blue-deep) !important;
}
.stTextInput > div > div > input::placeholder {
    color:#AAAACC !important;
    -webkit-text-fill-color:#AAAACC !important;
}

/* Bouton envoyer */
.send-btn .stButton > button {
    background:var(--blue-deep) !important;
    color:white !important;
    border:none !important;
    border-radius:12px !important;
    padding:0.62rem 1rem !important;
    font-weight:800 !important;
    height:44px !important;
}
.send-btn .stButton > button:hover {
    background:var(--blue-mid) !important;
}

/* Audio input compact */
.voice-box [data-testid="stAudioInput"] {
    margin-top:-8px !important;
}
.voice-box button {
    border-radius:12px !important;
}

.sugg-btn .stButton > button {
    background:white !important;
    color:var(--blue-deep) !important;
    border:1.5px solid var(--blue-light) !important;
    border-radius:20px !important;
    font-size:0.8rem !important;
    padding:0.45rem 0.65rem !important;
}
.sugg-btn .stButton > button:hover {
    background:var(--blue-pale) !important;
    border-color:var(--blue-mid) !important;
}


/* PAGES 3 ONGLETS */
.hero-card {
    background:white;
    border-radius:22px;
    padding:1.6rem;
    box-shadow:var(--shadow-sm);
    border:1px solid var(--blue-light);
    margin-bottom:1rem;
}
.hero-title {
    font-family:'DM Serif Display', serif;
    font-size:2.2rem;
    color:var(--grey-1);
    margin-bottom:0.4rem;
    line-height:1.1;
}
.hero-title span { color:var(--blue-deep); }
.hero-subtitle {
    font-size:0.98rem;
    color:var(--grey-2);
    line-height:1.6;
    max-width:950px;
}
.feature-grid {
    display:grid;
    grid-template-columns:repeat(3, minmax(0, 1fr));
    gap:14px;
    margin-top:1rem;
}
.feature-card {
    background:var(--blue-pale);
    border:1px solid var(--blue-light);
    border-radius:16px;
    padding:1rem;
    min-height:130px;
}
.feature-card h4 {
    margin:0 0 0.35rem;
    color:var(--grey-1);
    font-size:0.98rem;
}
.feature-card p {
    margin:0;
    color:var(--grey-2);
    font-size:0.82rem;
    line-height:1.5;
}
.demo-note {
    background:#FFFFFF;
    border-left:4px solid var(--blue-deep);
    border-radius:12px;
    padding:0.9rem 1rem;
    color:var(--grey-2);
    margin:0.8rem 0 1rem;
    box-shadow:var(--shadow-sm);
    font-size:0.88rem;
}
.video-placeholder {
    background:linear-gradient(135deg,var(--blue-deep),var(--blue-mid));
    color:white;
    border-radius:20px;
    padding:3rem 1.5rem;
    text-align:center;
    box-shadow:var(--shadow-sm);
    margin:1rem 0;
}
.video-placeholder h3 { font-size:1.4rem; margin-bottom:0.4rem; }
.video-placeholder p { opacity:0.82; font-size:0.9rem; }
@media (max-width: 900px) {
    .feature-grid { grid-template-columns:1fr; }
    .cards-grid { grid-template-columns:1fr; }
}

/* ─────────────────────────────────────────────
HIDE STREAMLIT TOP BAR
───────────────────────────────────────────── */

header[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

button[kind="header"] {
    display: none !important;
}

.stAppToolbar {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

#MainMenu, footer { visibility:hidden; }
.stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────

@st.cache_data
def load_profiles():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "..", "data", "users.json"), "r", encoding="utf-8") as f:
        users = json.load(f)["users"]
    with open(os.path.join(base, "..", "data", "vehicles.json"), "r", encoding="utf-8") as f:
        vehicles = json.load(f)["vehicles"]
    return users, vehicles


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def clean_message(text: str) -> str:
    """Convertit une réponse markdown simple en HTML sûr."""
    safe = html.escape(text or "")
    safe = safe.replace("\n", "<br>")
    safe = safe.replace("**", "")
    return safe


def add_user_message(message: str):
    st.session_state.messages.append({"role": "user", "content": message})


def add_assistant_message(message: str):
    st.session_state.messages.append({"role": "assistant", "content": message})


def ask_stella(message: str):
    """Envoie un message à l'agent et ajoute la réponse à l'historique."""
    if not message or not message.strip():
        return

    add_user_message(message.strip())

    with st.spinner("Stella analyse la situation..."):
        response = st.session_state.agent.chat(message.strip())

    add_assistant_message(response)

    # Synthèse vocale optionnelle.
    # On stocke l'audio dans session_state au lieu de l'afficher directement ici,
    # car ask_stella() est presque toujours suivi d'un st.rerun().
    if VOICE_AVAILABLE and st.session_state.get("voice_enabled") and response:
        audio = speak_response(response)
        if audio:
            st.session_state.last_tts_time = time.time()
            st.session_state.last_audio_response = audio
            st.session_state.last_audio_text = response[:160]


def set_pending(query: str):
    st.session_state.pending_sugg = query


def get_active_driver_name(user: dict) -> str:
    """Retourne le prénom du conducteur actif affiché dans l'interface."""
    conducteur = st.session_state.get("conducteur_actif")
    if isinstance(conducteur, dict) and conducteur.get("prenom"):
        return conducteur["prenom"]
    return user.get("prenom", "conductrice")


def render_profile_cards(user: dict, vehicle: dict):
    """Cartes visuelles contextuelles pour effet démo."""
    uid = user["user_id"]
    motorisation = vehicle.get("motorisation")

    voyants = vehicle.get("voyants_actifs", [])
    batterie = vehicle.get("niveau_batterie_pct", 100)
    anniv = vehicle.get("anniversaire_vehicule_dans_jours")

    cards = []

    if voyants:
        cards.append({
            "title": "🔧 Alerte entretien",
            "body": f"{voyants[0].get('libelle', 'Voyant actif')} détecté sur ta {vehicle.get('marque')} {vehicle.get('modele')}.",
            "tag": "Action recommandée",
            "tag_class": "tag-orange",
            "button": "Analyser le voyant",
            "query": "J’ai un voyant actif, que dois-je faire ?"
        })

    if motorisation == "electrique":
        cards.append({
            "title": "⚡ Recharge intelligente",
            "body": f"Batterie à {batterie}%. Stella peut recommander une borne proche et compatible Free2move.",
            "tag": "Free2move Charge",
            "tag_class": "tag-blue",
            "button": "Trouver une borne",
            "query": "Je cherche une borne de recharge proche."
        })

    if anniv == 0:
        cards.append({
            "title": "🎁 Offre anniversaire",
            "body": f"La {vehicle.get('marque')} {vehicle.get('modele')} fête son anniversaire aujourd’hui.",
            "tag": "Fidélité",
            "tag_class": "tag-green",
            "button": "Voir mon cadeau",
            "query": "Montre-moi mes offres et mes avantages fidélité."
        })

    cards.append({
        "title": "⭐ Fidélité",
        "body": f"{user.get('points_fidelite', 0)} points · niveau {user.get('niveau_fidelite', '?')}.",
        "tag": "Avantages",
        "tag_class": "tag-green",
        "button": "Voir mes points",
        "query": "Montre-moi mes avantages fidélité."
    })

    cards = cards[:3]

    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(len(cards))
    for i, (col, card) in enumerate(zip(cols, cards)):
        with col:
            st.markdown(f"""
            <div class="action-card">
                <h4>{card["title"]}</h4>
                <p>{card["body"]}</p>
                <span class="card-tag {card["tag_class"]}">{card["tag"]}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button(card["button"], key=f"card_{uid}_{i}", use_container_width=True):
                set_pending(card["query"])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_messages(user: dict, vehicle: dict, voyants: list, display_name: str | None = None):
    """Affiche les messages sans risquer d'afficher du HTML brut."""
    display_name = display_name or user.get("prenom", "conductrice")

    if not st.session_state.messages:
        bat = vehicle.get("niveau_batterie_pct", 100)
        anniv = vehicle.get("anniversaire_vehicule_dans_jours")

        if voyants:
            welcome = (
                f"👋 Bonjour {display_name} ! J’ai détecté un voyant actif sur ta "
                f"{vehicle['marque']} {vehicle['modele']}. Je peux t’aider à comprendre quoi faire."
            )
        elif vehicle.get("motorisation") == "electrique" and bat < 30:
            welcome = (
                f"⚡ Bonjour {display_name} ! Ta batterie est à {bat}%. "
                f"Je peux t’aider à trouver une borne proche et adaptée."
            )
        elif anniv == 0:
            welcome = (
                f"🎉 Bonjour {display_name} ! Aujourd’hui, c’est l’anniversaire de ta voiture. "
                f"J’ai préparé tes avantages du moment."
            )
        else:
            welcome = f"👋 Bonjour {display_name} ! Comment puis-je t’aider aujourd’hui ?"

        st.markdown('<div class="messages-zone">', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="msg-row">
                <div class="msg-ico stella">🌟</div>
                <div class="bubble stella">{clean_message(welcome)}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="messages-zone">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        content = clean_message(msg.get("content", ""))

        if msg.get("role") == "user":
            st.markdown(f"""
                <div class="msg-row user">
                    <div class="msg-ico user">👤</div>
                    <div class="bubble user">{content}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="msg-row">
                    <div class="msg-ico stella">🌟</div>
                    <div class="bubble stella">{content}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_quick_suggestions():
    st.markdown(
        '<p style="text-align:center;font-size:0.7rem;color:#AAAACC;text-transform:uppercase;letter-spacing:0.8px;margin:0.4rem 0;">Suggestions rapides</p>',
        unsafe_allow_html=True
    )

    suggestions = [
        ("🔧 Entretien", "Quel est l’état de mon entretien ?"),
        ("⭐ Fidélité", "Montre-moi mes avantages fidélité."),
        ("📍 Garage", "Trouve-moi un garage agréé proche."),
        ("⚡ Recharge", "Aide-moi à trouver une borne de recharge."),
    ]

    cols = st.columns(4)
    for i, (label, query) in enumerate(suggestions):
        with cols[i]:
            st.markdown('<div class="sugg-btn">', unsafe_allow_html=True)
            if st.button(label, use_container_width=True, key=f"sugg_{i}"):
                set_pending(query)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)



# ──────────────────────────────────────────────
# PAGES — PRÉSENTATION ET ROI
# ──────────────────────────────────────────────

def render_presentation_page():
    """Premier onglet : vidéo courte + descriptif de l'agent."""
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">STELLA — <span>Compagnon mobilité Stellantis</span></div>
        <div class="hero-subtitle">
            Stella est un agent conversationnel personnalisé qui accompagne les conductrices Stellantis
            dans leurs usages quotidiens : entretien, recharge, fidélité, services partenaires,
            documentation officielle et escalade vers un conseiller humain lorsque nécessaire.
        </div>
    </div>
    """, unsafe_allow_html=True)

    video_path = os.path.join(BASE_DIR, "assets", "stella_demo.mp4")

    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.markdown("""
        <div class="video-placeholder">
            <h3>🎬 Vidéo de présentation à ajouter</h3>
            <p>Place une vidéo courte ici : <strong>assets/stella_demo.mp4</strong> · durée recommandée : 45 à 60 secondes.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <h4>🔧 Entretien personnalisé</h4>
            <p>Stella lit l’état du véhicule, explique les voyants, anticipe la révision et recommande une action concrète.</p>
        </div>
        <div class="feature-card">
            <h4>⚡ Recharge intelligente</h4>
            <p>Pour les véhicules électriques, Stella recommande les bornes proches selon batterie, localisation et compatibilité Free2move.</p>
        </div>
        <div class="feature-card">
            <h4>⭐ Fidélité & offres</h4>
            <p>L’agent personnalise les avantages, points fidélité, offres anniversaire et services adaptés au profil de la conductrice.</p>
        </div>
        <div class="feature-card">
            <h4>📚 RAG officiel Stellantis</h4>
            <p>Stella recherche dans une base documentaire construite à partir de sources publiques officielles Stellantis.</p>
        </div>
        <div class="feature-card">
            <h4>👥 Multi-conducteurs</h4>
            <p>Un compte peut gérer plusieurs conducteurs associés, tout en conservant les avantages liés à la propriétaire.</p>
        </div>
        <div class="feature-card">
            <h4>🧭 Escalade humaine</h4>
            <p>En cas d’urgence, d’insatisfaction ou de demande explicite, Stella transmet le contexte à un conseiller humain.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-note">
        <strong>Architecture :</strong> agent Claude Sonnet avec tool-use, base documentaire RAG ChromaDB,
        données simulées utilisateurs/véhicules/partenaires/offres, interface Streamlit et option voix STT/TTS.
    </div>
    """, unsafe_allow_html=True)


def render_roi_page():
    """Troisième onglet : dashboard ROI HTML intégré."""
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">Dashboard <span>ROI</span></div>
        <div class="hero-subtitle">
            Ce tableau présente une projection économique prudente : coût moyen de Stella,
            taux de déflexion, part des demandes substituables, coûts humains évités et économies nettes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    candidates = [
        os.path.join(BASE_DIR, "stella_roi_dashboard_credible.html"),
        os.path.join(BASE_DIR, "stella_roi_dashboard_corrected.html"),
        os.path.join(BASE_DIR, "stella_roi_dashboard.html"),
    ]

    roi_path = next((p for p in candidates if os.path.exists(p)), None)

    if roi_path is None:
        st.warning("Dashboard ROI introuvable. Place `stella_roi_dashboard_credible.html` à la racine du projet.")
        return

    with open(roi_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=1150, scrolling=True)


def render_agent_demo_page(user: dict, vehicle: dict, voyants: list):
    """Deuxième onglet : démo agent, identique au chat existant."""
    active_display_name = get_active_driver_name(user)

    st.markdown(f"""
    <div class="chat-header">
        <div class="chat-avatar-hdr">🌟</div>
        <div>
            <div class="chat-hdr-title">Stella</div>
            <div class="chat-hdr-sub">
                <span class="online-dot"></span>En ligne · {active_display_name}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.pending_sugg:
        msg = st.session_state.pending_sugg
        st.session_state.pending_sugg = None
        ask_stella(msg)
        st.rerun()

    render_messages(user, vehicle, voyants, active_display_name)

    if (
        VOICE_AVAILABLE
        and st.session_state.get("voice_enabled")
        and st.session_state.get("last_audio_response")
    ):
        st.audio(st.session_state.last_audio_response, format="audio/mp3")
        if st.session_state.get("last_audio_text"):
            st.caption("🔊 Dernière réponse vocale disponible.")

    if not st.session_state.messages:
        render_profile_cards(user, vehicle)
        render_quick_suggestions()

    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

    voice_payload = None

    if VOICE_AVAILABLE and st.session_state.get("voice_enabled"):
        col_voice, col_input, col_send = st.columns([0.9, 5.2, 1.2])
    else:
        col_input, col_send = st.columns([5.2, 1.2])
        col_voice = None

    if col_voice is not None:
        with col_voice:
            st.markdown('<div class="voice-box">', unsafe_allow_html=True)
            voice_payload = render_voice_input()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_input:
        user_input = st.text_input(
            "Message",
            placeholder="Écris un message à Stella...",
            label_visibility="collapsed",
            key=f"chat_input_{st.session_state.input_key}"
        )

    with col_send:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send_clicked = st.button("Envoyer →", use_container_width=True, key="send_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if voice_payload:
        voice_text = voice_payload.get("text", "").strip()
        voice_hash = voice_payload.get("hash")

        if voice_text and voice_hash and voice_hash != st.session_state.last_voice_hash:
            st.session_state.last_voice_hash = voice_hash
            ask_stella(voice_text)
            st.rerun()

    if send_clicked and user_input.strip():
        ask_stella(user_input.strip())
        st.session_state.input_key += 1
        st.rerun()


# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────

if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_uid" not in st.session_state:
    st.session_state.current_uid = None
if "pending_sugg" not in st.session_state:
    st.session_state.pending_sugg = None
if "conducteur_actif_id" not in st.session_state:
    st.session_state.conducteur_actif_id = None
if "last_voice_hash" not in st.session_state:
    st.session_state.last_voice_hash = None
if "last_tts_time" not in st.session_state:
    st.session_state.last_tts_time = 0
if "last_audio_response" not in st.session_state:
    st.session_state.last_audio_response = None
if "last_audio_text" not in st.session_state:
    st.session_state.last_audio_text = None
if "conducteur_actif" not in st.session_state:
    st.session_state.conducteur_actif = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────

users, vehicles = load_profiles()

with st.sidebar:
    st.markdown("""
    <div class="stella-brand">
        <div style="font-size:2rem;">🚗</div>
        <span class="stella-name">Stella</span>
        <div class="stella-tagline">Compagnon mobilité Stellantis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.45);margin:0 0 5px;">Profil conductrice</p>',
        unsafe_allow_html=True
    )

    profile_map = {
        f"{u['prenom']} — {next((v['marque'] + ' ' + v['modele'] for v in vehicles if v['user_id'] == u['user_id']), '?')}": u["user_id"]
        for u in users
    }

    chosen_label = st.selectbox("Profil", list(profile_map.keys()), label_visibility="collapsed")
    chosen_uid = profile_map[chosen_label]

    if chosen_uid != st.session_state.current_uid:
        st.session_state.agent = StellaAgent(user_id=chosen_uid)
        st.session_state.messages = []
        st.session_state.current_uid = chosen_uid
        st.session_state.pending_sugg = None
        st.session_state.conducteur_actif_id = None
        st.session_state.conducteur_actif = None
        st.session_state.last_voice_hash = None
        st.session_state.last_audio_response = None
        st.session_state.last_audio_text = None
        st.session_state.input_key += 1

    user = next(u for u in users if u["user_id"] == chosen_uid)
    vehicle = next(v for v in vehicles if v["user_id"] == chosen_uid)

    mot_icon = {"electrique": "⚡", "hybride": "🔋", "thermique": "⛽"}.get(vehicle["motorisation"], "🚗")

    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-name">{user['prenom']}, {user['age']} ans</div>
        <div class="profile-sub">{mot_icon} {vehicle['marque']} {vehicle['modele']} {vehicle['annee']}</div>
        <span class="profile-badge">✨ {user['niveau_fidelite']}</span>
        <div class="profile-pts">⭐ {user['points_fidelite']} points fidélité</div>
    </div>
    """, unsafe_allow_html=True)

    voyants = vehicle.get("voyants_actifs", [])

    if vehicle["motorisation"] == "electrique":
        e_lbl = "🔋 Batterie"
        e_val = f"{vehicle.get('niveau_batterie_pct', '?')}% — {vehicle.get('autonomie_restante_km', '?')} km"
    elif vehicle["motorisation"] == "hybride":
        e_lbl = "⛽/🔋"
        e_val = f"{vehicle.get('niveau_carburant_pct', '?')}% / {vehicle.get('niveau_batterie_hybride_pct', '?')}%"
    else:
        e_lbl = "⛽ Carburant"
        e_val = f"{vehicle.get('niveau_carburant_pct', '?')}%"

    extra = ""
    if voyants:
        extra += f'<div class="veh-alert">⚠️ {voyants[0].get("libelle", "Voyant actif")}</div>'
    if vehicle.get("anniversaire_vehicule_dans_jours") == 0:
        extra += '<div class="veh-celebrate">🎉 Anniversaire du véhicule aujourd’hui</div>'

    st.markdown(f"""
    <div class="veh-box">
        <div class="veh-label">État du véhicule</div>
        <div class="veh-row"><span>{e_lbl}</span><span>{e_val}</span></div>
        <div class="veh-row"><span>🔧 Révision dans</span><span>{vehicle.get('km_avant_revision', '?')} km</span></div>
        <div class="veh-row"><span>📍 Ville</span><span>{user['ville']}</span></div>
        {extra}
    </div>
    """, unsafe_allow_html=True)

    # ── Conducteur actif ─────────────────────────────
    conducteurs = user.get("conducteurs_associes", [])

    if conducteurs:
        st.markdown(
            '<p style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.45);margin:10px 0 5px;">Conducteur actif</p>',
            unsafe_allow_html=True
        )

        options_conducteur = (
            [f"{user['prenom']} (propriétaire)"]
            + [f"{c['prenom']} ({c.get('relation', 'conducteur')})" for c in conducteurs]
        )

        choix_conducteur = st.selectbox(
            "Conducteur actif",
            options_conducteur,
            label_visibility="collapsed",
            key=f"conducteur_sidebar_{chosen_uid}",
            help="Les points fidélité et les offres restent liés à la propriétaire."
        )

        if choix_conducteur == options_conducteur[0]:
            conducteur_actif = None
        else:
            idx = options_conducteur.index(choix_conducteur) - 1
            conducteur_actif = conducteurs[idx]

        curr = conducteur_actif.get("conducteur_id") if conducteur_actif else None

        if st.session_state.conducteur_actif_id != curr:
            st.session_state.conducteur_actif_id = curr
            st.session_state.conducteur_actif = conducteur_actif

            if st.session_state.agent and hasattr(st.session_state.agent, "set_conducteur"):
                st.session_state.agent.set_conducteur(conducteur_actif, reset_conversation=True)

            st.session_state.messages = []
            st.session_state.pending_sugg = None
            st.session_state.last_voice_hash = None
            st.session_state.last_audio_response = None
            st.session_state.last_audio_text = None
            st.session_state.input_key += 1
            st.rerun()

    else:
        st.session_state.conducteur_actif_id = None
        st.session_state.conducteur_actif = None

    if st.session_state.agent:
        m = st.session_state.agent.get_metrics()
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="metric-val">{m.get('nb_tours_conversation', 0)}</div>
                <div class="metric-lbl">échanges</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{m.get('nb_appels_tools', 0)}</div>
                <div class="metric-lbl">tools</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{m.get('cout_estime_eur', 0):.4f}€</div>
                <div class="metric-lbl">coût</div>
            </div>
        </div>
        <div style="text-align:center;font-size:0.68rem;color:rgba(255,255,255,0.35);margin-top:3px;">
            {m.get('tokens_total', 0):,} tokens
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if VOICE_AVAILABLE:
        st.session_state["voice_enabled"] = st.toggle(
            "🎙️ Mode vocal",
            value=st.session_state.get("voice_enabled", False),
            help="Active le micro et la lecture vocale des réponses de Stella."
        )
    else:
        st.session_state["voice_enabled"] = False
        st.caption("🎙️ Mode vocal désactivé : OPENAI_API_KEY absente.")

    if st.button("🏠 Nouvelle conversation", use_container_width=True):
        if st.session_state.agent:
            st.session_state.agent.reset_conversation()
        st.session_state.messages = []
        st.session_state.pending_sugg = None
        st.session_state.last_voice_hash = None
        st.session_state.last_audio_response = None
        st.session_state.last_audio_text = None
        st.session_state.input_key += 1
        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:1rem;font-size:0.6rem;color:rgba(255,255,255,0.25);">
        STELLANTIS © 2026 · Women in GenAI Hackathon
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# MAIN — SITE À 3 ONGLETS
# ──────────────────────────────────────────────

tab_intro, tab_demo, tab_roi = st.tabs([
    "🎬 Présentation",
    "💬 Démo Stella",
    "📊 Dashboard ROI",
])

with tab_intro:
    render_presentation_page()

with tab_demo:
    render_agent_demo_page(user, vehicle, voyants)

with tab_roi:
    render_roi_page()
