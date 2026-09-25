"""Render a real-geography map and the vector map shared by the compass app."""
import json,math,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent; OUT=R.parent/'images'
r=json.loads((R/'results.json').read_text()); boundary=json.loads((R/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']
roads=json.loads((R/'streets_context.geojson').read_text())['features']
BG='#f7f3e8'; INK='#213d32'; MUTED='#616a5e'; TEAL='#207675'; RUST='#a85632'; RULE='#d6d7c9'
def merc(lon,lat):return (6378137*math.radians(lon),6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2)))
def parts(g):
    return g['coordinates'] if g['type'].startswith('Multi') else [g['coordinates']]
polygons=parts(boundary)
pts=[merc(*p) for poly in polygons for ring in poly for p in ring]
cx,cy=merc(r['longitude'],r['latitude'])
minx,miny=min(p[0] for p in pts),min(p[1] for p in pts); maxx,maxy=max(p[0] for p in pts),max(p[1] for p in pts)
mid=((minx+maxx)/2,(miny+maxy)/2); side=max(maxx-minx,maxy-miny)*1.13
bounds=[mid[0]-side/2,mid[1]-side/2,mid[0]+side/2,mid[1]+side/2]
def mapper(bounds,w,h):return lambda x,y:((x-bounds[0])/(bounds[2]-bounds[0])*w,(bounds[3]-y)/(bounds[3]-bounds[1])*h)
def font(size,serif=False,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),size)
def txt(d,x,y,s,size=28,color=INK,bold=False,serif=False,anchor=None):d.text((x,y),s,font=font(size,serif,bold),fill=color,anchor=anchor)
def draw_map(bounds,w,h,detail=False):
    im=Image.new('RGB',(w,h),BG); d=ImageDraw.Draw(im); xy=mapper(bounds,w,h)
    for poly in polygons:
        d.polygon([xy(*merc(*p)) for p in poly[0]],fill='#e6ebdf')
        for hole in poly[1:]: d.polygon([xy(*merc(*p)) for p in hole],fill=BG)
    highlighted={'South McBride Street','Jackson Street','East Adams Street','East Taylor Street','South State Street'}
    for f in roads:
        for line in parts(f['geometry']):
            points=[xy(*merc(*p)) for p in line]
            if max(p[0] for p in points)<0 or min(p[0] for p in points)>w or max(p[1] for p in points)<0 or min(p[1] for p in points)>h:continue
            d.line(points,fill='#9cae9b' if detail else '#c1cbbb',width=3 if detail else 1)
            if detail and f['properties']['name'] in highlighted: d.line(points,fill='#647b67',width=5)
    for poly in polygons:
        for ring in poly:d.line([xy(*merc(*p)) for p in ring],fill=INK,width=3)
    px,py=xy(cx,cy)
    d.ellipse((px-19,py-19,px+19,py+19),fill=BG,outline=RUST,width=3)
    d.line((px-28,py,px+28,py),fill=RUST,width=3); d.line((px,py-28,px,py+28),fill=RUST,width=3)
    d.ellipse((px-6,py-6,px+6,py+6),fill=RUST)
    txt(d,26,22,'N ↑',27,bold=True)
    metres=100 if detail else 1609.344
    length=metres/math.cos(math.radians(r['latitude']))/(bounds[2]-bounds[0])*w
    sy=h-48; d.rectangle((20,sy-25,30+length+100,h-14),fill=BG)
    d.line((30,sy,30+length,sy),fill=INK,width=4)
    txt(d,30,sy-31,'100 m' if detail else '1 mile',23)
    return im
