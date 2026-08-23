---
title: Current Draft in Observable Framework 
sql:
  cc_data: data/cc_data.parquet
  cc_data_grouping: data/cc_data_grouping.parquet
---

# Dashboard
+ the basis of aalysis here will be to (1) select ccn20 and then it will show comparisons with states and congressional disrict
+ the other tabs will be to explore the data and issues ? Will be more for comparison's sake on the basis of that sub-category. But this page will be dedicated to _one_ congressional community

```sql
CREATE OR REPLACE TABLE cc_data_age_prop AS (
    WITH base AS (
        SELECT
            CCN20,
            DC,
            State,
            "Total Population" AS tot_pop,
            "Total Population" - "18 years and over - Tot Pop" AS ageGroup_under18,
            "18 years and over - Tot Pop" - "65 years and over  - Tot Pop" AS ageGroup_18_65,
            "65 years and over  - Tot Pop" AS ageGroup_over65
        FROM cc_data
    )
    SELECT
        CCN20,
        DC,
        State,
        tot_pop,
        ageGroup_under18,
        ageGroup_18_65,
        ageGroup_over65,
        ageGroup_under18 / NULLIF(tot_pop, 0) AS age_prop_under18,
        ageGroup_18_65 / NULLIF(tot_pop, 0) AS age_prop_18_65,
        ageGroup_over65 / NULLIF(tot_pop, 0) AS age_prop_over65
    FROM base
);

SELECT * FROM cc_data_age_prop;
```

```js
const $ccn20 = vg.Param.value(10);
```

```sql id=ccn20_rows
-- this selects all the diff values 
SELECT DISTINCT CCN20 FROM cc_data
```
```js
// extracting options for ccn20
ccn20List = ccn20_rows.map(d => d.CCN20)
```


```js
// remaking line charts 

vg.vconcat(
    vg.menu({ as: $ccn20, options: ccn20List, label: "Congressional Community" }),
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop"), { x: "age_prop_under18", y: 0 })
    )
)
```

vg.vconcat(
  vg.hconcat(
    vg.menu({as: $unit, options: [1, 2, 5, 10, 25, 50, 100], label: "Unit"}),
    vg.menu({as: $round, options: [true, false], label: "Round"}),
    vg.menu({as: $gap, options: [0, 1, 2, 3, 4, 5], label: "Gap"}),
    vg.slider({as: $radius, min: 0, max: 10, step: 0.1, label: "Radius"})
  ),
  vg.vspace(10),
  vg.plot(
    vg.waffleY(
      vg.from("athletes"),
      {
        unit: $unit,
        round: $round,
        gap: $gap,
        rx: $radius,
        x: vg.sql`5 * floor(year("date_of_birth") / 5)`,
        y: vg.count()
      }
    ),
    vg.xLabel(null),
    vg.xTickSize(0),
    vg.xTickFormat("d")
  )
);