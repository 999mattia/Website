F = {"api/dashboard": "/w/fake_dashboard.json", "api/activities": "/w/fake_activities.json", "api/coach": "/w/fake_coach.json"}
def handle(route):
    u = route.request.url
    for k, f in F.items():
        if u.split("?")[0].endswith(k): return route.fulfill(path=f, content_type="application/json")
    if "/api/" in u or "mapbox" in u: return route.fulfill(status=404, body="{}")
    route.continue_()
