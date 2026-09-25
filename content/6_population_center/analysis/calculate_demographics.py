"""Calculate group centers on identical block centroids; audit all partitions."""
import csv,json,math
from pathlib import Path
from pyproj import Transformer,Geod
R=Path(__file__).resolve().parent
rows=list(csv.DictReader((R/'dhc_syracuse_counts.csv').open()));city=next(r for r in rows if r['geoid']=='city');rows=[r for r in rows if r['geoid']!='city']
centroids={r['geoid']:r for r in csv.DictReader((R/'block_centroids.csv').open())};assert set(centroids)=={r['geoid'] for r in rows}
base=json.loads((R/'results.json').read_text());U=Transformer.from_crs(26918,4326,always_xy=True).transform;geod=Geod(ellps='WGS84')
races=['White alone','Black or African American alone','American Indian and Alaska Native alone','Asian alone','Native Hawaiian and Other Pacific Islander alone','Some Other Race alone','Two or More Races']
groups=[{'id':'all','label':'All residents','type':'overall','fields':['P1_001N']}]
groups +=[{'id':f'race{i}','label':label,'type':'race','fields':[f'P3_{i:03d}N']} for i,label in enumerate(races,2)]
groups +=[{'id':'hispanic','label':'Hispanic or Latino (any race)','type':'ethnicity','fields':['P4_003N']},{'id':'nonhispanic','label':'Not Hispanic or Latino','type':'ethnicity','fields':['P4_002N']}]
for key,label,indices in [('under18','Under 18',range(3,7)),('18to34','18-34',range(7,13)),('35to64','35-64',range(13,20)),('65plus','65+',range(20,26))]:
 groups.append({'id':key,'label':label,'type':'age','fields':[f'P12_{i:03d}N' for i in list(indices)+[i+24 for i in indices]]})
differences=[]
for row in rows:
 p=int(row['P1_001N']);g=centroids[row['geoid']]
 assert p==int(row['P3_001N'])==int(row['P4_001N'])==int(row['P12_001N'])
 assert sum(int(row[f'P3_{i:03d}N']) for i in range(2,9))==p
 assert int(row['P4_002N'])+int(row['P4_003N'])==p
 assert sum(int(row[f'P12_{i:03d}N']) for i in list(range(3,26))+list(range(27,50)))==p
 assert all(int(v)>=0 for k,v in row.items() if k!='geoid')
 if p!=int(g['population']):differences.append({'geoid':row['geoid'],'dhc':p,'tigerweb':int(g['population'])})
for group in groups:
 weights=[sum(int(row[f]) for f in group['fields']) for row in rows];total=sum(weights)
 assert total==sum(int(city[f]) for f in group['fields']),(group['label'],total,[city[f] for f in group['fields']])
 x=math.fsum(w*float(centroids[row['geoid']]['easting']) for row,w in zip(rows,weights))/total
 y=math.fsum(w*float(centroids[row['geoid']]['northing']) for row,w in zip(rows,weights))/total
 lon,lat=U(x,y);az,_,distance=geod.inv(base['longitude'],base['latitude'],lon,lat)
 ix=math.fsum(w*float(centroids[row['geoid']]['internal_x']) for row,w in zip(rows,weights))/total
 iy=math.fsum(w*float(centroids[row['geoid']]['internal_y']) for row,w in zip(rows,weights))/total
 group.update(population=total,populated_blocks=sum(w>0 for w in weights),longitude=lon,latitude=lat,easting=x,northing=y,distance_from_overall_metres=distance,bearing_from_overall=az%360,internal_point_shift_metres=math.hypot(ix-x,iy-y),largest_block_share=max(weights)/total)
# Recombining each complete partition must recover the DHC overall mean.
checks={}
for typ in ['race','age','ethnicity']:
 partition=[g for g in groups if g['type']==typ];assert sum(g['population'] for g in partition)==148620
 err=math.hypot(sum(g['population']*g['easting'] for g in partition)/148620-groups[0]['easting'],sum(g['population']*g['northing'] for g in partition)/148620-groups[0]['northing']);assert err<1e-6;checks[typ]=err
result={'source':'2020 Census DHC P1, P3, P4, P12; all Syracuse 2020 blocks','groups':groups,'checks':{'block_count':len(rows),'all_groups_match_published_city_totals':True,'all_block_partitions_sum_to_block_total':True,'dhc_vs_tigerweb_total_differences':differences,'partition_center_recombination_error_metres':checks}}
(R/'group_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
