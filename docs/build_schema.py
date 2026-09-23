"""Régénère le diagramme relationnel (matplotlib, dépendance facultative)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
navy='#13283e';teal='#007e76';muted='#52667c';blue='#eaf3f8';gold='#fff3df'
fig,ax=plt.subplots(figsize=(14,11));ax.set_xlim(0,14);ax.set_ylim(0,11);ax.axis('off')
def box(x,y,w,h,title,body,color=blue):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.025,rounding_size=0.1',facecolor=color,edgecolor='#9eb6c6',linewidth=1.15,zorder=3))
 ax.text(x+.15,y+h-.24,title,fontsize=12,weight='bold',color=navy,va='top',zorder=4)
 ax.text(x+.15,y+h-.62,body,fontsize=10,color=muted,va='top',linespacing=1.55,zorder=4)
def arrow(a,b,label='',rad=0):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,color=teal,linewidth=1.5,connectionstyle=f'arc3,rad={rad}',zorder=2))
 if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.08,label,fontsize=9,color=teal,ha='center',backgroundcolor='white')
ax.text(.2,10.65,'ChronoTerre — modèle relationnel (12 tables)',fontsize=20,weight='bold',color=navy)
box(.2,8.6,3.1,1.5,'source','PK source_id\nNom, producteur, licence')
box(4.15,8.6,4.05,1.5,'raw_file','PK raw_id · FK source_id\nURL, date UTC, SHA-256, chemin')
arrow((3.3,9.35),(4.15,9.35),'1 → N')
ax.text(8.8,9.6,'PROVENANCE COMMUNE',fontsize=11,weight='bold',color=teal)
ax.text(8.8,8.85,'FK raw_id dans department, city,\nfossil_site, fossil_occurrence,\nclimate_series.',fontsize=10,color=muted,linespacing=1.5)
box(.2,6.3,3.1,1.5,'bibliography','PK reference_id\nCitation, lien PBDB')
box(3.95,6.3,3.1,1.5,'geo_interval','PK interval_id\nLibellés, max_ma, min_ma')
box(7.7,6.3,2.7,1.5,'department','PK department_code\nRégion = 11')
box(11,6.3,2.75,1.5,'city','PK city_code\nFK department_code')
box(.2,3.75,3.1,1.6,'taxon','PK taxon_id\nNom accepté, rang\nClasse, famille')
box(3.95,3.75,3.1,1.6,'fossil_occurrence','PK occurrence_id\nFK site, taxon, reference,\ninterval + raw_id',gold)
box(7.7,3.75,2.7,1.6,'climate_series','PK series_id\nFK city, model, raw\nPériode et maille',gold)
box(11,3.75,2.75,1.6,'climate_model','PK model_id\nType, institution\nForçage / scénario')
box(3.95,1.1,3.1,1.6,'fossil_site','PK site_id (= collection)\nFK department, raw\nCoordonnées et milieu')
box(7.7,1.1,2.7,1.6,'climate_day','PK (series_id, date)\nFK series_id\nTmin, Tmoy, Tmax, pluie')
arrow((1.8,6.3),(4.5,5.35),'1 → N',.06);arrow((5.5,6.3),(5.5,5.35),'1 → N');arrow((3.3,4.55),(3.95,4.55),'1 → N');arrow((5.5,2.7),(5.5,3.75),'1 → N');arrow((10.4,7.05),(11,7.05),'1 → N');arrow((12.4,6.3),(9.5,5.35),'1 → N',-.06);arrow((11,4.55),(10.4,4.55),'1 → N');arrow((9.05,3.75),(9.05,2.7),'1 → N')
# Corridor entre les deux branches : aucun trait ne traverse une entité.
ax.plot([7.7,7.38,7.38],[7.0,7.0,1.8],color=teal,lw=1.5,zorder=2)
arrow((7.38,1.8),(7.05,1.8))
ax.text(7.4,3.1,'1 → N',rotation=90,fontsize=9,color=teal,ha='center',backgroundcolor='white')
ax.text(.2,.3,'Flèches : parent 1 → enfant N. Les FK de provenance sont rappelées en haut pour préserver la lisibilité.\nDeux vues analytiques : v_fossils et v_climate_annual. Définition complète et contraintes : sql/schema.sql.',fontsize=11,color=muted,linespacing=1.6)
fig.savefig(Path(__file__).with_name('schema.png'),dpi=190,bbox_inches='tight',facecolor='white')
