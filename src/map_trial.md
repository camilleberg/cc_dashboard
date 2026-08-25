---
title: Map Trial
sql:
    ccn20_geo_raw: data/ccn20_geo.parquet
    cc_data: data/cc_data.parquet
    cc_data_grouping: data/cc_data_grouping.parquet
---

# this is to load the map 

<span style="color:blue">Current map page. Right now, when you click on the communities it counts the number of states. Shift click allows for multipple selection. Further work si to actually integrate the data and get informaiton on each cc. 

Possible other idea is to filter high earning communities or some metric of similairites and it will highlight on the mpa but that can be put on the back burner</span>.

```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

Then attaching data

```sql id=ccn20_geo 
-- transforming as geo 
CREATE OR REPLACE TABLE ccn20_geo AS (
    SELECT
    CCN20,
    DC,
    State,
    ST_AsGeoJSON(geometry) AS geometry
    FROM ccn20_geo_raw
);
```

```js
// A selection that accumulates clicked items (shift-click to add multiple)
const $selection = vg.Selection.crossfilter();
```

```js
vg.vconcat(
    vg.plot(
        vg.geo(vg.from("ccn20_geo"), {
            geometry: "geometry",
            fill: "State",              // keep State as the field bound to fill
            fillOpacity: 0.5,
            stroke: "currentColor",
            strokeWidth: 0.5
        }),
        vg.toggle({as: $selection, channels: ["fill"]}),
        vg.highlight({by: $selection}), // dims non-selected states on click
        vg.colorRange(["steelblue"]),   // forces a single fill color (monocolor)
        vg.projectionType("albers"),
        vg.margin(0)
        ),
    vg.plot(
        vg.barX(vg.from("ccn20_geo", {filterBy: $selection}), {
            x: vg.count(),
            y: "State",
            fill: "steelblue"
            }),
        vg.marginLeft(80)
    )
)
```