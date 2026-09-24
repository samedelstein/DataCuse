"""Trace mutually straightest street chains; all source inputs are local."""
import math
import json
import hashlib
from collections import defaultdict
from shapely.geometry import Point, mapping
from shapely.ops import transform
import street_network as sn

ROOT = sn.ROOT

def prepare(tolerance=.5):
    boundary, roads, excluded = sn.load()
    roads, ambiguous = sn.node_network(roads, tolerance)
    clipped = []
    for r in roads:
        g = r['geo'].intersection(boundary)
        for p in getattr(g, 'geoms', [g]):
            if p.geom_type != 'LineString' or p.length < 1e-5:
                continue
            def level(c):
                d = r['geo'].project(Point(c))
                if d < 1e-5: return r['z0']
                if abs(d-r['geo'].length) < 1e-5: return r['z1']
                return r['z0'] if r['z0']==r['z1'] else None
            clipped.append(dict(r, geo=p, z0=level(p.coords[0]), z1=level(p.coords[-1])))
    sn.endpoint_graph(clipped, tolerance)
    return boundary, clipped, dict(excluded), ambiguous

def trace(roads, threshold=30, look=10):
    ports=defaultdict(list)
    vectors={}
    for i,r in enumerate(roads):
        for side,n in enumerate(r['nodes']):
            port=(i,side)
            ports[n].append(port)
            g=r['geo']; d=min(look,g.length)
            a=g.interpolate(0 if side==0 else g.length)
            b=g.interpolate(d if side==0 else g.length-d)
            dx,dy=b.x-a.x,b.y-a.y
            length=math.hypot(dx,dy)
            vectors[port]=(dx/length,dy/length) if length else (0,0)
    choices={}; angles={}
    for group in ports.values():
        for p in group:
            options=[]
            for q in group:
                if p[0]==q[0]: continue
                dot=sum(a*b for a,b in zip(vectors[p],vectors[q]))
                angle=math.degrees(math.acos(max(-1,min(1,-dot))))
                if angle<=threshold: options.append((angle,q))
            options.sort()
            if options and (len(options)==1 or options[1][0]-options[0][0]>1e-7):
                angles[p],choices[p]=options[0]
    pairs={p:q for p,q in choices.items() if choices.get(q)==p}
    seen=set(); chains=[]
    starts=[(i,s) for i in range(len(roads)) for s in (0,1) if (i,s) not in pairs]
    starts.extend((i,0) for i in range(len(roads)))
    for start in starts:
        if start[0] in seen: continue
        seq=[]; turns=[]; p=start; cycle=False
        while p[0] not in seen:
            i,s=p; seen.add(i); seq.append((i,s))
            end=(i,1-s)
            if end not in pairs: break
            q=pairs[end]
            if q[0] in seen:
                cycle=q==start
                break
            turns.append(angles[end]); p=q
        names=[]; transitions=[]
        for k,(i,s) in enumerate(seq):
            r=roads[i]
            if not names or names[-1]!=r['name']:
                if names:
                    lon,lat=sn.UNPROJECT(*r['geo'].coords[0 if s==0 else -1])
                    transitions.append(dict(before=names[-1],after=r['name'],angle=turns[k-1],lon=lon,lat=lat,
                        before_id=roads[seq[k-1][0]]['id'],after_id=r['id']))
                names.append(r['name'])
        chains.append(dict(names=names,changes=len(names)-1,miles=sum(roads[i]['geo'].length for i,s in seq)/1609.344,
            max_join_angle=max(turns,default=0),cycle=cycle,transitions=transitions,sequence=seq))
    assert len(seen)==len(roads)
    # Closed loops are saved separately; no arbitrary starting sign gives a ranking advantage.
    ranked=sorted([c for c in chains if not c['cycle']],key=lambda c:(-c['changes'],-c['miles'],c['names']))
    for rank,c in enumerate(ranked,1): c['order']=rank
    return ranked, [c for c in chains if c['cycle']]

def brief(c):
    return {k:v for k,v in c.items() if k!='sequence'}

def main():
    boundary,roads,excluded,ambiguous=prepare()
    ranked,cycles=trace(roads)
    rows=[dict(order=c['order'],changes=c['changes'],miles=c['miles'],names=' > '.join(c['names']),max_join_angle=c['max_join_angle']) for c in ranked]
    sn.csv_write('chain_rankings.csv',rows)
    sensitivity=[]
    for threshold,look in [(15,10),(20,10),(30,10),(45,10),(30,5),(30,20)]:
        cs,ls=trace(roads,threshold,look)
        winners=[brief(c) for c in cs if c['changes']==cs[0]['changes']]
        sensitivity.append(dict(threshold=threshold,look_m=look,chains=len(cs),cycles=len(ls),max_changes=cs[0]['changes'],winners=winners))
    out=dict(snapshot='2026-09-19',tolerance_m=.5,threshold_degrees=30,look_m=10,edges=len(roads),chains=len(ranked),
        excluded=excluded,ambiguous_grade_contacts=len(ambiguous),cycles=[brief(c) for c in cycles],
        hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['streets_nys_current.geojson','syracuse_boundary.geojson']},
        top=[brief(c) for c in ranked[:20]],sensitivity=sensitivity)
    (ROOT/'results.json').write_text(json.dumps(out,indent=2))
    fs=[]
    for c in ranked[:20]:
        for k,(i,s) in enumerate(c['sequence']):
            r=roads[i]
            fs.append(dict(type='Feature',properties=dict(order=c['order'],sequence=k,name=r['name'],id=r['id'],side=s),geometry=mapping(transform(sn.UNPROJECT,r['geo']))))
    (ROOT/'top_chains.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=fs)))
    print(json.dumps(dict(edges=len(roads),chains=len(ranked),top=[brief(c) for c in ranked[:8]],sensitivity=[dict(threshold=s['threshold'],look=s['look_m'],max=s['max_changes'],winners=[c['names'] for c in s['winners']]) for s in sensitivity]),indent=2))

if __name__=='__main__': main()
