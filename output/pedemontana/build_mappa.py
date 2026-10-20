#!/usr/bin/env python3
"""Mappa terreni agricoli attigui al tracciato Pedemontana Lombarda (A36 + cantieri)."""

import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, MultiLineString, mapping, shape
from shapely.ops import transform, unary_union

UA = {"User-Agent": "SunPro-research/1.0 (mappa Pedemontana, uso interno)"}
OUT = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana")
BUFFER_M = 300
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)
TO_WGS = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# Tracciato in esercizio, da relation OSM A36.
RELATION_ID = 4543247
# Semi di cantiere / tracciato di progetto a est di Lentate.
SEED_WAYS = [1002142971, 173165468, 1002142979, 1531638135, 1531638136, 932835860]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def parse_osm(raw):
    root = ET.fromstring(raw)
    nodes = {}
    for node in root.findall("node"):
        nodes[node.get("id")] = (float(node.get("lon")), float(node.get("lat")))
    ways = {}
    for way in root.findall("way"):
        tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
        coords = []
        for nd in way.findall("nd"):
            point = nodes.get(nd.get("ref"))
            if point:
                coords.append(point)
        ways[way.get("id")] = {"tags": tags, "coords": coords}
    return ways


def way_line(item):
    coords = item["coords"]
    if len(coords) < 2:
        return None
    line = LineString(coords)
    return None if line.is_empty else line


def fetch_relation_ways():
    raw = get(f"https://api.openstreetmap.org/api/0.6/relation/{RELATION_ID}/full")
    ways = parse_osm(raw)
    open_lines = []
    for item in ways.values():
        highway = item["tags"].get("highway")
        if highway not in {"motorway", "trunk"}:
            continue
        line = way_line(item)
        if line is not None:
            open_lines.append(line)
    return open_lines


def follows_opera(tags):
    name = (tags.get("name") or "") + " " + (tags.get("ref") or "")
    highway = tags.get("highway") or ""
    if "Pedemontana" in name or "A36" in name:
        return highway in {"motorway", "trunk", "construction", "proposed", "motorway_link"}
    return highway in {"construction", "proposed"} and "motorway" in (tags.get("construction") or tags.get("proposed") or "")


def fetch_cantiere_ways():
    seen = {}
    queue = list(SEED_WAYS)
    while queue and len(seen) < 80:
        way_id = str(queue.pop(0))
        if way_id in seen:
            continue
        raw = get(f"https://api.openstreetmap.org/api/0.6/way/{way_id}/full")
        ways = parse_osm(raw)
        item = ways.get(way_id)
        if not item:
            continue
        seen[way_id] = item
        if len(item["coords"]) < 2:
            continue
        for node_id in (None,):
            pass
        # Rileggi gli id nodo dagli estremi interrogando i ways del nodo.
        root = ET.fromstring(raw)
        nds = [nd.get("ref") for nd in root.find("way").findall("nd")]
        for node_id in (nds[0], nds[-1]):
            time.sleep(0.2)
            around = get(f"https://api.openstreetmap.org/api/0.6/node/{node_id}/ways")
            around_root = ET.fromstring(around)
            for way in around_root.findall("way"):
                tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
                wid = way.get("id")
                if wid not in seen and follows_opera(tags):
                    queue.append(wid)
        time.sleep(0.15)
    lines = []
    for item in seen.values():
        if item["tags"].get("highway") in {"construction", "proposed", "trunk"}:
            line = way_line(item)
            if line is not None and line.length > 0:
                lines.append(line)
    return lines


def utm(geom):
    return transform(TO_UTM.transform, geom)


def wgs(geom):
    return transform(TO_WGS.transform, geom)


def overpass(query):
    servers = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    last = None
    for server in servers:
        try:
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(server, data=data, headers=UA)
            with urllib.request.urlopen(req, timeout=50) as response:
                return json.loads(response.read().decode())
        except Exception as exc:
            last = exc
            time.sleep(1)
    raise RuntimeError(last)


