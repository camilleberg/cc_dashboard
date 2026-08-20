---
title: Map Trial
---

# Trial to load map in mosaic

+ reference:

https://observablehq.com/framework/lib/mosaic

```js
import * as L from "npm:leaflet";
import * as topojson from "npm:topojson-client";
```

```html
<link rel="stylesheet" href="npm:leaflet/dist/leaflet.css">
```

```js
const div = display(document.createElement("div"));
div.style = "height: 400px;";

const map = L.map(div)
  .setView([51.505, -0.09], 13);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
})
  .addTo(map);

L.marker([51.5, -0.09])
  .addTo(map)
  .bindPopup("A nice popup<br> indicating a point of interest.")
  .openPopup();
```

```js
const us = await FileAttachment("./data/us-counties-10m.json").json();
const states = topojson.feature(us, us.objects.states);
```

```js
Plot.plot({ // Initialize the plot
  projection: "albers-usa", // Set the projection
  marks: [
    Plot.geo(states) // Add the state boundaries
    // Plot.dot(us_power_plants, { // Create dot marks (bubbles) using data from power_plants
    //   x: "longitude", // Provide longitude values
    //   y: "latitude", // Provide latitude values
    //   r: "Total_MW" // Update bubble radius based on this variable's value
    // })
  ],
  height: 500, // Update canvas height
  width: 800, // Update canvas width
  margin: 50 // Update margins
})
```