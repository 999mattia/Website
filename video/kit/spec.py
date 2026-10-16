import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram
from PIL import Image, ImageDraw
sr, x = wavfile.read(sys.argv[1]); x = x.mean(1) / 32768
f, t, S = spectrogram(x, sr, nperseg=2048, noverlap=1536)
S = 10 * np.log10(S + 1e-12); keep = f < 8000; S = S[keep][::-1]
S = np.clip((S + 110) / 80, 0, 1)
img = Image.fromarray((S * 255).astype(np.uint8)).resize((1400, 300))
rms = [20*np.log10(np.sqrt(np.mean(x[int(i*sr*0.25):int((i+1)*sr*0.25)]**2))+1e-9) for i in range(int(len(x)/sr*4))]
c = Image.new('L', (1400, 420), 0); c.paste(img, (0, 0)); d = ImageDraw.Draw(c)
for i, r in enumerate(rms):
    X = int(i / len(rms) * 1400); d.rectangle([X, 420 - int((r + 60) * 2), X + 1400 // len(rms) - 2, 420], fill=200)
for s in range(int(len(x)/sr)+1): d.line([s*1400*sr/len(x), 300, s*1400*sr/len(x), 310], fill=255)
c.save(sys.argv[2]); print('peak', np.abs(x).max(), 'clipped', int((np.abs(x) > 0.999).sum()))
