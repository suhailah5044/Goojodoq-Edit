"""Generate kasut/A/index.html and kasut/B/index.html (HyperFrames compositions) for the
Abaro school-shoe edits. Cue times are written in RAW-footage seconds and mapped onto the
edited timeline through edited_X.json (written by cut.py), so re-cutting never desyncs text.

Text lives only in the empty kitchen-cabinet band at the top of frame (y ~150-480); the shoes
are always mid/low frame, so nothing covers the product.

usage: python3 kasut/tools/build.py   (expects kasut/X/assets/edited_X.{mp4,json} + sfx)"""
import json, html, re, wave

def load(name):
    meta = json.load(open(f"kasut/{name}/assets/edited_{name}.json"))
    return meta

def mapper(meta):
    def at(src, seg=None):
        for s in meta["segments"]:
            a0, a1 = s["src"]
            if (seg is None or s["i"] == seg) and a0 - 1e-6 <= src <= a1 + 1e-6:
                return round(s["t"] + src - a0, 3)
        raise ValueError(f"source time {src} not in edit (seg={seg})")
    return at

def em(txt, cls="em"):
    """*word* -> emphasised span"""
    return re.sub(r"\*(.+?)\*", lambda m: f'<span class="{cls}">{html.escape(m.group(1))}</span>',
                  html.escape(txt).replace("&ast;", "*"))

SFX_LEN = {}
def sfx_len(name):
    if name not in SFX_LEN:
        w = wave.open(f"kasut/shared/sfx/{name}.wav"); SFX_LEN[name] = w.getnframes() / w.getframerate()
    return SFX_LEN[name]

FONTS = """
@font-face{font-family:"Kaushan";src:url(assets/fonts/kaushan-script-latin-400-normal.woff2) format("woff2")}
@font-face{font-family:"Archivo";font-weight:800;font-style:italic;src:url(assets/fonts/archivo-latin-800-italic.woff2) format("woff2")}
@font-face{font-family:"Archivo";font-weight:600;font-style:italic;src:url(assets/fonts/archivo-latin-600-italic.woff2) format("woff2")}
@font-face{font-family:"Archivo";font-weight:700;src:url(assets/fonts/archivo-latin-700-normal.woff2) format("woff2")}
@font-face{font-family:"Inter";font-weight:700;src:url(assets/fonts/inter-latin-700-normal.woff2) format("woff2")}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
.shade{position:absolute;left:0;top:0;width:100%;height:620px;pointer-events:none;
  background:linear-gradient(180deg,rgba(0,0,0,.34) 0%,rgba(0,0,0,.14) 55%,rgba(0,0,0,0) 100%)}
.ov{position:absolute;pointer-events:none;color:#fff}
"""

