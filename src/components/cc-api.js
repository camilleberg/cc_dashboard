import {CC_PROXY} from "./config.js";

export class CCError extends Error {
  constructor(message, {status = 0, code = null} = {}) {
    super(message);
    this.name = "CCError";
    this.status = status;
    this.code = code;
  }
}

function friendlyMessage(status, body) {
  const code = body?.detail?.code;
  if (status === 429 && code === "anon_zip_search_limit")
    return "We've reached today's limit for new ZIP code and town searches. " +
           "Places searched earlier today still work, and you can search by community or district name instead.";
  if (status === 429) return "Too many requests. Please try again later.";
  if (status === 404) return typeof body?.detail === "string"
    ? `${body.detail}. Some ZIP codes (for example PO-box-only ZIPs) aren't in our data.`
    : "We couldn't find that place.";
  if (status === 400) return "That doesn't look like a valid ZIP code or town.";
  if (status === 503) return "Town search is temporarily unavailable. Try a ZIP code instead.";
  if (status === 502) return "The search service is having trouble. Please try again later.";
  return "Something went wrong. Please try again.";
}

async function call(path, {signal, method = "GET", body} = {}) {
  let res;
  try {
    res = await fetch(`${CC_PROXY}${path}`, {
      method,
      signal,
      // Only send Content-Type on POST so GETs avoid a CORS preflight
      ...(body && {headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)})
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new CCError("Couldn't reach the search service.", {code: "network"});
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new CCError(friendlyMessage(res.status, data), {status: res.status, code: data?.detail?.code});
  return data;
}

/** Town suggestions while typing. Mirrors the docs: >=2 chars, never digits-only. */
export async function suggestTowns(text, {signal} = {}) {
  const q = text.trim();
  if (q.length < 2 || /^\d+$/.test(q)) return [];
  return (await call(`/places?q=${encodeURIComponent(q)}`, {signal})).places ?? [];
}

const lookupCache = new Map();

/**
 * selection: {kind: "ZIP", zip} or {kind: "Town", geoid}
 * geometry:  false (default) = lists only; true = include outlines for the map
 */
export async function findCommunities(selection, {signal, geometry = false} = {}) {
  const isZip = selection.kind === "ZIP";
  const id = isZip ? selection.zip : selection.geoid;
  const fullKey = `${selection.kind}:${id}:geo`;
  const slimKey = `${selection.kind}:${id}`;

  // A full response satisfies a slim request too
  const hit = lookupCache.get(fullKey) ?? (!geometry ? lookupCache.get(slimKey) : null);
  if (hit) return hit;

  const data = await call(`/lookup${geometry ? "?geometry=1" : ""}`, {
    signal,
    method: "POST",
    body: isZip ? {zip: id} : {geoid: id}
  });
  const result = {...data, communities: data.communities ?? []};   // empty list = "no results", not an error
  lookupCache.set(geometry ? fullKey : slimKey, result);
  return result;
}

const membersCache = new Map();

/** Representative + senators for a community ({stabcd: "CA49"}) */
export async function membersFor(community, {signal} = {}) {
  const key = community.stabcd;
  if (!membersCache.has(key))
    membersCache.set(key, await call(`/members?stabcd=${encodeURIComponent(key)}`, {signal}));
  return membersCache.get(key);
}

/** "CA-49", "CA49", "ca 5" -> {stabcd: "CA05", district: "CA-05"}; at-large uses 00. Adjust to your data. */
export function toStabcd(text) {
  const m = String(text ?? "").trim().match(/^([A-Za-z]{2})[-\s]?(\d{1,2})$/);
  if (!m) return null;
  const st = m[1].toUpperCase(), num = m[2].padStart(2, "0");
  return {stabcd: `${st}${num}`, district: `${st}-${num}`};
}