import { beforeEach, describe, expect, it } from "vitest";
import { resetAccessCache } from "../worker/access.ts";
import { base64UrlEncode } from "../worker/b64.ts";
import { resetTokenCache } from "../worker/google.ts";
import { handleRequest } from "../worker/index.ts";
import { env, fixture } from "./helpers.ts";

const TEAM = "littlechewz.cloudflareaccess.com";
const AUD = "test-aud";
const REAL = "ccc-q01-secret-ingredients-chapter-notes";
const REAL_FILE = "107xSYGXDG-46-bQA652m7HOhFR1CVb17";

const get = (path: string, headers: Record<string, string> = {}, host = "https://pack.example.workers.dev") =>
  new Request(`${host}${path}`, { headers });

async function rsaKeys(kid: string) {
  const pair = (await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true,
    ["sign", "verify"],
  )) as CryptoKeyPair;
  const jwk = { ...((await crypto.subtle.exportKey("jwk", pair.publicKey)) as JsonWebKey), kid };
  const pkcs8 = new Uint8Array((await crypto.subtle.exportKey("pkcs8", pair.privateKey)) as ArrayBuffer);
  const pem = `-----BEGIN PRIVATE KEY-----\n${btoa(String.fromCharCode(...pkcs8))}\n-----END PRIVATE KEY-----\n`;
  return { pair, jwk, pem };
}

async function signJwt(key: CryptoKey, kid: string, claims: Record<string, unknown>) {
  const head = base64UrlEncode(JSON.stringify({ alg: "RS256", kid, typ: "JWT" }));
  const body = base64UrlEncode(JSON.stringify(claims));
  const sig = new Uint8Array(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(`${head}.${body}`)));
  return `${head}.${body}.${base64UrlEncode(sig)}`;
}

