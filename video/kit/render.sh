#!/bin/bash
# Renders one video and its web versions:  video/kit/render.sh <swt|city|training>
# Needs the brag-tools image (docker build -t brag-tools video/kit). Writes video/<name>/brag.mp4 + brag.jpg
# and media/<name>.mp4, <name>-loop.mp4, <name>.jpg for the site. Frames and audio.wav are temporary.
set -e
N=$1; V=$(cd "$(dirname "$0")/.." && pwd); D=$V/$N; M=$V/../media
[ -f "$D/comp.html" ] || { echo "usage: $0 <swt|city|training>"; exit 1; }
DUR=$(python3 -c "import json;print(json.load(open('$D/audio.json'))['duration'])")
POSTER=$(python3 -c "import json;print(round(json.load(open('$D/audio.json'))['poster']*30))")
RUN="docker run --rm -v $V:/v -v $M:/m brag-tools"
if [ "$N" = city ]; then    # the city's footage is kept as clips; the composition reads it as frames
  $RUN sh -c 'for c in /v/city/clips/*.mp4; do n=$(basename $c .mp4); mkdir -p /v/city/a/f_$n; ffmpeg -y -loglevel error -i $c -q:v 2 -start_number 0 /v/city/a/f_$n/%04d.jpg; done'
fi
$RUN sh -c "rm -rf /v/$N/frames && python3 /v/kit/chill.py /v/$N/audio.json /v/$N/audio.wav && python3 /v/kit/capture.py /v/$N/comp.html /v/$N/frames $DUR"
$RUN sh -c "cd /v/$N && cp frames/$(printf %05d $POSTER).jpg brag.jpg && cp brag.jpg frames/00000.jpg &&
  ffmpeg -y -loglevel error -framerate 30 -i frames/%05d.jpg -i audio.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart brag.mp4 &&
  ffmpeg -y -loglevel error -i brag.mp4 -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart /m/$N.mp4 &&
  ffmpeg -y -loglevel error -i brag.mp4 -an -vf scale=768:432:flags=lanczos -c:v libx264 -preset slow -crf 27 -pix_fmt yuv420p -movflags +faststart /m/$N-loop.mp4 &&
  ffmpeg -y -loglevel error -i brag.jpg -vf scale=768:432:flags=lanczos -q:v 4 /m/$N.jpg &&
  rm -rf frames audio.wav && chown -R $(id -u):$(id -g) /v /m"
echo "done: $D/brag.mp4, media/$N.mp4"
