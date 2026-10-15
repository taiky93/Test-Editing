#!/usr/bin/env bash
# Construit source/edited.mp4 depuis « Video 8.mp4 » : métadonnées (GPS) supprimées, lumière corrigée,
# début resserré : la caméra a été touchée pendant l'ouverture du paquet (mains collées à l'objectif,
# image qui bouge), donc on COUPE la majeure partie de l'ouverture au lieu de seulement accélérer.
# Usage : bash scripts/build-video.sh   (depuis videos/booster-v8)
set -euo pipefail
MAIN="../Video 8.mp4"
# Vidéo 8 déjà plus claire que la 7 (blancs ~195/255) : correction plus douce pour ne pas brûler les cartes.
GRADE="colorlevels=rimin=0.07:gimin=0.07:bimin=0.07:rimax=0.86:gimax=0.86:bimax=0.86,eq=gamma=1.0:saturation=1.15,unsharp=5:5:0.35"
FMT="scale=1080:1920:flags=lanczos,fps=30,${GRADE},format=yuv420p"
ffmpeg -v error -stats -y -i "$MAIN" -filter_complex "
[0:v]${FMT},split=5[m1][m2][m3][m4][m5];
[m1]trim=0:1.5,setpts=PTS-STARTPTS[a];
[m2]trim=1.5:7,setpts=(PTS-STARTPTS)/2[b];
[m3]trim=7:10,setpts=(PTS-STARTPTS)/3[c];
[m4]trim=26:35,setpts=(PTS-STARTPTS)/3[d];
[m5]trim=35:91.3,setpts=PTS-STARTPTS[e];
[a][b][c][d][e]concat=n=5:v=1:a=0[v]" \
  -map "[v]" -an -map_metadata -1 -map_chapters -1 -c:v libx264 -preset medium -crf 16 -movflags +faststart source/edited.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 source/edited.mp4
