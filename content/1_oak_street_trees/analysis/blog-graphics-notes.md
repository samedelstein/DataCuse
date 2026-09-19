# Syracuse trees: blog graphics

## Images

PNG files and art prompts now live in the sibling `../images/` folder. The Markdown article lives at `../story/index.md`. Data, scripts, audit files, the notebook, and cached tiles live here in `analysis/`.

- `trees-map-blog.png`: 2400 × 2100. The 19 whole-word matches across Oak St, Maple St, Maple Ter, and Lilac St, with exact-location dots and offset symbolic tree illustrations.
- `trees-pictogram-blog.png`: 1800 × 1250. One icon per matching tree: 6, 6, 6, and 1.
- `lost-trees-oak-street.png`: 2400 × 2100. Oak Street's 56 maples and 6 oaks, plotted and counted with one tree icon per record. Other tree groups on Oak St are not displayed.

Suggested caption: **Oak Street has an identity crisis: 56 maples, six oaks. Apparently, some trees read the street signs. Others branch out.**

Suggested alt text for the lost-trees image: A Syracuse street map marks 56 maples and six oaks recorded on Oak Street. Orange maple and green oak illustrations connect to their recorded coordinates. An adjacent pictogram repeats one illustrated tree for each record, showing that maples greatly outnumber oaks on their namesake street.

## Reproduce

Dependencies: `pandas`, `Pillow`, and `requests`.

```sh
python analysis/download_map_tiles.py
python analysis/make_lost_trees_graphic.py
```

Run these commands from the story folder. The second command regenerates all three graphics into `images/`. The downloader reuses cached tiles in `analysis/map_tiles`, so no network access is needed once that cache is populated. Font paths currently target Windows fonts.

## Data and method

Source: the supplied `Syracuse_Tree_Data_7832308158023752279.csv`. These are inventory records, not a new field survey. Names use the lowercase text before the first comma in `SPP_COM`; aliases and differently ordered common names are not normalized. The first graphic matches that name as a whole word in `STREET`.

There are 1,836 oak records: six on exactly `Oak St`, and 1,830 on other named streets, with no missing street names among oak records. There are no oak records on `Maple St` or `Maple Ter`. Examples of oaks on other tree-named streets: Butternut St 11, Walnut Pl 8, Cedar St 4, Hickory St 1, Lilac St 1, Pine St 1.

Locations use each record's longitude and latitude, projected to Web Mercator to align with the basemap. Location dots remain fixed; nearby illustrations may be offset and connected by leader lines. Symbol heights, canopy shapes, flowering, and foliage color do not represent measured tree dimensions or observed seasonal conditions.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). Attribution is also printed on both map images. The maps use cached standard OSM tiles.

Tree artwork was generated with the built-in image-generation tool. Python/Pillow places the art and renders the counts, coordinates, text, and map. Exact generation/edit prompts are saved in `tree-art-prompts.md`.

Audit data: `blog_map_trees.csv`, `blog_map_audit.json`, `lost_trees_oak_street.csv`, and `lost_trees_audit.json`.
