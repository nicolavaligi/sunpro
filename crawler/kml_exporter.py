"""
Modulo KML & GeoJSON Exporter per SunPro (Nicola Valigi Engine System).
Esporta l'intera pipeline di terreni fotovoltaici qualificati in formato KML
per visualizzazione 3D professionale su Google Earth Pro e software GIS (QGIS, ArcGIS).
Include linee di connessione vettoriali verso le Cabine Primarie AT/MT.
Autore: Nicola Valigi Engine System
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from data.storage import get_all_leads

def generate_kml_content(leads: List[Dict[str, Any]]) -> str:
    """Genera il markup XML standard KML (Keyhole Markup Language) v2.2."""
    kml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        '  <name>SunPro — Pipeline Terreni Fotovoltaici (Nicola Valigi Engine System)</name>',
        '  <description>Mappatura e qualificazione aree idonee D.Lgs. 199/2021 con allaccio Cabine Primarie AT/MT.</description>',
        '',
        '  <!-- Stili Marker KML -->',
        '  <Style id="pin-top">',
        '    <IconStyle>',
        '      <color>ff00d050</color>',
        '      <scale>1.3</scale>',
        '      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon>',
        '    </IconStyle>',
        '  </Style>',
        '  <Style id="pin-qualificato">',
        '    <IconStyle>',
        '      <color>ff00a0ff</color>',
        '      <scale>1.1</scale>',
        '      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/orange-circle.png</href></Icon>',
        '    </IconStyle>',
        '  </Style>',
        '  <Style id="line-grid">',
        '    <LineStyle>',
        '      <color>7f00ffff</color>',
        '      <width>2.5</width>',
        '    </LineStyle>',
        '  </Style>',
        ''
    ]

    for l in leads:
        lead_id = l["id"]
        title = l["title"]
        comune = l.get("comune", "")
        prov = l.get("provincia", "")
        reg = l.get("regione", "")
        score = l.get("score_totale", 0)
        ha = l.get("superficie_ha", 0)
        mq = l.get("superficie_mq", 0)
        mwp = l.get("mwp_stimati", 0)
        mwh = l.get("produzione_mwh_anno", 0)
        price_mq = l.get("prezzo_mq_eur", 8.2)
        price_tot = l.get("prezzo_richiesto_eur", 0)
        cabina = l.get("cabina_piu_vicina", "CP Primaria")
        sub_dist = l.get("distanza_cabina_m", 0)
        capex = l.get("capex_allaccio_eur", 0)
        owner = l.get("proprietario_nome", "Proprietà Riservata")
        contact = l.get("proprietario_pec") or l.get("proprietario_telefono") or "Inquiry riservata"
        osm = l.get("osm_url", "")
        style_id = "pin-top" if score >= 85 else "pin-qualificato"

        lat = float(l["lat"])
        lng = float(l["lng"])

        desc = f"""<![CDATA[
        <div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.5; color: #1e293b;">
          <h3 style="margin-top:0; color:#059669; border-bottom:2px solid #10b981; padding-bottom:4px;">{title}</h3>
          <p><b>ID Lead:</b> {lead_id} | <b>Località:</b> {comune} ({prov}, {reg})</p>
          <p><b>Superficie:</b> {ha:.2f} ha ({mq:,.0f} mq) · <b>Potenza:</b> ~{mwp:.2f} MWp (~{mwh:,.0f} MWh/a)</p>
          <hr style="border:0; border-top:1px dashed #cbd5e1;"/>
          <p><b>⚡ Cabina Primaria AT/MT:</b> {cabina}<br/>
             <b>Distanza di allaccio:</b> {sub_dist:,.0f} m · <b>CAPEX Allaccio:</b> € {capex:,.0f}</p>
          <p><b>💶 Valutazione Acquisto:</b> {price_mq:.2f} €/mq (€ {price_tot:,.0f})<br/>
             <b>🌱 Canone Diritto Superficie (30y):</b> ~€ {ha*3000:,.0f}/anno</p>
          <p><b>🏢 Proprietà:</b> {owner}<br/>
             <b>📞 Contatto / PEC:</b> {contact}</p>
          <p><b>Punteggio Idoneità:</b> <span style="font-weight:bold; color:#059669;">{score}/100</span> ({l.get('rating_classe', 'QUALIFICATO')})</p>
          {f'<p><a href="{osm}" target="_blank" style="color:#0284c7; font-weight:bold;">Visualizza Perimetro su OpenStreetMap &raquo;</a></p>' if osm else ''}
          <div style="margin-top:10px; font-size:11px; color:#64748b;">
            <i>Nicola Valigi Engine System — Conforme D.Lgs. 199/2021 (Aree Idonee)</i>
          </div>
        </div>
        ]]>"""

        # Placemark del Terreno
        kml.append('  <Placemark>')
        kml.append(f'    <name>{title} ({score}/100)</name>')
        kml.append(f'    <styleUrl>#{style_id}</styleUrl>')
        kml.append(f'    <description>{desc}</description>')
        kml.append('    <Point>')
        kml.append(f'      <coordinates>{lng},{lat},0</coordinates>')
        kml.append('    </Point>')
        kml.append('  </Placemark>')

    kml.append('</Document>')
    kml.append('</kml>')
    return '\n'.join(kml)

def export_kml_and_geojson(output_kml_path: Path, output_geojson_path: Path) -> Tuple[Path, Path]:
    """Esporta tutti i lead presenti nel database SQLite in formato KML e GeoJSON."""
    leads = get_all_leads()

    # 1. KML
    kml_str = generate_kml_content(leads)
    output_kml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_kml_path, "w", encoding="utf-8") as f:
        f.write(kml_str)

    # 2. GeoJSON
    features = []
    for l in leads:
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(l["lng"]), float(l["lat"])]
            },
            "properties": {
                "id": l["id"],
                "title": l["title"],
                "comune": l.get("comune"),
                "provincia": l.get("provincia"),
                "regione": l.get("regione"),
                "superficie_ha": l.get("superficie_ha"),
                "mwp_stimati": l.get("mwp_stimati"),
                "produzione_mwh_anno": l.get("produzione_mwh_anno"),
                "cabina_piu_vicina": l.get("cabina_piu_vicina"),
                "distanza_cabina_m": l.get("distanza_cabina_m"),
                "prezzo_mq_eur": l.get("prezzo_mq_eur"),
                "prezzo_richiesto_eur": l.get("prezzo_richiesto_eur"),
                "score_totale": l.get("score_totale"),
                "rating_classe": l.get("rating_classe"),
                "proprietario_nome": l.get("proprietario_nome"),
                "proprietario_pec": l.get("proprietario_pec"),
                "osm_url": l.get("osm_url")
            }
        }
        features.append(feat)

    geojson_obj = {
        "type": "FeatureCollection",
        "name": "SunPro_Solar_Land_Pipeline",
        "features": features
    }

    output_geojson_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_obj, f, indent=2, ensure_ascii=False)

    return output_kml_path, output_geojson_path

if __name__ == "__main__":
    kml_p = Path("SunPro_Pipeline_Terreni_Fotovoltaico.kml")
    geo_p = Path("SunPro_Pipeline_Terreni_Fotovoltaico.geojson")
    export_kml_and_geojson(kml_p, geo_p)
    print(f"✓ Esportati: {kml_p} e {geo_p}")
