---
title: Comparisons
sql:
  cc_data_updated: ./data/cc_data_updated.parquet
  cc_data_all:  ./data/cc_tables/all/cc_data_all.parquet
  flights: data/flights-200k.parquet
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



This I think will be where I will develop visualizations for comparing across two congressional communtiies. 

## Density Hexbins

The histograms above provide a useful first-look at the data. However, to discover relations among the data we had to interactively explore. Instead of "hiding" patterns behind interactions, let's visualize relationships directly.

Below we use hexagonal bins to visualize the density (number of flights) by both time of day and arrival delay. Interactive histograms along the edges show marginal distributions for both.

```sql
SELECT * FROM cc_data_updated LIMIT 2
```


```sql
SELECT * FROM cc_data_all LIMIT 2
```


```sql
SELECT * FROM flights LIMIT 2
```

```js
const $query = vg.Selection.intersect(); // interval ranges
```

```js 
const $var1 =  vg.Param.value("age_prop_under18");
const $var2 = vg.Param.value("housing_rental_rate");
```

```js
$var1.value
```

# comparison

```js
vg.vconcat(
  vg.hconcat(
    vg.menu({ label: "Variable one", as: $var1, options: ["age_prop_under18", "age_prop_18_65", "age_prop_over65"] })
  ), 
  vg.hconcat(
    vg.plot(
      vg.rectY(
        vg.from("cc_data_all"),
        { x: vg.bin($var1.value), y: vg.count(), fill: "steelblue", inset: 0.5 }
      ),
      vg.intervalX({ as: $query }),
      vg.margins({"left":5,"right":5,"top":30,"bottom":0}),
      vg.xDomain(vg.Fixed),
      vg.xAxis("top"),
      vg.yAxis(null),
      vg.xLabelAnchor("center"),
      vg.xLabel("Proportion of Population Under 18"+ $var1.value),
      vg.width(605),
      vg.height(70)
    ), 
    vg.hspace(80)
  ), 
  vg.hconcat(
    vg.plot(
      vg.hexbin(
        vg.from("cc_data_all", { filterBy: $query }),
        { x: "age_prop_under18", y: "tot_rented_hholds", fill: vg.count(), binWidth: 10 }
      ),
      vg.hexgrid({ binWidth: 10 }),
      vg.name("hexbins"),
      vg.colorScheme("ylgnbu"),
      vg.colorScale('linear'),
      vg.margins({"left":5,"right":0,"top":0,"bottom":5}),
      vg.xAxis(null),
      vg.yAxis(null),
      vg.xyDomain(vg.Fixed),
      vg.width(600),
      vg.height(455)
    ),
    vg.plot(
      vg.rectX(
        vg.from("cc_data_all"),
        { x: vg.count(), y: vg.bin("tot_rented_hholds"), fill: "steelblue", inset: 0.5 }
      ),
      vg.intervalY({ as: $query }),
      vg.margins({"left":0,"right":50,"top":4,"bottom":5}),
      vg.yDomain([0,100000]), // change to max 
      vg.xAxis(null),
      vg.yAxis("right"),
      vg.yLabelAnchor("center"),
      vg.yLabel("Total Rentes Households"),
      vg.width(80),
      vg.height(455)
    )
  )
)

```
