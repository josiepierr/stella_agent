"""
app.py
Interface Streamlit de Stella — Agent Mobilité Stellantis
Version 2 — corrections UX : input visible, sidebar persistante, navigation
"""

import streamlit as st
import sys
import os
import json

# Path vers le dossier agent
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agent"))

from stella import StellaAgent

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
# CSS CORRIGÉ
# ──────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

:root {
    --blue-deep:  #003DA5;
    --blue-mid:   #1A56C4;
    --blue-light: #E8EEF8;
    --blue-pale:  #F0F4FC;
    --green:      #1B8A4B;
    --grey-1:     #1A1A2E;
    --grey-2:     #444466;
    --grey-3:     #888899;
    --grey-bg:    #F7F8FC;
    --white:      #FFFFFF;
    --shadow:     0 4px 24px rgba(0,61,165,0.10);
    --shadow-sm:  0 2px 8px rgba(0,61,165,0.08);
    --radius:     16px;
    --radius-sm:  10px;
}

* { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }
.stApp { background: var(--grey-bg); }

/* ── SIDEBAR */
[data-testid="stSidebar"] {
    background: var(--blue-deep) !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] > div { background: var(--blue-deep) !important; }
[data-testid="stSidebarContent"] { padding: 1.2rem 1rem; }
[data-testid="collapsedControl"] {
    background: var(--blue-deep) !important;
    color: white !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: rgba(255,255,255,0.9) !important; }

/* ── Brand */
.stella-brand {
    text-align: center;
    padding: 1rem 0 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 1.2rem;
}
.stella-name {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.5rem;
    color: white !important;
    margin: 6px 0 2px;
    display: block;
}
.stella-tagline {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.55) !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── Profile card */
.profile-card {
    background: rgba(255,255,255,0.1);
    border-radius: var(--radius-sm);
    padding: 0.9rem;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(255,255,255,0.15);
}
.profile-name { font-size: 1rem; font-weight: 600; color: white !important; margin: 0 0 2px; }
.profile-sub  { font-size: 0.78rem; color: rgba(255,255,255,0.65) !important; margin: 0 0 6px; }
.profile-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    color: white !important;
}
.profile-pts { font-size: 0.76rem; color: rgba(255,255,255,0.8) !important; margin-top: 5px; }

/* ── Vehicle status */
.veh-box {
    background: rgba(255,255,255,0.08);
    border-radius: var(--radius-sm);
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.75rem;
    font-size: 0.78rem;
}
.veh-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.45) !important; margin-bottom: 5px; }
.veh-row   { display: flex; justify-content: space-between; margin-bottom: 3px; color: rgba(255,255,255,0.85) !important; }
.veh-alert {
    background: rgba(255,87,51,0.2);
    border: 1px solid rgba(255,87,51,0.35);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 0.73rem;
    color: #FFB3A3 !important;
    margin-top: 4px;
}
.veh-celebrate {
    background: rgba(255,210,0,0.15);
    border: 1px solid rgba(255,210,0,0.3);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 0.73rem;
    color: #FFE580 !important;
    margin-top: 4px;
}

/* ── Metrics */
.metric-row { display: flex; gap: 8px; margin: 4px 0; }
.metric-box {
    flex: 1;
    background: rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 6px 8px;
    text-align: center;
}
.metric-val { font-size: 1rem; font-weight: 700; color: white !important; }
.metric-lbl { font-size: 0.62rem; color: rgba(255,255,255,0.45) !important; text-transform: uppercase; letter-spacing: 0.6px; }

/* ── Selectbox sidebar */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
    color: white !important;
}
[data-testid="stSidebar"] .stSelectbox svg { fill: white !important; }

/* ── Boutons sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.12) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.22) !important;
}

/* ── MAIN */
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Chat header */
.chat-header {
    display: flex; align-items: center; gap: 12px;
    padding: 1rem 1.25rem;
    background: white;
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.2rem;
}
.chat-avatar-hdr {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, var(--blue-deep), var(--blue-mid));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.chat-hdr-title { font-family: 'DM Serif Display', serif; font-size: 1.2rem; color: var(--grey-1); margin: 0; }
.chat-hdr-sub   { font-size: 0.75rem; color: var(--grey-3); margin: 0; }
.online-dot {
    display: inline-block; width: 7px; height: 7px;
    background: var(--green); border-radius: 50%; margin-right: 4px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Messages */
.messages-zone {
    background: white;
    border-radius: var(--radius);
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
    min-height: 280px;
}
.msg-row       { display: flex; align-items: flex-end; gap: 8px; margin-bottom: 10px; }
.msg-row.user  { flex-direction: row-reverse; }
.msg-ico       { width: 30px; height: 30px; border-radius: 50%; display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; }
.msg-ico.stella{ background: linear-gradient(135deg,var(--blue-deep),var(--blue-mid)); }
.msg-ico.user  { background: var(--blue-light); }
.bubble        { max-width: 70%; padding: 0.65rem 0.9rem; border-radius: 16px; font-size: 0.87rem; line-height: 1.55; box-shadow: var(--shadow-sm); }
.bubble.stella { background: var(--blue-pale); color: var(--grey-1); border-bottom-left-radius: 4px; }
.bubble.user   { background: var(--blue-deep); color: white; border-bottom-right-radius: 4px; }

/* ── INPUT — correction texte invisible */
.stTextInput > div > div > input {
    background: #FFFFFF !important;
    color: #1A1A2E !important;
    -webkit-text-fill-color: #1A1A2E !important;
    border: 2px solid var(--blue-light) !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.9rem !important;
    font-family: 'DM Sans', sans-serif !important;
    caret-color: var(--blue-deep) !important;
    opacity: 1 !important;
}
.stTextInput > div > div > input::placeholder {
    color: #AAAACC !important;
    -webkit-text-fill-color: #AAAACC !important;
    opacity: 1 !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue-mid) !important;
    box-shadow: 0 0 0 3px rgba(26,86,196,0.12) !important;
    outline: none !important;
}

