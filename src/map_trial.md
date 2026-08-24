---
title: MAp Trial
sql:
    ccn20_geo_raw: data/ccn20_geo.parquet
---



# this is toload the map 

```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

Then attaching data



```sql id=ccn20_geo
CREATE OR REPLACE TABLE ccn20_geo AS (
    SELECT
    CCN20,
    DC,
    State,
    ST_AsGeoJSON(geometry) AS geometry
    FROM ccn20_geo_raw
);

SELECT * FROM ccn20_geo;
```


```js
vg.plot(
  vg.geo(vg.from("ccn20_geo"), {geometry: "geometry", stroke: "currentColor", strokeWidth: 0.25}),
  vg.margin(0), 
  vg.projectionType("albers")
)
```


export default vg.plot(
  vg.geo(
    vg.from("counties"),
    {stroke: "currentColor", strokeWidth: 0.25}
  ),
  vg.geo(
    vg.from("states"),
    {stroke: "currentColor", strokeWidth: 1}
  ),
  vg.dot(
    vg.from("counties"),
    {
      x: vg.centroidX("geom"),
      y: vg.centroidY("geom"),
      r: 2,
      fill: "transparent",
      tip: true,
      title: "name"
    }
  ),
  vg.margin(0),
  vg.projectionType("albers")
);