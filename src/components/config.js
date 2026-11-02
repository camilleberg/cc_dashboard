const isLocal = ["localhost", "127.0.0.1"].includes(globalThis.location?.hostname);
export const CC_PROXY = isLocal
  ? "http://127.0.0.1:8787"                       // wrangler dev
  : "https://cc-proxy.<your-subdomain>.workers.dev";