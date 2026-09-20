"""Save dated NYS aerials and geographically registered overlays for review."""
import json
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime, timezone
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'review';OUT.mkdir(exist_ok=True)
T=Transformer.from_crs(4326,3857,always_xy=True).transform
URL='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export'
CASES=[('canal_segment',-76.10982,43.05476,950,'Canal Street'),
       ('erie_carriageways',-76.100,43.0545,450,'Erie Boulevard East'),
       ('salina_south',-76.143542,42.984941,350,'South Salina Street'),
       ('salina_north',-76.152177,43.050912,240,'South Salina Street')]
fs=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']]
B=transform(T,shape(json.loads((ROOT/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
manifest=[]
def drawgeo(d,g,xy,fill,width):
    if g.geom_type in ('LineString','LinearRing'): d.line([xy(*p) for p in g.coords],fill=fill,width=width)
    else:
        for p in getattr(g,'geoms',[]):drawgeo(d,p,xy,fill,width)
for slug,lon,lat,radius,name in CASES:
    x,y=T(lon,lat);bounds=(x-radius,y-radius*.65,x+radius,y+radius*.65)
    params=dict(bbox=','.join(map(str,bounds)),bboxSR=3857,imageSR=3857,size='1200,780',format='png',f='image')
    url=URL+'?'+urlencode(params);raw=OUT/(slug+'_aerial.png')
    if not raw.exists():
        with urlopen(url,timeout=45) as response:raw.write_bytes(response.read())
    im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im)
    xy=lambda x,y:((x-bounds[0])/(bounds[2]-bounds[0])*1200,(bounds[3]-y)/(bounds[3]-bounds[1])*780)
    area=box(*bounds);labelled=set()
    for p,g in fs:
        if not g.intersects(area):continue
        highlight=p['CompleteStreetName']==name
        drawgeo(d,g.intersection(area),xy,'#ffdd36' if highlight else '#44bcdd',4 if highlight else 1)
        label=p['CompleteStreetName']
        if label and label not in labelled and area.contains(g.centroid) and (highlight or p['FCC'] in ('A21','A31','A41')):
            labelled.add(label);px,py=xy(g.centroid.x,g.centroid.y)
            w=d.textlength(label,font=font);d.rectangle((px,py,px+w+6,py+23),fill='#172c27');d.text((px+3,py+2),label,fill='white',font=font)
    for poly in getattr(B,'geoms',[B]):drawgeo(d,poly.exterior.intersection(area),xy,'#fa6681',4)
    d.rectangle((0,0,1200,32),fill='#172c27');d.text((12,6),name+' | NYS 2022 aerial + September 19, 2026 streets | pink = city boundary',font=font,fill='white')
    im.save(OUT/(slug+'_review.png'))
    manifest.append(dict(name=name,url=url,bounds_3857=bounds,imagery_year=2022,retrieved_utc=datetime.now(timezone.utc).isoformat()))
(ROOT/'imagery_sources.json').write_text(json.dumps(manifest,indent=2))
print('Saved',len(manifest),'candidate reviews')
