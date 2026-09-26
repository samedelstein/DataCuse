import json,math,hashlib
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform
R=Path(__file__).resolve().parent;D=R/'review';D.mkdir(exist_ok=True)
rows=json.loads((R/'node_rankings.json').read_text())[:6]
T=Transformer.from_crs(4326,3857,always_xy=True).transform
roads=json.loads((R/'eligible_noded_roads.geojson').read_text())['features'];manifest=[]
colors=['#ffe344','#ff6b6b','#42d9eb','#c29bff','#82ee75','#ff9d41','#ffffff']
for i,row in enumerate(rows,1):
 x,y=T(row['longitude'],row['latitude']);rad=230;bounds=[x-rad,y-rad,x+rad,y+rad]
 url='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export?'+urlencode(dict(bbox=','.join(map(str,bounds)),bboxSR=3857,imageSR=3857,size='1000,1000',format='png',f='image'))
 raw=D/f'candidate-{i}-aerial.png'
 if not raw.exists():raw.write_bytes(urlopen(url,timeout=60).read())
 im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im);xy=lambda p:((p[0]-bounds[0])/460*1000,(bounds[3]-p[1])/460*1000)
 for k,arm in enumerate(row['incident']):
  g=transform(T,shape(roads[arm['edge']]['geometry']));clipped=g.intersection(box(*bounds))
  for part in getattr(clipped,'geoms',[clipped]):
   if part.geom_type=='LineString':d.line([xy(p) for p in part.coords],fill=colors[k],width=5)
  d.text((14,12+30*k),str(k+1)+' '+arm['name'],font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',22),fill=colors[k],stroke_width=2,stroke_fill='black')
 d.ellipse((487,487,513,513),outline='red',width=5);im.save(D/f'candidate-{i}-overlay.png')
 manifest.append({'candidate':i,'node':row['node'],'url':url,'bounds_3857':bounds,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'downloaded_utc':datetime.now(timezone.utc).isoformat(),'imagery_year':2022,'names':row['names']})
 print('Saved candidate',i,flush=True)
(R/'imagery_sources.json').write_text(json.dumps(manifest,indent=2))
