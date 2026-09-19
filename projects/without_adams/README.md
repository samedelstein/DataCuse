# Adams Access Lab

A dependency-light static DataCuse planning-screening site for the East Adams Street / hospital-access decision.

## Run locally

Open `index.html` in a browser, or serve this folder with any static server.

## Data status

The initial map shows hospital/network destinations. Address-to-address trips use Nominatim search and OSRM's non-live driving profile, so displayed route lines are snapped to mapped roads rather than hand-drawn. The closure case forces two waypoints across Harrison Street, preventing the comparison from using the proposed East Adams closure segment as its through connection. The map can also load NYSDOT's public AADT feature layer and road-snapped former-I-81/future-BL-81 context. AADT is historical annual-average traffic, not real-time congestion; no live traffic feed is represented.

## Deploy

Publish this directory as `/projects/without_adams/` within the DataCuse static site.
