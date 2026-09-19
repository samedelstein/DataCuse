"""Render the shortest-street story map in the Oak Street editorial style.

Map geometry is from NYS; no illustrated mark invents a geographic location.
"""
import json,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
from shapely.geometry import box,Point
from shapely.ops import unary_union
from map_design_data import ROOT,OUT,T,B,BOUNDS,ZOOM,tile_pixel,load_features

BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9'
GREEN='#316b4d';TEAL='#207675';ORANGE='#a85632';GOLD='#996327';OLIVE='#697541'
W,H=2400,2450
MX,MY,MS=80,485,1480
FONT_DIR='C:/Windows/Fonts/'

def font(size,serif=False,bold=False):
    name='georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'
    return ImageFont.truetype(FONT_DIR+name,size)

canvas=Image.new('RGB',(W,H),BG)
d=ImageDraw.Draw(canvas)
def text(x,y,value,size=30,color=INK,serif=False,bold=False,anchor=None):
    d.text((x,y),value,font=font(size,serif,bold),fill=color,anchor=anchor)

def line_geo(draw,geo,mapper,color,width):
    if geo.is_empty:return
    if geo.geom_type in ('LineString','LinearRing'):
        draw.line([mapper(x,y) for x,y in geo.coords],fill=color,width=width,joint='curve')
    elif hasattr(geo,'geoms'):
        for g in geo.geoms:line_geo(draw,g,mapper,color,width)

def polygon_mask(geo,mapper,size):
    mask=Image.new('L',size,0);md=ImageDraw.Draw(mask)
    for poly in (list(geo.geoms) if geo.geom_type=='MultiPolygon' else [geo]):
        md.polygon([mapper(x,y) for x,y in poly.exterior.coords],fill=255)
        for hole in poly.interiors:md.polygon([mapper(x,y) for x,y in hole.coords],fill=0)
    return mask

def basemap():
    left,bottom=tile_pixel(BOUNDS[0],BOUNDS[1]);right,top=tile_pixel(BOUNDS[2],BOUNDS[3])
    x0,y0=math.floor(left/256),math.floor(top/256)
    x1,y1=math.floor(right/256),math.floor(bottom/256)
    mosaic=Image.new('RGB',((x1-x0+1)*256,(y1-y0+1)*256),BG)
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            mosaic.paste(Image.open(ROOT/'map_tiles'/f'{ZOOM}-{x}-{y}.png'),((x-x0)*256,(y-y0)*256))
    crop=mosaic.crop((left-x0*256,top-y0*256,right-x0*256,bottom-y0*256)).resize((MS,MS),Image.Resampling.LANCZOS)
    gray=ImageOps.grayscale(crop).convert('RGB')
    quiet=Image.blend(gray,Image.new('RGB',(MS,MS),BG),.48)
    outside=Image.blend(quiet,Image.new('RGB',(MS,MS),BG),.62)
    mapper=lambda x,y:((x-BOUNDS[0])/(BOUNDS[2]-BOUNDS[0])*MS,(BOUNDS[3]-y)/(BOUNDS[3]-BOUNDS[1])*MS)
    mask=polygon_mask(B,mapper,(MS,MS))
    quiet=Image.composite(quiet,outside,mask)
    md=ImageDraw.Draw(quiet)
    for poly in (list(B.geoms) if B.geom_type=='MultiPolygon' else [B]):line_geo(md,poly.exterior,mapper,'#7d8c7c',3)
    return quiet,mapper

features=load_features()
byid={p['NYSStreetID']:(p,g) for p,g in features}
streets={name:unary_union([g for p,g in features if p['CompleteStreetName']==name]).intersection(B) for name in
    ('Fay Road','Lea Lane','Spring Lane','Pond Lane','South Avenue','Hovey Street','Marginal Street','Oak Street','Erie Boulevard East','Erie Boulevard West')}
map_image,map_pixel=basemap()
md=ImageDraw.Draw(map_image)
for name,color in [('Fay Road',GREEN),('Lea Lane',GREEN),('Spring Lane',TEAL),('Oak Street',OLIVE),('Erie Boulevard East',GOLD),('Erie Boulevard West',GOLD)]:
    line_geo(md,streets[name],map_pixel,BG,11)
    line_geo(md,streets[name],map_pixel,color,6)
link=byid['800051053'][1]
line_geo(md,link,map_pixel,ORANGE,7)
canvas.paste(map_image,(MX,MY));d=ImageDraw.Draw(canvas)
d.rectangle((MX,MY,MX+MS,MY+MS),outline=RULE,width=2)

