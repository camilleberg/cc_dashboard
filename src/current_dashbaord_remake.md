---
title: Current Draft in Observable Framework 
sql:
  cc_data: data/cc_data.parquet
  cc_data_grouping: data/cc_data_grouping.parquet
---



# Dashboard
+ the basis of aalysis here will be to (1) select ccn20 and then it will show comparisons with states and congressional disrict
+ the other tabs will be to explore the data and issues ? Will be more for comparison's sake on the basis of that sub-category. But this page will be dedicated to _one_ congressional community

```sql id=cc_data_age
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
const $ccn20 = vg.Selection.single();
const plot_height = 150;
const plot_width = 600;
```

```js
// remaking line charts 
vg.vconcat(
    vg.menu({ as: $ccn20, from: "cc_data_age_prop", column: "CCN20", label: "Congressional Community " }),
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop", { filterBy: $ccn20 }), 
        { x: "age_prop_under18", y: 0 , tip: true}), 
        vg.xDomain([0, 1]), // Sets explicit min and max for X axis
        vg.yDomain(vg.Fixed),  // Keeps Y axis domain fixed after initial load
        vg.width(plot_width),
        vg.height(plot_height),
        vg.xLabel("Proportion Under 18"), 
        vg.yAxis(null), 
    ), 
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop", { filterBy: $ccn20 }), 
        { x: "age_prop_18_65", y: 0 , tip: true}), 
        vg.xDomain([0, 1]), // Sets explicit min and max for X axis
        vg.yDomain(vg.Fixed),  // Keeps Y axis domain fixed after initial load
        vg.width(plot_width),
        vg.height(plot_height),
        vg.xLabel("Proportion Between 18 and 64"), 
        vg.yAxis(null)
    ), 
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop", { filterBy: $ccn20 }), 
        { x: "age_prop_over65", y: 0 , tip: true}), 
        vg.xDomain([0, 1]), // Sets explicit min and max for X axis
        vg.yDomain(vg.Fixed),  // Keeps Y axis domain fixed after initial load
        vg.width(plot_width),
        vg.height(plot_height),
        vg.xLabel("Proportion 65 and Over"), 
        vg.yAxis(null)
    )
)
```