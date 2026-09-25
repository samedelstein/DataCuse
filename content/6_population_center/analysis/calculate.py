"""Population-weighted mean of 2020 Syracuse Census block polygon centroids."""
import csv,json,math,hashlib
from pathlib import Path
from shapely.geometry import shape,Point,mapping
from shapely import make_valid
from shapely.ops import transform,unary_union
from pyproj import Transformer,Geod
R=Path(__file__).resolve().parent
T=Transformer.from_crs(4326,26918,always_xy=True).transform
U=Transformer.from_crs(26918,4326,always_xy=True).transform
E=Transformer.from_crs(4326,5070,always_xy=True).transform
EU=Transformer.from_crs(5070,4326,always_xy=True).transform
geod=Geod(ellps='WGS84')
place=json.loads((R/'syracuse_place_2020.geojson').read_text())['features'][0]
boundary=transform(T,shape(place['geometry'])); assert boundary.is_valid
candidates=json.loads((R/'blocks_candidate_2020.geojson').read_text())['features']
assert len({f['properties']['GEOID'] for f in candidates})==len(candidates)
selected=[]; excluded=[]; partial=[]; features=[]; geos=[]; repairs=[]
for f in candidates:
    p=f['properties'];g=transform(T,shape(f['geometry']))
    if not g.is_valid:
        before=g.area;g=make_valid(g)
        if g.geom_type=='GeometryCollection':g=unary_union([part for part in g.geoms if part.geom_type in ('Polygon','MultiPolygon')])
        repairs.append({'geoid':p['GEOID'],'area_change_m2':g.area-before})
    assert g.is_valid and g.geom_type in ('Polygon','MultiPolygon')
    overlap=g.intersection(boundary).area/g.area
    if 1e-5<overlap<1-1e-5:partial.append({'geoid':p['GEOID'],'overlap_fraction':overlap,'population':p['POP100']})
    if not boundary.covers(g.representative_point()):excluded.append(p['GEOID']);continue
    assert overlap>0.99999,(p['GEOID'],overlap)
    pop=p['POP100']; assert pop is not None and pop>=0 and pop==int(pop)
    centroid=g.centroid;lon,lat=U(centroid.x,centroid.y)
    internal=T(float(p['INTPTLON']),float(p['INTPTLAT']))
    ea=transform(Transformer.from_crs(26918,5070,always_xy=True).transform,g).centroid
    selected.append({'geoid':p['GEOID'],'population':int(pop),'area_m2':g.area,'easting':centroid.x,'northing':centroid.y,'longitude':lon,'latitude':lat,'internal_x':internal[0],'internal_y':internal[1],'equal_area_x':ea.x,'equal_area_y':ea.y,'overlap_fraction':overlap,'centroid_inside_block':g.covers(centroid)})
    features.append({'type':'Feature','properties':{'geoid':p['GEOID'],'population':int(pop)},'geometry':mapping(transform(U,g))});geos.append(g)
populated=[r for r in selected if r['population']>0]
total=sum(r['population'] for r in selected)
assert total==int(place['properties']['POP100'])==148620
assert not partial,partial
x=math.fsum(r['population']*r['easting'] for r in populated)/total
y=math.fsum(r['population']*r['northing'] for r in populated)/total
lon,lat=U(x,y)
ix=math.fsum(r['population']*r['internal_x'] for r in populated)/total
iy=math.fsum(r['population']*r['internal_y'] for r in populated)/total
ex=math.fsum(r['population']*r['equal_area_x'] for r in populated)/total
ey=math.fsum(r['population']*r['equal_area_y'] for r in populated)/total
elon,elat=EU(ex,ey)
# Independent accumulation around a local origin avoids multiplying large coordinates.
ax,ay=boundary.centroid.x,boundary.centroid.y
checkx=ax+sum(r['population']*(r['easting']-ax) for r in selected)/total
checky=ay+sum(r['population']*(r['northing']-ay) for r in selected)/total
assert math.hypot(checkx-x,checky-y)<1e-6
union=unary_union(geos); coverage_difference=union.symmetric_difference(boundary).area
assert coverage_difference<1,coverage_difference
prior_path=R.parents[1]/'5_geographic_center/analysis/results.json'
prior=json.loads(prior_path.read_text()); az,_,distance=geod.inv(prior['longitude'],prior['latitude'],lon,lat)
area_lon,area_lat=U(ax,ay)
road_path=R.parents[1]/'4_name_changes/analysis/streets_nys_current.geojson'
near=[];context=[];c=Point(x,y)
for f in json.loads(road_path.read_text())['features']:
    g=transform(T,shape(f['geometry']));d=g.distance(c)
    if d<300:near.append({'name':f['properties'].get('CompleteStreetName'),'distance_metres':d,'id':f['properties'].get('NYSStreetID')});context.append(f)
