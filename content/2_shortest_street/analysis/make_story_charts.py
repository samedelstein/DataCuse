"""Four data-driven editorial graphics; regenerate from saved CSVs and geometry.

Letter tiles and road-shaped bars are charts, not illustrations of physical signs
or pavement. Oak Street's map uses the source geometry in EPSG:26918.
"""
import csv
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
from shapely.geometry import shape, box, Point
from shapely.ops import transform, unary_union

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'images'
BG='#f7f3e8';INK='#213d32';MUTED='#616a5e';RULE='#d6d7c9'
GREEN='#316b4d';TEAL='#207675';GOLD='#996327';ORANGE='#a85632'
SOURCE='Source: DataCuse calculations from NYS Streets, downloaded September 19, 2026.'

def read_csv(name):
    with (ROOT/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
names={r['name']:r for r in read_csv('name_rankings.csv')}
whole=read_csv('whole_street_candidates.csv')
components=read_csv('connected_street_rankings.csv')
raw=read_csv('raw_segment_rankings.csv')

def font(size,serif=False,bold=False):
    f='georgiab.ttf' if serif and bold else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'
    return ImageFont.truetype('C:/Windows/Fonts/'+f,size)

class Graphic:
    def __init__(self,height,kicker,title,subtitle):
        self.im=Image.new('RGB',(2000,height),BG)
        self.d=ImageDraw.Draw(self.im)
        self.text(80,48,kicker,26,MUTED,bold=True)
        for i,line in enumerate(title.split('\n')):self.text(76,113+i*101,line,88,serif=True,bold=True)
        self.text(80,346,subtitle,30)
    def text(self,x,y,s,size=30,color=INK,serif=False,bold=False,anchor=None):
        self.d.text((x,y),s,font=font(size,serif,bold),fill=color,anchor=anchor)
    def rule(self,y):self.d.line((80,y,1920,y),fill=RULE,width=2)
    def tiles(self,s,x,y,color,size=54,gap=6):
        for c in s:
            if c==' ':x+=22;continue
            assert c.isalpha(),s
            self.d.rounded_rectangle((x,y,x+size,y+size+9),radius=6,fill=color)
            self.text(x+size/2,y+(size+9)/2-1,c,round(size*.60),BG,bold=True,anchor='mm')
            x+=size+gap
        return x
    def save(self,name):
        self.im.save(OUT/(name+'.png'),optimize=True)
        self.im.resize((1400,round(self.im.height*.7)),Image.Resampling.LANCZOS).save(OUT/(name+'-web.png'),optimize=True)

audit={}

# 1. Full-name counts. Selected comparisons, not a misleading complete top-four list.
g=Graphic(1390,'SYRACUSE / EVERY LETTER COUNTS','Small names.\nFull credit.','The street type counts, too. Spaces and punctuation do not.')
g.text(80,428,'STREET NAME',24,MUTED,bold=True)
g.text(615,428,'ONE TILE = ONE LETTER',24,MUTED,bold=True)
g.text(1860,428,'TOTAL',24,MUTED,bold=True,anchor='ra')
selected=['FAY ROAD','LEA LANE','OAK PLACE','OAK STREET']
audit['full_names']=[]
for i,name in enumerate(selected):
    r=names[name];y=496+i*169
    g.text(80,y+5,name.title(),40,serif=True,bold=True)
    g.text(80,y+64,'Tied for shortest' if i<2 else 'For comparison',25,MUTED)
    end=g.tiles(r['base'],615,y,GREEN)
    g.tiles(r['suffix'],end+18,y,TEAL)
    g.text(1810,y-7,r['full_characters'],69,serif=True,bold=True)
    assert int(r['full_characters'])==len(r['base'])+len(r['suffix'])
    g.rule(y+130)
    audit['full_names'].append(r)
g.text(80,1212,'Fay Road and Lea Lane take the shortest route through the alphabet.',31,serif=True)
g.text(80,1282,SOURCE,24,MUTED)
g.text(80,1318,'Full expanded names, including directions when present. Selected comparisons; all seven-letter ties are shown.',24,MUTED)
g.save('shortest-names-letterboard')

# 2. Street type/base comparison has a different denominator from the full-name race.
g=Graphic(1580,'SYRACUSE / BIG ENDING ENERGY','These endings\ntake the long way.','When the street type has more letters than the name it follows.')
g.text(80,435,'STREET',24,MUTED,bold=True)
g.text(600,435,'BASE NAME',24,GREEN,bold=True)
g.text(1060,435,'STREET TYPE',24,GOLD,bold=True)
g.text(1870,435,'EXTRA',24,MUTED,bold=True,anchor='ra')
audit['suffix_comparisons']=[]
for i,name in enumerate(['ERIE BOULEVARD EAST','GRANT BOULEVARD','OAK STREET','LEA LANE']):
    r=names[name];y=510+i*175
    title=name.title()
    if name=='ERIE BOULEVARD EAST':
        g.text(80,y,title.replace(' East',''),34,serif=True,bold=True)
        g.text(80,y+48,'East (West has the same split)',23,MUTED)
    else:g.text(80,y+10,title,34,serif=True,bold=True)
    g.tiles(r['base'],600,y,GREEN,43,5)
    g.tiles(r['suffix'],1060,y,GOLD,43,5)
    g.text(600,y+69,r['base_characters']+' letters',23,MUTED)
    g.text(1060,y+69,r['suffix_characters']+' letters',23,MUTED)
    g.text(1820,y,'+'+r['suffix_minus_base'],55,GOLD,serif=True,bold=True,anchor='ra')
    g.rule(y+136)
    audit['suffix_comparisons'].append(r)
n=len(names);longer=sum(int(r['suffix_minus_base'])>0 for r in names.values())
assert longer==232 and n==1192
g.text(80,1260,str(longer),92,GOLD,serif=True,bold=True)
g.text(320,1266,'of 1,192 qualifying names have a longer ending.',33,serif=True)
g.text(320,1320,f'That is {100*longer/n:.1f}%. The suffix has a lot to say.',29,MUTED)
g.text(80,1430,SOURCE,24,MUTED)
g.text(80,1470,'Count expanded street types. Directional words remain in full names but are excluded from this base/type comparison.',23,MUTED)
g.save('street-suffixes-long-way')

# 3. Common-scale bar chart dressed as road strips. Differences are intentionally small.
g=Graphic(1530,'SYRACUSE / SMALL STREETS, SAME RULER','Short streets.\nNo victory lap required.','Four leading whole-street candidates in the state map. Lengths are approximate.')
x0=540;scale=14.0
g.text(80,435,'CONNECTED STREET',24,MUTED,bold=True)
g.text(x0,435,'CENTERLINE LENGTH / FEET',24,MUTED,bold=True)
g.text(1905,435,'FEET',24,MUTED,bold=True,anchor='ra')
audit['length_comparisons']=[]
for i,r in enumerate(whole[:4]):
    assert r['components_in_city']=='1' and r['wholly_inside']=='True'
    y=530+i*177;value=float(r['length_ft']);end=x0+value*scale
    g.text(80,y+8,r['name'].title(),37,serif=True,bold=True)
    color=TEAL if i==0 else '#697c71'
    g.d.rectangle((x0,y,end,y+65),fill=color)
    for start in range(x0+10,int(end)-5,54):
        g.d.line((start,y+32,min(start+29,end-8),y+32),fill=BG,width=4)
    g.d.line((end,y-6,end,y+71),fill=color,width=3)
    g.text(1880,y-2,f'{value:.1f}',52,color,serif=True,bold=True,anchor='ra')
    if i==0:
        mark=x0+75*scale
        g.d.line((mark,y-16,mark,y+80),fill=ORANGE,width=3)
        g.text(mark,y+88,'~75 ft in the older city map',24,ORANGE,anchor='ma')
    audit['length_comparisons'].append(r)
axis_y=1225
g.d.line((x0,axis_y,x0+85*scale,axis_y),fill=MUTED,width=2)
for value in (0,20,40,60,80):
    x=x0+value*scale;g.d.line((x,axis_y-8,x,axis_y+8),fill=MUTED,width=2)
    g.text(x,axis_y+18,str(value),24,MUTED,anchor='ma')
g.text(80,1330,'The map gives Spring Lane the lead. A field measurement could change the order.',30,serif=True)
g.text(80,1410,SOURCE,24,MUTED)
g.text(80,1450,'Same zero-based scale. Whole streets lie within Syracuse; boundary fragments and reviewed traffic-island arcs excluded.',23,MUTED)
g.save('short-streets-same-ruler')

# 4. Geometry-led explanation: the smallest Oak feature is not the whole road.
project=Transformer.from_crs(4326,26918,always_xy=True).transform
fs=json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']
all_roads=[(f['properties'],transform(project,shape(f['geometry']))) for f in fs]
oak=[(p,line) for p,line in all_roads if p['CompleteStreetName']=='Oak Street']
oak_total=next(r for r in components if r['name']=='OAK STREET')
ids=set(oak_total['source_ids'].split(';'))
oak=[(p,line) for p,line in oak if p['NYSStreetID'] in ids]
assert len(oak)==22
geo=unary_union([line for p,line in oak])
small=min(oak,key=lambda item:item[1].length)
small_ft=small[1].length/.3048
g=Graphic(1680,'SYRACUSE / A PIECE IS NOT THE WHOLE STREET','One name.\nTwenty-two pieces.','Oak Street looks much longer when you connect the dots.')
panel=(80,445,880,1450)
cx,cy=geo.centroid.x,geo.centroid.y
span_y=(geo.bounds[3]-geo.bounds[1])*1.15
span_x=span_y*(panel[2]-panel[0])/(panel[3]-panel[1])
bounds=(cx-span_x/2,cy-span_y/2,cx+span_x/2,cy+span_y/2)
mapper=lambda x,y:(panel[0]+(x-bounds[0])/(bounds[2]-bounds[0])*(panel[2]-panel[0]),panel[3]-(y-bounds[1])/(bounds[3]-bounds[1])*(panel[3]-panel[1]))
g.d.rectangle(panel,fill='#ecebdd',outline=RULE,width=2)
def draw_geo(line,color,width):
    if line.is_empty:return
    if line.geom_type=='LineString':g.d.line([mapper(x,y) for x,y in line.coords],fill=color,width=width,joint='curve')
    elif hasattr(line,'geoms'):
        for part in line.geoms:draw_geo(part,color,width)
for p,line in all_roads:
    if line.intersects(box(*bounds)) and p['FCC'] not in ('A74','A71'):draw_geo(line.intersection(box(*bounds)),'#d0d2c4',2)
for i,(p,line) in enumerate(oak):
    draw_geo(line,TEAL,9)
    x,y=mapper(*line.coords[0]);g.d.ellipse((x-4,y-4,x+4,y+4),fill=BG,outline=TEAL,width=2)
draw_geo(small[1],ORANGE,12)
px,py=mapper(small[1].centroid.x,small[1].centroid.y)
g.d.ellipse((px-14,py-14,px+14,py+14),outline=ORANGE,width=3)
g.d.line((px+15,py,935,py,975,540),fill=ORANGE,width=3)
g.text(108,473,'OAK STREET',29,bold=True)
g.text(108,514,'N ↑',25,MUTED,bold=True)
for label in ('Grant Boulevard','Butternut Street','Burnet Avenue'):
    parts=[line.intersection(box(*bounds)) for p,line in all_roads if p['CompleteStreetName']==label and line.intersects(box(*bounds))]
    if parts:
        anchor=unary_union(parts).centroid;x,y=mapper(anchor.x,anchor.y)
        width=g.d.textlength(label,font=font(22))
        x=max(panel[0]+15,min(x,panel[2]-width-15))
        g.d.rectangle((x-4,y-4,x+width+5,y+27),fill=BG)
        g.text(x,y,label,22,MUTED)
scale_px=250/(bounds[2]-bounds[0])*(panel[2]-panel[0])
g.d.rectangle((100,1370,410,1430),fill=BG)
g.d.line((120,1406,120+scale_px,1406),fill=INK,width=4)
g.text(130+scale_px,1406,'250 m',23,anchor='lm')
g.text(1010,469,'THE TINY PIECE',25,ORANGE,bold=True)
g.text(1010,521,f'{small_ft:.1f} ft',88,ORANGE,serif=True,bold=True)
g.text(1010,634,'Oak Street’s shortest source feature.',30)
g.text(1010,681,'A database piece—not a verified block.',28,MUTED)
g.d.line((1010,768,1920,768),fill=RULE,width=2)
g.text(1010,808,'THE CONNECTED STREET',25,TEAL,bold=True)
g.text(1010,861,'1.44 miles',88,TEAL,serif=True,bold=True)
g.text(1010,975,f"{float(oak_total['length_ft']):,.0f} feet across 22 source features.",30)
g.text(1010,1020,'One continuous Oak Street.',30)
g.d.line((1010,1103,1920,1103),fill=RULE,width=2)
g.text(1010,1160,'The name has nine letters.',35,serif=True)
g.text(1010,1218,'The street has places to be.',35,serif=True)
g.text(1010,1315,'Map dots mark source-feature endpoints.',25,MUTED)
g.text(1010,1356,'They are not all separate intersections.',25,MUTED)
g.text(80,1510,SOURCE,24,MUTED)
g.text(80,1550,'North-up source geometry in NAD83 / UTM 18N. Line widths and endpoint dots enlarged for visibility.',24,MUTED)
g.text(80,1590,'Length follows the connected centerline, not the straight line between its endpoints. Measurements are approximate.',24,MUTED)
g.save('oak-street-pieces-and-whole')
audit['oak']=dict(source_features=len(oak),shortest_id=small[0]['NYSStreetID'],shortest_ft=small_ft,total_ft=float(oak_total['length_ft']))
(ROOT/'companion_graphics_audit.json').write_text(json.dumps(audit,indent=2))
print('Created four 2000-pixel companion graphics plus 1400-pixel web versions.')
