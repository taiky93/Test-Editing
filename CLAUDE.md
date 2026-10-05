# Notes du projet

## Voix off des vidéos (à réutiliser par défaut)
- Voix validée : **Chris** (ElevenLabs, `iP95p4xoKVk53GoZ742B`), modèle `eleven_multilingual_v2`, en français.
- Réglages et description : `videos/news-tcg/voice.json` ; mode d'emploi : `videos/news-tcg/VOICE.md`.
- Générer une voix off : `python3 videos/news-tcg/scripts/tts.py <texte.txt> <sortie.mp3>`.
- La clé API ElevenLabs n'est jamais versionnée : la demander à l'utilisateur et la mettre dans un `.env` ignoré par git.
