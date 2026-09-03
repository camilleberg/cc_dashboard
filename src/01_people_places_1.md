---
title: Main Page
sql:
  cc_data: data/cc_data.parquet
  ccn20_geo_raw: data/ccn20_geo_raw.parquet
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

<!-- Style tags-->
<style>
</style>


# Main Page

<span style="color:blue">This page will be dedicated to demographics and the like, there is another page (People and Place) that has the exact same information but with diffent chart options. This one has the three separate graphs as different blocks but with dynamically adjusting domains</span>.

<br>
<input id="autoComplete">
<div id="page-content">

<hr>



```sql id=load_extensions
-- loading spatial extension
INSTALL spatial;
LOAD spatial;
```

```js import_plotly.js
// defining colors
import Plotly from "npm:plotly.js-dist-min";
```

```js import_centroid.js
import * as turf from "@turf/turf";
```

```js import_us_states.js
import states from 'us-state-converter'
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
const block_color = "#f2e9e3";

function highlight(text, index) {
  const highlighted_text = html`<span style="color:${okabeItoColors[index]}">${text}</span>`;
  return highlighted_text;
}

const maplibre_style = "https://tiles.versatiles.org/assets/styles/colorful/style.json";
const page_background_color = "#f9f0ea";
const page_background_color_card = "#f2e9e3";
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

<!-- selecting the community-->

```js
const ccnList = await sql`
    SELECT DISTINCT CCN20
    FROM cc_data
    ORDER BY CCN20
`;

const ccnArray = [...ccnList];
```

```js import_autocomplete.js
//https://tarekraafat.github.io/autoComplete.js/#/installation
import autoComplete from "npm:@tarekraafat/autocomplete.js";
```

```js create_autocomplete.js
const autoCompleteJS = new autoComplete({
    // enter button
    submit: true,
    // message
    placeHolder: "Search for Your Community...",
    // HOLDS HISTROY
    cache: true,
    data: {
        src: ccnArray.map(d => d.CCN20),
        cache: true,
    },
    // SHOWS RESULTS ON CLICK 
    threshold: 0,
    resultsList: {
        maxResults: undefined
    },
    // Need to figure out how to export 
    resultItem: {
        highlight: true
    },
    // actual event
    events: {
    input: {
        selection: (event) => {
            const feedback = event.detail;
            const selection = feedback.selection.value; // flat array — no key needed
            autoCompleteJS.input.value = selection;
            // manually fire the event so Observable's reactivity notices the change
            autoCompleteJS.input.dispatchEvent(new Event("input", { bubbles: true }));
        }
    }
}
});

```

```js assining_output.js
const ccn = Generators.input(autoCompleteJS.input);
```

<!-- Blurring the page -->


```js blur_page.js
const setBlurState = (ccn) => {
  const content = document.getElementById("page-content");
  if (!content) return; // defensive, though this shouldn't happen anymore
  const hasSelection = !(ccn === undefined || ccn === "");
  content.style.filter = hasSelection ? "none" : "blur(5px)";
};

setBlurState(ccn); // runs on load AND re-runs automatically whenever ccn changes
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

```sql id=current_ccn_geo 
-- transforming as geo 
SELECT
  CCN20,
  DC,
  State,
  ST_AsGeoJSON(geometry) AS geometry
  FROM ccn20_geo_raw 
  WHERE CCN20 = ${ccn}
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

const dc_name = cc_data_age
  .getChild("DC")
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

const current_ccn_geojson = JSON.parse(
  current_ccn_geo.getChild("geometry").get(0)
);
```


```js make_div_bucket.js
const myDiv = display(document.createElement("div"));
```


```js helper_functions.js
// Supporting arrays/helpers — define once, before the chart function.
// Fill in real hex values / ordering to match your Python palette.
function floorToDecimals(x, decimals) {
  const factor = 10 ** decimals;
  return Math.floor(x * factor) / factor;
}

function ceilToDecimals(x, decimals) {
  const factor = 10 ** decimals;
  return Math.ceil(x * factor) / factor;
}
```

