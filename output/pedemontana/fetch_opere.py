#!/usr/bin/env python3
"""Scarica i tracciati autostradali OSM di Lombardia e Veneto, Pedemontana inclusa."""

import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = {"User-Agent": "SunPro-research/1.0 (suoli attigui)"}
RAW = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana/raw")
REFS = ["A4", "A1", "A21", "A22", "A7", "A35", "A27", "A31", "A13"]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=50) as response:
        return response.read()


def relation_id_for(ref):
    query = urllib.parse.quote(f"Autostrada {ref}")
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=jsonv2&countrycodes=it&limit=8"
    data = json.loads(get(url))
    time.sleep(1.1)
    for item in data:
        if item.get("osm_type") != "way":
            continue
        raw = get(f"https://api.openstreetmap.org/api/0.6/way/{item['osm_id']}/relations")
        root = ET.fromstring(raw)
        for rel in root.findall("relation"):
            tags = {tag.get("k"): tag.get("v") for tag in rel.findall("tag")}
            if tags.get("route") == "road" and tags.get("ref") == ref:
                return rel.get("id"), tags.get("name", ref)
        time.sleep(0.3)
    return None, None


def lines_of(rel_id):
    raw = get(f"https://api.openstreetmap.org/api/0.6/relation/{rel_id}/full")
    root = ET.fromstring(raw)
    nodes = {
        node.get("id"): (float(node.get("lon")), float(node.get("lat")))
        for node in root.findall("node")
    }
    lines = []
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        if tags.get("highway") not in {"motorway", "trunk"}:
            continue
        if tags.get("ref") and not str(tags.get("ref")).startswith(tuple(REFS + ["A36"])):
            continue
        coords = [list(nodes[nd.get("ref")]) for nd in way.findall("nd") if nd.get("ref") in nodes]
        if len(coords) >= 2:
            lines.append(coords)
    return lines


def local_pedemontana():
    lines = []
    root = ET.parse(RAW / "relation_4543247.osm").getroot()
    nodes = {
        node.get("id"): (float(node.get("lon")), float(node.get("lat")))
        for node in root.findall("node")
    }
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        if tags.get("highway") not in {"motorway", "trunk"}:
            continue
        coords = [list(nodes[nd.get("ref")]) for nd in way.findall("nd") if nd.get("ref") in nodes]
        if len(coords) >= 2:
            lines.append({"opera": "A36 Pedemontana Lombarda", "stato": "esercizio", "coords": coords})
    for item in json.loads((RAW / "cantiere_ways.json").read_text()):
        if item["tags"].get("highway") not in {"construction", "proposed"}:
            continue
        coords = item["coords"]
        if len(coords) >= 2:
            lines.append({"opera": "A36 Pedemontana Lombarda", "stato": "cantiere", "coords": coords})
    return lines


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    works = local_pedemontana()
    print("pedemontana", len(works))
    for ref in REFS:
        try:
            rel_id, name = relation_id_for(ref)
        except Exception as exc:
            print("lookup fail", ref, exc)
            continue
        if not rel_id:
            print("no relation", ref)
            continue
        try:
            lines = lines_of(rel_id)
        except Exception as exc:
            print("full fail", ref, exc)
            continue
        for coords in lines:
            works.append({"opera": f"{ref} {name or ''}".strip(), "stato": "esercizio", "coords": coords})
        print(ref, "relation", rel_id, "segments", len(lines))
        time.sleep(0.4)
    (RAW / "opere_lines.json").write_text(json.dumps(works), encoding="utf-8")
    print("saved", len(works))


if __name__ == "__main__":
    main()
