"""Fetch only the OSM tiles used by this single static map; reuse cached tiles."""
import json,math,time
from urllib.request import Request,urlopen
from map_design_data import ROOT,BOUNDS,ZOOM,tile_pixel

cache=ROOT/'map_tiles'
cache.mkdir(exist_ok=True)
x0,y1=tile_pixel(BOUNDS[0],BOUNDS[1]);x1,y0=tile_pixel(BOUNDS[2],BOUNDS[3])
tiles=[]
for x in range(math.floor(x0/256),math.floor(x1/256)+1):
    for y in range(math.floor(y0/256),math.floor(y1/256)+1):
        path=cache/f'{ZOOM}-{x}-{y}.png'
        url=f'https://tile.openstreetmap.org/{ZOOM}/{x}/{y}.png'
        if not path.exists():
            request=Request(url,headers={'User-Agent':'DataCuseEditorialMap/1.0 (single static Syracuse street illustration; datacuse.com)'})
            with urlopen(request,timeout=30) as response:data=response.read()
            assert data.startswith(b'\x89PNG'),url
            path.write_bytes(data)
            time.sleep(.1)
        tiles.append(dict(x=x,y=y,path=path.name,url=url))
(ROOT/'editorial_basemap_sources.json').write_text(json.dumps(dict(zoom=ZOOM,bounds_3857=BOUNDS,attribution='© OpenStreetMap contributors',copyright='https://www.openstreetmap.org/copyright',tiles=tiles),indent=2))
print('Map tiles cached:',len(tiles))
