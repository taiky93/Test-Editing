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

## Direction artistique
- Style « Gain/Perte » de la V2 : Montserrat 600/700, contour noir épais.
  - En haut à gauche : « Gain/Perte » blanc + compteur (rouge sous zéro, vert `#3cff3c` à partir de zéro), départ à -prix du booster.
  - Intro : gros « -XX,XX € » rouge + « le booster » au centre.
  - Prix de chaque carte : petit, vert, centré au-dessus de la carte, format `0,02 €`, apparaît 0,3 s après la carte.
- **Séquence HIT** (carte `"hit": true` + bloc `"hit"` dans `cards.json`) : coupe vers la preview du hit,
  flash blanc + zoom, halo doré, rayons, étincelles, « HIT ! » doré lettre par lettre, prix géant doré qui monte de 0 au prix,
  son spécial (boum + arpège). Le compteur monte en même temps.
- **Fin** : voile sombre, **WIN !** vert (rebond) si gain, **GAME OVER** rouge (secousse) si perte, montant ±XX,XX € dessous.
- **Lumière** : `colorlevels` (noirs 0,04, blancs 0,80) + `eq gamma 1.06 saturation 1.15` + `unsharp` léger.

## Sons
- Nappe douce de fond, carillon WIN / jingle GAME OVER, son spécial du hit.
- ⚠️ **À changer dès la prochaine vidéo** : le son à chaque prix est trop synthétique.
  Le remplacer par un son de **pièces de monnaie qui s'entrechoquent dans une bourse** (cliquetis métalliques courts + léger bruit de cuir/tissu).
  Un fichier fourni par l'utilisateur dans `sfx/price.(wav|mp3|m4a|ogg)` est toujours prioritaire.

## Musique
- Pas de musique protégée incrustée dans le fichier (l'utilisateur a déjà reçu un strike) : les musiques connues
  s'ajoutent dans l'éditeur TikTok (bibliothèque sous licence), ou on compose un thème original.
