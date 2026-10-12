#!/usr/bin/env bash
# Construit source/edited.mp4 depuis « video 7.mp4 » et « video 7 preview.mp4 » :
# métadonnées (GPS) supprimées, correction de lumière, ouverture ×3, insertion de la preview du hit,
# et accroche « suspense » au tout début : ralenti ×3 sur le moment où seul le bas du hit est visible, puis image figée.
# Usage : bash scripts/build-video.sh   (depuis videos/booster-v7)
set -euo pipefail
MAIN="../video 7.mp4"; PREV="../video 7 preview.mp4"
# Lumière : la vidéo est sous-exposée (hautes lumières à ~160/255) → on étire les niveaux,
# léger gamma, +15 % de saturation, un peu de netteté. Les noirs (gants) restent noirs.
GRADE="colorlevels=rimin=0.04:gimin=0.04:bimin=0.04:rimax=0.80:gimax=0.80:bimax=0.80,eq=gamma=1.06:saturation=1.15,unsharp=5:5:0.35"
FMT="scale=1080:1920:flags=lanczos,fps=30,${GRADE},format=yuv420p"
ffmpeg -v error -stats -y -i "$MAIN" -i "$PREV" -filter_complex "
[0:v]split=2[src][tsrc];
[tsrc]scale=1080:1920:flags=lanczos,${GRADE},trim=62.05:62.38,setpts=(PTS-STARTPTS)*3,minterpolate=fps=30:mi_mode=mci,tpad=stop_mode=clone:stop_duration=1.3,format=yuv420p,setpts=PTS-STARTPTS[t];
[src]${FMT},split=4[m1][m2][m3][m4];
[m1]trim=0:3,setpts=PTS-STARTPTS[a];
[m2]trim=3:12.5,setpts=(PTS-STARTPTS)/3[b];
[m3]trim=12.5:64,setpts=PTS-STARTPTS[c];
[1:v]${FMT},trim=0.5:8.5,setpts=PTS-STARTPTS[h];
[m4]trim=72.5:78.0,setpts=PTS-STARTPTS[d];
[t][a][b][c][h][d]concat=n=6:v=1:a=0[v]" \
  -map "[v]" -an -map_metadata -1 -map_chapters -1 -c:v libx264 -preset medium -crf 16 -movflags +faststart source/edited.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 source/edited.mp4
