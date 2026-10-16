# Cuts the dashboard's full-page captures (2x) into the cards the video uses. Boxes in 2x pixels; check them
# against boxes.json after a layout change.
from PIL import Image
T = Image.open("/w/f_training.png").convert("RGB"); H = Image.open("/w/f_health.png").convert("RGB")
crops = {"head": (T, (0, 0, 2880, 180)), "coach": (T, (36, 211, 2844, 780)), "gauge": (T, (38, 910, 2842, 1372)),
         "load": (T, (38, 2546, 2842, 3088)), "ytd": (T, (38, 5191, 2842, 5999)), "health": (H, (38, 910, 2842, 1784))}
for k, (im, box) in crops.items(): im.crop(box).save(f"/a/{k}.png")
print("cropped", list(crops))