```js make_waffle.js
// Largest-remainder rounding: turns a list of raw counts into
// integer icon counts (out of totalIcons) that sum exactly to totalIcons.
function allocateIcons(rawCounts, totalIcons) {
  const total = rawCounts.reduce((a, b) => a + b, 0);
  if (total === 0) return rawCounts.map(() => 0);

  const exact = rawCounts.map(c => (c / total) * totalIcons);
  const floored = exact.map(Math.floor);
  let remainder = totalIcons - floored.reduce((a, b) => a + b, 0);

  const order = exact
    .map((v, i) => ({i, frac: v - Math.floor(v)}))
    .sort((a, b) => b.frac - a.frac);

  const result = [...floored];
  for (let k = 0; k < remainder; k++) {
    result[order[k % order.length].i] += 1;
  }
  return result;
}

function renderWaffleLegend(labels, group_list, group_name_list) {
  const legend = document.createElement("div");
  legend.className = "waffle-legend";
  labels.forEach((label) => {
    const colorIdx = group_list.indexOf(label);
    const item = document.createElement("div");
    item.className = "waffle-legend-item";
    item.innerHTML = `
      <span class="waffle-legend-swatch" style="background:${okabeItoColors[colorIdx]}"></span>
      ${group_name_list[colorIdx]}
    `;
    legend.appendChild(item);
  });
  return legend;
}

// to make wafle chart
function renderFullWaffle(labels, countsByLabel, type, group_name_list) {
  const iconClass = 
    type === "people" 
      ? "fa-solid fa-user" 
      : type === "housing" 
        ? "fa-solid fa-house" 
        : type === "households"
          ? "fa-solid fa-people-group"
          : "fa-solid fa-question"; // Required fallback

  const title = 
    type === "people" 
      ? "people" 
      : type === "housing" 
        ? "housing units" 
        : type === "households" 
          ? "households" 
          : "other"; // Required fallback

  const rawCounts = labels.map((label) => countsByLabel[label]);
  const iconCounts = allocateIcons(rawCounts, 100);

  const cellColors = [];
  labels.forEach((label, idx) => {
    const colorIdx = labels.indexOf(label);
    const color = okabeItoColors[colorIdx];
    for (let c = 0; c < iconCounts[idx]; c++) cellColors.push(color);
  });
  while (cellColors.length < 100) cellColors.push(waffleNotUsedColor);

  const grid = document.createElement("div");
  grid.className = "waffle-grid-full";
  cellColors.forEach((color) => {
    const cellIcon = document.createElement("i");
    cellIcon.className = iconClass;
    cellIcon.style.color = color;
    grid.appendChild(cellIcon);
  });

  return html`<div class="waffle-section">
    <div class="waffle-title">If your community was <br> 100 <strong>${title}</strong>...<br><br></div>
    ${renderWaffleLegend(labels, labels, group_name_list)}
    ${grid}
  </div>`;
}
```

```js make_plotly_charts.js
function makeLineCompChartPlotly(label_list, group_list, var_list, type) {
  // choosing the correct dfs 
  const DF_SETS = {
    age: { cc: cc_data_age, dc: dc_data_age, state: state_data_age },
    housing: { cc: cc_data_housing, dc: dc_data_housing, state: state_data_housing }
  };
  const dfSet = DF_SETS[type];
  if (!dfSet) throw new Error(`Unknown type: ${type}`);
  const { cc: df_cc, dc: df_dc, state: df_state } = dfSet;

  
  // colors
  const idx = group_list.indexOf(label_list);
  const notUsed = lighterItoColors[idx];
  const colorUsed = okabeItoColors[idx];


  // number line ticks
  const intervals = Array.from({ length: 11 }, (_, i) => Math.round((i / 10) * 100) / 100);

  // pull proportions straight from the already-computed age_prop_* columns
  const xCc = df_cc.getChild(var_list).get(0);
  const xCd = df_dc.getChild(var_list).get(0);
  const xState = df_state.getChild(var_list).get(0);

  const traces = [];

  // baseline number line (tick marks along y=1)
  traces.push({
    x: intervals,
    y: intervals.map(() => 1),
    mode: "lines+markers",
    marker: { symbol: "line-ns", size: 10, color: "darkgrey", line: { width: 1 } },
    opacity: 0.5,
    hoverinfo: "skip",
    showlegend: false
  });

  // State
  traces.push({
    x: [xState],
    y: [1],
    mode: "markers",
    marker: { symbol: "diamond-x", size: 20, color: notUsed, line: { color: block_color, width: 2 } },
    name: "State",
    hovertemplate: `State: ${(xState * 100).toFixed(1)}%<extra></extra>`
  });

  // Congressional District
  traces.push({
    x: [xCd],
    y: [1],
    mode: "markers",
    marker: { symbol: "circle", size: 20, color: notUsed, line: { color: block_color, width: 2 } },
    name: "Congressional District",
    hovertemplate: `Congressional District: ${(xCd * 100).toFixed(1)}%<extra></extra>`
  });

  // Congressional Community (highlighted color)
  traces.push({
    x: [xCc],
    y: [1],
    mode: "markers",
    marker: { symbol: "circle", size: 20, color: colorUsed, line: { color: block_color, width: 2 } },
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
      color: "darkgrey"
    },
    yaxis: { visible: false, range: [0.9, 1.1] },
    legend: { orientation: "h", yanchor: "bottom", y: 1.02, xanchor: "center", x: 0.5, 
      "itemsizing": "constant", "itemwidth": 10
     },
    height: 200,
    margin: { l: 20, r: 20, t: 40, b: 40 },
    paper_bgcolor: 'rgba(0,0,0,0)', // Makes the outer container transparent
    plot_bgcolor: 'rgba(0,0,0,0)' , 
    hovermode: 'x'
  };

const config = {
  modeBarButtons: [[ 'toImage', 'resetScale2d' ]], 
  displaylogo: false
};

  return { traces, layout, config };
}
```