text(80,62,'SYRACUSE / LITTLE STREETS, BIG QUESTIONS',29,MUTED,bold=True)
text(75,130,'Syracuse takes',111,serif=True,bold=True)
text(75,264,'the short way home.',111,serif=True,bold=True)
text(82,415,'Two seven-letter names. One little lane. And a very short story in the data.',35)

callout_data=[]
def sign(name,detail,geo,pos,color,width=330):
    # Put the point on the line (not a multipart centroid that could fall elsewhere).
    point=geo.interpolate(geo.length/2) if geo.geom_type=='LineString' else min(geo.geoms,key=lambda g:g.distance(geo.centroid)).interpolate(.5,normalized=True)
    px,py=map_pixel(point.x,point.y);px+=MX;py+=MY
    x,y=MX+pos[0],MY+pos[1];h=100
    endx=max(x,min(px,x+width));endy=max(y,min(py,y+h))
    d.line((px,py,endx,endy),fill=color,width=3)
    d.ellipse((px-9,py-9,px+9,py+9),fill=color,outline=BG,width=3)
    # Road-sign-like callout, deliberately offset from the point and leader-linked.
    d.rounded_rectangle((x,y,x+width,y+h),radius=9,fill=color)
    d.rounded_rectangle((x+5,y+5,x+width-5,y+h-5),radius=6,outline=BG,width=2)
    size=27
    while d.textlength(name,font=font(size,bold=True))>width-34:size-=1
    text(x+17,y+13,name,size,BG,bold=True)
    text(x+17,y+55,detail,24,BG)
    callout_data.append(dict(name=name,detail=detail,point_3857=[point.x,point.y],label_offset_pixels=pos))

sign('FAY ROAD','7 letters',streets['Fay Road'],(25,850),GREEN,265)
sign('LEA LANE','7 letters',streets['Lea Lane'],(1080,135),GREEN,280)
sign('SPRING LANE','~64 ft in state data',streets['Spring Lane'],(290,50),TEAL,350)
sign('OAK STREET','9 letters · 1.44 miles',streets['Oak Street'],(1040,460),OLIVE,350)
sign('ERIE BOULEVARD WEST','4 letters + 9 + direction',streets['Erie Boulevard West'],(20,380),GOLD,415)
sign('ERIE BOULEVARD EAST','4 letters + 9 + direction',streets['Erie Boulevard East'],(1020,810),GOLD,415)
sign('SOUTH AVENUE','~16 ft mapped link',link,(410,1095),ORANGE,370)

# City outline key, ground scale and north arrow, all inside the map.
d.rounded_rectangle((MX+25,MY+MS-140,MX+450,MY+MS-25),radius=6,fill=BG)
text(MX+45,MY+MS-126,'N ↑   Syracuse city limits',25,bold=True)
scale_pixels=1000/math.cos(math.radians(43.04))/(BOUNDS[2]-BOUNDS[0])*MS
sx,sy=MX+47,MY+MS-52
d.line((sx,sy,sx+scale_pixels,sy),fill=INK,width=4)
d.line((sx,sy-7,sx,sy+7),fill=INK,width=3);d.line((sx+scale_pixels,sy-7,sx+scale_pixels,sy+7),fill=INK,width=3)
text(sx+scale_pixels+15,sy,'1 km',23,anchor='lm')

SX=1640
text(SX,490,'THE SHORT LIST',29,MUTED,bold=True)
text(SX,557,'01 / FULL NAME',26,GREEN,bold=True)
text(SX,604,'7',108,GREEN,serif=True,bold=True)
text(SX+85,670,'letters apiece',34,GREEN)

def tiles(value,x,y,color,size=45,gap=5):
    for letter in value:
        if letter==' ':x+=18;continue
        d.rounded_rectangle((x,y,x+size,y+size+7),radius=5,fill=color)
        text(x+size/2,y+(size+7)/2-1,letter,28,BG,bold=True,anchor='mm')
        x+=size+gap
tiles('FAY ROAD',SX,752,GREEN)
tiles('LEA LANE',SX,824,GREEN)
text(SX,902,'Count every letter. Skip spaces.',28,MUTED)
d.line((SX,965,2320,965),fill=RULE,width=2)

