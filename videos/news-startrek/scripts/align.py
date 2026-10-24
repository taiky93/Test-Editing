#!/usr/bin/env python3
"""Aligne les mots exacts de script.txt sur les timings Whisper (audio/voiceover-whisper.json).
Sortie : audio/words.json  [{text, start, end, line}]"""
import json, re, difflib, unicodedata, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
def ts(s): h, m, rest = s.split(":"); sec, ms = rest.split(","); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)

wh = []
for s in json.loads((root/"audio/voiceover-whisper.json").read_text())["transcription"]:
    t = s["text"].strip()
    if not t or t.startswith("["): continue
    for part in t.split():
        wh.append({"n": norm(part), "start": ts(s["timestamps"]["from"]), "end": ts(s["timestamps"]["to"])})

sw = []
for li, line in enumerate((root/"script.txt").read_text(encoding="utf-8").splitlines()):
    for w in line.split():
        if norm(w): sw.append({"text": w, "n": norm(w), "line": li})
        elif sw: sw[-1]["text"] += " " + w   # ponctuation isolée (":" "?" "!") collée au mot précédent

sm = difflib.SequenceMatcher(a=[x["n"] for x in sw], b=[x["n"] for x in wh], autojunk=False)
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        sw[a+k]["start"], sw[a+k]["end"] = wh[b+k]["start"], wh[b+k]["end"]
# mots non appariés : interpolation entre voisins appariés
i = 0
while i < len(sw):
    if "start" in sw[i]: i += 1; continue
    j = i
    while j < len(sw) and "start" not in sw[j]: j += 1
    t0 = sw[i-1]["end"] if i > 0 else 0.0
    t1 = sw[j]["start"] if j < len(sw) else t0 + 0.3*(j-i)
    step = (t1 - t0) / (j - i)
    for k in range(i, j):
        sw[k]["start"], sw[k]["end"] = t0 + step*(k-i), t0 + step*(k-i+1)
    i = j
# Whisper compresse parfois plusieurs mots au même instant (début de segment) :
# on répartit ces grappes sur une fenêtre réaliste, au prorata du nombre de lettres.
MIN = 0.09
i = 0
while i < len(sw):
    j = i
    while j + 1 < len(sw) and sw[j]["end"] - sw[i]["start"] < MIN * (j - i + 1) and j - i < 6:
        j += 1
    n = j - i + 1
    if n > 1 or sw[i]["end"] - sw[i]["start"] < 0.04:
        prev_end = sw[i-1]["end"] if i > 0 else 0.0
        ws = max(prev_end, sw[i]["start"] - 0.25)
        limit = sw[j+1]["end"] - 0.06 if j + 1 < len(sw) else sw[j]["end"] + 0.5
        we = min(limit, max(sw[j]["end"], ws + 0.16 * n))
        lens = [max(2, len(norm(sw[k]["text"]))) for k in range(i, j + 1)]
        tot = sum(lens); t = ws
        for k, L in zip(range(i, j + 1), lens):
            sw[k]["start"] = t; t += (we - ws) * L / tot; sw[k]["end"] = t
        if j + 1 < len(sw) and sw[j+1]["start"] < we:
            sw[j+1]["start"] = we
    i = j + 1
matched = sum(n for *_, n in sm.get_matching_blocks())
out = [{"text": x["text"], "start": round(x["start"], 3), "end": round(x["end"], 3), "line": x["line"]} for x in sw]
(root/"audio/words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(out)} mots, {matched} appariés directement à Whisper, {len(out)-matched} interpolés")
