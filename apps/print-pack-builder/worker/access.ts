/**
 * Cloudflare Access check. Access sits in front of the whole site and adds a
 * signed JWT (Cf-Access-Jwt-Assertion) to every request it lets through. The
 * Worker re-verifies it before serving any real worksheet, so a misrouted or
 * unprotected hostname still cannot download private files.
 */
import { base64Decode } from "./b64.ts";

export interface AccessConfig {
  teamDomain: string; // e.g. "littlechewz.cloudflareaccess.com"
  aud: string;
}

interface Jwk extends JsonWebKey {
  kid?: string;
}

const JWKS_TTL_MS = 60 * 60 * 1000;
let jwksCache: { domain: string; keys: Jwk[]; at: number } | null = null;

export function resetAccessCache() {
  jwksCache = null;
}

async function keysFor(domain: string, fetcher: typeof fetch): Promise<Jwk[]> {
  if (jwksCache && jwksCache.domain === domain && Date.now() - jwksCache.at < JWKS_TTL_MS) return jwksCache.keys;
  const res = await fetcher(`https://${domain}/cdn-cgi/access/certs`);
  if (!res.ok) throw new Error(`Access certs request failed (${res.status})`);
  const body = (await res.json()) as { keys?: Jwk[] };
  jwksCache = { domain, keys: body.keys ?? [], at: Date.now() };
  return jwksCache.keys;
}

const json = (part: string) => JSON.parse(new TextDecoder().decode(base64Decode(part)));

/** Returns null when the request carries a valid Access token, otherwise the reason. */
export async function verifyAccess(
  request: Request,
  config: AccessConfig,
  fetcher: typeof fetch = fetch,
  now = Date.now(),
): Promise<string | null> {
  const token = request.headers.get("Cf-Access-Jwt-Assertion");
  if (!token) return "missing Access token";
  const parts = token.split(".");
  if (parts.length !== 3) return "malformed Access token";
  let header: { alg?: string; kid?: string };
  let claims: { aud?: string | string[]; exp?: number; nbf?: number; iss?: string };
  try {
    header = json(parts[0]);
    claims = json(parts[1]);
  } catch {
    return "malformed Access token";
  }
  if (header.alg !== "RS256") return "unexpected token algorithm";
  const keys = await keysFor(config.teamDomain, fetcher);
  const jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) return "unknown signing key";
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const valid = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5",
    key,
    base64Decode(parts[2]),
    new TextEncoder().encode(`${parts[0]}.${parts[1]}`),
  );
  if (!valid) return "invalid token signature";
  const seconds = Math.floor(now / 1000);
  if (typeof claims.exp !== "number" || claims.exp <= seconds) return "token expired";
  if (typeof claims.nbf === "number" && claims.nbf > seconds + 60) return "token not yet valid";
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!aud.includes(config.aud)) return "token audience mismatch";
  if (claims.iss !== `https://${config.teamDomain}`) return "token issuer mismatch";
  return null;
}
