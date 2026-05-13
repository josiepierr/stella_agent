"""
test_voice.py
Teste le pipeline voix de Stella (TTS + STT).
Place ce fichier dans : agent/
Lance avec : python agent/test_voice.py (depuis la racine du projet)
"""

import sys
import os

# Racine du projet = un niveau au-dessus de agent/
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from interface.voice import speak_response, transcribe_audio


# -- Test TTS ------------------------------------------------------------------

print("=" * 50)
print("Test 1 - TTS (texte -> audio)")
print("=" * 50)

audio = speak_response(
    "Bonjour Sofia ! Ta batterie est a 15 pourcent. "
    "Je te recommande une borne Free2Move a 800 metres. "
    "Tu veux que je t'y guide ?"
)

if audio:
    output_path = os.path.join(ROOT_DIR, "test_tts.mp3")
    with open(output_path, "wb") as f:
        f.write(audio)
    print("OK TTS - ecoute le fichier : " + output_path)
else:
    print("ECHEC TTS - verifie OPENAI_API_KEY dans ton .env")


# -- Test STT ------------------------------------------------------------------

print()
print("=" * 50)
print("Test 2 - STT (audio .m4a -> texte)")
print("=" * 50)

# Le fichier .m4a doit etre a la RACINE du projet
audio_file_path = os.path.join(ROOT_DIR, "test_voice.m4a")

if not os.path.exists(audio_file_path):
    print("Fichier introuvable : " + audio_file_path)
    print("  -> Place test_voice.m4a a la racine du projet et relance.")
else:
    print("Fichier trouve : " + audio_file_path)
    print("Transcription en cours...")

    with open(audio_file_path, "rb") as f:
        audio_bytes = f.read()

    # Passer "test_voice.m4a" comme filename
    # pour que Whisper detecte le bon format audio
    text = transcribe_audio(audio_bytes, filename="test_voice.m4a")

    if text:
        print('OK STT - transcription : "' + text + '"')
    else:
        print("ECHEC STT - verifie OPENAI_API_KEY dans ton .env")
        print("  -> Si l'erreur mentionne 'format', convertis le .m4a en .mp3")
