---
title: Current Draft
---

# Current Draft

+ updated Aug 20, 2025
+ Last meeting on Aug 14, 2026

```js
import * as Plotly from "npm:plotly.js-dist-min";
```

```js
// Font Awesome is only a stylesheet, so a <link> tag is safe here
// (unlike a <script> tag, which won't execute when inserted this way).
display(html`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">`);
```

```js
display(html`<style>
  select { font-size: 16px; margin: 10px 10px 10px 0; }
  .chart-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
  }
  .chart-plot { flex: 1 1 auto; min-width: 0; height: 180px; }
  .stats-container { display: flex; flex-direction: column; gap: 10px; min-width: 100px; }
  .stat-card { font-family: Arial, sans-serif; padding: 16px; border-radius: 8px; background: #f4f6f9; }
  .stat-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold; }
  .stat-value { font-size: 28px; margin-top: 4px; }
  .page-layout { display: flex; align-items: flex-start; gap: 24px; }
  .main-content { flex: 1 1 auto; min-width: 0; }
  .right-panel { flex: 0 0 260px; position: sticky; top: 16px; }
  .waffle-section { margin: 10px 0 30px 0; text-align: center; }
  .waffle-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 12px; }
  .waffle-legend { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; margin: 0 auto 14px auto; width: fit-content; font-size: 12px; color: #333; }
  .waffle-legend-item { display: flex; align-items: center; gap: 6px; }
  .waffle-legend-swatch { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
  .waffle-grid-full { display: grid; grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(10, 1fr); gap: 2px; width: 220px; margin: 0 auto; }
  .waffle-grid-full i { font-size: 16px; line-height: 1; }
</style>`);
```

```js
// FileAttachment replaces the manual fetch() — Framework handles
// loading, caching, and build-time bundling of the data file for you.
const ageCcData = FileAttachment("./data/age_cc_data.json").json();
```

```js
const okabeItoColors = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"];
const lighterItoColors = ["#F5CC7F", "#A9DBF3", "#79CBB0", "#F8F19A", "#7FB8D8", "#EBA080", "#E2B9CF"];
const age_bracket_names = ["Under 18", "18-64", "65 and over"];
const greyscale_color = ["#D8D8D8", "#A2A2A2"];
const waffleNotUsedColor = "#D8D8D8";
```

```js
// pure helper functions — no DOM references, so they're easy to test on their own
function floorToDecimals(val, decimals) {
  const factor = Math.pow(10, decimals);
  return Math.floor(val * factor) / factor;
}

function ceilToDecimals(val, decimals) {
  const factor = Math.pow(10, decimals);
  return Math.ceil(val * factor) / factor;
}

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
```

```js
// Reactive dropdown built from a plain <select>, wired up with
// Generators.input — a built-in Framework global, so this needs no
// npm import. `ccn20` updates automatically whenever the user picks
// a new option, and every cell below that reads `ccn20` reruns on
// its own — no manual event listener or re-render call needed.
const ccn20List = Object.keys(ageCcData);

const ccn20Select = document.createElement("select");
ccn20List.forEach(id => {
  const opt = document.createElement("option");
  opt.value = id;
  opt.textContent = id;
  ccn20Select.appendChild(opt);
});

const initialCcn20 = new URLSearchParams(location.search).get("ccn20");
if (initialCcn20 && ccn20List.includes(initialCcn20)) {
  ccn20Select.value = initialCcn20;
}

display(ccn20Select);
```

```js
const ccn20 = Generators.input(ccn20Select);
```

```js
const d = ageCcData[ccn20];
const ageBrackets = d.age_brackets;
```

```js
// keep the URL in sync with the current selection (optional, but preserves
// the old "shareable link" behavior)
{
  const url = new URL(location);
  url.searchParams.set("ccn20", ccn20);
  history.replaceState({}, "", url);
}
```

```js
function renderWaffleLegend(ageBrackets) {
  const legend = document.createElement("div");
  legend.className = "waffle-legend";
  ageBrackets.forEach((label, i) => {
    const item = document.createElement("div");
    item.className = "waffle-legend-item";
    item.innerHTML = `
      <span class="waffle-legend-swatch" style="background:${okabeItoColors[i % okabeItoColors.length]}"></span>
      ${age_bracket_names[i] ?? label}
    `;
    legend.appendChild(item);
  });
  return legend;
}

function renderFullWaffle(ageBrackets, d) {
  const rawCounts = ageBrackets.map(label => d.cc[label]);
  const iconCounts = allocateIcons(rawCounts, 100);

  const cellColors = [];
  iconCounts.forEach((count, idx) => {
    const color = okabeItoColors[idx % okabeItoColors.length];
    for (let c = 0; c < count; c++) cellColors.push(color);
  });
  while (cellColors.length < 100) cellColors.push(waffleNotUsedColor);

  const grid = document.createElement("div");
  grid.className = "waffle-grid-full";
  cellColors.forEach(color => {
    const icon = document.createElement("i");
    icon.className = "fa-solid fa-user";
    icon.style.color = color;
    grid.appendChild(icon);
  });

  return html`<div class="waffle-section">
    <div class="waffle-title">If your community was 100 people... by age</div>
    ${renderWaffleLegend(ageBrackets)}
    ${grid}
  </div>`;
}

