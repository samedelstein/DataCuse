"""Shared geometry and layout for the editorial map."""
import json,math
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform,unary_union
from pyproj import Transformer
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'images'
T=Transformer.from_crs(4326,3857,always_xy=True).transform
B=transform(T,shape(json.loads((ROOT/'syracuse_boundary.geojson').read_text())['features'][0]['geometry']))
CX=(B.bounds[0]+B.bounds[2])/2
CY=(B.bounds[1]+B.bounds[3])/2
SIDE=max(B.bounds[2]-B.bounds[0],B.bounds[3]-B.bounds[1])*1.10
BOUNDS=(CX-SIDE/2,CY-SIDE/2,CX+SIDE/2,CY+SIDE/2)
ZOOM=14
WORLD=2*math.pi*6378137
def tile_pixel(x,y):
    scale=256*2**ZOOM/WORLD
    return ((x+WORLD/2)*scale,(WORLD/2-y)*scale)

def load_features():
    fs=json.loads((ROOT/'streets_nys_current.geojson').read_text())['features']
    return [(f['properties'],transform(T,shape(f['geometry']))) for f in fs]
