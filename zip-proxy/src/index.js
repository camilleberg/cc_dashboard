const ALLOWED_ORIGINS = [
  "https://camilleberg.github.io",   // origin only, no path
  "http://127.0.0.1:3000",
  "http://127.0.0.1:3001",
  "http://localhost:3000",
  "http://localhost:3001"
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

async function readBody(request, cors) {
  try {
    return { body: await request.json() };
  } catch {
    return { error: json({ error: "Invalid JSON" }, 400, cors) };
  }
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") ?? "";
    const cors = corsHeaders(origin);
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    if (!env.CC_API_KEY) {
      return json({ error: "CC_API_KEY secret not set" }, 500, cors);
    }

    const authHeaders = { "CC-API-Key": env.CC_API_KEY };

    // ---- GET /place-search?town=laguna%20ni ----
    if (request.method === "GET" && path === "/place-search") {
      const town = (url.searchParams.get("town") ?? url.searchParams.get("q") ?? "").trim();
      if (town.length < 2 || town.length > 60 || !/^[\p{L}\s.'-]+$/u.test(town)) {
        return json({ error: "town must be 2-60 letters, spaces, . ' or -" }, 400, cors);
      }
      return forward(
        `${API_BASE}/place-search?q=${encodeURIComponent(town)}`,
        { method: "GET", headers: authHeaders },
        cors
      );
    }

    // ---- POST /place-lookup  body: {"geoid": "0639248"} ----
    if (request.method === "POST" && path === "/place-lookup") {
      const { body, error } = await readBody(request, cors);
      if (error) return error;

      const geoid = body?.geoid;
      if (typeof geoid !== "string" || !/^\d{7}$/.test(geoid)) {
        return json({ error: "geoid must be a 7-digit string, e.g. 0639248" }, 400, cors);
      }
      return forward(
        `${API_BASE}/place-lookup`,
        {
          method: "POST",
          headers: { ...authHeaders, "Content-Type": "application/json" },
          body: JSON.stringify({ geoid })
        },
        cors
      );
    }

    // ---- POST / or /zip-lookup  body: {"zip": "92677"} ----
    if (request.method === "POST" && (path === "/" || path === "/zip-lookup")) {
      const { body, error } = await readBody(request, cors);
      if (error) return error;

      const zip = body?.zip;
      if (typeof zip !== "string" || !/^\d{5}$/.test(zip)) {
        return json({ error: "ZIP must be 5 digits" }, 400, cors);
      }
      return forward(
        `${API_BASE}/zip-lookup`,
        {
          method: "POST",
          headers: { ...authHeaders, "Content-Type": "application/json" },
          body: JSON.stringify({ zip })
        },
        cors
      );
    }

    return json({ error: "Not found or method not allowed" }, 404, cors);
  }
};