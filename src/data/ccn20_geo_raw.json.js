// src/data/ccn20_geo_raw.json.js

async function json(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`fetch failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(
      `${data.error.code}: ${data.error.message}`
    );
  }

  return data;
}


// ArcGIS item
const itemId = "732bb26310fe460f86db3b4fc15b58d1";

// Get item metadata
const item = await json(
  `https://cc2020.maps.arcgis.com/sharing/rest/content/items/${itemId}?f=json`
);

console.log("ITEM:");
console.log(item);

console.log("SERVICE URL:");
console.log(item.url);