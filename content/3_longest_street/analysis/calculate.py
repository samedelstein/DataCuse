"""Rank the saved September 19 NYS snapshot; city-clipped distances in UTM 18N."""
import csv
import hashlib
import json
from collections import defaultdict, Counter
from pathlib import Path
import networkx as nx
from shapely.geometry import Point, mapping
from shapely.ops import unary_union, transform
import street_network as sn

ROOT = Path(__file__).resolve().parent
FT = 0.3048
MILE = 1609.344

def write_csv(name, rows):
    with (ROOT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def lines(g):
    if g.geom_type == 'LineString': return [g] if g.length > .01 else []
    return [p for part in getattr(g, 'geoms', []) for p in lines(part)]

def run(tolerance=.5, save=True):
    boundary, roads, excluded = sn.load()
    eligible_names = {r['name'] for r in roads if r['city_attributed'] and r['geo'].intersection(boundary).length > .01}
    roads = [r for r in roads if r['name'] in eligible_names]
    groups = defaultdict(list)
    raw = []
    for r in roads:
        g = r['geo'].intersection(boundary)
        if g.length <= .01: continue
        groups[r['name']].append(r)
        raw.append(dict(name=r['name'], source_id=r['id'], inside_ft=g.length/FT,
                        original_ft=r['geo'].length/FT, clipped=r['geo'].difference(boundary).length>.01))
    raw.sort(key=lambda r: (-r['inside_ft'], r['name'], r['source_id']))
    names = [dict(name=n, letters=sn.count(n), source_ids=';'.join(sorted({r['id'] for r in rs}))) for n,rs in groups.items()]
    names.sort(key=lambda r:(-r['letters'],r['name']))
    noded, ambiguous = sn.node_network(roads, tolerance)
    assert abs(sum(r['geo'].length for r in noded)-sum(r['geo'].length for r in roads)) < .001
    clipped=[]
    for r in noded:
        for g in lines(r['geo'].intersection(boundary)):
            def level(pt):
                if pt.distance(Point(r['geo'].coords[0])) < 1e-5: return r['z0']
                if pt.distance(Point(r['geo'].coords[-1])) < 1e-5: return r['z1']
                return r['z0'] if r['z0']==r['z1'] else ('boundary',r['id'])
            clipped.append(dict(r,geo=g,z0=level(Point(g.coords[0])),z1=level(Point(g.coords[-1]))))
    sn.endpoint_graph(clipped,tolerance)
    by_name=defaultdict(list)
    for r in clipped: by_name[r['name']].append(r)
    totals=[]; features=[]; audits={}
    for name, rs in by_name.items():
        union=unary_union([r['geo'] for r in rs])
        G=nx.Graph()
        for r in rs:
            u,v=r['nodes']; weight=r['geo'].length
            if not G.has_edge(u,v) or weight<G[u][v]['weight']:
                G.add_edge(u,v,weight=weight,road=r)
        best=(-1,None,None); comp_lengths=[]
        for nodes in nx.connected_components(G):
            H=G.subgraph(nodes)
            comp_lengths.append(unary_union([e['road']['geo'] for _,_,e in H.edges(data=True)]).length)
            for u,distances in nx.all_pairs_dijkstra_path_length(H,weight='weight'):
                v,dist=max(distances.items(),key=lambda p:p[1])
                if dist>best[0]: best=(dist,u,v)
        dist,u,v=best
        path=nx.shortest_path(G,u,v,weight='weight')
        route=[G[a][b]['road'] for a,b in zip(path,path[1:])]
        node_coords={}
        for r in rs:
            node_coords[r['nodes'][0]]=r['geo'].coords[0]; node_coords[r['nodes'][1]]=r['geo'].coords[-1]
        corridor_paths=[]
        if name=='ERIE BOULEVARD EAST':
            west=min(G.nodes,key=lambda n:node_coords[n][0])
            eastern=[n for n in G.nodes if Point(node_coords[n]).distance(boundary.boundary)<1 and node_coords[n][0]>node_coords[west][0]+3000]
            for end in eastern:
                p=nx.shortest_path(G,west,end,weight='weight')
                members=[G[a][b]['road'] for a,b in zip(p,p[1:])]
                length=sum(r['geo'].length for r in members)
                corridor_paths.append(dict(miles=length/MILE, endpoints=[list(transform(sn.UNPROJECT,Point(node_coords[n])).coords[0]) for n in [west,end]],source_ids=[r['id'] for r in members]))
            assert corridor_paths
            # Illustrate the longer west-to-east alternative, never the U-turn diameter.
            chosen=max(corridor_paths,key=lambda p:p['miles'])
            chosen_ids=set(chosen['source_ids'])
            route=[r for r in rs if r['id'] in chosen_ids]
        row=dict(name=name,total_ft=union.length/FT,total_miles=union.length/MILE,
                 longest_connected_sum_miles=max(comp_lengths)/MILE, components=len(comp_lengths),
                 graph_diameter_miles=dist/MILE, source_features=len({r['id'] for r in rs}),
                 split_class_ft=sum(r['geo'].length for r in rs if r['fcc'] in {'A25','A26','A27','A35','A36','A37','A45','A46','A47'})/FT)
        totals.append(row)
        if name in {'SOUTH SALINA STREET','ERIE BOULEVARD EAST','CANAL STREET','ONONDAGA CREEK BOULEVARD EAST','EAST BRIGHTON AVENUE AVENUE NORTHBOUND','GENANT TO NORTH CLINTON CONNECTOR'}:
            endpoints=[Point(node_coords[x]) for x in (u,v)]
            audits[name]=dict(row,route_source_ids=sorted({r['id'] for r in route}),
                endpoints=[list(transform(sn.UNPROJECT,p).coords[0]) for p in endpoints],
                endpoint_nearby=[sorted([(round(p.distance(r['geo']),1),r['name']) for r in roads if r['name']!=name])[:8] for p in endpoints],
                road_classes=dict(Counter(r['fcc'] for r in rs)), cycles=len(nx.cycle_basis(G)),
                boundary_distances_m=[p.distance(boundary.boundary) for p in endpoints], corridor_paths=corridor_paths)
            for r in groups[name]:
                features.append(dict(type='Feature',properties=dict(name=name,id=r['id'],fcc=r['fcc'],role='source'),geometry=mapping(transform(sn.UNPROJECT,r['geo']))))
            if route:
                features.append(dict(type='Feature',properties=dict(name=name,role='end_to_end'),geometry=mapping(transform(sn.UNPROJECT,unary_union([r['geo'] for r in route])))))
            for i,p in enumerate(endpoints):
                features.append(dict(type='Feature',properties=dict(name=name,role='endpoint',end=i),geometry=mapping(transform(sn.UNPROJECT,p))))
    totals.sort(key=lambda r:(-r['total_ft'],r['name']))
    route_rank=sorted(totals,key=lambda r:(-r['graph_diameter_miles'],r['name']))
    result=dict(snapshot_date='2026-09-19',tolerance_m=tolerance,names=len(names),excluded=dict(excluded),
        ambiguous_grade_crossings=len(ambiguous),longest_names=names[:10],longest_segments=raw[:10],
        total_ranking=totals[:12],graph_diameter_ranking=route_rank[:12],reviews=audits,
        hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['streets_nys_current.geojson','syracuse_boundary.geojson']})
    if save:
        write_csv('name_rankings.csv',names); write_csv('segment_rankings.csv',raw)
        write_csv('total_street_rankings.csv',totals); write_csv('graph_diameter_rankings.csv',route_rank)
        (ROOT/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        (ROOT/'review_geometry.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features)),encoding='utf-8')
    return result

if __name__=='__main__':
    r=run()
    print(json.dumps({k:r[k] for k in ['names','longest_names','longest_segments','total_ranking','graph_diameter_ranking','reviews']},indent=2))
