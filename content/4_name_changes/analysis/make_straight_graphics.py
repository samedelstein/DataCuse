"""Whole-path evidence: equal-scale maps and a signed offset plot."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,box,LineString
from shapely.ops import transform,substring,unary_union
from pyproj import Transformer
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'images'
R=json.loads((ROOT/'straightness_results.json').read_text())
T=Transformer.from_crs(4326,26918,always_xy=True).transform
FS=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'straightness_geometry.geojson').read_text())['features']]
FULL=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'top_chains.geojson').read_text())['features']]
CITY=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'city_comparison_extract.geojson').read_text())['features']]
BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9';TEAL='#207675';GOLD='#996327';RUST='#a85632'
def font(s,serif=False,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),s)
def text(d,x,y,s,size=30,color=INK,serif=False,bold=False):d.text((x,y),s,font=font(size,serif,bold),fill=color)
def wrap(d,x,y,s,width,size=30,color=INK):
    ln=''
    for word in s.split():
        test=(ln+' '+word).strip()
        if d.textlength(test,font=font(size))>width:
            text(d,x,y,ln,size,color);y+=size+12;ln=word
        else:ln=test
    text(d,x,y,ln,size,color)
    return y+size+12
def line(d,g,xy,color,width):
    if g.is_empty:return
    if g.geom_type in ['LineString','LinearRing']:d.line([xy(*p) for p in g.coords],fill=color,width=width,joint='curve')
    else:
        for p in getattr(g,'geoms',[]):line(d,p,xy,color,width)
def projection(g,rect,pad=70):
    x,y,w,h=rect;a,b,c,e=g.bounds;cx=(a+c)/2;cy=(b+e)/2
    scale=min(w/(c-a+2*pad),h/(e-b+2*pad))
    return lambda xx,yy:(x+w/2+(xx-cx)*scale,y+h/2-(yy-cy)*scale),scale

# The full continuous winners versus their endpoint-to-endpoint lines.
im=Image.new('RGB',(1800,1330),BG);d=ImageDraw.Draw(im)
text(d,65,35,'SYRACUSE / CONTINUOUS IS ONLY THE FIRST TEST',25,MUTED,bold=True)
text(d,60,95,'The road keeps going. And bending.',68,serif=True,bold=True)
text(d,65,205,'Teal = whole mapped chain     Gold = straight line connecting its endpoints',31)
for k,record in enumerate(R['full_chains'][:2]):
    parts=sorted([(p,g) for p,g in FULL if p['order']==record['order']],key=lambda z:z[0]['sequence'])
    pts=[]
    for p,g in parts:
        coords=list(g.coords)
        if p['side']:coords.reverse()
        pts+=coords
    g=LineString(pts);chord=LineString([pts[0],pts[-1]])
    x=65+k*865;rect=(x,350,790,680);xy,scale=projection(g,rect)
    text(d,x,285,'Crawford–Comstock' if k==0 else 'State Fair–Court',43,serif=True,bold=True)
    line(d,chord,xy,GOLD,5);line(d,g,xy,TEAL,9)
    for p in (pts[0],pts[-1]):
        xx,yy=xy(*p);d.ellipse((xx-9,yy-9,xx+9,yy+9),fill=INK)
    text(d,x+10,370,'N ↑',26,bold=True)
    d.line((x+25,1020,x+25+500*scale,1020),fill=INK,width=3)
    text(d,x+25,1030,'500 metres',23)
    text(d,x,1090,f"{record['length_m']/1609.344:.2f} miles of road",37,serif=True,bold=True)
    text(d,x,1140,f"{record['chord_m']/1609.344:.2f} miles in a straight line",31)
    text(d,x,1188,f"{record['ratio']:.2f}× the direct distance",31,TEAL,bold=True)
text(d,65,1265,'NYS Streets, September 19, 2026 snapshot. North up; panels have separate scale bars.',25,MUTED)
im.save(OUT/'continuous-versus-straight.png',optimize=True)

# Monticello: mapped street plus all-vertex offset from the endpoint chord.
w=R['sensitivity'][0]['winners'][0];g=next(g for p,g in FS if p['id']==w['id']);pts=list(g.coords)
im=Image.new('RGB',(1800,1530),BG);d=ImageDraw.Draw(im)
text(d,65,35,'SYRACUSE / PUTTING A RULER TO THE ROAD',25,MUTED,bold=True)
text(d,60,95,'Three names. A much straighter story.',65,serif=True,bold=True)
text(d,65,200,'Monticello Drive South → Monticello Drive North → Springbrook Avenue',31)
xy,scale=projection(g,(65,300,560,790),pad=45)
area=g.buffer(180)
for p,h in CITY:line(d,h.intersection(area),xy,'#c8cdc4',3)
chord=LineString([pts[0],pts[-1]]);line(d,chord,xy,GOLD,4)
distance=0;markers=[]
for k,length in enumerate(w['run_lengths_m']):
    line(d,substring(g,distance,distance+length),xy,[RUST,TEAL,'#316b4d'][k],8)
    if k<2:
        point=g.interpolate(distance+length);x,y=xy(point.x,point.y)
        markers.append((x,y,k+1))
    distance+=length
for x,y,num in markers:
    d.ellipse((x-18,y-18,x+18,y+18),fill=BG,outline=INK,width=3)
    d.text((x,y),str(num),anchor='mm',font=font(24,bold=True),fill=INK)
text(d,80,315,'N ↑',26,bold=True)
d.line((95,1040,95+100*scale,1040),fill=INK,width=3);text(d,95,1055,'100 metres',23)
text(d,700,310,'2 name changes',61,TEAL,serif=True,bold=True)
text(d,700,415,f"{w['length_m']:.1f} m along the road",41,serif=True,bold=True)
text(d,700,475,f"{w['chord_m']:.1f} m between endpoints",35)
text(d,700,535,f"Only {(w['ratio']-1)*100:.2f}% extra distance",35,TEAL,bold=True)
text(d,700,640,f"{w['max_offset_m']:.1f} m maximum departure",41,serif=True,bold=True)
wrap(d,700,710,'The entire line stays within 10 metres of its endpoint chord. The allowed extra distance is 1%; this stretch uses about one fifth of that allowance.',990,32)
wrap(d,700,890,'Tested window: 50 m of Monticello South, all of Monticello North, then 50 m of Springbrook. South becomes North at East Seneca Turnpike; Springbrook starts at East Glen Avenue.',990,30)
text(d,65,1135,'DEPARTURE FROM THE STRAIGHT LINE / METRES',25,MUTED,bold=True)
vx=pts[-1][0]-pts[0][0];vy=pts[-1][1]-pts[0][1];length=math.hypot(vx,vy)
x0,y0,pw,ph=145,1195,1550,185
for off in (-10,0,10):
    yy=y0+ph/2-off/20*ph;d.line((x0,yy,x0+pw,yy),fill=GOLD if off==0 else RULE,width=2)
    text(d,75,yy-15,f'{off:+d}',24,MUTED)
plot=[]
for p in pts:
    dx=p[0]-pts[0][0];dy=p[1]-pts[0][1]
    along=(dx*vx+dy*vy)/length;off=(vx*dy-vy*dx)/length
    plot.append((x0+along/length*pw,y0+ph/2-off/20*ph))
d.line(plot,fill=TEAL,width=5)
text(d,x0,1390,'0',23,MUTED);text(d,x0+pw-70,1390,f'{length:.0f} m',23,MUTED)
text(d,65,1450,'Offset plot exaggerates sideways variation; map above preserves geographic scale.',24,MUTED)
text(d,65,1487,'Source: NYS Streets, September 19, 2026. Full recorded names include North and South.',24,MUTED)
im.save(OUT/'monticello-straightness.png',optimize=True)

# The tied inventory anomaly: state name versus older city map.
w=R['sensitivity'][0]['winners'][1]
im=Image.new('RGB',(1800,1000),BG);d=ImageDraw.Draw(im)
text(d,65,35,'SYRACUSE / THE STRAIGHT ROAD WITH A CROOKED LABEL',25,MUTED,bold=True)
text(d,60,95,'Tennyson takes a very brief alias.',73,serif=True,bold=True)
text(d,65,215,'The state inventory inserts Burnet Park Drive for about 44 metres, then returns to Tennyson.',31)
text(d,65,330,'NYS NAME FIELD',27,MUTED,bold=True)
colors=[TEAL,RUST,TEAL];cursor=65;factor=1670/sum(w['run_lengths_m'])
for name,dist,color in zip(w['names'],w['run_lengths_m'],colors):
    width=dist*factor;d.rectangle((cursor,400,cursor+width,510),fill=color)
    label='Burnet Park Drive' if name=='BURNET PARK DRIVE' else 'Tennyson Avenue'
    text(d,cursor+20,420,label,33,BG,serif=True,bold=True)
    text(d,cursor+20,465,f'{dist:.1f} m',27,BG)
    cursor+=width
text(d,65,590,'OLDER CITY MAP',27,MUTED,bold=True)
d.rectangle((65,650,1735,745),fill=TEAL);text(d,90,675,'Tennyson Avenue at all three sampled name-run midpoints',36,BG,serif=True,bold=True)
wrap(d,65,795,'Two state-data name changes; two distinct names. The city-map disagreement leaves a naming discrepancy to resolve before calling these real street-sign changes.',1640,32)
text(d,65,945,'Saved NYS and City of Syracuse street layers, downloaded September 19, 2026. Bar lengths share one scale.',24,MUTED)
im.save(OUT/'tennyson-name-check.png',optimize=True)
(ROOT/'straight_graphics_audit.json').write_text(json.dumps(dict(full_chains=R['full_chains'][:2],baseline_winners=R['sensitivity'][0]['winners']),indent=2))
print('Saved three straightness graphics')
