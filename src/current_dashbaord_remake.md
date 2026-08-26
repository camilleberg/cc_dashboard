---
title: Current Draft in Observable Framework 
sql:
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


<span style="color:blue">This page is to play aroudn in a new framework? If there maybe wants to be one compact dashabord for each community</span>.

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
// creating selection bar 
const $ccn20 = vg.Selection.single();
```

```js
// shared sttributes
const attributes = [
  vg.width(600),
  vg.height(150),
  vg.margin(0),
  vg.yAxis(null),
  vg.xDomain([0, 1]),
  vg.colorScale("symlog")
];
```

```js
// remaking line charts 
vg.vconcat(
    vg.menu({ as: $ccn20, from: "cc_data_age_prop", column: "CCN20", label: "Congressional Community " }),
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop", { filterBy: $ccn20 }), 
        { x: "age_prop_under18", y: 0 , tip: true}), 
        ...attributes,
        vg.xLabel("Proportion Under 18"), 
    ), 
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop", { filterBy: $ccn20 }), 
        { x: "age_prop_18_65", y: 0 , tip: true}), 
        ...attributes,
        vg.xLabel("Proportion Between 18 and 64"), 
    ), 
    vg.plot(
        vg.dot(vg.from("cc_data_age_prop", { filterBy: $ccn20 }), 
        { x: "age_prop_over65", y: 0 , tip: true}), 
        ...attributes,
        vg.xLabel("Proportion 65 and Over"), 
    )
)
```