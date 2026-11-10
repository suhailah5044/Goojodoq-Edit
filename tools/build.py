"""Generate project/index.html (HyperFrames composition) from the cue list below."""
import json, html
DUR = 61.6
Y = 204  # default overlay baseline area (empty car-ceiling zone at top)

HOOK = dict(t=0.05, end=2.95, text="Headphone ni memang worth it!", sfx="hook")
# (start, end, text-or-list, sfx, y-override)
CUES = [
    (2.85, 4.35, "TAK SAKIT TELINGA", "ting", None),
    (7.85, 9.45, "EAR CUP LEMBUT", "pop", None),
    (13.96, 16.30, "HEADBAND BOLEH ADJUST", "tick", None),
    (17.52, 19.45, "SOUND CLEAR", "ting2", None),
    (19.66, 21.80, "BASS SEDAP", "bass", None),
    (24.46, 26.45, "NAMPAK PREMIUM", "shimmer", None),
    (28.50, 30.05, "BLUETOOTH • TERUS PAIR", "blip", None),
    (36.98, 38.20, "LUPA DIRI WEH", "whoosh", None),
    (38.80, 39.62, "HARGA MURAH", "cash", None),
    (44.94, 46.40, "RAMAI DAH GRAB", "ting", None),
    (49.16, 52.40, [(49.16, "SELESA"), (50.62, "PADU"), (51.52, "SOUND BEST")], "tick", None),
    (54.24, 56.10, "GOOJODOQ J236", "shimmer", None),
    (56.34, 57.95, "SANGAT RECOMMEND", "ting2", None),
    (59.68, DUR, "HARGA PROMO • GRAB CEPAT", "finale", None),
]
SFX_VOL = {"hook": .55, "ting": .38, "ting2": .38, "pop": .5, "tick": .35, "blip": .42,
           "shimmer": .35, "bass": .6, "cash": .38, "finale": .42, "whoosh": .45}

els, auds, js = [], [], []
import wave as _w
LEN = {}
def sfx(t, name, i):
    if name not in LEN:
        f = _w.open(f"project/assets/sfx/{name}.wav"); LEN[name] = f.getnframes() / f.getframerate()
    auds.append(f'<audio id="sfx{i}" src="assets/sfx/{name}.wav" data-start="{t:.2f}" '
                f'data-duration="{LEN[name]:.2f}" data-volume="{SFX_VOL[name]}" data-track-index="{3 + len(auds) % 2}"></audio>')

# hook
h = HOOK
els.append(f'<div id="hook" class="ov hook clip" data-start="{h["t"]}" data-duration="{h["end"]-h["t"]:.2f}" '
           f'data-track-index="1" style="top:{Y-6}px"><span class="in">{html.escape(h["text"])}</span>'
           f'<i class="rule"></i></div>')
sfx(0.0, h["sfx"], "h")
js.append(f'tl.fromTo("#hook .in",{{opacity:0,y:14,scale:.96}},{{opacity:1,y:0,scale:1,duration:.55,ease:"power3.out"}},{h["t"]+.12});')
js.append(f'tl.fromTo("#hook .rule",{{scaleX:0,opacity:0}},{{scaleX:1,opacity:.9,duration:.6,ease:"power2.out"}},{h["t"]+.35});')
js.append(f'tl.to("#hook",{{opacity:0,y:-8,duration:.3,ease:"power2.in"}},{h["end"]-.3:.2f});')

n = 0
for k, (s, e, txt, snd, yo) in enumerate(CUES):
    y, dx = (yo[0] or Y, yo[1]) if isinstance(yo, tuple) else (yo or Y, 0)
    if isinstance(txt, list):
        parts = "".join(f'<span class="w" id="c{k}w{j}">{html.escape(w)}</span>'
                        + ('<span class="dot" id="c{0}d{1}">·</span>'.format(k, j) if j < len(txt)-1 else "")
                        for j, (_, w) in enumerate(txt))
        els.append(f'<div id="c{k}" class="ov kw clip" data-start="{s}" data-duration="{e-s:.2f}" data-track-index="2" style="top:{y}px;left:{dx}px"><span class="in">{parts}</span></div>')
        for j, (tw, _) in enumerate(txt):
            js.append(f'tl.fromTo("#c{k}w{j}",{{opacity:0,y:10}},{{opacity:1,y:0,duration:.32,ease:"power3.out"}},{tw:.2f});')
            if j: js.append(f'tl.fromTo("#c{k}d{j-1}",{{opacity:0}},{{opacity:.7,duration:.2}},{tw-.05:.2f});')
            sfx(tw, snd, f"{k}_{j}")
    else:
        els.append(f'<div id="c{k}" class="ov kw clip" data-start="{s}" data-duration="{e-s:.2f}" data-track-index="2" style="top:{y}px;left:{dx}px"><span class="in">{html.escape(txt)}</span></div>')
        js.append(f'tl.fromTo("#c{k} .in",{{opacity:0,y:12,scale:.97}},{{opacity:1,y:0,scale:1,duration:.38,ease:"power3.out"}},{s:.2f});')
        sfx(s - (0.04 if snd != "bass" else 0), snd, k)
    js.append(f'tl.to("#c{k} .in",{{opacity:0,y:-6,duration:.25,ease:"power2.in"}},{e-.25:.2f});')

page = f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:"Lexend Mega";font-weight:400;src:url(assets/fonts/lexend-mega-latin-400-normal.woff2) format("woff2")}}
@font-face{{font-family:"Lexend Mega";font-weight:500;src:url(assets/fonts/lexend-mega-latin-500-normal.woff2) format("woff2")}}
@font-face{{font-family:"Inter";font-weight:500;src:url(assets/fonts/inter-latin-500-normal.woff2) format("woff2")}}
@font-face{{font-family:"Inter";font-weight:600;src:url(assets/fonts/inter-latin-600-normal.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
/* soft top shade: only deepens the empty ceiling so white text reads clean; footage colours untouched */
.shade{{position:absolute;left:0;top:0;width:100%;height:470px;pointer-events:none;
  background:linear-gradient(180deg,rgba(0,0,0,.30) 0%,rgba(0,0,0,.16) 45%,rgba(0,0,0,0) 100%)}}
.ov{{position:absolute;left:0;width:100%;text-align:center;color:#fff;pointer-events:none}}
.ov .in{{display:inline-block;text-shadow:0 2px 14px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.35)}}
.hook .in{{font-family:"Inter";font-weight:600;font-size:46px;letter-spacing:-.01em}}
.hook .rule{{display:block;width:120px;height:3px;margin:16px auto 0;background:#fff;border-radius:2px;transform-origin:center;box-shadow:0 1px 8px rgba(0,0,0,.4)}}
.kw .in{{font-family:"Lexend Mega";font-weight:500;font-size:29px;letter-spacing:-.03em}}
.kw .dot{{display:inline-block;margin:0 .45em;opacity:0}}
.kw .w{{display:inline-block}}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
<video id="a-roll" class="clip" src="assets/edited.mp4" playsinline data-start="0" data-duration="{DUR}" data-track-index="0" data-has-audio="true"
  style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></video>
<div class="shade"></div>
{chr(10).join(els)}
{chr(10).join(auds)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
open("project/index.html", "w").write(page)
print("cues", len(CUES), "sfx", len(auds))
