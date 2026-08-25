---
title: People and Places Copy
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

```js
import Plotly from "npm:plotly.js-dist-min";
```

<!-- creating the tables-->

```sql id=create_tables

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

<div class="grid grid-cols-2 style="grid-auto-rows: 504px;">
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

```js
const myDiv = display(document.createElement("div"));
```

```js
// Supporting arrays/helpers — define once, before the chart function.
// Fill in real hex values / ordering to match your Python palette.
const ageBracketCols = ["over65", "18_65", "under18"];
const ageGroupNames = ["65 and Older", "Between 18 and 64", "18 and Younger"]
const okabeItoColors = ["#E69F00", "#56B4E9", "#009E73"];
const lighterItoColors = ["#F5D08A", "#B7E1F5", "#8FD9C4"];

function floorToDecimals(x, decimals) {
  const factor = 10 ** decimals;
  return Math.floor(x * factor) / factor;
}

function ceilToDecimals(x, decimals) {
  const factor = 10 ** decimals;
  return Math.ceil(x * factor) / factor;
}
```


```js
function makeLineCompChartPlotly(ageGroupLabel) {
  const idx = ageBracketCols.indexOf(ageGroupLabel);
  const notUsed = lighterItoColors[idx];
  const colorUsed = okabeItoColors[idx];

  // number line ticks
  const intervals = Array.from({ length: 11 }, (_, i) => Math.round((i / 10) * 100) / 100);

  // pull proportions straight from the already-computed age_prop_* columns
  const propKey = `age_prop_${ageGroupLabel}`;
  const xCc = cc_data_age.getChild(propKey).get(0);
  const xCd = dc_data_age.getChild(propKey).get(0);
  const xState = state_data_age.getChild(propKey).get(0);

  const traces = [];

  // baseline number line (tick marks along y=1)
  traces.push({
    x: intervals,
    y: intervals.map(() => 1),
    mode: "lines+markers",
    marker: { symbol: "line-ns", size: 10, color: "lightgrey", line: { width: 1 } },
    opacity: 0.5,
    hoverinfo: "skip",
    showlegend: false
  });


  // State
  traces.push({
    x: [xState],
    y: [1],
    mode: "markers",
    marker: { symbol: "diamond-x", size: 20, color: notUsed, line: { color: "white", width: 2 } },
    name: "State",
    hovertemplate: `State: ${(xState * 100).toFixed(1)}%<extra></extra>`
  });

  // Congressional District
  traces.push({
    x: [xCd],
    y: [1],
    mode: "markers",
    marker: { symbol: "circle", size: 20, color: notUsed, line: { color: "white", width: 2 } },
    name: "Congressional District",
    hovertemplate: `Congressional District: ${(xCd * 100).toFixed(1)}%<extra></extra>`
  });

  // Congressional Community (highlighted color)
  traces.push({
    x: [xCc],
    y: [1],
    mode: "markers",
    marker: { symbol: "circle", size: 20, color: colorUsed, line: { color: "white", width: 2 } },
    name: "Congressional Community",
    hovertemplate: `Congressional Community: ${(xCc * 100).toFixed(1)}%<extra></extra>`
  });

  // dynamically adjust x range
  const xMin = floorToDecimals(Math.min(xCc, xCd, xState), 1) - 0.01;
  const xMax = ceilToDecimals(Math.max(xCc, xCd, xState), 2) + 0.07;

  const layout = {
    xaxis: {
      range: [xMin, xMax],
      tickmode: "array",
      tickvals: intervals,
      ticktext: intervals.map((v) => `${Math.round(v * 100)}%`),
      showgrid: false,
      zeroline: false,
      color: "lightgrey"
    },
    yaxis: { visible: false, range: [0.9, 1.1] },
    legend: { orientation: "h", yanchor: "bottom", y: 1.02, xanchor: "center", x: 0.5 },
    height: 200,
    margin: { l: 20, r: 20, t: 40, b: 40 },
    paper_bgcolor: 'rgba(0,0,0,0)', // Makes the outer container transparent
    plot_bgcolor: 'rgba(0,0,0,0)'  
  };

  return { traces, layout };
}
```



<div class="grid grid-cols-3" style="grid-auto-rows: 200px;">
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout } = makeLineCompChartPlotly("under18");
      Plotly.newPlot(div, traces, { ...layout, width });
      return div;
    }) 
  }</div>
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout } = makeLineCompChartPlotly("18_65");
      Plotly.newPlot(div, traces, { ...layout, width });
      return div;
    }) 
  }</div>
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout } = makeLineCompChartPlotly("over65");
      Plotly.newPlot(div, traces, { ...layout, width });
      return div;
    }) 
  }</div>
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

# remaking line maps in javascript



[insert waffle map and line plots here in story map]

Communities with younger (older) individuals often have different priorities, so understanding where your community sits on this spectrum helps explain which policy fights actually matter locally, even when they don't dominate the district-wide conversation.

[link blocks to causes, e.g. youth – childcare, education, loans – can tag interest groups and integrate with fuzzy matching]
