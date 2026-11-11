"""Generate index.html (HyperFrames composition) for the Abaro school-shoe edit."""
import html, wave
DUR = 55.6
AROLL_END = 54.34

# ---- B-roll inserts (full-screen "overlay besar"): id, file, start, dur, entry transition
BROLL = [
    ("b_hook",   "hook_side",    0.00, 2.20, None),
    ("b_air",    "air_ramp",     7.85, 2.15, "whip"),
    ("b_wipe",   "air_wipe",    16.50, 2.75, None),
    ("b_rear",   "strap_rear",  32.60, 1.80, None),
    ("b_logo",   "air_logo",    42.90, 1.43, None),
    ("b_velcro", "strap_velcro",46.40, 3.20, "whip"),
    ("b_end",    "end_side",    54.20, 1.40, None),
]
# ---- A-roll zoom moves: (kind, t0, t1, peak scale, origin)
#  slow  = slow push across the shot; punch = demo punch-in, hold, smooth zoom-out; usp = small accent punch
AZOOM = [
    ("usp",   3.55, 4.55, 1.08, "50% 55%"),
    ("slow",  4.57, 7.85, 1.10, "55% 60%"),
    ("usp",  10.80, 12.40, 1.08, "50% 55%"),
    ("slow", 19.25, 22.90, 1.06, "62% 72%"),
    ("punch",23.05, 25.60, 1.20, "60% 62%"),   # "nampak tak bahagian dalam ni"
    ("punch",29.05, 30.29, 1.20, "52% 46%"),   # soles: anti-slip
    ("usp",  31.50, 32.60, 1.08, "50% 55%"),
    ("usp",  36.30, 38.57, 1.08, "50% 55%"),
    ("slow", 38.57, 42.90, 1.10, "55% 60%"),
    ("usp",  44.35, 46.40, 1.08, "50% 55%"),
    ("slow", 49.60, 54.34, 1.07, "55% 60%"),
]
# B-roll slow zoom (close-up product: 100 -> 110 across the shot)
BZOOM = {"b_air": (1.0, 1.08), "b_wipe": (1.0, 1.10), "b_rear": (1.0, 1.10), "b_logo": (1.02, 1.10),
         "b_velcro": (1.0, 1.06), "b_end": (1.0, 1.08)}

HOOK_WORDS = [("Kasut", .12), ("sekolah", .27), ("waterproof!", .45)]
HOOK_END = 2.95
# ---- keyword overlays: (start, end, text, sfx)
KW = [
    (3.55, 4.95, "Kasut sekolah ABARO", "ding"),
    (7.95, 9.95, "Kena air? Tak tembus!", "ding"),
    (10.80, 12.30, "Kotor? Senang cuci", "ding"),
    (18.25, 19.20, "Lap je, bersih!", "ding"),
    (20.10, 22.20, "Air tak masuk ke dalam", "ding"),
    (24.30, 26.40, "Dalam tak basah langsung", "ding"),
    (29.40, 30.29, "Tapak anti-slip", "ding"),
    (31.50, 32.55, "Sangat recommend", "ding"),
    (32.75, 34.35, "Cantik & kemas", "ding"),
    (36.30, 37.20, "Harga promo", "cash"),
    (37.25, 38.50, "Size masih banyak", "ding"),
    (42.25, 44.30, "Berbaloi + design cantik", "ding"),
    (44.40, 46.30, "Sesuai sekolah rendah", "ding"),
    (47.15, 49.55, "Strap velcro • senang pakai", None),
]
CTA_T = 51.25
# extra SFX: (t, name, vol)
EXTRA = [
    (2.08, "whoosh", .40),                       # zoom transition hook -> A-roll
    (7.80, "whip", .45), (46.35, "whip", .45),   # whip transitions into B-roll
    (23.05, "impact", .45), (29.05, "impact", .45),   # demo punch-ins
    (46.95, "velcro", .45), (48.55, "click", .55),    # strap opened / pressed shut
    (CTA_T, "pop", .55),
]
# --- the anti-slip / puddle sentence (+2.73 s) was restored after timing: shift everything after 30.3 s
SH, AT = 2.73, 30.30
sh = lambda t: t + SH if t >= AT else t
DUR, AROLL_END, CTA_T = sh(DUR), sh(AROLL_END), sh(CTA_T)
BROLL = [(a, f, sh(s), d, tr) for a, f, s, d, tr in BROLL]
AZOOM = [(k, sh(a), sh(b), sc, o) for k, a, b, sc, o in AZOOM]
KW = [(sh(a), sh(b), t, x) for a, b, t, x in KW] + [(32.00, 33.55, "Lalu lopak pun tak licin", "ding")]
EXTRA = [(sh(t), n, v) for t, n, v in EXTRA]
VOL = {"ding": .32, "cash": .36, "hook": .60}

