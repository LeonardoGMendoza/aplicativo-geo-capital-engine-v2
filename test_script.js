
var uLat=0, uLng=0;

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
    if(el.tags['addr:street']) end=el.tags['addr:street']+(el.tags['addr:housenumber']?', '+el.tags['addr:housenumber']:'')+' – SP';
    var p={nome:nome,lat:elLat,lon:elLon,endereco:end,dist:dist,id:el.id};
    if(amenity==='pharmacy'||nome.match(/farmácia|farmacia|drogaria/i)) listas.m.push(p);
    else if(shop==='supermarket'||shop==='convenience'||shop==='marketplace'||nome.match(/mercado|supermercado|atacadão|atacado/i)) listas.c.push(p);
    else if(tourism==='hotel'||tourism==='hostel'||tourism==='guest_house'||social==='shelter'||nome.match(/hotel|albergue|pousada|abrigo temporário/i)) listas.s2.push(p);
    else if(amenity==='marketplace'||social==='food_bank'||nome.match(/banco de alimentos|cozinha comunitária|restaurante popular|distribuição de alimentos/i)) listas.q.push(p);
    else if(amenity==='hospital'||hc==='hospital'||nome.match(/hospital/i)) listas.h.push(p);
    else if(nome.match(/UPA/i)||op.match(/UPA/i)) listas.u.push(p);
    else if(nome.match(/UBS|UBSF|USF|AMA\b|Unidade de Sa/i)||op.match(/UBS|SUS/i)) listas.u.push(p);
    else if(amenity==='police'||nome.match(/delegacia|policia|polícia/i)) listas.d.push(p);
    else if(amenity==='social_facility'||nome.match(/ONG|abrigo|refugio|refúgio|assistência/i)) listas.o.push(p);
    else if(nome.match(/Pronto|Saúde|Saude|clinica|clínica/i)) listas.u.push(p);
    else listas.h.push(p);
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
