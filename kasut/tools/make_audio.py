"""Synthesise SFX (assets/sfx/*.wav) and a soft-beat music bed with speech ducking (assets/music.wav)."""
import numpy as np, wave, os, subprocess
SR = 48000
rng = np.random.default_rng(11)
os.makedirs("assets/sfx", exist_ok=True)
t_ = lambda d: np.arange(int(SR * d)) / SR

def env(n, a=0.003, dec=0.25):
    t = np.arange(n) / SR; e = np.exp(-t / dec); k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k); return e
def lp(x, a):
    y = np.zeros_like(x); p = 0.
    for i, v in enumerate(x): p += a * (v - p); y[i] = p
    return y
def bell(f, d=1.0, dec=.3, parts=((1, 1), (2.76, .35), (5.4, .12))):
    t = t_(d); return sum(g*np.sin(2*np.pi*f*m*t)*np.exp(-t/(dec/(1+m*.4))) for m, g in parts) * env(len(t), .002, 10)
def mix(*parts):
    n = max(len(p) + int(o*SR) for o, p in parts); y = np.zeros(n)
    for o, p in parts: k = int(o*SR); y[k:k+len(p)] += p
    return y
def save(name, x, peak=.8, path=None):
    x = x / (np.abs(x).max() + 1e-9) * peak; f = int(.004*SR); x[-f:] *= np.linspace(1, 0, f)
    with wave.open(path or f"assets/sfx/{name}.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes())

# whoosh (hook / transitions)
d = .5; t = t_(d); n = rng.standard_normal(len(t)); sw = np.sin(np.pi*t/d)**2
whoosh = (lp(n, .03)*.6 + lp(n, .15)*sw*.5) * sw
save("whoosh", whoosh, .6)
# whip: shorter, brighter
d = .28; t = t_(d); n = rng.standard_normal(len(t)); sw = np.sin(np.pi*t/d)**3
save("whip", (lp(n, .25) - lp(n, .03)) * sw, .6)
# soft impact / bass hit
t = t_(.6); f = 95*np.exp(-t*8) + 42
impact = np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(t), .002, .18) + lp(rng.standard_normal(len(t)), .08)*env(len(t), .001, .03)*.5
save("impact", impact, .9)
# hook = whoosh into impact
save("hook", mix((0, whoosh*.8), (.16, impact)), .85)
# ding (USP keyword)
save("ding", mix((0, bell(2093, 1.0, .3)), (.0, bell(3136, .8, .18)*.3)), .6)
# click (button / velcro press)
t = t_(.06); save("click", (np.sin(2*np.pi*2600*t)*.5 + lp(rng.standard_normal(len(t)), .6)*.6)*env(len(t), .0004, .007), .6)
# velcro rip
d = .38; t = t_(d); n = rng.standard_normal(len(t)); am = (np.sin(2*np.pi*55*t) > .2).astype(float)*.8 + .2
save("velcro", (n - lp(n, .2)) * am * env(len(t), .01, .2), .45)
# cash (harga promo)
save("cash", mix((0, bell(2637, .7, .18)), (.07, bell(3520, .9, .22)*.8)), .55)
# pop (CTA)
t = t_(.13); f = 900*np.exp(-t*28) + 280
save("pop", np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(t), .001, .04), .75)

# ---------------- music bed: soft lo-fi beat, 92 bpm ----------------
DUR = float(os.environ.get("DUR", "55.6")); BPM = 92; beat = 60/BPM
N = int(DUR*SR); m = np.zeros(N)
def add(at, sig, g=1.):
    k = int(at*SR)
    if k >= N: return
    e = min(N, k+len(sig)); m[k:e] += sig[:e-k]*g
kt = t_(.35); kick = np.sin(2*np.pi*np.cumsum(60*np.exp(-kt*18)+48)/SR)*env(len(kt), .002, .12)
hat = (lambda x: x - lp(x, .3))(rng.standard_normal(int(.06*SR)))*env(int(.06*SR), .0005, .015)
st = t_(.25); snare = (lp(rng.standard_normal(len(st)), .35)*.7 + np.sin(2*np.pi*190*st)*.3)*env(len(st), .001, .06)
def keys(fs, d):  # soft electric-piano chord
    t = t_(d); s = sum(np.sin(2*np.pi*f*t)*(1 + .25*np.sin(2*np.pi*f*2*t)) for f in fs)
    return s*env(len(t), .015, .9)*np.minimum(1, (d - t)/.3)
CH = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 349.2]]
bass = lambda f, d: np.sin(2*np.pi*f*t_(d))*env(int(d*SR), .01, .5)
nb = int(DUR/beat) + 1
for b in range(nb):
    at = b*beat
    if b % 4 in (0, 2) or b % 8 == 7: add(at + (beat/2 if b % 8 == 7 else 0), kick, .9)
    if b % 4 in (1, 3): add(at, snare, .35)
    add(at + beat/2, hat, .22); add(at, hat, .12)
    if b % 4 == 0:
        c = CH[(b//4) % 4]; add(at, keys(c, 4*beat), .16); add(at, bass(c[0]/2, 4*beat), .35)
m = lp(m, .5)
# fade in/out
fi, fo = int(.4*SR), int(1.5*SR); m[:fi] *= np.linspace(0, 1, fi); m[-fo:] *= np.linspace(1, 0, fo)
m = m / np.abs(m).max()
# ducking: follow the speech envelope of the cut A-roll
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "assets/aroll.mp4", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True).stdout
sp = np.frombuffer(raw, np.int16).astype(float)/32768
sp = np.pad(sp, (0, max(0, N-len(sp))))[:N]
win = int(.05*SR); rms = np.sqrt(np.convolve(sp**2, np.ones(win)/win, "same"))
talk = (20*np.log10(rms+1e-9) > -38).astype(float)
# hold + smooth (attack ~60 ms, release ~350 ms)
g = np.zeros(N); cur = 0.
att, rel = 1/(.06*SR), 1/(.35*SR)
for i in range(0, N, 48):
    tgt = talk[i]; cur += (tgt-cur)*(att*48 if tgt > cur else rel*48); g[i:i+48] = cur
gain = 10**((-24 - 9*g)/20)   # -24 dBFS bed, -33 under speech
save("music", m*gain, peak=float(np.abs(m*gain).max()), path="assets/music.wav")
print("ok")