display(renderFullWaffle(ageBrackets, d));
```

```js
function statCard(label, value, color) {
  const card = document.createElement("div");
  card.className = "stat-card";
  card.innerHTML = `
    <span class="stat-label" style="color:${color}">${label}</span>
    <div class="stat-value" style="color:${color}">${value}</div>
  `;
  return card;
}

function buildDashboard(ageBrackets, d) {
  const container = document.createElement("div");
  container.className = "main-content";

  ageBrackets.forEach((label, i) => {
    const color = okabeItoColors[i % okabeItoColors.length];

    const xCc = d.cc[label] / d.cc_total;
    const xCd = d.cd[label] / d.cd_total;
    const diff_cc_cd = xCc - xCd;

    const row = document.createElement("div");
    row.className = "chart-row";

    const statsContainer = document.createElement("div");
    statsContainer.className = "stats-container";
    statsContainer.appendChild(statCard("Community Population", d.cc[label].toLocaleString(), color));
    statsContainer.appendChild(statCard("Community vs<br>Congressional District", (diff_cc_cd * 100).toFixed(2) + "%", color));

    const chartDiv = document.createElement("div");
    chartDiv.id = `chart_${i}`;
    chartDiv.className = "chart-plot";

    row.appendChild(statsContainer);
    row.appendChild(chartDiv);
    container.appendChild(row);
  });

  return container;
}

const dashboard = buildDashboard(ageBrackets, d);
display(dashboard);
```

```js
// Plotly needs the chart divs to already be attached to the DOM,
// so this cell runs after `dashboard` above has been displayed.
function renderChart(divId, ageLabel, ageIndex, d) {
  const notUsed = lighterItoColors[ageIndex];
  const colorUsed = okabeItoColors[ageIndex];

  const xCc = d.cc[ageLabel] / d.cc_total;
  const xCd = d.cd[ageLabel] / d.cd_total;
  const xState = d.state[ageLabel] / d.state_total;

  const intervals = [];
  for (let i = 0; i <= 20; i++) intervals.push(Math.round((i / 20) * 100) / 100);

  const traces = [
    {x: [null], y: [null], type: "scatter", mode: "markers",
     marker: {symbol: "diamond", size: 20, color: greyscale_color[0], line: {color: "white", width: 2}},
     name: "State", showlegend: ageIndex === 0},
    {x: [null], y: [null], type: "scatter", mode: "markers",
     marker: {symbol: "circle", size: 20, color: greyscale_color[0], line: {color: "white", width: 2}},
     name: "Congressional District", showlegend: ageIndex === 0},
    {x: [null], y: [null], type: "scatter", mode: "markers",
     marker: {symbol: "circle", size: 20, color: greyscale_color[1], line: {color: "white", width: 2}},
     name: "Congressional Community", showlegend: ageIndex === 0},
    {x: intervals, y: intervals.map(() => 1), mode: "lines+markers",
     marker: {symbol: "line-ns", size: 10, color: "lightgrey", line: {width: 2, color: "lightgrey"}},
     opacity: 0.5, hoverinfo: "skip", showlegend: false},
    {x: [xState], y: [1], mode: "markers",
     marker: {symbol: "diamond", size: 20, color: notUsed, line: {color: "white", width: 2}},
     name: "State", showlegend: false,
     hovertemplate: `State: ${(xState * 100).toFixed(1)}%<extra></extra>`},
    {x: [xCd], y: [1], mode: "markers",
     marker: {symbol: "circle", size: 20, color: notUsed, line: {color: "white", width: 2}},
     name: "Congressional District", showlegend: false,
     hovertemplate: `Congressional District: ${(xCd * 100).toFixed(1)}%<extra></extra>`},
    {x: [xCc], y: [1], mode: "markers",
     marker: {symbol: "circle", size: 20, color: colorUsed, line: {color: "white", width: 2}},
     name: "Congressional Community", showlegend: false,
     hovertemplate: `Congressional Community: ${(xCc * 100).toFixed(1)}%<extra></extra>`}
  ];

  const xMin = floorToDecimals(Math.min(xCc, xCd, xState), 1);
  const xMax = ceilToDecimals(Math.max(xCc, xCd, xState), 1);

  const layout = {
    title: {text: "Group: " + age_bracket_names[ageIndex], font: {size: 13, color: "darkgrey"}, x: 0.01, xanchor: "left", yanchor: "top", y: 0.7},
    xaxis: {
      range: [xMin, xMax],
      tickmode: "array",
      tickvals: intervals,
      ticktext: intervals.map(v => `${Math.round(v * 100)}%`),
      showgrid: false,
      zeroline: false,
      color: "lightgrey"
    },
    yaxis: {visible: false, range: [0.9, 1.1]},
    legend: ageIndex === 0
      ? {orientation: "h", yanchor: "bottom", y: 1.3, xanchor: "center", x: 0.5}
      : {},
    height: 180,
    width: 900,
    margin: {l: 20, r: 20, t: ageIndex === 0 ? 60 : 30, b: 30},
    plot_bgcolor: "white"
  };

  Plotly.newPlot(divId, traces, layout, {displayModeBar: false, responsive: true});
}

ageBrackets.forEach((label, i) => renderChart(`chart_${i}`, label, i, d));
```