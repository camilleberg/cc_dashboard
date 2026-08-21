---
title: Age stuff
sql:
  cc_data: data/cc_data.parquet
  cc_data_grouping: data/cc_data_grouping.parquet
---



# Age and map stuff

+ source: https://github.com/uwdata/mosaic-framework-example
## Interactive exploration of large-scale transportation data


We use [Mosaic vgplot](https://idl.uw.edu/mosaic/) to create scalable, interactive visualizations. Mosaic loads data from a Parquet file into DuckDB-WASM, running in the browser. Mosaic queries the database to transform data as part of the visualization process.

## Cross-Filtered Histograms
The histogram will display 

```js
// a selection instance to manage selected intervals from each plot
const $brush = vg.Selection.crossfilter();
```

```js
// this is the graph 
vg.vconcat(
    // put map selection here, to dynamically update 
  vg.plot(
    vg.rectY(
      vg.from("cc_data", { filterBy: $brush }),
      { x: vg.bin("Dependency Ratio"), y: vg.count(), fill: "steelblue", inset: 0.5 }
    ),
    vg.intervalX({ as: $brush }),
    vg.xDomain(vg.Fixed),
    vg.yTickFormat("s"),
    vg.xLabel("Dependency Ratio"),
    vg.yLabel("Number of Communities"),
    vg.width(600),
    vg.height(150)
  )
)

```
