---
title:  for search verifictation
sql:
  cc_data_all:  ./data/cc_tables/all/cc_data_all.parquet
head: '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tarekraafat/autocomplete.js@10/dist/css/autoComplete.min.css">'
---


```sql
SELECT * FROM cc_data_all LIMIT 3
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

# now to choose result for 

${input}

${result_list
  ? html`<pre>${JSON.stringify(result_list, null, 2)}</pre>`
  : "Enter a town, city, or 5-digit ZIP"}

${result_list?.communities?.[0]?.geoid}



## gettiing geoid
```js


```