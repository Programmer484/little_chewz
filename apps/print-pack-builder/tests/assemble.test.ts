import { PDFDocument } from "pdf-lib";
import { describe, expect, it } from "vitest";
import { PacketError, assemblePacket } from "../src/lib/assemble.ts";
import { packetFilename } from "../src/lib/packet.ts";
import { fixture, pdfWithPages } from "./helpers.ts";

const item = (title: string, bytes: Uint8Array, copies: number) => ({ resourceId: title, title, bytes, copies });
const sizes = async (bytes: Uint8Array) =>
  (await PDFDocument.load(bytes)).getPages().map((p) => [Math.round(p.getWidth()), Math.round(p.getHeight())]);

describe("assemblePacket", () => {
  it("repeats every page of a multi-page PDF, copy after copy", async () => {
    const src = await PDFDocument.create();
    src.addPage([612, 792]).drawText("first");
    src.addPage([300, 400]).drawText("second");
    const out = await assemblePacket([item("two-page", await src.save(), 3)]);
    expect(out.pageCount).toBe(6);
    expect(await sizes(out.bytes)).toEqual([
      [612, 792], [300, 400],
      [612, 792], [300, 400],
      [612, 792], [300, 400],
    ]);
  });

  it("keeps resources in order and preserves page sizes", async () => {
    const out = await assemblePacket([
      item("A4 sheet", fixture("exit-ticket.pdf"), 2),
      item("Letter sheet", await pdfWithPages(1), 1),
    ]);
    expect(await sizes(out.bytes)).toEqual([[595, 842], [595, 842], [612, 792]]);
  });

  it("fits a PNG onto a portrait page and a landscape JPEG onto a landscape page", async () => {
    const out = await assemblePacket([item("png", fixture("station-poster.png"), 2), item("jpg", fixture("photo-prompt.jpg"), 1)]);
    expect(await sizes(out.bytes)).toEqual([[612, 792], [612, 792], [792, 612]]);
  });

  it("does not duplicate image bytes for repeated copies", async () => {
    const jpg = fixture("photo-prompt.jpg");
    const one = await assemblePacket([item("jpg", jpg, 1)]);
    const many = await assemblePacket([item("jpg", jpg, 30)]);
    expect(many.bytes.length).toBeLessThan(one.bytes.length + 30 * 1000);
    const pdf = await assemblePacket([item("pdf", one.bytes, 1)]);
    const pdfMany = await assemblePacket([item("pdf", one.bytes, 30)]);
    expect(pdfMany.bytes.length).toBeLessThan(pdf.bytes.length + 30 * 1000);
  });

  it("skips zero-copy items and refuses an empty pack", async () => {
    const out = await assemblePacket([item("a", await pdfWithPages(1), 0), item("b", await pdfWithPages(2), 1)]);
    expect(out.pageCount).toBe(2);
    await expect(assemblePacket([item("a", await pdfWithPages(1), 0)])).rejects.toThrow(/nothing to print/);
  });

  it("rejects HTML error pages and other unsupported files", async () => {
    const html = new TextEncoder().encode("<!doctype html><html><body>Sign in</body></html>");
    await expect(assemblePacket([item("Clue Tracker", html, 1)])).rejects.toThrow(PacketError);
    await expect(assemblePacket([item("Clue Tracker", html, 1)])).rejects.toThrow(/not a PDF, PNG or JPEG/);
    const gif = new TextEncoder().encode("GIF89a.....");
    await expect(assemblePacket([item("gif", gif, 1)])).rejects.toThrow(/not a PDF, PNG or JPEG/);
  });

  it("rejects malformed PDFs and images", async () => {
    const badPdf = new TextEncoder().encode("%PDF-1.7\nthis is not really a pdf");
    await expect(assemblePacket([item("Broken", badPdf, 1)])).rejects.toThrow(PacketError);
    const badPng = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 1, 2, 3]);
    await expect(assemblePacket([item("Broken PNG", badPng, 1)])).rejects.toThrow(/could not be read as an image/);
  });

  it("enforces the page limit before building", async () => {
    await expect(assemblePacket([item("big", await pdfWithPages(5), 10)], { maxPages: 40 })).rejects.toThrow(/over 40 pages/);
  });
});

describe("packetFilename", () => {
  it("builds a descriptive filename", () => {
    expect(packetFilename("Set the Table")).toBe("Little_Chewz_Set_the_Table_Print_Pack.pdf");
    expect(packetFilename("Secret Ingredients")).toBe("Little_Chewz_Secret_Ingredients_Print_Pack.pdf");
    expect(packetFilename("Café: Part 2!")).toBe("Little_Chewz_Cafe_Part_2_Print_Pack.pdf");
  });
});
