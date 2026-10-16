#!/bin/bash
# Quick check before a full render: video/kit/stills.sh <name> 1.0,5.5,12  ->  video/<name>/stills/still_*.png
N=$1; V=$(cd "$(dirname "$0")/.." && pwd)
[ "$N" = city ] && [ ! -d $V/city/a ] && echo "run render.sh city once first (it unpacks the clips)" && exit 1
docker run --rm -v $V:/v brag-tools sh -c "python3 /v/kit/capture.py /v/$N/comp.html /v/$N/stills 0 --stills $2 && chown -R $(id -u):$(id -g) /v/$N/stills"
