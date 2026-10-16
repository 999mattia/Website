# Renders city frames: python3 city.py <out> <query> <w> <h> <frames> <campath.json|-> [warm]
import json, sys, time, os
from playwright.sync_api import sync_playwright
out, q, w, h, n, cam = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
warm = int(sys.argv[7]) if len(sys.argv) > 7 else 60
os.makedirs(out, exist_ok=True)
path = json.load(open(cam)) if cam != '-' else None   # list of [x,y,z] per frame, or {"from":..,"to":..}
CSS = "#hud,#modes,#quality,#ticker,#tip,#homeBtn,.home{display:none!important}"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": w, "height": h})
    pg.add_init_script(path="/w/fakeclock.js")
    pg.route("**/app.js", lambda r: r.fulfill(path="/w/app.debug.js", content_type="text/javascript"))
    pg.goto("http://127.0.0.1:8197/?" + q)
    pg.wait_for_function("!document.getElementById('loading')", timeout=300000, polling=500)
    pg.add_style_tag(content=CSS)
    def campos(i):
        if not path: return None
        if isinstance(path, dict):
            import math
            k = i / max(1, n - 1); k = k * k * (3 - 2 * k) if path.get("ease", True) else k
            return [a + (b_ - a) * k for a, b_ in zip(path["from"], path["to"])]
        return path[i]
    c0 = campos(0)
    if c0: pg.evaluate("c => window.__camPos = c", c0)
    pg.evaluate("window.__norender = true")
    for i in range(warm): pg.evaluate("__step(33.333)")
    pg.evaluate("window.__norender = false")
    if n == 0:
        print(json.dumps(pg.evaluate("""() => { const c = __city(); return { cam: c.camera.position.toArray(), dir: c.VIEW_DIR.toArray(), center: c.CENTER.toArray(),
          b: c.buildings.map(b => ({ kind: b.kind, role: b.role, name: b.name || b.id || b.title, metric: !!b.metric, a: b.anchor })) } }""")))
    for i in range(n):
        t = time.time()
        c = campos(i)
        if c: pg.evaluate("c => window.__camPos = c", c)
        pg.evaluate("__step(33.333)")
        pg.screenshot(path=f"{out}/{i:04d}.png", timeout=600000)
        print(i, round(time.time() - t, 1), flush=True)
    b.close()
