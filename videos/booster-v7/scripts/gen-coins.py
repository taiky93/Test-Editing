#!/usr/bin/env python3
"""Génère des sons « pièces de monnaie » (synthèse physique simple, déterministe).
Chaque pièce = impact bref + modes inharmoniques d'un disque métallique qui décroissent.
Variantes : bourse (pièces étouffées dans du cuir), claires (pièces sur table), pluie (chute dans un tas).
Usage : python3 scripts/gen-coins.py   (écrit sfx/coins/*.wav)"""
import numpy as np, wave, pathlib
SR = 44100
OUT = pathlib.Path(__file__).resolve().parent.parent / "sfx" / "coins"; OUT.mkdir(parents=True, exist_ok=True)
RATIOS = [1.0, 1.59, 2.14, 2.65, 3.16, 3.65, 4.15]   # modes d'un disque mince (approx.)

def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y

def coin(rng, f0, ring, bright, dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, r in enumerate(RATIOS):
        f = f0 * r * (1 + rng.uniform(-0.012, 0.012))
        if f > 16000: break
        amp = rng.uniform(0.5, 1.0) * (bright ** k)
        decay = ring / (1 + 0.9 * k)              # les modes aigus s'éteignent plus vite
        y += amp * np.exp(-t / decay) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    click = rng.standard_normal(n) * np.exp(-t / 0.0015)  # impact
    return y * (1 - np.exp(-t / 0.0004)) + 0.6 * click

def place(buf, x, at, g):
    i = int(at * SR); j = min(len(buf), i + len(x)); buf[i:j] += g * x[: j - i]

def rustle(rng, n, length, fc_lo, fc_hi, gain):
    t = np.arange(n) / SR; nz = rng.standard_normal(n)
    band = onepole_lp(nz, fc_hi) - onepole_lp(nz, fc_lo)
    env = np.clip(t / 0.02, 0, 1) * np.exp(-np.maximum(t - 0.02, 0) / length)
    return gain * band * env

def finish(x, name, lp=None, fade=0.05):
    if lp: x = onepole_lp(x, lp)
    n = len(x); x[-int(fade * SR):] *= np.linspace(1, 0, int(fade * SR))
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, 37) * 0.96], 1)       # léger élargissement stéréo
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    return st

def bourse(seed=1):
    """Quelques pièces qui s'entrechoquent dans une bourse en cuir (étouffé, chaud)."""
    rng = np.random.default_rng(seed); buf = np.zeros(int(0.75 * SR))
    for i in range(9):
        at = 0.01 + rng.uniform(0, 0.24) * (i / 8) ** 0.8
        place(buf, coin(rng, rng.uniform(2300, 3600), ring=rng.uniform(0.05, 0.11), bright=0.55, dur=0.5), at, rng.uniform(0.25, 0.75))
    buf += rustle(rng, len(buf), 0.09, 350, 2600, 0.35)          # frottement du cuir
    thump = np.sin(2 * np.pi * 95 * np.arange(len(buf)) / SR) * np.exp(-np.arange(len(buf)) / SR / 0.04)
    buf += 0.25 * thump                                          # la bourse qu'on soupèse
    return finish(buf, "A-bourse", lp=7500)

def claires(seed=2):
    """Deux-trois pièces qui tintent nettement (plus brillant, plus de résonance)."""
    rng = np.random.default_rng(seed); buf = np.zeros(int(0.9 * SR))
    for at, g in ((0.0, 1.0), (0.07, 0.7), (0.115, 0.5), (0.2, 0.35)):
        place(buf, coin(rng, rng.uniform(2800, 4200), ring=rng.uniform(0.22, 0.35), bright=0.7), at, g)
    return finish(buf, "B-claires", lp=11000)

def pluie(seed=3):
    """Une poignée de pièces qui tombent sur un tas (plus long, idéal pour un gros prix / le hit)."""
    rng = np.random.default_rng(seed); buf = np.zeros(int(1.4 * SR))
    for i in range(22):
        at = rng.uniform(0, 0.6) ** 1.3
        place(buf, coin(rng, rng.uniform(2200, 4000), ring=rng.uniform(0.08, 0.25), bright=0.62, dur=0.7), at, rng.uniform(0.2, 0.8) * (1 - at))
    buf += rustle(rng, len(buf), 0.25, 400, 3000, 0.18)
    return finish(buf, "C-pluie", lp=9500)

if __name__ == "__main__":
    for f in (bourse, claires, pluie): f(); print("ok", f.__name__)
