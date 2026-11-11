"""Jump-cut the talking A-roll: keep only the clean takes (source seconds), drop repeats & dead air."""
import subprocess, sys, json
SRC = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/aroll.mp4"
SEG = [  # (in, out, what is said)
    (3.03, 7.60, "kalau korang tengah cari kasut sekolah ... recommend sangat Abaro ni"),
    (9.42, 14.85, "kasut sekolah Abaro ni setiap tahun mesti saya repeat sebab kena air tak tembus"),
    (14.87, 17.27, "lepas tu kalau kotor senang sangat nak cuci"),
    (20.27, 27.12, "lagi-lagi anak kita melasak ... saya lap sahaja"),
    (40.72, 48.66, "yang saya suka kena air tak tembus ... tak basah langsung, senang nak jaga"),
    (49.36, 57.50, "senang nak jaga, tapak anti-slip, lalu lopak tak tergelincir, sangat recommend"),
    (59.40, 65.37, "cantik pun cantik ... harga promo, size masih banyak"),
    (67.47, 73.25, "ibu ayah beli je ... berbaloi, design serius cantik"),
    (76.45, 83.05, "sesuai anak sekolah rendah ... strap ... tak payah susah-susah"),
    (89.93, 93.32, "boleh dapatkan kasut sekolah Abaro dekat beg kuning saya"),
]
F = 0.012
v, a, t = [], [], 0.0
for i, (s, e, _) in enumerate(SEG):
    d = e - s
    v.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30,scale=1080:1920,setsar=1[v{i}]")
    a.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d={F},afade=t=out:st={d-F:.3f}:d={F}[a{i}]")
    t += d
n = len(SEG)
fc = ";".join(v + a) + ";" + "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "30",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", OUT], check=True)
# edit decision list: output start time of every segment
eds, t = [], 0.0
for s, e, txt in SEG: eds.append(dict(out=round(t, 3), src=s, dur=round(e - s, 3), say=txt)); t += e - s
json.dump(eds, open("tools/edl.json", "w"), indent=1)
print("total", round(t, 2))
