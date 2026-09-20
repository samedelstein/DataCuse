"""NYS eligibility and topology helpers, adapted from post 2 on September 19, 2026.

Use calculate.py for this post; this module has no executable ranking entrypoint.
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
