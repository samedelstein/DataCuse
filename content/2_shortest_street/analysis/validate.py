"""Meaningful checks: split conservation, grade separation and ranking sensitivity."""
import json
from shapely.geometry import LineString
from calculate import ROOT,node_network,calculate

cross=[dict(id='a',geo=LineString([(0,0),(10,0)]),z0=0,z1=0),dict(id='b',geo=LineString([(5,-5),(5,5)]),z0=0,z1=0)]
noded,audit=node_network(cross,0)
assert len(noded)==4 and abs(sum(r['geo'].length for r in noded)-20)<1e-9
cross[1]['z0']=cross[1]['z1']=1
noded,audit=node_network(cross,0)
assert len(noded)==2, 'A grade-separated crossing must not be split'
summaries=[]
for tolerance in (0,.5,1):
    r=calculate(tolerance,save=tolerance==.5)
    summaries.append(dict(tolerance_m=tolerance,eligible_names=r['eligible_names'],suffix_longer=r['suffix_longer'],
        shortest_block=r['blocks'][0],shortest_whole_street=r['whole_streets'][0],
        noded_pieces=r['noded_pieces'],ambiguous_grade_crossings=r['ambiguous_grade_crossings']))
    print('Completed tolerance',tolerance,flush=True)
assert len({s['shortest_block']['name'] for s in summaries})==1
assert len({s['shortest_whole_street']['name'] for s in summaries})==1
assert len({s['eligible_names'] for s in summaries})==1
(ROOT/'validation.json').write_text(json.dumps(dict(synthetic_tests='passed',sensitivity=summaries),indent=2))
print(json.dumps(summaries,indent=2))
