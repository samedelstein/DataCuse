"""Draw a publication figure from cached NYS aerials and measured source lines."""
import json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'images'
T=Transformer.from_crs(4326,3857,always_xy=True).transform
fs=json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']
byid={f['properties']['NYSStreetID']:f for f in fs}
manifest={r['name']:r for r in json.loads((ROOT/'imagery_sources.json').read_text())}
cases=[('Spring Lane','spring_lane','477429983','A whole named street','About 64 feet in NYS data',('Pond Lane','Carbon Street','Spring Street')),
       ('South Avenue','south_avenue','800051053','A link inside a junction','About 16 feet, but not a conventional block',('Hovey Street','Marginal Street','South Avenue'))]
fig,axes=plt.subplots(1,2,figsize=(12,7.3),dpi=170)
fig.patch.set_facecolor('#f5f2eb')
for ax,(name,slug,feature_id,title,subtitle,labels) in zip(axes,cases):
    bounds=manifest[name]['bounds_3857']
    ax.imshow(Image.open(OUT/(slug+'_aerial.png')),extent=(bounds[0],bounds[2],bounds[1],bounds[3]))
    seen=set()
    for f in fs:
        p=f['properties'];label=p['CompleteStreetName']
        if label not in labels:continue
        g=transform(T,shape(f['geometry']))
        if not g.intersects(box(*bounds)):continue
        for line in (list(g.geoms) if g.geom_type=='MultiLineString' else [g]):
            x,y=line.xy;ax.plot(x,y,color='white',lw=1.1,alpha=.6)
        centre=g.intersection(box(*bounds)).centroid
        if label not in seen:
            seen.add(label)
            ax.text(centre.x,centre.y,label,fontsize=8,color='white',bbox=dict(facecolor='#112d38',alpha=.85,pad=2),zorder=8)
    g=transform(T,shape(byid[feature_id]['geometry']));x,y=g.xy
    ax.plot(x,y,lw=4,color='#ffe36d',zorder=9)
    ax.scatter([x[0],x[-1]],[y[0],y[-1]],s=25,color='#ffe36d',zorder=10)
    ax.annotate('Spring Lane' if slug=='spring_lane' else '16-foot mapped link',xy=(g.centroid.x,g.centroid.y),xytext=(bounds[0]+15,bounds[3]-45),
        color='#112d38',fontsize=10,fontweight='bold',bbox=dict(facecolor='#ffe36d',edgecolor='none',pad=5),
        arrowprops=dict(arrowstyle='->',color='#ffe36d',lw=2),zorder=11)
    lat=byid[feature_id]['geometry']['coordinates'][0][1]
    scale=25/math.cos(math.radians(lat));sx=bounds[0]+15;sy=bounds[1]+15
    ax.plot([sx,sx+scale],[sy,sy],color='white',lw=3)
    ax.text(sx,sy+5,'25 m',color='white',fontsize=8,bbox=dict(facecolor='#112d38',alpha=.7,pad=1))
    ax.text(.94,.94,'N ↑',transform=ax.transAxes,color='white',ha='right',fontsize=11,fontweight='bold')
    ax.set(xlim=(bounds[0],bounds[2]),ylim=(bounds[1],bounds[3]));ax.axis('off')
    ax.set_title(title+'\n'+subtitle,loc='left',fontsize=12,color='#112d38',pad=12)
fig.text(.055,.96,'Syracuse, by the short stretch',fontsize=24,color='#112d38',fontweight='bold')
fig.text(.055,.055,'Yellow: measured NYS street centerline. Imagery: NYS ITS, spring 2022. Street data downloaded September 19, 2026.',fontsize=8,color='#334b54')
fig.text(.055,.031,'Spring Lane is about 75 feet in the older city map. Measurements are GIS estimates; neither panel establishes a surveyed record.',fontsize=8,color='#334b54')
fig.subplots_adjust(left=.05,right=.95,top=.84,bottom=.11,wspace=.08)
fig.savefig(OUT/'shortest_streets.png',facecolor=fig.get_facecolor())
print(OUT/'shortest_streets.png')
