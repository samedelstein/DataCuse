"""Check city clipping, distance bounds, and endpoint tolerance sensitivity."""
import json
from pathlib import Path
from calculate import run

ROOT=Path(__file__).resolve().parent
baseline=json.loads((ROOT/'results.json').read_text())
checks=[]
for tolerance in [0,1]:
    r=run(tolerance,save=False)
    assert r['names']==baseline['names']==1192
    assert r['longest_names'][0]['name']==baseline['longest_names'][0]['name']
    assert r['longest_segments'][0]['source_id']=='477433624'
    assert abs(r['longest_segments'][0]['inside_ft']-baseline['longest_segments'][0]['inside_ft'])<.001
    salina=r['reviews']['SOUTH SALINA STREET'];erie=r['reviews']['ERIE BOULEVARD EAST']
    assert salina['components']==1
    # At 1 m a real 0.974 m boundary piece contracts to a self-loop. The raw
    # union length is unchanged; quantify this instead of claiming exact topology stability.
    path_difference_m=abs(salina['total_miles']-salina['graph_diameter_miles'])*1609.344
    assert path_difference_m < 1.0
    if tolerance==0:
        assert salina['cycles']==0 and path_difference_m<1e-5
    assert abs(salina['total_miles']-baseline['reviews']['SOUTH SALINA STREET']['total_miles'])<1e-8
    # Exact clipping adds near-duplicate nodes under zero snapping; compare distances, not node counts.
    assert len(erie['corridor_paths'])>=2
    assert all(3.55<p['miles']<3.60 for p in erie['corridor_paths'])
    assert abs(max(p['miles'] for p in erie['corridor_paths'])-max(p['miles'] for p in baseline['reviews']['ERIE BOULEVARD EAST']['corridor_paths']))<.001
    # Every other name's entire mapped sum is below Salina, even before correcting splits.
    assert max(x['total_miles'] for x in r['total_ranking'] if x['name'] not in ['SOUTH SALINA STREET','ERIE BOULEVARD EAST'])<salina['total_miles']
    assert salina['boundary_distances_m'][0] <= tolerance+.01
    checks.append(dict(tolerance_m=tolerance,names=r['names'],segment_ft=r['longest_segments'][0]['inside_ft'],salina_miles=salina['total_miles'],salina_path_difference_m=path_difference_m,salina_graph_cycles=salina['cycles'],erie_path_miles=[p['miles'] for p in erie['corridor_paths']]))
(ROOT/'validation.json').write_text(json.dumps(dict(passed=True,checks=checks,notes='Recomputes from source; noding conserves line length. Distances are map estimates, not field surveys.'),indent=2))
print(json.dumps(checks,indent=2))
