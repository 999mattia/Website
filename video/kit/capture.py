# Renders an HTML composition frame by frame: every frame is window.render(t), a pure function of time.
# python3 capture.py comp.html out_dir duration [--stills t1,t2,...] [--from f0 --to f1]
import argparse, os, subprocess
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out"); ap.add_argument("duration", type=float)
ap.add_argument("--fps", type=int, default=30); ap.add_argument("--stills", default="")
ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
    pg = b.new_page(viewport={"width": a.w, "height": a.h}, device_scale_factor=1)
    pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.goto("file://" + os.path.abspath(a.html))
    pg.evaluate("window.ready")          # fonts and every image loaded and decoded
    if a.stills:
        for t in a.stills.split(","):
            pg.evaluate(f"render({float(t)})")
            pg.screenshot(path=f"{a.out}/still_{float(t):06.2f}.png")
    else:
        n = round(a.duration * a.fps)
        for i in range(n):
            pg.evaluate(f"render({i / a.fps})")
            pg.screenshot(path=f"{a.out}/{i:05d}.jpg", type="jpeg", quality=96)
            if i % 60 == 0: print("frame", i, "/", n, flush=True)
    b.close()
