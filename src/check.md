---
title:  for search verifictation
sql:
  cc_data_all:  ./data/cc_tables/all/cc_data_all.parquet
  cdp: ./data/input/acs2025_cdp.parquet
  zcta: ./data/input/zcta5.parquet
head: '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tarekraafat/autocomplete.js@10/dist/css/autoComplete.min.css">'
---


```sql
SELECT * FROM cc_data_all LIMIT 3
```

```sql
SELECT * FROM cdp LIMIT 3
```

```sql
SELECT * FROM zcta LIMIT 3
```


# new 
```js
const input = Inputs.text({
  label: "Search",
  placeholder: "e.g. San Jose or ZIP code"
});
const results = Generators.input(input);
```

```js
const query = (results ?? "").trim();
const isZip = /^\d{5}$/.test(query);
const WORKER = "https://cc-proxy.congress-comm-dev.workers.dev";   // match your deployed Worker
```

```js
const result_list = await (async () => {
  if (isZip) {
    const res = await fetch(`${WORKER}/lookup`, {              // adjust path to your Worker
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ zip: query })
    });
    if (!res.ok) return { error: `Lookup failed (${res.status})` };
    return await res.json();
  }

  if (query.length < 2 || /^\d+$/.test(query)) return null;    // too short, or partial ZIP

  const res = await fetch(`${WORKER}/places?q=${encodeURIComponent(query)}`);   // adjust path/param
  if (!res.ok) return { error: `Lookup failed (${res.status})` };
  return await res.json();
})();
```

# now to choose result for the thing 
we have 
${input}

${result_list
  ? html`<pre>${JSON.stringify(result_list, null, 2)}</pre>`
  : "Enter a town, city, or 5-digit ZIP"}

```js
const geoid = isZip
  ? result_list?.communities?.[0]?.geoid
  : result_list?.places?.[0]?.geoid;
```

the geoid is ${geoid}

## to get place 

```js
const placeData = await (async () => {
  const res = await fetch("https://zip-proxy.congress-comm-dev.workers.dev/place-lookup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ geoid })   // e.g. the geoid picked from a place-search result
  });
  if (!res.ok) return { error: `Lookup failed (${res.status})` };
  return await res.json();
})();
```

${placeData ? Object.keys(placeData).join(", ") : "no data yet"}

${placeData?.place?.label}
${placeData?.communities?.map(c => c.custom_id).join(", ")}
${placeData?.searches_remaining}