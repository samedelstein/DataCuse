"""Extract matching Syracuse records from official DHC ZIP using HTTP ranges.
Only three ZIP members are downloaded. Full state files stay in the temp cache.
"""
import urllib.request,struct,zlib,json,csv,hashlib,tempfile,io,zipfile
from pathlib import Path
from datetime import datetime,timezone
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parent
CACHE=Path(tempfile.gettempdir())/'datacuse-dhc';CACHE.mkdir(exist_ok=True)
URL='https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/New_York/ny2020.dhc.zip'
DOC='https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/'
provenance={'downloaded_utc':datetime.now(timezone.utc).isoformat(),'zip_url':URL,'members':{},'metadata':{}}
def get(url,ran=None):
 q=urllib.request.Request(url,headers={'Range':ran} if ran else {})
 with urllib.request.urlopen(q,timeout=120) as response:
  if ran:assert response.status==206
  return response.read()
def xlsx_rows(name,sheet):
 p=R/name
 if not p.exists():p.write_bytes(get(DOC+name))
 provenance['metadata'][name]={'url':DOC+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 z=zipfile.ZipFile(p);ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 ss=[''.join(t.itertext()) for t in E.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si',ns)];rows=[]
 for row in E.fromstring(z.read('xl/worksheets/sheet'+str(sheet)+'.xml')).findall('.//x:row',ns):
  d={}
  for c in row.findall('x:c',ns):
   v=c.find('x:v',ns)
   if v is not None:d[''.join(x for x in c.attrib['r'] if x.isalpha())]=ss[int(v.text)] if c.attrib.get('t')=='s' else v.text
  rows.append(d)
 return rows
geo_fields=[r['B'].strip() for r in xlsx_rows('geoheader-2020-dhc-state.xlsx',1) if r.get('B','').strip() and r.get('C','').isdigit()]
segments=xlsx_rows('2020-dhc-table-matrix.xlsx',2);field_maps={}
for seg in (5,6):
 fields=['FILEID','STUSAB','CHARITER','CIFSN','LOGRECNO']
 for row in sorted([r for r in segments if r.get('B')==str(seg)],key=lambda r:int(r['D'])):
  table=row['A'].strip();fields.extend(f'{table}_{i:03d}N' for i in range(1,int(row['C'])+1))
 field_maps[seg]=fields
(R/'dhc_field_layouts.json').write_text(json.dumps({'geo':geo_fields,'segments':field_maps},indent=2))
tail=get(URL,'bytes=-65536');end=tail.rfind(b'PK\x05\x06');size,offset=struct.unpack_from('<II',tail,end+12)
central=get(URL,f'bytes={offset}-{offset+size-1}');i=0;entries={}
while central[i:i+4]==b'PK\x01\x02':
 h=struct.unpack_from('<4s6H3I5H2I',central,i);n,e,c=h[10:13];name=central[i+46:i+46+n].decode();entries[name]={'compressed':h[8],'uncompressed':h[9],'crc32':h[7],'offset':h[-1]};i+=46+n+e+c
(R/'dhc_zip_directory.json').write_text(json.dumps(entries,indent=2))
def member(name):
 info=entries[name];p=CACHE/name
 if not p.exists():
  h=get(URL,f"bytes={info['offset']}-{info['offset']+29}");assert h[:4]==b'PK\x03\x04';n,e=struct.unpack_from('<HH',h,26);start=info['offset']+30+n+e
  packed=get(URL,f"bytes={start}-{start+info['compressed']-1}");b=zlib.decompress(packed,-15);assert len(b)==info['uncompressed'];assert zlib.crc32(b)==info['crc32'];p.write_bytes(b)
 b=p.read_bytes();assert len(b)==info['uncompressed'] and zlib.crc32(b)==info['crc32']
 provenance['members'][name]={**info,'sha256_uncompressed':hashlib.sha256(b).hexdigest()}
 print('Read',name,len(b),flush=True);return b.decode('utf-8-sig').splitlines()
blocks={r['geoid'] for r in csv.DictReader((R/'block_centroids.csv').open())};lookup={};geo_lines=[];city=None
for line in member('nygeo2020.dhc'):
 vals=line.split('|');assert len(vals)==len(geo_fields),(len(vals),len(geo_fields));d=dict(zip(geo_fields,vals))
 geoid=d['STATE']+d['COUNTY']+d['TRACT']+d['BLOCK']
 if d['SUMLEV']=='100' and d['GEOCOMP']=='00' and geoid in blocks:
  assert geoid not in lookup.values();lookup[d['LOGRECNO']]=geoid;geo_lines.append(line);assert d['PLACE']=='73000'
 if d['SUMLEV']=='160' and d['GEOCOMP']=='00' and d['GEOVAR']=='00' and d['STATE']=='36' and d['PLACE']=='73000':
  assert city is None;city=d['LOGRECNO'];lookup[city]='city';geo_lines.append(line)
assert len(lookup)==len(blocks)+1 and city
(R/'dhc_syracuse_geography.txt').write_text('\n'.join(geo_lines)+'\n',encoding='utf-8')
records={key:{'geoid':value} for key,value in lookup.items()}
for seg in (5,6):
 selected=[];seen=set();fields=field_maps[seg]
 for line in member(f'ny000{seg:02d}2020.dhc'):
  v=line.split('|')
  if v[4] not in lookup:continue
  assert len(v)==len(fields) and v[2]=='000' and int(v[3])==seg and v[4] not in seen
  seen.add(v[4]);selected.append(line)
  records[v[4]].update({k:int(value) for k,value in zip(fields[5:],v[5:]) if k.startswith(('P1_','P3_','P4_','P12_'))})
 assert seen==set(lookup)
 (R/f'dhc_syracuse_segment_{seg}.txt').write_text('\n'.join(selected)+'\n',encoding='utf-8')
for table in ('P3','P4','P12'):
 url=f'https://api.census.gov/data/2020/dec/dhc/groups/{table}.json';b=get(url);(R/f'dhc_{table}_metadata.json').write_bytes(b);provenance['metadata'][table]={'url':url,'sha256':hashlib.sha256(b).hexdigest()}
rows=sorted(records.values(),key=lambda r:r['geoid'])
with (R/'dhc_syracuse_counts.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
for p in R.glob('dhc_syracuse*'):provenance.setdefault('extracts',{})[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(R/'dhc_provenance.json').write_text(json.dumps(provenance,indent=2));print('Saved',len(rows),'records including city total')
