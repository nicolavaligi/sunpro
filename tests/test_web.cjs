const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const html=fs.readFileSync(require('node:path').join(__dirname, '..', 'index.html'),'utf8');
const script=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]).join('\n');
const els=new Map();
function element(){return {style:{},dataset:{},children:[],listeners:{},classList:{add(){},remove(){},contains(){return false},toggle(){}},addEventListener(k,fn){this.listeners[k]=fn},setAttribute(){},removeAttribute(){},appendChild(c){this.children.push(c)},scrollIntoView(){}}}
const get=id=>{if(!els.has(id))els.set(id,element());return els.get(id)}; get('searchInput').value='';
const handlers={}; const layers=new Map();const sources=new Map();
class MapMock {constructor(options){options.style.layers.forEach(x=>layers.set(x.id,x));}on(k,...args){handlers[k]=args.at(-1)}addControl(){}isStyleLoaded(){return true}getLayer(k){return layers.get(k)}getSource(k){return sources.get(k)}addSource(k,s){assert(!sources.has(k));sources.set(k,s)}addLayer(l){assert(!layers.has(l.id));layers.set(l.id,l)}setLayoutProperty(k,p,v){assert(layers.has(k));layers.get(k)[p]=v}getBearing(){return 45}setBearing(){}flyTo(){}getCanvas(){return {style:{}}}}
const context=vm.createContext({document:{getElementById:get,createElement:element,querySelectorAll:()=>[],querySelector:()=>null,addEventListener(){}}, maplibregl:{Map:MapMock,NavigationControl:class{},Marker:class{setLngLat(){return this}addTo(){return this}}},setInterval(){},setTimeout,clearTimeout,requestAnimationFrame(){return 1},cancelAnimationFrame(){},fetch:async()=>({ok:false,status:503}),console,Intl,Date});
vm.runInContext(script,context);
const run=code=>vm.runInContext(code,context);
assert.equal(get('cards').children.length,run('SITES.length'));
run("renderCards('Lombardia','  MILANO  ')");assert.equal(get('cards').children.length,run('SITES.length'));
run("renderCards('TUTTE','zzzzzzzz')");assert.equal(get('emptyResults').hidden,false);
run("renderCards('TUTTE','')");assert.equal(get('emptyResults').hidden,true);assert.equal(get('cards').children.length,run('SITES.length'));
handlers.load();assert.equal(get('cards').children.length,run('SITES.length'));
get('tSat').listeners.click({currentTarget:get('tSat')});assert.equal(layers.get('satellite-layer').visibility,'none');assert(layers.has('carto-layer'));
get('tSat').listeners.click({currentTarget:get('tSat')});assert.equal(layers.get('satellite-layer').visibility,'visible');
(async()=>{await get('tAgri').listeners.click({currentTarget:get('tAgri')});assert.equal(get('tAgri').disabled,false);assert.match(get('mapStatus').textContent,/riprovare/);let requests=0;context.fetch=async()=>{requests++;return {ok:true,json:async()=>({type:'FeatureCollection',features:[]})}};await Promise.all([get('tAgri').listeners.click({currentTarget:get('tAgri')}),get('tAgri').listeners.click({currentTarget:get('tAgri')})]);assert.equal(requests,1);assert(layers.has('attigui-fill'));await get('tAgri').listeners.click({currentTarget:get('tAgri')});assert.equal(layers.get('attigui-fill').visibility,'none');assert.equal(requests,1);console.log('PASS: startup, search, card reuse, empty state, map initialization, satellite toggle, fetch failure/retry, concurrent clicks and cached layer toggle');})();
assert.equal(run("SITES.find(s => s.id === 'FV-AGRI-MN-005').verifica.stato"), 'ANOMALIA_SEGNALATA');
assert.equal(run("isShortlist(SITES.find(s => s.id === 'FV-AGRI-MN-005'))"), false);
run("renderCards('ANOMALIE','')");
assert.equal(get('sitesCount').textContent,'1 siti');
assert.equal(get('cards').children.filter(c=>!c.hidden).length,1);
run("showGuideTip(SITES.find(s => s.id === 'FV-AGRI-MN-005'))");
assert.match(get('siteTip').innerHTML,/Anomalia segnalata/);
assert.doesNotMatch(get('siteTip').innerHTML,/WMS AdE Verificato/);
assert.match(get('siteTip').innerHTML, /Scheda preliminare HTML/);
assert.match(get('siteTip').innerHTML, /Dati e verifiche JSON/);
run("openPdf('FV-AGRI-MN-005')");assert.match(get('mapStatus').textContent,/Dossier sospeso/);
run("openPdf(SITES[0].id)");assert.match(get('mapStatus').textContent,/Dossier sospeso/);
assert.equal(run("SITES.filter(s => s.catasto_stato === 'VERIFICATO_WMS_ADE').length"),0);
console.log('PASS: cadastral anomaly, candidate exclusion, anomaly filter, popup labels and unvalidated dossier blocking');