def page(name, dur, css, els, auds, js):
    return f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>{FONTS}{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
<video id="a-roll" class="clip" src="assets/edited_{name}.mp4" playsinline data-start="0" data-duration="{dur}" data-track-index="0" data-has-audio="true"
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

class Comp:
    def __init__(self, name):
        self.name = name; self.meta = load(name); self.at = mapper(self.meta)
        self.els, self.auds, self.js = [], [], []
    def sfx(self, t, snd, vol):
        i = len(self.auds)
        self.auds.append(f'<audio id="s{i}" src="assets/sfx/{snd}.wav" data-start="{max(0, t):.2f}" '
                         f'data-duration="{sfx_len(snd):.2f}" data-volume="{vol}" data-track-index="{3 + i % 2}"></audio>')
    def write(self, css):
        open(f"kasut/{self.name}/index.html", "w").write(page(self.name, self.meta["dur"], css, self.els, self.auds, self.js))
        print(self.name, "dur", self.meta["dur"], "overlays", len(self.els), "sfx", len(self.auds))

STAR = ('<svg class="st" viewBox="0 0 20 20" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px">'
        '<path d="M10 0 L12 8 L20 10 L12 12 L10 20 L8 12 L0 10 L8 8Z" fill="{c}"/></svg>')

# ───────────────────────────── VIDEO A ─────────────────────────────
# Reference look: brand pill + yellow outlined script title + white bold line; feature callouts
# in bold italic with a yellow keyword, a hand-drawn swoosh under it, and twinkling sparkles.
def build_A():
    c = Comp("A"); at = c.at; D = c.meta["dur"]
    css = """
.hook{left:0;width:100%;top:150px;text-align:center}
.pill{display:inline-block;background:#fff;color:#111;font:700 30px/1 "Archivo";letter-spacing:.14em;
  padding:11px 22px 10px;border-radius:12px;box-shadow:0 4px 14px rgba(0,0,0,.35)}
.script{display:block;margin-top:8px;font:96px/1.05 "Kaushan";color:#FFE11B;
  -webkit-text-stroke:9px #111;paint-order:stroke fill;text-shadow:0 6px 0 #111,0 10px 24px rgba(0,0,0,.45)}
.sub{display:block;margin-top:2px;font:800 italic 46px/1.1 "Archivo";color:#fff;letter-spacing:-.01em;
  -webkit-text-stroke:7px #111;paint-order:stroke fill;text-shadow:0 4px 0 #111}
.ca{left:0;width:100%;text-align:center}
.ca .lead{display:block;font:600 italic 34px/1.15 "Archivo";color:#fff;
  text-shadow:0 2px 10px rgba(0,0,0,.6),0 0 2px rgba(0,0,0,.5)}
.ca .em,.ca .key{font:800 italic 48px/1.15 "Archivo";color:#FFE11B;letter-spacing:-.01em;
  -webkit-text-stroke:6px #111;paint-order:stroke fill;text-shadow:0 3px 0 #111}
.ca .key{display:inline-block}
.ca .sw{display:block;width:300px;height:22px;margin:-4px auto 0;overflow:visible}
.ca .sw path{fill:none;stroke:#FFE11B;stroke-width:6;stroke-linecap:round;filter:drop-shadow(0 2px 3px rgba(0,0,0,.5))}
.st{position:absolute;opacity:0}
.end{left:0;width:100%;top:170px;text-align:center}
.end .script{font-size:84px}
.end .bk{display:inline-block;margin-top:14px;background:#FFE11B;color:#111;font:800 italic 40px/1 "Archivo";
  padding:14px 26px 12px;border-radius:14px;border:4px solid #111;box-shadow:0 6px 0 #111}
"""
    # hook (0 → 3.0s)
    c.els.append('<div id="hook" class="ov hook clip" data-start="0" data-duration="3.10" data-track-index="1">'
                 '<span class="pill">ABARO</span><span class="script">Kasut Sekolah</span>'
                 '<span class="sub">yang betul-betul tahan lasak!</span>'
                 + STAR.format(x=190, y=120, s=34, c="#fff") + STAR.format(x=860, y=200, s=26, c="#FFE11B")
                 + STAR.format(x=150, y=330, s=22, c="#FFE11B") + '</div>')
    c.js += ['tl.fromTo("#hook .pill",{opacity:0,y:-20},{opacity:1,y:0,duration:.35,ease:"back.out(2)"},0.05);',
             'tl.fromTo("#hook .script",{opacity:0,scale:.6,rotation:-6},{opacity:1,scale:1,rotation:-3,duration:.5,ease:"back.out(1.8)"},0.18);',
             'tl.fromTo("#hook .sub",{opacity:0,y:18},{opacity:1,y:0,duration:.4,ease:"power3.out"},0.48);',
             'tl.fromTo("#hook .st",{opacity:0,scale:0},{opacity:1,scale:1,duration:.3,stagger:.12,ease:"back.out(3)"},0.6);',
             'tl.to("#hook .st",{rotation:90,duration:1.6,ease:"none"},0.9);',
             'tl.to("#hook",{opacity:0,y:-14,duration:.28,ease:"power2.in"},2.80);']
    c.sfx(0.0, "hook", .55)

    # (src_start, src_end, seg, lead, key, y, sfx)
    CUES = [
        (11.86, 12.95, 1, "Setiap tahun mesti", "REPEAT!", 230, "pop"),
        (13.10, 14.78, 1, "Kena air", "TAK TEMBUS", 230, "ting"),
        (15.48, 17.20, 2, "Kotor?", "Senang cuci", 230, "pop"),
        (21.40, 24.95, 3, "Anak lasak pun", "TAHAN!", 240, "ting2"),
        (26.20, 27.20, 4, "Lap je,", "terus bersih", 240, "pop"),
        (41.70, 44.30, 5, "Test air depan-depan", "KALIS AIR", 300, "ting"),
        (44.86, 47.00, 6, "Bahagian dalam", "KERING!", 280, "pop"),
        (50.48, 52.54, 7, "Tapak", "ANTI-SLIP", 280, "ting2"),
        (76.90, 78.60, 8, "Sesuai untuk", "sekolah rendah", 280, "pop"),
        (78.64, 83.00, 8, "Jenis velcro,", "pakai sendiri!", 280, "ting"),
        (56.28, 57.64, 9, "Saya", "SANGAT RECOMMEND", 280, "shimmer"),
        (63.16, 64.00, 10, "Sekarang", "HARGA PROMO", 280, "cash"),
        (64.04, 65.38, 10, "Size", "masih banyak!", 280, "pop"),
    ]
    for k, (s0, s1, seg, lead, key, y, snd) in enumerate(CUES):
        t0, t1 = at(s0, seg), at(s1, seg)
        w = 40 + 26 * len(key)
        c.els.append(f'<div id="a{k}" class="ov ca clip" data-start="{t0:.2f}" data-duration="{t1 - t0:.2f}" data-track-index="2" style="top:{y}px">'
                     f'<span class="lead">{html.escape(lead)}</span><span class="key">{html.escape(key)}</span>'
                     f'<svg class="sw" viewBox="0 0 300 22" style="width:{min(w, 520)}px"><path d="M6 15 C 80 4, 200 2, 294 11"/></svg>'
                     + STAR.format(x=540 + min(w, 520) // 2 + 6, y=-6, s=24, c="#fff")
                     + STAR.format(x=540 - min(w, 520) // 2 - 34, y=50, s=18, c="#FFE11B") + '</div>')
        c.js += [f'tl.fromTo("#a{k} .lead",{{opacity:0,y:10}},{{opacity:1,y:0,duration:.28,ease:"power3.out"}},{t0:.2f});',
                 f'tl.fromTo("#a{k} .key",{{opacity:0,scale:.7}},{{opacity:1,scale:1,duration:.34,ease:"back.out(2.2)"}},{t0 + .10:.2f});',
                 f'tl.fromTo("#a{k} .sw path",{{strokeDasharray:320,strokeDashoffset:320}},{{strokeDashoffset:0,duration:.4,ease:"power2.out"}},{t0 + .26:.2f});',
                 f'tl.fromTo("#a{k} .st",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:.25,stagger:.1,ease:"back.out(3)"}},{t0 + .3:.2f});',
                 f'tl.to("#a{k}",{{opacity:0,y:-8,duration:.22,ease:"power2.in"}},{t1 - .22:.2f});']
        c.sfx(t0 + .08, snd, .4 if snd != "cash" else .36)

    # end card over the final pitch (beg kuning → berbaloi)
    t0 = at(67.70, 11); t1 = D
    c.els.append(f'<div id="end" class="ov end clip" data-start="{t0:.2f}" data-duration="{t1 - t0:.2f}" data-track-index="1">'
                 '<span class="script">Sangat berbaloi!</span><span class="bk">Grab di beg kuning</span>'
                 + STAR.format(x=170, y=10, s=30, c="#fff") + STAR.format(x=880, y=60, s=26, c="#FFE11B") + '</div>')
    c.js += [f'tl.fromTo("#end .script",{{opacity:0,scale:.6,rotation:-6}},{{opacity:1,scale:1,rotation:-3,duration:.5,ease:"back.out(1.8)"}},{t0:.2f});',
             f'tl.fromTo("#end .bk",{{opacity:0,y:24}},{{opacity:1,y:0,duration:.4,ease:"back.out(2)"}},{t0 + .35:.2f});',
             f'tl.fromTo("#end .st",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:.3,stagger:.12,ease:"back.out(3)"}},{t0 + .5:.2f});',
             f'tl.to("#end .bk",{{scale:1.06,duration:.35,yoyo:true,repeat:5,ease:"sine.inOut"}},{t0 + 1.0:.2f});']
    c.sfx(t0, "finale", .4)
    c.write(css)

# ───────────────────────────── VIDEO B ─────────────────────────────
# Different hook (cold open on the dry-inside proof shot), different order, and a different
# caption system: left/right-anchored stacks with a yellow highlighter bar behind the keyword.
def build_B():
    c = Comp("B"); at = c.at; D = c.meta["dur"]
    css = """
.hook{left:0;width:100%;top:150px;text-align:center}
.big{display:block;font:800 italic 70px/1 "Archivo";color:#fff;letter-spacing:-.02em;text-transform:uppercase;
  -webkit-text-stroke:9px #111;paint-order:stroke fill;text-shadow:0 6px 0 #111,0 10px 26px rgba(0,0,0,.4)}
.big .w{display:inline-block;margin:0 .12em}
.script{display:block;margin-top:2px;font:84px/1.1 "Kaushan";color:#FFE11B;
  -webkit-text-stroke:9px #111;paint-order:stroke fill;text-shadow:0 6px 0 #111}
.tag{display:inline-block;margin-top:12px;background:#111;color:#fff;font:700 26px/1 "Inter";letter-spacing:.08em;
  padding:10px 18px;border-radius:999px;border:2px solid #FFE11B}
.cb{width:620px}
.cb.L{left:64px;text-align:left}
.cb.R{right:64px;text-align:right}
.cb .lead{display:block;font:600 italic 32px/1.2 "Archivo";color:#fff;
  text-shadow:0 2px 10px rgba(0,0,0,.65),0 0 2px rgba(0,0,0,.5)}
.cb .hl{position:relative;isolation:isolate;z-index:0;display:inline-block;margin-top:6px;padding:6px 16px 4px;
  font:800 italic 42px/1.1 "Archivo";color:#111;text-transform:uppercase;letter-spacing:-.01em}
.cb .hl i{position:absolute;inset:0;background:#FFE11B;border-radius:6px;transform:skewX(-8deg);z-index:-1;
  box-shadow:0 5px 0 #111}
.cb .hl b{position:relative;font:inherit}
.cb .bar{display:inline-block;width:10px;height:10px;border-radius:50%;background:#FF4B3E;margin:0 10px 4px 0;vertical-align:middle}
.cb.R .bar{margin:0 0 4px 10px}
.end{left:0;width:100%;top:160px;text-align:center}
.end .big{font-size:58px}
.end .script{font-size:78px}
.arrow{display:block;margin:6px auto 0;width:60px;height:60px}
"""
    # hook: cold open (0 → 2.5s), words punch in one by one
    words = ["Kena", "air", "pun..."]
    c.els.append('<div id="hook" class="ov hook clip" data-start="0" data-duration="2.52" data-track-index="1">'
                 '<span class="big">' + "".join(f'<span class="w">{w}</span>' for w in words) + '</span>'
                 '<span class="script">tak basah langsung?!</span>'
                 '<span class="tag">KASUT SEKOLAH ABARO</span></div>')
    c.js += ['tl.fromTo("#hook .w",{opacity:0,scale:1.8},{opacity:1,scale:1,duration:.22,stagger:.16,ease:"power4.out"},0.02);',
             'tl.fromTo("#hook .script",{opacity:0,y:20,rotation:-4},{opacity:1,y:0,rotation:-2,duration:.42,ease:"back.out(2)"},0.55);',
             'tl.fromTo("#hook .tag",{opacity:0,scale:.8},{opacity:1,scale:1,duration:.3,ease:"back.out(2)"},0.9);',
             'tl.to("#hook",{opacity:0,y:-14,duration:.26,ease:"power2.in"},2.24);']
    for j in range(3): c.sfx(0.02 + .16 * j, "tick", .45)
    c.sfx(0.5, "whoosh", .5); c.sfx(0.9, "ting2", .38)

    # (src_start, src_end, seg, lead, key, side, y, sfx)
    CUES = [
        (41.46, 42.98, 1, "Saya suka sebab", "air tak tembus", "L", 300, "blip"),
        (10.60, 12.18, 2, "Setiap tahun", "wajib repeat", "R", 250, "pop"),
        (71.86, 74.38, 3, "Design dia", "serius cantik", "L", 260, "blip"),
        (83.00, 86.74, None, "Belakang pun", "stylish", "R", 300, "pop"),
        (50.48, 52.54, 6, "Tapak", "anti-slip", "L", 300, "bass"),
        (76.90, 78.60, 7, "Sesuai untuk", "sekolah rendah", "R", 300, "blip"),
        (79.30, 83.00, 7, "Velcro — pakai sendiri,", "tak payah ikat", "L", 300, "pop"),
        (18.16, 20.40, 8, "Kotor?", "senang cuci", "R", 260, "blip"),
        (26.16, 27.20, 9, "Saya", "lap je!", "L", 260, "pop"),
        (62.46, 63.94, 10, "Sekarang tengah", "harga promo", "R", 280, "cash"),
        (66.24, 67.54, 11, "Cepat, size", "masih banyak", "L", 280, "pop"),
    ]
    for k, (s0, s1, seg, lead, key, side, y, snd) in enumerate(CUES):
        if seg is None:  # spans the two 'belakang' pieces
            t0, t1 = at(s0, 4), at(s1, 5)
        else:
            t0, t1 = at(s0, seg), at(s1, seg)
        bar = '<span class="bar"></span>'
        lead_html = (bar + html.escape(lead)) if side == "L" else (html.escape(lead) + bar)
        c.els.append(f'<div id="b{k}" class="ov cb {side} clip" data-start="{t0:.2f}" data-duration="{t1 - t0:.2f}" data-track-index="2" style="top:{y}px">'
                     f'<span class="lead">{lead_html}</span><span class="hl"><i></i><b>{html.escape(key)}</b></span></div>')
        dx = -40 if side == "L" else 40
        c.js += [f'tl.fromTo("#b{k} .lead",{{opacity:0,x:{dx}}},{{opacity:1,x:0,duration:.3,ease:"power3.out"}},{t0:.2f});',
                 f'tl.fromTo("#b{k} .hl i",{{scaleX:0,transformOrigin:"{"left" if side == "L" else "right"} center"}},{{scaleX:1,duration:.3,ease:"power3.out"}},{t0 + .1:.2f});',
                 f'tl.fromTo("#b{k} .hl b",{{opacity:0,y:8}},{{opacity:1,y:0,duration:.24,ease:"power2.out"}},{t0 + .22:.2f});',
                 f'tl.to("#b{k}",{{opacity:0,x:{-dx // 2},duration:.22,ease:"power2.in"}},{t1 - .22:.2f});']
        c.sfx(t0 + .06, snd, {"bass": .5, "cash": .36}.get(snd, .4))

    # end card on "boleh dapatkan ... dekat beg kuning saya"
    t0 = at(90.22, 12); t1 = D
    c.els.append(f'<div id="end" class="ov end clip" data-start="{t0:.2f}" data-duration="{t1 - t0:.2f}" data-track-index="1">'
                 '<span class="big">Dapatkan sekarang</span><span class="script">di beg kuning!</span>'
                 '<svg class="arrow" viewBox="0 0 60 60"><path d="M30 6 V48 M14 34 L30 50 L46 34" fill="none" stroke="#FFE11B" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 3px 0 #111)"/></svg></div>')
    c.js += [f'tl.fromTo("#end .big",{{opacity:0,scale:1.5}},{{opacity:1,scale:1,duration:.3,ease:"power4.out"}},{t0:.2f});',
             f'tl.fromTo("#end .script",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"back.out(2)"}},{t0 + .3:.2f});',
             f'tl.fromTo("#end .arrow",{{opacity:0,y:-10}},{{opacity:1,y:0,duration:.3}},{t0 + .6:.2f});',
             f'tl.to("#end .arrow",{{y:12,duration:.3,yoyo:true,repeat:6,ease:"sine.inOut"}},{t0 + .9:.2f});']
    c.sfx(t0, "cash", .38); c.sfx(t0 + .3, "finale", .36)
    c.write(css)

build_A(); build_B()
