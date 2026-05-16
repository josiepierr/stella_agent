"""
voice.py
Pipeline voix de Stella — STT Whisper + TTS OpenAI.
Version stable Streamlit : pas de boucle infinie, retour avec hash audio.
"""

import io
import os
import re
import hashlib
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TTS_VOICE = "nova"
TTS_MODEL = "tts-1"
STT_MODEL = "whisper-1"


def _openai_client():
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY manquante.")
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


# ──────────────────────────────────────────────
# STT — Speech to Text
# ──────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcrit un audio micro en texte via Whisper.
    """
    if not audio_bytes:
        return ""

    try:
        client = _openai_client()

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcript = client.audio.transcriptions.create(
            model=STT_MODEL,
            file=audio_file,
            language="fr",
            response_format="text"
        )

        return transcript.strip() if transcript else ""

    except Exception as e:
        print(f"[STT] Erreur transcription : {e}")
        return ""


# ──────────────────────────────────────────────
# TTS — Text to Speech
# ──────────────────────────────────────────────

def speak_response(text: str, max_chars: int = 500) -> bytes | None:
    """
    Convertit la réponse de Stella en MP3.
    """
    if not text:
        return None

    try:
        client = _openai_client()

        clean_text = _strip_markdown(text)

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars].rsplit(" ", 1)[0] + "..."

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
    Nettoie le markdown pour une lecture vocale naturelle.
    """
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"[✅⚠️🔴🟠🟡🟢🔧📍☎️🕒⭐✔️🚗💡📊🎯🔐🎁⚡]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ──────────────────────────────────────────────
# Streamlit widgets
# ──────────────────────────────────────────────

def render_voice_input() -> dict | None:
    """
    Affiche le micro Streamlit.

    Retourne :
    {
        "text": "...",
        "hash": "..."
    }

    Le hash permet à app.py d'éviter de retraiter le même audio à chaque rerun.
    """
    try:
        import streamlit as st

        audio_value = st.audio_input(
            "🎙️",
            label_visibility="collapsed",
            key="voice_input"
        )

        if audio_value is None:
            return None

        audio_bytes = audio_value.read()

        if not audio_bytes:
            return None

        audio_hash = hashlib.md5(audio_bytes).hexdigest()

        with st.spinner("Stella écoute..."):
            text = transcribe_audio(audio_bytes, filename="audio.wav")

        if not text:
            st.warning("Je n’ai pas bien entendu. Tu peux réessayer ou taper ton message.")
            return None

        st.caption(f"💬 Transcription : *{text}*")

        return {
            "text": text,
            "hash": audio_hash
        }

    except AttributeError:
        import streamlit as st
        st.info("🎙️ La fonction vocale nécessite Streamlit ≥ 1.31.")
        return None

    except Exception as e:
        import streamlit as st
        st.warning(f"Mode vocal indisponible : {e}")
        return None


def render_audio_player(audio_bytes: bytes, autoplay: bool = False) -> None:
    """
    Affiche la réponse audio de Stella.

    Par défaut autoplay=False pour éviter que le micro réécoute la réponse
    et relance une boucle.
    """
    if not audio_bytes:
        return

    try:
        import streamlit as st
        st.audio(audio_bytes, format="audio/mp3", autoplay=autoplay)
    except TypeError:
        import streamlit as st
        st.audio(audio_bytes, format="audio/mp3")