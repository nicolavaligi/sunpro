"""
Generatore della mappa HTML standalone interattiva con layer Satellitare (Esri) e OpenStreetMap,
buffer D.Lgs. 199/2021, cabine AT/MT e schede popup dei lead.
Autore: Houdinick (Nicola Valigi)
"""

import folium
from folium.plugins import MarkerCluster, Fullscreen
from pathlib import Path
from data.storage import get_all_leads

def build_standalone_map(output_path: Path) -> Path:
    leads = get_all_leads()
    if not leads:
        return output_path

    avg_lat = sum(l["lat"] for l in leads) / len(leads)
    avg_lng = sum(l["lng"] for l in leads) / len(leads)

    # Crea mappa base
    m = folium.Map(
        location=[avg_lat, avg_lng],
        zoom_start=8,
        tiles=None
    )

    # Layer 1: OpenStreetMap Standard
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Mappa Stradale (OpenStreetMap)",
        control=True
    ).add_to(m)

    # Layer 2: CartoDB Positron (pulita per business)
    folium.TileLayer(
        tiles="CartoDB positron",
        name="Cartografia Neutra (CartoDB)",
        control=True
    ).add_to(m)

    # Layer 3: Esri World Imagery (Satellite alta risoluzione)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Ortofoto Satellitare (Esri Satellite)",
        control=True
    ).add_to(m)

    # Cluster di marker
    cluster = MarkerCluster(name="Aree Fotovoltaiche Qualificate").add_to(m)

    for l in leads:
        score = l["score_totale"]
        color = "green" if score >= 75 else ("orange" if score >= 60 else "blue")
        icon_name = "bolt" if "CAVA" in l["tipologia"] or "DISCARICA" in l["tipologia"] else "sun"

        wms_link = f"https://www.google.com/maps/@{l['lat']},{l['lng']},18m/data=!3m1!1e3"

        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; width: 280px; padding: 4px;">
            <div style="border-bottom: 2px solid #059669; padding-bottom: 6px; margin-bottom: 8px;">
                <h4 style="margin: 0; color: #0f172a; font-size: 15px;">{l['title']}</h4>
                <span style="font-size: 11px; color: #64748b;">ID: <b>{l['id']}</b> | {l['comune']} ({l['provincia']})</span>
            </div>

            <div style="background: #f8fafc; padding: 8px; border-radius: 6px; margin-bottom: 8px; font-size: 12px; border: 1px solid #e2e8f0;">
                <div>📐 <b>Superficie:</b> {l['superficie_ha']:.1f} ha ({l['mwp_stimati']:.1f} MWp)</div>
                <div>💶 <b>Prezzo Target:</b> {l['prezzo_mq_eur']:.2f} €/mq ({l['prezzo_richiesto_eur']:,.0f} €)</div>
                <div>⚡ <b>Cabina AT/MT:</b> {l['cabina_piu_vicina']}</div>
                <div>📏 <b>Distanza Cabina:</b> <b>{l['distanza_cabina_m']:,.0f} m</b></div>
                <div>📜 <b>Catasto:</b> Fg. {l.get('foglio')} - P.lle {l.get('particella')}</div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="background: #dcfce7; color: #166534; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px;">
                    Score: {score}/100
                </span>
                <span style="font-size: 11px; color: #475569; font-weight: 600;">{l['rating_classe']}</span>
            </div>

            <div style="font-size: 11px; color: #334155; margin-bottom: 8px;">
                <b>Proprietario:</b> {l['proprietario_nome']}<br/>
                <b>Canale:</b> {l.get('proprietario_pec') or l.get('proprietario_telefono') or 'Visura Sister'}
            </div>

            <a href="{wms_link}" target="_blank" style="display: block; text-align: center; background: #0284c7; color: #ffffff; text-decoration: none; padding: 6px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                🛰️ Ispeziona Satellite HD
            </a>
        </div>
        """

        # Marker particella
        folium.Marker(
            location=[l["lat"], l["lng"]],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"{l['title']} - {score}/100 ({l['superficie_ha']:.1f} ha)",
            icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
        ).add_to(cluster)

        # Cerchio buffer di prossimità cabina
        folium.Circle(
            location=[l["lat"], l["lng"]],
            radius=float(l["distanza_cabina_m"]),
            color="#059669",
            weight=1,
            fill=False,
            dash_array="4, 4",
            tooltip=f"Raggio Connessione Cabina: {l['distanza_cabina_m']:,.0f} m"
        ).add_to(m)

    # Tool avanzati
    Fullscreen(position="topright").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    m.save(str(output_path))
    return output_path

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "output" / "solar_land_map_standalone.html"
    build_standalone_map(out)
    print(f"Mappa generata in: {out}")
