#!/usr/bin/env bash
# Vidéo 8 montée exactement comme la V2 Final Fantasy (booster-v3/v2) : pas de correction de lumière,
# ouverture accélérée ×3, métadonnées (GPS) supprimées, 1080×1920 à 30 i/s.
# Le passage où la caméra a été touchée (10–26 s) reste coupé.
# Usage : bash scripts/build-video.sh   (depuis videos/booster-v8-ff)
set -euo pipefail
MAIN="../Video 8.mp4"
FMT="scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"
ffmpeg -v error -stats -y -i "$MAIN" -filter_complex "
[0:v]${FMT},split=4[m1][m2][m3][m4];
[m1]trim=0:3,setpts=PTS-STARTPTS[a];
[m2]trim=3:10,setpts=(PTS-STARTPTS)/3[b];
[m3]trim=26:35,setpts=(PTS-STARTPTS)/3[c];
[m4]trim=35:91.3,setpts=PTS-STARTPTS[d];
[a][b][c][d]concat=n=4:v=1:a=0[v]" \
  -map "[v]" -an -map_metadata -1 -map_chapters -1 -c:v libx264 -preset medium -crf 16 -movflags +faststart source/edited.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 source/edited.mp4
