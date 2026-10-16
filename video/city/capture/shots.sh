#!/bin/bash
# Re-records the city footage (slow: ~10 s per frame in software WebGL, about 1.5 h for all five).
#   video/city/capture/shots.sh [turb open night vps lapse]
# Starts a mock city from ~/homelab-city on :8197, renders each shot frame by frame with a hand-stepped clock,
# and stores it as video/city/clips/<shot>.mp4. Camera paths: <shot>.json ({"from","to"} positions, eased).
set -e
C=$(cd "$(dirname "$0")" && pwd); CITY=${CITY:-$HOME/homelab-city}
python3 $C/make_debug.py $CITY/public/app.js
(cd $CITY && MOCK=1 MOCK_WEATHER=sunny PORT=8197 python3 server.py > /dev/null 2>&1 & echo $! > $C/out.pid) ; mkdir -p $C/out; sleep 2
trap 'kill $(cat $C/out.pid) 2>/dev/null; rm -f $C/out.pid' EXIT
declare -A Q=([turb]="time=11:30&labels=none 75 turb.json 60" [open]="time=18:10&labels=none 105 open.json 60"
  [night]="time=20:40&labels=none 75 night.json 60" [vps]="time=13:00&labels=none 75 vps.json 60" [lapse]="time=16:30&speed=5400&labels=none 90 - 10")
for s in ${@:-turb open night vps lapse}; do
  set -- ${Q[$s]}
  docker run --rm --network host -v $C:/w brag-tools sh -c "python3 /w/city.py /w/out/$s '$1' 1280 720 $2 $( [ $3 = - ] && echo - || echo /w/$3) $4 &&
    ffmpeg -y -loglevel error -framerate 30 -i /w/out/$s/%04d.png -c:v libx264 -preset veryslow -crf 17 -pix_fmt yuv420p /w/../clips/$s.mp4 &&
    rm -rf /w/out/$s && chown -R $(id -u):$(id -g) /w/../clips"
done