<!-- Map chart -->


```js import_maplibre.js
import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.6.0/dist/maplibre-gl.mjs';
// bright basemap
display(html`<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@6.6.0/dist/maplibre-gl.css">`);
```

```js find_bounds.js
function boundsFromGeoJSON(geojson) {
  const bounds = new maplibregl.LngLatBounds();

  function extendWithCoords(coords) {
    if (typeof coords[0] === "number") {
      bounds.extend(coords);
    } else {
      coords.forEach(extendWithCoords);
    }
  }

  // handle Feature, bare Geometry, or FeatureCollection
  const geometry = geojson.type === "Feature" ? geojson.geometry
                  : geojson.type === "FeatureCollection" ? null
                  : geojson;

  if (geojson.type === "FeatureCollection") {
    geojson.features.forEach(f => extendWithCoords(f.geometry.coordinates));
  } else {
    extendWithCoords(geometry.coordinates);
  }

  return bounds;
}
```



## Snapshot of your Congressional Community

```js calc_ccn_coords.js
// calculating the lat long
const current_ccn_center = turf.centroid(current_ccn_geojson)
const current_ccn_coords = current_ccn_center.geometry.coordinates
```

```js
const mapDiv = display(document.createElement("div"));
mapDiv.style = "height: 400px;";

const map = new maplibregl.Map({
    container: mapDiv,
    style: maplibre_style,
    // close to center of us, but not wuite 
    center: [ -90.137451890638886, 39.13734351262877],
    zoom: 5
});

map.on('load', () => {
    map.setPaintProperty('background', 'background-color', page_background_color);
    map.addSource('current_ccn_geo', {
        'type': 'geojson',
        'data': current_ccn_geojson
    });
    map.addLayer({
        'id': 'ccn20-fill',
        'type': 'fill',
        'source': 'current_ccn_geo',
        'layout': {},
        'paint': {
            'fill-color': lighterItoColors[6],
            'fill-opacity': 0.6, 
        }
    });
    map.addLayer({
        'id': 'ccn20-line',
        'type': 'line',
        'source': 'current_ccn_geo',
        'layout': {},
        'paint': {
            "line-color": okabeItoColors[6],
            "line-width": 3
        }
    });
    // adding popup 
    // https://maplibre.org/maplibre-gl-js/docs/examples/display-a-popup-on-hover/
    // setting map bounds
    const bounds = boundsFromGeoJSON(current_ccn_geojson);
    map.fitBounds(bounds, { padding: 40 });


    // adding control panels, zoom and everything
    map.addControl(new maplibregl.NavigationControl({
    visualizePitch: true,
    visualizeRoll: true,
    showZoom: true,
    showCompass: true
  }));

   // capture zoom (and center) once the fitBounds animation completes
    let fittedZoom;
    map.once('moveend', () => {
        fittedZoom = map.getZoom();
        console.log('zoom after fitBounds:', fittedZoom);
    });


  // the actual function
  class ResetControl {
    onAdd(map) {
      this._map = map;
      this._container = document.createElement('div');
      this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group';
      
      const button = document.createElement('button');
      button.type = 'button';
      button.innerHTML = '🏠'; // Or use an SVG icon
      button.title = 'Reset Map';
      button.onclick = () => {
        this._map.flyTo({
          center: current_ccn_coords, // Your initial longitude, latitude
          zoom: fittedZoom,
          bearing: 0,
          pitch: 0
        });
      };

      // adding the widget
      this._container.appendChild(button);
      return this._container;
    }

    onRemove() {
      this._container.parentNode.removeChild(this._container);
      this._map = undefined;
    }
  }

  // Add it to your map
  const resetControl = new ResetControl();
  map.addControl(resetControl, 'top-right');

});

