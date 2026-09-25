"""Draw two evidence graphics from the saved population-center results."""
import json,csv,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;OUT=R.parent/'images'
r=json.loads((R/'results.json').read_text());blocks=list(csv.DictReader((R/'block_centroids.csv').open()))
geo=json.loads((R/'syracuse_place_2020.geojson').read_text())['features'][0]['geometry']
roads=json.loads((R.parents[1]/'5_geographic_center/analysis/streets_context.geojson').read_text())['features']
BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9';TEAL='#207675';RUST='#a85632';GREEN='#316b4d'
def font(n,serif=False,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),n)
def text(d,x,y,s,n=30,color=INK,bold=False,serif=False,anchor=None):d.text((x,y),s,font=font(n,serif,bold),fill=color,anchor=anchor)
def merc(lon,lat):return (6378137*math.radians(lon),6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2)))
def parts(g):return g['coordinates'] if g['type'].startswith('Multi') else [g['coordinates']]
polys=parts(geo);pts=[merc(*p) for poly in polys for ring in poly for p in ring]
px,py=merc(r['longitude'],r['latitude']);prior=r['comparison_with_geographic_center'];gx,gy=merc(prior['longitude'],prior['latitude'])
def fit_bounds(points,w,h,pad=1.08):
    lowx,lowy=min(p[0] for p in points),min(p[1] for p in points);highx,highy=max(p[0] for p in points),max(p[1] for p in points)
    cx,cy=(lowx+highx)/2,(lowy+highy)/2;bw=max(highx-lowx,(highy-lowy)*w/h)*pad;bh=bw*h/w
    return [cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2]
def mapper(b,w,h):return lambda x,y:((x-b[0])/(b[2]-b[0])*w,(b[3]-y)/(b[3]-b[1])*h)
def map_base(b,w,h,detail=False):
    im=Image.new('RGB',(w,h),BG);d=ImageDraw.Draw(im);xy=mapper(b,w,h)
    for poly in polys:
        d.polygon([xy(*merc(*p)) for p in poly[0]],fill='#e7eadf')
        for hole in poly[1:]:d.polygon([xy(*merc(*p)) for p in hole],fill=BG)
    for f in roads:
        for line in parts(f['geometry']):
            coords=[xy(*merc(*p)) for p in line]
            if max(p[0] for p in coords)<0 or min(p[0] for p in coords)>w or max(p[1] for p in coords)<0 or min(p[1] for p in coords)>h:continue
            d.line(coords,fill='#b8c2b0' if detail else '#d0d4c5',width=4 if detail else 1)
    for poly in polys:
        for ring in poly:d.line([xy(*merc(*p)) for p in ring],fill=INK,width=3)
    return im,xy
W,H=2200,1800;im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
text(d,65,45,'SYRACUSE / THE WEIGHT OF THE PEOPLE',29,MUTED,True)
text(d,60,116,'The people move the middle.',91,serif=True,bold=True)
text(d,65,250,'Population center estimated from 2020 Census blocks.',38)
b=fit_bounds(pts,1280,1280);m,xy=map_base(b,1280,1280)
overlay=Image.new('RGBA',m.size,(0,0,0,0));md=ImageDraw.Draw(overlay)
for row in sorted(blocks,key=lambda b:int(b['population']),reverse=True):
    pop=int(row['population'])
    if not pop:continue
    x,y=xy(*merc(float(row['longitude']),float(row['latitude'])));radius=6*math.sqrt(pop/100)
    md.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(49,107,77,140),outline=(33,61,50,170),width=1)
m=Image.alpha_composite(m.convert('RGBA'),overlay).convert('RGB');md=ImageDraw.Draw(m)
x,y=xy(px,py);md.ellipse((x-20,y-20,x+20,y+20),fill=BG,outline=RUST,width=5);md.line((x-32,y,x+32,y),fill=RUST,width=4);md.line((x,y-32,x,y+32),fill=RUST,width=4)
text(md,20,20,'N ↑',29,bold=True)
scale=1609.344/math.cos(math.radians(r['latitude']))/(b[2]-b[0])*1280
md.rectangle((15,1190,scale+50,1270),fill=BG);md.line((25,1245,25+scale,1245),fill=INK,width=4);text(md,25,1200,'1 mile',26)
im.paste(m,(45,375));d=ImageDraw.Draw(im)
# Leader connects the exact computed center to its place label.
d.line((45+x+24,375+y,1380,375+y,1430,995),fill=RUST,width=3)
SX=1450
text(d,SX,390,f"{r['population']:,}",84,serif=True,bold=True)
text(d,SX,495,'counted residents',33)
text(d,SX,560,f"{r['populated_blocks']:,}",70,serif=True,bold=True)
text(d,SX,650,'populated Census blocks',31)
text(d,SX,720,'One circle = one populated block.',27,MUTED)
text(d,SX,762,'Circle area scales with population.',27,MUTED)
for pop,lx in [(25,1490),(100,1680),(400,1900)]:
    radius=6*math.sqrt(pop/100);d.ellipse((lx-radius,850-radius,lx+radius,850+radius),fill=GREEN)
    text(d,lx,888,str(pop),26,anchor='mt')
