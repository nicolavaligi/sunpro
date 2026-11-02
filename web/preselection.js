/* SunPro — Copyright (c) 2026 Nicola Valigi. All rights reserved. */
(function (root) {
  'use strict';
  const number = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : null;
  const escape = value => String(value ?? 'Da verificare').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function assess(site, now = new Date()) {
    const checks = [];
    const add = (label, value, source, date) => checks.push({label, value: value ?? 'Da verificare', source: source || 'Fonte non documentata', date: date || 'Data non documentata'});
    const distance = number(site.sub_dist);
    const capacity = number(site.grid_capacity_mw);
    const documentedCapacity = capacity !== null && Boolean(site.grid_source && site.grid_updated_at);
    add('Superficie dichiarata (ha)', number(site.ha), site.area_source, site.area_updated_at);
    add('Superficie utile verificata (ha)', number(site.usable_area_ha), site.usable_area_source, site.usable_area_updated_at);
    add('Distanza cabina dichiarata (m)', distance, site.substation_source, site.substation_updated_at);
    add('Capacità di rete pubblicata (MW)', documentedCapacity ? capacity : null, site.grid_source, site.grid_updated_at);
    add('Area idonea', site.suitable_area_source && site.suitable_area_updated_at ? site.suitable_area_status : null, site.suitable_area_source, site.suitable_area_updated_at);
    add('Area di accelerazione', site.acceleration_area_source && site.acceleration_area_updated_at ? site.acceleration_area_status : null, site.acceleration_area_source, site.acceleration_area_updated_at);
    add('Vincoli territoriali', site.constraints_source && site.constraints_updated_at ? site.constraints_status : null, site.constraints_source, site.constraints_updated_at);
    add('Verifica catastale', site.verifica?.stato || site.catasto_stato, site.verifica?.fonte, site.verifica?.data);
    const pending = checks.filter(c => c.value === 'Da verificare' || c.source === 'Fonte non documentata' || c.date === 'Data non documentata').map(c => c.label);
    const warnings = ['La prossimità alla cabina non dimostra la disponibilità di connessione.', 'Area idonea, area di accelerazione e autorizzabilità richiedono verifiche distinte.', 'Potenza e produzione sono stime; la superficie dichiarata non coincide necessariamente con quella utilizzabile.'];
    if (distance === 0) warnings.push('Distanza cabina pari a zero: verificare coordinate e metodo di misura.');
    if (site.verifica?.stato === 'ANOMALIA_SEGNALATA') warnings.push(site.verifica.motivo || 'Anomalia catastale segnalata.');
    return {schema_version: 1, generated_at: now.toISOString(), id: site.id, name: site.name, comune: site.comune, coordinates_declared_lat_lon: site.ll, status: site.verifica?.stato === 'ANOMALIA_SEGNALATA' ? 'ANOMALIA_SEGNALATA' : 'PRESELEZIONE_DA_VERIFICARE', score_declared: number(site.score), score_note: 'Punteggio del motore esistente, non probabilità di autorizzazione.', checks, pending, warnings};
  }
  function html(report) {
    return '<!doctype html><html lang="it"><meta charset="utf-8"><title>Scheda di preselezione SunPro</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:20px;color:#172b35}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:10px;text-align:left}button{padding:12px}@media print{button{display:none}}</style><h1>SunPro · Scheda di preselezione</h1><h2>'+escape(report.name)+'</h2><p>'+escape(report.id)+' · '+escape(report.comune)+' · '+escape(report.status)+'</p><p>Generata: '+escape(report.generated_at)+'</p><p>Score dichiarato: '+escape(report.score_declared)+' / 100. '+escape(report.score_note)+'</p><table><thead><tr><th>Parametro</th><th>Valore</th><th>Fonte</th><th>Data del dato</th></tr></thead><tbody>'+report.checks.map(c=>'<tr>'+[c.label,c.value,c.source,c.date].map(v=>'<td>'+escape(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table><h2>Verifiche aperte</h2><ul>'+report.pending.map(v=>'<li>'+escape(v)+'</li>').join('')+'</ul><h2>Limiti della preselezione</h2><ul>'+report.warnings.map(v=>'<li>'+escape(v)+'</li>').join('')+'</ul><p>© 2026 Nicola Valigi — SunPro</p></html>';
  }
  root.SunProPreselection = {assess, html};
  if (typeof module !== 'undefined') module.exports = {assess, html};
})(typeof globalThis !== 'undefined' ? globalThis : this);