els, auds, js = [], [], []
LEN = {}
def sfx(t, name, vol, i):
    if name not in LEN:
        w = wave.open(f"assets/sfx/{name}.wav"); LEN[name] = w.getnframes()/w.getframerate()
    auds.append(f'<audio id="s{i}" src="assets/sfx/{name}.wav" data-start="{max(0,t):.2f}" data-duration="{LEN[name]:.2f}" '
                f'data-volume="{vol}" data-track-index="{20 + len(auds) % 3}"></audio>')

# A-roll
els.append(f'<video id="aroll" class="clip vid" src="assets/aroll.mp4" playsinline data-start="0" data-duration="{AROLL_END}" '
           f'data-track-index="0" data-has-audio="true"></video>')
for k, (kind, t0, t1, s, org) in enumerate(AZOOM):
    js.append(f'tl.set("#aroll",{{transformOrigin:"{org}"}},{t0:.2f});')
    if kind == "slow":
        js.append(f'tl.fromTo("#aroll",{{scale:1}},{{scale:{s},duration:{t1-t0:.2f},ease:"sine.inOut",immediateRender:false}},{t0:.2f});')
    elif kind == "usp":
        js.append(f'tl.fromTo("#aroll",{{scale:1}},{{scale:{s},duration:.28,ease:"power2.inOut",immediateRender:false}},{t0:.2f});')
        js.append(f'tl.to("#aroll",{{scale:1,duration:.45,ease:"power2.inOut"}},{t1-.45:.2f});')
    else:  # punch: in, hold, smooth out
        js.append(f'tl.fromTo("#aroll",{{scale:1}},{{scale:{s},duration:.32,ease:"power3.inOut",immediateRender:false}},{t0:.2f});')
        js.append(f'tl.to("#aroll",{{scale:1,duration:.5,ease:"power2.inOut"}},{t1-.5:.2f});')
    js.append(f'tl.set("#aroll",{{scale:1}},{t1:.2f});')

# B-roll
for i, (bid, f, s, d, tr) in enumerate(BROLL):
    els.append(f'<video id="{bid}" class="clip vid" src="assets/broll/{f}.mp4" muted playsinline data-start="{s:.2f}" '
               f'data-duration="{d:.2f}" data-track-index="{1 + i % 2}"></video>')
    if bid in BZOOM:
        a, b = BZOOM[bid]
        js.append(f'tl.fromTo("#{bid}",{{scale:{a}}},{{scale:{b},duration:{d:.2f},ease:"none"}},{s:.2f});')
    if tr == "whip":
        js.append(f'tl.fromTo("#{bid}",{{xPercent:70,filter:"blur(22px)"}},{{xPercent:0,filter:"blur(0px)",duration:.24,ease:"power3.out"}},{s:.2f});')
        js.append(f'tl.fromTo("#aroll",{{xPercent:0,filter:"blur(0px)"}},{{xPercent:-30,filter:"blur(14px)",duration:.24,ease:"power3.in",immediateRender:false}},{s-.02:.2f});')
        js.append(f'tl.set("#aroll",{{xPercent:0,filter:"blur(0px)"}},{s+d:.2f});')

# Hook: punch-in 100 -> 115 in 0.3 s, then gentle drift; light sweep once; zoom transition out
js.append('tl.fromTo("#b_hook",{scale:1},{scale:1.15,duration:.3,ease:"power2.out"},0);')
js.append('tl.to("#b_hook",{scale:1.19,duration:1.75,ease:"none"},.3);')
js.append('tl.to("#b_hook",{scale:1.4,filter:"blur(10px)",duration:.15,ease:"power2.in"},2.05);')
js.append('tl.fromTo("#aroll",{scale:1.3,filter:"blur(10px)"},{scale:1,filter:"blur(0px)",duration:.28,ease:"power2.out"},2.2);')
js.append('tl.set("#aroll",{filter:"none"},2.5);')
els.append('<div id="sweep" class="clip" data-start="0.35" data-duration="1.2" data-track-index="5"><i></i></div>')
js.append('tl.fromTo("#sweep i",{xPercent:-160},{xPercent:260,duration:1.05,ease:"power1.inOut"},.4);')