```


<!-- To make CD chart -->



```sql id=current_cd_geo 
SELECT DC, 
  STATE, 
  ST_AsGeoJSON(geometry) AS geometry
FROM cd119_geos 
WHERE DC = ${dc_name}
```

```sql id=current_ccn_within_cd_geo 
-- transforming as geo 
  SELECT
    CCN20,
    DC,
    State,
    ST_AsGeoJSON(geometry) AS geometry
    FROM ccn20_geo_raw 
    WHERE DC = ${dc_name}
```

```js calc_ccn_coords.js
// transfomring to geo
const current_cd_geojson = JSON.parse(
  current_cd_geo.getChild("geometry").get(0)
  );
  

// calculating the lat long
const current_cd_center = turf.centroid(current_cd_geojson);
const current_cd_coords = current_cd_center.geometry.coordinates;
```


```js grab_geo_data_dc.js
const current_ccn_within_cd_geojson = {
  type: "FeatureCollection",
  features: current_ccn_within_cd_geo.toArray().map(row => ({
    type: "Feature",
    properties: { CCN20: row.CCN20, DC: row.DC, State: row.State },
    geometry: JSON.parse(row.geometry)
  }))
};
```

```js make_dc_map.js
function create_dc_map(container, { invalidation } = {}) {
  return new Promise((resolve) => {

    // current ccn records 
    const map_district = new maplibregl.Map({
        container: container,
        style: maplibre_style,
        center: current_ccn_coords,
        zoom: 6,
        // causes pan & zoom handlers not to be applied, similar to
        // .dragging.disable() and other handler .disable() functions in Leaflet.
        interactive: false
    });

    //current cnn backgrounf
    map_district.on('load', () => {
      map_district.setPaintProperty('background', 'background-color', page_background_color_card);

        // current ccns
      map_district.addSource('current_ccn_within_cd_geo', {
          'type': 'geojson',
          'data': current_ccn_within_cd_geojson
      });
      map_district.addLayer({
            'id': 'ccn20-fill',
            'type': 'fill',
            'source': 'current_ccn_within_cd_geo',
            'layout': {},
            'paint': {
                'fill-color': lighterItoColors[6],
                'fill-opacity': 0.6,
            }
        });

      // cd outline
      map_district.addSource('current_cd_geo', {
          'type': 'geojson',
          'data': current_cd_geojson
      });
      map_district.addLayer({
            'id': 'cd-line',
            'type': 'line',
            'source': 'current_cd_geo',
            'layout': {},
            'paint': {
                'line-color': lighterItoColors[6],
                'line-width': 5,
            }
        });

      // adding in outline for current
      map_district.addSource('current_ccn_geo', {
            'type': 'geojson',
            'data': current_ccn_geojson
        });
      map_district.addLayer({
          'id': 'ccn20-line',
          'type': 'line',
          'source': 'current_ccn_geo',
          'layout': {},
          'paint': {
              "line-color": okabeItoColors[6],
              "line-width": 3
          }
      });

      resolve(map_district);
    });

    // clean up when this cell reruns or is removed, if the caller passed invalidation in
    if (invalidation) {
      invalidation.then(() => map_district.remove());
    }
  });
}
```





<hr>

## People and Places


<!-- Waffle chart -->

```js display_waffle.js
const countsByLabel_age = {
  under18: age_under_18,
  "18_65": age_18_65,
  over65: age_over65
};
const ageBracketCols = ["over65", "18_65", "under18"];
const ageGroupNames = ["65 and Older", "Between 18 and 64", "18 and Younger"]
```

```js
async function buildMapDcAge() {
  const container = document.createElement("div");
  container.style = "height: 300px;";
  const map = await create_dc_map(container, { invalidation });
  requestAnimationFrame(() => map.resize());
  return container;
}
const map_dc_age = buildMapDcAge()
```



<div class="grid grid-cols-3" style="grid-auto-rows: 330px;">
  <div class="card">${
    resize((width) => renderFullWaffle(ageBracketCols, countsByLabel_age, "people", ageGroupNames))
  }</div>
  <div class="card grid-colspan-2">${
    resize((width) => map_dc_age)
  }
  </div>
</div>

<!-- Text -->


<center>
Your congressional community, <strong>${ccn}</strong>, is a community of <strong>${cc_tot_pop.toLocaleString()}</strong> individuals. Compared to your congressional district of <strong>${Math.abs(dc_tot_pop).toFixed(0).toLocaleString()}</strong> people, your community skews <strong>${cc_dc_younger}</strong> by <strong>${(Math.abs(cc_dc_diff) * 100).toFixed(1)} percentage points</strong>. It is similarly <strong>${cc_state_younger}</strong> than <strong>${states.fullName(state_name)}</strong>, by <strong>${(Math.abs(cc_state_diff) * 100).toFixed(1)} percentage points</strong>.
</center>
<!-- Cards with big numbers -->

<div class="grid grid-cols-3">
  <div class="card">
    <h3>${highlight("Under 18 Population", 2)}</h3>
    <span class="big">${highlight(age_under_18.toLocaleString(), 2)}</span>
  </div>
  <div class="card">
    <h3>${highlight("18 to 64 Population", 1)}</h3>
    <span class="big">${highlight(age_18_65.toLocaleString(), 1)}</span>
  </div>
  <div class="card">
    <h3>${highlight("65 and Over Population", 0)}</h3>
    <span class="big">${highlight(age_over65.toLocaleString(), 0)}</span>
  </div>
</div>

<!-- plotly graphs -->

```js make_plotly_var_list_age.js
const ageKey = [`age_prop_under18`, 'age_prop_18_65', 'age_prop_over65'];
```

<div class="grid grid-cols-3" style="grid-auto-rows: 220px;">
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("under18", ageBracketCols, ageKey[0], "age");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("18_65", ageBracketCols, ageKey[1], "age");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("over65", ageBracketCols, ageKey[2], "age");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
</div>


<!-- plot attributes -->

<center>
Communities with younger (older) individuals often have different priorities, so understanding where your community sits on this spectrum helps explain which policy fights actually matter locally, even when they don't dominate the district-wide conversation.

</center>

[link blocks to causes, e.g. youth – childcare, education, loans – can tag interest groups and integrate with fuzzy matching]

<hr>

## Housing

<!-- creating the tables for housing-->

```sql id=create_tables_housing 

