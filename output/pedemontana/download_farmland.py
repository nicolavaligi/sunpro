#!/usr/bin/env python3
"""Campiona seminativi OSM lungo il tracciato già scaricato."""

import json
import math
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = {"User-Agent": "SunPro-research/1.0 (mappa Pedemontana)"}
RAW = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana/raw")


def xy(lon, lat):
    return (lon * 111320 * math.cos(math.radians(lat)), lat * 110540)


def samples(points, step_m=2200):
    kept = []
    for lon, lat in points:
        x, y = xy(lon, lat)
        if all(math.hypot(x - px, y - py) > step_m for px, py, _, _ in kept):
            kept.append((x, y, lon, lat))
    return [(lon, lat) for _, _, lon, lat in kept]


def relation_points():
    root = ET.parse(RAW / "relation_4543247.osm").getroot()
    nodes = {n.get("id"): (float(n.get("lon")), float(n.get("lat"))) for n in root.findall("node")}
    points = []
    for way in root.findall("way"):
        tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
        if tags.get("highway") not in {"motorway", "trunk"}:
            continue
        for nd in way.findall("nd"):
            if nd.get("ref") in nodes:
                points.append(nodes[nd.get("ref")])
    return points


def overpass(lat, lon):
    query = f"""
[out:json][timeout:25];
(
  way["landuse"~"^(farmland|meadow|orchard|vineyard)$"](around:1400,{lat},{lon});
);
out geom;
"""
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter", data=data, headers=UA
    )
    with urllib.request.urlopen(req, timeout=40) as response:
        return json.loads(response.read().decode())


def main():
    points = relation_points()
    for item in json.loads((RAW / "cantiere_ways.json").read_text()):
        highway = item["tags"].get("highway")
        if highway in {"construction", "proposed", "trunk", "motorway"}:
            points.extend(tuple(p) for p in item["coords"])
    centers = samples(points)
    print("centri", len(centers))
    found = {}
    for index, (lon, lat) in enumerate(centers, start=1):
        try:
            payload = overpass(lat, lon)
        except Exception as exc:
            print("skip", index, exc)
            time.sleep(2)
            continue
        for element in payload.get("elements", []):
            found[element["id"]] = element
        print(index, round(lat, 3), round(lon, 3), "tot", len(found))
        time.sleep(1.2)
    (RAW / "farmland.json").write_text(json.dumps(list(found.values())), encoding="utf-8")
    print("salvati", len(found))


if __name__ == "__main__":
    main()