near.sort(key=lambda r:r['distance_metres'])
top=sorted(populated,key=lambda r:r['population'],reverse=True)[:10]
# A per-block worst-case geometric displacement bound, not a statistical interval.
weighted_radius=0
for row,g in zip(selected,geos):
    if not row['population']:continue
    pts=[p for poly in ([g] if g.geom_type=='Polygon' else g.geoms) for p in poly.exterior.coords]
    radius=max(math.hypot(a-row['easting'],b-row['northing']) for a,b in pts)
    weighted_radius+=row['population']*radius
results={'definition':'Population-weighted mean of geometric polygon centroids for 2020 Census blocks in Syracuse city. Each block population is located at that block centroid.','vintage':'2020 Census; boundaries January 1, 2020; population Census Day April 1, 2020','projection':'EPSG:26918','population':total,'candidate_blocks':len(candidates),'selected_blocks':len(selected),'populated_blocks':len(populated),'zero_population_blocks':len(selected)-len(populated),'latitude':lat,'longitude':lon,'easting':x,'northing':y,'inside_city':boundary.covers(c),'city_total_check':place['properties']['POP100'],'selection_checks':{'geometry_repairs':repairs,'partially_overlapping_blocks':partial,'union_difference_square_metres':coverage_difference,'min_selected_overlap_fraction':min(r['overlap_fraction'] for r in selected),'independent_weighted_mean_difference_metres':math.hypot(checkx-x,checky-y)},'comparison_with_geographic_center':{'latitude':prior['latitude'],'longitude':prior['longitude'],'source':'post 5, full NYS municipal area','distance_metres':distance,'distance_miles':distance/1609.344,'bearing_degrees':az%360},'matching_2020_area_centroid':{'longitude':area_lon,'latitude':area_lat,'distance_from_post5_metres':geod.inv(prior['longitude'],prior['latitude'],area_lon,area_lat)[2]},'sensitivity':{'internal_point_mean':{'longitude':U(ix,iy)[0],'latitude':U(ix,iy)[1],'difference_metres':math.hypot(ix-x,iy-y)},'equal_area_projection':{'longitude':elon,'latitude':elat,'difference_metres':geod.inv(lon,lat,elon,elat)[2]},'populated_block_centroids_outside_own_polygon':sum(not r['centroid_inside_block'] for r in populated),'weighted_max_block_radius_metres':weighted_radius/total,'note':'Internal-point and projection comparisons are sensitivity checks, not confidence intervals. Radius is a conservative geometric upper bound assuming all residents are somewhere inside their recorded blocks, not an estimate of actual error.'},'nearest_streets':near[:12],'most_populated_blocks':top,'source_hashes':{'post5_results':hashlib.sha256(prior_path.read_bytes()).hexdigest(),'nys_streets_context_input':hashlib.sha256(road_path.read_bytes()).hexdigest()}}
assert results['inside_city']
(R/'results.json').write_text(json.dumps(results,indent=2))
(R/'syracuse_blocks_2020.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':')))
(R/'nearby_streets.geojson').write_text(json.dumps({'type':'FeatureCollection','features':context},separators=(',',':')))
with (R/'block_centroids.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=list(selected[0]));writer.writeheader();writer.writerows(selected)
print(json.dumps({k:v for k,v in results.items() if k not in ('most_populated_blocks','source_hashes')},indent=2))
