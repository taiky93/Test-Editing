# Référence — montage « ouverture de booster » (DA validée sur la vidéo 7)

Ce projet est **le modèle à copier** pour les prochaines ouvertures de booster.
Copier le dossier (sans `source/`, `renders/`, `snapshots/`), remplacer `cards.json`, adapter `scripts/build-video.sh`.

## Déroulé
1. **Analyse** : planches de vignettes (2 i/s), lecture du n° de collection en bas de chaque carte sur la 4K
   (`FRA ★ FR` = foil, `FRA • FR` = non-foil). Versions exactes via Scryfall (`set:<code> lang:fr`).
2. **Validation utilisateur** : tableau temps / carte / n° / finition / prix + prix du booster + vitesse.
   On ignore toujours les **jetons** et les **terrains de base**.
3. **Prix** : price guide public Cardmarket (`price_guide_1.json`), champ **tendance** (`trend`, ou `trend-foil` si foil).
   Jamais de scraping du site Cardmarket. Si l'utilisateur donne un prix relevé lui-même, il prime (le noter dans `priceSource`).
4. **Vidéo source** (`scripts/build-video.sh`) : métadonnées supprimées (GPS !), 1080×1920 à 30 i/s, audio d'origine retiré,
   ouverture du paquet accélérée **×3**, correction de lumière, insertion de la preview du hit.
5. **Sons** (`scripts/build-sfx.py`), **composition** (`index.html`), `check`, `snapshot`, `render`.
6. **Livraison** : métadonnées retirées du rendu, morceaux de 25 Mo + SHA-256 (+ commande `copy /b`), aperçu 720p < 30 Mo.

## Direction artistique (v2 de la vidéo 7, après le strike)
⚠️ Le style « Gain/Perte » (Montserrat, copié de la Référence 1) a valu **deux strikes** : ne plus l'utiliser.
On utilise le style **V3** (`booster-v3`, sans strike), avec les ajustements validés :
- **Accroche** (`"teaser"` dans `cards.json`) : 2,3 s tout au début — ralenti ×3 sur un moment où l'on ne voit
  qu'une partie du gros hit (jamais la carte entière), puis image figée + flash, zoom, secousse, vignette, **son de choc**.
- Ouverture : prix du booster en or (« 33€ ») en haut à gauche, Cinzel.
- Prix de chaque carte : Cinzel, **vert**, en haut à gauche, **sans devise**.
- **Gros prix** (≥ `bigPrice`, 20 €) : plus grand, gras, halo doré, rebond, pulsation, étincelles, **son cash**.
- **Barre** à **1 320 px** (un peu sous les 2/3, juste sous les cartes) : total (rose → vert), progression %, prix du booster en lavande (seul €).
- **Séquence HIT** (preview du hit) : flash, zoom, halo, rayons, « HIT ! » doré, prix géant vert qui monte sous la barre.
- **Fin** : voile, **WIN !** vert ou **GAME OVER** rouge (secousse), montant ±XX.XX €.
- **Lumière** : `colorlevels` (noirs 0,04, blancs 0,80) + `eq gamma 1.06 saturation 1.15` + `unsharp` léger.

## Sons (fournis par l'utilisateur, déclarés libres de droits — voir `sfx/sources/SOURCES.md`)
- `sfx/price.wav` : pièce qui tombe (0,5 s) pour chaque carte.
- `sfx/bigprice.wav` : cash (1,25 s) pour les prix ≥ 20 € et le hit.
- `sfx/shock.wav` : choc de l'accroche.
- Nappe douce (démarre après l'accroche) et carillon WIN / jingle GAME OVER générés par `scripts/build-sfx.py`.

## Musique
- Pas de musique protégée incrustée dans le fichier (l'utilisateur a déjà reçu un strike) : les musiques connues
  s'ajoutent dans l'éditeur TikTok (bibliothèque sous licence), ou on compose un thème original.
