const ALLOWED_ORIGINS = [
  "https://camilleberg.github.io",   // origin only: no path
  "http://127.0.0.1:3000",
  "http://localhost:3000"
];

const API_BASE = "https://api.congressionalcommunities.org";

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin"
  };
}

function json(body, status, cors) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json" }
  });
}

async function forward(url, init, cors) {
  let upstream;
  try {
    upstream = await fetch(url, init);
  } catch (err) {
    return json({ error: "Upstream failed", detail: String(err) }, 502, cors);
  }
  return new Response(upstream.body, {
    status: upstream.status,
    headers: { ...cors, "Content-Type": "application/json" }
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") ?? "";
    const cors = corsHeaders(origin);
    const url = new URL(request.url);

    // Browser preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // Check the secret before doing anything else
    if (!env.CC_API_KEY) {
      return json({ error: "CC_API_KEY secret not set" }, 500, cors);
    }

    // ---- GET /place-search?town=laguna%20ni ----
    if (request.method === "GET" && url.pathname === "/place-search") {
      const town = (url.searchParams.get("town") ?? url.searchParams.get("q") ?? "").trim();

      if (town.length < 2 || town.length > 60 || !/^[\p{L}\s.'-]+$/u.test(town)) {
        return json({ error: "town must be 2-60 letters, spaces, . ' or -" }, 400, cors);
      }

      return forward(
        `${API_BASE}/place-search?q=${encodeURIComponent(town)}`,
        { method: "GET", headers: { "CC-API-Key": env.CC_API_KEY } },
        cors
      );
    }

    // ---- POST / (ZIP lookup, body: {"zip": "92677"}) ----
    if (request.method === "POST") {
      let zip;
      try {
        ({ zip } = await request.json());
      } catch {
        return json({ error: "Invalid JSON" }, 400, cors);
      }
      if (typeof zip