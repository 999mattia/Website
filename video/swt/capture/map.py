from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":1600,"height":1000}, device_scale_factor=2)
    pg.goto("https://swt.mattiag.ch/", wait_until="networkidle")
    pg.select_option("select >> nth=0", "en")
    pg.locator("button[aria-label]").nth(1).click(); pg.wait_for_timeout(2500)
    box = pg.locator(".leaflet-container").bounding_box(); print(box)
    # zoom in on Switzerland with the wheel, centred on the cluster
    cx, cy = box["x"] + box["width"]*0.42, box["y"] + box["height"]*0.75
    pg.mouse.move(cx, cy)
    for i in range(2): pg.mouse.wheel(0, -300); pg.wait_for_timeout(900)
    pg.wait_for_timeout(1500)
    # drag the map so Switzerland sits in the middle
    pg.mouse.move(box["x"]+box["width"]/2-110, box["y"]+box["height"]*0.85); pg.mouse.down()
    pg.mouse.move(box["x"]+box["width"]/2, box["y"]+box["height"]*0.5+25, steps=10); pg.mouse.up()
    pg.mouse.move(5, 5); pg.wait_for_timeout(4000)
    pg.locator(".leaflet-container").screenshot(path="/w/map_zoom.png")
    b.close()
