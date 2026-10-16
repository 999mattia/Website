FROM mcr.microsoft.com/playwright/python:v1.55.0-noble
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-inter && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir --break-system-packages playwright==1.55.0 numpy pillow scipy
