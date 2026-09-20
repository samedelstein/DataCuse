"""Data-driven editorial figures. No generated geography or handwritten results."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from pyproj import Transformer
from shapely.geometry import shape,box,Point
from shapely.ops import transform,unary_union

ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'images';OUT.mkdir(exist_ok=True)
R=json.loads((ROOT/'results.json').read_text());REV=R['reviews']
BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9';GREEN='#316b4d';TEAL='#207675';GOLD='#996327';RUST='#a85632'
T=Transformer.from_crs(4326,3857,always_xy=True).transform
B=transform(T,shape(json.loads((ROOT/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
FS=[(f['properties'],transform(T,shape(f['geometry']))) for f in json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']]
BYID={p['NYSStreetID']:(p,g) for p,g in FS}
def street(name):return unary_union([g for p,g in FS if p['CompleteStreetName'].upper()==name])
def font(size=32,serif=False,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),size)
def line(d,g,xy,color,width=3):
    if g.is_empty:return
    if g.geom_type in ['LineString','LinearRing']:d.line([xy(*p) for p in g.coords],fill=color,width=width,joint='curve')
    else:
        for part in getattr(g,'geoms',[]):line(d,part,xy,color,width)
class Figure:
    def __init__(self,h,kicker,title,subtitle):
        self.im=Image.new('RGB',(2000,h),BG);self.d=ImageDraw.Draw(self.im);self.h=h
        self.text(75,48,'SYRACUSE / '+kicker,27,MUTED,bold=True)
        self.text(70,108,title,86,serif=True,bold=True)
        self.text(76,230,subtitle,32)
    def text(self,x,y,s,size=32,color=INK,serif=False,bold=False):
        self.d.text((x,y),s,font=font(size,serif,bold),fill=color)
    def para(self,x,y,s,width,size=31,color=MUTED,gap=12):
        words=s.split();ln=''
        for word in words:
            test=(ln+' '+word).strip()
            if self.d.textlength(test,font=font(size))>width and ln:
                self.text(x,y,ln,size,color);y+=size+gap;ln=word
            else:ln=test
        if ln:self.text(x,y,ln,size,color);y+=size+gap
        return y
    def rule(self,y):self.d.line((75,y,1925,y),fill=RULE,width=2)
    def footer(self,lines):
        y=self.h-45-len(lines)*37;self.rule(y-25)
        for s in lines:self.text(75,y,s,25,MUTED);y+=37
    def save(self,name):
        self.im.save(OUT/(name+'.png'),optimize=True)
        self.im.resize((1400,round(self.h*.7)),Image.Resampling.LANCZOS).save(OUT/(name+'-web.png'),optimize=True)
def geo_panel(f,rect,bounds,highlights=(),aerial=None):
    x,y,w,h=rect
    if aerial:
        # Crop the raster and its geographic extent together; never stretch geography.
        original=list(bounds);cy=(bounds[1]+bounds[3])/2;half=(bounds[2]-bounds[0])*h/w/2
        bounds=(bounds[0],cy-half,bounds[2],cy+half)
    xy=lambda xx,yy:(x+(xx-bounds[0])/(bounds[2]-bounds[0])*w,y+(bounds[3]-yy)/(bounds[3]-bounds[1])*h)
    area=box(*bounds)
    if aerial:
        source=Image.blend(ImageOps.grayscale(Image.open(aerial)).convert('RGB'),Image.new('RGB',(1200,780),BG),.23)
        top=(original[3]-bounds[3])/(original[3]-original[1])*780;bottom=(original[3]-bounds[1])/(original[3]-original[1])*780
        f.im.paste(source.crop((0,top,1200,bottom)).resize((w,h)),(x,y))
    else:
        f.d.rectangle((x,y,x+w,y+h),fill='#efeee4')
        for p,g in FS:
            if g.intersects(area) and p['FCC'] not in ('A71','A74'):line(f.d,g.intersection(area),xy,'#ccd1c7',2)
    for poly in getattr(B,'geoms',[B]):line(f.d,poly.exterior.intersection(area),xy,RUST,4)
    for g,c,lw in highlights:line(f.d,g.intersection(area),xy,BG,lw+4);line(f.d,g.intersection(area),xy,c,lw)
    f.d.rectangle((x,y,x+w,y+h),outline=RULE,width=2)
    return xy
def label(f,xy,point,x,y,title,detail,color,width=420):
    px,py=xy(point.x,point.y);height=96
    f.d.line((px,py,max(x,min(px,x+width)),max(y,min(py,y+height))),fill=color,width=3)
    f.d.ellipse((px-8,py-8,px+8,py+8),fill=color,outline=BG,width=2)
    f.d.rounded_rectangle((x,y,x+width,y+height),radius=8,fill=color)
    f.d.rounded_rectangle((x+5,y+5,x+width-5,y+height-5),radius=5,outline=BG,width=2)
    f.text(x+16,y+13,title,27,BG,bold=True);f.text(x+16,y+53,detail,25,BG)
def scale(f,xy,bounds,x,y,metres):
    lat=43.04;units=metres/math.cos(math.radians(lat));a=xy(bounds[0],bounds[1])[0];b=xy(bounds[0]+units,bounds[1])[0]
    f.d.line((x,y,x+b-a,y),fill=INK,width=4)
    for xx in (x,x+b-a):f.d.line((xx,y-8,xx,y+8),fill=INK,width=3)
    f.text(x,y-75,'N ↑',27,bold=True);f.text(x+b-a+15,y-17,f'{metres/1000:g} km' if metres>=1000 else f'{metres} m',25)

# 1. Locator map, using the same cached OSM tiles as the companion story.
f=Figure(2060,'THE LONG WAY AROUND','How long is a street?','One mapped piece. One very long name. One road that keeps going.')
bounds=json.loads((ROOT/'editorial_basemap_sources.json').read_text())['bounds_3857'];world=2*math.pi*6378137
def tilepx(x,y):return ((x+world/2)*256*2**14/world,(world/2-y)*256*2**14/world)
left,bottom=tilepx(bounds[0],bounds[1]);right,top=tilepx(bounds[2],bounds[3]);x0,y0=int(left//256),int(top//256);x1,y1=int(right//256),int(bottom//256)
m=Image.new('RGB',((x1-x0+1)*256,(y1-y0+1)*256),BG)
for xx in range(x0,x1+1):
    for yy in range(y0,y1+1):m.paste(Image.open(ROOT/'map_tiles'/f'14-{xx}-{yy}.png'),((xx-x0)*256,(yy-y0)*256))
m=m.crop((left-x0*256,top-y0*256,right-x0*256,bottom-y0*256)).resize((1300,1300),Image.Resampling.LANCZOS)
m=Image.blend(ImageOps.grayscale(m).convert('RGB'),Image.new('RGB',m.size,BG),.43)
f.im.paste(m,(75,360));xy=lambda x,y:(75+(x-bounds[0])/(bounds[2]-bounds[0])*1300,360+(bounds[3]-y)/(bounds[3]-bounds[1])*1300)
for poly in getattr(B,'geoms',[B]):line(f.d,poly.exterior,xy,'#86907e',3)
salina=street('SOUTH SALINA STREET').intersection(B);canal=BYID[R['longest_segments'][0]['source_id']][1];bad=street(R['longest_names'][0]['name'])
for g,c in [(salina,TEAL),(canal,GOLD),(bad,RUST)]:line(f.d,g,xy,BG,11);line(f.d,g,xy,c,7)
label(f,xy,canal.interpolate(.5,normalized=True),880,660,'CANAL STREET','Longest individual feature',GOLD,410)
salina_anchor=salina.interpolate(salina.project(salina.centroid))
label(f,xy,salina_anchor,120,1050,'SOUTH SALINA STREET','4.66 miles inside Syracuse',TEAL,445)
label(f,xy,bad.centroid,890,1230,'EAST BRIGHTON…','The 34-letter data wrinkle',RUST,410)
scale(f,xy,bounds,115,1580,1000)
for yy,kicker,title,value,note,c in [
    (380,'01 / SINGLE FEATURE','Canal Street',f"{R['longest_segments'][0]['inside_ft']:,.0f} ft",'One source feature, about 0.64 mile. Source breaks are not a universal definition of a block.',GOLD),
    (830,'02 / FULL NAME FIELD','A long story','34 letters','East Brighton Avenue Avenue Northbound. Yes, the source repeats Avenue. That needs a footnote.',RUST),
    (1310,'03 / WHOLE STREET','South Salina',f"{REV['SOUTH SALINA STREET']['total_miles']:.2f} miles",'94 mapped pieces, joined. Count stops at the city line, even though South Salina keeps going.',TEAL)]:
    f.text(1430,yy,kicker,25,c,bold=True);f.text(1430,yy+60,title,43,serif=True,bold=True)
    f.text(1430,yy+130,value,66,c,serif=True,bold=True);f.para(1430,yy+235,note,485,29)
f.para(75,1730,'Lengths stop at the Syracuse boundary. Full names keep their directional words. Divided roads get a second look, not double credit.',1850,34,INK)
f.footer(['Source: DataCuse calculations from NYS Streets and city boundary; snapshot September 19, 2026.',
          'Basemap © OpenStreetMap contributors (openstreetmap.org/copyright). GIS estimates; no field measurement.'])
f.save('longest-streets-map')

# 2. Literal field values, with the malformed value visibly retained.
f=Figure(1980,'EVERY LETTER COUNTS','The name goes on. And on.','Count letters in the full name. Keep directions and street types; skip spaces.')
selected=[R['longest_names'][i] for i in [0,1,4,5]]
blocks=[['EAST BRIGHTON','AVENUE AVENUE NORTHBOUND'],['GENANT TO NORTH','CLINTON CONNECTOR'],['ONONDAGA CREEK','BOULEVARD EAST'],['ELIZABETH BLACKWELL','STREET']]
notes=['Literal field winner: repeated Avenue plus a carriageway modifier.',
       '29 letters, but this field describes a connector between two streets.',
       '26 letters in this conventional street-style entry; not a sign survey.',
       '24 letters. A selected comparison, not the fourth-place ranking.']
for i,(r,rows,note) in enumerate(zip(selected,blocks,notes)):
    y=350+i*350;c=RUST if i==0 else TEAL if i==1 else GREEN
    f.text(75,y,r['name'].title(),34,serif=True,bold=True)
    f.text(1740,y+55,str(r['letters']),93,c,serif=True,bold=True)
    for j,s in enumerate(rows):
        x=75
        for ch in s:
            if ch==' ':x+=25;continue
            f.d.rounded_rectangle((x,y+66+j*69,x+49,y+122+j*69),radius=4,fill=c)
            f.text(x+12,y+72+j*69,ch,34,BG,bold=True);x+=57
    f.text(75,y+235,note,29,MUTED);f.rule(y+309)
f.para(75,1760,'The longest database label is clear. The longest name on an actual street sign needs a separate check.',1840,32,INK)
f.footer(['Source: NYS Streets, downloaded September 19, 2026. One tile = one letter.',
          'Source spelling retained. Selected comparisons; these four rows are not a complete ranking.'])
f.save('longest-names-letterboard')

# 3. The single source feature, and honest common-scale street bars.
f=Figure(1840,'ONE PIECE OF THE PUZZLE','Canal Street goes the distance.','The longest individual mapped feature: about 3,359 feet, or 0.64 mile.')
manifest=json.loads((ROOT/'imagery_sources.json').read_text());canal_meta=next(m for m in manifest if m['name']=='Canal Street')
xy2=geo_panel(f,(75,335,1850,760),canal_meta['bounds_3857'],[(canal,GOLD,8)],ROOT/'review/canal_segment_aerial.png')
coords=list(canal.coords)
for pt in [Point(coords[0]),Point(coords[-1])]:
    xx,yy=xy2(pt.x,pt.y);f.d.ellipse((xx-10,yy-10,xx+10,yy+10),fill=GOLD,outline=BG,width=3)
label(f,xy2,Point(coords[0]),115,850,'PEAT STREET END','Mapped endpoint',GOLD,355)
label(f,xy2,Point(coords[-1]),1400,390,'MIDLER / SIMON END','Mapped endpoint',GOLD,420)
f.text(85,1115,'N ↑   NYS 2022 aerial imagery; overlay uses the 2026 street snapshot.',27,MUTED)
for i,r in enumerate(R['longest_segments'][:4]):
    y=1210+i*100;v=r['inside_ft'];end=680+v/3600*1050;c=GOLD if i==0 else '#697c71'
    f.text(75,y,r['name'].title(),34,serif=True,bold=True)
    f.d.rectangle((680,y+8,end,y+53),fill=c)
    for x in range(690,int(end)-20,55):f.d.line((x,y+30,min(x+25,end-5),y+30),fill=BG,width=3)
    f.text(1770,y,f'{v:,.0f}',36,c,serif=True,bold=True)
for v in [0,1000,2000,3000]:
    x=680+v/3600*1050;f.d.line((x,1630,x,1644),fill=MUTED,width=2);f.text(x-10,1650,f'{v:,}',24,MUTED)
f.text(75,1645,'Same zero-based scale / feet',27,MUTED)
f.footer(['Source: NYS Streets, downloaded September 19, 2026; lengths clipped to Syracuse.',
          'A source feature is a database unit. This does not establish the longest conventional city block.'])
f.save('longest-single-segment')

# 4. The double-carriageway correction, from traced data rather than halving a total.
erie=REV['ERIE BOULEVARD EAST'];sal=REV['SOUTH SALINA STREET'];pathmax=max(p['miles'] for p in erie['corridor_paths'])
f=Figure(1720,'TWO WAYS TO ADD IT UP','Erie gets counted twice.','Two carriageways are two mapped lines. They are not two trips across town.')
meta=next(m for m in manifest if m['name']=='Erie Boulevard East')
geo_panel(f,(75,330,1850,610),meta['bounds_3857'],[(street('ERIE BOULEVARD EAST'),GOLD,6)],ROOT/'review/erie_carriageways_aerial.png')
f.text(95,970,'N ↑   Two highlighted carriageways near South Midler Avenue. NYS 2022 aerial.',29,MUTED)
data=[('Erie: add every line',erie['total_miles'],GOLD),('Erie: trace the corridor once',pathmax,RUST),('South Salina: joined length',sal['total_miles'],TEAL)]
for i,(title,v,c) in enumerate(data):
    y=1090+i*125;end=740+v/6*980
    f.text(75,y,title,32,serif=True,bold=True);f.d.rectangle((740,y+5,end,y+57),fill=c)
    for x in range(750,int(end)-20,60):f.d.line((x,y+31,min(x+28,end-5),y+31),fill=BG,width=3)
    f.text(1760,y,f'{v:.2f}',42,c,serif=True,bold=True)
for v in range(7):
    x=740+v/6*980;f.d.line((x,1475,x,1488),fill=MUTED,width=2);f.text(x-8,1502,str(v),25,MUTED)
f.text(75,1497,'Same scale / miles within Syracuse',27,MUTED)
f.footer(['Source: NYS Streets, September 19, 2026. Erie west-to-east paths: 3.571 and 3.575 miles.',
          'Paths follow mapped geometry without traffic-direction restrictions; not driving directions.'])
f.save('erie-double-count')

# 5. Where the name changes versus where the municipal count stops.
f=Figure(1920,'WHERE DOES IT REALLY END?','The road keeps going.','South Salina Street: about 4.66 miles inside Syracuse, from 94 mapped pieces.')
for slug,y,title,detail in [('salina_north',350,'NORTH END / THE NAME CHANGES','At Erie Boulevard, the state data changes from South Salina to North Salina.'),
                           ('salina_south',1050,'SOUTH END / THE COUNT STOPS','Just south of Dorwin Avenue, the city line cuts across a continuing South Salina Street.')]:
    meta=next(m for m in manifest if ('salina_north' if m['bounds_3857'][1]>T(-76.15,43.02)[1] else 'salina_south')==slug and m['name']=='South Salina Street')
    f.text(75,y,title,29,TEAL,bold=True)
    xy3=geo_panel(f,(75,y+60,1120,520),meta['bounds_3857'],[(salina,TEAL,7)],ROOT/'review'/f'{slug}_aerial.png')
    f.para(1260,y+80,detail,650,38,INK)
    f.para(1260,y+280,'Teal = counted South Salina. Rust = Syracuse boundary. N ↑',620,31,TEAL)
    if slug=='salina_south':
        # Show the continuation explicitly, using source geometry outside the city.
        bb=meta['bounds_3857'];cy=(bb[1]+bb[3])/2;half=(bb[2]-bb[0])*520/1120/2
        visible=box(bb[0],cy-half,bb[2],cy+half)
        line(f.d,street('SOUTH SALINA STREET').difference(B).intersection(visible),xy3,GOLD,7)
        f.para(1260,y+405,'Gold = same name, outside the count.',620,31,GOLD)
f.footer(['Source: NYS Streets and city boundary, downloaded September 19, 2026. Imagery: NYS 2022.',
          'Municipal cutoff is not the physical end of the street. No field measurement was performed.'])
f.save('south-salina-endpoints')
(ROOT/'graphics_audit.json').write_text(json.dumps(dict(source='results.json',graphics=[p.name for p in OUT.glob('*.png')],segment_id=R['longest_segments'][0]['source_id'],name_rows=selected,erie_paths=erie['corridor_paths'],salina=sal),indent=2))
print('Saved five full-size figures and five web exports.')
