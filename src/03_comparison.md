---
title: Comparisons
sql:
  cc_data_all:  ./data/cc_tables/all/cc_data_all.parquet
  cd119_geos: ./data/cd119_geos.parquet
head: '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tarekraafat/autocomplete.js@10/dist/css/autoComplete.min.css">'
---

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2M9HMSTWCC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-2M9HMSTWCC');
</script>

```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

```js
const blue_color = "#2573ac";
```


This I think will be where I will develop visualizations for comparing across two congressional communtiies. 

## Density Hexbins

The histograms above provide a useful first-look at the data. However, to discover relations among the data we had to interactively explore. Instead of "hiding" patterns behind interactions, let's visualize relationships directly.

Below we use hexagonal bins to visualize the density (number of flights) by both time of day and arrival delay. Interactive histograms along the edges show marginal distributions for both.


```sql
SELECT * FROM cc_data_all LIMIT 2
```

```sql
SELECT * FROM cd119_geos LIMIT 2
```

```js
const map_width  = 550;
const grid_height = 200;
```

# comparison

```js
const $query = vg.Selection.intersect();
```

```js
const labels = {
  age_prop_under18: "Proportion under 18",
  age_prop_18_65: "Proportion 18 to 64",
  age_prop_over65: "Proportion 65 and over",
  tot_rented_hholds: "Total renter households",
  tot_owned_hholds: "Total owner households"
};

const var1 = view(Inputs.select(
  ["age_prop_under18", "age_prop_18_65", "age_prop_over65"],
  { label: "Variable 1", format: (d) => labels[d] }
));

const var2 = view(Inputs.select(
  ["tot_rented_hholds", "tot_owned_hholds"],
  { label: "Variable 2", format: (d) => labels[d] }
));
```


```js
vg.vconcat(
  vg.hconcat(

    // top graph 
    vg.plot(
      vg.rectY(
        vg.from("cc_data_all"),
        { x: vg.bin(var1), y: vg.count(), fill: blue_color, inset: 0.5 }
      ),
      vg.intervalX({ as: $query }),
      vg.margins({ left: 5, right: 5, top: 30, bottom: 0 }),
      vg.xAxis("top"),
      vg.yAxis(null),
      vg.xLabelAnchor("center"),
      vg.xLabel(labels[var1]),
      vg.width(map_width),
      vg.height(70)
    ),
    vg.hspace(80)
  ),
  vg.hconcat(

    // hex grid 
    vg.plot(
      vg.hexbin(
        vg.from("cc_data_all", { filterBy: $query }),
        { x: var1, y: var2, fill: vg.count(), binWidth: 10 }
      ),
      vg.hexgrid({ binWidth: 10 }),
      vg.name("hexbins"),
      vg.colorScheme("ylgnbu"),
      vg.colorScale("linear"),
      vg.margins({ left: 5, right: 0, top: 0, bottom: 5 }),
      vg.xAxis(null),
      vg.yAxis(null),
      vg.width(map_width),
      vg.height(grid_height), 
      vg.xyDomain(vg.Fixed),
    ),

    /// right side bar 
    vg.plot(
      vg.rectX(
        vg.from("cc_data_all"),
        { x: vg.count(), y: vg.bin(var2), fill: blue_color, inset: 0.5 }
      ),
      vg.intervalY({ as: $query }),
      vg.margins({ left: 0, right: 50, top: 4, bottom: 5 }),
      vg.xAxis(null),
      vg.yAxis("right"),
      vg.yLabelAnchor("center"),
      vg.yLabel(labels[var2]),
      vg.width(80),
      vg.height(grid_height)
    )
  ),

  // usa map 
  vg.plot(
    // background: every community, neutral
    vg.geo(vg.from("cd119_geos"), {
      geometry: "geometry",
      fill: "#e5e0db",
      stroke: "currentColor",
      strokeWidth: 0.3
    }),

    // foreground: only rows matching the brush, colored by the chosen variable
    vg.geo(vg.from("cc_data_all", { filterBy: $query }), {
      geometry: "geometry",
      fill: var1,
      fillOpacity: 0.8,
      stroke: "currentColor",
      strokeWidth: 0.5
    }),

    vg.colorScheme("ylgnbu"),
    vg.colorScale("linear"),
    vg.projectionType("albers"),
    vg.margin(0),
    vg.width(map_width),
    vg.height(400)
  )
)
```
