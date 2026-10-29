#!/usr/bin/env bash
# Construit source/edited.mp4 depuis « Video 13.mp4 » (même principe que la vidéo 8 v2) :
# métadonnées (GPS) supprimées ; la vidéo 13 est filmée en HDR (HLG, 10 bits) : conversion en SDR
# (sinon image délavée/surexposée) ; ouverture du paquet accélérée ×3 ; fin coupée après le jeton.
# Usage : bash scripts/build-video.sh   (depuis videos/booster-v13)
set -euo pipefail
MAIN="../Video 13.mp4"
TONEMAP="zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv"
# Étalonnage en Rec.709 (SDR, ce que TikTok affiche) : courbe en S douce (contraste) + vibrance
# (sature surtout les couleurs ternes, ménage les peaux et les cartes déjà vives) + netteté légère.
GRADE="curves=master='0/0 0.25/0.21 0.5/0.5 0.75/0.8 1/1',vibrance=intensity=0.35,eq=saturation=1.05,unsharp=5:5:0.35"
# format=yuv420p juste après la conversion HDR : sinon le redimensionnement délave l'image
FMT="${TONEMAP},format=yuv420p,scale=1080:1920:flags=lanczos,fps=30,${GRADE},format=yuv420p"
ffmpeg -v error -stats -y -i "$MAIN" -filter_complex "
[0:v]${FMT},split=3[m1][m2][m3];
[m1]trim=0:3,setpts=PTS-STARTPTS[a];
[m2]trim=3:12.5,setpts=(PTS-STARTPTS)/3[b];
[m3]trim=12.5:56.5,setpts=PTS-STARTPTS[c];
[a][b][c]concat=n=3:v=1:a=0[v]" \
  -map "[v]" -an -map_metadata -1 -map_chapters -1 -c:v libx264 -preset medium -crf 16 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart source/edited.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 source/edited.mp4
