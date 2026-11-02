/**
 * Combine worksheet files into one printable PDF with pdf-lib.
 *
 * - PDF pages are copied, never rasterized, so artwork and vector text are untouched.
 * - Each entry in the sequence is one copy of a whole worksheet (all its pages).
 * - Repeat copies share the first copy's content and image streams, so the
 *   packet does not grow by the size of the artwork for every student.
 * - PNG and JPEG worksheets are embedded once and fitted proportionally onto
 *   a printable page.
 * - Double-sided: a blank page follows every copy with an odd page count, so
 *   each copy starts on a new sheet and no two copies share a sheet.
 */
import { EncryptedPDFError, PDFDocument, PDFName, PDFPage, type PDFImage, type PDFPageLeaf } from "pdf-lib";
import { LIMITS } from "../../shared/limits.ts";
import { sniffMime } from "../../shared/sniff.ts";

export class PacketError extends Error {}

export interface SourceFile {
  title: string;
  bytes: Uint8Array;
}

export interface AssembleOptions {
  duplex?: boolean;
  /** Paper for image worksheets. PDFs keep their own page size. */
  imagePaper?: "letter" | "a4";
  /** Margin around image worksheets, in points. */
  imageMargin?: number;
  maxPages?: number;
  onProgress?: (done: number, total: number, title: string) => void;
}

export interface AssembledPacket {
  bytes: Uint8Array;
  /** Pages in the PDF, blank backs included. */
  pageCount: number;
  /** Pages that are blank backs added for double-sided printing. */
  blankPages: number;
  /** Paper sheets: pages, or pages / 2 when double-sided. */
  sheetCount: number;
}

const PAPER = { letter: [612, 792], a4: [595.28, 841.89] } as const;

/** A page sharing the original's content, resources and size, without its annotations. */
function repeatPage(doc: PDFDocument, page: PDFPage): PDFPage {
  const node = page.node.clone(doc.context) as PDFPageLeaf;
  node.delete(PDFName.of("Annots"));
  const ref = doc.context.register(node);
  return PDFPage.of(node, ref, doc);
}

type Prepared =
  | { kind: "pdf"; title: string; pages: PDFPage[]; used: boolean; size: [number, number] }
  | { kind: "image"; title: string; image: PDFImage; size: [number, number] };

async function prepare(out: PDFDocument, file: SourceFile, options: AssembleOptions): Promise<Prepared> {
  const kind = sniffMime(file.bytes);
  if (!kind) throw new PacketError(`“${file.title}” is not a PDF, PNG or JPEG file.`);
  if (kind === "application/pdf") {
    let src: PDFDocument;
    let count: number;
    try {
      src = await PDFDocument.load(file.bytes, { updateMetadata: false });
      count = src.getPageCount(); // reading the page tree catches broken files early
    } catch (e) {
      if (e instanceof EncryptedPDFError) throw new PacketError(`“${file.title}” is a protected PDF and cannot be combined.`);
      throw new PacketError(`“${file.title}” could not be read as a PDF.`);
    }
    if (count === 0) throw new PacketError(`“${file.title}” has no pages.`);
    let pages: PDFPage[];
    try {
      pages = await out.copyPages(src, src.getPageIndices());
    } catch {
      throw new PacketError(`“${file.title}” could not be copied from its PDF.`);
    }
    const last = pages[pages.length - 1];
    return { kind: "pdf", title: file.title, pages, used: false, size: [last.getWidth(), last.getHeight()] };
  }
  let image: PDFImage;
  try {
    image = kind === "image/png" ? await out.embedPng(file.bytes) : await out.embedJpg(file.bytes);
  } catch {
    throw new PacketError(`“${file.title}” could not be read as an image.`);
  }
  const [pw, ph] = PAPER[options.imagePaper ?? "letter"];
  const size: [number, number] = image.width > image.height ? [ph, pw] : [pw, ph]; // landscape images get landscape pages
  return { kind: "image", title: file.title, image, size };
}

const pageCountOf = (p: Prepared) => (p.kind === "pdf" ? p.pages.length : 1);

/**
 * Build the packet.
 * @param files    each distinct worksheet, by resource ID
 * @param sequence one resource ID per copy, in print order (see printSequence)
 */
export async function assemblePacket(
  files: ReadonlyMap<string, SourceFile>,
  sequence: readonly string[],
  options: AssembleOptions = {},
): Promise<AssembledPacket> {
  if (sequence.length === 0) throw new PacketError("There is nothing to print for these choices.");
  const maxPages = options.maxPages ?? LIMITS.maxTotalPages;
  const margin = options.imageMargin ?? 18;
  const out = await PDFDocument.create();
  out.setTitle("Little Chewz Print Pack");
  out.setCreator("Little Chewz Print Pack Builder");

  const ids = [...new Set(sequence)];
  const prepared = new Map<string, Prepared>();
  for (const [i, id] of ids.entries()) {
    const file = files.get(id);
    if (!file) throw new PacketError(`A worksheet is missing from the download (${id}).`);
    options.onProgress?.(i, ids.length, file.title);
    prepared.set(id, await prepare(out, file, options));
  }

  // Check the size before building anything.
  let expected = 0;
  let blanks = 0;
  for (const id of sequence) {
    const n = pageCountOf(prepared.get(id)!);
    expected += n;
    if (options.duplex && n % 2 === 1) blanks++;
  }
  if (expected + blanks > maxPages)
    throw new PacketError(`The pack would be ${expected + blanks} pages, over the ${maxPages}-page limit. Lower the copies and try again.`);

  for (const id of sequence) {
    const p = prepared.get(id)!;
    if (p.kind === "pdf") {
      for (const page of p.pages) out.addPage(p.used ? repeatPage(out, page) : page);
      p.used = true;
    } else {
      const [w, h] = p.size;
      const scale = Math.min((w - 2 * margin) / p.image.width, (h - 2 * margin) / p.image.height);
      const dw = p.image.width * scale;
      const dh = p.image.height * scale;
      out.addPage([w, h]).drawImage(p.image, { x: (w - dw) / 2, y: (h - dh) / 2, width: dw, height: dh });
    }
    if (options.duplex && pageCountOf(p) % 2 === 1) out.addPage(p.size); // blank back, same size as the last page
  }
  options.onProgress?.(ids.length, ids.length, "");

  const pageCount = expected + blanks;
  if (out.getPageCount() !== pageCount) throw new PacketError("The pack did not assemble completely. Please try again.");
  const bytes = await out.save();
  return { bytes, pageCount, blankPages: blanks, sheetCount: options.duplex ? Math.ceil(pageCount / 2) : pageCount };
}
