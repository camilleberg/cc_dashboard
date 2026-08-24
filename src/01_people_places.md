---
title: People and Places
sql:
  cc_data: data/cc_data.parquet
  ccn20_geo_raw: data/ccn20_geo.parquet
---
# People and Places 


```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

<!-- creating the tables-->

```sql

CREATE OR REPLACE TABLE cc_data_age_table AS

WITH base AS (
    SELECT
        CCN20,
        DC,
        State,
        "Total Population" AS tot_pop,

        "Total Population"
            - "18 years and over - Tot Pop"
            AS ageGroup_under18,

        "18 years and over - Tot Pop"
            - "65 years and over  - Tot Pop"
            AS ageGroup_18_65,

        "65 years and over  - Tot Pop"
            AS ageGroup_over65

    FROM cc_data
)

SELECT
    *,
    ageGroup_under18
        / NULLIF(tot_pop, 0)::DOUBLE
        AS age_prop_under18,

    ageGroup_18_65
        / NULLIF(tot_pop, 0)::DOUBLE
        AS age_prop_18_65,

    ageGroup_over65
        / NULLIF(tot_pop, 0)::DOUBLE
        AS age_prop_over65

FROM base;


CREATE OR REPLACE TABLE dc_data_age_table AS

WITH base AS (
    SELECT
        DC,

        "Total Population" AS tot_pop,

        "Total Population"
            - "18 years and over - Tot Pop"
            AS ageGroup_under18,

        "18 years and over - Tot Pop"
            - "65 years and over  - Tot Pop"
            AS ageGroup_18_65,

        "65 years and over  - Tot Pop"
            AS ageGroup_over65

    FROM cc_data
)

SELECT
    DC,

    SUM(tot_pop) AS tot_pop,
    SUM(ageGroup_under18) AS ageGroup_under18,
    SUM(ageGroup_18_65) AS ageGroup_18_65,
    SUM(ageGroup_over65) AS ageGroup_over65,

    SUM(ageGroup_under18)
        / NULLIF(SUM(tot_pop), 0)::DOUBLE
        AS age_prop_under18,

    SUM(ageGroup_18_65)
        / NULLIF(SUM(tot_pop), 0)::DOUBLE
        AS age_prop_18_65,

    SUM(ageGroup_over65)
        / NULLIF(SUM(tot_pop), 0)::DOUBLE
        AS age_prop_over65

FROM base
GROUP BY DC;


CREATE OR REPLACE TABLE state_data_age_table AS

WITH base AS (
    SELECT
        State,

        "Total Population" AS tot_pop,

        "Total Population"
            - "18 years and over - Tot Pop"
            AS ageGroup_under18,

        "18 years and over - Tot Pop"
            - "65 years and over  - Tot Pop"
            AS ageGroup_18_65,

        "65 years and over  - Tot Pop"
            AS ageGroup_over65

    FROM cc_data
)

SELECT
    State,

    SUM(tot_pop) AS tot_pop,
    SUM(ageGroup_under18) AS ageGroup_under18,
    SUM(ageGroup_18_65) AS ageGroup_18_65,
    SUM(ageGroup_over65) AS ageGroup_over65,

    SUM(ageGroup_under18)
        / NULLIF(SUM(tot_pop), 0)::DOUBLE
        AS age_prop_under18,

    SUM(ageGroup_18_65)
        / NULLIF(SUM(tot_pop), 0)::DOUBLE
        AS age_prop_18_65,

    SUM(ageGroup_over65)
        / NULLIF(SUM(tot_pop), 0)::DOUBLE
        AS age_prop_over65

FROM base
GROUP BY State;
```

<!-- slecting the community-->

```js
const ccnList = await sql`
    SELECT DISTINCT CCN20
    FROM cc_data
    ORDER BY CCN20
`;

const ccnArray = [...ccnList];