describe("worker API", () => {
  beforeEach(() => {
    resetAccessCache();
    resetTokenCache();
  });

  it("lists lessons without Drive IDs or URLs", async () => {
    for (const mode of ["disabled", "demo", "drive"]) {
      const res = await handleRequest(get("/api/lessons"), env({ RESOURCE_MODE: mode }));
      const text = await res.text();
      expect(res.status).toBe(200);
      expect(text).not.toMatch(/drive\.google|docs\.google|file\/d\/|1cRfJWiGJJ|107xSYGXDG/);
    }
  });

  it("refuses downloads when the site is not switched on", async () => {
    const res = await handleRequest(get(`/api/resources/${REAL}`), env());
    expect(res.status).toBe(503);
  });

  it("rejects malformed, unknown and unapproved resource IDs", async () => {
    const e = env({ RESOURCE_MODE: "demo" });
    expect((await handleRequest(get("/api/resources/..%2Fsecret"), e)).status).toBe(400);
    expect((await handleRequest(get("/api/resources/%E0%A4%A"), e)).status).toBe(400);
    expect((await handleRequest(get("/api/resources/Not_Valid"), e)).status).toBe(400);
    expect((await handleRequest(get("/api/resources/no-such-thing"), e)).status).toBe(404);
    // Another student worksheet in a guide that is still marked unpublished.
    expect((await handleRequest(get("/api/resources/ccc-q01-set-the-table-school-song-activity"), e)).status).toBe(404);
    // A teacher-only resource that is published but not a student printable.
    expect((await handleRequest(get("/api/resources/ccc-q01-secret-ingredients-teacher-guide"), e)).status).toBe(404);
    // Object prototype keys are not resources.
    expect((await handleRequest(get("/api/resources/constructor"), e)).status).toBe(404);
  });

  it("only allows GET", async () => {
    const res = await handleRequest(new Request("https://x.dev/api/lessons", { method: "POST" }), env());
    expect(res.status).toBe(405);
  });

  it("serves synthetic fixtures and placeholders in demo mode", async () => {
    const e = env({ RESOURCE_MODE: "demo" });
    const png = await handleRequest(get("/api/resources/demo-station-poster"), e);
    expect(png.headers.get("content-type")).toBe("image/png");
    expect(new Uint8Array(await png.arrayBuffer())).toEqual(fixture("station-poster.png"));
    const placeholder = await handleRequest(get(`/api/resources/${REAL}`), e);
    expect(placeholder.status).toBe(200);
    expect(placeholder.headers.get("content-type")).toBe("application/pdf");
    const bytes = new Uint8Array(await placeholder.arrayBuffer());
    expect(new TextDecoder().decode(bytes.slice(0, 5))).toBe("%PDF-");
    // Demo fixtures are not served outside demo mode.
    expect((await handleRequest(get("/api/resources/demo-station-poster"), env({ RESOURCE_MODE: "drive", ACCESS_TEAM_DOMAIN: TEAM, ACCESS_AUD: AUD }))).status).toBe(404);
  });

  describe("drive mode", () => {
    it("keeps real files off when Access is not configured", async () => {
      const res = await handleRequest(get(`/api/resources/${REAL}`), env({ RESOURCE_MODE: "drive", GOOGLE_SERVICE_ACCOUNT_JSON: "{}" }));
      expect(res.status).toBe(503);
      expect(await res.text()).toMatch(/Private pilot access is not configured/);
    });

    it("allows local testing without Access only on localhost with the flag", async () => {
      const e = env({ RESOURCE_MODE: "drive", LOCAL_DRIVE_TESTING: "true" });
      const remote = await handleRequest(get(`/api/resources/${REAL}`), e);
      expect(remote.status).toBe(503);
      const local = await handleRequest(get(`/api/resources/${REAL}`, {}, "http://localhost:5173"), e);
      expect(local.status).toBe(503);
      expect(await local.text()).toMatch(/credentials are not configured/);
    });

    it("serves published files without a login when REQUIRE_ACCESS is false", async () => {
      const google = await rsaKeys("g2");
      const pdf = fixture("reading-log.pdf");
      const fetcher = (async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("oauth2")) return Response.json({ access_token: "tok", expires_in: 3600 });
        if (url.includes("cloudflareaccess")) throw new Error("Access must not be consulted");
        return url.includes("alt=media") ? new Response(pdf) : Response.json({ mimeType: "application/pdf" });
      }) as typeof fetch;
      const sa = JSON.stringify({ client_email: "r@x.iam.gserviceaccount.com", private_key: google.pem });
      const e = env({ RESOURCE_MODE: "drive", REQUIRE_ACCESS: "false", GOOGLE_SERVICE_ACCOUNT_JSON: sa });
      const res = await handleRequest(get(`/api/resources/${REAL}`), e, undefined, fetcher);
      expect(res.status).toBe(200);
      expect(new Uint8Array(await res.arrayBuffer())).toEqual(pdf);
      const health = await (await handleRequest(get("/api/health"), e)).json();
      expect(health).toMatchObject({ accessRequired: false });
      // Unpublished worksheets and non-worksheets are still refused.
      expect((await handleRequest(get("/api/resources/ccc-q01-set-the-table-school-song-activity"), e, undefined, fetcher)).status).toBe(404);
      expect((await handleRequest(get("/api/resources/ccc-q01-secret-ingredients-teacher-guide"), e, undefined, fetcher)).status).toBe(404);
    });

    it("verifies the Access token when a login is required, then fetches the Drive file", async () => {
      const access = await rsaKeys("k1");
      const google = await rsaKeys("g1");
      const now = Math.floor(Date.now() / 1000);
      const pdf = fixture("reading-log.pdf");
      const calls: string[] = [];
      const fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        calls.push(url);
        if (url === `https://${TEAM}/cdn-cgi/access/certs`) return Response.json({ keys: [access.jwk] });
        if (url === "https://oauth2.googleapis.com/token") {
          expect(String(init?.body)).toContain("jwt-bearer");
          return Response.json({ access_token: "tok", expires_in: 3600 });
        }
        expect((init?.headers as Record<string, string>).authorization).toBe("Bearer tok");
        if (url.includes("alt=media")) return new Response(pdf);
        return Response.json({ id: REAL_FILE, mimeType: "application/pdf", size: String(pdf.length) });
      }) as typeof fetch;
      const sa = JSON.stringify({ client_email: "reader@x.iam.gserviceaccount.com", private_key: google.pem });
      const e = env({ RESOURCE_MODE: "drive", ACCESS_TEAM_DOMAIN: TEAM, ACCESS_AUD: AUD, GOOGLE_SERVICE_ACCOUNT_JSON: sa });
      const call = (headers: Record<string, string>) => handleRequest(get(`/api/resources/${REAL}`, headers), e, undefined, fetcher);

      expect((await call({})).status).toBe(403);
      const wrongAud = await signJwt(access.pair.privateKey, "k1", { aud: ["other"], exp: now + 60, iss: `https://${TEAM}` });
      expect((await call({ "Cf-Access-Jwt-Assertion": wrongAud })).status).toBe(403);
      const expired = await signJwt(access.pair.privateKey, "k1", { aud: [AUD], exp: now - 10, iss: `https://${TEAM}` });
      expect((await call({ "Cf-Access-Jwt-Assertion": expired })).status).toBe(403);
      const forged = await signJwt(google.pair.privateKey, "k1", { aud: [AUD], exp: now + 60, iss: `https://${TEAM}` });
      expect((await call({ "Cf-Access-Jwt-Assertion": forged })).status).toBe(403);

      const good = await signJwt(access.pair.privateKey, "k1", { aud: [AUD], exp: now + 60, iss: `https://${TEAM}` });
      const res = await call({ "Cf-Access-Jwt-Assertion": good });
      expect(res.status).toBe(200);
      expect(res.headers.get("content-type")).toBe("application/pdf");
      expect(new Uint8Array(await res.arrayBuffer())).toEqual(pdf);
      expect(calls.some((c) => c.includes(`/files/${REAL_FILE}?alt=media`))).toBe(true);
    });
  });
});

