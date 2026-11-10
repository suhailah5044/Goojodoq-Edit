"""Synthesise the overlay sound effects (48 kHz mono WAV) into project/assets/sfx."""
import numpy as np, wave, os, sys
SR = 48000
OUT = sys.argv[1] if len(sys.argv) > 1 else "project/assets/sfx"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
t_ = lambda d: np.arange(int(SR * d)) / SR

def env(n, a=0.003, dec=0.25):
    t = np.arange(n) / SR
    e = np.exp(-t / dec)
    k = int(a * SR); e[:k] *= np.linspace(0, 1, k)
    return e

def bell(f, d=1.2, dec=0.35, parts=((1, 1), (2.76, .35), (5.4, .12), (8.9, .05))):
    t = t_(d); s = sum(g * np.sin(2*np.pi*f*m*t) * np.exp(-t/(dec/(1+m*.4))) for m, g in parts)
    return s * env(len(t), .002, 10)

def lp(x, a):  # one-pole lowpass
    y = np.zeros_like(x); p = 0.
    for i, v in enumerate(x): p += a*(v-p); y[i] = p
    return y

def save(name, x, peak=0.8):
    x = x / (np.abs(x).max() + 1e-9) * peak
    fade = int(.004*SR); x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(f"{OUT}/{name}.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x*32767).astype(np.int16).tobytes())

def mix(*parts):
    n = max(len(p) + int(o*SR) for o, p in parts); y = np.zeros(n)
    for o, p in parts: k = int(o*SR); y[k:k+len(p)] += p
    return y

# soft airy whoosh (hook entrance)
d = .55; t = t_(d); n = rng.standard_normal(len(t))
sweep = np.sin(np.pi * t / d) ** 2
w = lp(n, 0.02) * 0.6 + lp(n, 0.12) * sweep * 0.5
save("whoosh", w * sweep, .55)
# hook sparkle: whoosh + glassy chime pair
save("hook", mix((0, w*sweep*.6), (.30, bell(1568, 1.4, .5)*.5), (.38, bell(2349, 1.3, .45)*.35)), .7)
# ting (clean single bell)
save("ting", bell(2093, 1.0, .30), .6)
# ting2 (double ting)
save("ting2", mix((0, bell(1760, .9, .25)), (.09, bell(2637, 1.0, .28)*.8)), .6)
# pop (bubble)
t = t_(.12); f = 900*np.exp(-t*30)+260
save("pop", np.sin(2*np.pi*np.cumsum(f)/SR) * env(len(t), .001, .035), .7)
# UI click / tick
t = t_(.05); save("tick", (np.sin(2*np.pi*3200*t)*.6 + lp(rng.standard_normal(len(t)), .5)*.4) * env(len(t), .0005, .008), .5)
# UI prompt blip (two-tone confirm, like a connect sound)
t = t_(.11); b = lambda f: np.sin(2*np.pi*f*t)*env(len(t), .002, .05)
save("blip", mix((0, b(1318)), (.085, b(1975))), .55)
# shimmer (premium / estetik): fast rising bell arpeggio
notes = [1568, 1976, 2349, 2794, 3136]
save("shimmer", mix(*[(i*.045, bell(f, 1.2, .4)*(.8-i*.08)) for i, f in enumerate(notes)]), .55)
# bass thump for BASS SEDAP
t = t_(.45); f = 110*np.exp(-t*9)+45
save("bass", np.sin(2*np.pi*np.cumsum(f)/SR) * env(len(t), .002, .16) + lp(rng.standard_normal(len(t)), .05)*env(len(t), .001, .02)*.4, .9)
# cash (two quick high bells + tick)
save("cash", mix((0, bell(2637, .7, .18)), (.07, bell(3520, .9, .22)*.8), (0, lp(rng.standard_normal(2400), .6)*env(2400, .0005, .006)*.5)), .55)
# finale chime (major arpeggio)
save("finale", mix(*[(i*.08, bell(f, 1.6, .55)*.7) for i, f in enumerate([1046, 1318, 1568, 2093])]), .65)
print("ok", sorted(os.listdir(OUT)))
