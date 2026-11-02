/**
 * Read-only Google Drive access with a service account. The key lives only in
 * the GOOGLE_SERVICE_ACCOUNT_JSON Worker secret; tokens never leave the Worker.
 */
import { LIMITS } from "../shared/limits.ts";
import { SNIFF_BYTES, isAllowedMime, sniffMime } from "../shared/sniff.ts";
import type { AllowedMime } from "../shared/types.ts";
import { base64Decode, base64UrlEncode } from "./b64.ts";

const SCOPE = "https://www.googleapis.com/auth/drive.readonly";
const DRIVE = "https://www.googleapis.com/drive/v3/files";

export class ResourceError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

interface ServiceAccount {
  client_email: string;
  private_key: string;
  token_uri: string;
}

export function parseServiceAccount(raw: string | undefined): ServiceAccount | null {
  if (!raw) return null;
  try {
    const sa = JSON.parse(raw) as Partial<ServiceAccount>;
    if (!sa.client_email || !sa.private_key) return null;
    return { client_email: sa.client_email, private_key: sa.private_key, token_uri: sa.token_uri ?? "https://oauth2.googleapis.com/token" };
  } catch {
    return null;
  }
}

let tokenCache: { email: string; token: string; expires: number } | null = null;

export function resetTokenCache() {
  tokenCache = null;
}

async function signJwt(sa: ServiceAccount, now: number): Promise<string> {
  const pem = sa.private_key.replace(/-----(BEGIN|END) PRIVATE KEY-----/g, "").replace(/\s+/g, "");
  const key = await crypto.subtle.importKey("pkcs8", base64Decode(pem), { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const iat = Math.floor(now / 1000);
  const head = base64UrlEncode(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const body = base64UrlEncode(JSON.stringify({ iss: sa.client_email, scope: SCOPE, aud: sa.token_uri, iat, exp: iat + 3600 }));
  const sig = new Uint8Array(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(`${head}.${body}`)));
  return `${head}.${body}.${base64UrlEncode(sig)}`;
}

export async function accessToken(sa: ServiceAccount, fetcher: typeof fetch, now = Date.now()): Promise<string> {
  if (tokenCache && tokenCache.email === sa.client_email && tokenCache.expires - 60_000 > now) return tokenCache.token;
  const res = await fetcher(sa.token_uri, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion: await signJwt(sa, now) }),
  });
  if (!res.ok) throw new ResourceError(`Google sign-in failed (${res.status}).`, 502);
  const body = (await res.json()) as { access_token?: string; expires_in?: number };
  if (!body.access_token) throw new ResourceError("Google sign-in returned no token.", 502);
  tokenCache = { email: sa.client_email, token: body.access_token, expires: now + (body.expires_in ?? 3600) * 1000 };
  return body.access_token;
}

/**
 * Wrap a body so it is only returned once its first bytes match the expected
 * type, and so it errors if it grows past maxBytes.
 */
export async function validatedStream(
  body: ReadableStream<Uint8Array>,
  expected: AllowedMime,
  maxBytes: number,
): Promise<ReadableStream<Uint8Array>> {
  const reader = body.getReader();
  const head: Uint8Array[] = [];
  let have = 0;
  let done = false;
  while (have < SNIFF_BYTES && !done) {
    const r = await reader.read();
    if (r.done) done = true;
    else {
      head.push(r.value);
      have += r.value.length;
    }
  }
  const first = new Uint8Array(have);
  let off = 0;
  for (const c of head) {
    first.set(c, off);
    off += c.length;
  }
  const actual = sniffMime(first);
  if (actual !== expected) {
    await reader.cancel();
    throw new ResourceError(`File content is not the expected ${expected}.`, 502);
  }
  if (have > maxBytes) {
    await reader.cancel();
    throw new ResourceError("File is larger than the allowed size.", 502);
  }
  let total = have;
  let sentHead = false;
  return new ReadableStream<Uint8Array>({
    async pull(controller) {
      if (!sentHead) {
        sentHead = true;
        if (first.length) controller.enqueue(first);
        if (done) controller.close();
        return;
      }
      const r = await reader.read();
      if (r.done) return controller.close();
      total += r.value.length;
      if (total > maxBytes) {
        await reader.cancel();
        return controller.error(new ResourceError("File is larger than the allowed size.", 502));
      }
      controller.enqueue(r.value);
    },
    cancel(reason) {
      return reader.cancel(reason);
    },
  });
}

export interface DriveFile {
  body: ReadableStream<Uint8Array>;
  size: number | null;
  mimeType: AllowedMime;
}

/** Fetch one trusted Drive file after checking its metadata. Only PDF, PNG and JPEG files are served. */
export async function fetchDriveFile(sa: ServiceAccount, fileId: string, fetcher: typeof fetch = fetch): Promise<DriveFile> {
  const token = await accessToken(sa, fetcher);
  const auth = { authorization: `Bearer ${token}` };
  const id = encodeURIComponent(fileId);
  const meta = await fetcher(`${DRIVE}/${id}?fields=id,mimeType,size,trashed&supportsAllDrives=true`, { headers: auth });
  if (meta.status === 404) throw new ResourceError("The file is missing or not shared with the service account.", 502);
  if (!meta.ok) throw new ResourceError(`Google Drive refused the file details (${meta.status}).`, 502);
  const info = (await meta.json()) as { mimeType?: string; size?: string; trashed?: boolean };
  if (info.trashed) throw new ResourceError("The file is in the Drive trash.", 502);
  const mimeType = info.mimeType ?? "";
  if (!isAllowedMime(mimeType))
    throw new ResourceError(`Drive reports ${mimeType || "an unknown type"}; only PDF, PNG and JPEG worksheets can be printed.`, 502);
  const size = info.size ? Number(info.size) : null;
  if (size !== null && size > LIMITS.maxResourceBytes) throw new ResourceError("The file is larger than the allowed size.", 502);

  const media = await fetcher(`${DRIVE}/${id}?alt=media&supportsAllDrives=true`, { headers: auth });
  if (!media.ok || !media.body) throw new ResourceError(`Google Drive refused the download (${media.status}).`, 502);
  return { body: await validatedStream(media.body, mimeType, LIMITS.maxResourceBytes), size, mimeType };
}
