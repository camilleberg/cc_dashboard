---
title: Housing
sql:
  cc_data: data/cc_data.parquet
---

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2M9HMSTWCC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-2M9HMSTWCC');
</script>



# Housing



```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

```js import_plotly.js
// defining colors
import Plotly from "npm:plotly.js-dist-min";
```


```js
// Font Awesome is only a stylesheet, so a <link> tag is safe here
// (unlike a <script> tag, which won't execute when inserted this way).
display(html`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">`);
```

```js
display(html`<style>
  .waffle-section { margin: 10px  30px 0; text-align: center; }
  .waffle-legend { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; margin: 0 auto 14px auto; width: fit-content; font-size: 12px; color: #333; }
  .waffle-legend-item { display: flex; align-items: ; gap: 6px; }
  .waffle-legend-swatch { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
  .waffle-grid-full { display: grid; grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(10, 1fr); gap: 2px; width: 220px; margin: 0 auto; }
  .waffle-grid-full i { font-size: 16px; line-height: 1; }
</style>`);
```
<!-- color block-->

```js assigning_colors.js
const okabeItoColors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000'];
// # at 40 % lighter
const lighterItoColors = ['#F0C566', '#99D2F1', '#66C4AB', '#F6EE8D', '#66AAD0', '#E59E66', '#E0AECA', '#666666'];
const waffleNotUsedColor = "#D8D8D8";

function highlight(text, index) {
  const highlighted_text = html`<span style="color:${okabeItoColors[index]}">${text}</span>`;
  return highlighted_text;
}
```


<!-- creating the tables-->

```sql id=create_tables_housing 

CREATE OR REPLACE TABLE cc_data_housing_table AS

WITH base AS (
    SELECT
        CCN20,
        DC,
        State,
        "Total housing units" AS tot_housing,

        "Occupied housing units - total housing units" AS tot_hholds,

        "Occupied housing units - total housing units"
            - "Owner-occupied housing units - Housing Tenure"
            AS hholds_ownership_own,
    
    FROM cc_data
)

SELECT
    *,
    tot_hholds 
        / NULLIF(tot_housing, 0)::DOUBLE
        AS housing_occupancy_rate,

    hholds_ownership_own
        / NULLIF(tot_hholds, 0)::DOUBLE
        AS housing_ownership_rate,


FROM base;


CREATE OR REPLACE TABLE dc_data_housing_table AS

WITH base AS (
    SELECT
        DC,

        "Total housing units" AS tot_housing,

        "Occupied housing units - total housing units" AS tot_hholds, 

        "Occupied housing units - total housing units"
            - "Owner-occupied housing units - Housing Tenure"
            AS hholds_ownership_own,
    
    FROM cc_data
)

SELECT
    DC,

    SUM(tot_housing) AS tot_housing,
    SUM(tot_hholds) AS tot_hholds,
    SUM(hholds_ownership_own) AS hholds_ownership_own,

    SUM(tot_hholds)
        / NULLIF(SUM(tot_housing), 0)::DOUBLE
        AS ousing_occupancy_rate,

    SUM(hholds_ownership_own)
        / NULLIF(SUM(tot_hholds), 0)::DOUBLE
        AS housing_ownership_rate,

FROM base
GROUP BY DC;


CREATE OR REPLACE TABLE state_data_housing_table AS

WITH base AS (
    SELECT
        State,

        "Total housing units" AS tot_housing,

        "Occupied housing units - total housing units" AS tot_hholds, 

        "Occupied housing units - total housing units"
            - "Owner-occupied housing units - Housing Tenure"
            AS hholds_ownership_own,
    
    FROM cc_data
)

SELECT
    State,

    SUM(tot_housing) AS tot_housing,
    SUM(tot_hholds) AS tot_hholds,
    SUM(hholds_ownership_own) AS hholds_ownership_own,

    SUM(tot_hholds)
        / NULLIF(SUM(tot_housing), 0)::DOUBLE
        AS housing_occupancy_rate,

    SUM(hholds_ownership_own)
        / NULLIF(SUM(tot_hholds), 0)::DOUBLE
        AS housing_ownership_rate,

FROM base
GROUP BY State;
```

```js
// for proof of concept
const ccn = "4830001";
```

```sql id=cc_data_housing
SELECT *
FROM cc_data_housing_table
WHERE CCN20 = ${ccn};
```

```sql id=dc_data_housing
SELECT *
FROM dc_data_housing_table
WHERE DC = (
    SELECT DC
    FROM cc_data_housing_table
    WHERE CCN20 = ${ccn}
);
```

```sql id=state_data_housing
SELECT *
FROM state_data_housing_table
WHERE State = (
    SELECT State
    FROM cc_data_housing_table
    WHERE CCN20 = ${ccn}
);
```


<!-- Cleaning and extracting data-->
```js
const cc_tot_housing = cc_data_housing
  .getChild("tot_housing")
  .get(0);

const dc_tot_housing = dc_data_housing
  .getChild("tot_housing")
  .get(0);

const state_tot_housing = state_data_housing
  .getChild("tot_housing")
  .get(0);

const cc_tot_hholds = cc_data_housing
  .getChild("tot_hholds")
  .get(0);

const cc_occupancy_rate = cc_data_housing
  .getChild("housing_occupancy_rate")
  .get(0);

const dc_occupancy_rate = dc_data_housing
  .getChild("housing_occupancy_rate")
  .get(0);

const state_occupancy_rate = state_data_housing
  .getChild("housing_occupancy_rate")
  .get(0);

const cc_own_rate = cc_data_housing
  .getChild("housing_ownership_rate")
  .get(0);

const dc_own_rate = dc_data_housing
  .getChild("housing_ownership_rate")
  .get(0);

const state_own_rate = state_data_housing
  .getChild("housing_ownership_rate")
  .get(0);

const cc_dc_diff_own_rate =
  cc_own_rate - dc_own_rate;

const cc_dc_ownership =
  cc_dc_diff_own_rate > 0 ? "higher" : "lower";

const cc_state_diff_own_rate =
  cc_own_rate - state_own_rate;

const cc_state_ownership =
  cc_state_diff_own_rate > 0 ? "higher" : "lower";

```


<span style="color:blue">This housing data pull /analysis is in progress!</span>.



In general, your community has **${cc_tot_housing.toLocaleString()}** housing units, of which **${Math.abs(cc_own_rate).toFixed(0).toLocaleString()}**% are owned. That means that, compared to your congressional district and state, there are x.x% and x.x% more (fewer) homeowners, respectively.
[insert graph about housing]
Given the current state of the housing market, homeownership rates say a lot about how exposed a community is to rent increases, displacement, and housing-cost burden. Policies like rent stabilization or first-time buyer programs will therefore have varying levels of impact depending on the local environment. Knowing more about housing in your community can help you and your representative understand which policies will actually help you.
[link blocks to causes — e.g., renters → tenant protections, rent stabilization; owners → property tax relief, homeowner assistance programs]
