from playwright.sync_api import sync_playwright
W="/w/"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, color_scheme="light")
    pg.goto("https://swt.mattiag.ch/", wait_until="networkidle")
    pg.select_option("select >> nth=0", "en"); pg.wait_for_timeout(800)
    pg.screenshot(path=W+"p_list.png")
    q="bielersee"
    for i in range(1,len(q)+1):
        pg.fill("input", q[:i]); pg.wait_for_timeout(250)
        pg.screenshot(path=W+f"p_type{i:02d}.png")
    print(pg.inner_text("main")[:600] if pg.locator("main").count() else "")
    pg.locator("a[aria-label^='Details']").first.click(); pg.wait_for_timeout(2000)
    pg.screenshot(path=W+"p_station.png"); pg.screenshot(path=W+"p_station_full.png", full_page=True)
    print(pg.url)
    pg.go_back(); pg.wait_for_timeout(800)
    pg.fill("input",""); pg.wait_for_timeout(300)
    pg.select_option("select >> nth=1", index=1); pg.wait_for_timeout(600)
    pg.screenshot(path=W+"p_warm.png")
    pg.locator("button[aria-label]").nth(1).click(); pg.wait_for_timeout(3500)
    pg.screenshot(path=W+"p_map.png")
    pg2 = b.new_page(viewport={"width":1920,"height":1080}, device_scale_factor=1)
    pg2.goto("https://swt.mattiag.ch/", wait_until="networkidle")
    pg2.select_option("select >> nth=0", "en")
    pg2.locator("button[aria-label]").nth(1).click(); pg2.wait_for_timeout(4000)
    pg2.screenshot(path=W+"d_map.png")
    b.close()
