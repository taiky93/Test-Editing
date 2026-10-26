# Notes du projet

## Voix off des vidéos (à réutiliser par défaut)
- Voix validée : **Chris** (ElevenLabs, `iP95p4xoKVk53GoZ742B`), modèle `eleven_multilingual_v2`, en français.
- Réglages et description : `videos/news-tcg/voice.json` ; mode d'emploi : `videos/news-tcg/VOICE.md`.
- Générer une voix off : `python3 videos/news-tcg/scripts/tts.py <texte.txt> <sortie.mp3>`.
- Prononciation : dans les scripts, écrire **« mana » sans S**, même au pluriel (« trois mana ») : la voix prononce « manase » sinon.
- La clé API ElevenLabs n'est jamais versionnée : la demander à l'utilisateur et la mettre dans un `.env` ignoré par git.

## Vidéos d'ouverture de booster (DA de référence)
- Modèle validé : **`videos/booster-v7/`** (vidéo 7). Tout est décrit dans `videos/booster-v7/REFERENCE.md` : à suivre pour chaque nouvelle ouverture.
- Style **V3** (prix verts sans devise, barre à 1 320 px, accroche suspense seulement si hit > 50 €, son cash seulement ≥ 5 €, sons pièce/cash/choc de l'utilisateur). **Ne plus utiliser le style « Gain/Perte »** (deux strikes).

## Musique de fond
- **Plus jamais de musique / son de fond** dans les vidéos : l'utilisateur ajoute la musique avec l'outil TikTok. Les petits bruitages (whoosh, sons de cartes) restent possibles.
