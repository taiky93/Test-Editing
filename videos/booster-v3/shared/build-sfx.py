#!/usr/bin/env python3
"""Construit sfx/sfx-track.wav d'une vidéo à partir de son cards.json.
Tes sons sont prioritaires : sfx/price.(wav|mp3|m4a|ogg), sfx/final.(…), sfx/bed.(…).
Sinon : tick doux pour chaque prix, jingle « game over » (ou carillon « win »), nappe douce.
Usage : python3 ../shared/build-sfx.py   (depuis le dossier vX)"""
import json, subprocess, pathlib
root = pathlib.Path.cwd(); sfx = root / "sfx"; sfx.mkdir(exist_ok=True)
d = json.loads((root / "cards.json").read_text(encoding="utf-8"))
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, a)], check=True)
def pick(n):
    for e in ("wav", "mp3", "m4a", "ogg"):
        p = sfx / f"{n}.{e}"
        if p.exists(): return p
cards = [c for c in d["cards"] if not c.get("skip") and c.get("price") is not None]
won = sum(round(c["price"] * 100) for c in cards) >= round(d["boosterPrice"] * 100)
dur = d["duration"]
price = pick("price")
if not price:
    e = "0.5*(1-exp(-600*t))*exp(-14*t)*(sin(2*PI*1318*t)+0.5*sin(2*PI*2637*t)+0.25*sin(2*PI*3955*t))"
    ff("-f", "lavfi", "-i", f"aevalsrc='{e}|{e}':s=44100:d=0.5", sfx / "gen-price.wav"); price = sfx / "gen-price.wav"
final = pick("final")
if not final:
    if won:
        e = "0.22*(1-exp(-300*t))*exp(-2*t)*(sin(2*PI*1047*t)+sin(2*PI*1319*t)*gte(t,0.12)+sin(2*PI*1568*t)*gte(t,0.24)+sin(2*PI*2093*t)*gte(t,0.36))"
        ff("-f", "lavfi", "-i", f"aevalsrc='{e}|{e}':s=44100:d=2.4", sfx / "gen-final.wav")
    else:
        # « game over » : 4 notes descendantes (sol, fa#, fa, mi) en onde carrée adoucie, la dernière tenue avec vibrato
        notes = [(392.0, 0.0, 0.32), (370.0, 0.34, 0.32), (349.2, 0.68, 0.32), (329.6, 1.02, 1.3)]
        parts = []
        for f, s, l in notes:
            parts.append(f"between(t,{s},{s+l})*exp(-1.6*(t-{s}))*(1-exp(-300*(t-{s})))*(sin(2*PI*{f}*(t-{s})+0.08*sin(2*PI*6*(t-{s})))+0.33*sin(3*(2*PI*{f}*(t-{s})))+0.2*sin(5*(2*PI*{f}*(t-{s}))))")
        e = "0.16*(" + "+".join(parts) + ")"
        ff("-f", "lavfi", "-i", f"aevalsrc='{e}|{e}':s=44100:d=2.6", "-af", "lowpass=f=2200", sfx / "gen-final.wav")
    final = sfx / "gen-final.wav"
bed = pick("bed")
if not bed:
    ch = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    for i, (a, b, c) in enumerate(ch):
        e = f"0.07*(sin(2*PI*{a}*t)+sin(2*PI*{b}*t)+0.8*sin(2*PI*{c}*t)+0.3*sin(2*PI*{a/2}*t))*(0.85+0.15*sin(2*PI*0.5*t))*min(1,t/0.6)*min(1,(4-t)/0.6)"
        ff("-f", "lavfi", "-i", f"aevalsrc='{e}|{e}':s=44100:d=4", sfx / f"_c{i}.wav")
    (sfx / "_l.txt").write_text("".join(f"file '_c{i}.wav'\n" for i in range(4)))
    ff("-f", "concat", "-safe", "0", "-i", sfx / "_l.txt", "-c", "copy", sfx / "_loop.wav")
    ff("-stream_loop", "-1", "-i", sfx / "_loop.wav", "-t", dur, "-af", f"lowpass=f=1600,afade=t=in:d=1.5,afade=t=out:st={dur-1.5}:d=1.5", sfx / "gen-bed.wav")
    for p in sfx.glob("_*"): p.unlink()
    bed = sfx / "gen-bed.wav"
ev = [(c["t"] + d.get("popDelay", 0.3), price, 0.9) for c in cards] + [(d["finalAt"] + 0.25, final, 1.0)]
ins = ["-i", bed]; ch = ["[0:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.5[b]"]; lab = "[b]"
for i, (t, src, vol) in enumerate(ev, 1):
    ms = int(t * 1000); ins += ["-i", src]
    ch.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[e{i}]"); lab += f"[e{i}]"
ch.append(f"{lab}amix=inputs={len(ev)+1}:normalize=0,atrim=0:{dur}[out]")
ff(*ins, "-filter_complex", ";".join(ch), "-map", "[out]", "-c:a", "pcm_s16le", sfx / "sfx-track.wav")
print(f"sfx-track.wav : {len(ev)} sons, fin {'win' if won else 'game over'}, sources {price.name} / {final.name} / {bed.name}")
