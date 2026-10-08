# Voix des vidéos « news TCG »

La voix off utilise **Chris** (bibliothèque ElevenLabs), avec les réglages de `voice.json`.
Ce fichier sert de référence pour que toutes les prochaines vidéos aient la même voix.

## Prérequis
1. Une clé API ElevenLabs (elevenlabs.io → profil → Developers → API Keys).
2. Un fichier `.env` dans le dossier du projet, **jamais poussé sur GitHub** (vérifie qu'il est dans `.gitignore`) :
   ```
   ELEVENLABS_API_KEY=sk_...
   ```

## Générer une voix off
```bash
python3 scripts/tts.py script.txt audio/voiceover.mp3
```
Le script lit `voice.json` (voix, modèle, réglages) et la clé dans `.env`.

## Réglages (dans `voice.json`)
| Réglage | Valeur | Effet |
|---|---|---|
| `stability` | 0.38 | plus bas = plus expressif ; plus haut = plus régulier |
| `similarity_boost` | 0.75 | fidélité au timbre de la voix |
| `style` | 0.35 | intensité du jeu (exagération) |
| `speed` | 1.1 | débit (0.7 à 1.2) |
| `model_id` | eleven_multilingual_v2 | modèle multilingue, français |

Pour une autre ambiance (plus posée, plus énergique), change seulement ces valeurs dans `voice.json` :
la voix reste la même.

## Bonnes pratiques
- Écris les nombres comme ils doivent être dits si la prononciation est mauvaise (« vingt-quatre heures »).
- Garde une ponctuation claire : les points et les virgules donnent les respirations.
- Offre gratuite ElevenLabs : ~10 000 caractères/mois, pas de droits commerciaux, il faut créditer ElevenLabs.
  Pour monétiser les vidéos, passe sur l'offre Starter.
- Si tu passes sur une offre payante et veux une voix 100 % unique, utilise Voice Design avec la
  description `style_description` de `voice.json`, puis remplace `voice_id`.
