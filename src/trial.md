---
title: Age stuff
sql:
  cc_data: data/cc_data.parquet
  cc_data_grouping: data/cc_data_grouping.parquet
---




# Age and map stuff

```sql id=age_group_data
SET VARIABLE target_cols = (
    SELECT list(col_name) 
    FROM cc_data_grouping
    WHERE "group" = 'tot_pop_1'
);

-- Step 2: Use COLUMNS() and a lambda function to match the list
CREATE OR REPLACE TABLE age_group_data_raw AS (
  SELECT CCN20, col_name, value
  FROM (
      SELECT 
          CCN20, -- Keep keys explicitly if desired
          COLUMNS(c -> list_contains(getvariable('target_cols'), c))
      FROM cc_data
  ) sub
  UNPIVOT (
      value FOR col_name IN (COLUMNS(* EXCLUDE (CCN20)))
  )
);
```

```sql 
CREATE OR REPLACE TABLE age_group_data AS (
    SELECT 
        r.CCN20,
        r.col_name,
        r.value,
        c."Dependency Ratio" AS "Dependency Ratio"
    FROM age_group_data_raw r
    JOIN cc_data c ON r.CCN20 = c.CCN20
);
```

To check sql query 
```sql
SELECT * FROM age_group_data LIMIT 10
```

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
  ), 
  vg.plot(
    vg.barY(vg.from("age_group_data", { filterBy: $brush }), 
    { x: 'col_name', y: vg.sum('value') , fill: "steelblue"})
  ), 
  vg.plot(
    vg.waffleY(
      vg.from("age_group_data", { filterBy: $brush }),
      {
        unit: 100000,
        round: false,
        gap: 1,
        rx: 3,
        x: 'col_name',
        y: vg.sum('value')
      }
    )
    // ...other marks/plot-level options...
  )
)
```
```sql
SELECT sum(value) FROM age_group_data
```