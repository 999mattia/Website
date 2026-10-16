# Project clips

Sources of the three clips on the site's project cards (`media/swt*`, `media/city*`, `media/training*`). Made with
the brag-slim approach: each video is an HTML page whose `render(t)` draws frame `t` (`<name>/comp.html`), captured
frame by frame with Playwright, plus a soundtrack synthesized from a cue sheet (`<name>/audio.json`). Not part of
the site's image (the Dockerfile copies only `index.html`, `njs/`, `media/`).

## Render

```bash
docker build -t brag-tools video/kit        # once: Playwright + ffmpeg + numpy/scipy
video/kit/stills.sh training 1.0,6.0,15.6   # look at a few frames -> video/training/stills/
video/kit/render.sh training                # brag.mp4 + media/training.mp4, -loop.mp4, .jpg
```

Then commit `media/` and push (the site's image builds, Komodo deploys the `website` service).

## What to edit

- **Text, timing, layout:** `<name>/comp.html`. Scenes are time windows in `render(t)`; `kit/kit.js` has the helpers
  (`prog`, easing `E`, `words`, `life`). Keep every frame a pure function of `t`.
- **Music and effects:** `<name>/audio.json` — `bpm`, `root` (MIDI tonic), `prog` (scale degrees of the 7th/9th
  chords), `drop` (where the groove starts), `musicEnd`, `fx` (cues: `whoosh`, `tap`, `tick`, `pop`, `bell`,
  `riser` at a time `t`). Synth: `kit/chill.py` (laid-back e-piano, sub bass, swung drums). `poster` = the second
  used as thumbnail and frame 0. `kit/spec.py wav png` draws a spectrogram to check a mix without listening.
- **Footage / screenshots:** `<name>/a/` (city: `city/clips/*.mp4`, unpacked to `city/a/` by `render.sh`).
  Re-capture with `<name>/capture/` scripts:
  - `swt/capture/capture.sh` — the live public site.
  - `training/capture/capture.sh` — the real dashboard UI with **fictional** health data, names, routes and coach
    text (`sanitize.py`). Never commit `capture/data/`; keep service workers blocked.
  - `city/capture/shots.sh [shot...]` — Homelab City with mock data, camera paths in `city/capture/<shot>.json`,
    ~1.5 h for all five shots. Needs `~/homelab-city` (private), patched by `make_debug.py`.

`<name>/brag-plan.md` has each storyboard, `share-copy.txt` a caption for posting.
