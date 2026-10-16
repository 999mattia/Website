#!/bin/bash
# Re-captures the training dashboard's cards into video/training/a/ with FICTIONAL health data.
# Reads the real API on the server (127.0.0.1:8081) into data/ (gitignored, never commit it), sanitize.py replaces
# health series, names, routes, serials and the coach note, then the real UI is screenshotted with the fake JSON.
# Service workers MUST stay blocked (cap.py does it): the dashboard's worker otherwise loads the real data.
set -e
C=$(cd "$(dirname "$0")" && pwd); mkdir -p $C/data
for e in dashboard coach activities; do curl -fsS http://127.0.0.1:8081/api/$e -o $C/data/$( [ $e = dashboard ] && echo real || echo $e).json; done
(cd $C/data && python3 ../sanitize.py)
cp $C/route.py $C/cap.py $C/data/
docker run --rm --network host -v $C/data:/w -v $C/../a:/a -v $C:/c brag-tools sh -c "python3 /w/cap.py && python3 /c/crop.py && chown -R $(id -u):$(id -g) /a /w"