manifest={r['name']:r for r in json.loads((ROOT/'imagery_sources.json').read_text())}
def inset(name,slug,feature_id,x,y,width,height,half_width,labels,color):
    p,g=byid[feature_id];cx,cy=g.centroid.x,g.centroid.y
    half_height=half_width*height/width
    bounds=(cx-half_width,cy-half_height,cx+half_width,cy+half_height)
    orig=manifest[name]['bounds_3857']
    raw=Image.open(OUT/(slug+'_aerial.png'))
    def orig_pixel(a,b):return ((a-orig[0])/(orig[2]-orig[0])*raw.width,(orig[3]-b)/(orig[3]-orig[1])*raw.height)
    left,top=orig_pixel(bounds[0],bounds[3]);right,bottom=orig_pixel(bounds[2],bounds[1])
    im=raw.crop((left,top,right,bottom)).resize((width,height),Image.Resampling.LANCZOS)
    im=Image.blend(ImageOps.grayscale(im).convert('RGB'),Image.new('RGB',im.size,BG),.37)
    draw=ImageDraw.Draw(im)
    mapper=lambda a,b:((a-bounds[0])/(bounds[2]-bounds[0])*width,(bounds[3]-b)/(bounds[3]-bounds[1])*height)
    for label,tx,ty in labels:
        for pp,gg in features:
            if pp['CompleteStreetName']==label and gg.intersects(box(*bounds)):
                line_geo(draw,gg.intersection(box(*bounds)),mapper,'#fbf7ea',3)
        draw.rounded_rectangle((tx-5,ty-3,tx+draw.textlength(label,font=font(21))+7,ty+25),radius=2,fill=BG)
        draw.text((tx,ty),label,font=font(21),fill=INK)
    line_geo(draw,g,mapper,BG,10);line_geo(draw,g,mapper,color,6)
    for q in (g.coords[0],g.coords[-1]):
        px,py=mapper(*q);draw.ellipse((px-5,py-5,px+5,py+5),fill=color)
    canvas.paste(im,(x,y));d.rectangle((x,y,x+width,y+height),outline=RULE,width=2)

text(SX,1003,'02 / WHOLE CONNECTED STREET',26,TEAL,bold=True)
text(SX,1050,'Spring Lane',49,TEAL,serif=True,bold=True)
text(SX,1120,'~64 feet. Brief, but to the point.',29)
inset('Spring Lane','spring_lane','477429983',SX,1178,680,260,105,[('Pond Lane',415,50),('Spring Lane',25,175)],TEAL)
text(SX,1460,'NYS estimate; older city map: ~75 ft.',26,MUTED)
d.line((SX,1520,2320,1520),fill=RULE,width=2)

text(SX,1558,'03 / MAPPED JUNCTION LINK',26,ORANGE,bold=True)
text(SX,1607,'South Avenue',49,ORANGE,serif=True,bold=True)
text(SX,1677,'~16 feet. Here is the small print.',29)
inset('South Avenue','south_avenue','800051053',SX,1735,680,200,80,[('Hovey Street',415,8),('Marginal Street',15,157)],ORANGE)
text(SX,1952,'Offset junction. Not a verified city block.',25,MUTED)

text(MX,1995,'Highlights stop at the city line; Fay Road continues west. Labels are offset and connected to mapped locations.',24,MUTED)
d.line((80,2070,2320,2070),fill=RULE,width=2)
text(80,2110,'232',108,GOLD,serif=True,bold=True)
text(330,2120,'names let their endings',42,serif=True)
text(330,2179,'do most of the talking.',42,serif=True)
text(330,2242,'Street-type suffix longer than base name; 1,192 names compared.',26,MUTED)
tiles('ERIE',1620,2112,GOLD,40,4)
tiles('BOULEVARD',1620,2180,GOLD,40,4)
text(1620,2245,'4 letters / 9 letters',26,MUTED)

text(80,2320,'Sources: NYS Streets and Civil Boundaries · Downloaded September 19, 2026 · Insets: NYS 2022 aerial imagery.',25,MUTED)
text(80,2358,'Basemap © OpenStreetMap contributors (openstreetmap.org/copyright). Lengths are GIS estimates, not field measurements.',25,MUTED)
text(80,2396,'Whole-street ranking excludes boundary fragments and reviewed traffic-island pieces. See the accompanying method for scope.',25,MUTED)

OUT.mkdir(exist_ok=True)
canvas.save(OUT/'shortest-streets-map-blog.png',optimize=True)
canvas.resize((1600,round(H*1600/W)),Image.Resampling.LANCZOS).save(OUT/'shortest-streets-map-web.png',optimize=True)
(ROOT/'editorial_map_audit.json').write_text(json.dumps(dict(bounds_3857=BOUNDS,main_map_size_px=MS,projection='EPSG:3857',callouts=callout_data,highlighted_names=list(streets),note='Line locations are exact source geometries. Label locations are offset with leaders; tiny features have symbolic dots. Lengths were calculated separately in EPSG:26918.'),indent=2))
print('Saved 2400-pixel print/blog map and 1600-pixel web map')
