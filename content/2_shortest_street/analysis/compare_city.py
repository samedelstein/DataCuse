"""Apply the same endpoint/block calculation to the older city layer."""
import json
from collections import Counter
import calculate as calc
from shapely.geometry import shape
from shapely.ops import transform

def city_load():
    boundary=transform(calc.PROJECT,shape(json.loads((calc.ROOT/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
    area=boundary.buffer(500)
    fs=json.loads((calc.ROOT/'streets_city.geojson').read_text())['features']
    roads=[]
    for f in fs:
        p=f['properties'];name=calc.clean(p['FULLNAME'])
        if not name or calc.clean(p['CFCC']) not in calc.ROAD_CLASSES or calc.clean(p['TYPE']) in ('RAMP','PATH'): continue
        g=transform(calc.PROJECT,shape(f['geometry']))
        if not g.intersects(area): continue
        for line in (list(g.geoms) if g.geom_type=='MultiLineString' else [g]):
            roads.append(dict(name=name,base=calc.clean(p['NAME']),suffix=calc.clean(p['TYPE']),id=str(p['FID']),oid=p['FID'],part=0,geo=line,z0=0,z1=0,fcc=p['CFCC'],jurisdiction='12',props=p,city_attributed=True))
    return boundary,roads,Counter()

if __name__=='__main__':
    calc.load=city_load
    result=calc.calculate(save=False)
    (calc.ROOT/'city_comparison.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ('blocks','totals')},indent=2))
