#!/usr/bin/env python3
"""Piste son du format « collection » : sons neutres, sans codes du jeu d'argent.
- un léger glissement de carte (souffle filtré) à chaque fiche ;
- un carillon doux pour la carte la plus rare ;
- une nappe calme en fond.
Pas de pièces, pas de caisse enregistreuse, pas de son de choc.
Usage : python3 scripts/build-sfx.py   (depuis le dossier du projet)"""
import json, subprocess, pathlib
root = pathlib.Path.cwd(); sfx = root / "sfx"; sfx.mkdir(exist_ok=True)
d = json.loads((root / "cards.json").read_text(encoding="utf-8"))
dur = d["duration"]
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, a)], check=True)
# glissement de carte : bruit rose filtré passe-bande qui monte, 0,28 s
ff("-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.6:d=0.28:seed=7", "-af",
   "highpass=f=900,lowpass=f=5200,afade=t=in:d=0.06,afade=t=out:st=0.08:d=0.2,volume=0.55,aformat=channel_layouts=stereo", sfx / "swipe.wav")
# carillon doux : 3 notes (mi, sol#, si) en cloche, sans cuivre ni jackpot
e = "+".join(f"gte(t,{0.11*i})*0.12*exp(-2.6*(t-{0.11*i}))*(sin(2*PI*{f}*t)+0.3*sin(2*PI*{2*f}*t))" for i, f in enumerate((659.25, 830.61, 987.77)))
ff("-f", "lavfi", "-i", f"aevalsrc='{e}|{e}':s=44100:d=2.4", "-af", "aecho=0.8:0.5:60:0.25", sfx / "chime.wav")
# nappe calme
ch = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
for i, (a, b, c) in enumerate(ch):
    x = f"0.06*(sin(2*PI*{a}*t)+sin(2*PI*{b}*t)+0.8*sin(2*PI*{c}*t))*min(1,t/0.8)*min(1,(4-t)/0.8)"
    ff("-f", "lavfi", "-i", f"aevalsrc='{x}|{x}':s=44100:d=4", sfx / f"_c{i}.wav")
(sfx / "_l.txt").write_text("".join(f"file '_c{i}.wav'\n" for i in range(4)))
ff("-f", "concat", "-safe", "0", "-i", sfx / "_l.txt", "-c", "copy", sfx / "_loop.wav")
ff("-stream_loop", "-1", "-i", sfx / "_loop.wav", "-t", dur, "-af", f"lowpass=f=1400,afade=t=in:d=2,afade=t=out:st={dur-2}:d=2", sfx / "bed.wav")
for p in sfx.glob("_*"): p.unlink()
ev = [(c["t"] + 0.35, sfx / "swipe.wav", 0.8) for c in d["cards"]]
if d.get("hit"): ev.append((d["hit"]["start"] + 0.4, sfx / "chime.wav", 0.9))
ins = ["-i", sfx / "bed.wav"]; chn = ["[0:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.6[b]"]; lab = "[b]"
for i, (t, src, vol) in enumerate(ev, 1):
    ms = int(t * 1000); ins += ["-i", src]
    chn.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[e{i}]"); lab += f"[e{i}]"
chn.append(f"{lab}amix=inputs={len(ev)+1}:normalize=0,volume=2.4,atrim=0:{dur}[out]")
ff(*ins, "-filter_complex", ";".join(chn), "-map", "[out]", "-c:a", "pcm_s16le", sfx / "sfx-track.wav")
print(f"sfx-track.wav : {len(ev)} sons (glissements + carillon), nappe calme, {dur} s")
