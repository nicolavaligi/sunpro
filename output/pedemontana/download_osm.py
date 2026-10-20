#!/usr/bin/env python3
"""Scarica tracciato A36 e cantieri Pedemontana. Solo rete, niente geometria."""

import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = {"User-Agent": "SunPro-research/1.0 (mappa Pedemontana)"}
OUT = Path("/Users/houdinick/solar-land-acquisition-crawler/output/pedemontana/raw")
SEED_WAYS = [1002142971, 173165468, 1002142979, 1531638135, 1531638136, 932835860]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read()


def way_record(raw, way_id):
    root = ET.fromstring(raw)
    nodes = {
        node.get("id"): [float(node.get("lon")), float(node.get("lat"))]
        for node in root.findall("node")
    }
    way = root.find("way")
    tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
    coords = [nodes[nd.get("ref")] for nd in way.findall("nd") if nd.get("ref") in nodes]
    ends = [nd.get("ref") for nd in way.findall("nd")]
    return {"id": way_id, "tags": tags, "coords": coords, "ends": [ends[0], ends[-1]] if ends else []}


def follows(tags):
    name = f"{tags.get('name', '')} {tags.get('ref', '')}"
    highway = tags.get("highway") or ""
    if "Pedemontana" in name or "A36" in name:
        return highway in {"motorway", "trunk", "construction", "proposed", "motorway_link"}
    return highway in {"construction", "proposed"} and "motorway" in (
        tags.get("construction") or tags.get("proposed") or ""
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rel = get("https://api.openstreetmap.org/api/0.6/relation/4543247/full")
    (OUT / "relation_4543247.osm").write_bytes(rel)
    print("relation", len(rel))

    seen = {}
    queue = [str(item) for item in SEED_WAYS]
    while queue and len(seen) < 60:
        way_id = queue.pop(0)
        if way_id in seen:
            continue
        raw = get(f"https://api.openstreetmap.org/api/0.6/way/{way_id}/full")
        record = way_record(raw, way_id)
        seen[way_id] = record
        print("way", way_id, record["tags"].get("highway"), record["tags"].get("name", "")[:40], len(record["coords"]))
        for node_id in record["ends"]:
            time.sleep(0.25)
            around = ET.fromstring(get(f"https://api.openstreetmap.org/api/0.6/node/{node_id}/ways"))
            for way in around.findall("way"):
                tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
                wid = way.get("id")
                if wid not in seen and follows(tags):
                    queue.append(wid)
        time.sleep(0.2)
    (OUT / "cantiere_ways.json").write_text(json.dumps(list(seen.values())), encoding="utf-8")
    print("cantiere ways", len(seen))


if __name__ == "__main__":
    main()
