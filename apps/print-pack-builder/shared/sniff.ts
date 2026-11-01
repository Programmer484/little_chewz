import type { AllowedMime } from "./types.ts";

const PNG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const PDF = [0x25, 0x50, 0x44, 0x46, 0x2d]; // "%PDF-"

/** Bytes needed to recognise a file. A PDF header may follow a little junk. */
export const SNIFF_BYTES = 1024;

/** Identify a PDF, PNG or JPEG from its first bytes; null for anything else (HTML error pages included). */
export function sniffMime(bytes: Uint8Array): AllowedMime | null {
  const starts = (sig: number[], at = 0) => sig.every((b, i) => bytes[at + i] === b);
  if (starts(PNG)) return "image/png";
  if (bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return "image/jpeg";
  const limit = Math.min(bytes.length - PDF.length, SNIFF_BYTES - PDF.length);
  for (let i = 0; i <= limit; i++) if (starts(PDF, i)) return "application/pdf";
  return null;
}

export function isAllowedMime(value: string): value is AllowedMime {
  return value === "application/pdf" || value === "image/png" || value === "image/jpeg";
}
