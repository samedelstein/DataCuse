"""Three editorial graphics with true geometry and audited counts."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform
R=Path(__file__).resolve().parent;OUT=R.parent/'images';r=json.loads((R/'results.json').read_text())
T=Transformer.from_crs(4326,26918,always_xy=True).transform
roads=json.loads((R/'eligible_noded_roads.geojson').read_text())['features'];geos=[transform(T,shape(f['geometry'])) for f in roads]
BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9';COL=['#207675','#a85632','#316b4d','#806484']
def font(n,serif=False,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),n)
def text(d,x,y,s,n=30,color=INK,bold=False,serif=False,anchor=None):d.text((x,y),s,font=font(n,serif,bold),fill=color,anchor=anchor)
def wrap(d,x,y,s,n,width,color=INK,bold=False):
 lines=[];line=''
 for word in s.split():
  test=(line+' '+word).strip()
  if d.textlength(test,font=font(n,bold=bold))>width and line:lines.append(line);line=word
  else:line=test
 if line:lines.append(line)
 for i,line in enumerate(lines):text(d,x,y+i*(n+10),line,n,color,bold)
 return y+len(lines)*(n+10)
def stroke(d,g,xy,color,width):
 for part in getattr(g,'geoms',[g]):
  if part.geom_type=='LineString':d.line([xy(x,y) for x,y in part.coords],fill=color,width=width)
def map_panel(row,w,h,bw,colors,number=False):
 x,y=row['x'],row['y'];bh=bw*h/w;b=[x-bw/2,y-bh/2,x+bw/2,y+bh/2];view=box(*b)
 xy=lambda xx,yy:((xx-b[0])/bw*w,(b[3]-yy)/bh*h)
 m=Image.new('RGB',(w,h),'#e9ece2');d=ImageDraw.Draw(m)
 for g in geos:
  if g.intersects(view):stroke(d,g.intersection(view),xy,'#cbd1c4',3)
 for f,g in zip(roads,geos):
  if f['properties']['name'] in colors and g.intersects(view):stroke(d,g.intersection(view),xy,colors[f['properties']['name']],11)
 arms=sorted(row['incident'],key=lambda a:a['bearing'])
 for i,arm in enumerate(arms,1):
  g=geos[arm['edge']];stroke(d,g.intersection(view),xy,colors[arm['name']],11)
  if number:
   length=min(90,g.length*.85);p=g.interpolate(length if arm['end']==0 else g.length-length);xx,yy=xy(p.x,p.y)
   d.ellipse((xx-23,yy-23,xx+23,yy+23),fill=colors[arm['name']],outline=BG,width=4);text(d,xx,yy,str(i),27,BG,True,anchor='mm')
 xx,yy=xy(x,y);d.ellipse((xx-12,yy-12,xx+12,yy+12),fill=BG,outline=INK,width=4)
 d.rectangle((12,12,100,62),fill=BG);text(d,23,19,'N ↑',29,bold=True)
 scale=100/bw*w;d.rectangle((15,h-90,scale+45,h-12),fill=BG);text(d,25,h-84,'100 metres',25);d.line((25,h-35,25+scale,h-35),fill=INK,width=4)
 return m,arms,b

def head(title,sub,kicker='SYRACUSE / COUNTING THE WAYS',height=1600,size=88):
 im=Image.new('RGB',(2200,height),BG);d=ImageDraw.Draw(im);text(d,65,45,kicker,29,MUTED,True);text(d,60,118,title,size,INK,True,True);text(d,65,247,sub,36);return im,d

def footer(d,y,line1,line2):
 d.line((65,y,2135,y),fill=RULE,width=2);text(d,65,y+25,line1,25,MUTED);text(d,65,y+65,line2,25,MUTED)

six=r['six_way'];palette=dict(zip(six['names'],COL));im,d=head('Six ways. Three street names.','North Salina, Lodi and Kirkpatrick form a six-arm junction.',height=1560)
m,arms,b=map_panel(six,1280,1020,340,palette,True);im.paste(m,(55,360));d=ImageDraw.Draw(im);SX=1450
text(d,SX,370,'6',150,serif=True,bold=True);text(d,SX,550,'separate approaches',40,serif=True)
for i,name in enumerate(six['names']):
 yy=675+i*170;d.ellipse((SX,yy+8,SX+25,yy+33),fill=palette[name]);text(d,SX+45,yy,name.title(),37,palette[name],True,True)
 nums=[str(k) for k,a in enumerate(arms,1) if a['name']==name];text(d,SX+45,yy+59,'Arms '+' + '.join(nums),30,MUTED)
wrap(d,SX,1230,'Each street continues on both sides of the junction.',31,660)
footer(d,1430,'Source: NYS Streets snapshot, Sept. 19, 2026. Six approaches corroborated by city street nodes and NYS 2022 imagery.','North-up map, true geometry. Counts are street approaches, not lanes or permitted driving movements.')
im.save(OUT/'six-ways-three-names.png',optimize=True)

seven=r['seven_line'];im,d=head('Seven lines need a second look.','Hiawatha / North Salina / Lodi: seven lines, four street approaches.',height=1590,size=85)
# Exact georeferenced aerial and matching geometry, without invented streets.
aerial=Image.open(R/'review/candidate-1-aerial.png').convert('RGB');aerial=Image.blend(aerial,Image.new('RGB',aerial.size,BG),.2)
md=ImageDraw.Draw(aerial);manifest=json.loads((R/'imagery_sources.json').read_text())[0];bb=manifest['bounds_3857'];M=Transformer.from_crs(4326,3857,always_xy=True).transform
xy=lambda x,y:((x-bb[0])/(bb[2]-bb[0])*1000,(bb[3]-y)/(bb[3]-bb[1])*1000);palette=dict(zip(seven['names'],COL))
for arm in seven['incident']:
 g=transform(M,shape(roads[arm['edge']]['geometry']));stroke(md,g.intersection(box(*bb)),xy,palette[arm['name']],7)
md.ellipse((489,489,511,511),fill=BG,outline=INK,width=4);md.rectangle((15,15,110,65),fill=BG);text(md,25,20,'N ↑',28,bold=True)
scale=100/math.cos(math.radians(seven['latitude']))/(bb[2]-bb[0])*1000;md.rectangle((15,905,scale+45,985),fill=BG);text(md,25,914,'100 metres',25);md.line((25,963,25+scale,963),fill=INK,width=4)
im.paste(aerial,(55,365));d=ImageDraw.Draw(im);SX=1180
text(d,SX,380,'MAPPED LINES → STREET APPROACHES',27,MUTED,True)
for i,name in enumerate(seven['names']):
 yy=475+i*180;count=sum(a['name']==name for a in seven['incident']);text(d,SX,yy,name.title(),39,palette[name],True,True);text(d,SX,yy+62,f'{count} mapped '+('line' if count==1 else 'lines')+' → 1 approach',32)
text(d,SX,1220,'7 mapped lines. 4 approaches.',40,INK,True,True)
text(d,65,1400,'A split carriageway does not turn one street approach into two.',34,bold=True)
footer(d,1470,'Aerial: NYS 2022 orthophotography. Overlaid lines: NYS Streets, Sept. 19, 2026. North up.','Independent city street topology records four arms here. Nearby ramps and the freeway are outside the street count.')
im.save(OUT/'seven-lines-four-approaches.png',optimize=True)

im,d=head('Four names can take five ways.','Two of the tied name-count leaders show why the two counts differ.',height=1810,size=86)
examples=[next(x for x in r['four_name_leaders'] if 'EUCLID AVENUE' in x['names']),next(x for x in r['four_name_leaders'] if 'DEMONG DRIVE' in x['names'])]
for i,row in enumerate(examples):
 x=55+i*1100;palette=dict(zip(row['names'],COL));m,arms,bounds=map_panel(row,990,780,340,palette);im.paste(m,(x,355));d=ImageDraw.Draw(im)
 text(d,x,1160,f"4 names / {row['arms']} approaches",47,INK,True,True)
 for k,name in enumerate(row['names']):text(d,x,1260+k*69,name.title(),34,palette[name],True)
text(d,65,1590,'Full names count separately, including directions such as East and West.',33)
footer(d,1690,'Source: NYS Streets, Sept. 19, 2026; both examples agree with the city street map. True geometry; north up.','Primary scan: 2,910 nodes with at least three mapped outward arms. Five nodes tie at four full names.')
im.save(OUT/'four-names-two-shapes.png',optimize=True)
(R/'graphics_audit.json').write_text(json.dumps({'hero_node':six['node'],'hero_numbered_arms': [{'number':i,'name':a['name'],'street_id':a['id']} for i,a in enumerate(sorted(six['incident'],key=lambda a:a['bearing']),1)],'seven_line_node':seven['node'],'line_counts_by_name':{name:sum(a['name']==name for a in seven['incident']) for name in seven['names']},'four_name_examples':[row['node'] for row in examples],'calculation_and_map_crs':'EPSG:26918 except aerial overlay EPSG:3857 with ground-corrected scale'},indent=2))
print('Saved three final graphics')

