"""Reproducible NYS street rankings. Run with analysis/.venv/Scripts/python.exe.

See methodology.md for scope and candidate review; computed rankings are GIS results.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from pyproj import Transformer
from shapely.geometry import shape, Point, mapping
from shapely.ops import transform, unary_union, substring
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent
PROJECT = Transformer.from_crs(4326, 26918, always_xy=True).transform
UNPROJECT = Transformer.from_crs(26918, 4326, always_xy=True).transform
PUBLIC = {'01', '02', '03', '12', '13'}
ROAD_CLASSES = {f'A{i}' for i in range(20, 50)} | {'A61', 'A62'}

def clean(value):
    return ' '.join((value or '').upper().split())

def count(value):
    return sum(c.isalpha() for c in value)

def csv_write(name, rows):
    if rows:
        with (ROOT/name).open('w', newline='', encoding='utf-8-sig') as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

def load():
    boundary = transform(PROJECT, shape(json.loads((ROOT/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
    area = boundary.buffer(500)
    features = json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']
    roads, excluded, seen = [], Counter(), set()
    for feature in features:
        p = feature['properties']
        geo = transform(PROJECT, shape(feature['geometry']))
        if not geo.intersects(area):
            continue
        name = clean(p['CompleteStreetName'])
        reason = None
        if p['Status'] != 'Active': reason = 'inactive'
        elif p['JURISDICTION'] not in PUBLIC: reason = 'not documented public jurisdiction'
        elif p['FCC'] not in ROAD_CLASSES: reason = 'ramp, freeway, driveway, path, service road or other excluded class'
        elif not name or 'UNNAMED' in name or 'UNKNOWN' in name: reason = 'unnamed'
        elif any(word in name.split() for word in ('DRIVEWAY','RAMP','ENTRANCE','EXIT')): reason = 'named driveway, ramp or entrance'
        elif p['PreType'] in ('Interstate','Route','State Route','US Highway'): reason = 'route designation rather than street name'
        if reason:
            if geo.intersects(boundary): excluded[reason] += 1
            continue
        parts = list(geo.geoms) if geo.geom_type == 'MultiLineString' else [geo]
        for part, line in enumerate(parts):
            signature = (name, line.normalize().wkb)
            if signature in seen:
                excluded['duplicate geometry/name'] += 1
                continue
            seen.add(signature)
            roads.append(dict(name=name, base=clean(p['StreetName']), suffix=clean(p['CLDXF_PostType']),
                id=p['NYSStreetID'], oid=p['OBJECTID'], part=part, geo=line,
                z0=p['FromZlev'] or 0, z1=p['ToZlev'] or 0,
                fcc=p['FCC'], jurisdiction=p['JURISDICTION'], props=p,
                city_attributed=any(p.get(k)=='Syracuse' for k in ('LeftIncorporatedMunicipality','RightIncorporatedMunicipality'))))
    return boundary, roads, excluded

def node_network(roads, tolerance):
    """Split at compatible ground-level crossings and endpoint-on-line contacts.

    Do not infer interior elevation for a segment that changes Z level.
    These crossings remain available for inspection in the grade audit.
    """
    geos=[r['geo'] for r in roads]
    tree=STRtree(geos)
    cuts=[{0.,g.length} for g in geos]
    ambiguous=[]
    def z_at(road, distance):
        if distance<1e-5: return road['z0']
        if abs(distance-road['geo'].length)<1e-5: return road['z1']
        if road['z0']==road['z1']: return road['z0']
        return None
    for i,g in enumerate(geos):
        for j in tree.query(g.buffer(max(tolerance,1e-5))):
            j=int(j)
            if j<=i: continue
            h=geos[j]
            intersection=g.intersection(h)
            points=[]
            if intersection.geom_type=='Point': points=[intersection]
            elif intersection.geom_type=='MultiPoint': points=list(intersection.geoms)
            for point in points:
                a,b=g.project(point),h.project(point)
                za,zb=z_at(roads[i],a),z_at(roads[j],b)
                if za is not None and za==zb:
                    cuts[i].add(a); cuts[j].add(b)
                elif za is None or zb is None:
                    ambiguous.append(dict(id_a=roads[i]['id'],id_b=roads[j]['id']))
            if tolerance>0:
                for src,dst in ((i,j),(j,i)):
                    for point,z in ((Point(geos[src].coords[0]),roads[src]['z0']),(Point(geos[src].coords[-1]),roads[src]['z1'])):
                        distance=geos[dst].project(point)
                        if point.distance(geos[dst])<=tolerance and z_at(roads[dst],distance)==z:
                            cuts[dst].add(distance)
    result=[]
    for r,distances in zip(roads,cuts):
        positions=sorted(distances)
        clean_positions=[positions[0]]
        for d in positions[1:]:
            if d-clean_positions[-1]>1e-5: clean_positions.append(d)
        for a,b in zip(clean_positions,clean_positions[1:]):
            if b-a<1e-5: continue
            result.append(dict(r,geo=substring(r['geo'],a,b),z0=z_at(r,a),z1=z_at(r,b)))
    return result,ambiguous

def endpoint_graph(roads, tolerance):
    points = []
    for r in roads:
        points.extend([Point(r['geo'].coords[0]), Point(r['geo'].coords[-1])])
    uf = nx.utils.UnionFind(range(len(points)))
    tree = STRtree(points)
    levels = [r[z] for r in roads for z in ('z0','z1')]
    for i, point in enumerate(points):
        nearby = tree.query(point.buffer(max(tolerance, 0.000001)))
        for j in nearby:
            if j > i and levels[i] == levels[j] and point.distance(points[j]) <= max(tolerance, 0.000001):
                uf.union(i,int(j))
    graph = nx.MultiGraph()
    for i, road in enumerate(roads):
        u,v = uf[2*i],uf[2*i+1]
        graph.add_edge(u,v,key=i,index=i)
        road['nodes'] = (u,v)
    return graph

def calculate(tolerance=0.5, save=True):
    boundary, roads, excluded = load()
    original_roads=roads
    roads,grade_audit=node_network(roads,tolerance)
    assert abs(sum(r['geo'].length for r in roads)-sum(r['geo'].length for r in original_roads))<.001
    graph = endpoint_graph(roads,tolerance)
    groups = defaultdict(list)
    for i,r in enumerate(roads): groups[r['name']].append(i)
    totals, components, blocks, name_rows, raw = [], [], [], [], []
    for name, indices in groups.items():
        selected = [i for i in indices if roads[i]['city_attributed'] and roads[i]['geo'].intersection(boundary).length > .01]
        if not selected: continue
        r = roads[selected[0]]
        name_rows.append(dict(name=name,base=r['base'],suffix=r['suffix'],base_characters=count(r['base']),
            full_characters=count(name),suffix_characters=count(r['suffix']),suffix_minus_base=count(r['suffix'])-count(r['base'])))
        sub = nx.MultiGraph()
        for i in indices:
            u,v=roads[i]['nodes']
            sub.add_edge(u,v,key=i,index=i)
        component_rows = []
        for comp_index,nodes in enumerate(nx.connected_components(sub),1):
            edges = list(sub.subgraph(nodes).edges(keys=True))
            members = [roads[i] for _,_,i in edges]
            geom = unary_union([r['geo'] for r in members])
            inside = geom.intersection(boundary)
            if inside.length <= .01: continue
            outside = geom.difference(boundary).length
            centre = transform(UNPROJECT,inside.centroid)
            row=dict(name=name,component=comp_index,length_ft=inside.length/.3048,
                full_component_ft=geom.length/.3048,outside_city_ft=outside/.3048,
                wholly_inside=outside < .01,source_segments=len(members),
                source_ids=';'.join(sorted(set(r['id'] for r in members))),lon=centre.x,lat=centre.y)
            component_rows.append(row)
        for row in component_rows: row['components_in_city']=len(component_rows)
        components.extend(component_rows)
        totals.append(dict(name=name,length_ft=sum(r['length_ft'] for r in component_rows),components=len(component_rows),
            wholly_inside=all(r['wholly_inside'] for r in component_rows)))
        # Walk through degree-two nodes only when they are not intersections
        # with another eligible street. Real same-name branches terminate blocks.
        def cross_names(node):
            return sorted({roads[k]['name'] for _,_,k in graph.edges(node,keys=True)}-{name})
        def stop(node): return sub.degree(node)!=2 or bool(cross_names(node))
        visited=set()
        for start in sorted(sub.nodes):
            if not stop(start): continue
            for _,nxt,first in list(sub.edges(start,keys=True)):
                if first in visited: continue
                edge_ids=[first]; visited.add(first); current=nxt
                while not stop(current):
                    choices=[(v,k) for _,v,k in sub.edges(current,keys=True) if k not in visited]
                    if not choices: break
                    current,k=choices[0]; visited.add(k); edge_ids.append(k)
                geo=unary_union([roads[i]['geo'] for i in edge_ids])
                if geo.intersection(boundary).length<=.01: continue
                a,b=cross_names(start),cross_names(current)
                centre=transform(UNPROJECT,geo.centroid)
                blocks.append(dict(name=name,length_ft=geo.length/.3048,
                    endpoint_a=';'.join(a) or 'DEAD END / SAME-NAME BRANCH',
                    endpoint_b=';'.join(b) or 'DEAD END / SAME-NAME BRANCH',
                    intersection_to_intersection=bool(a and b and start!=current),wholly_inside=geo.difference(boundary).length<.01,
                    source_segments=len(edge_ids),source_ids=';'.join(roads[i]['id'] for i in edge_ids),
                    lon=centre.x,lat=centre.y))
    for r in original_roads:
        if r['geo'].intersection(boundary).length>.01:
            raw.append(dict(name=r['name'],id=r['id'],length_ft=r['geo'].length/.3048,fcc=r['fcc'],
                wholly_inside=r['geo'].difference(boundary).length<.01,lon=transform(UNPROJECT,r['geo'].centroid).x,lat=transform(UNPROJECT,r['geo'].centroid).y))
    for rows in (components,totals,blocks,raw): rows.sort(key=lambda r:(r['length_ft'],r['name']))
    name_rows.sort(key=lambda r:(r['full_characters'],r['name']))
    eligible_blocks=[r for r in blocks if r['intersection_to_intersection'] and r['wholly_inside']]
    # Aerial review: two isolated Rugby Road components are traffic-island arcs.
    # Preserve them in the diagnostic component table, exclude from whole streets.
    island_ids={'504326410','504326416'}
    whole_streets=[r for r in components if r['wholly_inside'] and not set(r['source_ids'].split(';'))<=island_ids]
    if save:
        csv_write('name_rankings.csv',name_rows)
        csv_write('whole_name_rankings.csv',totals)
        csv_write('connected_street_rankings.csv',components)
        csv_write('whole_street_candidates.csv',whole_streets)
        csv_write('block_rankings.csv',eligible_blocks)
        csv_write('all_block_candidates.csv',blocks)
        csv_write('raw_segment_rankings.csv',raw)
        csv_write('suffix_longer_than_name.csv',[r for r in name_rows if r['suffix_minus_base']>0])
    summary=dict(tolerance_m=tolerance,eligible_names=len(name_rows),excluded=dict(excluded),
        input_roads=len(original_roads),noded_pieces=len(roads),ambiguous_grade_crossings=len(grade_audit),
        shortest_names=name_rows[:20],
        shortest_base_names=sorted(name_rows,key=lambda r:(r['base_characters'],r['name']))[:20],
        suffix_longer=sum(r['suffix_minus_base']>0 for r in name_rows),
        shortest_full_names=sorted(name_rows,key=lambda r:(r['full_characters'],r['name']))[:10],
        largest_suffix_gaps=sorted(name_rows,key=lambda r:(-r['suffix_minus_base'],r['name']))[:10],
        whole_streets=whole_streets[:20],
        blocks=eligible_blocks[:20],components=components[:20],totals=totals[:20],raw=raw[:10])
    if save: (ROOT/'results.json').write_text(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    result=calculate()
    print(json.dumps(result,indent=2))
