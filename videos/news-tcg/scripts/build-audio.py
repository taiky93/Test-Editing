#!/usr/bin/env python3
"""Génère la musique d'ambiance (synthèse, libre de droits) et les whooshs de défilement
à partir de scenes.json. Sortie : audio/bed.wav. Relancer si scenes.json change."""
import json, subprocess, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
sc = json.loads((root/"scenes.json").read_text(encoding="utf-8"))
dur = sc["duration"]
def ff(*a): subprocess.run(["ffmpeg","-v","error","-y",*a], check=True)
a = root/"audio"
# Nappe douce : accords Am - F - C - G (4 s chacun), sinus filtrés + léger trémolo
chords = [(220.0,261.63,329.63),(174.61,220.0,261.63),(261.63,329.63,392.0),(196.0,246.94,293.66)]
parts=[]
for i,(f1,f2,f3) in enumerate(chords):
    expr=f"0.09*(sin(2*PI*{f1}*t)+sin(2*PI*{f2}*t)+0.8*sin(2*PI*{f3}*t)+0.3*sin(2*PI*{f1/2}*t))*(0.85+0.15*sin(2*PI*0.5*t))*min(1,t/0.6)*min(1,(4-t)/0.6)"
    ff("-f","lavfi","-i",f"aevalsrc='{expr}|{expr}':s=44100:d=4",str(a/f"_c{i}.wav")); parts.append(a/f"_c{i}.wav")
lst=a/"_loop.txt"; lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
ff("-f","concat","-safe","0","-i",str(lst),"-c","copy",str(a/"_loop.wav"))
ff("-stream_loop","-1","-i",str(a/"_loop.wav"),"-t",str(dur),"-af",f"lowpass=f=1800,afade=t=in:d=1.5,afade=t=out:st={dur-2}:d=2",str(a/"_music.wav"))
# Whoosh : bruit filtré passe-bande avec enveloppe
ff("-f","lavfi","-i","anoisesrc=d=0.6:c=pink:a=0.6","-af","bandpass=f=1400:w=1200,afade=t=in:d=0.25,afade=t=out:st=0.3:d=0.3,volume=0.5","-ac","2",str(a/"_whoosh.wav"))
times=[f["t"] for f in sc["foci"][1:]]
ins=["-i",str(a/"_music.wav")]; chains=["[0:a]volume=1[m]"]; labels="[m]"
for i,t in enumerate(times,1):
    ins+=["-i",str(a/"_whoosh.wav")]; ms=int(max(0,t-0.25)*1000)
    chains.append(f"[{i}:a]adelay={ms}|{ms}[w{i}]"); labels+=f"[w{i}]"
chains.append(f"{labels}amix=inputs={len(times)+1}:normalize=0,atrim=0:{dur}[out]")
ff(*ins,"-filter_complex",";".join(chains),"-map","[out]",str(a/"bed.wav"))
for p in a.glob("_*"): p.unlink()
print("audio/bed.wav OK", dur, "s,", len(times), "whooshs")
