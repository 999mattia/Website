---
title: "Useful HUGO Shortcodes"
date: 2026-04-23
author: "Mattia"
summary: "Useful HUGO Shortcodes for running, cycling and 3D-Printing"
---

When trying out HUGO as a possible framework for this website, I did some research into shortcodes that could be useful for the topics I'm passionate about.

# Displaying GPX Tracks

For displaying GPX Tracks I stumbled across the [hugo-gpx-module](https://github.com/ravelzh/hugo-gpx-module) shortcode.\
The creator of this shortcode travels the world with offroad motorcycles and documents the journeys on his [Blog](https://go-offroad.ch/en/).\
Besides displaying GPX Tracks on a Leaflet map, the module also automatically generates a summary, an elevation profile, allows multiple GPX Tracks on a single map instance and is extensively customizable. The shortcode gets installed as a hugo module.

## Example

{{< gpx-map file="gpx/GrossiScheidegg.gpx" >}}

# Displaying 3D Models

I actually didn't find a lightweight shortcode for displaying 3D Models, so I decided to build one myself with a little help from the [Google Model Viewer](https://modelviewer.dev/).

```go
<script
	type="module"
	src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"
></script>

{{ $model := resources.Get (.Get "src") }} {{ if $model }}
<model-viewer
	src="{{ $model.RelPermalink }}"
	alt="3D Modell"
	auto-rotate
	camera-controls
	style="width: 100%; height: 400px; background-color: #ffffff"
>
</model-viewer>
{{ else }}
<p style="color: red">Model not found: {{ .Get "src" }}</p>
{{ end }}
```

The only downside is, that this shortcode only supports .glb files. This is not ideal, as I work with .stl files for 3D-Printing. However, I found a easy-to-use [converter](https://imagetostl.com/convert/file/stl/to/glb).

## Example

{{< 3d-model src="glb/Capybara.glb" >}}
