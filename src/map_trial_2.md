---
title: MAp Trial two
sql:
    cc_data: data/cc_data.parquet
    cc_data_grouping: data/cc_data_grouping.parquet
---

# this is toload the map , again

```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

Then attaching data



```js
const ccn20_geo = await FileAttachment("./data/ccn20_geo_topo.json").json();
```

```js
Object.keys(ccn20_geo)
```

```js
Object.keys(ccn20_geo.objects)
```

```js
await vg.coordinator().exec([
  vg.loadSpatial(
    "ccn20_geo",
    "data/ccn20_geo_topo.json",
    {layer: "data"}
  )
]);
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