---
title: Current Draft
---
# Current Draft

+  updated Aug 20, 2025
+ Last meeting on Aug 14, 2026

```js
display(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    body { margin: 0; font-family: sans-serif; padding: 10px; }
    select { font-size: 16px; margin: 10px 10px 10px 0; }
    .chart-row {
      display: flex;
      align-items: center;
      margin-bottom: -20px;
    }
    .chart-plot {
      flex: 1 1 auto;
      min-width: 0;
    }
    .stat-card {
      flex: 0 0 auto;
      margin-left: 16px;
    }
    .page-layout {
      display: flex;
      align-items: flex-start;
      gap: 24px;
    }
    .main-content {
      flex: 1 1 auto;
      min-width: 0;
    }
    .right-panel {
      flex: 0 0 260px;
      position: sticky;
      top: 16px;
    }
    .waffle-section {
      margin: 10px 0 30px 0;
      text-align: center;
    }
    .waffle-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 12px;
    }
    .waffle-legend {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
      margin: 0 auto 14px auto;
      width: fit-content;
      font-size: 12px;
      color: #333;
    }
    .waffle-legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .waffle-legend-swatch {
      width: 12px;
      height: 12px;
      border-radius: 2px;
      display: inline-block;
    }
    .waffle-grid-full {
      display: grid;
      grid-template-columns: repeat(10, 1fr);
      grid-template-rows: repeat(10, 1fr);
      gap: 2px;
      width: 220px;
      margin: 0 auto;
    }
    .waffle-grid-full i {
      font-size: 16px;
      line-height: 1;
    }
  </style>
</head>
<body>

  <div class="page-layout">
    <div class="main-content">
      <select id="ccn20Select"></select>
      <div id="chartsContainer"></div>
    </div>

    <div class="right-panel">
      <div class="waffle-section">
        <div class="waffle-title">If your community was 100 people...by age</div>
        <div id="waffleLegend" class="waffle-legend"></div>
        <div id="waffleFull" class="waffle-grid-full"></div>
      </div>
    </div>
  </div>

  <script>
    const okabeItoColors = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"];
    const lighterItoColors = ["#F5CC7F", "#A9DBF3", "#79CBB0", "#F8F19A", "#7FB8D8", "#EBA080", "#E2B9CF"];
    const age_bracket_names = ["Under 18", "18-64", "65 and over"];
    const greyscale_color = ["#D8D8D8", "#A2A2A2"];
    const waffleNotUsedColor = "#D8D8D8";

    let allData = {};
    let currentCcn20 = null;

    fetch('../data/age_cc_data.json')
      .then(res => res.json())
      .then(data => {
        allData = data;
        const ccn20List = Object.keys(data);
        populateCcn20Dropdown(ccn20List);

        const params = new URLSearchParams(window.location.search);
        currentCcn20 = params.get('ccn20') || ccn20List[0];

        document.getElementById('ccn20Select').value = currentCcn20;
        buildChartContainers(allData[currentCcn20].age_brackets);
        renderFullWaffle(allData[currentCcn20].age_brackets);
        renderAllCharts();
      });

    function populateCcn20Dropdown(ccn20List) {
      const select = document.getElementById('ccn20Select');
      ccn20List.forEach(id => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = id;
        select.appendChild(opt);
      });
      select.addEventListener('change', (e) => {
        currentCcn20 = e.target.value;
        buildChartContainers(allData[currentCcn20].age_brackets);
        renderFullWaffle(allData[currentCcn20].age_brackets);
        renderAllCharts();
        updateUrl();
      });
    }

    // creates one row per age bracket: a chart div and a stat card, left to right
    function buildChartContainers(ageBrackets) {
        const container = document.getElementById('chartsContainer');
        container.innerHTML = '';

        ageBrackets.forEach((label, i) => {
            const color = okabeItoColors[i % okabeItoColors.length];

            // Row: stats | chart
            const row = document.createElement('div');
            row.className = 'chart-row';
            row.style.display = 'flex';
            row.style.alignItems = 'center';
            row.style.gap = '10px';
            row.style.marginBottom = '20px';

            // Chart
            const chartDiv = document.createElement('div');
            chartDiv.id = `chart_${i}`;
            chartDiv.className = 'chart-plot';
            chartDiv.style.flex = '1';
            chartDiv.style.height = '180px';
            chartDiv.style.minWidth = '0'; // allow shrinking

            // Vertical stats container
            const statsContainer = document.createElement('div');
            statsContainer.className = 'stats-container';
            statsContainer.style.display = 'flex';
            statsContainer.style.flexDirection = 'column';
            statsContainer.style.gap = '10px';
            statsContainer.style.minWidth = '100px';

            // Stat card 1
            const statDiv = document.createElement('div');
            statDiv.innerHTML = `
            <div style="
                font-family: Arial, sans-serif;
                padding:16px;
                border-radius:8px;
                background:#f4f6f9;
            ">
                <span
                id="stat_label_${i}"
                style="
                    font-size:12px;
                    text-transform:uppercase;
                    letter-spacing:0.5px;
                    color:${color};
                    font-weight:bold;
                ">
                Community Population
                </span>

                <div
                id="stat_value_${i}"
                style="
                    font-size:28px;
                    color:${color};
                    margin-top:4px;
                ">
                —
                </div>
            </div>
            `;

            // Stat card 2
            const statDivPop = document.createElement('div');
            statDivPop.innerHTML = `
            <div style="
                font-family: Arial, sans-serif;
                padding:16px;
                border-radius:8px;
                background:#f4f6f9;
            ">
                <span
                id="stat2_label_${i}"
                style="
                    font-size:12px;
                    text-transform:uppercase;
                    letter-spacing:0.5px;
                    color:${color};
                    font-weight:bold;
                ">
                Community vs <br>Congressional District
                </span>

                <div
                id="stat2_value_${i}"
                style="
                    font-size:28px;
                    color:${color};
                    margin-top:4px;
                ">
                —
                </div>
            </div>
            `;

            statsContainer.appendChild(statDiv);
            statsContainer.appendChild(statDivPop);

            row.appendChild(statsContainer);
            row.appendChild(chartDiv);

            container.appendChild(row);
        });
        }

    // for making automaticbounds 
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

      // distribute leftover icons to the entries with the largest fractional remainder
      const order = exact
        .map((v, i) => ({ i, frac: v - Math.floor(v) }))
        .sort((a, b) => b.frac - a.frac);

      const result = [...floored];
      for (let k = 0; k < remainder; k++) {
        result[order[k % order.length].i] += 1;
      }
      return result;
    }

    // builds ONE combined 10x10 (100-icon) waffle chart showing the full
    // age-bracket composition of the Congressional Community, with every
    // bracket shown in its own true color at once (mirrors make_full_chart_cc).
    function renderFullWaffle(ageBrackets) {
      const d = allData[currentCcn20];

      const rawCounts = ageBrackets.map(label => d.cc[label]);
      const iconCounts = allocateIcons(rawCounts, 100);

      // build a flat array of 100 color assignments, grouped by bracket,
      // in "NW" (row-major, top-left start) order to match the grid
      const cellColors = [];
      iconCounts.forEach((count, idx) => {
        const color = okabeItoColors[idx % okabeItoColors.length];
        for (let c = 0; c < count; c++) cellColors.push(color);
      });
      // in case rounding leaves us short (shouldn't happen with allocateIcons, but be safe)
      while (cellColors.length < 100) cellColors.push(waffleNotUsedColor);

      const grid = document.getElementById('waffleFull');
      grid.innerHTML = '';
      cellColors.forEach(color => {
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-user';
        icon.style.color = color;
        grid.appendChild(icon);
      });

      renderWaffleLegend(ageBrackets);
    }

    function renderWaffleLegend(ageBrackets) {
      const legend = document.getElementById('waffleLegend');
      legend.innerHTML = '';
      ageBrackets.forEach((label, i) => {
        const item = document.createElement('div');
        item.className = 'waffle-legend-item';
        item.innerHTML = `
          <span class="waffle-legend-swatch" style="background:${okabeItoColors[i % okabeItoColors.length]}"></span>
          ${age_bracket_names[i] || label}
        `;
        legend.appendChild(item);
      });
    }

    // renders one chart + updates its matching stat card
    function renderChart(divId, ageLabel, ageIndex) {
      const d = allData[currentCcn20];

      const notUsed = lighterItoColors[ageIndex];
      const colorUsed = okabeItoColors[ageIndex];

      const xCc = d.cc[ageLabel] / d.cc_total;
      const xCd = d.cd[ageLabel] / d.cd_total;
      const xState = d.state[ageLabel] / d.state_total;

      const diff_cc_cd = xCc - xCd;
      const diff_cc_state = xCc - xState;

      // --- update the stat card for this age bracket ---
      // swap this for whatever number you actually want displayed
      // (e.g. raw count d.cc[ageLabel], or a percentage like (xCc*100).toFixed(1) + '%')
      const statValue = d.cc[ageLabel];
      document.getElementById(`stat_value_${ageIndex}`).textContent =
        statValue.toLocaleString();

      const statValue2 = (diff_cc_cd.toFixed(2) + '%');
      document.getElementById(`stat2_value_${ageIndex}`).textContent =
        statValue2.toLocaleString();

      const intervals = [];
      for (let i = 0; i <= 20; i++) intervals.push(Math.round((i / 20) * 100) / 100);

      

      const traces = [
        { // legend
          x: [null], y: [null], type: 'scatter', mode: 'markers',
          marker: { symbol: 'diamond', size: 20, color: greyscale_color[0], line: { color: 'white', width: 2 }},
          name: 'State', showlegend: ageIndex === 0
        },
        { // legend
          x: [null], y: [null], type: 'scatter', mode: 'markers',
          marker: { symbol: 'circle', size: 20, color: greyscale_color[0], line: { color: 'white', width: 2 }},
          name: 'Congressional District', showlegend: ageIndex === 0
        },
        { // legend
          x: [null], y: [null], type: 'scatter', mode: 'markers',
          marker: { symbol: 'circle', size: 20, color: greyscale_color[1], line: { color: 'white', width: 2 }},
          name: 'Congressional Community', showlegend: ageIndex === 0
        },
        { // tick marrks
          x: intervals,
          y: intervals.map(() => 1),
          mode: 'lines+markers',
          marker: { symbol: 'line-ns', size: 10, color: 'lightgrey', line: { width: 2, color: 'lightgrey' } },
          opacity: 0.5,
          hoverinfo: 'skip',
          showlegend: false
        },
        {
          x: [xState], y: [1],
          mode: 'markers',
          marker: { symbol: 'diamond', size: 20, color: notUsed, line: { color: 'white', width: 2 } },
          name: 'State', showlegend: false,
          hovertemplate: `State: ${(xState * 100).toFixed(1)}%<extra></extra>`
        },
        {
          x: [xCd], y: [1],
          mode: 'markers',
          marker: { symbol: 'circle', size: 20, color: notUsed, line: { color: 'white', width: 2 } },
          name: 'Congressional District', showlegend: false,
          hovertemplate: `Congressional District: ${(xCd * 100).toFixed(1)}%<extra></extra>`
        },
        {
          x: [xCc], y: [1],
          mode: 'markers',
          marker: { symbol: 'circle', size: 20, color: colorUsed, line: { color: 'white', width: 2 } },
          name: 'Congressional Community', showlegend: false,
          hovertemplate: `Congressional Community: ${(xCc * 100).toFixed(1)}%<extra></extra>`
        }
      ];

      const xMin = floorToDecimals(Math.min(xCc, xCd, xState), 1);
      const xMax = ceilToDecimals(Math.max(xCc, xCd, xState), 1);

      const layout = {
        title: { text: 'Group: ' + age_bracket_names[ageIndex], font: { size: 13, color: 'darkgrey' }, x: 0.01, xanchor: 'left', yanchor: 'top', y: 0.7 },
        xaxis: {
          range: [xMin, xMax],
          tickmode: 'array',
          tickvals: intervals,
          ticktext: intervals.map(v => `${Math.round(v * 100)}%`),
          showgrid: false,
          zeroline: false,
          color: 'lightgrey'
        },
        yaxis: { visible: false, range: [0.9, 1.1] },
        legend: ageIndex === 0
          ? { orientation: 'h', yanchor: 'bottom', y: 1.3, xanchor: 'center', x: 0.5 }
          : {},
        height: 180,
        width: 900,
        margin: { l: 20, r: 20, t: ageIndex === 0 ? 60 : 30, b: 30 },
        plot_bgcolor: 'white'
      };

      Plotly.newPlot(divId, traces, layout, { displayModeBar: false, responsive: true });
    }

    function renderAllCharts() {
      const ageBrackets = allData[currentCcn20].age_brackets;
      ageBrackets.forEach((label, i) => {
        renderChart(`chart_${i}`, label, i);
      });
    }

    function updateUrl() {
      const url = new URL(window.location);
      url.searchParams.set('ccn20', currentCcn20);
      window.history.replaceState({}, '', url);
    }
  </script>

</body>
</html>
