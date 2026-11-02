/**
 * Combine worksheets as consecutive student packets, followed by shared copies.
 * Duplex padding occurs only at packet boundaries and on shared material backs.
 * Multi-card cutout sheets print front-only, even when the source has many pages.
 */
import { EncryptedPDFError, PDFDocument, PDFName, PDFPage, type PDFImage, type PDFPageLeaf } from "pdf-lib";
import { LIMITS } from "../../shared/limits.ts";
import type { PrintSequence } from "../../shared/types.ts";
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
 * Every selected file is prepared once and reused without rasterizing PDF pages.
 * Student worksheets may share a physical sheet; separate students never do.
 */
export async function assemblePacket(
  files: ReadonlyMap<string, SourceFile>,
  sequence: PrintSequence,
  options: AssembleOptions = {},
): Promise<AssembledPacket> {
  const packets = sequence.packets.filter((packet) => packet.length);
  const ids = [...new Set([...packets.flat(), ...sequence.shared.map((copy) => copy.resourceId)])];
  if (!ids.length) throw new PacketError("There is nothing to print for these choices.");

  const maxPages = options.maxPages ?? LIMITS.maxTotalPages;
  const margin = options.imageMargin ?? 18;
  const out = await PDFDocument.create();
  out.setTitle("Little Chewz Print Pack");
  out.setCreator("Little Chewz Print Pack Builder");

  const prepared = new Map<string, Prepared>();
  for (const [i, id] of ids.entries()) {
    const file = files.get(id);
    if (!file) throw new PacketError(`A worksheet is missing from the download (${id}).`);
    options.onProgress?.(i, ids.length, file.title);
    prepared.set(id, await prepare(out, file, options));
  }

  let expected = 0;
  let blanks = 0;
  for (const [i, packet] of packets.entries()) {
    const pages = packet.reduce((sum, id) => sum + pageCountOf(prepared.get(id)!), 0);
    expected += pages;
    if (options.duplex && pages % 2 && (i < packets.length - 1 || sequence.shared.length)) blanks++;
  }
  for (const copy of sequence.shared) {
    const pages = pageCountOf(prepared.get(copy.resourceId)!);
    expected += pages;
    if (options.duplex) blanks += copy.frontOnly ? pages : pages % 2;
  }
  if (expected + blanks > maxPages)
    throw new PacketError(`The pack would be ${expected + blanks} pages, over the ${maxPages}-page limit. Lower the copies and try again.`);

  const blankBack = () => {
    const last = out.getPages().at(-1)!;
    out.addPage([last.getWidth(), last.getHeight()]);
  };
  const addCopy = (id: string, frontOnly: boolean) => {
    const p = prepared.get(id)!;
    if (p.kind === "pdf") {
      for (const page of p.pages) {
        out.addPage(p.used ? repeatPage(out, page) : page);
        if (options.duplex && frontOnly) blankBack();
      }
      p.used = true;
    } else {
      const [w, h] = p.size;
      const scale = Math.min((w - 2 * margin) / p.image.width, (h - 2 * margin) / p.image.height);
      const dw = p.image.width * scale;
      const dh = p.image.height * scale;
      out.addPage([w, h]).drawImage(p.image, { x: (w - dw) / 2, y: (h - dh) / 2, width: dw, height: dh });
      if (options.duplex && frontOnly) blankBack();
    }
  };

  for (const [i, packet] of packets.entries()) {
    for (const id of packet) addCopy(id, false);
    const pages = packet.reduce((sum, id) => sum + pageCountOf(prepared.get(id)!), 0);
    if (options.duplex && pages % 2 && (i < packets.length - 1 || sequence.shared.length)) blankBack();
  }
  for (const copy of sequence.shared) {
    addCopy(copy.resourceId, copy.frontOnly);
    if (options.duplex && !copy.frontOnly && pageCountOf(prepared.get(copy.resourceId)!) % 2) blankBack();
  }
  options.onProgress?.(ids.length, ids.length, "");
  const pageCount = expected + blanks;
  if (out.getPageCount() !== pageCount) throw new PacketError("The pack did not assemble completely. Please try again.");
  const bytes = await out.save();
  return { bytes, pageCount, blankPages: blanks, sheetCount: options.duplex ? Math.ceil(pageCount / 2) : pageCount };
}
