#!/usr/bin/env python3
"""Cherche un détail visible (ex. un oeil sur fond noir) N'IMPORTE OÙ dans toutes les illustrations,
à plusieurs tailles : utile quand le jeu ne cadre pas l'illustration comme Scryfall.
Usage : python3 scripts/find_patch.py <capture.png> [--thr 15] [--top 10] [--width 320]
La plus grande zone non noire de la capture sert de modèle ; le noir est ignoré."""
import argparse, json, pathlib, numpy as np, cv2, concurrent.futures as cf

root = pathlib.Path(__file__).resolve().parent.parent
data = root / "data"
ap = argparse.ArgumentParser()
ap.add_argument("image"); ap.add_argument("--thr", type=int, default=15)
ap.add_argument("--top", type=int, default=10); ap.add_argument("--width", type=int, default=320)
ap.add_argument("--all", action="store_true", help="modèle = toutes les zones visibles (et pas seulement la plus grande)")
ap.add_argument("--zooms", default="0.6,0.75,0.9,1.0,1.1,1.25,1.5,1.8")
a = ap.parse_args()

g = cv2.imread(a.image, cv2.IMREAD_COLOR)
vis = (g.max(axis=2) > a.thr).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(vis, np.ones((9, 9), np.uint8)))
if a.all:
    ys, xs = np.nonzero(vis); x, y, w, h = xs.min(), ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
else:
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = st[k, :4]
tpl0, msk0 = g[y:y + h, x:x + w], vis[y:y + h, x:x + w] * 255
print(f"modèle : {w}x{h} px en ({x},{y}) sur une capture de {g.shape[1]}x{g.shape[0]}")
ZOOMS = [float(z) for z in a.zooms.split(",")]
base = a.width / g.shape[1]
TPL = []
for z in ZOOMS:
    tw, th = max(6, round(w * base * z)), max(6, round(h * base * z))
    TPL.append((z, cv2.resize(tpl0, (tw, th), interpolation=cv2.INTER_AREA), cv2.resize(msk0, (tw, th), interpolation=cv2.INTER_NEAREST)))
meta = json.loads((data / "index_meta.json").read_text())

def score(i):
    im = cv2.imread(str(data / "art" / (meta[i]["id"] + ".jpg")), cv2.IMREAD_REDUCED_COLOR_2)
    if im is None:
        return (i, -1, None)
    im = cv2.resize(im, (a.width, round(im.shape[0] * a.width / im.shape[1])), interpolation=cv2.INTER_AREA)
    best = (-1, None)
    for z, t, m in TPL:
        if t.shape[0] >= im.shape[0] or t.shape[1] >= im.shape[1]:
            continue
        r = cv2.matchTemplate(im, t, cv2.TM_CCOEFF_NORMED, mask=m)
        r[~np.isfinite(r)] = -1
        _, mx, _, loc = cv2.minMaxLoc(r)
        if mx > best[0]:
            best = (mx, (z, loc))
    return (i, best[0], best[1])

with cf.ProcessPoolExecutor() as ex:
    res = list(ex.map(score, range(len(meta)), chunksize=200))
res.sort(key=lambda r: -r[1])
for rank, (i, s, where) in enumerate(res[:a.top], 1):
    c = meta[i]
    print(f"{rank:2d}. {s:.3f}  {c['name']}  [{c['set'].upper()} #{c['num']}]  {c['artist']}  zoom {where[0]} pos {where[1]}  {c['img']}")
(data / "last_patch_results.json").write_text(json.dumps([{"id": meta[i]["id"], "score": s, "where": w} for i, s, w in res[:50]]))
