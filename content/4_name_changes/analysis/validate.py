"""Check the actual ranking at alternate snapping tolerances."""
import json
from collections import Counter
import calculate as c
checks=[]
for tolerance in (0,1):
    b,roads,excluded,ambiguous=c.prepare(tolerance)
    ranked,cycles=c.trace(roads)
    winners=[x for x in ranked if x['changes']==ranked[0]['changes']]
    checks.append(dict(tolerance_m=tolerance,max_changes=ranked[0]['changes'],winners=[c.brief(x) for x in winners],edges=len(roads)))
    assert ranked[0]['changes']==4
    assert {tuple(x['names']) for x in winners}=={tuple(x['names']) for x in json.loads((c.ROOT/'results.json').read_text())['top'][:2]}
    for chain in ranked:
        assert chain['changes']==len(chain['names'])-1
        assert chain['max_join_angle']<=30
        assert len(chain['sequence'])==len({i for i,s in chain['sequence']})
(c.ROOT/'validation.json').write_text(json.dumps(dict(passed=True,checks=checks),indent=2))
print('Passed: both tied leaders survive 0 m and 1 m endpoint tolerance; all joins <=30 degrees; no repeated edges.')
