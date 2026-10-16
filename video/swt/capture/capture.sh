#!/bin/bash
# Re-captures the SwissWaterTemps screenshots from the live site into video/swt/a/ (phone 390x844 @2x, map @2x).
C=$(cd "$(dirname "$0")" && pwd)
docker run --rm --network host -v $C:/c -v $C/../a:/w brag-tools sh -c "python3 /c/cap.py && python3 /c/map.py && chown -R $(id -u):$(id -g) /w"
