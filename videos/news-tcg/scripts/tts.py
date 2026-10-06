#!/usr/bin/env python3
"""Génère une voix off ElevenLabs avec la voix définie dans voice.json.
Usage : python3 scripts/tts.py <texte.txt> <sortie.mp3>
La clé est lue dans .env (ELEVENLABS_API_KEY), jamais dans un fichier versionné."""
import json, pathlib, sys, urllib.request

root = pathlib.Path(__file__).resolve().parent.parent
voice = json.loads((root / "voice.json").read_text(encoding="utf-8"))
env = dict(l.split("=", 1) for l in (root / ".env").read_text().splitlines() if "=" in l)
key = env[voice["api_key_env"]].strip()

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").strip()
body = {"text": text, "model_id": voice["model_id"], "language_code": voice["language_code"],
        "voice_settings": voice["voice_settings"]}
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice['voice_id']}?output_format={voice['output_format']}"
req = urllib.request.Request(url, data=json.dumps(body).encode(),
                             headers={"xi-api-key": key, "Content-Type": "application/json"})
pathlib.Path(sys.argv[2]).write_bytes(urllib.request.urlopen(req, timeout=600).read())
print(f"OK : {sys.argv[2]} ({len(text)} caractères)")
