import json
from playwright.sync_api import sync_playwright
exec(open('/w/route.py').read())
FIND = """(labels) => { const out = {};
  const all = [...document.querySelectorAll('body *')];
  for (const l of labels) {
    const el = all.find(e => e.children.length === 0 && e.textContent.trim().startsWith(l));
    if (!el) { out[l] = null; continue; }
    let b = el; while (b.parentElement && (b.getBoundingClientRect().height < 160 || b.getBoundingClientRect().width < 300)) b = b.parentElement;
    const r = b.getBoundingClientRect(); out[l] = [r.x + scrollX, r.y + scrollY, r.width, r.height, b.className]; }
  return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(service_workers="block", viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    pg = ctx.new_page(); pg.route("**/*", handle)
    boxes = {}
    for tab, rng, labels in [("training", "90D", ["Load ratio", "Training load", "Year to date", "Activity calendar", "Best efforts"]),
                             ("health", "30D", ["Resting heart rate", "Sleep HRV", "Sleep", "Sleep heart rate"]),
                             ("activities", None, ["October 2026"])]:
        pg.goto(f"http://127.0.0.1:8081/#/{tab}"); pg.wait_for_timeout(1500)
        if rng: pg.get_by_text(rng, exact=True).first.click(); pg.wait_for_timeout(1500)
        pg.add_style_tag(content="nav.tabbar, .tabbar, [class*=tabbar] { display: none !important }")
        pg.wait_for_timeout(300)
        pg.screenshot(path=f"/w/f_{tab}.png", full_page=True)
        boxes[tab] = pg.evaluate(FIND, labels)
        boxes[tab]["coach"] = pg.evaluate("() => { const r = document.querySelector('section.coach')?.getBoundingClientRect(); return r && [r.x, r.y + scrollY, r.width, r.height] }")
    json.dump(boxes, open("/w/boxes.json", "w"), indent=1)
    b.close()
