"""Whole-path straightness, separate from local straightest continuation.

Test consecutive name-run windows with a fixed lead-in/lead-out, and save
all scores rather than deciding straightness from angles only at joins.
"""
import json,math
from collections import Counter
from shapely.geometry import LineString,Point,mapping
from shapely.ops import substring,transform
import calculate as c
ROOT=c.ROOT

def assemble(chain,roads):
    coords=[];runs=[];distance=0.;gaps=[]
    for i,side in chain['sequence']:
        r=roads[i];pts=list(r['geo'].coords)
        if side:pts.reverse()
        if coords:
            gap=math.dist(coords[-1],pts[0]);distance+=gap;gaps.append(gap)
        start=distance;distance+=r['geo'].length
        if not runs or runs[-1]['name']!=r['name']:
            runs.append(dict(name=r['name'],start=start,end=distance,ids=[r['id']]))
        else:
            runs[-1]['end']=distance;runs[-1]['ids'].append(r['id'])
        coords.extend(pts)
    line=LineString(coords)
    assert abs(line.length-distance)<1e-5
    return line,runs,max(gaps,default=0)

def score(line):
    chord=LineString([line.coords[0],line.coords[-1]])
    if not chord.length:return dict(length_m=line.length,chord_m=0,ratio=999,max_offset_m=999)
    return dict(length_m=line.length,chord_m=chord.length,ratio=line.length/chord.length,
        max_offset_m=max(Point(p).distance(chord) for p in line.coords))

def run():
    b,roads,ex,amb=c.prepare()
    chains,cycles=c.trace(roads)
    full=[];candidates=[];features=[]
    for chain in chains:
        if chain['changes']==0:continue
        line,runs,gap=assemble(chain,roads)
        full.append(dict(order=chain['order'],names=chain['names'],changes=chain['changes'],max_gap_m=gap,**score(line)))
        for margin in (25,50,100):
            for i in range(len(runs)-1):
                for j in range(i+1,len(runs)):
                    if runs[i]['end']-runs[i]['start']<margin or runs[j]['end']-runs[j]['start']<margin:continue
                    lo=runs[i]['end']-margin;hi=runs[j]['start']+margin
                    segment=substring(line,lo,hi)
                    metrics=score(segment)
                    lengths=[min(hi,r['end'])-max(lo,r['start']) for r in runs[i:j+1]]
                    key=len(candidates)
                    record=dict(id=key,chain_order=chain['order'],margin_m=margin,names=[r['name'] for r in runs[i:j+1]],changes=j-i,
                        run_lengths_m=lengths,min_run_m=min(lengths),start_m=lo,end_m=hi,**metrics)
                    candidates.append(record)
                    features.append(dict(type='Feature',properties=record,geometry=mapping(transform(c.sn.UNPROJECT,segment))))
    summaries=[]
    for margin,offset,ratio,minrun in [(50,10,1.01,0),(50,5,1.01,0),(50,20,1.01,0),(25,10,1.01,0),(100,10,1.01,0),(50,10,1.01,25),(50,10,1.01,50)]:
        eligible=[x for x in candidates if x['margin_m']==margin and x['max_offset_m']<=offset and x['ratio']<=ratio and x['min_run_m']+1e-7>=minrun]
        eligible.sort(key=lambda x:(-x['changes'],-x['length_m']))
        top=eligible[0]['changes'] if eligible else 0
        summaries.append(dict(margin_m=margin,offset_limit_m=offset,ratio_limit=ratio,min_run_m=minrun,eligible=len(eligible),max_changes=top,winners=[x for x in eligible if x['changes']==top]))
    out=dict(rule='Consecutive name runs in the 30-degree mutual-straightest chains; first and last name each represented by exactly the stated margin distance.',
        baseline=dict(margin_m=50,offset_limit_m=10,ratio_limit=1.01,min_run_m=0),full_chains=full,candidates=candidates,sensitivity=summaries)
    (ROOT/'straightness_results.json').write_text(json.dumps(out,indent=2))
    (ROOT/'straightness_geometry.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features)))
    c.sn.csv_write('straightness_candidates.csv',[{**x,'names':' > '.join(x['names']),'run_lengths_m':' > '.join(f'{v:.3f}' for v in x['run_lengths_m'])} for x in candidates])
    print(json.dumps(dict(full_leaders=full[:2],sensitivity=summaries),indent=2))

if __name__=='__main__':run()
