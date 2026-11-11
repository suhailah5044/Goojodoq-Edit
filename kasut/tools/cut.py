"""Cut the raw Abaro school-shoe footage into two different edits (A and B).
usage: python3 kasut/tools/cut.py RAW.mov OUT_DIR
Each segment: (audio_in, audio_out, video_in or None, zoom). video_in lets a line play over other
footage (J-cut, e.g. the tap-water demo under "kalau kena air pun tak tembus")."""
import subprocess, sys, os, json
RAW, OUT = sys.argv[1], sys.argv[2]
EDITS = {
  # A — problem/solution, chronological, opens on her pitch
  "A": [
    (3.02, 7.70, None, 1.00),   # kalau korang tengah cari kasut sekolah yang betul-betul tahan lasak...
    (9.40, 14.80, None, 1.10),  # Abaro ni setiap tahun mesti saya repeat sebab kena air tak tembus
    (14.86, 17.22, None, 1.00), # lepas tu kalau kotor senang sangat nak cuci
    (20.42, 24.98, None, 1.08), # lagi-lagi anak kita melasak dekat sekolah...
    (25.00, 27.22, None, 1.00), # bila kotor dia senang, saya lap sahaja
    (40.58, 44.32, 36.55, 1.00),# [tap water b-roll] kena air pun tak tembus, selalu (lalu) sahaja
    (44.50, 47.02, None, 1.08), # nampak tak bahagian dalam tak basah langsung
    (49.48, 52.56, None, 1.00), # senang nak jaga, bahagian belakang anti-slip
    (76.44, 83.02, None, 1.08), # sesuai sekolah rendah, jenis velcro, tak payah susah-susah
    (55.72, 57.66, None, 1.00), # yang ini memang saya sangat-sangat recommend
    (60.26, 65.40, None, 1.08), # boleh tengok dekat beg kuning, harga promo, size banyak lagi
    (67.62, 71.82, None, 1.00), # ibu ayah beli je dekat beg kuning saya, berbaloi
  ],
  # B — cold-open on the waterproof proof shot, design-led, different order and punch-ins
  "B": [
    (44.50, 47.02, None, 1.12), # nampak tak bahagian dalam ni tak basah langsung  (cold open)
    (40.58, 43.00, 36.55, 1.06),# [tap water] yang saya suka kena air pun tak tembus ke dalam
    (9.40, 12.20, None, 1.00),  # Abaro ni setiap tahun mesti saya repeat
    (71.84, 74.40, None, 1.10), # design dia serius memang cantik
    (83.00, 83.88, None, 1.00), # bahagian belakang ni pun
    (85.32, 86.76, None, 1.00), # design dia sangat-sangat cantik
    (49.48, 52.56, None, 1.12), # bahagian belakang pun jenis anti-slip
    (76.44, 83.02, None, 1.00), # sesuai sekolah rendah, velcro
    (18.12, 20.42, None, 1.10), # bila kena kotor senang sangat nak cuci
    (26.12, 27.22, None, 1.00), # saya semua lap sahaja
    (61.40, 63.96, None, 1.08), # sekarang ni tengah bagi harga promo
    (65.70, 67.56, None, 1.00), # sementara size pun masih banyak
    (90.18, 93.34, None, 1.10), # boleh dapatkan kasut sekolah Abaro dekat beg kuning saya
  ],
}
os.makedirs(OUT, exist_ok=True)
for name, segs in EDITS.items():
    parts, t, marks = [], 0.0, []
    for i, (a0, a1, v0, z) in enumerate(segs):
        d = a1 - a0; v0 = a0 if v0 is None else v0
        p = f"{OUT}/{name}_{i:02d}.mkv"
        vf = (f"scale={int(1080*z)//2*2}:{int(1920*z)//2*2},crop=1080:1920:(iw-1080)/2:(ih-1920)/2," if z != 1 else "") + \
             "fps=30,format=yuv420p,setsar=1"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{v0:.3f}", "-t", f"{d:.3f}", "-i", RAW,
                        "-ss", f"{a0:.3f}", "-t", f"{d:.3f}", "-i", RAW, "-map", "0:v", "-map", "1:a",
                        "-vf", vf, "-af", f"afade=t=in:d=0.015,afade=t=out:st={d-0.02:.3f}:d=0.02,aresample=48000",
                        "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-c:a", "pcm_s16le", "-ac", "2", p], check=True)
        parts.append(p); marks.append({"i": i, "src": [a0, a1], "t": round(t, 3)}); t += d
    lst = f"{OUT}/{name}_list.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", f"{OUT}/edited_{name}.mp4"], check=True)
    json.dump({"dur": round(t, 3), "segments": marks}, open(f"{OUT}/edited_{name}.json", "w"), indent=1)
    for p in parts: os.remove(p)
    print(name, round(t, 2), "s", len(segs), "segments")