def farmland_along(line_wgs):
    """Scarica i poligoni agricoli OSM in finestre lungo il tracciato."""
    length_m = utm(line_wgs).length
    step = 3500
    collected = {}
    distance = 0
    utm_line = utm(line_wgs)
    while distance < length_m:
        point = wgs(utm_line.interpolate(min(distance, length_m)))
        lon, lat = point.x, point.y
        query = f"""
[out:json][timeout:40];
(
  way["landuse"~"farmland|meadow|orchard|vineyard"](around:700,{lat},{lon});
  relation["landuse"~"farmland|meadow|orchard|vineyard"](around:700,{lat},{lon});
);
out geom;
"""
        try:
            payload = overpass(query)
        except Exception as exc:
            print("overpass skip", round(lat, 3), round(lon, 3), exc)
            distance += step
            continue
        for element in payload.get("elements", []):
            collected[element["id"]] = element
        print("finestra", round(lat, 3), round(lon, 3), "tot", len(collected))
        distance += step
        time.sleep(1)
    polygons = []
    for element in collected.values():
        geom = element_polygon(element)
        if geom is not None and geom.is_valid and not geom.is_empty:
            polygons.append((element["id"], element.get("tags", {}), geom))
    return polygons


def element_polygon(element):
    if element.get("type") == "way" and element.get("geometry"):
        coords = [(p["lon"], p["lat"]) for p in element["geometry"]]
        if len(coords) >= 4 and coords[0] == coords[-1]:
            return shape({"type": "Polygon", "coordinates": [coords]})
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("tracciato in esercizio")
    open_lines = fetch_relation_ways()
    print("  segmenti", len(open_lines))
    print("cantiere")
    work_lines = fetch_cantiere_ways()
    print("  segmenti", len(work_lines))

    open_geom = unary_union(open_lines)
    work_geom = unary_union(work_lines) if work_lines else None
    parts = [open_geom] + ([work_geom] if work_geom is not None else [])
    axis = unary_union(parts)
    corridor = wgs(utm(axis).buffer(BUFFER_M))
    print("km esercizio", round(utm(open_geom).length / 1000, 1))
    if work_geom is not None:
        print("km cantiere/progetto", round(utm(work_geom).length / 1000, 1))

    samples = axis if isinstance(axis, LineString) else MultiLineString(
        [g for g in getattr(axis, "geoms", [axis]) if g.geom_type == "LineString"]
    )
    # Una linea di campionamento: il pezzo più lungo più i cantieri.
    pieces = [g for g in (samples.geoms if isinstance(samples, MultiLineString) else [samples])]
    pieces = sorted(pieces, key=lambda g: utm(g).length, reverse=True)
    farmland = []
    seen_ids = set()
    for piece in pieces[:6]:
        if utm(piece).length < 400:
            continue
        for osm_id, tags, geom in farmland_along(piece):
            if osm_id in seen_ids:
                continue
            seen_ids.add(osm_id)
            farmland.append((osm_id, tags, geom))
    print("poligoni agricoli OSM", len(farmland))

    features = []
    total_touch_ha = 0.0
    for osm_id, tags, geom in farmland:
        piece = geom.intersection(corridor)
        if piece.is_empty:
            continue
        inside_ha = utm(piece).area / 10000
        full_ha = utm(geom).area / 10000
        if inside_ha < 0.4:
            continue
        total_touch_ha += inside_ha
        features.append({
            "type": "Feature",
            "properties": {
                "osm_id": osm_id,
                "landuse": tags.get("landuse", "farmland"),
                "name": tags.get("name", ""),
                "ettari_attigui": round(inside_ha, 2),
                "ettari_appezzamento": round(full_ha, 2),
            },
            "geometry": mapping(piece),
        })
    features.sort(key=lambda f: -f["properties"]["ettari_attigui"])
    print("attigui", len(features), "ha dentro 300m", round(total_touch_ha, 1))

    def dump(name, geom, props):
        return {
            "type": "Feature",
            "properties": props,
            "geometry": mapping(geom),
        }

    collection = {
        "type": "FeatureCollection",
        "features": [
            dump("esercizio", open_geom, {"layer": "esercizio", "nome": "A36 in esercizio"}),
        ]
        + ([dump("cantiere", work_geom, {"layer": "cantiere", "nome": "Cantiere e tracciato di progetto"})] if work_geom is not None else [])
        + [dump("corridoio", corridor, {"layer": "corridoio", "nome": "Fascia 300 m"})]
        + features,
    }
    geojson_path = OUT / "pedemontana_terreni_attigui.geojson"
    geojson_path.write_text(json.dumps(collection), encoding="utf-8")
    write_html(OUT / "mappa_pedemontana_lombarda.html", collection, len(features), total_touch_ha)
    desktop = Path("/Users/houdinick/Desktop/Mappa_Pedemontana_Lombarda.html")
    desktop.write_text((OUT / "mappa_pedemontana_lombarda.html").read_text(encoding="utf-8"), encoding="utf-8")
    print(geojson_path)
    print(desktop)


