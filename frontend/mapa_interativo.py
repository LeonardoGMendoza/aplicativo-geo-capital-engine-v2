"""
frontend/mapa_interativo.py
Mapa interativo com Leaflet 1.9.4.
- Locais REAIS buscados via Overpass API (OpenStreetMap)
- Clique no ponto → painel com botão Waze e Google Maps
- 100% em português, sem dados duplicados
- Funciona local e no Streamlit Cloud (sem API key)
"""
import json
from streamlit.components.v1 import html as st_html

# ============================================================
# DADOS DE FALLBACK — exibidos apenas se Overpass falhar
# (mesmos do app React original do Leonardo)
# ============================================================
FALLBACK_LOCAIS = [
    # ── Saúde ──────────────────────────────────────────────────────────────
    {"id": 9001, "nome": "UBS Itaquera",                    "tipo": "UBS",         "lat": -23.5394, "lon": -46.4552, "endereco": "Itaquera, São Paulo – SP"},
    {"id": 9002, "nome": "Hospital Santa Marcelina",         "tipo": "Hospital",    "lat": -23.5543, "lon": -46.4614, "endereco": "R. Santa Marcelina, 177 – Itaquera, SP"},
    {"id": 9003, "nome": "UBS Vila Ramos",                   "tipo": "UBS",         "lat": -23.5205, "lon": -46.4639, "endereco": "Vila Ramos, São Paulo – SP"},
    {"id": 9004, "nome": "UPA Penha",                        "tipo": "UPA",         "lat": -23.5199, "lon": -46.5309, "endereco": "Penha, São Paulo – SP"},
    {"id": 9005, "nome": "Hospital Tide Setubal",            "tipo": "Hospital",    "lat": -23.4972, "lon": -46.4401, "endereco": "São Miguel Paulista, São Paulo – SP"},
    # ── Abrigos ────────────────────────────────────────────────────────────
    {"id": 9006, "nome": "Ginásio Municipal Lajeado",        "tipo": "Abrigo",      "lat": -29.4660, "lon": -51.9610, "endereco": "Lajeado, RS"},
    {"id": 9007, "nome": "Rodoviária de Porto Alegre",       "tipo": "Abrigo",      "lat": -30.0350, "lon": -51.2210, "endereco": "Porto Alegre, RS"},
    {"id": 9008, "nome": "UPA São Sebastião",                "tipo": "UPA",         "lat": -23.8000, "lon": -45.4060, "endereco": "São Sebastião, SP"},
    {"id": 9009, "nome": "Hospital Bruno Born",              "tipo": "Hospital",    "lat": -29.4590, "lon": -51.9730, "endereco": "Lajeado, RS"},
    {"id": 9010, "nome": "Hospital Público Norte Fluminense","tipo": "Hospital",    "lat": -22.3600, "lon": -41.8000, "endereco": "Macaé, RJ"},
    # ── Alimento (q) ───────────────────────────────────────────────────────
    {"id": 9011, "nome": "Mercado Municipal de SP (Mercadão)","tipo": "Alimento",   "lat": -23.5421, "lon": -46.6293, "endereco": "R. da Cantareira, 306 – Centro, São Paulo – SP"},
    {"id": 9012, "nome": "Restaurante Bom Prato – Centro",   "tipo": "Alimento",   "lat": -23.5466, "lon": -46.6368, "endereco": "R. Boa Vista, 93 – Centro, São Paulo – SP"},
    {"id": 9013, "nome": "Feira Livre da Liberdade",          "tipo": "Alimento",   "lat": -23.5581, "lon": -46.6370, "endereco": "Pç. da Liberdade – Liberdade, São Paulo – SP"},
    # ── Medicamento (m) ────────────────────────────────────────────────────
    {"id": 9014, "nome": "Farmácia Popular – Centro SP",     "tipo": "Medicamento", "lat": -23.5500, "lon": -46.6340, "endereco": "Centro, São Paulo – SP"},
    {"id": 9015, "nome": "Droga Raia – Av. Paulista",        "tipo": "Medicamento", "lat": -23.5631, "lon": -46.6544, "endereco": "Av. Paulista, 726 – Bela Vista, São Paulo – SP"},
    {"id": 9016, "nome": "Drogasil – Pinheiros",             "tipo": "Medicamento", "lat": -23.5615, "lon": -46.6906, "endereco": "R. dos Pinheiros, 498 – Pinheiros, São Paulo – SP"},
    # ── Dormir (s2) ────────────────────────────────────────────────────────
    {"id": 9017, "nome": "Hotel Ibis São Paulo Centro",      "tipo": "Dormir",      "lat": -23.5412, "lon": -46.6380, "endereco": "R. Martins Fontes, 330 – República, São Paulo – SP"},
    {"id": 9018, "nome": "Albergue da Juventude SP",         "tipo": "Dormir",      "lat": -23.5600, "lon": -46.6500, "endereco": "Glicério, São Paulo – SP"},
    {"id": 9019, "nome": "Hotel Fórmula 1 – Paulista",       "tipo": "Dormir",      "lat": -23.5478, "lon": -46.6401, "endereco": "R. Vergueiro, 1571 – Paraíso, São Paulo – SP"},
    # ── Compras (c) ────────────────────────────────────────────────────────
    {"id": 9020, "nome": "Extra Hipermercado – Tatuapé",     "tipo": "Compras",     "lat": -23.5332, "lon": -46.5762, "endereco": "R. Itaquera, 800 – Tatuapé, São Paulo – SP"},
    {"id": 9021, "nome": "Carrefour – Pinheiros",            "tipo": "Compras",     "lat": -23.5665, "lon": -46.6925, "endereco": "Av. Sumaré, 901 – Pinheiros, São Paulo – SP"},
    {"id": 9022, "nome": "Pão de Açúcar – Consolação",       "tipo": "Compras",     "lat": -23.5555, "lon": -46.6528, "endereco": "R. da Consolação, 3085 – Consolação, São Paulo – SP"},
]


