"""Trim/rotate/scale the B-roll into 1080x1920 30fps muted clips. Speed-ramp = fast part + normal part."""
import subprocess, sys, os
DL = sys.argv[1]  # folder holding air.mov and strap.mov
# name: (source, [(in, out, speed), ...])
CLIPS = {
    "hook_side":   ("strap", [(10.10, 12.30, 1.0)]),               # hero side profile (hook)
    "air_ramp":    ("air",   [(23.00, 25.00, 2.0), (25.00, 26.15, 1.0)]),  # water poured on shoe, speed ramp
    "air_wipe":    ("air",   [(30.50, 33.25, 1.0)]),               # hands wiping the wet shoe
    "strap_rear":  ("strap", [(8.00, 9.80, 1.0)]),                 # heel + logo
    "air_logo":    ("air",   [(33.50, 34.95, 1.0)]),               # side panel with logo
    "strap_velcro":("strap", [(3.70, 7.10, 1.0)]),                 # open & close velcro strap
    "end_side":    ("strap", [(10.90, 12.30, 1.0)]),               # end card hero
}
os.makedirs("assets/broll", exist_ok=True)
for name, (src, parts) in CLIPS.items():
    fc, labels = [], ""
    for i, (a, b, sp) in enumerate(parts):
        fc.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps=30,scale=1080:1920:flags=lanczos,setsar=1[p{i}]")
        labels += f"[p{i}]"
    fc.append(f"{labels}concat=n={len(parts)}:v=1:a=0[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{DL}/{src}.mov", "-filter_complex", ";".join(fc),
                    "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-g", "15", f"assets/broll/{name}.mp4"], check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        f"assets/broll/{name}.mp4"], capture_output=True, text=True).stdout.strip()
    print(name, d)
