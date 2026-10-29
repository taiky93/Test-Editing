#!/usr/bin/env python3
"""Télécharge toutes les illustrations uniques de Magic (Scryfall, art_crop) dans data/art/.
Usage : python3 scripts/download_art.py   (relançable : saute les images déjà téléchargées)"""
import gzip, json, pathlib, time, urllib.request, concurrent.futures as cf

root = pathlib.Path(__file__).resolve().parent.parent
data = root / "data"
art = data / "art"
art.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "mtg-art-finder/1.0", "Accept": "*/*"}

cards = []
with gzip.open(data / "unique-artwork.jsonl.gz", "rt") as f:
    for line in f:
        o = json.loads(line)
        face = o if o.get("image_uris") else (o.get("card_faces") or [{}])[0]
        iu = face.get("image_uris") or {}
        if not iu.get("art_crop"):
            continue
        cards.append({"id": o["id"], "name": o["name"], "set": o["set"], "set_name": o.get("set_name"),
                      "num": o.get("collector_number"), "artist": o.get("artist"), "lang": o.get("lang"),
                      "art": iu["art_crop"], "img": iu.get("normal")})
(data / "cards.json").write_text(json.dumps(cards, ensure_ascii=False))

def get(c):
    p = art / (c["id"] + ".jpg")
    if p.exists() and p.stat().st_size > 1000:
        return "skip"
    for attempt in range(4):
        try:
            p.write_bytes(urllib.request.urlopen(urllib.request.Request(c["art"], headers=H), timeout=60).read())
            return "ok"
        except Exception:
            time.sleep(2 ** attempt)
    return "fail"

t0 = time.time(); done = {"ok": 0, "skip": 0, "fail": 0}
with cf.ThreadPoolExecutor(8) as ex:
    for i, r in enumerate(ex.map(get, cards), 1):
        done[r] += 1
        if i % 1000 == 0 or i == len(cards):
            print(f"{i}/{len(cards)} {done} {time.time()-t0:.0f}s", flush=True)
print("FIN", done, flush=True)
