import json
import os
from PySide6.QtWebEngineWidgets import QWebEngineView
from utils import extract_gps

# ─── Map HTML ─────────────────────────────────────────────────────────────────

MAP_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body {{ margin: 0; padding: 0; background: {bg}; color: {text}; }}
    #map {{ width: 100%; height: 100vh; }}
    .leaflet-popup-content-wrapper {{
      background: {surface};
      color: {text};
      border: 1px solid {border};
      border-radius: 8px;
      font-family: 'Segoe UI', sans-serif;
      font-size: 12px;
    }}
    .leaflet-popup-tip {{ background: {surface}; }}
  </style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map', {{ zoomControl: true }}).setView([{center_lat}, {center_lon}], {zoom});
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19
  }}).addTo(map);

  var markerIcon = L.icon({{
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }});

  var pins = {pins_json};
  var bounds = [];
  pins.forEach(function(pin) {{
    var marker = L.marker([pin.lat, pin.lon], {{icon: markerIcon}})
      .bindPopup('<b>' + pin.label + '</b><br>' + pin.lat.toFixed(5) + ', ' + pin.lon.toFixed(5))
      .addTo(map);
    bounds.push([pin.lat, pin.lon]);
  }});
  if (bounds.length > 1) {{
    map.fitBounds(bounds, {{ padding: [40, 40], maxZoom: 16 }});
  }} else if (bounds.length === 1) {{
    map.setView(bounds[0], 14);
  }}
</script>
</body>
</html>"""

NO_GPS_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="background:{bg};color:{muted};display:flex;align-items:center;
             justify-content:center;height:100vh;margin:0;
             font-family:'Segoe UI',sans-serif;flex-direction:column;gap:12px;">
  <div style="font-size:48px;">&#128507;</div>
  <div style="font-size:16px;color:{accent};">No GPS data found</div>
  <div style="font-size:13px;">Photos without GPS coordinates won't appear on the map.</div>
</body>
</html>"""

PLACEHOLDER_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="background:{bg};color:{muted};display:flex;align-items:center;
             justify-content:center;height:100vh;margin:0;
             font-family:'Segoe UI',sans-serif;flex-direction:column;gap:12px;">
  <div style="font-size:48px;">&#128205;</div>
  <div style="font-size:16px;color:{accent};">Map will appear here</div>
  <div style="font-size:13px;">Open a folder or file to see photo locations.</div>
</body>
</html>"""

class MapView(QWebEngineView):
    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.palette_dict = palette
        self.data_cache = []
        self._update_display()

    def set_theme(self, palette):
        self.palette_dict = palette
        self._update_display()

    def update_map(self, data_cache):
        self.data_cache = data_cache
        self._update_display()

    def _update_display(self):
        p = self.palette_dict
        pins = []
        seen = set()
        for entry in self.data_cache:
            coords = extract_gps(entry)
            if coords:
                key = (round(coords[0], 5), round(coords[1], 5))
                if key not in seen:
                    seen.add(key)
                    name = os.path.basename(entry.get("SourceFile", "Photo"))
                    pins.append({"lat": coords[0], "lon": coords[1], "label": name})

        if not self.data_cache:
            html = PLACEHOLDER_HTML.format(bg=p['BG'], muted=p['MUTED'], accent=p['ACCENT'])
        elif not pins:
            html = NO_GPS_HTML.format(bg=p['BG'], muted=p['MUTED'], accent=p['ACCENT'])
        else:
            avg_lat = sum(p["lat"] for p in pins) / len(pins)
            avg_lon = sum(p["lon"] for p in pins) / len(pins)
            zoom = 14 if len(pins) == 1 else 6
            html = MAP_HTML_TEMPLATE.format(
                bg=p['BG'], text=p['TEXT'], surface=p['SURFACE'], border=p['BORDER'],
                center_lat=avg_lat, center_lon=avg_lon, zoom=zoom,
                pins_json=json.dumps(pins)
            )
        self.setHtml(html)

    def clear(self):
        self.data_cache = []
        self._update_display()
