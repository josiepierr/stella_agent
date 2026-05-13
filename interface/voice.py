"""
voice.py
Pipeline voix de Stella — STT (Whisper) + TTS (OpenAI TTS)

Intégration dans app.py :
    from voice import transcribe_audio, speak_response, render_voice_input

Usage :
    # STT : convertir l'audio micro en texte
    text = transcribe_audio(audio_bytes)

    # TTS : convertir la réponse Stella en audio
    audio_data = speak_response(response_text)

    # Widget micro Streamlit (à placer dans app.py à côté du text_input)
    render_voice_input()
"""

import io
import os
import base64

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Voix TTS — 'nova' (chaleureuse) ou 'shimmer' (douce)
# Choix recommandé pour Stella : 'nova'
TTS_VOICE = "nova"
TTS_MODEL = "tts-1"         # tts-1 = rapide, tts-1-hd = qualité max
STT_MODEL = "whisper-1"


# ──────────────────────────────────────────────
# STT — Speech to Text (Whisper API)
# ──────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcrit un enregistrement audio en texte via Whisper API.

    Args:
        audio_bytes : contenu binaire du fichier audio (wav, mp3, m4a, webm…)
        filename    : nom du fichier avec extension correcte (aide Whisper)

    Returns:
        Texte transcrit, ou "" si erreur.

    Coût estimé : ~0.006 $/minute d'audio
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcript = client.audio.transcriptions.create(
            model=STT_MODEL,
            file=audio_file,
            language="fr",          # forcer le français pour éviter les erreurs
            response_format="text"
        )
        return transcript.strip()

    except Exception as e:
        print(f"[STT] Erreur transcription : {e}")
        return ""


# ──────────────────────────────────────────────
# TTS — Text to Speech (OpenAI TTS)
# ──────────────────────────────────────────────

def speak_response(text: str, max_chars: int = 500) -> bytes | None:
    """
    Convertit la réponse de Stella en audio MP3 via OpenAI TTS.

    Args:
        text      : texte à lire (le markdown est nettoyé automatiquement)
        max_chars : tronque le texte si trop long (évite les coûts excessifs)

    Returns:
        Contenu binaire MP3, ou None si erreur.

    Coût estimé : ~0.015 $/1000 caractères (tts-1)
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Nettoyage du markdown pour une lecture naturelle
        clean_text = _strip_markdown(text)

        # Tronquer si nécessaire (évite de lire 3 paragraphes entiers)
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars].rsplit(' ', 1)[0] + "..."

        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=clean_text,
            response_format="mp3"
        )

        return response.content

    except Exception as e:
        print(f"[TTS] Erreur synthèse vocale : {e}")
        return None


def _strip_markdown(text: str) -> str:
    """
    Supprime le formatage markdown pour une lecture TTS naturelle.
    Exemples : **gras** → gras, # Titre → Titre, - item → item
    """
    import re
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)   # gras/italique
    text = re.sub(r'#{1,6}\s*', '', text)                   # titres
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)          # code
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)   # liens
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)  # listes
    text = re.sub(r'\n{2,}', '. ', text)                    # sauts de ligne → pause
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[✅⚠️🔴🟠🟡🟢🔧📍☎️🕒⭐✔️🚗💡📊🎯🔐]', '', text)  # emojis
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ──────────────────────────────────────────────
# Widget Streamlit — Micro + lecture audio
# ──────────────────────────────────────────────

def render_voice_input() -> str | None:
    """
    Affiche le widget micro Streamlit et retourne le texte transcrit.
    À appeler dans app.py à côté du text_input.

    Nécessite Streamlit >= 1.31 (st.audio_input disponible).

    Returns:
        Texte transcrit si l'utilisatrice a enregistré un message, sinon None.
    """
    try:
        import streamlit as st

        audio_value = st.audio_input(
            "🎙️ Parle à Stella",
            label_visibility="collapsed",
            key="voice_input"
        )

        if audio_value is not None:
            with st.spinner("Stella écoute..."):
                audio_bytes = audio_value.read()
                text = transcribe_audio(audio_bytes, filename="audio.wav")

            if text:
                st.caption(f"💬 Transcription : *{text}*")
                return text
            else:
                st.warning("Je n'ai pas bien entendu — tu peux réessayer ou taper ton message.")
                return None

        return None

    except AttributeError:
        # st.audio_input n'existe pas (Streamlit < 1.31)
        import streamlit as st
        st.info("🎙️ La fonction vocale nécessite Streamlit ≥ 1.31. "
                "Lance `pip install --upgrade streamlit` pour l'activer.")
        return None


def render_audio_player(audio_bytes: bytes) -> None:
    """
    Affiche un lecteur audio Streamlit pour la réponse TTS de Stella.
    À appeler dans app.py après chaque réponse si TTS activé.

    Args:
        audio_bytes : contenu MP3 retourné par speak_response()
    """
    import streamlit as st
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)


# ──────────────────────────────────────────────
# Intégration dans app.py — Guide copier-coller
# ──────────────────────────────────────────────
#
# 1. Ajouter l'import en haut de app.py :
#
#    from voice import render_voice_input, speak_response, render_audio_player
#
# 2. Dans la sidebar, ajouter un toggle :
#
#    voice_enabled = st.toggle("🎙️ Mode vocal", value=False, key="voice_toggle")
#
# 3. Dans la zone de saisie (à côté du form chat), ajouter :
#
#    if voice_enabled:
#        voice_text = render_voice_input()
#        if voice_text:
#            ask_stella(voice_text)
#            st.rerun()
#
# 4. Dans ask_stella(), après la réponse de l'agent, ajouter :
#
#    if st.session_state.get("voice_toggle") and response:
#        audio = speak_response(response)
#        if audio:
#            render_audio_player(audio)
#
