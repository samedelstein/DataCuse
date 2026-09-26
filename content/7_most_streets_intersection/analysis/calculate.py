"""Rank same-level named public street nodes; preserve arms and name counts."""
import sys,json,math,csv,hashlib,importlib.util
from pathlib import Path
from collections import Counter
from shapely.geometry import Point,mapping
R=Path(__file__).resolve().parent
SOURCE=R.parents[1]/'4_name_changes/analysis'
spec=importlib.util.spec_from_file_location('prior_network',SOURCE/'street_network.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
boundary,original,excluded=n.load()
outputs={};all_top=[]
for tolerance in [0,1,3,5,10,20]:
 roads,ambiguous=n.node_network(original,tolerance);graph=n.endpoint_graph(roads,tolerance);rows=[]
 for node in graph.nodes:
  incident=[];positions=[]
  for _,_,key,data in graph.edges(node,keys=True,data=True):
   r=roads[data['index']]
   if r['nodes'][0]==r['nodes'][1]:continue # Internal collapsed links are not outward arms.
   for end,u in enumerate(r['nodes']):
    if u!=node:continue
    coords=list(r['geo'].coords);p=coords[0 if end==0 else -1];positions.append(p)
    dist=min(20,r['geo'].length/2);q=r['geo'].interpolate(dist if end==0 else r['geo'].length-dist)
    bearing=math.degrees(math.atan2(q.x-p[0],q.y-p[1]))%360
    incident.append({'id':r['id'],'name':r['name'],'edge':data['index'],'end':end,'bearing':bearing,'length_m':r['geo'].length,'z':r['z0' if end==0 else 'z1']})
  if not positions:continue
  x=sum(p[0] for p in positions)/len(positions);y=sum(p[1] for p in positions)/len(positions)
  if not boundary.covers(Point(x,y)):continue
  names=sorted({a['name'] for a in incident});arms=len(incident)
  if arms<3:continue
  lon,lat=n.UNPROJECT(x,y);row={'node':node,'longitude':lon,'latitude':lat,'x':x,'y':y,'arms':arms,'name_count':len(names),'names':names,'incident':incident,'cluster_diameter_m':max(math.dist(a,b) for a in positions for b in positions)};rows.append(row)
 rows.sort(key=lambda r:(-r['name_count'],-r['arms'],r['latitude'],r['longitude']))
 outputs[str(tolerance)]={'intersection_nodes':len(rows),'max_names':max(r['name_count'] for r in rows),'max_arms':max(r['arms'] for r in rows),'distribution':dict(Counter(str((r['name_count'],r['arms'])) for r in rows)),'ambiguous_crossings':ambiguous,'candidates':[r for r in rows if r['name_count']>=4 or r['arms']>=5]}
 if tolerance==1:
  (R/'node_rankings.json').write_text(json.dumps(rows,indent=2))
  features=[{'type':'Feature','geometry':mapping(n.transform(n.UNPROJECT,r['geo'])),'properties':{k:r[k] for k in ['name','id','z0','z1','fcc','jurisdiction','nodes']}} for r in roads]
  (R/'eligible_noded_roads.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':')))
 print('TOLERANCE',tolerance,'nodes',len(rows),'max names',outputs[str(tolerance)]['max_names'],'max arms',outputs[str(tolerance)]['max_arms'],flush=True)
 for r in rows[:12]:print(r['name_count'],r['arms'],r['latitude'],r['longitude'],r['names'],flush=True)
(R/'sensitivity.json').write_text(json.dumps(outputs,indent=2))
provenance={'inputs':{str(p.relative_to(R.parents[2])):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [SOURCE/'streets_nys_current.geojson',SOURCE/'syracuse_boundary.geojson',SOURCE/'street_network.py',SOURCE/'streets_city_reference.geojson']},'snapshot_date':'2026-09-19','primary_tolerance_metres':1,'eligible_input_parts':len(original),'excluded':dict(excluded),'projection':'EPSG:26918','source_provenance':json.loads((SOURCE/'nys_provenance.json').read_text())}
(R/'provenance.json').write_text(json.dumps(provenance,indent=2))

