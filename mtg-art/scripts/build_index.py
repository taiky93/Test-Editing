#!/usr/bin/env python3
"""Construit l'index de recherche : chaque illustration réduite à 64x48 (RGB) dans data/index.npy,
dans le même ordre que data/index_meta.json. Relancer après un nouveau téléchargement."""
import json, pathlib, numpy as np, concurrent.futures as cf
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent
data = root / "data"
W, H = 64, 48
cards = [c for c in json.loads((data / "cards.json").read_text()) if (data / "art" / (c["id"] + ".jpg")).exists()]

def thumb(c):
    try:
        im = Image.open(data / "art" / (c["id"] + ".jpg")).convert("RGB")
        return (np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.uint8),
                np.asarray(im.resize((W * 2, H * 2), Image.LANCZOS), dtype=np.uint8))
    except Exception:
        return None

with cf.ProcessPoolExecutor() as ex:
    thumbs = list(ex.map(thumb, cards, chunksize=256))
keep = [i for i, t in enumerate(thumbs) if t is not None]
np.save(data / "index.npy", np.stack([thumbs[i][0] for i in keep]))
# Index 128x96, pour les captures où seul un petit détail est visible
big = np.lib.format.open_memmap(data / "index128.npy", mode="w+", dtype=np.uint8, shape=(len(keep), H * 2, W * 2, 3))
for j, i in enumerate(keep):
    big[j] = thumbs[i][1]
big.flush()
(data / "index_meta.json").write_text(json.dumps([cards[i] for i in keep], ensure_ascii=False))
print(len(keep), "illustrations indexées")
