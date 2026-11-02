import { LIMITS } from "../../shared/limits.ts";
import { isAllowedMime, sniffMime } from "../../shared/sniff.ts";
import { PacketError } from "./assemble.ts";

/** Fetch one worksheet from the Worker and check it really is a usable file. */
export async function fetchResource(
  resourceId: string,
  title: string,
  fetcher: typeof fetch = fetch,
  signal?: AbortSignal,
): Promise<Uint8Array> {
  let res: Response;
  try {
    res = await fetcher(`/api/resources/${encodeURIComponent(resourceId)}`, { signal, credentials: "same-origin" });
  } catch {
    if (signal?.aborted) throw new PacketError("Download cancelled.");
    throw new PacketError(`Could not reach the server for “${title}”. Check your connection and try again.`);
  }
  if (!res.ok) {
    let message = `Could not retrieve “${title}” (error ${res.status}).`;
    try {
      const body = (await res.json()) as { error?: string };
      if (body.error) message = body.error;
    } catch {
      /* not JSON */
    }
    throw new PacketError(message);
  }
  const type = (res.headers.get("content-type") ?? "").split(";")[0].trim();
  if (!isAllowedMime(type)) throw new PacketError(`“${title}” did not arrive as a PDF or image.`);
  const length = Number(res.headers.get("content-length") ?? "0");
  if (length > LIMITS.maxResourceBytes) throw new PacketError(`“${title}” is too large to combine.`);
  let bytes: Uint8Array;
  try {
    bytes = new Uint8Array(await res.arrayBuffer());
  } catch {
    throw new PacketError(`The download of “${title}” was interrupted. Please try again.`);
  }
  if (bytes.length === 0) throw new PacketError(`“${title}” arrived empty.`);
  if (bytes.length > LIMITS.maxResourceBytes) throw new PacketError(`“${title}” is too large to combine.`);
  if (length && bytes.length !== length) throw new PacketError(`The download of “${title}” was incomplete. Please try again.`);
  if (sniffMime(bytes) !== type) throw new PacketError(`“${title}” is not the file type the server reported.`);
  return bytes;
}
