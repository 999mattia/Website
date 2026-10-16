# Builds app.debug.js from Homelab City's app.js (private repo, so only this patch lives here):
# window.__camPos overrides the camera, window.__norender skips drawing during warm-up steps.
# python3 make_debug.py ~/homelab-city/public/app.js
import sys, os
src = open(sys.argv[1]).read()
a = "    view.update(dt);\n"
b = "    if (post) post.composer.render(dt); else renderer.render(scene, camera);\n  };"
c = "function step(dt, t) {"
for s in (a, b, c): assert src.count(s) == 1, f"app.js changed, update the patch near: {s.strip()}"
src = src.replace(a, a + "    if (window.__camPos) { const c = window.__camPos; camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[0] - VIEW_DIR.x, c[1] - VIEW_DIR.y, c[2] - VIEW_DIR.z); camera.updateMatrixWorld(); aimLights(); placeLabels(); }\n")
src = src.replace(b, "    if (window.__norender) return;\n" + b)
src = src.replace(c, "window.__city = () => ({ VIEW_DIR, camera, buildings, TARGET, CENTER });\n" + c)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.debug.js"), "w").write(src)
print("app.debug.js written")
