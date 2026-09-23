'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = (n, digits=0) => new Intl.NumberFormat('fr-FR',{maximumFractionDigits:digits,minimumFractionDigits:digits}).format(n);
  const sign = (n, digits=1) => `${n>=0?'+':'−'}${fmt(Math.abs(n),digits)}`;
  const classNames = {Gastropoda:'Gastéropodes',Bivalvia:'Bivalves',Mammalia:'Mammifères',Reptilia:'Reptiles',Actinopterygii:'Poissons à nageoires rayonnées',Chondrichthyes:'Poissons cartilagineux',Cephalopoda:'Céphalopodes',Echinoidea:'Oursins',Asteroidea:'Étoiles de mer',Ophiuroidea:'Ophiures',Malacostraca:'Crustacés',Gymnolaemata:'Bryozoaires',Rhynchonellata:'Brachiopodes',Anthozoa:'Coraux et apparentés'};
  const environments = {'marine indet.':'Milieu marin, non précisé','carbonate indet.':'Milieu carbonaté, non précisé','terrestrial indet.':'Milieu continental, non précisé','fluvial indet.':'Milieu fluvial','lacustrine indet.':'Milieu lacustre','lagoonal':'Lagune','coastal indet.':'Milieu côtier','reef, buildup or bioherm':'Récif ou construction biologique','shoreface':'Avant-plage','offshore':'Milieu marin au large','deltaic indet.':'Milieu deltaïque'};
  const monthNames = ['Jan','Fév','Mar','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc'];
  const metrics = {mean_c:{label:'Température moyenne',unit:'°C',digits:1},hot_days:{label:'Jours ≥ 30 °C',unit:'j/an',digits:1},tropical_nights:{label:'Nuits ≥ 20 °C',unit:'j/an',digits:1},rain_mm:{label:'Précipitations',unit:'mm/an',digits:0},frost_days:{label:'Jours de gel',unit:'j/an',digits:1}};
  let D, siteMap, cityMap, refMap, filtered = [], currentSites=[];
  let state = {mode:'past',city:'78640',model:'MRI_AGCM3_2_S',metric:'mean_c',chart:'temp',department:'',group:'',search:'',young:0,old:150,nearby:false,radius:30,selected:null,limit:12};
  let view = {x:0,y:0,w:760,h:540};
  let quiz = {index:0,score:0,answered:false,questions:[]};
  const groupLabel = x => classNames[x] || x || 'Groupe non renseigné';
  const age = f => `${fmt(f.min_ma,1)}–${fmt(f.max_ma,1)} Ma`;
  const city = () => cityMap[state.city];
  function distance(a,b){const r=Math.PI/180;const x=Math.sin((b.latitude-a.latitude)*r/2)**2+Math.cos(a.latitude*r)*Math.cos(b.latitude*r)*Math.sin((b.longitude-a.longitude)*r/2)**2;return 12742*Math.asin(Math.min(1,Math.sqrt(x)));}
  const selectedSeries = (code=state.city, kind=state.mode==='present'?'baseline':'future', model=state.model) => D.climate.find(x=>x.city_code===code && x.kind===kind && (kind==='baseline'||x.model_id===model) && x.available);
  function option(value,text){return `<option value="${esc(value)}">${esc(text)}</option>`;}
  function stat(value,label,note=''){return `<div class="stat"><strong>${value}</strong><small>${esc(label)}</small>${note?`<em>${esc(note)}</em>`:''}</div>`;}
  function project(lon,lat){return [(lon-1.4)/2.2*690+35,(49.25-lat)/1.15*450+35];}
  function geometryPath(geometry){const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.coordinates;return polygons.map(poly=>poly.map(ring=>ring.map((p,i)=>`${i?'L':'M'}${project(...p).map(v=>v.toFixed(1)).join(',')}`).join('')+'Z').join('')).join('');}
  function filterFossils(){
    const search=state.search.trim().toLocaleLowerCase('fr');
    filtered=D.fossils.filter(f=>{const s=siteMap[f.site_id];return (!state.department||s.department_code===state.department)&&(!state.group||(state.group==='__missing__'?!f.class_name:f.class_name===state.group))&&f.max_ma>=state.young&&f.min_ma<=state.old&&(!state.nearby||distance(city(),s)<=state.radius)&&(!search||[f.accepted_name,f.identified_name,f.class_name,groupLabel(f.class_name),s.name].some(t=>(t||'').toLocaleLowerCase('fr').includes(search)));});
    const counts=new Map();filtered.forEach(f=>counts.set(f.site_id,(counts.get(f.site_id)||0)+1));
    currentSites=[...counts].map(([id,count])=>({...siteMap[id],count}));
    if (state.selected && !filtered.some(f=>f.occurrence_id===state.selected)) state.selected=null;
  }
  function updateControls(){
    $('city').value=state.city;$('model').value=state.model;$('metric').value=state.metric;
    $('department').value=state.department;$('taxon-class').value=state.group;$('search').value=state.search;
    $('age-young').value=state.young;$('age-old').value=state.old;
    $('young-value').textContent=`${fmt(state.young,1)} Ma`;$('old-value').textContent=`${fmt(state.old,1)} Ma`;
    $('age-label').textContent=`${fmt(state.young,1)}–${fmt(state.old,1)} Ma`;
    $('nearby').checked=state.nearby;$('radius').value=state.radius;$('radius-value').textContent=`${state.radius} km`;$('radius').disabled=!state.nearby;
    document.querySelectorAll('[data-mode]').forEach(b=>{const active=b.dataset.mode===state.mode;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    $('past-filters').hidden=state.mode!=='past';$('climate-filters').hidden=state.mode==='past';$('model-control').hidden=state.mode==='present';
    $('mobile-filters').hidden=state.mode!=='past';
    $('past-results').hidden=state.mode!=='past';$('climate-results').hidden=state.mode==='past';$('analogues-panel').hidden=state.mode!=='future';
    $('explorer').hidden=state.mode==='data';$('data-view').hidden=state.mode!=='data';
  }
  function render(){
    updateControls();
    if(state.mode==='data'){renderData();return;}
    if(state.mode==='past'){
      filterFossils();
      $('stats').innerHTML=stat(fmt(filtered.length),'Occurrences documentées')+stat(fmt(currentSites.length),'Collections PBDB')+stat(fmt(new Set(filtered.map(f=>f.taxon_id)).size),'Taxons acceptés distincts');
      $('map-kicker').textContent='CARTE DES DÉCOUVERTES';$('map-title').textContent=state.nearby?`Autour de ${city().name}`:'Les traces du passé';
      $('legend').innerHTML='<span><i class="dot"></i>Collections fossiles · taille = occurrences</span><span><i class="dot mint"></i>Commune repère</span>';
      $('random').disabled=!filtered.length;renderList();renderInspector();
    }else{renderClimate();}
    renderMap();
  }
  function renderMap(){
    let svg='<defs><pattern id="grid" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M 38 0 L 0 0 0 38" fill="none" stroke="#47637c" stroke-width=".45" opacity=".22"/></pattern></defs><rect x="-3000" y="-3000" width="6500" height="6500" fill="url(#grid)"/>';
    D.departments.features.forEach(f=>{const p=f.properties;svg+=`<path class="map-department ${p.code===state.department?'selected':''}" d="${geometryPath(f.geometry)}" fill-rule="evenodd" data-dept="${esc(p.code)}"><title>${esc(p.nom)} (${p.code})</title></path>`;});
    const labels=[['YVELINES',1.8,48.85],['VAL-D’OISE',2.15,49.15],['SEINE-ET-MARNE',3.04,48.61],['ESSONNE',2.24,48.42]];
    svg+=labels.map(([t,lon,lat])=>{const[x,y]=project(lon,lat);return`<text class="dept-label" x="${x}" y="${y}">${t}</text>`;}).join('');
    if(state.mode==='past'){
      if(state.nearby){const[x,y]=project(city().longitude,city().latitude);svg+=`<ellipse class="radius-circle" cx="${x}" cy="${y}" rx="${state.radius/73.3/2.2*690}" ry="${state.radius/111.2/1.15*450}"/>`;}
      // Agrégation seulement des collections aux coordonnées strictement identiques.
      const points=new Map();currentSites.forEach(s=>{const k=`${s.longitude},${s.latitude}`;if(!points.has(k))points.set(k,[]);points.get(k).push(s);});
      for(const sites of points.values()){
        const first=sites[0], n=sites.reduce((a,s)=>a+s.count,0),[x,y]=project(first.longitude,first.latitude), selected=sites.some(s=>filtered.some(f=>f.occurrence_id===state.selected&&f.site_id===s.site_id));
        const r=Math.min(17,4+Math.sqrt(n)*.6);
        const label=`${first.name} · ${fmt(n)} occurrences${sites.length>1?` · ${sites.length} collections au même point`:''}`;
        svg+=`<circle class="site-marker ${selected?'selected':''}" cx="${x}" cy="${y}" r="${r}" tabindex="0" role="button" data-site="${first.site_id}" data-site-ids="${sites.map(s=>s.site_id).join(',')}" aria-label="${esc(label)}"><title>${esc(label)}</title></circle>`;
      }
    }
    const vals=D.cities.map(c=>selectedSeries(c.city_code)?.summary[state.metric]).filter(Number.isFinite),vmin=Math.min(...vals),vmax=Math.max(...vals);
    D.cities.forEach(c=>{const[x,y]=project(c.longitude,c.latitude),sel=c.city_code===state.city;let color='var(--mint)',r=sel?6:3.7,label=c.name;
      if(state.mode!=='past'){const v=selectedSeries(c.city_code)?.summary[state.metric];r=sel?13:9;const t=v===undefined?0:(v-vmin)/(vmax-vmin||1);color=`hsl(${170-t*140} 68% ${63-t*5}%)`;label=`${c.name} · ${v===undefined?'indisponible':fmt(v,metrics[state.metric].digits)+' '+metrics[state.metric].unit}`;}
      svg+=`<circle class="city-marker" cx="${x}" cy="${y}" r="${r}" style="fill:${color}" data-city="${c.city_code}" tabindex="0" role="button" aria-label="${esc(label)}"><title>${esc(label)}</title></circle>`;
      if(sel||['75056','95127','77284','77288','77186','91228'].includes(c.city_code)){const dx=c.city_code==='78640'?-12:10,anchor=c.city_code==='78640'?'end':'start';svg+=`<text class="city-label ${sel?'selected':''}" x="${x+dx}" y="${y-10}" text-anchor="${anchor}">${esc(c.name)}</text>`;}
    });
    $('map').innerHTML=svg;applyView();
    if(state.mode!=='past')$('legend').innerHTML=`<span>Couleur relative aux 10 communes · ${esc(metrics[state.metric].label)}</span><span style="color:#78d8c6">${fmt(vmin,metrics[state.metric].digits)}</span><span>—</span><span style="color:#f1ae5b">${fmt(vmax,metrics[state.metric].digits)} ${esc(metrics[state.metric].unit)}</span>`;
  }
  function applyView(){$('map').setAttribute('viewBox',`${view.x} ${view.y} ${view.w} ${view.h}`);}
  function zoom(factor){const w=Math.max(140,Math.min(1100,view.w*factor)),h=w*540/760;view={x:view.x+(view.w-w)/2,y:view.y+(view.h-h)/2,w,h};applyView();}
  function focusPoint(s){const[x,y]=project(s.longitude,s.latitude);view={x:x-210,y:y-150,w:420,h:300};applyView();}
  function renderList(){
    $('result-summary').textContent=`${fmt(filtered.length)} occurrences dans votre sélection. Une occurrence relie un taxon, une collection et une publication ; ce n’est pas un nombre d’animaux.`;
    $('fossil-list').innerHTML=filtered.length?filtered.slice(0,state.limit).map(f=>{const s=siteMap[f.site_id];return`<button class="fossil-card ${state.selected===f.occurrence_id?'selected':''}" data-occurrence="${f.occurrence_id}"><span class="group">${esc(groupLabel(f.class_name))}</span><strong>${esc(f.identified_name)}</strong><small>${esc(s.name)}</small><small class="age">${age(f)}${state.nearby?' · '+fmt(distance(city(),s),1)+' km':''}</small></button>`;}).join(''):'<div class="empty">Aucune occurrence dans cette sélection. Élargissez la période ou le rayon, ou retirez un filtre. Une absence dans cette base ne prouve pas une absence passée.</div>';
    $('more').hidden=state.limit>=filtered.length;
  }
  function selectFossil(id){if(!filtered.some(f=>f.occurrence_id===id))return;state.selected=id;renderList();renderInspector();renderMap();if(innerWidth<1181)$('inspector').scrollIntoView({behavior:'smooth',block:'nearest'});}
  function renderInspector(){
    const f=filtered.find(f=>f.occurrence_id===state.selected);
    if(!f){$('inspector').innerHTML=`<p class="eyebrow">VOTRE CARNET DE VOYAGE</p><h2>Qu’y avait-il ici avant nous ?</h2><p class="muted">Cliquez sur une découverte pour connaître son âge, son milieu et la publication qui la décrit.</p><div class="detail-row"><small>Votre point de départ</small><span>${esc(city().name)}</span></div><div class="detail-row"><small>Ce que montre la carte</small><span>Des collections documentées, parfois plusieurs au même endroit.</span></div><div class="notice">Les positions sont indicatives. Ce ne sont ni des adresses de fouille ni une reconstitution exacte des anciens paysages.</div><button class="primary full" id="inspector-random" ${filtered.length?'':'disabled'}>Ouvrir une découverte</button>`;$('inspector-random').onclick=randomFossil;return;}
    const s=siteMap[f.site_id],ref=refMap[f.reference_id];
    $('inspector').innerHTML=`<p class="eyebrow">${esc(groupLabel(f.class_name))} · OCC. ${f.occurrence_id}</p><h2 class="species">${esc(f.identified_name)}</h2><span class="age-badge">Il y a ${age(f)}</span><div class="detail-row"><small>Collection / lieu déclaré</small><span>${esc(s.name)} · ${esc(s.department_code)}</span></div><div class="detail-row"><small>Âge indiqué par PBDB</small><span>${esc(f.early_name)}${f.late_name?' → '+esc(f.late_name):''}</span></div><div class="detail-row"><small>Milieu de dépôt renseigné</small><span>${esc(environments[s.environment]||s.environment||'Non renseigné')}</span></div><div class="detail-row"><small>Nom taxonomique accepté</small><span><i>${esc(f.accepted_name)}</i></span></div><div class="detail-row"><small>Distance indicative à ${esc(city().name)}</small><span>${fmt(distance(city(),s),1)} km à vol d’oiseau</span></div><details><summary>Précision de la localisation</summary><p>${esc(s.coordinate_basis||'Méthode non renseignée')} · précision source : ${esc(s.coordinate_precision||'non renseignée')}.</p>${s.geographic_comment?`<p>${esc(s.geographic_comment)}</p>`:''}</details><div class="reference"><p class="eyebrow">LA PREUVE DERRIÈRE LE POINT</p><p>${esc(ref?.citation||'')}</p><a target="_blank" rel="noopener noreferrer" href="https://paleobiodb.org/classic/basicCollectionSearch?collection_no=${s.site_id}&is_real_user=1">Collection PBDB ↗</a><br><a target="_blank" rel="noopener noreferrer" href="${esc(ref?.url||'https://paleobiodb.org/')}">Publication référencée ↗</a></div>`;
  }
  function randomFossil(){if(!filtered.length)return;const f=filtered[Math.floor(Math.random()*filtered.length)];selectFossil(f.occurrence_id);focusPoint(siteMap[f.site_id]);}
  function renderClimate(){
    const base=selectedSeries(state.city,'baseline'),future=selectedSeries(state.city,'future');const s=state.mode==='present'?base:future;
    if(!s||!base){$('stats').innerHTML=stat('—','Série incomplète');$('inspector').innerHTML='<h2>Données indisponibles</h2><p>Cette série ne contient pas toutes les années attendues. Aucun résultat n’est extrapolé.</p>';return;}
    const b=base.summary,v=s.summary;
    $('stats').innerHTML=stat(`${fmt(v.mean_c,1)}°`,'Température annuelle moyenne',state.mode==='future'?`${sign(v.mean_c-b.mean_c)} °C vs 1991–2020`:'ERA5-Land (température)')+stat(fmt(v.hot_days,1),'Jours ≥ 30 °C par an',state.mode==='future'?`${sign(v.hot_days-b.hot_days)} jours vs référence`:'Moyenne sur 30 ans')+stat(fmt(v.rain_mm),'mm de pluie par an',state.mode==='future'?`${sign((v.rain_mm/b.rain_mm-1)*100,0)} % vs référence`:'Cumul annuel moyen');
    $('map-kicker').textContent=state.mode==='present'?'RÉFÉRENCE CLIMATIQUE · 1991–2020':'PROJECTION · MOYENNE 2030–2049';$('map-title').textContent=metrics[state.metric].label;
    $('climate-title').textContent=`${city().name}, mois après mois · ${s.complete_years}/${s.expected_years} années complètes`;
    renderChart(base,state.mode==='future'?future:null);
    $('climate-table').innerHTML=`<thead><tr><th>Indicateur</th><th>1991–2020</th>${state.mode==='future'?'<th>2030–2049</th><th>Écart</th>':''}</tr></thead><tbody>${Object.entries(metrics).map(([key,m])=>`<tr><td>${esc(m.label)}</td><td>${fmt(b[key],m.digits)} ${m.unit}</td>${state.mode==='future'?`<td>${fmt(v[key],m.digits)} ${m.unit}</td><td><strong>${sign(v[key]-b[key],m.digits)}</strong></td>`:''}</tr>`).join('')}</tbody>`;
    const models=D.climate.filter(x=>x.city_code===state.city&&x.kind==='future'&&x.available);
    const deltas=models.map(x=>x.summary.mean_c-b.mean_c),lo=Math.min(...deltas),hi=Math.max(...deltas);
    $('inspector').innerHTML=state.mode==='present'?`<p class="eyebrow">LE CLIMAT DE RÉFÉRENCE</p><h2>${esc(city().name)}</h2><p class="muted">Une base de comparaison sur 30 années complètes, de 1991 à 2020.</p><div class="detail-row"><small>Jeu de données</small><span>ERA5-Seamless · température ERA5-Land, pluie ERA5 · Copernicus / ECMWF via Open-Meteo</span></div><div class="detail-row"><small>Maille renvoyée par l’API</small><span>${fmt(base.grid_latitude,3)}° N, ${fmt(base.grid_longitude,3)}° E</span></div><div class="notice">Une réanalyse combine des observations et un modèle. Elle ne mesure pas précisément chaque rue ou l’îlot de chaleur de votre quartier.</div><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noopener noreferrer">Comprendre ERA5-Land ↗</a>`:`<p class="eyebrow">CE QUE DIT LE MODÈLE</p><h2>${esc(city().name)}<br>à l’horizon 2050</h2><div class="big-number">${sign(v.mean_c-b.mean_c)}<small> °C</small></div><p class="muted">Écart de température moyenne entre 2030–2049 et la référence 1991–2020.</p><div class="detail-row"><small>Modèle sélectionné</small><span>${esc(D.models.find(x=>x.model_id===state.model)?.name)}</span></div><div class="detail-row"><small>Étendue des deux modèles</small><span>${sign(lo)} à ${sign(hi)} °C</span></div><div class="notice">Cette étendue n’est pas un intervalle de confiance. Deux modèles ne couvrent pas toute l’incertitude ; les valeurs reposent sur un forçage proche de RCP8.5.</div><a href="https://open-meteo.com/en/docs/climate-api" target="_blank" rel="noopener noreferrer">Méthode et modèles ↗</a>`;
    if(state.mode==='future'){
      $('inspector').innerHTML+=`<div class="detail-row"><small>Couverture des années</small>${models.map(x=>`<p>${esc(D.models.find(m=>m.model_id===x.model_id)?.name)} : ${x.complete_years}/${x.expected_years}${x.excluded_years?.length?` · exclusions : ${x.excluded_years.join(', ')}`:''}</p>`).join('')}</div><p class="helper">Seules les années complètes alimentent les indicateurs. La synthèse exige au moins 90 % des années ; des fenêtres effectives différentes limitent la comparaison entre modèles.</p>`;
      renderAnalogues(future);
    }
  }
  function renderChart(base,future){
    const key=state.chart==='temp'?'temp':'rain',sets=[base,...(future?[future]:[])],vals=sets.flatMap(s=>s.monthly.map(m=>m[key]));
    const low=key==='rain'?0:Math.floor(Math.min(...vals)/5)*5,high=Math.ceil((Math.max(...vals)+1)/(key==='rain'?20:5))*(key==='rain'?20:5),x=i=>52+i*61.6,y=v=>240-(v-low)/(high-low)*190;
    let svg=`<title>${esc(city().name)} : ${key==='temp'?'températures moyennes en °C':'précipitations mensuelles en mm'}</title>`;
    for(let i=0;i<=4;i++){const v=low+(high-low)*i/4,yy=y(v);svg+=`<line x1="48" y1="${yy}" x2="735" y2="${yy}" stroke="#2b3c51"/><text x="39" y="${yy+4}" text-anchor="end">${fmt(v,0)}</text>`;}
    svg+=`<text x="14" y="27">${key==='temp'?'°C':'mm'}</text>`;
    sets.forEach((s,idx)=>{const color=idx?'#f4ba78':'#6be3c4';svg+=`<path d="${s.monthly.map((m,i)=>`${i?'L':'M'}${x(i)},${y(m[key])}`).join(' ')}" fill="none" stroke="${color}" stroke-width="3"/>`;svg+=s.monthly.map((m,i)=>`<circle cx="${x(i)}" cy="${y(m[key])}" r="4" fill="${color}"><title>${monthNames[i]} · ${s.kind==='baseline'?'Référence':'Projection'} : ${fmt(m[key],1)} ${key==='temp'?'°C':'mm'}</title></circle>`).join('');});
    svg+=monthNames.map((m,i)=>`<text x="${x(i)}" y="264" text-anchor="middle">${m}</text>`).join('');
    $('climate-chart').innerHTML=svg;$('climate-chart').setAttribute('aria-label',`${city().name}, profil mensuel ${key==='temp'?'de température':'de précipitations'}. Valeurs précises dans l’export CSV.`);
    $('chart-legend').innerHTML='<span><i></i>Référence · 1991–2020</span>'+(future?'<span><i class="future"></i>Projection · 2030–2049</span>':'');
    document.querySelectorAll('[data-chart]').forEach(b=>b.classList.toggle('active',b.dataset.chart===state.chart));
  }
  function analogueRows(future){const a=D.meta.analogue;return D.climate.filter(s=>s.kind==='baseline'&&s.available).map(base=>{let sum=0;future.monthly.forEach((f,i)=>{sum+=((f.temp-base.monthly[i].temp)/a.temperature_scale_c)**2+((f.rain-base.monthly[i].rain)/a.precipitation_scale_mm)**2;});return {city_code:base.city_code,distance:Math.sqrt(sum/24)};}).sort((a,b)=>a.distance-b.distance||a.city_code.localeCompare(b.city_code));}
  function renderAnalogues(future){const rows=analogueRows(future),best=rows[0],close=best.distance<=D.meta.analogue.close_distance_max;
    $('analogue-verdict').innerHTML=close?`<strong>${esc(cityMap[best.city_code].name)}</strong> est le profil le plus proche dans cet échantillon régional (score ${fmt(best.distance,2)}). Cela ne signifie pas que les climats sont identiques.`:`<strong>Aucun analogue proche dans cet échantillon.</strong> Le moins éloigné est ${esc(cityMap[best.city_code].name)}, avec un score de ${fmt(best.distance,2)}. Le futur calculé dépasse ce que ces 10 climats de référence permettent de reproduire selon notre seuil.`;
    $('analogue-list').innerHTML=rows.map((r,i)=>`<div class="analogue"><span class="analogue-rank">${String(i+1).padStart(2,'0')}</span><div>${esc(cityMap[r.city_code].name)}${r.city_code===state.city?' <span class="muted">· même commune</span>':''}<div class="analogue-bar"><span style="width:${100/(1+r.distance)}%"></span></div></div><span class="analogue-score">${fmt(r.distance,2)}</span></div>`).join('');
  }
  function renderData(){const q=D.quality,f=q.datasets.fossils,c=q.datasets.climate_daily;
    $('data-view').innerHTML=`<div class="data-grid"><article class="data-card wide"><p class="eyebrow">DES RÉSULTATS QUE L’ON PEUT VÉRIFIER</p><h2>De l’API à votre carte</h2><div class="pipeline-steps"><span>1 · Réponses brutes horodatées</span><span>2 · Profilage & contrôles</span><span>3 · Données validées / rejets</span><span>4 · SQLite, API & dashboard</span></div><div class="stats">${stat(fmt(q.accepted_rows),'Observations retenues')}${stat('12','Tables relationnelles')}${stat(fmt(q.rules.length),'Règles de contrôle par ligne')}</div><p>Collecte conservée, empreintes SHA-256 vérifiées, données sources inchangées. Le ZIP du projet contient les scripts, les fichiers bruts, les CSV, les rejets et les preuves du rejeu.</p></article><article class="data-card"><p class="eyebrow">CE QUI EST ENTRÉ, CE QUI EST SORTI</p><h2>Rapport de qualité</h2><p class="quality-status">${esc(q.quality_status)}</p><div class="table-wrap"><table><thead><tr><th>Jeu</th><th>Entrées</th><th>Retenues</th><th>Rejetées</th></tr></thead><tbody><tr><td>Fossiles</td><td>${fmt(f.input)}</td><td>${fmt(f.accepted)}</td><td>${fmt(f.rejected)}</td></tr><tr><td>Climat · jours</td><td>${fmt(c.input)}</td><td>${fmt(c.accepted)}</td><td>${fmt(c.rejected)}</td></tr></tbody></table></div><p>${fmt(q.duplicates_removed)} doublon(s) retiré(s). Une ligne peut échouer à plusieurs règles : les compteurs ci-dessous ne s’additionnent pas en un total de lignes.</p><div class="table-wrap"><table><thead><tr><th>Règle</th><th>Échecs</th></tr></thead><tbody>${q.rules.map(r=>`<tr><td><b>${r.id}</b> · ${esc(r.condition)}</td><td>${fmt(r.failure_count)}</td></tr>`).join('')}</tbody></table></div><button id="report-download" class="secondary full">Télécharger le rapport JSON</button></article><article class="data-card"><p class="eyebrow">ATTRIBUTION & TRAÇABILITÉ</p><h2>Les sources utilisées</h2>${D.sources.map(s=>`<div class="source-line"><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.name)} ↗</a><p>${esc(s.owner)}</p><span class="tag">${esc(s.license)}</span></div>`).join('')}<h3 style="margin-top:25px">Une empreinte reproductible</h3><p>Le contenu des tables est trié puis haché. Deux exécutions sur les mêmes fichiers doivent donner exactement cette empreinte.</p><p class="mono">${esc(q.semantic_sha256)}</p><p>État affiché : ${window.CHRONOTERRE_API?'base locale via l’API du projet':'instantané pré-calculé, exploration dans votre navigateur'}. Les filtres ne déclenchent pas de nouveaux appels aux fournisseurs.</p></article><article class="data-card wide"><p class="eyebrow">LES LIMITES FONT PARTIE DU RÉSULTAT</p><h2>Ce que ChronoTerre permet de dire</h2><p>PBDB recense des occurrences publiées et saisies dans la base : ce n’est pas un inventaire exhaustif. Les localités très étudiées sont surreprésentées. Les collections ne correspondent pas nécessairement à des lieux uniques ; plusieurs séries d’échantillons peuvent partager des coordonnées.</p><p>Les contours départementaux sont généralisés à 100 m. Une localisation historique approximative près d’une limite administrative peut être mal affectée. Les coordonnées politiques et les contradictions connues sont exclues ; aucune précision manquante n’est inventée.</p><p>Les cartes du passé et du futur répondent à des questions différentes. Les fossiles n’annoncent pas le retour des espèces ni l’arrivée de la mer. Le climat de référence 1991–2020 n’est pas la météo d’aujourd’hui. Le futur désigne 2030–2049, avec deux modèles, pas toutes les trajectoires possibles.</p><p>La recherche d’analogues compare seulement 10 communes franciliennes et des profils température/pluie. Elle ne mesure ni la biodiversité, ni le confort individuel, ni les risques complets.</p></article></div>`;
    $('report-download').onclick=()=>download('rapport_chronoterre.json',JSON.stringify(q,null,2),'application/json');
  }
  function download(name,body,type){const blob=new Blob([type==='text/csv'?'\ufeff':'',body],{type:type+';charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function csv(rows){if(!rows.length)return '';const fields=Object.keys(rows[0]);const cell=x=>{let s=String(x??'');if(/^[=+@]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};return [fields.map(cell).join(';'),...rows.map(r=>fields.map(k=>cell(r[k])).join(';'))].join('\r\n');}
  function modal(content,eyebrow='MÉTHODE & LIMITES'){$('modal-eyebrow').textContent=eyebrow;$('modal-content').innerHTML=content;if(!$('modal').open)$('modal').showModal();}
  function method(){modal('<h2>Trois fenêtres sur l’Île-de-France</h2><p><b>Le passé.</b> Des occurrences paléontologiques de PBDB, liées à une collection et une publication. Le point est un lieu déclaré aux coordonnées modernes, pas la position d’un animal vivant autrefois.</p><p><b>La référence.</b> Les moyennes 1991–2020 issues de la réanalyse ERA5-Seamless (température ERA5-Land, pluie ERA5). Les indicateurs annuels ne retiennent que les années complètes.</p><p><b>Horizon 2050.</b> Les moyennes 2030–2049 de deux modèles CMIP6 HighResMIP, corrigés par Open-Meteo, sous un forçage proche de RCP8.5. Ce sont des projections climatiques, pas une prévision météo.</p><p><b>Les ressemblances.</b> Une distance température/pluie entre le futur de la commune et la référence des 10 communes franciliennes. Aucun analogue proche est une réponse possible et informative.</p><p>Les contrôles et les attributions détaillées sont dans l’onglet « Les coulisses ». L’application n’extrapole pas la présence future d’espèces à partir des fossiles.</p><button id="see-data" class="primary full">Ouvrir les sources et les contrôles</button>');$('see-data').onclick=()=>{$('modal').close();setMode('data');};}
  function makeQuiz(){
    const bases=D.climate.filter(s=>s.kind==='baseline'&&s.available).sort((a,b)=>b.summary.hot_days-a.summary.hot_days);
    const cold=bases.slice(-2),warm=bases[0];
    const sample=D.fossils.find(f=>siteMap[f.site_id].name.includes('Grignon')&&f.min_ma>33.9&&f.max_ma<=56)||D.fossils[0];
    const s=siteMap[sample.site_id];
    return [
      {question:`${sample.identified_name}, documenté à ${s.name}, a quel âge selon la source ?`,options:[age(sample),'Environ 2 000 ans','Environ 2 milliards d’années'],answer:0,explanation:`L’intervalle PBDB est ${age(sample)} (${sample.early_name}). Il décrit une incertitude de datation, pas un âge exact. Référence PBDB ${sample.reference_id}.`},
      {question:'Parmi ces communes, laquelle compte le plus de jours ≥ 30 °C par an dans la référence 1991–2020 ?',options:[cityMap[cold[0].city_code].name,cityMap[warm.city_code].name,cityMap[cold[1].city_code].name],answer:1,explanation:`${cityMap[warm.city_code].name} : ${fmt(warm.summary.hot_days,1)} jours par an dans ERA5-Seamless, contre ${fmt(cold[0].summary.hot_days,1)} et ${fmt(cold[1].summary.hot_days,1)} pour les deux autres. Il s’agit d’estimations sur une maille climatique.`},
      {question:'Un département affiche peu de fossiles dans cette base. Qu’est-ce qu’on peut en conclure ?',options:['Il n’y avait presque pas de vie','Il a toujours été sous la glace','Peu d’occurrences sont documentées dans notre extrait'],answer:2,explanation:'La base dépend des découvertes, des publications et de leur saisie. Une faible couverture n’est pas une mesure de l’abondance ancienne des êtres vivants.'},
      {question:'Le plus proche « jumeau » a un score supérieur à 1. Comment afficher ce résultat ?',options:['Aucun analogue proche parmi nos 10 communes','Ces deux climats sont identiques','Cette commune aura exactement le même temps'],answer:0,explanation:'Le meilleur candidat peut rester éloigné. Le seuil 1 est un choix pédagogique de notre méthode, pas une certification scientifique.'}
    ];
  }
  function showQuiz(){
    if(quiz.index>=quiz.questions.length){modal(`<p class="quiz-progress">EXPLORATION TERMINÉE</p><h2>${quiz.score} / ${quiz.questions.length} · Votre regard a changé.</h2><p>La bonne question compte autant que le chiffre. Continuez la carte pour retrouver les sources derrière les réponses.</p><button id="quiz-restart" class="primary full">Rejouer</button>`,'LE DÉFI CHRONOTERRE');$('quiz-restart').onclick=startQuiz;return;}
    const q=quiz.questions[quiz.index];quiz.answered=false;
    modal(`<p class="quiz-progress">Question ${quiz.index+1} / ${quiz.questions.length} · ${quiz.score} bonne(s) réponse(s)</p><h2>${esc(q.question)}</h2><div class="quiz-choices">${q.options.map((o,i)=>`<button class="secondary" data-answer="${i}">${esc(o)}</button>`).join('')}</div><div id="quiz-feedback" aria-live="polite"></div><button id="quiz-next" class="primary full" hidden>${quiz.index===quiz.questions.length-1?'Voir mon résultat':'Question suivante'}</button>`,'LE DÉFI CHRONOTERRE');
    $('modal-content').querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{if(quiz.answered)return;quiz.answered=true;const correct=Number(b.dataset.answer)===q.answer;if(correct)quiz.score++;
      $('modal-content').querySelectorAll('[data-answer]').forEach(x=>{x.disabled=true;if(Number(x.dataset.answer)===q.answer)x.classList.add('correct');});if(!correct)b.classList.add('wrong');$('quiz-feedback').innerHTML=`<div class="notice"><strong>${correct?'Bien vu.':'Regardons les données.'}</strong> ${esc(q.explanation)}</div>`;$('quiz-next').hidden=false;});
    $('quiz-next').onclick=()=>{quiz.index++;showQuiz();};
  }
  function startQuiz(){quiz={index:0,score:0,answered:false,questions:makeQuiz()};showQuiz();}
  function setMode(mode){if(!['past','present','future','data'].includes(mode))throw Error('Mode inconnu');state.mode=mode;try{history.replaceState(null,'','#'+mode);}catch{}render();}
  function reset(){Object.assign(state,{department:'',group:'',search:'',young:0,old:150,nearby:false,radius:30,selected:null,limit:12});$('period').value='all';view={x:0,y:0,w:760,h:540};render();}
  function registerWebMCP(){
    const registry=document.modelContext;if(!registry?.registerTool)return;
    const lifecycle=new AbortController();addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
    const tools=[{name:'read_chronoterre_state',description:'Lire la sélection et les comptes affichés dans ChronoTerre.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true},execute:()=>({mode:state.mode,city:state.city,model:state.model,visible_fossil_occurrences:filtered.length})},
      {name:'configure_chronoterre_exploration',description:'Changer le mode, la commune et éventuellement le modèle du dashboard visible.',inputSchema:{type:'object',properties:{mode:{type:'string',enum:['past','present','future','data']},city_code:{type:'string'},model:{type:'string',enum:['MRI_AGCM3_2_S','EC_Earth3P_HR']}},required:['mode','city_code'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{if(!input||!['past','present','future','data'].includes(input.mode)||!cityMap[input.city_code]||(input.model&&!D.models.some(m=>m.kind==='projection'&&m.model_id===input.model)))throw Error('Sélection invalide');state.city=input.city_code;if(input.model)state.model=input.model;setMode(input.mode);return{mode:state.mode,city:state.city,model:state.model};}}];
    for(const tool of tools){try{Promise.resolve(registry.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{});}catch{}}
  }
  function bind(){
    addEventListener('hashchange',()=>{const m=location.hash.slice(1);if(['past','present','future','data'].includes(m)&&m!==state.mode)setMode(m);});
    $('mobile-filters').onclick=()=>{const open=document.querySelector('.filters').classList.toggle('expanded');$('mobile-filters').setAttribute('aria-expanded',String(open));$('mobile-filters').textContent=open?'Masquer les filtres':'Afficher les filtres';};
    document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));
    $('city').onchange=e=>{state.city=e.target.value;render();};$('department').onchange=e=>{state.department=e.target.value;state.limit=12;render();};$('taxon-class').onchange=e=>{state.group=e.target.value;state.limit=12;render();};
    $('search').oninput=e=>{state.search=e.target.value;state.limit=12;render();};
    $('period').onchange=e=>{const [a,b]=e.target.value==='all'?[0,150]:e.target.value.split(',').map(Number);state.young=a;state.old=b;state.limit=12;render();};
    $('age-young').oninput=e=>{state.young=Math.min(Number(e.target.value),state.old);$('period').value='all';render();};$('age-old').oninput=e=>{state.old=Math.max(Number(e.target.value),state.young);$('period').value='all';render();};
    $('nearby').onchange=e=>{state.nearby=e.target.checked;render();};$('radius').oninput=e=>{state.radius=Number(e.target.value);render();};
    $('reset').onclick=reset;$('random').onclick=randomFossil;$('more').onclick=()=>{state.limit+=12;renderList();};
    $('model').onchange=e=>{state.model=e.target.value;render();};$('metric').onchange=e=>{state.metric=e.target.value;render();};document.querySelectorAll('[data-chart]').forEach(b=>b.onclick=()=>{state.chart=b.dataset.chart;renderClimate();});
    $('fossil-list').onclick=e=>{const b=e.target.closest('[data-occurrence]');if(b)selectFossil(Number(b.dataset.occurrence));};
    $('zoom-in').onclick=()=>zoom(.75);$('zoom-out').onclick=()=>zoom(1.3);$('map-reset').onclick=()=>{view={x:0,y:0,w:760,h:540};applyView();};
    let drag=null,moved=false;
    $('map').onpointerdown=e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,v:{...view}};moved=false;};
    $('map').onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>5)moved=true;if(moved){view.x=drag.v.x-dx/$('map').clientWidth*view.w;view.y=drag.v.y-dy/$('map').clientHeight*view.h;applyView();}};
    addEventListener('pointerup',()=>{drag=null;});$('map').onpointerleave=()=>{drag=null;};
    $('map').onclick=e=>{if(moved)return;const el=e.target.closest('[data-site],[data-city],[data-dept]');if(!el)return;if(el.dataset.city){state.city=el.dataset.city;render();}else if(el.dataset.site){const ids=el.dataset.siteIds.split(',').map(Number),f=filtered.find(x=>ids.includes(x.site_id));if(f)selectFossil(f.occurrence_id);}else if(state.mode==='past'){state.department=state.department===el.dataset.dept?'':el.dataset.dept;state.limit=12;render();}};
    $('map').onkeydown=e=>{if(['Enter',' '].includes(e.key)&&e.target.matches('[role=button]')){e.preventDefault();moved=false;e.target.dispatchEvent(new MouseEvent('click',{bubbles:true}));return;}const step=view.w*.08;if(['+','=','-','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();if(e.key==='+'||e.key==='=')zoom(.75);if(e.key==='-')zoom(1.3);if(e.key==='ArrowLeft')view.x-=step;if(e.key==='ArrowRight')view.x+=step;if(e.key==='ArrowUp')view.y-=step;if(e.key==='ArrowDown')view.y+=step;applyView();}};
    $('map').addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey){e.preventDefault();zoom(e.deltaY>0?1.12:.9);}},{passive:false});
    $('export-fossils').onclick=()=>download('chronoterre_fossiles_selection.csv',csv(filtered.map(f=>({...f,site_name:siteMap[f.site_id].name,department:siteMap[f.site_id].department_code,latitude:siteMap[f.site_id].latitude,longitude:siteMap[f.site_id].longitude,citation:refMap[f.reference_id]?.citation}))), 'text/csv');
    $('export-climate').onclick=()=>{const base=selectedSeries(state.city,'baseline'),future=selectedSeries(state.city,'future');const rows=base.monthly.map((m,i)=>({commune:city().name,mois:m.month,annees_reference:base.complete_years,temperature_reference_c:m.temp,pluie_reference_mm:m.rain,...(state.mode==='future'?{modele:state.model,annees_projection:future.complete_years,annees_exclues:future.excluded_years.join('|'),temperature_2030_2049_c:future.monthly[i].temp,pluie_2030_2049_mm:future.monthly[i].rain}:{})}));download('chronoterre_climat_mensuel.csv',csv(rows),'text/csv');};
    $('method-button').onclick=method;$('footer-method').onclick=method;$('quiz-open').onclick=startQuiz;$('close-modal').onclick=()=>$('modal').close();$('modal').onclick=e=>{if(e.target===$('modal')){const r=$('modal').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('modal').close();}};
  }
  async function boot(){
    D=window.CHRONOTERRE_DATA;if(!D)throw Error('Les données sont absentes. Conservez le dossier dist complet ou relancez le pipeline.');
    let live=false;if(window.CHRONOTERRE_API){try{const r=await fetch(window.CHRONOTERRE_API+'/bootstrap');if(!r.ok)throw Error('API indisponible');D=await r.json();live=true;}catch{window.CHRONOTERRE_API=null;}}
    siteMap=Object.fromEntries(D.sites.map(s=>[s.site_id,s]));cityMap=Object.fromEntries(D.cities.map(c=>[c.city_code,c]));refMap=Object.fromEntries(D.references.map(r=>[r.reference_id,r]));
    $('city').innerHTML=D.cities.map(c=>option(c.city_code,c.name)).join('');$('model').innerHTML=D.models.filter(m=>m.kind==='projection').map(m=>option(m.model_id,m.name)).join('');
    $('department').innerHTML=option('','Toute l’Île-de-France')+D.departments.features.map(f=>option(f.properties.code,f.properties.code+' · '+f.properties.nom)).join('');
    $('taxon-class').innerHTML=option('','Tous les groupes')+[...new Set(D.fossils.map(f=>f.class_name).filter(Boolean))].sort().map(c=>option(c,groupLabel(c))).join('')+(D.fossils.some(f=>!f.class_name)?option('__missing__','Classe non renseignée'):'');
    $('snapshot').innerHTML=`Données collectées le ${esc(new Date(D.quality.raw_files.find(f=>f.key==='occurrences').fetched_at).toLocaleDateString('fr-FR'))}<br>${live?'API locale connectée · SQLite':'Instantané vérifié · exploration hors ligne possible'}`;
    const hash=location.hash.slice(1);if(['past','present','future','data'].includes(hash))state.mode=hash;
    bind();render();registerWebMCP();
  }
  boot().catch(e=>{$('app-error').hidden=false;$('app-error').textContent=e.message;$('explorer').hidden=true;$('snapshot').textContent='Chargement interrompu';console.error(e);});
})();
