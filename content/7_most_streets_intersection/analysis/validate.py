"""Independent endpoint-only ranking and evidence assertions."""
import json,math,importlib.util
from pathlib import Path
from collections import defaultdict,Counter
from shapely.geometry import Point
R=Path(__file__).resolve().parent;S=R.parents[1]/'4_name_changes/analysis'
spec=importlib.util.spec_from_file_location('network',S/'street_network.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);boundary,roads,excluded=n.load()
ends=defaultdict(list)
for r in roads:
 for end,z in [(0,r['z0']),(-1,r['z1'])]:
  x,y=r['geo'].coords[end];ends[(round(x,5),round(y,5),z)].append({'id':r['id'],'name':r['name']})
rows=[]
for (x,y,z),arms in ends.items():
 if not boundary.covers(Point(x,y)) or len(arms)<3:continue
 rows.append({'x':x,'y':y,'z':z,'arms':len(arms),'names':sorted({a['name'] for a in arms})})
rank=json.loads((R/'node_rankings.json').read_text());six=next(r for r in rank if r['names']==['KIRKPATRICK STREET','LODI STREET','NORTH SALINA STREET'] and r['arms']==6);seven=next(r for r in rank if r['arms']==7)
assert max(r['arms'] for r in rows)==7
assert max(len(r['names']) for r in rows)==4
for row in [six,seven]:
 match=min(rows,key=lambda r:math.hypot(r['x']-row['x'],r['y']-row['y']));assert math.hypot(match['x']-row['x'],match['y']-row['y'])<0.001;assert match['names']==row['names'] and match['arms']==row['arms']
city=json.loads((R/'city_crosscheck.json').read_text());assert max(r['arms'] for r in city['top'])==6;assert [r for r in city['top'] if r['arms']==6][0]['node']==661
sens=json.loads((R/'sensitivity.json').read_text())
for tol in ('0','1','3','5'):
 high=[r for r in sens[tol]['candidates'] if r['arms']>=6];assert len(high)==2
 assert max(r['name_count'] for r in sens[tol]['candidates'])==4
result={'endpoint_only_intersections':len(rows),'endpoint_only_max_lines':max(r['arms'] for r in rows),'endpoint_only_max_names':4,'six_way_exact_endpoints_agree':True,'city_six_way_agrees':True,'stable_top_two_from_0_through_5_metres':True,'z_level_endpoint_counts':dict(Counter(str(r[z]) for r in roads for z in ('z0','z1'))),'strict_graph_intersections':len(rank),'name_leaders':sum(r['name_count']==4 for r in rank),'manual_review':{'six_way':{'node':six['node'],'approaches':6,'names':3,'basis':'2022 NYS imagery plus independent city node 661; six separate corridors'},'seven_line':{'node':seven['node'],'source_lines':7,'approaches':4,'names':4,'basis':'2022 imagery and city node 389: pairs of Hiawatha East, Hiawatha West and North Salina lines each represent one approach; Lodi is single'},'four_name_candidates':'All five primary leaders inspected in 2022 aerial imagery. City names agree at four; Seymour/Shonnard/West Adams/West Onondaga differs in older city topology.'}}
(R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
(R/'results.json').write_text(json.dumps({'six_way':six,'seven_line':seven,'four_name_leaders':[r for r in rank if r['name_count']==4],'interpretation':'Six distinct surface-street approaches at North Salina/Lodi/Kirkpatrick is the clearest reviewed winner under a single-junction definition. Full street names instead top out at four, with ties. Wide clustering is not accepted as a count of one junction.','reviewed_approaches':result['manual_review']},indent=2))
