#!/usr/bin/env python3
"""« Bourse de pièces d'or qui fait tching » — synthèse physique plus réaliste que gen-coins.py :
pièces lourdes (fondamentale plus grave, modes irréguliers propres à chaque pièce), salve dense de micro-chocs
étouffés par la bourse, 2-3 pièces qui sonnent clair (le « tching »), quelques pièces qui se posent,
choc sourd de la bourse et petite réverbération de pièce. Déterministe (graines fixes).
Usage : python3 scripts/gen-gold.py   (écrit sfx/coins/D-*.wav, E-*.wav, F-*.wav)"""
import numpy as np, wave, pathlib
SR = 44100
OUT = pathlib.Path(__file__).resolve().parent.parent / "sfx" / "coins"; OUT.mkdir(parents=True, exist_ok=True)

def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y

def hp(x, fc): return x - lp(x, fc)

def coin(rng, f0, ring, dur):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    ratios = [1.0, rng.uniform(1.48, 1.7), rng.uniform(2.0, 2.35), rng.uniform(2.6, 2.95),
              rng.uniform(3.1, 3.55), rng.uniform(4.0, 4.6), rng.uniform(5.0, 5.8)]
    for k, r in enumerate(ratios):
        f = f0 * r
        if f > 17000: break
        amp = rng.uniform(0.35, 1.0) * 0.72 ** k
        d = ring * rng.uniform(0.6, 1.2) / (1 + 0.6 * k)
        beat = 1 + 0.25 * np.sin(2 * np.pi * rng.uniform(2, 9) * t)   # battements (pièce pas parfaitement ronde)
        y += amp * beat * np.exp(-t / d) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    att = int(0.0004 * SR); y[:att] *= np.linspace(0, 1, att)
    click = hp(rng.standard_normal(n) * np.exp(-t / 0.00025), 3000)    # contact métal/métal très bref
    return y + 0.5 * click

def place(buf, x, at, g):
    i = int(at * SR); j = min(len(buf), i + len(x));
    if i < len(buf): buf[i:j] += g * x[: j - i]

def thud(rng, n, gain, length=0.035):
    t = np.arange(n) / SR
    return gain * lp(lp(rng.standard_normal(n), 260), 260) * np.exp(-t / length) * 6

def room(x, rng, mix=0.16, rt=0.16):
    n = int(rt * 4 * SR); t = np.arange(n) / SR
    ir = lp(rng.standard_normal(n), 6000) * np.exp(-t / (rt / 3))
    ir[:int(0.006 * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n; F = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[: len(x)]
    return x + mix * wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(x))

def write(x, name):
    fade = int(0.04 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, 29) * 0.95], 1)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())

def bag(seed, length, n_burst, n_clear, n_settle, weight, name):
    rng = np.random.default_rng(seed); buf = np.zeros(int(length * SR))
    for _ in range(n_burst):                                   # salve dense, étouffée par la bourse
        at = abs(rng.normal(0.0, 0.03)) + 0.005
        place(buf, coin(rng, rng.uniform(1700, 3300), rng.uniform(0.015, 0.05), 0.25), at, rng.uniform(0.08, 0.35))
    for i in range(n_clear):                                   # le « tching » : pièces qui sonnent clair
        at = 0.012 + i * rng.uniform(0.025, 0.05)
        place(buf, coin(rng, rng.uniform(2000, 2900), rng.uniform(0.28, 0.5), 1.0), at, rng.uniform(0.55, 0.9))
    for i in range(n_settle):                                  # pièces qui se posent
        at = 0.09 + rng.uniform(0, 0.22) * (i + 1) / n_settle
        place(buf, coin(rng, rng.uniform(1800, 3200), rng.uniform(0.04, 0.12), 0.4), at, rng.uniform(0.1, 0.3))
    buf = hp(buf, 400)
    buf += thud(rng, len(buf), weight)                          # poids de la bourse
    buf = room(buf, rng)
    write(buf, name)

if __name__ == "__main__":
    bag(11, 0.9, 34, 3, 6, 0.35, "D-bourse-or-tching")       # proposition principale (chaque prix)
    bag(12, 0.6, 16, 2, 3, 0.2, "E-tching-court")            # plus léger, pour les petits prix
    bag(13, 1.3, 70, 4, 14, 0.7, "F-grosse-bourse")          # plus lourd, pour le hit
    print("ok")