W,H=2200,1740
im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
txt(d,70,52,'SYRACUSE / FINDING OUR BALANCE',29,MUTED,True)
txt(d,66,116,'The center of attention.',105,serif=True,bold=True)
txt(d,72,260,'A balance point near South McBride and Jackson streets.',39)
main=draw_map(bounds,1140,1140);im.paste(main,(60,370));d=ImageDraw.Draw(im)
px,py=mapper(bounds,1140,1140)(cx,cy);px+=60;py+=370
d.line((px+22,py,1050,py,1220,515),fill=RUST,width=3)
txt(d,1260,385,'THE CALCULATED CENTER',28,RUST,True)
txt(d,1260,435,f"{r['latitude']:.5f}° N",65,serif=True,bold=True)
txt(d,1260,515,f"{abs(r['longitude']):.5f}° W",65,serif=True,bold=True)
txt(d,1260,630,'Zoom in',33,bold=True)
zoom_side=650
zoom_bounds=[cx-zoom_side/2,cy-zoom_side*700/840/2,cx+zoom_side/2,cy+zoom_side*700/840/2]
zoom=draw_map(zoom_bounds,840,700,True); zd=ImageDraw.Draw(zoom)
zxy=mapper(zoom_bounds,840,700)
# Anchor street labels on the nearest segment of each named street.
for name,label,at in [('South McBride Street','S. McBride St.',(20,190)),('Jackson Street','Jackson St.',(490,105)),('East Adams Street','E. Adams St.',(465,38)),('South State Street','S. State St.',(18,515))]:
    candidates=[f for f in roads if f['properties']['name']==name]
    candidates.sort(key=lambda f:min((merc(*p)[0]-cx)**2+(merc(*p)[1]-cy)**2 for line in parts(f['geometry']) for p in line))
    if not candidates:continue
    line=parts(candidates[0]['geometry'])[0]; p=min(line,key=lambda p:(merc(*p)[0]-cx)**2+(merc(*p)[1]-cy)**2); ax,ay=zxy(*merc(*p))
    if not (0<=ax<=840 and 0<=ay<=700):continue
    x,y=at; tw=zd.textlength(label,font=font(25,bold=True))+20
    zd.line((ax,ay,x+tw/2,y+17),fill=INK,width=2);zd.ellipse((ax-4,ay-4,ax+4,ay+4),fill=INK)
    zd.rectangle((x,y,x+tw,y+36),fill=BG);txt(zd,x+10,y+3,label,25,bold=True)
im.paste(zoom,(1260,690));d=ImageDraw.Draw(im)
d.rectangle((1260,690,2100,1390),outline=RULE,width=2)
txt(d,1260,1424,'Full municipal area, including water.',28,bold=True)
txt(d,1260,1470,'The point is a calculation, not a city marker.',27,MUTED)
d.line((70,1560,2130,1560),fill=RULE,width=2)
txt(d,70,1590,'Imagine cutting Syracuse out of cardboard. This is where the flat shape would balance.',33,serif=True)
txt(d,70,1650,'NYS Civil Boundaries · downloaded Sept. 24, 2026 · Street context: NYS Streets, Sept. 19, 2026.',25,MUTED)
im.save(OUT/'syracuse-balance-point.png',optimize=True)
# App map: embed local vectors so no third-party map requests receive a visitor location.
xy=mapper(bounds,900,900)
def svg_path(lines,closed=False):
    return ' '.join('M'+' L'.join(f'{xy(*merc(*p))[0]:.1f},{xy(*merc(*p))[1]:.1f}' for p in line)+(' Z' if closed else '') for line in lines)
svg='<g aria-hidden="true"><path d="'+svg_path([ring for poly in polygons for ring in poly],True)+'" fill="#e6ebdf" fill-rule="evenodd" stroke="#213d32" stroke-width="2"/>'
all_lines=[line for f in roads for line in parts(f['geometry'])]
svg+='<path d="'+svg_path(all_lines)+'" fill="none" stroke="#b2c0ac" stroke-width="0.8"/>'
for name in ['South Salina Street','James Street','Erie Boulevard East','West Genesee Street']:
    ls=[line for f in roads if f['properties']['name']==name for line in parts(f['geometry'])]
    svg+='<path d="'+svg_path(ls)+'" fill="none" stroke="#6b8069" stroke-width="1.5"/>'
for name in ['South Salina Street','James Street','Erie Boulevard East','West Genesee Street']:
    points=[p for f in roads if f['properties']['name']==name for line in parts(f['geometry']) for p in line]
    points.sort(key=lambda p:p[1])
    p=points[len(points)//2]; x,y=xy(*merc(*p))
    short=name.replace('South ','S. ').replace('West ','W. ').replace('Street','St.').replace('Boulevard East','Blvd. E.')
    svg+=f'<text class="road-label" x="{x+6:.1f}" y="{y-8:.1f}" font-size="23">{html.escape(short)}</text>'
svg+='</g>'
(R/'app-map.svg').write_text(svg)
(R/'map_config.json').write_text(json.dumps({'bounds':bounds,'center':{'lat':r['latitude'],'lon':r['longitude']},'width':900,'height':900}))
print('Saved article PNG, app vector map and map configuration')

