/* Weekly OSM candidates: land-cover polygons, never cadastral boundaries. */
(async function loadWeeklyResearch() {
  const status = document.getElementById('weeklyStatus');
  const list = document.getElementById('weeklyCandidates');
  try {
    const [reportResponse, featuresResponse] = await Promise.all([
      fetch('weekly/latest.json', {cache:'no-cache'}),
      fetch('weekly/candidates.geojson', {cache:'no-cache'})
    ]);
    if (!reportResponse.ok || !featuresResponse.ok) throw new Error('Report unavailable');
    const report = await reportResponse.json();
    const data = await featuresResponse.json();
    const date = report.generated_at ? new Date(report.generated_at).toLocaleString('it-IT') : 'mai';
    status.textContent = `Ultima ricerca: ${date}. Esito: ${report.status}. Nuovi: ${report.new_ids.length}; modificati: ${report.changed_ids.length}; candidati: ${data.features.length}.`;
    if (report.regions_failed.length) status.textContent += ` Ricerca non riuscita: ${report.regions_failed.join(', ')}. Dati precedenti conservati.`;
    const stale = report.generated_at && Date.now() - Date.parse(report.generated_at) > 8*24*60*60*1000;
    if (stale) status.textContent += ' Report non aggiornato da oltre 8 giorni.';
    function installLayer() {
      if (map.getSource('weekly-candidates')) return;
      map.addSource('weekly-candidates', {type:'geojson',data,attribution:'© OpenStreetMap contributors'});
      map.addLayer({id:'weekly-candidates-fill',type:'fill',source:'weekly-candidates',paint:{'fill-color':'#f59e0b','fill-opacity':0.28}});
      map.addLayer({id:'weekly-candidates-outline',type:'line',source:'weekly-candidates',paint:{'line-color':'#fbbf24','line-width':2}});
      map.on('click','weekly-candidates-fill', event => {
        const prop = event.features[0].properties;
        const box = document.createElement('div');
        box.style.cssText = 'color:#0f172a;font-size:13px;line-height:1.5';
        const title = document.createElement('b');
        title.textContent = `${prop.region} · ${prop.area_ha} ha stimati`;
        const note = document.createElement('p');
        note.textContent = 'Candidato OSM da verificare. Confine di uso del suolo, non catastale. Disponibilità, edifici, prezzo e idoneità non accertati.';
        const link = document.createElement('a');
        link.href = `https://www.openstreetmap.org/way/${String(prop.id).replace('osm-way-','')}`;
        link.target = '_blank'; link.rel='noopener noreferrer';link.textContent='Apri fonte OpenStreetMap';
        box.append(title,note,link);
        new maplibregl.Popup().setLngLat(event.lngLat).setDOMContent(box).addTo(map);
      });
    }
    if (map.isStyleLoaded()) installLayer(); else map.once('load',installLayer);
    const summary = document.createElement('p');
    summary.textContent = 'Poligoni ambra: almeno 2 ha, vicini ad autostrade secondo OSM. Non costituiscono una qualifica catastale o normativa.';
    list.appendChild(summary);
    const toggle = document.createElement('button');
    toggle.className='btn';toggle.textContent='Mostra/nascondi candidati OSM';toggle.setAttribute('aria-pressed','true');
    let visible=true;
    toggle.addEventListener('click',()=>{
      if (!map.getLayer('weekly-candidates-fill')) return;
      visible=!visible;toggle.setAttribute('aria-pressed',String(visible));
      ['weekly-candidates-fill','weekly-candidates-outline'].forEach(id=>map.setLayoutProperty(id,'visibility',visible?'visible':'none'));
    });
    list.appendChild(toggle);
    data.features.slice().sort((a,b)=>b.properties.first_seen.localeCompare(a.properties.first_seen)).slice(0,30).forEach(feature=>{
      const prop=feature.properties;
      const button=document.createElement('button');button.className='btn';
      button.style.cssText='display:block;width:100%;margin-top:6px;text-align:left';
      button.textContent=`${prop.region} · ${prop.area_ha} ha · ${prop.id}`;
      button.addEventListener('click',()=>{stopOrbit();map.flyTo({center:prop.point,zoom:15,pitch:0});});
      list.appendChild(button);
    });
    if (data.features.length>30) {const extra=document.createElement('p');extra.textContent='Elenco: 30 candidati più recenti. Tutti i poligoni sono visibili in mappa e nel GeoJSON.';list.appendChild(extra);}
  } catch (error) {
    status.textContent='Report settimanale non ancora disponibile o caricamento non riuscito. Consulta le esecuzioni su GitHub.';
  }
})();
