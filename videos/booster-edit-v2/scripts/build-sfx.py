#!/usr/bin/env python3
"""Construit sfx/sfx-track.wav à partir de cards.json.

Tes propres sons sont prioritaires s'ils existent : sfx/price.(wav|mp3|m4a|ogg) et sfx/final.(...).
Sinon le script génère sfx/gen-price.wav (ding court et brillant) et sfx/gen-final.wav (carillon plus marqué).
À relancer après une modification des timecodes dans cards.json :  python3 scripts/build-sfx.py
"""
import json, subprocess, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
sfx = root / "sfx"
data = json.loads((root / "cards.json").read_text(encoding="utf-8"))


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def pick(name):
    for ext in ("wav", "mp3", "m4a", "ogg", "aac"):
        p = sfx / f"{name}.{ext}"
        if p.exists():
            return p
    return None


def generate():
    # Ding court et brillant (sol 6 + harmoniques), attaque rapide, ~0,6 s de déclin
    ding = ("0.55*(1-exp(-400*t))*exp(-7*t)*(sin(2*PI*1568*t)+0.45*sin(2*PI*3136*t)"
            "+0.2*sin(2*PI*4704*t)+0.12*sin(2*PI*6272*t))")
    run(["-f", "lavfi", "-i", f"aevalsrc='{ding}|{ding}':s=44100:d=0.8", str(sfx / "gen-price.wav")])
    # Final : accord de do majeur en carillon + scintillement aigu, ~2 s
    chord = ("0.2*(1-exp(-300*t))*exp(-2.2*t)*(sin(2*PI*1047*t)+sin(2*PI*1319*t)+sin(2*PI*1568*t)"
             "+0.8*sin(2*PI*2093*t))+0.12*exp(-3*t)*sin(2*PI*5274*t)*(0.5+0.5*sin(2*PI*14*t))")
    run(["-f", "lavfi", "-i", f"aevalsrc='{chord}|{chord}':s=44100:d=2.2", str(sfx / "gen-final.wav")])


price = pick("price")
final = pick("final")
if not price or not final:
    generate()
price = price or sfx / "gen-price.wav"
final = final or sfx / "gen-final.wav"

delay = data.get("popDelay", 0.3)
events = [(c["t"] + delay, price) for c in data["cards"]]
events.append((data["finalAt"], final))

args, chains = [], []
for i, (t, src) in enumerate(events):
    args += ["-i", str(src)]
    ms = int(round(t * 1000))
    chains.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(events)))
chains.append(f"{mix}amix=inputs={len(events)}:normalize=0,apad,atrim=0:{data['duration']}[out]")
run([*args, "-filter_complex", ";".join(chains), "-map", "[out]", "-c:a", "pcm_s16le", str(sfx / "sfx-track.wav")])
print(f"sfx-track.wav : {len(events)} sons (prix : {price.name}, final : {final.name})")
