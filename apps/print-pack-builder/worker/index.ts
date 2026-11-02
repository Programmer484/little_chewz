/**
 * Print Pack Builder API. Static assets (the React app) are served by
 * Cloudflare; only /api/* reaches this Worker (see wrangler.jsonc).
 *
 *   GET /api/health                 mode and configuration flags (no secrets)
 *   GET /api/lessons                sanitized lessons, no Drive IDs
 *   GET /api/resources/:resourceId  bytes of one published student worksheet
 */
import { LIMITS } from "../shared/limits.ts";
import type { LessonsResponse } from "../shared/types.ts";
import { verifyAccess } from "./access.ts";
import { base64Decode } from "./b64.ts";
import { type Catalog, parseMode } from "./catalog.ts";
import { catalog as defaultCatalog } from "./data.ts";
import { FIXTURES } from "./demo/fixtures.generated.ts";
import { placeholderPdf } from "./demo/placeholder.ts";
import type { Env } from "./env.ts";
import { ResourceError, fetchDriveFile, parseServiceAccount } from "./google.ts";

const RESOURCE_ID = /^[a-z0-9][a-z0-9-]{0,119}$/;
const SECURITY_HEADERS = { "x-content-type-options": "nosniff", "cache-control": "private, no-store" };

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...SECURITY_HEADERS },
  });
}

const error = (status: number, message: string) => json({ error: message }, status);

const isLocal = (url: URL) => url.hostname === "localhost" || url.hostname === "127.0.0.1";

export const accessRequired = (env: Env) => env.REQUIRE_ACCESS?.trim().toLowerCase() !== "false";

/** Null when real Drive files may be served for this request; otherwise the refusal. */
async function driveGate(request: Request, env: Env, fetcher: typeof fetch): Promise<Response | null> {
  const url = new URL(request.url);
  // No login: only published student worksheets are ever served, and those are public on Drive.
  if (!accessRequired(env)) return null;
  const teamDomain = env.ACCESS_TEAM_DOMAIN?.trim();
  const aud = env.ACCESS_AUD?.trim();
  if (!teamDomain || !aud) {
    if (env.LOCAL_DRIVE_TESTING === "true" && isLocal(url)) return null;
    return error(503, "Private pilot access is not configured, so real worksheet downloads are switched off.");
  }
  const reason = await verifyAccess(request, { teamDomain, aud }, fetcher);
  return reason ? error(403, "Sign in through the pilot access page to download worksheets.") : null;
}

export async function handleResource(
  request: Request,
  env: Env,
  id: string,
  catalog: Catalog,
  fetcher: typeof fetch,
): Promise<Response> {
  if (!RESOURCE_ID.test(id)) return error(400, "Invalid resource ID.");
  const mode = parseMode(env.RESOURCE_MODE);
  if (mode === "disabled") return error(503, "Worksheet downloads are not switched on for this site yet.");
  const served = catalog.lookup(id, mode);
  if (!served) return error(404, "This resource is not available for download.");
  if (served.source.kind === "demo-fixture") {
    const fixture = FIXTURES[served.source.fixture];
    if (!fixture) return error(500, "Demo file is missing.");
    const bytes = base64Decode(fixture);
    return new Response(bytes, {
      headers: { ...SECURITY_HEADERS, "content-type": served.source.mimeType, "content-length": String(bytes.length) },
    });
  }
  if (served.source.kind === "demo-placeholder") {
    const bytes = await placeholderPdf(served.title, 1);
    return new Response(bytes as Uint8Array<ArrayBuffer>, {
      headers: { ...SECURITY_HEADERS, "content-type": "application/pdf", "content-length": String(bytes.length) },
    });
  }

  const refusal = await driveGate(request, env, fetcher);
  if (refusal) return refusal;
  const sa = parseServiceAccount(env.GOOGLE_SERVICE_ACCOUNT_JSON);
  if (!sa) return error(503, "Google Drive credentials are not configured on the server.");
  try {
    const file = await fetchDriveFile(sa, served.source.fileId, fetcher);
    const headers: Record<string, string> = { ...SECURITY_HEADERS, "content-type": file.mimeType };
    if (file.size !== null) headers["content-length"] = String(file.size);
    return new Response(file.body, { headers });
  } catch (e) {
    if (e instanceof ResourceError) return error(e.status, `Could not retrieve “${served.title}”: ${e.message}`);
    console.error("resource fetch failed", id, e);
    return error(502, `Could not retrieve “${served.title}”.`);
  }
}

export async function handleRequest(
  request: Request,
  env: Env,
  catalog: Catalog = defaultCatalog,
  fetcher: typeof fetch = fetch,
): Promise<Response> {
  const url = new URL(request.url);
  if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);
  if (request.method !== "GET" && request.method !== "HEAD") return error(405, "Method not allowed.");
  const mode = parseMode(env.RESOURCE_MODE);

  if (url.pathname === "/api/health")
    return json({
      mode,
      accessRequired: accessRequired(env),
      accessConfigured: Boolean(env.ACCESS_TEAM_DOMAIN?.trim() && env.ACCESS_AUD?.trim()),
      driveConfigured: parseServiceAccount(env.GOOGLE_SERVICE_ACCOUNT_JSON) !== null,
      limits: LIMITS,
    });
  if (url.pathname === "/api/lessons") return json({ mode, lessons: catalog.lessons(mode) } satisfies LessonsResponse);
  const match = /^\/api\/resources\/([^/]+)$/.exec(url.pathname);
  if (match) {
    let id: string;
    try {
      id = decodeURIComponent(match[1]);
    } catch {
      return error(400, "Invalid resource ID.");
    }
    return handleResource(request, env, id, catalog, fetcher);
  }
  return error(404, "Not found.");
}

export default {
  fetch: (request, env) => handleRequest(request, env),
} satisfies ExportedHandler<Env>;
