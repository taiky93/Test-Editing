# Notes du projet

## Voix off des vidéos (à réutiliser par défaut)
- Voix validée : **Chris** (ElevenLabs, `iP95p4xoKVk53GoZ742B`), modèle `eleven_multilingual_v2`, en français.
- Réglages et description : `videos/news-tcg/voice.json` ; mode d'emploi : `videos/news-tcg/VOICE.md`.
- Générer une voix off : `python3 videos/news-tcg/scripts/tts.py <texte.txt> <sortie.mp3>`.
- La clé API ElevenLabs n'est jamais versionnée : la demander à l'utilisateur et la mettre dans un `.env` ignoré par git.

## Vidéos d'ouverture de booster (DA de référence)
- Modèle validé : **`videos/booster-v7/`** (vidéo 7). Tout est décrit dans `videos/booster-v7/REFERENCE.md` : à suivre pour chaque nouvelle ouverture.
- Prochaine vidéo : remplacer le son des prix par un son de **pièces de monnaie dans une bourse** (le son actuel est trop synthétique).