/* ── Bouton envoyer */
.send-btn .stButton > button {
    background: var(--blue-deep) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    height: 44px !important;
}
.send-btn .stButton > button:hover {
    background: var(--blue-mid) !important;
    transform: translateY(-1px) !important;
}

/* ── Boutons suggestion */
.sugg-btn .stButton > button {
    background: white !important;
    color: var(--blue-deep) !important;
    border: 1.5px solid var(--blue-light) !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 0.6rem !important;
    transition: all 0.15s !important;
}
.sugg-btn .stButton > button:hover {
    background: var(--blue-pale) !important;
    border-color: var(--blue-mid) !important;
}

/* ── Cacher branding Streamlit */
#MainMenu, footer { visibility: hidden; }
.stDeployButton   { display: none; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
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
# SESSION STATE
# ──────────────────────────────────────────────

if "agent"        not in st.session_state: st.session_state.agent        = None
if "messages"     not in st.session_state: st.session_state.messages     = []
if "current_uid"  not in st.session_state: st.session_state.current_uid  = None
if "input_key"    not in st.session_state: st.session_state.input_key    = 0
if "pending_sugg" not in st.session_state: st.session_state.pending_sugg = None


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

    st.markdown('<p style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.45);margin:0 0 5px;">Profil conductrice</p>', unsafe_allow_html=True)

    profile_map = {
        f"{u['prenom']} — {next((v['marque']+' '+v['modele'] for v in vehicles if v['user_id']==u['user_id']),'?')}": u['user_id']
        for u in users
    }
    chosen_label = st.selectbox("Profil", list(profile_map.keys()), label_visibility="collapsed")
    chosen_uid   = profile_map[chosen_label]

    if chosen_uid != st.session_state.current_uid:
        st.session_state.agent       = StellaAgent(user_id=chosen_uid)
        st.session_state.messages    = []
        st.session_state.current_uid = chosen_uid
        st.session_state.input_key  += 1

    user    = next(u for u in users    if u["user_id"] == chosen_uid)
    vehicle = next(v for v in vehicles if v["user_id"] == chosen_uid)

    mot_icon = {"electrique":"⚡","hybride":"🔋","thermique":"⛽"}.get(vehicle["motorisation"],"🚗")
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
        e_lbl, e_val = "🔋 Batterie", f"{vehicle.get('niveau_batterie_pct','?')}% — {vehicle.get('autonomie_restante_km','?')} km"
    elif vehicle["motorisation"] == "hybride":
        e_lbl, e_val = "⛽/🔋", f"{vehicle.get('niveau_carburant_pct','?')}% / {vehicle.get('niveau_batterie_hybride_pct','?')}%"
    else:
        e_lbl, e_val = "⛽ Carburant", f"{vehicle.get('niveau_carburant_pct','?')}%"

    extra = ""
    if voyants:
        extra += f'<div class="veh-alert">⚠️ {voyants[0].get("libelle","Voyant actif")}</div>'
    if vehicle.get("anniversaire_vehicule_dans_jours") == 0:
        extra += '<div class="veh-celebrate">🎉 Anniversaire du véhicule aujourd\'hui !</div>'

    st.markdown(f"""
    <div class="veh-box">
        <div class="veh-label">État du véhicule</div>
        <div class="veh-row"><span>{e_lbl}</span><span>{e_val}</span></div>
        <div class="veh-row"><span>🔧 Révision dans</span><span>{vehicle.get('km_avant_revision','?')} km</span></div>
        <div class="veh-row"><span>📍</span><span>{user['ville']}</span></div>
        {extra}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.agent:
        m = st.session_state.agent.get_metrics()
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="metric-val">{m['nb_tours_conversation']}</div>
                <div class="metric-lbl">échanges</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{m['nb_appels_tools']}</div>
                <div class="metric-lbl">tools</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{m.get('cout_estime_eur',0):.4f}€</div>
                <div class="metric-lbl">coût</div>
            </div>
        </div>
        <div style="text-align:center;font-size:0.68rem;color:rgba(255,255,255,0.35);margin-top:3px;">
            {m.get('tokens_total',0):,} tokens
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🏠 Nouvelle conversation", use_container_width=True):
        if st.session_state.agent:
            st.session_state.agent.reset_conversation()
        st.session_state.messages = []
        st.session_state.input_key += 1
        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:1rem;font-size:0.6rem;color:rgba(255,255,255,0.2);">
        STELLANTIS © 2026 · Women in GenAI Hackathon
    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# ZONE PRINCIPALE
# ──────────────────────────────────────────────

st.markdown(f"""
<div class="chat-header">
    <div class="chat-avatar-hdr">🌟</div>
    <div>
        <div class="chat-hdr-title">Stella</div>
        <div class="chat-hdr-sub">
            <span class="online-dot"></span>En ligne · Compagnon de {user['prenom']}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Traitement suggestion en attente (doit être avant l'affichage)
if st.session_state.pending_sugg:
    msg = st.session_state.pending_sugg
    st.session_state.pending_sugg = None
    st.session_state.messages.append({"role": "user", "content": msg})
    with st.spinner("Stella réfléchit..."):
        resp = st.session_state.agent.chat(msg)
    st.session_state.messages.append({"role": "assistant", "content": resp})
    st.rerun()

# ── Affichage messages ou accueil
if not st.session_state.messages:

    # Message de bienvenue contextuel
    bat   = vehicle.get("niveau_batterie_pct", 100)
    anniv = vehicle.get("anniversaire_vehicule_dans_jours")
    if voyants:
        welcome = f"👋 Bonjour {user['prenom']} ! J'ai vu qu'un voyant est allumé sur ta {vehicle['marque']} {vehicle['modele']}. Tu veux qu'on s'en occupe ?"
    elif bat < 30:
        welcome = f"⚡ Bonjour {user['prenom']} ! Ta batterie est à {bat}%. Je peux t'aider à trouver une borne proche."
    elif anniv == 0:
        welcome = f"🎉 Bonjour {user['prenom']} ! Aujourd'hui c'est l'anniversaire de ta voiture ! J'ai une surprise pour toi... 🎁"
    else:
        welcome = f"👋 Bonjour {user['prenom']} ! Comment puis-je t'aider aujourd'hui ?"

    st.markdown(f"""
    <div class="messages-zone">
        <div class="msg-row">
            <div class="msg-ico stella">🌟</div>
            <div class="bubble stella">{welcome}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="text-align:center;font-size:0.7rem;color:#AAAACC;text-transform:uppercase;letter-spacing:0.8px;margin:0.5rem 0;">Suggestions rapides</p>', unsafe_allow_html=True)

    suggestions = [
        ("🔧 Mon entretien",  "Quel est l'état de mon entretien ?"),
        ("⭐ Mes avantages",  "Montre-moi mes avantages fidélité."),
        ("📍 Garage proche", "Trouve-moi un garage agréé proche."),
        ("⚡ Recharge",       "Aide-moi à trouver une borne de recharge."),
    ]
    cols = st.columns(4)
    for col, (label, query) in zip(cols, suggestions):
        with col:
            st.markdown('<div class="sugg-btn">', unsafe_allow_html=True)
            if st.button(label, use_container_width=True, key=f"sg_{label}"):
                st.session_state.pending_sugg = query
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Historique
    msgs_html = ""
    for msg in st.session_state.messages:
        content = msg["content"].replace("\n", "<br>").replace("**", "")
        if msg["role"] == "user":
            msgs_html += f"""
            <div class="msg-row user">
                <div class="msg-ico user">👤</div>
                <div class="bubble user">{content}</div>
            </div>"""
        else:
            msgs_html += f"""
            <div class="msg-row">
                <div class="msg-ico stella">🌟</div>
                <div class="bubble stella">{content}</div>
            </div>"""

    st.markdown(f'<div class="messages-zone">{msgs_html}</div>', unsafe_allow_html=True)

   

# Zone saisie
inp_col, btn_col = st.columns([5, 1])
with inp_col:
    user_input = st.text_input(
        "msg",
        placeholder="Écris un message à Stella...",
        label_visibility="collapsed",
        key=f"inp_{st.session_state.input_key}"
    )
with btn_col:
    st.markdown('<div class="send-btn">', unsafe_allow_html=True)
    send = st.button("Envoyer →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if send and user_input.strip():
    msg = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": msg})
    st.session_state.input_key += 1
    with st.spinner("Stella réfléchit..."):
        resp = st.session_state.agent.chat(msg)
    st.session_state.messages.append({"role": "assistant", "content": resp})
    st.rerun()