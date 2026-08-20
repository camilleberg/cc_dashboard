---
title: Example Map
---

# U.S. Counties


```js
const loaded = await vg.coordinator().exec([
  vg.loadExtension("spatial"),
  vg.loadSpatial("counties", "./data/us-counties-10m.json", {layer: "counties"}),
  vg.loadSpatial("states", "./data/us-counties-10m.json", {layer: "states"})
]);
```

```js
// Referencing `loaded` here (even though we don't use its value) gives
// Framework an explicit dependency edge, so this cell is guaranteed to
// run only after the load above finishes — rather than racing it.
loaded;

vg.plot(
  vg.geo(
    vg.from("counties"),
    {stroke: "currentColor", strokeWidth: 0.25}
  ),
  vg.geo(
    vg.from("states"),
    {stroke: "currentColor", strokeWidth: 1}
  ),
  vg.dot(
    vg.from("counties"),
    {
      x: vg.centroidX("geom"),
      y: vg.centroidY("geom"),
      r: 2,
      fill: "transparent",
      tip: true,
      title: "name"
    }
  ),
  vg.margin(0),
  vg.projectionType("albers")
)
```