#!/usr/bin/env python3
"""Terreni agricoli attigui alle opere in Lombardia e Veneto.

Stessa logica dello script richiesto (filtro classi agricole, buffer, spatial join),
con due correzioni necessarie:
- il buffer è in metri, dopo la proiezione in UTM 32N. Dieci metri sull'asse
  restano sulla piattaforma stradale, quindi la fascia è 300 m, come nel crawler.
- Lombardia: DUSAF 2015 (codici 2*, seminativi, vigneti, frutteti, prati).
- Veneto: uso del suolo OpenStreetMap, perché il portale regionale non pubblica
  un poligonale agricolo interrogabile.
"""

import hashlib
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, box, mapping, shape
from shapely.ops import transform, unary_union

UA = {"User-Agent": "SunPro-research/1.0 (suoli attigui)"}
RAW = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana/raw")
OUT_GEOJSON = Path("/Users/houdinick/solar-land-acquisition-crawler/terreni_attigui_lombardia_veneto.geojson")
BUFFER_M = 300
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)
TO_WGS = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)
LOMB = box(8.40, 44.55, 10.62, 46.68)
VEN = box(10.62, 44.78, 13.10, 46.72)
RELATIONS = {
    "136434": "A4 Serenissima",
    "3306416": "A35 BreBeMi",
    "960769": "A22 Brennero",
    "93329": "A1 del Sole",
    "1206982": "A31 Valdastico",
    "1283714": "A13 Bologna-Padova",
    "2431238": "A27 d'Alemagna",
}


def utm(geom):
    return transform(TO_UTM.transform, geom)


def wgs(geom):
    return transform(TO_WGS.transform, geom)


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def relation_lines(path, opera):
    root = ET.parse(path).getroot()
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
            lines.append((opera, "esercizio", LineString(coords)))
    return lines


def pedemontana_lines():
    lines = relation_lines(RAW / "relation_4543247.osm", "A36 Pedemontana")
    for item in json.loads((RAW / "cantiere_ways.json").read_text()):
        if item["tags"].get("highway") not in {"construction", "proposed"}:
            continue
        coords = [tuple(point) for point in item["coords"]]
        if len(coords) >= 2:
            lines.append(("A36 Pedemontana", "cantiere", LineString(coords)))
    return lines


def pieces_in(line, region):
    cut = line.intersection(region)
    if cut.is_empty:
        return []
    if cut.geom_type == "LineString":
        return [cut]
    if cut.geom_type == "MultiLineString":
        return list(cut.geoms)
    return [g for g in getattr(cut, "geoms", []) if g.geom_type == "LineString"]


def samples(lines, step_m=4500):
    points = []
    for opera, stato, line in lines:
        length = utm(line).length
        if length < 200:
            continue
        metric = utm(line)
        distance = 0.0
        while distance <= length:
            point = wgs(metric.interpolate(min(distance, length)))
            points.append((opera, stato, point.y, point.x))
            distance += step_m
    return points


def dusaf_cell(lat, lon):
    params = {
        "where": "CODICE LIKE '2%'",
        "geometry": f"{lon-0.03},{lat-0.025},{lon+0.03},{lat+0.025}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "CODICE,DES_COMPLETA",
        "returnGeometry": "true",
        "outSR": "4326",
        "resultRecordCount": "200",
        "f": "geojson",
    }
    url = (
        "https://www.cartografia.servizirl.it/arcgis2/rest/services/"
        "BaseMap/DUSAF2015/MapServer/0/query?" + urllib.parse.urlencode(params)
    )
    payload = json.loads(get(url, timeout=35))
    return payload.get("features") or []


def osm_cell(lat, lon):
    query = (
        f'[out:json][timeout:25];'
        f'way["landuse"~"^(farmland|meadow|orchard|vineyard)$"](around:1600,{lat},{lon});'
        f"out geom;"
    )
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=35) as response:
        payload = json.loads(response.read().decode())
    features = []
    for element in payload.get("elements") or []:
        coords = [(p["lon"], p["lat"]) for p in element.get("geometry") or []]
        if len(coords) >= 4 and coords[0] == coords[-1]:
            features.append({
                "properties": {
                    "CODICE": element.get("tags", {}).get("landuse", "farmland"),
                    "DES_COMPLETA": element.get("tags", {}).get("name") or element.get("tags", {}).get("landuse"),
                },
                "geometry": {"type": "Polygon", "coordinates": [coords]},
                "_id": f"osm-{element['id']}",
            })
    return features


