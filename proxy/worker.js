// proxy/worker.js
const UPSTREAM = "https://api.congressionalcommunities.org";
const ALLOWED_ORIGINS = [
  "https://your-framework-site.example",
  "http://127.0.0.1:3000",
  "http://localhost:3000"
];
const TTL = { lookup: 60 * 60 * 24 * 30, members: 60 * 60 * 24 };

const corsHeaders = (origin) => ({
  ...(origin && {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  }),
  Vary: "Origin"
});

const json = (data, status, origin, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(origin), ...extra }
  });

const upstream = (path, env, init = {}) =>
  fetch(UPSTREAM + path, {
    ...init,
    headers: { "CC-API-Key": env.CC_API_KEY, "Content-Type": "application/json" }
  });

// Never leak upstream auth problems to the browser.
function passthrough(res, body, origin) {
  if (res.status === 401 || res.status === 403)
    return json({ detail: "Search service is misconfigured" }, 502, origin);
  return json(body ?? { detail: `Upstream error (${res.status})` }, res.status, origin);
}

function slim(data) {
  const { zip_boundary, boundary, ...rest } = data;
  return {
    ...rest,
    communities: (data.communities ?? []).map(({ geometry, ...c }) => c)
  };
}

export default {
  async fetch(request, env, ctx) {
    const reqOrigin = request.headers.get("Origin") ?? "";
    const origin = ALLOWED_ORIGINS.includes(reqOrigin) ? reqOrigin : "";
    if (request.method === "OPTIONS")
      return new Response(null, { status: 204, headers: corsHeaders(origin) });

    const url = new URL(request.url);

    try {
      // ---- Town suggestions (not rate-limited upstream) ----
      if (url.pathname === "/places" && request.method === "GET") {
        const q = (url.searchParams.get("q") ?? "").trim();
        if (q.length < 2 || /^\d+$/.test(q)) return json({ places: [] }, 200, origin);
        const res = await upstream(`/place-search?q=${encodeURIComponent(q)}`, env);
        const body = await res.json().catch(() => null);
        if (!res.ok) return passthrough(res, body, origin);
        return json(body, 200, origin, { "Cache-Control": "public, max-age=3600" });
      }

      // ---- ZIP / town lookup (counts toward the daily limit) ----
      if (url.pathname === "/lookup" && request.method === "POST") {
        const body = await request.json().catch(() => ({}));
        let kind, id, path, payload;
        if (/^\d{5}$/.test(body.zip ?? "")) {
          kind = "zip"; id = body.zip; path = "/zip-lookup"; payload = { zip: id };
        } else if (/^\d{7}$/.test(body.geoid ?? "")) {
          kind = "place"; id = body.geoid; path = "/place-lookup"; payload = { geoid: id };
        } else {
          return json({ detail: "Provide a 5-digit zip or a 7-digit geoid" }, 400, origin);
        }

        const cacheKey = `lookup:${kind}:${id}`;
        let data = await env.CC_CACHE.get(cacheKey, "json");
        const fromCache = !!data;

        if (!data) {
          const res = await upstream(path, env, { method: "POST", body: JSON.stringify(payload) });
          const resBody = await res.json().catch(() => null);
          if (!res.ok) return passthrough(res, resBody, origin);
          data = resBody;
          ctx.waitUntil(
            env.CC_CACHE.put(cacheKey, JSON.stringify(data), { expirationTtl: TTL.lookup })
          );
        }

        let out = url.searchParams.get("geometry") === "1" ? data : slim(data);
        if (fromCache) {
          // searches_remaining is stale on a cache hit; don't mislead the UI
          const { searches_remaining, ...rest } = out;
          out = { ...rest, from_cache: true };
        }
        return json(out, 200, origin);
      }

      // ---- Rep + senators in one call (not rate-limited upstream) ----
      if (url.pathname === "/members" && request.method === "GET") {
        const stabcd = (url.searchParams.get("stabcd") ?? "").toUpperCase();
        if (!/^[A-Z]{2}\d{2}$/.test(stabcd))
          return json({ detail: "stabcd must look like CA49" }, 400, origin);

        const cacheKey = `members:${stabcd}`;
        let data = await env.CC_CACHE.get(cacheKey, "json");
        if (!data) {
          const [repRes, senRes] = await Promise.all([
            upstream(`/rep?stabcd=${stabcd}&include=`, env),
            upstream(`/senators?state=${stabcd.slice(0, 2)}&include=`, env)
          ]);
          if (!repRes.ok || !senRes.ok)
            return json({ detail: "Member lookup failed" }, 502, origin);
          data = { rep: await repRes.json(), senators: await senRes.json() };
          ctx.waitUntil(
            env.CC_CACHE.put(cacheKey, JSON.stringify(data), { expirationTtl: TTL.members })
          );
        }
        return json(data, 200, origin);
      }

      return json({ detail: "Not found" }, 404, origin);
    } catch (err) {
      return json({ detail: "Proxy error" }, 500, origin);
    }
  }
};