---
title: Map Trial 1
sql:
    ccn20_geo_raw: data/ccn20_geo.parquet
    cc_data: data/cc_data.parquet
    cc_data_grouping: data/cc_data_grouping.parquet
---

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2M9HMSTWCC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-2M9HMSTWCC');
</script>

# this is to load the map , v1

<span style="color:blue">Current map page. Right now, when you click on the communities it counts the number of states. Shift click allows for multipple selection. Further work si to actually integrate the data and get informaiton on each cc. 

Possible other idea is to filter high earning communities or some metric of similairites and it will highlight on the mpa but that can be put on the back burner</span>.

```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

Then attaching data

```sql id=ccn_geo
-- transforming as geo 
SELECT
    CCN20,
    DC,
    State,
    ST_AsGeoJSON(geometry) AS geometry
    FROM ccn20_geo_raw
```


```js import_maplibre.js
import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.6.0/dist/maplibre-gl.mjs';
display(html`<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@6.6.0/dist/maplibre-gl.css">`);
```

```js find_bounds.js
function boundsFromGeoJSON(geojson) {
  const bounds = new maplibregl.LngLatBounds();

  function extendWithCoords(coords) {
    if (typeof coords[0] === "number") {
      bounds.extend(coords);
    } else {
      coords.forEach(extendWithCoords);
    }
  }

  // handle Feature, bare Geometry, or FeatureCollection
  const geometry = geojson.type === "Feature" ? geojson.geometry
                  : geojson.type === "FeatureCollection" ? null
                  : geojson;

  if (geojson.type === "FeatureCollection") {
    geojson.features.forEach(f => extendWithCoords(f.geometry.coordinates));
  } else {
    extendWithCoords(geometry.coordinates);
  }

  return bounds;
}
```

```js get_geo.js
const ccn_geojson = {
  type: "FeatureCollection",
  features: ccn_geo.toArray().map(row => ({
    type: "Feature",
    properties: { CCN20: row.CCN20, DC: row.DC, State: row.State },
    geometry: JSON.parse(row.geometry)
  }))
};
```

```js make_map.js
const mapDiv = display(document.createElement("div"));
mapDiv.style = "height: 400px;";

const map = new maplibregl.Map({
    container: mapDiv,
    style: "https://tiles.versatiles.org/assets/styles/colorful/style.json",
    //center: [-68.13734351262877, 45.137451890638886],
    zoom: 5
});

map.on('load', () => {
    map.addSource('maine', {
        'type': 'geojson',
        'data': ccn_geojson
    });
    map.addLayer({
        'id': 'maine',
        'type': 'fill',
        'source': 'maine',
        'layout': {},
        'paint': {
            'fill-color': '#088',
            'fill-opacity': 0.8
        }
    });

    const bounds = boundsFromGeoJSON(ccn_geojson);
    map.fitBounds(bounds, { padding: 20 });
});

```

