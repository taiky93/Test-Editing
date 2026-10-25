#!/usr/bin/env python3
"""Génère uniquement les whooshs de transition (pas de musique de fond : la musique est ajoutée dans TikTok)
à partir de scenes.json. Sortie : audio/bed.wav. Relancer si scenes.json change."""
import json, subprocess, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
sc = json.loads((root/"scenes.json").read_text(encoding="utf-8"))
dur = sc["duration"]
def ff(*a): subprocess.run(["ffmpeg","-v","error","-y",*a], check=True)
a = root/"audio"
# Whoosh : bruit filtré passe-bande avec enveloppe
ff("-f","lavfi","-i","anoisesrc=d=0.6:c=pink:a=0.6","-af","bandpass=f=1400:w=1200,afade=t=in:d=0.25,afade=t=out:st=0.3:d=0.3,volume=0.5","-ac","2",str(a/"_whoosh.wav"))
times=[f["t"] for f in sc["foci"][1:]]
ff("-f","lavfi","-i",f"anullsrc=r=44100:cl=stereo","-t",str(dur),str(a/"_music.wav"))  # piste muette de base
ins=["-i",str(a/"_music.wav")]; chains=["[0:a]volume=1[m]"]; labels="[m]"
for i,t in enumerate(times,1):
    ins+=["-i",str(a/"_whoosh.wav")]; ms=int(max(0,t-0.25)*1000)
    chains.append(f"[{i}:a]adelay={ms}|{ms}[w{i}]"); labels+=f"[w{i}]"
chains.append(f"{labels}amix=inputs={len(times)+1}:normalize=0,atrim=0:{dur}[out]")
ff(*ins,"-filter_complex",";".join(chains),"-map","[out]",str(a/"bed.wav"))
for p in a.glob("_*"): p.unlink()
print("audio/bed.wav OK", dur, "s,", len(times), "whooshs")