CIDADES_COORDS = {
    "São Paulo/SP":     (-23.5505, -46.6333, 13),
    "São Sebastião/SP": (-23.8077, -45.4075, 13),
    "Porto Alegre/RS":  (-30.0346, -51.2177, 13),
    "Lajeado/RS":       (-29.4661, -51.9615, 14),
    "Macaé/RJ":         (-22.3762, -41.7869, 13),
}

# ============================================================
# TEMPLATE HTML — raw string (sem f-string p/ não conflitar com JS)
# Substituição via __PLACEHOLDER__
# ============================================================
_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0e1117;color:#f9fafb;overflow:hidden}

/* ── barra superior ── */
#topbar{display:flex;align-items:center;flex-wrap:wrap;gap:6px;padding:7px 10px;background:#1a1f2e;border-bottom:1px solid #2d3748;min-height:46px}
.tbg{display:flex;align-items:center;gap:5px}
.sep{width:1px;height:20px;background:#374151;margin:0 3px}
.fb{padding:3px 10px;border-radius:14px;border:2px solid;cursor:pointer;font-size:11px;font-weight:700;background:transparent;transition:opacity .2s}
.fb.on{opacity:1}.fb.off{opacity:.28}
.fa{border-color:#22c55e;color:#22c55e}
.fh{border-color:#ef4444;color:#ef4444}
.fu{border-color:#f97316;color:#f97316}
.fd{border-color:#8b5cf6;color:#8b5cf6}
.fo{border-color:#06b6d4;color:#06b6d4}
.fn{border-color:#e11d48;color:#e11d48}
.fq{border-color:#eab308;color:#eab308}
.fm{border-color:#ec4899;color:#ec4899}
.fs2{border-color:#0ea5e9;color:#0ea5e9}
.fc{border-color:#a16207;color:#a16207}
.gpsbtn{padding:3px 10px;border-radius:14px;border:2px solid #7c3aed;cursor:pointer;font-size:11px;font-weight:700;background:transparent;color:#c4b5fd}
.gpsbtn:hover{background:#2e1065}
.thbtn{padding:3px 10px;border-radius:14px;border:2px solid #475569;cursor:pointer;font-size:11px;font-weight:700;background:transparent;color:#94a3b8}
#searchbox{flex:1;min-width:140px;padding:4px 10px;border-radius:14px;border:1px solid #374151;background:#111827;color:#f9fafb;font-size:12px;outline:none}
#searchbox::placeholder{color:#6b7280}
#searchbtn{padding:4px 10px;border-radius:14px;background:#3b82f6;color:#fff;border:none;font-size:11px;font-weight:700;cursor:pointer}
#searchbtn:hover{background:#2563eb}

/* ── layout ── */
#wrap{display:flex;height:__ALTURA_MAPA__px}
#map{flex:3;min-width:0;position:relative}
#panel{flex:0 0 270px;overflow-y:auto;padding:12px;background:#111827;border-left:1px solid #1f2937;font-size:12.5px;line-height:1.55}
@media (max-width:700px){
  #wrap{flex-direction:column}
  #panel{flex:0 0 150px;border-left:none;border-top:1px solid #1f2937}
  .tbg{width:100%;overflow-x:auto;flex-wrap:nowrap;-webkit-overflow-scrolling:touch;scroll-behavior:smooth;padding-bottom:2px}
  .tbg::-webkit-scrollbar{height:3px}
  .tbg::-webkit-scrollbar-thumb{background:#374151;border-radius:3px}
  .fb{flex:0 0 auto}
}

/* ── filtro escuro sobre tiles OSM ── */
#map.dark-map .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(0.82) saturate(1.1)}
#map.dark-map .leaflet-overlay-pane,
#map.dark-map .leaflet-marker-pane,
#map.dark-map .leaflet-popup-pane,
#map.dark-map .leaflet-tooltip-pane{filter:invert(1) hue-rotate(180deg)}

/* ── spinner de busca ── */
#spinner{display:none;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:999;background:#111827cc;padding:16px 24px;border-radius:12px;color:#f9fafb;font-size:13px;font-weight:600;text-align:center}
#spinner.show{display:block}

/* ── painel ── */
#panel h3{color:#60a5fa;margin-bottom:5px;font-size:13px}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;margin-bottom:8px}
.ir{display:flex;justify-content:space-between;margin:3px 0;gap:8px}
.il{color:#9ca3af;white-space:nowrap}.iv{font-weight:700;color:#f9fafb;text-align:right}
hr.div{border:none;border-top:1px solid #1f2937;margin:8px 0}
.ph{color:#6b7280;font-size:12px;text-align:center;margin-top:30px;line-height:1.8}
.nb{display:block;width:100%;margin:4px 0;padding:7px 10px;border-radius:8px;border:1px solid;cursor:pointer;font-size:12px;font-weight:700;text-align:center;background:transparent;transition:background .15s}
.na{border-color:#22c55e;color:#22c55e}.na:hover{background:#052e16}
.nh{border-color:#ef4444;color:#ef4444}.nh:hover{background:#3f0000}
.nu{border-color:#f97316;color:#f97316}.nu:hover{background:#431407}
.nd{border-color:#8b5cf6;color:#8b5cf6}.nd:hover{background:#1d0d3b}
.no{border-color:#06b6d4;color:#06b6d4}.no:hover{background:#032026}
.nq{border-color:#eab308;color:#eab308}.nq:hover{background:#1c1500}
.nm{border-color:#ec4899;color:#ec4899}.nm:hover{background:#2d0018}
.ns2{border-color:#0ea5e9;color:#0ea5e9}.ns2:hover{background:#021520}
.nc{border-color:#a16207;color:#a16207}.nc:hover{background:#1c1000}
.waze-btn{display:block;width:100%;margin:4px 0;padding:9px;border-radius:10px;border:none;cursor:pointer;font-size:13px;font-weight:800;text-align:center;background:#08d9d6;color:#000;transition:opacity .15s}
.waze-btn:hover{opacity:.85}
.gmaps-btn{display:block;width:100%;margin:4px 0;padding:9px;border-radius:10px;border:none;cursor:pointer;font-size:13px;font-weight:800;text-align:center;background:#4285f4;color:#fff;transition:opacity .15s}
.gmaps-btn:hover{opacity:.85}
.fn2{padding:5px 8px;border-radius:6px;background:#1e293b;border:1px solid #334155;color:#94a3b8;font-size:10px;margin:5px 0}
.aw{margin:5px 0;padding:6px 8px;border-radius:5px;background:#78350f;border:1px solid #d97706;color:#fcd34d;font-size:11px}
.ac{margin:5px 0;padding:6px 8px;border-radius:5px;background:#7f1d1d;border:1px solid #ef4444;color:#fca5a5;font-size:11px}
.near-group{margin-top:10px}
.near-title{font-size:10px;color:#6b7280;font-weight:700;margin:6px 0 3px;text-transform:uppercase;letter-spacing:.5px}

/* tema claro */
body.light{background:#f1f5f9;color:#0f172a}
body.light #topbar{background:#e2e8f0;border-color:#cbd5e0}
body.light #panel{background:#f8fafc;border-color:#e2e8f0;color:#1e293b}
body.light #panel h3{color:#1d4ed8}
body.light .iv{color:#0f172a}
body.light .ph{color:#94a3b8}
body.light #searchbox{background:#fff;color:#0f172a;border-color:#cbd5e0}
body.light #spinner{background:#f8fafccc;color:#0f172a}
</style>
</head>
<body>

<div id="topbar">
  <div class="tbg">
    <button class="fb fa on" onclick="toggleLayer('a',this)">🏠 Abrigos</button>
    <button class="fb fh on" onclick="toggleLayer('h',this)">🏥 Hospital</button>
    <button class="fb fu on" onclick="toggleLayer('u',this)">🏨 UBS/UPA</button>
    <button class="fb fd on" onclick="toggleLayer('d',this)">👮 Delegacia</button>
    <button class="fb fo on" onclick="toggleLayer('o',this)">🤝 ONG</button>
    <button class="fb fn on" onclick="toggleLayer('n',this)">🛰️ NASA</button>
    <button class="fb fq on" onclick="toggleLayer('q',this)">🍲 Alimento</button>
    <button class="fb fm on" onclick="toggleLayer('m',this)">💊 Medicamento</button>
    <button class="fb fs2 on" onclick="toggleLayer('s2',this)">🛏️ Dormir</button>
    <button class="fb fc on" onclick="toggleLayer('c',this)">🛒 Compras</button>
  </div>
  <div class="sep"></div>
  <input id="searchbox" placeholder="🔍 Buscar cidade ou bairro…" onkeydown="if(event.key==='Enter')buscarLocal()">
  <button id="searchbtn" onclick="buscarLocal()">Buscar</button>
  <div class="sep"></div>
  <button class="gpsbtn" onclick="usarGPS()">📍 GPS</button>
  <div class="sep"></div>
  <button class="thbtn" id="btema" onclick="toggleTema()">☀️ Claro</button>
</div>

<div id="wrap">
  <div id="map">
    <div id="spinner">🛰️ Buscando locais<br>no OpenStreetMap…</div>
  </div>
  <div id="panel">
    <div class="ph">
      👆 Clique em um ponto<br>no mapa para ver detalhes<br>e abrir a rota no Waze.<br><br>
      Ou use os botões abaixo<br>para ir ao mais próximo:
    </div>
    <div class="near-group">
      <div class="near-title">Ir para o mais próximo:</div>
      <button class="nb na" onclick="irMaisProximo('a')">🏠 Abrigo mais próximo</button>
      <button class="nb nh" onclick="irMaisProximo('h')">🏥 Hospital mais próximo</button>
      <button class="nb nu" onclick="irMaisProximo('u')">🏨 UBS/UPA mais próxima</button>
      <button class="nb nd" onclick="irMaisProximo('d')">👮 Delegacia mais próxima</button>
      <button class="nb no" onclick="irMaisProximo('o')">🤝 ONG mais próxima</button>
      <button class="nb nq" onclick="irMaisProximo('q')">🍲 Alimento mais próximo</button>
      <button class="nb nm" onclick="irMaisProximo('m')">💊 Farmácia mais próxima</button>
      <button class="nb ns2" onclick="irMaisProximo('s2')">🛏️ Local p/ dormir mais próximo</button>
      <button class="nb nc" onclick="irMaisProximo('c')">🛒 Mercado mais próximo</button>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
__JS_VARS__

/* ── MAPA ── */
var map = L.map('map',{zoomControl:true}).setView([INIT_LAT,INIT_LNG],INIT_ZOOM);
var tileOSM = L.tileLayer(
  'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  {attribution:'&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',maxZoom:19}
);
tileOSM.addTo(map);

var temaEscuro = true;
document.getElementById('map').classList.add('dark-map');

/* ── ÍCONES ── */
function mkIco(em,cor){
  return L.divIcon({
    html:'<div style="font-size:24px;line-height:1;filter:drop-shadow(0 1px 4px '+cor+')text-shadow:0 0 6px '+cor+'">'+em+'</div>',
    iconSize:[28,28],iconAnchor:[14,14],popupAnchor:[0,-16],className:''
  });
}
var ICOS = {
  a: mkIco('🏠','#22c55e'),
  h: mkIco('🏥','#ef4444'),
  u: mkIco('🏨','#f97316'),
  d: mkIco('👮','#8b5cf6'),
  o: mkIco('🤝','#06b6d4'),
  n: mkIco('⚠️','#e11d48'),
  q: mkIco('🍲','#eab308'),
  m: mkIco('💊','#ec4899'),
  s2:mkIco('🛏️','#0ea5e9'),
  c: mkIco('🛒','#a16207'),
  user: L.divIcon({
    html:'<div style="width:18px;height:18px;background:#3b82f6;border:3px solid #fff;border-radius:50%;box-shadow:0 0 0 4px rgba(59,130,246,.35)"></div>',
    iconSize:[18,18],iconAnchor:[9,9],className:''
  })
};

/* ── ESTADO ── */
var uLat=INIT_LAT, uLng=INIT_LNG;
var uMark = L.marker([uLat,uLng],{icon:ICOS.user,draggable:true,zIndexOffset:2000,title:'Você está aqui – arraste para mover'}).addTo(map);
uMark.on('dragend',function(e){uLat=e.target.getLatLng().lat;uLng=e.target.getLatLng().lng;});
map.on('click',function(e){
  if(e.originalEvent&&e.originalEvent._mk) return;
  uLat=e.latlng.lat; uLng=e.latlng.lng;
  uMark.setLatLng(e.latlng);
});

/* ── LAYERS ── */
var lyrs={a:L.layerGroup().addTo(map),h:L.layerGroup().addTo(map),u:L.layerGroup().addTo(map),
          d:L.layerGroup().addTo(map),o:L.layerGroup().addTo(map),n:L.layerGroup().addTo(map),
          q:L.layerGroup().addTo(map),m:L.layerGroup().addTo(map),s2:L.layerGroup().addTo(map),c:L.layerGroup().addTo(map)};
var vis={a:true,h:true,u:true,d:true,o:true,n:true,q:true,m:true,s2:true,c:true};

/* dados ativos por tipo */
var dados={a:[],h:[],u:[],d:[],o:[],n:[],q:[],m:[],s2:[],c:[]};

/* ── HAVERSINE ── */
function hav(a1,o1,a2,o2){
  var R=6371,dA=(a2-a1)*Math.PI/180,dO=(o2-o1)*Math.PI/180;
  var a=Math.sin(dA/2)*Math.sin(dA/2)+Math.cos(a1*Math.PI/180)*Math.cos(a2*Math.PI/180)*Math.sin(dO/2)*Math.sin(dO/2);
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}
function fDist(km){return km<1?(km*1000).toFixed(0)+' m':km.toFixed(1)+' km';}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

/* ── ADICIONAR MARCADORES ── */
function addMarkers(arr,tipo){
  lyrs[tipo].clearLayers();
  dados[tipo]=arr;
  arr.forEach(function(p){
    if(!p.lat||!p.lon) return;
    var m=L.marker([p.lat,p.lon],{icon:ICOS[tipo]});
    m.on('click',function(e){
      e.originalEvent._mk=true;
      mostrarPainel(p,tipo);
      map.setView([p.lat,p.lon],15,{animate:true});
    });
    var tt='<b>'+esc(p.nome||p.name||'')+'</b>'+(p.tipo?'<br><small>'+esc(p.tipo)+'</small>':'');
    m.bindTooltip(tt,{sticky:true,opacity:.92});
    lyrs[tipo].addLayer(m);
  });
}

/* ── PAINEL DE DETALHES ── */
var CORES={a:'#22c55e',h:'#ef4444',u:'#f97316',d:'#8b5cf6',o:'#06b6d4',q:'#eab308',m:'#ec4899',s2:'#0ea5e9',c:'#a16207'};
var LABELS={a:'Abrigo de Evacuação',h:'Hospital',u:'UBS / UPA / Clínica',d:'Delegacia / Segurança',o:'ONG / Apoio Social',q:'🍲 Ponto de Alimento',m:'💊 Farmácia / Medicamento',s2:'🛏️ Local para Dormir',c:'🛒 Mercado / Compras'};
var EMJS={a:'🏠',h:'🏥',u:'🏨',d:'👮',o:'🤝',q:'🍲',m:'💊',s2:'🛏️',c:'🛒'};

function mostrarPainel(p,tipo){
  var cor=CORES[tipo]||'#60a5fa';
  var lbl=LABELS[tipo]||'Local';
  var emj=EMJS[tipo]||'📍';
  var nome=p.nome||p.name||'Local';
  var end=p.endereco||p.address||'';
  var dist=hav(uLat,uLng,p.lat,p.lon);

  /* alertas NASA próximos ao destino */
  var alerts=[];
  dados.n.forEach(function(ev){var d=hav(p.lat,p.lon,ev.lat,ev.lon);if(d<300)alerts.push({d:d,t:ev.title||ev.nome});});
  alerts.sort(function(a,b){return a.d-b.d;});

  var h='<h3 style="color:'+cor+'">'+emj+' '+esc(nome)+'</h3>';
  h+='<span class="badge" style="background:'+cor+'22;color:'+cor+'">'+lbl+'</span>';
  h+='<div class="ir"><span class="il">📏 Distância</span><span class="iv">'+fDist(dist)+' de você</span></div>';
  if(end) h+='<div class="ir"><span class="il">📍 Endereço</span><span class="iv" style="max-width:160px">'+esc(end)+'</span></div>';
  if(p.cidade) h+='<div class="ir"><span class="il">🏙️ Cidade</span><span class="iv">'+esc(p.cidade)+'</span></div>';
  if(p.capacidade) h+='<div class="ir"><span class="il">👥 Capacidade</span><span class="iv">'+p.capacidade+' pessoas</span></div>';

  if(alerts.length){
    h+='<hr class="div">';
    alerts.slice(0,2).forEach(function(al){
      h+='<div class="'+(al.d<100?'ac':'aw')+'">⚠️ '+esc(al.t)+'<br><small>'+al.d.toFixed(0)+' km deste local</small></div>';
    });
  }

  h+='<hr class="div">';
  h+='<p style="font-size:11px;color:#9ca3af;margin-bottom:6px">Abrir rota no aplicativo:</p>';
  h+='<button class="waze-btn" onclick="abrirWaze('+p.lat+','+p.lon+')">🚗 Ir pelo Waze</button>';
  h+='<button class="gmaps-btn" onclick="abrirGMaps('+p.lat+','+p.lon+')">🗺️ Ir pelo Google Maps</button>';

  h+='<hr class="div">';
  h+='<div class="near-group"><div class="near-title">Ir para o mais próximo:</div>';
  h+='<button class="nb na" onclick="irMaisProximo(\'a\')">🏠 Abrigo</button>';
  h+='<button class="nb nh" onclick="irMaisProximo(\'h\')">🏥 Hospital</button>';
  h+='<button class="nb nu" onclick="irMaisProximo(\'u\')">🏨 UBS/UPA</button>';
  h+='<button class="nb nd" onclick="irMaisProximo(\'d\')">👮 Delegacia</button>';
  h+='<button class="nb no" onclick="irMaisProximo(\'o\')">🤝 ONG</button>';
  h+='<button class="nb nq" onclick="irMaisProximo(\'q\')">🍲 Alimento</button>';
  h+='<button class="nb nm" onclick="irMaisProximo(\'m\')">💊 Farmácia</button>';
  h+='<button class="nb ns2" onclick="irMaisProximo(\'s2\')">🛏️ Dormir</button>';
  h+='<button class="nb nc" onclick="irMaisProximo(\'c\')">🛒 Mercado</button></div>';

  document.getElementById('panel').innerHTML=h;
}

/* ── ABRIR WAZE / GOOGLE MAPS ── */
function abrirWaze(lat,lon){
  var wz = "https://www.waze.com/live-map/directions?navigate=yes&to=ll."+lat+"%2C"+lon+"&from=ll."+uLat+"%2C"+uLng;
  window.open(wz, '_blank');
}
function abrirGMaps(lat,lon){
  var gm = "https://www.google.com/maps/dir/?api=1&origin="+uLat+","+uLng+"&destination="+lat+","+lon;
  window.open(gm, '_blank');
}

/* ── NASA ── */
NASA_DATA.forEach(function(p){
  var m=L.marker([p.lat,p.lon],{icon:ICOS.n});
  m.bindTooltip('<b>🛰️ '+esc(p.title||p.nome||'')+'</b><br><small>'+esc(p.cat||'')+'</small>',{sticky:true,opacity:.92});
  m.on('click',function(e){e.originalEvent._mk=true;});
  lyrs.n.addLayer(m);
  dados.n.push(p);
});

/* ── BUSCA OVERPASS (locais reais do OSM) ── */
async function buscarOverpass(lat,lon,usarFallback){
  mostrarSpinner(true);
  var r=10000;
  var q='[out:json][timeout:60];('
    +'node["amenity"~"hospital|clinic|doctors|health_post"](around:'+r+','+lat+','+lon+');'
    +'way["amenity"~"hospital|clinic|doctors|health_post"](around:'+r+','+lat+','+lon+');'
    +'node["healthcare"~"hospital|clinic|centre|doctor"](around:'+r+','+lat+','+lon+');'
    +'way["healthcare"~"hospital|clinic|centre|doctor"](around:'+r+','+lat+','+lon+');'
    +'node["name"~"UBS|UPA|AMA|Hospital|Pronto|Saúde|Delegacia|ONG|Abrigo",i](around:'+r+','+lat+','+lon+');'
    +'way["name"~"UBS|UPA|AMA|Hospital|Pronto|Saúde|Delegacia|ONG|Abrigo",i](around:'+r+','+lat+','+lon+');'
    +'node["amenity"="police"](around:'+r+','+lat+','+lon+');'
    +'way["amenity"="police"](around:'+r+','+lat+','+lon+');'
    +'node["amenity"="social_facility"](around:'+r+','+lat+','+lon+');'
    +'way["amenity"="social_facility"](around:'+r+','+lat+','+lon+');'
    +'node["amenity"="pharmacy"](around:'+r+','+lat+','+lon+');'
    +'way["amenity"="pharmacy"](around:'+r+','+lat+','+lon+');'
    +'node["shop"~"supermarket|convenience|marketplace"](around:'+r+','+lat+','+lon+');'
    +'way["shop"~"supermarket|convenience|marketplace"](around:'+r+','+lat+','+lon+');'
    +'node["tourism"~"hotel|hostel|guest_house"](around:'+r+','+lat+','+lon+');'
    +'way["tourism"~"hotel|hostel|guest_house"](around:'+r+','+lat+','+lon+');'
    +'node["social_facility"~"shelter|food_bank"](around:'+r+','+lat+','+lon+');'
    +'way["social_facility"~"shelter|food_bank"](around:'+r+','+lat+','+lon+');'
    +'node["amenity"="marketplace"](around:'+r+','+lat+','+lon+');'
    +'way["amenity"="marketplace"](around:'+r+','+lat+','+lon+');'
    +');out center;';
  try{
    var resp=await fetch('https://overpass-api.de/api/interpreter',{
      method:'POST',body:q,
      headers:{'Content-Type':'text/plain','User-Agent':'OmniEcoRescue/1.0'},
      signal:AbortSignal.timeout?AbortSignal.timeout(35000):undefined
    });
    var data=await resp.json();
    processarOverpass(data.elements,lat,lon);
  }catch(err){
    console.warn('Overpass falhou:',err);
    if(usarFallback) carregarFallback(lat,lon);
  }finally{mostrarSpinner(false);}
}

function processarOverpass(elements,refLat,refLon){
  var listas={a:[],h:[],u:[],d:[],o:[],q:[],m:[],s2:[],c:[]};
  var vistos=new Set();
  elements.forEach(function(el){
    var nome=el.tags&&el.tags.name;
    if(!nome||vistos.has(nome)) return;
    vistos.add(nome);
    var elLat=el.lat||(el.center&&el.center.lat);
    var elLon=el.lon||(el.center&&el.center.lon);
    if(!elLat||!elLon) return;
    var amenity=(el.tags.amenity||'').toLowerCase();
    var hc=(el.tags.healthcare||'').toLowerCase();
    var op=(el.tags.operator||'');
    var social=(el.tags.social_facility||'').toLowerCase();
    var shop=(el.tags.shop||'').toLowerCase();
    var tourism=(el.tags.tourism||'').toLowerCase();
    var dist=hav(refLat,refLon,elLat,elLon);
    var end='';
    if(el.tags['addr:street']) end=el.tags['addr:street']+(el.tags['addr:housenumber']?', '+el.tags['addr:housenumber']:'');
    var p={nome:nome,lat:elLat,lon:elLon,endereco:end,dist:dist,id:el.id};
    if(amenity==='pharmacy'||nome.match(/farmácia|farmacia|drogaria/i)) listas.m.push(p);
    else if(shop==='supermarket'||shop==='convenience'||shop==='marketplace'||nome.match(/mercado|supermercado|atacadão|atacado/i)) listas.c.push(p);
    else if(tourism==='hotel'||tourism==='hostel'||tourism==='guest_house'||social==='shelter'||nome.match(/hotel|albergue|pousada|abrigo temporário/i)) listas.s2.push(p);
    else if(amenity==='marketplace'||social==='food_bank'||nome.match(/banco de alimentos|cozinha comunitária|restaurante popular|distribuição de alimentos/i)) listas.q.push(p);
    else if(amenity==='hospital'||hc==='hospital'||nome.match(/hospital/i)) listas.h.push(p);
    else if(/\bUPA\b/.test(nome)||/\bUPA\b/.test(op)) listas.u.push(p);
    else if(/\b(UBS|UBSF|USF|AMA)\b/.test(nome)||nome.match(/Unidade de Sa/i)||/\b(UBS|SUS)\b/.test(op)) listas.u.push(p);
    else if(amenity==='police'||nome.match(/delegacia|policia|polícia/i)) listas.d.push(p);
    else if(amenity==='social_facility'||/\bONG\b/.test(nome)||nome.match(/abrigo|refugio|ref\u00fagio|assist\u00eancia/i)) listas.o.push(p);
    else if(nome.match(/Pronto[- ]?(Socorro|Atendimento)|Sa[\u00fau]de|Cl[\u00edi]nica/i)) listas.u.push(p);
  });
  /* ordena por distância e limita */
  Object.keys(listas).forEach(function(t){
    listas[t].sort(function(a,b){return a.dist-b.dist;});
    listas[t]=listas[t].slice(0,40);
    addMarkers(listas[t],t);
  });
  /* abrigos fixos sempre presentes */
  addMarkers(ABRIGOS_DATA,'a');
}

function carregarFallback(lat,lon){
  var listas={a:[],h:[],u:[],d:[],o:[],q:[],m:[],s2:[],c:[]};
  FALLBACK.forEach(function(p){
    p.dist=hav(lat,lon,p.lat,p.lon);
    if(p.tipo==='Hospital')                                    listas.h.push(p);
    else if(p.tipo==='UBS'||p.tipo==='UPA'||p.tipo==='AMA')   listas.u.push(p);
    else if(p.tipo==='Abrigo')                                 listas.a.push(p);
    else if(p.tipo==='Alimento')                               listas.q.push(p);
    else if(p.tipo==='Medicamento')                            listas.m.push(p);
    else if(p.tipo==='Dormir')                                 listas.s2.push(p);
    else if(p.tipo==='Compras')                                listas.c.push(p);
    else                                                       listas.o.push(p);
  });
  Object.keys(listas).forEach(function(t){addMarkers(listas[t],t);});
  addMarkers(ABRIGOS_DATA,'a');
}

/* ── GPS ── */
function usarGPS(){
  if(!navigator.geolocation){alert('Geolocalização não disponível. Use a caixa de busca.');return;}
  mostrarSpinner(true);
  navigator.geolocation.getCurrentPosition(
    function(p){
      uLat=p.coords.latitude; uLng=p.coords.longitude;
      uMark.setLatLng([uLat,uLng]);
      map.setView([uLat,uLng],14,{animate:true});
      buscarOverpass(uLat,uLng,true);
    },
    function(e){
      mostrarSpinner(false);
      alert('GPS bloqueado ('+e.message+'). Use a caixa de busca para digitar sua cidade.');
    },
    {timeout:10000,enableHighAccuracy:true}
  );
}

/* ── BUSCA POR TEXTO ── */
async function buscarLocal(){
  var q=document.getElementById('searchbox').value.trim();
  if(!q) return;
  mostrarSpinner(true);
  try{
    var r=await fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=br&q='+encodeURIComponent(q),
      {headers:{'User-Agent':'OmniEcoRescue/1.0'}});
    var d=await r.json();
    if(d&&d.length>0){
      uLat=parseFloat(d[0].lat); uLng=parseFloat(d[0].lon);
      uMark.setLatLng([uLat,uLng]);
      map.setView([uLat,uLng],13,{animate:true});
      buscarOverpass(uLat,uLng,true);
    } else {
      mostrarSpinner(false);
      alert('Local não encontrado. Tente um nome de bairro ou cidade do Brasil.');
    }
  }catch(e){mostrarSpinner(false);alert('Erro ao buscar: '+e.message);}
}

/* ── SPINNER ── */
function mostrarSpinner(s){
  document.getElementById('spinner').classList.toggle('show',s);
}

/* ── FILTROS ── */
function toggleLayer(t,btn){
  vis[t]=!vis[t];
  btn.classList.toggle('on',vis[t]);
  btn.classList.toggle('off',!vis[t]);
  vis[t]?map.addLayer(lyrs[t]):map.removeLayer(lyrs[t]);
  if(btn.parentElement && btn.parentElement.classList.contains('tbg')){
    btn.parentElement.scrollTo({left: btn.offsetLeft - 4, behavior:'smooth'});
  }
}

/* ── MAIS PRÓXIMO ── */
function irMaisProximo(t){
  var arr=dados[t];
  if(!arr||!arr.length){alert('Nenhum ponto deste tipo carregado. Clique em GPS ou busque sua cidade primeiro.');return;}
  var best=null,bd=Infinity;
  arr.forEach(function(p){var d=hav(uLat,uLng,p.lat,p.lon);if(d<bd){bd=d;best=p;}});
  if(best){
    mostrarPainel(best,t);
    map.setView([best.lat,best.lon],15,{animate:true});
  }
}

/* ── TEMA ── */
function toggleTema(){
  temaEscuro=!temaEscuro;
  var btn=document.getElementById('btema');
  var me=document.getElementById('map');
  if(temaEscuro){document.body.classList.remove('light');me.classList.add('dark-map');btn.textContent='☀️ Claro';}
  else{document.body.classList.add('light');me.classList.remove('dark-map');btn.textContent='🌙 Escuro';}
}

/* ── CARGA INICIAL ── */
buscarOverpass(INIT_LAT,INIT_LNG,true);
</script>
</body>
</html>
"""

def render_mapa_interativo(abrigos, eventos_nasa, origem="São Paulo/SP", altura=640):
    """
    Renderiza mapa interativo com:
    - Locais REAIS buscados via Overpass API (OSM): hospitais, UBS, UPA, delegacias, ONGs
    - Clique no ponto → painel em português + botões Waze e Google Maps
    - Abrigos da lista fixa sempre presentes como camada base
    - Eventos NASA como pontos de alerta
    """
    lat, lng, zoom = CIDADES_COORDS.get(origem, (-23.5505, -46.6333, 13))
    altura_mapa = altura - 48  # desconta topbar

    # NASA: extrai com json.dumps (escapa tudo automaticamente)
    nasa_pts = []
    for ev in (eventos_nasa or [])[:25]:
        try:
            geom = ev.get("geometry", [])
            if not geom:
                continue
            coords = geom[-1].get("coordinates")
            if not coords or len(coords) < 2:
                continue
            nasa_pts.append({
                "lat":   float(coords[1]),
                "lon":   float(coords[0]),
                "title": str(ev.get("title", "Evento NASA")),
                "cat":   str(ev["categories"][0]["title"]) if ev.get("categories") else "Desastre",
            })
        except (KeyError, IndexError, TypeError, ValueError):
            continue

    js_vars = (
        f"var ABRIGOS_DATA = {json.dumps(abrigos,      ensure_ascii=False)};\n"
        f"var FALLBACK     = {json.dumps(FALLBACK_LOCAIS, ensure_ascii=False)};\n"
        f"var NASA_DATA    = {json.dumps(nasa_pts,     ensure_ascii=False)};\n"
        f"var INIT_LAT     = {lat};\n"
        f"var INIT_LNG     = {lng};\n"
        f"var INIT_ZOOM    = {zoom};\n"
    )

    html = (
        _TEMPLATE
        .replace("__JS_VARS__",     js_vars)
        .replace("__ALTURA_MAPA__", str(altura_mapa))
    )
    st_html(html, height=altura)
