/**
 * Combine worksheet files into one printable PDF with pdf-lib.
 *
 * - PDF pages are copied, never rasterized, so artwork and vector text are untouched.
 * - A multi-page worksheet is repeated whole, copy after copy.
 * - Repeat copies share the first copy's content and image streams, so the
 *   packet does not grow by the size of the artwork for every student.
 * - PNG and JPEG worksheets are embedded once and fitted proportionally onto
 *   a printable page.
 */
import { EncryptedPDFError, PDFDocument, PDFName, PDFPage, type PDFPageLeaf } from "pdf-lib";
import { LIMITS } from "../../shared/limits.ts";
import { sniffMime } from "../../shared/sniff.ts";

export class PacketError extends Error {}

export interface PacketItem {
  resourceId: string;
  title: string;
  copies: number;
  bytes: Uint8Array;
}

export interface AssembleOptions {
  /** Paper for image worksheets. PDFs keep their own page size. */
  imagePaper?: "letter" | "a4";
  /** Margin around image worksheets, in points. */
  imageMargin?: number;
  maxPages?: number;
  onProgress?: (done: number, total: number, title: string) => void;
}

const PAPER = { letter: [612, 792], a4: [595.28, 841.89] } as const;

/** A page sharing the original's content, resources and size, without its annotations. */
function repeatPage(doc: PDFDocument, page: PDFPage): PDFPage {
  const node = page.node.clone(doc.context) as PDFPageLeaf;
  node.delete(PDFName.of("Annots"));
  const ref = doc.context.register(node);
  return PDFPage.of(node, ref, doc);
}

async function loadSource(item: PacketItem): Promise<{ src: PDFDocument; count: number }> {
  try {
    const src = await PDFDocument.load(item.bytes, { updateMetadata: false });
    return { src, count: src.getPageCount() }; // reading the page tree catches broken files early
  } catch (e) {
    if (e instanceof EncryptedPDFError)
      throw new PacketError(`“${item.title}” is a protected PDF and cannot be combined.`);
    throw new PacketError(`“${item.title}” could not be read as a PDF.`);
  }
}

export interface AssembledPacket {
  bytes: Uint8Array;
  pageCount: number;
}

export async function assemblePacket(items: PacketItem[], options: AssembleOptions = {}): Promise<AssembledPacket> {
  const maxPages = options.maxPages ?? LIMITS.maxTotalPages;
  const margin = options.imageMargin ?? 18;
  const out = await PDFDocument.create();
  out.setTitle("Little Chewz Print Pack");
  out.setCreator("Little Chewz Print Pack Builder");
  let expected = 0;

  const printable = items.filter((i) => i.copies > 0);
  for (const [index, item] of printable.entries()) {
    options.onProgress?.(index, printable.length, item.title);
    if (!Number.isInteger(item.copies) || item.copies < 0) throw new PacketError(`Invalid copy count for “${item.title}”.`);
    const kind = sniffMime(item.bytes);
    if (!kind) throw new PacketError(`“${item.title}” is not a PDF, PNG or JPEG file.`);

    if (kind === "application/pdf") {
      const { src, count } = await loadSource(item);
      if (count === 0) throw new PacketError(`“${item.title}” has no pages.`);
      if (expected + count * item.copies > maxPages)
        throw new PacketError(`The pack would be over ${maxPages} pages. Lower the quantities and try again.`);
      let first: PDFPage[];
      try {
        first = await out.copyPages(src, src.getPageIndices());
      } catch {
        throw new PacketError(`“${item.title}” could not be copied from its PDF.`);
      }
      first.forEach((p) => out.addPage(p));
      for (let c = 1; c < item.copies; c++) first.forEach((p) => out.addPage(repeatPage(out, p)));
      expected += count * item.copies;
    } else {
      if (expected + item.copies > maxPages)
        throw new PacketError(`The pack would be over ${maxPages} pages. Lower the quantities and try again.`);
      let image;
      try {
        image = kind === "image/png" ? await out.embedPng(item.bytes) : await out.embedJpg(item.bytes);
      } catch {
        throw new PacketError(`“${item.title}” could not be read as an image.`);
      }
      const [pw, ph] = PAPER[options.imagePaper ?? "letter"];
      const [w, h] = image.width > image.height ? [ph, pw] : [pw, ph]; // landscape images get landscape pages
      const scale = Math.min((w - 2 * margin) / image.width, (h - 2 * margin) / image.height);
      const dw = image.width * scale;
      const dh = image.height * scale;
      for (let c = 0; c < item.copies; c++) {
        const page = out.addPage([w, h]);
        page.drawImage(image, { x: (w - dw) / 2, y: (h - dh) / 2, width: dw, height: dh });
      }
      expected += item.copies;
    }
  }
  options.onProgress?.(printable.length, printable.length, "");
  if (expected === 0) throw new PacketError("There is nothing to print for these choices.");
  if (out.getPageCount() !== expected) throw new PacketError("The pack did not assemble completely. Please try again.");
  const bytes = await out.save();
  return { bytes, pageCount: expected };
}
