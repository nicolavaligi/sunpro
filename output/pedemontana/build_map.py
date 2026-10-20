#!/usr/bin/env python3
"""Compone la mappa: tracciato, fascia 300 m, seminativi attigui."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, mapping, shape
from shapely.ops import transform, unary_union

RAW = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana/raw")
OUT = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana")
DESKTOP = Path("/Users/houdinick/Desktop/Mappa_Pedemontana_Lombarda.html")
BUFFER_M = 300
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)
TO_WGS = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)


def utm(geom):
    return transform(TO_UTM.transform, geom)


def wgs(geom):
    return transform(TO_WGS.transform, geom)


def lines_from_relation():
    root = ET.parse(RAW / "relation_4543247.osm").getroot()
    nodes = {
        node.get("id"): (float(node.get("lon")), float(node.get("lat")))
        for node in root.findall("node")
    }
    lines = []
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        if tags.get("highway") not in {"motorway", "trunk"}:
            continue
        coords = [nodes[nd.get("ref")] for nd in way.findall("nd") if nd.get("ref") in nodes]
        if len(coords) >= 2:
            lines.append(LineString(coords))
    return lines


def lines_from_cantiere():
    lines = []
    for item in json.loads((RAW / "cantiere_ways.json").read_text()):
        highway = item["tags"].get("highway")
        if highway not in {"construction", "proposed"}:
            continue
        coords = [tuple(point) for point in item["coords"]]
        if len(coords) >= 2:
            lines.append(LineString(coords))
    return lines


def polygons():
    items = []
    for element in json.loads((RAW / "farmland.json").read_text()):
        geom = element.get("geometry") or []
        coords = [(point["lon"], point["lat"]) for point in geom]
        if len(coords) >= 4 and coords[0] == coords[-1]:
            poly = shape({"type": "Polygon", "coordinates": [coords]})
            if poly.is_valid and not poly.is_empty:
                items.append((element["id"], element.get("tags") or {}, poly))
    return items


def feature(geom, props):
    return {"type": "Feature", "properties": props, "geometry": mapping(geom)}


def main():
    open_geom = unary_union(lines_from_relation())
    work_lines = lines_from_cantiere()
    work_geom = unary_union(work_lines) if work_lines else None
    axis = unary_union([open_geom] + ([work_geom] if work_geom is not None else []))
    corridor = wgs(utm(axis).buffer(BUFFER_M))
    fields = []
    for osm_id, tags, geom in polygons():
        piece = geom.intersection(corridor)
        if piece.is_empty:
            continue
        inside = utm(piece).area / 10000
        if inside < 0.5:
            continue
        fields.append(feature(piece, {
            "layer": "seminativo",
            "osm_id": osm_id,
            "landuse": tags.get("landuse", "farmland"),
            "name": tags.get("name", ""),
            "ettari_attigui": round(inside, 2),
            "ettari_appezzamento": round(utm(geom).area / 10000, 2),
        }))
    fields.sort(key=lambda item: -item["properties"]["ettari_attigui"])
    hectares = sum(item["properties"]["ettari_attigui"] for item in fields)
    collection = {
        "type": "FeatureCollection",
        "features": [
            feature(open_geom, {"layer": "esercizio", "nome": "A36 in esercizio"}),
        ]
        + ([feature(work_geom, {"layer": "cantiere", "nome": "Cantiere e tracciato di progetto"})] if work_geom is not None else [])
        + [feature(corridor, {"layer": "corridoio", "nome": "Fascia 300 m"})]
        + fields,
    }
    (OUT / "pedemontana_terreni_attigui.geojson").write_text(json.dumps(collection), encoding="utf-8")
    html_path = OUT / "mappa_pedemontana_lombarda.html"
    html_path.write_text(render(collection, len(fields), hectares), encoding="utf-8")
    DESKTOP.write_text(html_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"esercizio_km {utm(open_geom).length/1000:.1f}")
    if work_geom is not None:
        print(f"cantiere_km {utm(work_geom).length/1000:.1f}")
    print(f"appezzamenti {len(fields)} ha_fascia {hectares:.1f}")
    print(html_path)
    print(DESKTOP)


def render(collection, count, hectares):
    data = json.dumps(collection)
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Pedemontana Lombarda — terreni agricoli attigui</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body, #map {{ margin:0; height:100%; background:#0b1220; }}
  .panel {{
    position:absolute; z-index:500; top:12px; left:12px; width:340px;
    background:rgba(10,16,28,.94); color:#e8eef7; border:1px solid #243044;
    border-radius:12px; padding:12px 14px; font:13px/1.45 -apple-system,sans-serif;
  }}
  .panel h1 {{ font-size:16px; margin:0 0 6px; }}
  .panel p {{ margin:4px 0; color:#b7c3d6; }}
  .swatch {{ display:inline-block; width:12px; height:12px; border-radius:2px; margin-right:6px; vertical-align:-1px; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
  <h1>Pedemontana Lombarda</h1>
  <p>{count} appezzamenti agricoli dentro la fascia di 300 m. {hectares:.0f} ettari complessivi nella fascia.</p>
  <p><span class="swatch" style="background:#1d4ed8"></span>A36 in esercizio, Cassano Magnago–Lentate</p>
  <p><span class="swatch" style="background:#f97316"></span>Cantiere e tracciato di progetto, verso Desio e Vimercate</p>
  <p><span class="swatch" style="background:#38bdf8"></span>Fascia di 300 m dal ciglio del tracciato</p>
  <p><span class="swatch" style="background:#22c55e"></span>Seminativo, prato, frutteto o vigneto attiguo</p>
  <p>Clicca un campo per gli ettari. Fonte: OpenStreetMap. Sono appezzamenti, non particelle catastali e non il tracciato ufficiale APL.</p>
</div>
<script>
const data = {data};
const map = L.map('map');
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
  attribution: 'Esri World Imagery · OpenStreetMap'
}}).addTo(map);
function style(feature) {{
  const layer = feature.properties.layer;
  if (layer === 'esercizio') return {{color:'#1d4ed8', weight:5, opacity:0.95}};
  if (layer === 'cantiere') return {{color:'#f97316', weight:5, opacity:0.95, dashArray:'7 5'}};
  if (layer === 'corridoio') return {{color:'#38bdf8', weight:1.2, fillColor:'#38bdf8', fillOpacity:0.14}};
  const ha = feature.properties.ettari_attigui || 0;
  return {{color:'#14532d', weight:1, fillColor: ha >= 5 ? '#4ade80' : '#22c55e', fillOpacity: ha >= 5 ? 0.62 : 0.4}};
}}
const layer = L.geoJSON(data, {{
  style,
  onEachFeature: (feature, lyr) => {{
    const p = feature.properties;
    if (p.layer !== 'seminativo') return;
    const nome = p.name || 'Seminativo';
    lyr.bindPopup('<b>' + nome + '</b><br>' + p.landuse +
      '<br><b>' + p.ettari_attigui + ' ha</b> nella fascia di 300 m' +
      '<br>Appezzamento intero: ' + p.ettari_appezzamento + ' ha');
  }}
}}).addTo(map);
map.fitBounds(layer.getBounds(), {{padding:[28,28]}});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