# Hook text: word pop
words = "".join(f'<span class="w" id="hw{j}">{html.escape(w)}</span>' for j, (w, _) in enumerate(HOOK_WORDS))
els.append(f'<div id="hook" class="ov clip" data-start="0.05" data-duration="{HOOK_END-.05:.2f}" data-track-index="6"><i class="glow"></i><span class="hookpill">{words.strip()}</span></div>')
js.append('tl.fromTo("#hook .glow",{opacity:0,scaleX:.6},{opacity:1,scaleX:1,duration:.4,ease:"power2.out"},.05);')
for j, (_, tw) in enumerate(HOOK_WORDS):
    js.append(f'tl.fromTo("#hw{j}",{{opacity:0,scale:.55,y:10}},{{opacity:1,scale:1,y:0,duration:.26,ease:"back.out(2.2)"}},{tw:.2f});')
js.append(f'tl.to("#hook",{{opacity:0,y:-10,duration:.25,ease:"power2.in"}},{HOOK_END-.25:.2f});')
sfx(0, "hook", VOL["hook"], "h")

# Keyword overlays: slide-up halus
for k, (s, e, txt, snd) in enumerate(KW):
    els.append(f'<div id="k{k}" class="ov clip" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="7"><span class="pill kw">{html.escape(txt)}</span></div>')
    js.append(f'tl.fromTo("#k{k} .pill",{{opacity:0,y:26}},{{opacity:1,y:0,duration:.32,ease:"power3.out"}},{s:.2f});')
    js.append(f'tl.to("#k{k} .pill",{{opacity:0,y:-12,duration:.22,ease:"power2.in"}},{e-.22:.2f});')
    if snd: sfx(s - .03, snd, VOL[snd], f"k{k}")

# CTA
els.append(f'<div id="cta" class="ov clip" data-start="{CTA_T:.2f}" data-duration="{DUR-CTA_T:.2f}" data-track-index="8">'
           '<span class="pill cta">Link kat bawah!</span>'
           '<svg id="arrow" width="48" height="48" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')
js.append(f'tl.fromTo("#cta .pill",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2.4)"}},{CTA_T:.2f});')
js.append(f'tl.fromTo("#arrow",{{opacity:0,y:-10}},{{opacity:1,y:0,duration:.3,ease:"power2.out"}},{CTA_T+.25:.2f});')
for r in range(5):
    js.append(f'tl.to("#arrow",{{y:12,duration:.3,ease:"sine.inOut",yoyo:true,repeat:1}},{CTA_T+.6+r*.7:.2f});')

for i, (t, n, v) in enumerate(EXTRA): sfx(t, n, v, f"x{i}")
auds.append(f'<audio id="music" src="assets/music.wav" data-start="0" data-duration="{DUR}" data-volume="1" data-track-index="19"></audio>')

page = f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:"Lexend Mega";font-weight:500;src:url(assets/fonts/lexend-mega-latin-500-normal.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden}}
.vid{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 55%}}
#sweep{{position:absolute;inset:0;overflow:hidden;pointer-events:none;mix-blend-mode:screen}}
#sweep i{{position:absolute;top:-10%;left:0;width:34%;height:120%;transform:rotate(18deg);
  background:linear-gradient(90deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.22) 45%,rgba(255,255,255,.38) 50%,rgba(255,255,255,.22) 55%,rgba(255,255,255,0) 100%)}}
.ov{{position:absolute;left:0;top:250px;width:100%;text-align:center;color:#fff;pointer-events:none}}
.pill{{display:inline-block;font-family:"Lexend Mega";font-weight:500;color:#fff;background:rgba(10,10,12,.46);
  border-radius:22px;text-shadow:0 2px 10px rgba(0,0,0,.35);box-shadow:0 6px 24px rgba(0,0,0,.18)}}
.hookpill{{position:relative;display:inline-block;font-family:"Lexend Mega";font-weight:500;font-size:40px;letter-spacing:-.04em;text-shadow:0 3px 14px rgba(0,0,0,.55),0 0 3px rgba(0,0,0,.4)}}
#hook .glow{{position:absolute;left:50%;top:50%;width:860px;height:190px;margin:-95px 0 0 -430px;border-radius:50%;background:radial-gradient(ellipse at center,rgba(0,0,0,.55) 0%,rgba(0,0,0,.32) 45%,rgba(0,0,0,0) 72%)}}
.hookpill .w{{display:inline-block;margin:0 .13em}}
.kw{{font-size:27px;letter-spacing:-.035em;padding:13px 24px;border-radius:16px}}
.cta{{font-size:34px;letter-spacing:-.035em;padding:16px 30px;border-radius:18px}}
#arrow{{display:block;margin:10px auto 0;filter:drop-shadow(0 2px 8px rgba(0,0,0,.5))}}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
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
open("index.html", "w").write(page)
print("broll", len(BROLL), "kw", len(KW), "sfx", len(auds) - 1)
