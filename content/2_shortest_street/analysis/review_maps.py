"""Download NYS 2022 aerial imagery and overlay street candidates for review."""
import json
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from pyproj import Transformer
from shapely.geometry import shape, box
from shapely.ops import transform

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'images'
OUT.mkdir(exist_ok=True)
T=Transformer.from_crs(4326,3857,always_xy=True).transform
URL='https://orthos.its.ny.gov/arcgis/rest/services/wms/2022/MapServer/export'
CASES=[('spring_lane',-76.1519333,43.0681016,140,'Spring Lane'),
       ('south_avenue',-76.1587239,43.0308640,140,'South Avenue'),
       ('rugby_road',-76.13293,43.06702,220,'Rugby Road'),
       ('meade_court',-76.1616433,43.0440226,140,'Meade Court')]
queue=json.loads((ROOT/'junction_review_queue.json').read_text()) if (ROOT/'junction_review_queue.json').exists() else []
for candidate in queue[:8]:
    if candidate['name'] in ('SEYMOUR STREET','GIFFORD STREET','FABIUS STREET'): continue
    CASES.append((candidate['name'].lower().replace(' ','_'),float(candidate['lon']),float(candidate['lat']),110,candidate['name'].title()))

if __name__=='__main__':
    fs=json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']
    features=[(f['properties'],transform(T,shape(f['geometry']))) for f in fs]
    manifest=[]
    for slug,lon,lat,radius,name in CASES:
        x,y=T(lon,lat); bounds=(x-radius,y-radius,x+radius,y+radius)
        params=dict(bbox=','.join(map(str,bounds)),bboxSR=3857,imageSR=3857,size='1000,1000',format='png',f='image')
        url=URL+'?'+urlencode(params)
        raw=OUT/(slug+'_aerial.png')
        if not raw.exists():
            with urlopen(url,timeout=60) as response: raw.write_bytes(response.read())
        image=Image.open(raw)
        fig,ax=plt.subplots(figsize=(9,9),dpi=150)
        ax.imshow(image,extent=(bounds[0],bounds[2],bounds[1],bounds[3]))
        labelled=set()
        for p,g in features:
            if not g.intersects(box(*bounds)): continue
            parts=list(g.geoms) if g.geom_type=='MultiLineString' else [g]
            highlight=p['CompleteStreetName']==name
            for line in parts:
                a,b=line.xy
                ax.plot(a,b,color='#ffdc32' if highlight else '#51d7ed',lw=3 if highlight else 1,alpha=.9 if highlight else .5)
            label=p['CompleteStreetName']
            if label and label not in labelled and box(*bounds).contains(g.centroid) and p['FCC'] not in ('A74','A71'):
                labelled.add(label)
                ax.text(g.centroid.x,g.centroid.y,label,fontsize=7,color='white',bbox=dict(facecolor='black',alpha=.65,pad=1))
        ax.set(xlim=(bounds[0],bounds[2]),ylim=(bounds[1],bounds[3]))
        ax.axis('off'); ax.set_title(name+' | NYS streets over 2022 aerial imagery',fontsize=12)
        fig.text(.12,.045,'Review image. Imagery: NYS ITS Geospatial Services (2022). Street download: September 19, 2026.',fontsize=7)
        fig.savefig(OUT/(slug+'_review.png'),bbox_inches='tight');plt.close(fig)
        manifest.append(dict(name=name,url=url,bounds_3857=bounds))
    (ROOT/'imagery_sources.json').write_text(json.dumps(manifest,indent=2))
    print('Saved',len(manifest),'review images')
