---
title: Comparisons
sql:
  cc_data_all:  ./data/cc_tables/all/cc_data_all.parquet
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


```js
function calc_steps(col, table) {
  const values = Array.from(table, (row) => row[col]).filter((v) => v != null);
  const min = Math.min(...values);
  const max = Math.max(...values);
  return (max - min) / 15;
}
```

```js
const cc_data_table = await sql([`SELECT cd119, State, "${var1}", "${var2}" FROM cc_data_all`]);
```


```js
const map_width  = 650;
const grid_height = 200;
const map_height = 450;
```

# comparison

```js
const $query = vg.Selection.intersect();
const $hover = vg.Selection.intersect({empty: true});
```

```js
const labels = {
  age_prop_under18: "% under 18",
  age_prop_18_65: "% 18 to 64",
  age_prop_over65: "% 65 and over",
  tot_rented_hholds: "Total renter households",
  tot_owned_hholds: "Total owner households", 
  unemp_rate3: "Unemployment %", 
  lfp_rate: "Labor Force Participation %", 
  emp_to_pop: "Employment to Pop Ratio"
};

const selections = ["age_prop_under18", "age_prop_18_65", "age_prop_over65", 
  "tot_rented_hholds", "tot_owned_hholds",
  "unemp_rate3", "lfp_rate", "emp_to_pop"]

const var1 = view(Inputs.select(
  selections,
  { label: "Variable 1", format: (d) => labels[d] }
));

const var2 = view(Inputs.select(
  selections,
  { label: "Variable 2", format: (d) => labels[d] }
));
```

```js calc_steps.js
const cc_data_table_filter = await sql([`SELECT ccn20 AS Community, State, "${var1}" AS  "${labels[var1]}",  "${var2}" AS  "${labels[var2]}," FROM cc_data_all`]);

const var1_steps = calc_steps(var1, cc_data_table)
const var2_steps = calc_steps(var2, cc_data_table)
```


```js subset_ready.js
const subset_ready = await vg.coordinator().exec(`
  CREATE OR REPLACE TABLE cc_subset AS
  SELECT ccn20,
         State, 
         "${var1}", 
         "${var2}",
         geometry,
         ccn20      AS "Community",
         "${var1}"  AS "${labels[var1]}",
         "${var2}"  AS "${labels[var2]}"
  FROM cc_data_all
`);
```

```js satte_totals.js
const totals_ready = await vg.coordinator().exec(`
  CREATE OR REPLACE VIEW cc_with_totals AS
  SELECT c.*, t.state_total
  FROM cc_data_all c
  JOIN (SELECT State, COUNT(*) AS state_total FROM cc_data_all GROUP BY State) t
    USING (State)
`);
```


```js
subset_ready; 
totals_ready;
display(
vg.hconcat(
  vg.vconcat(
    vg.hconcat( 
      vg.hspace(100),
      // top graph 
      vg.plot(
        vg.rectY(
          vg.from("cc_subset"),
          { x: vg.bin(var1, {step: var1_steps}), y: vg.count(), fill: blue_color, inset: 0.5 }
        ),
        vg.intervalX({ as: $query }),
        vg.margins({ left: 5, right: 5, top: 40, bottom: 0 }),
        vg.xAxis("top"),
        vg.yAxis(null),
        vg.xLabelAnchor("center"),
        vg.xLabel(labels[var1]),
        vg.width(map_width),
        vg.height(70)
      )
    ),
    vg.hconcat(
      /// left side bar 
      vg.plot(
        vg.rectX(
          vg.from("cc_subset"),
          {  x: vg.sql`-1 * ${vg.count()}`, y: vg.bin(var2, { step: var2_steps }) , fill: blue_color, inset: 0.5 }
        ),
        vg.intervalY({ as: $query }),
        vg.margins({ left: 70, right: 0, top: 4, bottom: 5 }),
        vg.xAxis(null),
        vg.yAxis("left"),
        vg.yLabelAnchor("center"),
        vg.yLabel(labels[var2]),
        vg.width(100),
        vg.height(grid_height)
      ),
      // hex grid 
      vg.plot(

        // colorful bins
        vg.hexbin(
          vg.from("cc_subset", { filterBy: $query }),
          { x: var1, y: var2, fill: vg.count(), binWidth: 10 }
        ),
        vg.intervalXY({ as: $hover, pixelSize: 2 }),  // brush-select instead of hover

        // underlyign grid
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

    ),

    // table
    vg.hconcat(
        vg.table({
          from: "cc_subset",
          maxWidth: 150 + 80 + 30,
          height: map_height,
          filterBy: $query,
          // as: $hover,
          columns: ["Community", "State", labels[var1], labels[var2]],
          width: {Community: 80, State: 40, [labels[var1]]: 60, [labels[var2]]: 60}, 
      }),
      vg.hspace(15),

      // usa map 
      vg.plot(
        // background: every community, neutral
    /*     vg.geo(vg.from("cd119_geos"), {
          geometry: "geometry",
          fill: "#e5e0db",
          stroke: "currentColor",
          strokeWidth: 0.3
        }), */

        // foreground: only rows matching the brush, colored by the chosen variable
        vg.geo(
          vg.from("cc_subset", { filterBy: $query }),
          {
            geometry: "geometry",
            fill: var1,
            fillOpacity: 0.8,
            stroke: "currentColor",
            strokeWidth: 0.5
          }
        ),

        // dots for hover
        /* vg.dot(
          vg.from("cc_data_all"),
          {  
              x: vg.centroidX("geometry"),
              y: vg.centroidY("geometry"),
             r: 5, fill: "red" }
        ), */
        vg.colorScheme("ylgnbu"),
        vg.colorScale("linear"),
        vg.projectionType("albers-usa"),
        vg.margin(0),
        vg.width(map_width - 150),
        vg.height(map_height)
      ), 
    )
  ), 
  vg.hspace(20),
  // counter by state
   vg.plot(
    // outlines 
    vg.rectX(vg.from("cc_data_all"), { x: vg.count(), y: "State", fill: null, stroke: "black", inset: 0.5 }),

    // actual plots
    vg.rectX(vg.from("cc_data_all", {filterBy: $query}), { x: vg.count(), y: "State", fill: blue_color, inset: 0.5 }),

    // text 
    vg.text(
      vg.from("cc_with_totals", {filterBy: $query}),
      {
        x: vg.max("state_total"),   // anchor: total (outline bar end), unaffected by the brush
        y: "State",
        text: vg.count(),           // number: filtered count, changes with the brush
        dx: 4,
        textAnchor: "start",
        fontSize: 9, 
        fill: blue_color   
      }
    ),

    vg.margins({ left: 50, right: 25, top: 5, bottom: 5 }),   // right margin raised for the labels
    vg.yTickSize(0),
    vg.xAxis(null),
    vg.yAxis("left"),
    vg.yLabel("State"),
    vg.width(100),
    vg.height(grid_height + map_height + 70)
  ),
)
)
```
