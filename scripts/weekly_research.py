"""Weekly OSM screening. Geometry is land cover, never cadastral ownership."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pyproj import Geod
from shapely.geometry import Polygon, Point, mapping, shape

ROOT = Path(__file__).resolve().parents[1]
REGIONS = {'Lombardia':'IT-25','Veneto':'IT-34','Emilia-Romagna':'IT-45',
           'Piemonte':'IT-21','Toscana':'IT-52','Umbria':'IT-55','Marche':'IT-57'}
ENDPOINTS = ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']
DISCLAIMER = ('Screening preliminare OpenStreetMap: poligoni di uso agricolo, non particelle catastali. '
              'Superficie geometrica stimata; nessuna conferma di disponibilità, prezzo, connessione, assenza di edifici o idoneità normativa. '
              'Sono considerate le sole way chiuse landuse=farmland entro circa 300 m da autostrade OSM; '
              'relazioni multipoligono, terreni non mappati e altre tipologie non sono coperti. '
              'Nuovo significa rilevato per la prima volta da questo monitoraggio.')


def query_region(code):
    return f'''[out:json][timeout:150];
area["ISO3166-2"="{code}"]["boundary"="administrative"]->.region;
way(area.region)["highway"="motorway"]->.roads;
way(area.region)(around.roads:300)["landuse"="farmland"];
out meta geom;'''


def fetch_region(code):
    for endpoint in ENDPOINTS:
        try:
            req = Request(endpoint, data=urlencode({'data':query_region(code)}).encode(),
                          headers={'User-Agent':'SunPro-Weekly/1.0 (+https://github.com/nicolavaligi/sunpro)'})
            with urlopen(req, timeout=175) as response:
                data = json.load(response)
            if data.get('remark') or not isinstance(data.get('elements'), list):
                raise ValueError('Risposta incompleta Overpass')
            return data['elements']
        except Exception:
            if endpoint == ENDPOINTS[-1]:
                raise RuntimeError('Overpass non disponibile o risposta incompleta') from None
            time.sleep(3)


def candidate(element, region, timestamp):
    if element.get('type') != 'way' or element.get('tags',{}).get('landuse') != 'farmland':
        return None
    coords = [(p['lon'],p['lat']) for p in element.get('geometry',[]) if 'lon' in p and 'lat' in p]
    if len(coords) < 4 or coords[0] != coords[-1]:
        return None
    if any(not (-180 <= x <= 180 and -90 <= y <= 90) for x,y in coords):
        return None
    polygon = Polygon(coords)
    if not polygon.is_valid or polygon.is_empty:
        return None
    area = abs(Geod(ellps='WGS84').geometry_area_perimeter(polygon)[0])
    if area < 20_000:
        return None
    tags = element.get('tags',{})
    if tags.get('building') not in (None,'no') or tags.get('access') == 'no':
        return None
    point = polygon.representative_point()
    digest = hashlib.sha256(json.dumps({'coordinates':coords,'tags':tags},sort_keys=True).encode()).hexdigest()
    return {'type':'Feature','id':f"osm-way-{element['id']}", 'geometry':mapping(polygon), 'properties':{
        'id':f"osm-way-{element['id']}", 'region':region, 'name':tags.get('name','Area agricola OSM'),
        'area_ha':round(area/10_000,2), 'point':[point.x,point.y], 'status':'DA_VERIFICARE',
        'source_url':f"https://www.openstreetmap.org/way/{element['id']}",
        'source_timestamp':element.get('timestamp'), 'first_seen':timestamp, 'last_seen':timestamp,
        'changed_at':None, 'fingerprint':digest}}


def read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def run(root=ROOT, fetcher=fetch_region, now=None):
    now = now or datetime.now(timezone.utc)
    stamp = now.isoformat()
    week = now.strftime('%G-W%V')
    target = root/'weekly/candidates.geojson'
    previous = read_json(target,{'features':[]})
    old = {f['id']:f for f in previous['features']}
    found, coverage, errors = {}, [], []
    new_ids, changed, retired = [], [], []
    for region, code in REGIONS.items():
        try:
            elements = fetcher(code)
            region_found = {}
            for item in elements:
                feature = candidate(item,region,stamp)
                if not feature:
                    continue
                fid, prop = feature['id'], feature['properties']
                if fid in old:
                    prior = old[fid]['properties']
                    prop['first_seen'] = prior['first_seen']
                    prop['changed_at'] = prior.get('changed_at')
                    if prop['fingerprint'] != prior['fingerprint']:
                        prop['changed_at'] = stamp
                        changed.append(fid)
                else:
                    new_ids.append(fid)
                region_found[fid] = feature
            found.update(region_found)
            coverage.append(region)
        except Exception:
            errors.append(region)
    # On partial outages retain old geometry and its original last_seen date.
    for fid, feature in old.items():
        if feature['properties']['region'] in errors:
            found[fid] = feature
        elif fid not in found:
            retired.append(fid)
    features = sorted(found.values(),key=lambda f:(f['properties']['region'],f['id']))
    report = {'generated_at':stamp,'week':week,'status':'ok' if not errors else 'parziale' if coverage else 'errore',
              'regions_checked':coverage,'regions_failed':errors,'new_ids':sorted(set(new_ids)),
              'changed_ids':sorted(set(changed)),'no_longer_matching_ids':retired,'total_candidates':len(features),
              'disclaimer':DISCLAIMER}
    save(target,{'type':'FeatureCollection','generated_at':stamp,'features':features})
    save(root/'weekly/latest.json',report)
    save(root/f'weekly/history/{week}.json',report)
    lines = [f'# SunPro — Report {week}',f'Aggiornato: {stamp}',f"Esito ricerca: **{report['status']}**",
             f'Nuovi candidati: **{len(new_ids)}** · Modificati: **{len(changed)}** · Non più corrispondenti: **{len(retired)}**',
             f'Candidati totali in mappa: **{len(features)}**',
             'Regioni controllate: '+(', '.join(coverage) or 'nessuna'),
             'Fonti non disponibili: '+(', '.join(errors) or 'nessuna'),
             'I candidati delle regioni non disponibili sono conservati con la data del precedente riscontro.',DISCLAIMER,
             '## Nuove zone interessanti']
    for fid in sorted(set(new_ids)):
        p = found[fid]['properties']
        lines.append(f"- [{p['id']}]({p['source_url']}) · {p['region']} · {p['area_ha']} ha stimati · da verificare")
    if not new_ids:
        lines.append('Nessun nuovo candidato rilevato.' if coverage else 'Ricerca non riuscita: non è possibile stabilire se ci siano novità.')
    for label, ids in [('Candidati modificati', changed), ('Non più corrispondenti ai criteri OSM',retired)]:
        lines.append('## '+label)
        lines.extend('- '+fid for fid in sorted(set(ids)))
        if not ids:
            lines.append('Nessuno.' if coverage else 'Non valutabile.')
    md = '\n\n'.join(lines)+'\n'
    for dest in [root/'weekly/latest.md',root/f'weekly/history/{week}.md']:
        dest.write_text(md)
    report_html = ('<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>SunPro · Report settimanale</title><style>body{max-width:950px;margin:40px auto;padding:20px;'
        'background:#0d1526;color:#eaf0fa;font:16px system-ui}a{color:#38bdf8}pre{white-space:pre-wrap;line-height:1.6}</style>'
        '<a href="../index.html">← Torna alla mappa</a><pre>'+html.escape(md)+'</pre></html>')
    (root/'weekly/report.html').write_text(report_html)
    web = root/'web'
    if web.exists():
        import shutil
        shutil.copytree(root/'weekly',web/'weekly',dirs_exist_ok=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as file:
            file.write(md)
    print(json.dumps({k:v for k,v in report.items() if k != 'disclaimer'},ensure_ascii=False))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture',type=Path,help='Fixture locale: non esegue richieste di rete')
    args = parser.parse_args()
    fixture = read_json(args.fixture,{}) if args.fixture else None
    run(fetcher=(lambda code:fixture.get(code,[])) if fixture is not None else fetch_region)
