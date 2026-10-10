// Tests de logique/DOM avec jsdom, explicitement PAS un navigateur ni un test WebGL.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {JSDOM}=require(process.env.JSDOM_PATH||'jsdom');const root=path.resolve(__dirname,'..'),events=[];
const dom=new JSDOM(fs.readFileSync(path.join(root,'dist/index.html'),'utf8'),{url:'http://localhost/',runScripts:'outside-only'}),w=dom.window;
w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
w.fetch=async url=>{if(!String(url).startsWith('data/'))throw Error('Fournisseur volontairement indisponible dans ce test');const p=path.join(root,'dist',url);return{ok:fs.existsSync(p),status:fs.existsSync(p)?200:404,headers:{get:()=> String(url).endsWith('.geojson')?'application/octet-stream':'application/json'},json:async()=>JSON.parse(fs.readFileSync(p,'utf8'))};};w.AbortSignal=AbortSignal;w.AbortController=AbortController;w.console.error=(...x)=>events.push(x.join(' '));w.eval(fs.readFileSync(path.join(root,'dist/app.js'),'utf8')+'\nwindow.testAPI={selectCity,search,showSite,getJSON};');
const wait=async()=>{for(let i=0;i<100;i++){if(w.document.querySelector('h1'))return;await new Promise(r=>setTimeout(r,20));}throw Error('Initialisation sans fiche');};const text=()=>w.document.body.textContent;
(async()=>{const results=[];await wait();assert(text().includes('La Rochelle'));results.push('Initialisation avec vrais instantanés, GeoJSON servi en octet-stream et WebGL indisponible');
let before=w.document.querySelector('.hero-stat .number').textContent;w.document.querySelector('[data-h="2100"]').click();assert.notEqual(w.document.querySelector('.hero-stat .number').textContent,before);assert(w.document.querySelector('#plus50').disabled);results.push('Horizon modifie valeurs ; 2076 désactivé');
await w.testAPI.selectCity('2A004',false);assert(text().includes('Ajaccio'));w.document.querySelector('#add-compare').click();await w.testAPI.selectCity('17300',false);w.document.querySelector('#add-compare').click();w.document.querySelector('#compare').click();assert(w.document.querySelector('#dialog').textContent.includes('Ajaccio'));let p=w.document.querySelector('#priority');p.value='heat';p.dispatchEvent(new w.Event('change'));assert.equal(w.document.querySelector('#priority').value,'heat');assert.equal(w.document.querySelectorAll('tr[data-family]').length,2);results.push('Comparaison et priorité persistante');
w.document.querySelector('#dialog-close').click();await w.testAPI.selectCity('97411',false);assert(text().includes('Réunion'));results.push('Domaine outre-mer explicite');
await w.testAPI.search('17000');assert(w.document.querySelector('#search-results').textContent.includes('La Rochelle'));results.push('Code postal, résultat INSEE');
await w.testAPI.search('12 rue adresse fictive pour test');assert(w.document.querySelector('#search-note').textContent.includes('indisponibles'));results.push('Erreur géocodeur : recherche communale conservée');
const media=JSON.parse(fs.readFileSync(path.join(root,'dist/data/media.json')));let taxon=media.links[0].taxon_id;const meta=JSON.parse(fs.readFileSync(path.join(root,'dist/data/meta.json')));let row;
for(const d of meta.fossil_departments){row=JSON.parse(fs.readFileSync(path.join(root,'dist/data/fossils',d+'.json'))).find(r=>r[2]===taxon);if(row)break;}
assert(row);await w.testAPI.showSite(row[1],false);assert(w.document.querySelector('#place-panel img'));assert(text().includes('Reconstitution')||text().includes('fossile'));results.push('Fiche fossilifère avec illustration taxonomique et crédits');
const savedFetch=w.fetch;
for(const mime of ['application/octet-stream','text/plain','']){
 w.fetch=async()=>({ok:true,headers:{get:()=>mime},json:async()=>({type:'FeatureCollection',features:[]})});
 assert.equal((await w.testAPI.getJSON('data/test.geojson',1000,true)).type,'FeatureCollection');
}
w.fetch=async()=>({ok:true,headers:{get:()=> 'text/html'},json:async()=>({})});
await assert.rejects(()=>w.testAPI.getJSON('data/test.json',1000,true),/page HTML/);
w.fetch=async()=>({ok:true,headers:{get:()=> 'application/octet-stream'},json:async()=>({})});
await assert.rejects(()=>w.testAPI.getJSON('https://example.org/api',1000),/fournisseur inattendue/);
w.fetch=async()=>({ok:true,headers:{get:()=> 'application/json'},json:async()=>{throw new SyntaxError('invalid');}});
await assert.rejects(()=>w.testAPI.getJSON('data/test.json',1000,true),/JSON illisibles/);
w.fetch=savedFetch;
results.push('Types MIME statiques génériques acceptés ; HTML, JSON invalide et fournisseur non JSON refusés');
assert.equal(events.length,0,events.join('\n'));fs.writeFileSync(path.join(root,'reports/front_dom.json'),JSON.stringify({at:new Date().toISOString(),status:'PASS',tests:results,limits:'jsdom : aucun rendu graphique, réseau externe ni interaction réelle navigateur vérifiés'},null,2));console.log(results.join('\n'));dom.window.close();})().catch(e=>{console.error(e);dom.window.close();process.exitCode=1;});