describe("drive retrieval failures", () => {
  beforeEach(() => resetTokenCache());

  async function driveCall(meta: () => Response, media: () => Response = () => new Response(fixture("reading-log.pdf"))) {
    const google = await rsaKeys("g");
    const fetcher = (async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("oauth2")) return Response.json({ access_token: "tok", expires_in: 3600 });
      return url.includes("alt=media") ? media() : meta();
    }) as typeof fetch;
    const sa = JSON.stringify({ client_email: "r@x.iam.gserviceaccount.com", private_key: google.pem });
    const e = env({ RESOURCE_MODE: "drive", LOCAL_DRIVE_TESTING: "true", GOOGLE_SERVICE_ACCOUNT_JSON: sa });
    return handleRequest(get(`/api/resources/${REAL}`, {}, "http://127.0.0.1:8787"), e, undefined, fetcher);
  }

  it("reports a file that is missing or not shared", async () => {
    const res = await driveCall(() => new Response("nope", { status: 404 }));
    expect(res.status).toBe(502);
    expect(await res.text()).toMatch(/not shared with the service account/);
  });

  it("rejects Google Docs and other types that are not PDF, PNG or JPEG", async () => {
    const res = await driveCall(() => Response.json({ mimeType: "application/vnd.google-apps.document", size: "10" }));
    expect(res.status).toBe(502);
    expect(await res.text()).toMatch(/only PDF, PNG and JPEG/);
  });

  it("rejects content that does not match the type Drive reports", async () => {
    const res = await driveCall(() => Response.json({ mimeType: "image/png" }));
    expect(res.status).toBe(502);
    expect(await res.text()).toMatch(/not the expected image\/png/);
  });

  it("rejects oversized files", async () => {
    const res = await driveCall(() => Response.json({ mimeType: "application/pdf", size: String(500 * 1024 * 1024) }));
    expect(res.status).toBe(502);
    expect(await res.text()).toMatch(/larger than the allowed size/);
  });

  it("rejects content that is not really a PDF", async () => {
    const res = await driveCall(
      () => Response.json({ mimeType: "application/pdf" }),
      () => new Response("<html>Sign in to continue</html>"),
    );
    expect(res.status).toBe(502);
    expect(await res.text()).toMatch(/not the expected application\/pdf/);
  });

  it("reports a failed Google sign-in", async () => {
    const google = await rsaKeys("g");
    const fetcher = (async () => new Response("bad", { status: 401 })) as unknown as typeof fetch;
    const sa = JSON.stringify({ client_email: "r@x", private_key: google.pem });
    const e = env({ RESOURCE_MODE: "drive", LOCAL_DRIVE_TESTING: "true", GOOGLE_SERVICE_ACCOUNT_JSON: sa });
    const res = await handleRequest(get(`/api/resources/${REAL}`, {}, "http://localhost"), e, undefined, fetcher);
    expect(res.status).toBe(502);
    expect(await res.text()).toMatch(/Google sign-in failed/);
  });

  it("treats malformed credentials as missing", async () => {
    const e = env({ RESOURCE_MODE: "drive", LOCAL_DRIVE_TESTING: "true", GOOGLE_SERVICE_ACCOUNT_JSON: "not json" });
    const res = await handleRequest(get(`/api/resources/${REAL}`, {}, "http://localhost"), e);
    expect(res.status).toBe(503);
    const health = await (await handleRequest(get("/api/health"), e)).json();
    expect(health).toMatchObject({ mode: "drive", driveConfigured: false, accessConfigured: false });
  });
});
