/* Pure preference engine: no scientific habitability score. Node and browser. */
(function(root){
'use strict';
const metrics=[
 {id:'S1',label:'Jours très chauds',detail:'Seuil 35 °C du producteur',unit:'j/an',limit:10,max:120,weight:2},
 {id:'S2',label:'Nuits chaudes',detail:'Seuil 20 °C du producteur',unit:'nuits/an',limit:20,max:180,weight:3},
 {id:'G2',label:'Jours de gel',detail:'Minimum quotidien < 0 °C',unit:'j/an',limit:40,max:200,weight:1},
 {id:'G4',label:'Jours de pluie en été',detail:'Précipitations > 1 mm / jour',unit:'j/été',limit:25,max:92,weight:1},
 {id:'AG1',label:'Plus longue séquence sèche en été',detail:'Jours consécutifs avec pluie < 1 mm',unit:'jours',limit:30,max:92,weight:1}
];
const labels=['Dans tous tes seuils','Des compromis','Plus éloigné de tes critères','Données insuffisantes'];
function defaults(){return metrics.map(m=>({limit:m.limit,weight:m.weight}));}
function valid(p){return Array.isArray(p)&&p.length===metrics.length&&p.every((x,i)=>x&&Number.isFinite(x.limit)&&x.limit>=0&&x.limit<=metrics[i].max&&Number.isInteger(x.weight)&&x.weight>=0&&x.weight<=3)&&p.some(x=>x.weight>0);}
function evaluate(row,prefs,band=0){
 if(!valid(prefs))throw Error('Active au moins un critère et vérifie les seuils.');
 let total=0,matched=0,loss=0,missing=0;const details=[];
 prefs.forEach((p,i)=>{if(!p.weight)return;const v=row?.[i+1]?.[band];total++;if(!Number.isFinite(v)){missing++;details.push({id:metrics[i].id,value:null,pass:null});return;}const excess=Math.max(0,v-p.limit)/Math.max(1,p.limit);if(v<=p.limit)matched++;loss+=p.weight*excess;details.push({id:metrics[i].id,value:v,pass:v<=p.limit,limit:p.limit,weight:p.weight,excess});});
 const category=missing?3:matched===total?0:matched>=Math.ceil(total/2)?1:2;
 return {category,label:labels[category],total,matched,missing,loss:missing?null:loss,details};
}
function sensitivity(row,prefs,horizon){if(horizon==='ref')return {label:'Référence historique',categories:[]};const lo=evaluate(row,prefs,1),hi=evaluate(row,prefs,2);if(lo.missing||hi.missing)return {label:'Bornes incomplètes',categories:[]};return {label:lo.category===hi.category?'Catégorie inchangée dans les bornes publiées':'Catégorie sensible aux bornes publiées',categories:[lo.category,hi.category]};}
function compare(a,b,reverse=false){if(a.fit.missing!==b.fit.missing)return a.fit.missing?1:-1;const sign=reverse?-1:1;return sign*(a.fit.category-b.fit.category||((a.fit.loss??0)-(b.fit.loss??0)))||a.city.name.localeCompare(b.city.name,'fr')||a.city.code.localeCompare(b.city.code);}
const api={metrics,labels,defaults,valid,evaluate,sensitivity,compare};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.HomeEngine=api;
})(typeof window==='undefined'?globalThis:window);