def feature_id(feature):
    if feature.get("_id"):
        return feature["_id"]
    props = feature.get("properties") or {}
    geom = json.dumps(feature.get("geometry"), sort_keys=True)[:240]
    return hashlib.sha1(f"{props.get('CODICE')}|{geom}".encode()).hexdigest()


def main():
    catalog = []
    for rel_id, opera in RELATIONS.items():
        catalog.extend(relation_lines(RAW / f"rel_{rel_id}.osm", opera))
    catalog.extend(pedemontana_lines())
    regional = []
    for opera, stato, line in catalog:
        for piece in pieces_in(line, LOMB):
            regional.append((opera, stato, "Lombardia", piece))
        for piece in pieces_in(line, VEN):
            regional.append((opera, stato, "Veneto", piece))
    print("tratti regionali", len(regional))

    by_opera = {}
    for opera, stato, region, line in regional:
        by_opera.setdefault(opera, []).append(line)
    opera_geom = {name: unary_union(lines) for name, lines in by_opera.items()}
    corridor = wgs(utm(unary_union(list(opera_geom.values()))).buffer(BUFFER_M))

    raw_centers = []
    for opera, stato, region, line in regional:
        for _, _, lat, lon in samples([(opera, stato, line)]):
            raw_centers.append((region, lat, lon))
    centers = []
    for region, lat, lon in raw_centers:
        point = utm(shape({"type": "Point", "coordinates": [lon, lat]}))
        if all(point.distance(utm(shape({"type": "Point", "coordinates": [x, y]}))) > 3500 for _, y, x in centers):
            centers.append((region, lat, lon))
    print("centri", len(centers), "grezzi", len(raw_centers))

    collected = {}
    for index, (region, lat, lon) in enumerate(centers, start=1):
        try:
            if region == "Lombardia":
                batch = dusaf_cell(lat, lon)
                fonte = "DUSAF 2015"
            else:
                batch = osm_cell(lat, lon)
                fonte = "OpenStreetMap"
                time.sleep(1.0)
        except Exception as exc:
            print("skip", index, region, round(lat, 3), round(lon, 3), type(exc).__name__)
            continue
        for feature in batch:
            feature["_fonte"] = fonte
            feature["_regione"] = region
            collected[feature_id(feature)] = feature
        if index % 10 == 0:
            print("query", index, "/", len(centers), "poligoni", len(collected))

    fields = []
    for feature in collected.values():
        try:
            geom = shape(feature["geometry"])
        except Exception:
            continue
        if geom.is_empty or not geom.is_valid:
            geom = geom.buffer(0)
        piece = geom.intersection(corridor)
        if piece.is_empty:
            continue
        inside_ha = utm(piece).area / 10000
        if inside_ha < 1:
            continue
        props = feature.get("properties") or {}
        code = str(props.get("CODICE") or "")
        label = str(props.get("DES_COMPLETA") or code)
        centroid = piece.centroid
        nearest = min(opera_geom, key=lambda name: utm(opera_geom[name]).distance(utm(centroid)))
        fields.append({
            "type": "Feature",
            "properties": {
                "layer": "seminativo",
                "regione": feature["_regione"],
                "fonte": feature["_fonte"],
                "codice": code,
                "classe": label,
                "ettari_fascia": round(inside_ha, 2),
                "opera": nearest,
            },
            "geometry": mapping(piece.simplify(0.00015, preserve_topology=True)),
        })
    fields.sort(key=lambda item: -item["properties"]["ettari_fascia"])
    fields = fields[:700]
    hectares = sum(item["properties"]["ettari_fascia"] for item in fields)

    axis_features = []
    for name, geom in opera_geom.items():
        axis_features.append({
            "type": "Feature",
            "properties": {"layer": "opera", "opera": name},
            "geometry": mapping(geom.simplify(0.0002, preserve_topology=True)),
        })
    collection = {"type": "FeatureCollection", "features": axis_features + fields}
    OUT_GEOJSON.write_text(json.dumps(collection), encoding="utf-8")
    web = Path("/Users/houdinick/solar-land-acquisition-crawler/web") / OUT_GEOJSON.name
    web.write_text(OUT_GEOJSON.read_text(encoding="utf-8"), encoding="utf-8")
    by_region = {}
    for item in fields:
        by_region[item["properties"]["regione"]] = by_region.get(item["properties"]["regione"], 0) + 1
    print("campi", len(fields), "ha", round(hectares, 1), by_region)
    print(OUT_GEOJSON, OUT_GEOJSON.stat().st_size)


if __name__ == "__main__":
    main()