const ccn = view(
    Inputs.select(
        ccnArray.map(d => d.CCN20),
        {label: "My Congressional Community"}
    )
);
```

<!-- Filtering the data-->

```sql id=cc_data_age
SELECT *
FROM cc_data_age_table
WHERE CCN20 = ${ccn};
```

```sql id=dc_data_age
SELECT *
FROM dc_data_age_table
WHERE DC = (
    SELECT DC
    FROM cc_data_age_table
    WHERE CCN20 = ${ccn}
);
```

```sql id=state_data_age
SELECT *
FROM state_data_age_table
WHERE State = (
    SELECT State
    FROM cc_data_age_table
    WHERE CCN20 = ${ccn}
);
```



<!-- Cleaning and extracting data-->
```js
const cc_tot_pop = cc_data_age
  .getChild("tot_pop")
  .get(0);

const dc_tot_pop = dc_data_age
  .getChild("tot_pop")
  .get(0);

const state_tot_pop = state_data_age
  .getChild("tot_pop")
  .get(0);

const state_name = cc_data_age
  .getChild("State")
  .get(0);

const cc_under18_prop = cc_data_age
  .getChild("age_prop_under18")
  .get(0);

const dc_under18_prop = dc_data_age
  .getChild("age_prop_under18")
  .get(0);

const state_under18_prop = state_data_age
  .getChild("age_prop_under18")
  .get(0);

const cc_dc_diff =
  cc_under18_prop - dc_under18_prop;

const cc_dc_younger =
  cc_dc_diff > 0 ? "younger" : "older";

const cc_state_diff =
  cc_under18_prop - state_under18_prop;

const cc_state_younger =
  cc_state_diff > 0 ? "younger" : "older";

const age_under_18 = cc_data_age
  .getChild("ageGroup_under18")
  .get(0);

const age_18_65 = cc_data_age
  .getChild("ageGroup_18_65")
  .get(0);

const age_over65 = cc_data_age
  .getChild("ageGroup_over65")
  .get(0);
```



Your congressional community, **${ccn}**, is a community of **${cc_tot_pop.toLocaleString()}** individuals. Compared to your congressional district of **${Math.abs(dc_tot_pop).toFixed(0).toLocaleString()}** people, your community skews **${cc_dc_younger}** by **${(Math.abs(cc_dc_diff) * 100).toFixed(1)} percentage points**. It is similarly **${cc_state_younger}** than **${state_name}**, by **${(Math.abs(cc_state_diff) * 100).toFixed(1)} percentage points**.

<!-- Cards with big numbers -->

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Total Community Population</h2>
    <span class="big">${cc_tot_pop.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Children Population </h2>
    <span class="big">${age_under_18.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Working Age Population</h2>
    <span class="big">${age_18_65.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Over 65</h2>
    <span class="big">${age_over65.toLocaleString()}</span>
  </div>
</div>

<!-- plot attributes -->


```js
// shared sttributes
const attributes = [
  vg.width(600),
  vg.height(150),
  vg.margin(0),
  vg.yAxis(null),
  vg.xDomain([0, 1]),
];
```

```js
const community = sql`
  SELECT *
  FROM cc_data_age_table
  WHERE CCN20 = ${ccn}
`;
```



```js
// remaking line charts 

vg.vconcat(
    vg.plot(
        vg.dot(vg.from("cc_data_age_table"), 
        { x: "age_prop_under18", y: 0 , tip: true}), 
        ...attributes,
        vg.xLabel("Proportion Under 18"), 
    ), 
    vg.plot(
        vg.dot(vg.from("cc_data_age_table"), 
        { x: "age_prop_18_65", y: 0 , tip: true}), 
        ...attributes,
        vg.xLabel("Proportion Between 18 and 64"), 
    ), 
    vg.plot(
        vg.dot(vg.from("cc_data_age_table"), 
        { x: "age_prop_over65", y: 0 , tip: true}), 
        ...attributes,
        vg.xLabel("Proportion 65 and Over"), 
    )
)
```



[insert waffle map and line plots here in story map]

Communities with younger (older) individuals often have different priorities, so understanding where your community sits on this spectrum helps explain which policy fights actually matter locally, even when they don't dominate the district-wide conversation.

[link blocks to causes, e.g. youth – childcare, education, loans – can tag interest groups and integrate with fuzzy matching]
