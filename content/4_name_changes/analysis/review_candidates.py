"""Download dated imagery for all eight leading name transitions."""
import json, math
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import urlopen
from urllib.parse import urlencode
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'review';OUT.mkdir(exist_ok=True)
R=json.loads((ROOT/'results.json').read_text())
T=Transformer.from_crs(4326,3857,always_xy=True).transform
F=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'top_chains.geojson').read_text())['features']]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
manifest=[]
for c in R['top'][:2]:
    for k,t in enumerate(c['transitions'],1):
        x,y=T(t['lon'],t['lat']);rad=180;bounds=(x-rad,y-rad,x+rad,y+rad)
        url='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export?'+urlencode(dict(bbox=','.join(map(str,bounds)),bboxSR=3857,imageSR=3857,size='800,800',format='png',f='image'))
        slug=f"chain{c['order']}_change{k}";raw=OUT/(slug+'_aerial.png')
        if not raw.exists():
            with urlopen(url,timeout=45) as resp:raw.write_bytes(resp.read())
        im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im)
        xy=lambda xx,yy:((xx-bounds[0])/360*800,(bounds[3]-yy)/360*800)
        for p,g in F:
            if p['order']!=c['order'] or not g.intersects(box(*bounds)):continue
            for part in getattr(g.intersection(box(*bounds)),'geoms',[g.intersection(box(*bounds))]):
                if part.geom_type=='LineString':d.line([xy(*pt) for pt in part.coords],fill='#ffdd36',width=3)
        d.ellipse((390,390,410,410),outline='#ef5360',width=4)
        d.rectangle((0,0,800,93),fill='#213d32')
        for j,line in enumerate([t['before']+' >',t['after'],f"NYS 2022 aerial | join {t['angle']:.1f} degrees | north up"]):d.text((12,5+28*j),line,font=font,fill='white')
        im.save(OUT/(slug+'_review.png'))
        manifest.append(dict(slug=slug,url=url,bounds_3857=bounds,transition=t,retrieved_utc=datetime.now(timezone.utc).isoformat(),imagery_year=2022))
(ROOT/'imagery_sources.json').write_text(json.dumps(manifest,indent=2))
sheet=Image.new('RGB',(1600,3200),'white')
for i,m in enumerate(manifest):sheet.paste(Image.open(OUT/(m['slug']+'_review.png')),((i//4)*800,(i%4)*800))
sheet.save(OUT/'all_transitions.jpg')
print('Saved eight aerial reviews')