def write_html(path, collection, n_fields, hectares):
    data = json.dumps(collection)
    html = f"""<!DOCTYPE html>
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
    position:absolute; z-index:500; top:12px; left:12px; width:320px;
    background:rgba(10,16,28,.92); color:#e8eef7; border:1px solid #243044;
    border-radius:12px; padding:12px 14px; font:13px/1.4 -apple-system,sans-serif;
  }}
  .panel h1 {{ font-size:15px; margin:0 0 4px; }}
  .panel p {{ margin:4px 0; color:#b7c3d6; }}
  .swatch {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
  <h1>Pedemontana Lombarda</h1>
  <p>Terreni agricoli OSM che toccano la fascia di 300 m dal tracciato. {n_fields} appezzamenti, {hectares:.0f} ha dentro la fascia.</p>
  <p><span class="swatch" style="background:#1d4ed8"></span>A36 in esercizio</p>
  <p><span class="swatch" style="background:#f97316"></span>Cantiere e tracciato di progetto</p>
  <p><span class="swatch" style="background:#38bdf8"></span>Fascia 300 m</p>
  <p><span class="swatch" style="background:#22c55e"></span>Seminativo attiguo</p>
  <p>Fonte tracciato e suoli: OpenStreetMap. Non è il particellare catastale né il tracciato ufficiale APL.</p>
</div>
<script>
const data = {data};
const map = L.map('map', {{zoomControl:true}});
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
  attribution: 'Esri, OSM'
}}).addTo(map);
function style(feature) {{
  const layer = feature.properties.layer;
  if (layer === 'esercizio') return {{color:'#1d4ed8', weight:5, opacity:0.95}};
  if (layer === 'cantiere') return {{color:'#f97316', weight:5, opacity:0.95, dashArray:'6 4'}};
  if (layer === 'corridoio') return {{color:'#38bdf8', weight:1, fillColor:'#38bdf8', fillOpacity:0.12}};
  return {{color:'#166534', weight:1, fillColor:'#22c55e', fillOpacity:0.45}};
}}
const layer = L.geoJSON(data, {{
  style: style,
  onEachFeature: (feature, lyr) => {{
    const p = feature.properties;
    if (!p.ettari_attigui) return;
    lyr.bindPopup('<b>' + (p.name || 'Seminativo') + '</b><br>' + p.landuse +
      '<br>' + p.ettari_attigui + ' ha nella fascia di 300 m<br>Appezzamento OSM ' + p.ettari_appezzamento + ' ha');
  }}
}}).addTo(map);
map.fitBounds(layer.getBounds(), {{padding:[24,24]}});
</script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
