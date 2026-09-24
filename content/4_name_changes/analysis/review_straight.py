"""Independent saved city-map name comparison and dated aerial review."""
import json,hashlib
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,Point,box
from shapely.ops import transform
from pyproj import Transformer
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'review'
T=Transformer.from_crs(4326,26918,always_xy=True).transform
WEB=Transformer.from_crs(4326,3857,always_xy=True).transform
R=json.loads((ROOT/'straightness_results.json').read_text());old=json.loads((ROOT/'results.json').read_text())
source=ROOT/'streets_city_reference.geojson'
city=json.loads(source.read_text())
cityrows=[(f['properties'],transform(T,shape(f['geometry'])),f) for f in city['features']]
fs=json.loads((ROOT/'straightness_geometry.geojson').read_text())['features']
winners=R['sensitivity'][0]['winners'];manifest=[];audit=[];saved={}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for w in winners:
    feature=next(f for f in fs if f['properties']['id']==w['id']);g=transform(T,shape(feature['geometry']))
    matches=[]
    for p,h,f in cityrows:
        if h.distance(g)<=10:
            overlap=h.intersection(g.buffer(10)).length
            if overlap>10:
                matches.append(dict(name=p.get('FULLNAME'),id=p.get('FID'),overlap_m=overlap))
                saved[str(p.get('FID'))]=f
    samples=[];dist=0
    for name,length in zip(w['names'],w['run_lengths_m']):
        point=g.interpolate(dist+length/2)
        p,h,f=min(cityrows,key=lambda row:row[1].distance(point))
        samples.append(dict(nys_name=name,city_name=p['FULLNAME'],city_fid=p['FID'],distance_m=h.distance(point)))
        dist+=length
    audit.append(dict(names=w['names'],midpoint_name_checks=samples,matches=matches))
    chain=next(c for c in old['top'] if c['order']==w['chain_order'])
    transitions=[t for t in chain['transitions'] if t['before'] in w['names'] and t['after'] in w['names']]
    webgeo=transform(WEB,shape(feature['geometry']))
    for k,t in enumerate(transitions,1):
        x,y=WEB(t['lon'],t['lat']);rad=150;bounds=(x-rad,y-rad,x+rad,y+rad)
        url='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export?'+urlencode(dict(bbox=','.join(map(str,bounds)),bboxSR=3857,imageSR=3857,size='800,800',format='png',f='image'))
        slug=f"straight_{w['id']}_change{k}";raw=OUT/(slug+'_aerial.png')
        if not raw.exists():
            with urlopen(url,timeout=45) as resp:raw.write_bytes(resp.read())
        im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im)
        xy=lambda xx,yy:((xx-bounds[0])/300*800,(bounds[3]-yy)/300*800)
        clip=webgeo.intersection(box(*bounds))
        for part in getattr(clip,'geoms',[clip]):
            if part.geom_type=='LineString':d.line([xy(*pt) for pt in part.coords],fill='#ffdd36',width=3)
        d.ellipse((390,390,410,410),outline='#ef5360',width=4)
        d.rectangle((0,0,800,98),fill='#213d32')
        for j,line in enumerate([t['before']+' >',t['after'],'NYS 2022 aerial | north up | marker = recorded name change']):d.text((12,5+29*j),line,font=font,fill='white')
        im.save(OUT/(slug+'_review.png'))
        manifest.append(dict(slug=slug,url=url,bounds_3857=bounds,transition=t,retrieved_utc=datetime.now(timezone.utc).isoformat(),imagery_year=2022))
(ROOT/'straight_imagery_sources.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'city_name_check.json').write_text(json.dumps(dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),downloaded='2026-09-19',source_url='https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services/Streets/FeatureServer/0',audit=audit),indent=2))
(ROOT/'city_comparison_extract.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=list(saved.values()))))
sheet=Image.new('RGB',(1600,1600),'white')
for i,m in enumerate(manifest):sheet.paste(Image.open(OUT/(m['slug']+'_review.png')),((i//2)*800,(i%2)*800))
sheet.save(OUT/'straight_transitions.jpg')
print(json.dumps(audit,indent=2))
