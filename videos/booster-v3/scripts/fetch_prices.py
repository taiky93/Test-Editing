#!/usr/bin/env python3
"""Remplit les prix de vX/cards.json depuis le price guide public Cardmarket (champ « low » =
1er prix référencé, « low-foil » pour les foils). Correspondance carte → produit Cardmarket via Scryfall.
Usage : python3 scripts/fetch_prices.py <price_guide.json> v1 v2 v3"""
import json, sys, time, urllib.request, urllib.parse, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
pg = {g["idProduct"]: g for g in json.load(open(sys.argv[1]))["priceGuides"]}
UA = {"User-Agent": "booster-edit/1.0", "Accept": "application/json"}

def get(url):
    time.sleep(0.12)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))

def search(q):
    url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode({"q": q, "unique": "prints", "order": "set"})
    out = []
    while url:
        d = get(url); out += d["data"]; url = d.get("next_page")
    return out

cache = {}
def english_prints(set_code):
    if set_code not in cache:
        cache[set_code] = search(f"set:{set_code} lang:en")
    return cache[set_code]

def find(name, set_code, lang):
    base = name.split(" // ")[0]
    if lang == "fr":
        fr = [c for c in search(f"set:{set_code} lang:fr") ] if (set_code, "fr") not in cache else cache[(set_code, "fr")]
        cache[(set_code, "fr")] = fr
        hits = [c for c in fr if (c.get("printed_name") or "").lower() == base.lower()]
        if not hits: return None
        nums = {c["collector_number"] for c in hits}
        en = [c for c in english_prints(set_code) if c["collector_number"] in nums]
    else:
        en = [c for c in english_prints(set_code) if c["name"].split(" // ")[0].lower() == base.lower()
              or c["name"].lower() == name.lower()]
    en = [c for c in en if c.get("cardmarket_id")]
    if not en: return None
    def key(c):
        n = c["collector_number"]; digits = "".join(ch for ch in n if ch.isdigit()) or "99999"
        return (not c.get("booster", False), int(digits))
    return sorted(en, key=key)[0]

for v in sys.argv[2:]:
    p = root / v / "cards.json"; d = json.loads(p.read_text(encoding="utf-8"))
    lang = "fr" if "FR" in d["set"] else "en"
    for c in d["cards"]:
        if c.get("skip"): continue
        card = find(c["name"], c["set"].lower(), lang)
        if not card:
            c["priceSource"] = "introuvable sur Scryfall"; print(v, c["name"], "→ introuvable"); continue
        g = pg.get(card["cardmarket_id"])
        field = "low-foil" if c["foil"] else "low"
        c["cardmarketId"] = card["cardmarket_id"]; c["collector"] = card["collector_number"]
        c["cardmarketUrl"] = (card.get("purchase_uris") or {}).get("cardmarket")
        if g and g.get(field) is not None:
            c["price"] = round(g[field], 2)
            c["priceSource"] = f"Cardmarket price guide, « {field} » (1er prix référencé)"
        else:
            c["priceSource"] = f"Cardmarket : pas de valeur « {field} »"
        print(f'{v} {c["name"]:34s} #{card["collector_number"]:>5} idCM={card["cardmarket_id"]} {field}={c.get("price")}')
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
