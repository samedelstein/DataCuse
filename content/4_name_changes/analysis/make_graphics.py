"""Draw exact saved chain geometry and results in DataCuse's editorial palette."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,box
from shapely.ops import transform,unary_union
from pyproj import Transformer
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'images'
R=json.loads((ROOT/'results.json').read_text())
T=Transformer.from_crs(4326,26918,always_xy=True).transform
FS=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'top_chains.geojson').read_text())['features']]
BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9'
COLORS=['#316b4d','#207675','#996327','#a85632','#725b7a']
BASE=[transform(T,shape(f['geometry'])) for f in json.loads((ROOT/'streets_nys_current.geojson').read_text())['features'] if f['properties']['FCC'] in ['A41','A31','A21','A25']]
B=transform(T,shape(json.loads((ROOT/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
def font(s,serif=False,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),s)
def text(d,x,y,s,size=30,color=INK,serif=False,bold=False):d.text((x,y),s,font=font(size,serif,bold),fill=color)
def line(d,g,xy,color,width):
    if g.is_empty:return
    if g.geom_type in ['LineString','LinearRing']:d.line([xy(*p) for p in g.coords],fill=color,width=width,joint='curve')
    else:
        for p in getattr(g,'geoms',[]):line(d,p,xy,color,width)
def wrap(d,x,y,s,width,size=30,color=INK):
    ln=''
    for word in s.split():
        test=(ln+' '+word).strip()
        if d.textlength(test,font=font(size))>width:
            text(d,x,y,ln,size,color);y+=size+12;ln=word
        else:ln=test
    text(d,x,y,ln,size,color)
    return y+size+12
audit=[]
for c in R['top'][:2]:
    im=Image.new('RGB',(1800,1420),BG);d=ImageDraw.Draw(im)
    text(d,65,35,'SYRACUSE / A CHANGE OF NAME',25,MUTED,bold=True)
    text(d,60,85,'Five names. Four handoffs.',76,serif=True,bold=True)
    text(d,65,195,f"Tied at the top under a 30° junction rule • {c['miles']:.2f} mapped miles",32)
    selected=[(p,g) for p,g in FS if p['order']==c['order']]
    u=unary_union([g for p,g in selected]);a,b,e,f=u.bounds
    cx,cy=(a+e)/2,(b+f)/2;w=max(e-a+450,(f-b+450)*.88);h=w/.88
    bounds=(cx-w/2,cy-h/2,cx+w/2,cy+h/2);area=box(*bounds)
    rect=(65,295,880,1000)
    xy=lambda x,y:(rect[0]+(x-bounds[0])/w*rect[2],rect[1]+(bounds[3]-y)/h*rect[3])
    d.rectangle((65,295,945,1295),fill='#ecebe2')
    for g in BASE:
        if g.intersects(area):line(d,g.intersection(area),xy,'#c8cdc4',2)
    line(d,B.boundary.intersection(area),xy,'#a85632',3)
    for p,g in selected:line(d,g,xy,COLORS[c['names'].index(p['name'])],8)
    for k,t in enumerate(c['transitions'],1):
        x,y=xy(*T(t['lon'],t['lat']));d.ellipse((x-20,y-20,x+20,y+20),fill=BG,outline=INK,width=3)
        d.text((x,y),str(k),anchor='mm',font=font(25,bold=True),fill=INK)
    text(d,85,320,'N ↑',29,bold=True)
    scale=500/w*880;d.line((105,1250,105+scale,1250),fill=INK,width=4)
    text(d,105,1260,'500 metres',22)
    text(d,1010,305,'NAME SEQUENCE',26,MUTED,bold=True)
    for k,name in enumerate(c['names']):
        y=370+k*150
        d.rounded_rectangle((1005,y,1735,y+78),radius=8,fill=COLORS[k])
        text(d,1025,y+20,name.title(),34,BG,serif=True,bold=True)
        if k<4:
            text(d,1035,y+92,f"↓  Change {k+1} • {c['transitions'][k]['angle']:.1f}° join",27,MUTED)
    wrap(d,1010,1160,'Roads bend along the way. Numbers locate the four name changes; this is a map trace, not driving directions.',720,29)
    text(d,65,1330,'Source: NYS Streets and city boundary, downloaded September 19, 2026.',25,MUTED)
    text(d,65,1367,'Rust outline = city limit • full names count • 10 m approach measurement',25,MUTED)
    name='crawford-to-comstock' if c['order']==1 else 'state-fair-to-court'
    im.save(OUT/(name+'.png'),optimize=True)
    audit.append(dict(image=name,names=c['names'],changes=c['changes'],miles=c['miles'],angles=[t['angle'] for t in c['transitions']]))

im=Image.new('RGB',(1800,1250),BG);d=ImageDraw.Draw(im)
text(d,65,35,'SYRACUSE / THE RULE CHANGES THE RESULT',25,MUTED,bold=True)
text(d,60,90,'How straight is straight?',78,serif=True,bold=True)
text(d,65,205,'Maximum bend allowed where mapped pieces join; 10 m approach measurement.',31)
text(d,65,315,'ANGLE LIMIT',26,MUTED,bold=True)
text(d,360,315,'MOST NAME CHANGES',26,MUTED,bold=True)
text(d,870,315,'LEADING CHAIN(S)',26,MUTED,bold=True)
for j,s in enumerate(R['sensitivity'][:4]):
    y=395+j*145
    text(d,80,y,str(s['threshold'])+'°',60,serif=True,bold=True)
    width=s['max_changes']*100
    d.rectangle((365,y+5,365+width,y+62),fill=COLORS[1])
    for x in range(375,365+width-15,40):d.line((x,y+33,x+22,y+33),fill=BG,width=3)
    text(d,790,y+4,str(s['max_changes']),50,serif=True,bold=True)
    if s['threshold']==15:
        wrap(d,870,y,'McChesney Park–Townsend; Fayette–Tennyson*',820,33)
    elif len(s['winners'])==1:
        wrap(d,870,y,'State Fair–Court',820,33)
    else:wrap(d,870,y,'Crawford–Comstock; State Fair–Court',820,33)
text(d,65,1000,'*The Tennyson chain changes away from its name, then back again. Both count.',27,MUTED)
wrap(d,65,1055,'A second choice matters too: measure 20 m into each piece instead of 10 m, and only State Fair–Court reaches four at the 30° limit.',1650,31)
text(d,65,1175,'Source: DataCuse calculations from NYS Streets, September 19, 2026 snapshot.',25,MUTED)
im.save(OUT/'angle-rule-comparison.png',optimize=True)
(ROOT/'graphics_audit.json').write_text(json.dumps(dict(maps=audit,sensitivity=R['sensitivity']),indent=2))
print('Saved three graphics')
