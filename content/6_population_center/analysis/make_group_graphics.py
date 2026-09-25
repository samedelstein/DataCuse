"""Race and age comparison maps, both on the same north-up scale."""
# Reuse the house-style drawing and basemap helpers; regenerates the two overview maps.
from make_graphics import *
import textwrap
G=json.loads((R/'group_results.json').read_text())['groups'];byid={g['id']:g for g in G}
colors=[TEAL,RUST,'#6c6185',GREEN,'#77705f','#99702b','#477d9a']
# A fixed extent shared by both figures, centered on the whole set of group points.
points=[merc(g['longitude'],g['latitude']) for g in G]
b=fit_bounds(points,1120,1120,pad=1.55)
def wrap(d,x,y,s,size,width,color=INK,bold=False):
 words=s.split();line='';lines=[]
 for word in words:
  trial=(line+' '+word).strip()
  if d.textlength(trial,font=font(size,bold=bold))>width and line:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 for i,line in enumerate(lines):text(d,x,y+i*(size+8),line,size,color,bold)
 return y+len(lines)*(size+8)
def dot(d,x,y,color,number):
 d.ellipse((x-23,y-23,x+23,y+23),fill=color,outline=BG,width=4)
 text(d,x,y,str(number),27,BG,True,anchor='mm')
def cross(d,x,y):
 d.ellipse((x-21,y-21,x+21,y+21),fill=BG,outline=INK,width=3)
 d.line((x-30,y,x+30,y),fill=INK,width=4);d.line((x,y-30,x,y+30),fill=INK,width=4)
for typ,title,subtitle in [('age','The middle has an age range.','Four age groups. Four estimated balance points.'),('race','One city. Several balance points.','2020 Census race categories, shown separately from ethnicity.')]:
 selected=[g for g in G if g['type']==typ];im=Image.new('RGB',(2200,1770),BG);d=ImageDraw.Draw(im)
 text(d,65,45,'SYRACUSE / POPULATION CENTER BY '+typ.upper(),29,MUTED,True)
 text(d,60,118,title,79,serif=True,bold=True);text(d,65,245,subtitle,36)
 m,xy=map_base(b,1120,1120,True);md=ImageDraw.Draw(m)
 # Label two named east-west streets with leaders to their true coordinates.
 for name,label,lx,ly,target in [('Erie Boulevard East','Erie Blvd. E.',600,120,(px,py+900)),('East Adams Street','E. Adams St.',780,1000,(px+450,py-350))]:
  candidates=[p for f in roads if f['properties']['name']==name for line in parts(f['geometry']) for p in line]
  if candidates:
   point=min(candidates,key=lambda p:(merc(*p)[0]-target[0])**2+(merc(*p)[1]-target[1])**2);tx,ty=xy(*merc(*point));tw=md.textlength(label,font=font(27,bold=True))+20
   if 0<tx<1120 and 0<ty<1120:
    md.line((tx,ty,lx+tw/2,ly+20),fill=MUTED,width=2);md.rectangle((lx,ly,lx+tw,ly+40),fill=BG);text(md,lx+10,ly+3,label,27,bold=True)
 x,y=xy(px,py)
 for n,g in enumerate(selected,1):
  xx,yy=xy(*merc(g['longitude'],g['latitude']));md.line((x,y,xx,yy),fill='#9eaa98',width=2);dot(md,xx,yy,colors[n-1],n)
 cross(md,x,y);text(md,20,20,'N ↑',29,bold=True)
 scale=402.336/math.cos(math.radians(r['latitude']))/(b[2]-b[0])*1120
 md.rectangle((15,1035,scale+50,1110),fill=BG);md.line((25,1090,25+scale,1090),fill=INK,width=4);text(md,25,1043,'¼ mile',26)
 im.paste(m,(55,390));d=ImageDraw.Draw(im);SX=1270
 for n,g in enumerate(selected,1):
  yy=395+(n-1)*(154 if typ=='race' else 207);dot(d,SX,yy+25,colors[n-1],n)
  end=wrap(d,SX+47,yy,g['label'].replace('-', '–'),31,795,bold=True)
  text(d,SX+47,end+3,f"{g['population']:,} residents",30,MUTED)
  if typ=='age':
   compass=['N','NE','E','SE','S','SW','W','NW'][int((g['bearing_from_overall']+22.5)//45)%8]
   text(d,SX+47,end+49,f"About {g['distance_from_overall_metres']/1609.344:.2f} mile {compass} of all residents",27,MUTED)
 if typ=='age':
  text(d,SX+47,1280,'Same map extent as the race comparison.',28,MUTED)
  text(d,SX+47,1330,'All ages include people in group quarters.',28,MUTED)
 cross(d,90,1580);text(d,140,1558,'All residents: 148,620',32,bold=True)
 text(d,65,1630,'Small populations are less stable: the Pacific Islander category has just 67 people.' if typ=='race' else 'Each point weights the same block centers by the number of residents in that age group.',29,MUTED)
 d.line((65,1690,2135,1690),fill=RULE,width=2)
 text(d,65,1710,'Source: 2020 Census DHC '+('P3' if typ=='race' else 'P12')+' + TIGERweb blocks; downloaded Sept. 25, 2026 UTC. NYS street context: Sept. 2026.',25,MUTED)
 im.save(OUT/f'{typ}-centers.png',optimize=True)
(R/'group_graphics_audit.json').write_text(json.dumps({'shared_map_bounds_3857':b,'map_size':[1120,1120],'labels_read_from':'group_results.json','point_sizes':'Equal sizes indicate centers, not population totals; totals printed in key.'},indent=2))
print('Saved group maps')
