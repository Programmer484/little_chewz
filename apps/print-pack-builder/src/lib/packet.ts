import { LIMITS } from "../../shared/limits.ts";
import type { Plan } from "../../shared/types.ts";
import { type AssembledPacket, PacketError, assemblePacket } from "./assemble.ts";
import { fetchResource } from "./fetchResource.ts";

export type Progress = { stage: "fetching" | "assembling"; done: number; total: number; title: string };

/**
 * Fetch every planned resource, then assemble the packet. Any failure stops
 * the whole build: a partial packet is never returned.
 */
export async function buildPacket(
  plan: Plan,
  onProgress: (p: Progress) => void = () => {},
  fetcher: typeof fetch = fetch,
  signal?: AbortSignal,
): Promise<AssembledPacket> {
  if (plan.problems.length) throw new PacketError(plan.problems[0]);
  const lines = plan.lines.filter((l) => l.copies > 0);
  const files: Uint8Array[] = [];
  let totalBytes = 0;
  for (const [i, line] of lines.entries()) {
    onProgress({ stage: "fetching", done: i, total: lines.length, title: line.title });
    const bytes = await fetchResource(line.resourceId, line.title, fetcher, signal);
    totalBytes += bytes.length;
    if (totalBytes > LIMITS.maxTotalSourceBytes)
      throw new PacketError("These worksheets are too large to combine in one pack. Try fewer activities at a time.");
    files.push(bytes);
  }
  if (signal?.aborted) throw new PacketError("Download cancelled.");
  return assemblePacket(
    lines.map((line, i) => ({ resourceId: line.resourceId, title: line.title, copies: line.copies, bytes: files[i] })),
    { onProgress: (done, total, title) => onProgress({ stage: "assembling", done, total, title }) },
  );
}

export function packetFilename(lessonTitle: string): string {
  const slug = lessonTitle
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^A-Za-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return `Little_Chewz_${slug || "Lesson"}_Print_Pack.pdf`;
}

/** Save bytes as a file download in the browser. */
export function saveFile(bytes: Uint8Array, filename: string) {
  const blob = new Blob([bytes as Uint8Array<ArrayBuffer>], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}