CREATE OR REPLACE TABLE cc_data_housing_table AS

WITH base AS (
    SELECT
        CCN20,
        DC,
        State,
        "Total housing units" AS tot_housing,

        "Occupied housing units - total housing units" AS tot_hholds,

        "Owner-occupied housing units - Housing Tenure"
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

        "Owner-occupied housing units - Housing Tenure"
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
        AS housing_occupancy_rate,

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

        "Owner-occupied housing units - Housing Tenure"
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

```sql id=cc_data_housing
SELECT *, 
  1 - housing_occupancy_rate AS housing_vacancy_rate, 
  1 - housing_ownership_rate AS housing_rental_rate
FROM cc_data_housing_table
WHERE CCN20 = ${ccn};
```

```sql id=dc_data_housing
SELECT *, 
  1 - housing_occupancy_rate AS housing_vacancy_rate, 
  1 - housing_ownership_rate AS housing_rental_rate
FROM dc_data_housing_table
WHERE DC = (
    SELECT DC
    FROM cc_data_housing_table
    WHERE CCN20 = ${ccn}
);
```

```sql id=state_data_housing
SELECT *, 
  1 - housing_occupancy_rate AS housing_vacancy_rate, 
  1 - housing_ownership_rate AS housing_rental_rate
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

// for waffle
const cc_vacant_units = cc_tot_housing - cc_tot_hholds;
const cc_owned_units = cc_data_housing
  .getChild("hholds_ownership_own")
  .get(0);
const cc_rented_units = cc_tot_hholds - cc_owned_units

```



<span style="color:blue">This housing data pull /analysis is in progress!</span>.

### Housing Units

<!-- Waffle chart -->


```js assign_housing_waffle.js
const vacancyCols = ["occupied", "vacant"];
const countsByLabel_vacancy = {
  occupied: cc_tot_hholds,
  vacant: cc_vacant_units,
}

const vacancyGroupNames = ["Occupied Units", "Vacant Units"]
```


<div class="grid grid-cols-2" style="grid-auto-rows: 310px;">
  <div class="card">${
    resize((width) => renderFullWaffle(vacancyCols, countsByLabel_vacancy, "housing", vacancyGroupNames))
  }</div>
  <div class="card">${
    
  }
  </div>
</div>



In general, 

<div class="grid grid-cols-2">
  <div class="card">
    <h3>${highlight("Occupied Units", 0)}</h3>
    <span class="big">${highlight(cc_tot_hholds.toLocaleString(), 0)}</span>
  </div>
  <div class="card">
    <h3>${highlight("Vacant Units", 1)}</h3>
    <span class="big">${highlight(cc_vacant_units.toLocaleString(), 1)}</span>
  </div>
</div>


<!-- plotly graphs -->

```js make_plotly_var_list_vacancy.js
const vacancyKey = [`housing_occupancy_rate`, 'housing_vacancy_rate'];
```


<div class="grid grid-cols-2" style="grid-auto-rows: 220px;">
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("occupied", vacancyCols, vacancyKey[0], "housing");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("vacant", vacancyCols, vacancyKey[1], "housing");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
</div>


### Households

```js assign_hhold_waffle.js
const ownershipCols = ["owned", "rented"]
const countsByLabel_ownership = {
  owned: cc_owned_units,
  rented: cc_rented_units
}
const ownershipGroupNames = ["Owned Households", "Rented Households"]
```

<!-- waffle chart!-->

<div class="grid grid-cols-2" style="grid-auto-rows: 310px;">
  <div class="card">${
    resize((width) => renderFullWaffle(ownershipCols, countsByLabel_ownership, "households", ownershipGroupNames))
  }</div>
  <div class="card">${
   
  }
  </div>
</div>

Of all occupied **${cc_tot_hholds.toLocaleString()}** housing units, **${Math.abs(cc_own_rate * 100).toFixed(1).toLocaleString()}**% are owned. That means that, compared to your congressional district and state, your congressional district's homeownership rate is **${Math.abs(cc_dc_diff_own_rate*100).toFixed(1).toLocaleString()}** percentage points **${cc_dc_ownership}** and your state's homeownerhsip rate is **${Math.abs(cc_state_diff_own_rate*100).toFixed(1).toLocaleString()}** percentage points **${cc_state_ownership}**. 

<!-- cards with big numbers -->

<div class="grid grid-cols-2">
  <div class="card">
    <h3>${highlight("Homeowner Households", 0)}</h3>
    <span class="big">${highlight(cc_owned_units.toLocaleString(), 0)}</span>
  </div>
  <div class="card">
    <h3>${highlight("Renter Househoolds", 1)}</h3>
    <span class="big">${highlight(cc_rented_units.toLocaleString(), 1)}</span>
  </div>
</div>


<!-- plotly graphs -->

```js make_plotly_var_list_owner.js
const ownershipKey = [`housing_ownership_rate`, 'housing_rental_rate'];
```


<div class="grid grid-cols-2" style="grid-auto-rows: 220px;">
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("owned", ownershipCols, ownershipKey[0], "housing");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
  <div class="card">${
    resize((width) => {
      const div = document.createElement("div");
      const { traces, layout, config } = makeLineCompChartPlotly("rented", ownershipCols, ownershipKey[1], "housing");
      Plotly.newPlot(div, traces, { ...layout, width }, config);
      return div;
    }) 
  }</div>
</div>


Given the current state of the housing market, homeownership rates say a lot about how exposed a community is to rent increases, displacement, and housing-cost burden. Policies like rent stabilization or first-time buyer programs will therefore have varying levels of impact depending on the local environment. Knowing more about housing in your community can help you and your representative understand which policies will actually help you.
[link blocks to causes — e.g., renters → tenant protections, rent stabilization; owners → property tax relief, homeowner assistance programs]
