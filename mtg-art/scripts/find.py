#!/usr/bin/env python3
"""Retrouve une carte Magic à partir d'une illustration partiellement cachée.
Usage : python3 scripts/find.py <capture.png> [--box x,y,w,h] [--hide x,y,w,h ...] [--mask-color R,G,B[,tol]] [--top 10]
  --box        zone de la capture qui contient l'illustration (par défaut : toute l'image)
  --hide       zones cachées à ignorer (répétable), en pixels de la capture
  --mask-color couleur unie du cache (ex. 0,0,0 pour du noir) : ces pixels sont ignorés
Compare seulement les pixels visibles, après normalisation de la luminosité et du contraste."""
import argparse, json, pathlib, numpy as np
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent
data = root / "data"
W, H = 64, 48

ap = argparse.ArgumentParser()
ap.add_argument("image")
ap.add_argument("--box")
ap.add_argument("--hide", action="append", default=[])
ap.add_argument("--mask-color")
ap.add_argument("--top", type=int, default=10)
a = ap.parse_args()

im = Image.open(a.image).convert("RGB")
ox = oy = 0
if a.box:
    x, y, w, h = map(int, a.box.split(","))
    im = im.crop((x, y, x + w, y + h)); ox, oy = x, y
full = np.asarray(im, dtype=np.float32)
vis = np.ones(full.shape[:2], dtype=bool)
for b in a.hide:
    x, y, w, h = map(int, b.split(","))
    vis[max(0, y - oy):y - oy + h, max(0, x - ox):x - ox + w] = False
if a.mask_color:
    v = list(map(int, a.mask_color.split(","))); tol = v[3] if len(v) > 3 else 12
    vis &= np.abs(full - np.array(v[:3])).max(axis=2) > tol

q = np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.float32)
m = np.asarray(Image.fromarray(vis.astype(np.uint8) * 255).resize((W, H), Image.BILINEAR)) > 250
if m.sum() < 20:
    raise SystemExit("Trop peu de pixels visibles pour comparer.")

idx = np.load(data / "index.npy", mmap_mode="r")
meta = json.loads((data / "index_meta.json").read_text())
qv = q[m]                                   # (n,3)
qv = (qv - qv.mean(0)) / (qv.std(0) + 1e-3)
scores = np.empty(len(idx), dtype=np.float32)
step = 4096
for s in range(0, len(idx), step):
    blk = np.asarray(idx[s:s + step], dtype=np.float32)[:, m]   # (b,n,3)
    blk = (blk - blk.mean(1, keepdims=True)) / (blk.std(1, keepdims=True) + 1e-3)
    scores[s:s + step] = np.abs(blk - qv).mean(axis=(1, 2))
order = np.argsort(scores)[:a.top]
print(f"{int(m.sum())}/{W*H} pixels visibles comparés")
for r, i in enumerate(order, 1):
    c = meta[i]
    print(f"{r:2d}. {scores[i]:.3f}  {c['name']}  [{c['set'].upper()} #{c['num']}]  {c['artist']}  {c['img']}")