text(d,SX,955,'ESTIMATED POPULATION CENTER',25,RUST,True)
text(d,SX,1015,'Near Sarah Loguen',40,serif=True,bold=True)
text(d,SX,1070,'and Harrison streets',40,serif=True,bold=True)
text(d,SX,1180,'People give each block its weight.',29)
text(d,SX,1230,'No residents? No weight.',29)
text(d,SX,1320,'Each dot uses a block centroid,',28,MUTED)
text(d,SX,1365,'not a household address.',28,MUTED)
text(d,SX,1450,'This is a 2020 estimate,',28,RUST,True)
text(d,SX,1495,'not a live population map.',28,RUST,True)
d.line((65,1680,2135,1680),fill=RULE,width=2)
text(d,65,1710,'Source: U.S. Census Bureau, 2020 Census blocks and place boundary (TIGERweb), downloaded Sept. 25, 2026 UTC.',25,MUTED)
text(d,65,1750,'DataCuse calculation · Whole block populations placed at geometric centroids · Street context: NYS, Sept. 19, 2026.',25,MUTED)
im.save(OUT/'population-balance-map.png',optimize=True)
# A second graphic answers the distinct comparison question at neighborhood scale.
W,H=2200,1680;im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
text(d,65,45,'SYRACUSE / TWO WAYS TO FIND THE MIDDLE',29,MUTED,True)
text(d,60,112,'Same city. Different balance.',91,serif=True,bold=True)
text(d,65,248,'Weight the land area, then weight the people counted in 2020.',37)
# 900 Web Mercator metres wide; the scale bar converts to local ground distance.
bw=1100;bh=bw*1150/1370;mx,my=(px+gx)/2,(py+gy)/2
b=[mx-bw/2,my-bh/2,mx+bw/2,my+bh/2]
m,xy=map_base(b,1370,1150,True);md=ImageDraw.Draw(m)
a=xy(gx,gy);z=xy(px,py)
md.line((*a,*z),fill=RUST,width=5)
# Arrowhead follows the actual connector, north-up.
angle=math.atan2(z[1]-a[1],z[0]-a[0]);length=23
md.polygon([z,(z[0]-length*math.cos(angle-.45),z[1]-length*math.sin(angle-.45)),(z[0]-length*math.cos(angle+.45),z[1]-length*math.sin(angle+.45))],fill=RUST)
for p,color in [(a,TEAL),(z,RUST)]:md.ellipse((p[0]-14,p[1]-14,p[0]+14,p[1]+14),fill=color,outline=BG,width=4)
text(md,22,22,'N ↑',29,bold=True)
# Exact named-road anchors; labels offset with visible leaders.
labels=[('Harrison Street','Harrison St.',(710,90),(px,py)),('Sarah Loguen Street','Sarah Loguen St.',(910,240),(px,py)),('East Adams Street','E. Adams St.',(970,610),(px,py)),('Jackson Street','Jackson St.',(35,930),(gx,gy)),('South McBride Street','S. McBride St.',(35,690),(gx,gy))]
for name,label,(lx,ly),target in labels:
    candidates=[f for f in roads if f['properties']['name']==name]
    points=[p for f in candidates for line in parts(f['geometry']) for p in line]
    point=min(points,key=lambda p:(merc(*p)[0]-target[0])**2+(merc(*p)[1]-target[1])**2)
    tx,ty=xy(*merc(*point));tw=md.textlength(label,font=font(27,bold=True))+24
    if not(0<=tx<=1370 and 0<=ty<=1150):continue
    md.line((tx,ty,lx+tw/2,ly+19),fill=MUTED,width=2);md.ellipse((tx-4,ty-4,tx+4,ty+4),fill=MUTED)
    md.rectangle((lx,ly,lx+tw,ly+40),fill=BG);text(md,lx+12,ly+4,label,27,bold=True)
scale=200/math.cos(math.radians(r['latitude']))/bw*1370
md.rectangle((20,1040,scale+50,1130),fill=BG);md.line((30,1100,30+scale,1100),fill=INK,width=4);text(md,30,1054,'200 metres',26)
im.paste(m,(45,365));d=ImageDraw.Draw(im)
SX=1470
text(d,SX,390,'ABOUT',27,MUTED,True)
text(d,SX,445,f"{prior['distance_miles']:.2f}",120,RUST,True,True)
text(d,SX,580,'mile northeast',43,serif=True)
text(d,SX,646,f"{prior['distance_metres']:.0f} metres in a straight line",28,MUTED)
d.line((SX,740,2140,740),fill=RULE,width=2)
d.ellipse((SX,806,SX+24,830),fill=TEAL);text(d,SX+43,795,'Geographic center',37,TEAL,True,True)
text(d,SX,862,'The full municipal area',29)
text(d,SX,907,'gets equal weight per acre.',29)
text(d,SX,960,'Near South McBride / Jackson',26,MUTED)
d.ellipse((SX,1076,SX+24,1100),fill=RUST);text(d,SX+43,1065,'Population center',37,RUST,True,True)
text(d,SX,1132,'Each counted resident',29)
text(d,SX,1177,'gets equal weight.',29)
text(d,SX,1230,'Near Sarah Loguen / Harrison',26,MUTED)
text(d,SX,1350,'Map points are estimates,',29,bold=True)
text(d,SX,1395,'not marked visitor destinations.',28)
d.line((65,1550,2135,1550),fill=RULE,width=2)
text(d,65,1580,'Population: 2020 Census block-centroid estimate. Geographic center: full NYS municipal boundary used in the previous story.',25,MUTED)
text(d,65,1620,'Source: U.S. Census Bureau; NYS Civil Boundaries and Streets. North-up map. Road context is a September 2026 snapshot.',25,MUTED)
im.save(OUT/'two-centers-comparison.png',optimize=True)
(R/'graphics_audit.json').write_text(json.dumps({'population_dots':r['populated_blocks'],'represented_population':r['population'],'dot_radius_pixels':'6 * sqrt(population / 100)','zero_population_blocks_omitted':r['zero_population_blocks'],'comparison_bounds_3857':b,'comparison_map_px':[1370,1150],'distance_metres':prior['distance_metres'],'display_projection':'EPSG:3857 with ground-corrected scale bars','calculation_projection':'EPSG:26918'},indent=2))
print('Saved population map and two-center comparison')
