import { PDFDocument } from "pdf-lib";
import { describe, expect, it } from "vitest";
import { PacketError, type SourceFile, assemblePacket } from "../src/lib/assemble.ts";
import { packetFilename } from "../src/lib/packet.ts";
import { fixture, pdfWithPages } from "./helpers.ts";

const files = (entries: [string, Uint8Array][]) => new Map<string, SourceFile>(entries.map(([id, bytes]) => [id, { title: id, bytes }]));
const repeat = (id: string, n: number) => Array<string>(n).fill(id);
const sizes = async (bytes: Uint8Array) =>
  (await PDFDocument.load(bytes)).getPages().map((p) => [Math.round(p.getWidth()), Math.round(p.getHeight())]);
const texts = async (bytes: Uint8Array) => {
  const doc = await PDFDocument.load(bytes);
  // Each test page draws one label; blank backs have no content stream.
  return doc.getPages().map((p) => (p.node.Contents() ? "page" : "blank"));
};

describe("assemblePacket", () => {
  it("repeats every page of a multi-page PDF, copy after copy", async () => {
    const src = await PDFDocument.create();
    src.addPage([612, 792]).drawText("first");
    src.addPage([300, 400]).drawText("second");
    const out = await assemblePacket(files([["two", await src.save()]]), repeat("two", 3));
    expect(out).toMatchObject({ pageCount: 6, sheetCount: 6, blankPages: 0 });
    expect(await sizes(out.bytes)).toEqual([[612, 792], [300, 400], [612, 792], [300, 400], [612, 792], [300, 400]]);
  });

  it("follows the given order and keeps page sizes", async () => {
    const f = files([["a4", fixture("exit-ticket.pdf")], ["letter", await pdfWithPages(1)]]);
    expect(await sizes((await assemblePacket(f, ["a4", "a4", "letter"])).bytes)).toEqual([[595, 842], [595, 842], [612, 792]]);
    expect(await sizes((await assemblePacket(f, ["a4", "letter", "a4", "letter"])).bytes)).toEqual([[595, 842], [612, 792], [595, 842], [612, 792]]);
  });

  it("adds a blank back after every odd-page copy when double-sided", async () => {
    const f = files([["one", await pdfWithPages(1)], ["two", await pdfWithPages(2)], ["three", await pdfWithPages(3, [595, 842])]]);
    const out = await assemblePacket(f, ["one", "two", "three", "one"], { duplex: true });
    expect(out).toMatchObject({ pageCount: 10, blankPages: 3, sheetCount: 5 });
    expect(await texts(out.bytes)).toEqual(["page", "blank", "page", "page", "page", "page", "page", "blank", "page", "blank"]);
    expect((await sizes(out.bytes))[7]).toEqual([595, 842]); // the blank back matches the A4 page before it
  });

  it("fits a PNG onto a portrait page and a landscape JPEG onto a landscape page", async () => {
    const out = await assemblePacket(files([["png", fixture("station-poster.png")], ["jpg", fixture("photo-prompt.jpg")]]), ["png", "png", "jpg"]);
    expect(await sizes(out.bytes)).toEqual([[612, 792], [612, 792], [792, 612]]);
  });

  it("does not duplicate image bytes for repeated copies", async () => {
    const jpg = fixture("photo-prompt.jpg");
    const one = await assemblePacket(files([["jpg", jpg]]), ["jpg"]);
    const many = await assemblePacket(files([["jpg", jpg]]), repeat("jpg", 30));
    expect(many.bytes.length).toBeLessThan(one.bytes.length + 30 * 1000);
    const pdfOne = await assemblePacket(files([["pdf", one.bytes]]), ["pdf"]);
    const pdfMany = await assemblePacket(files([["pdf", one.bytes]]), repeat("pdf", 30));
    expect(pdfMany.bytes.length).toBeLessThan(pdfOne.bytes.length + 30 * 1000);
  });

  it("refuses an empty pack or a missing file", async () => {
    await expect(assemblePacket(files([]), [])).rejects.toThrow(/nothing to print/);
    await expect(assemblePacket(files([]), ["ghost"])).rejects.toThrow(/missing/);
  });

  it("rejects HTML error pages and other unsupported files", async () => {
    const html = new TextEncoder().encode("<!doctype html><html><body>Sign in</body></html>");
    await expect(assemblePacket(files([["Clue Tracker", html]]), ["Clue Tracker"])).rejects.toThrow(PacketError);
    await expect(assemblePacket(files([["Clue Tracker", html]]), ["Clue Tracker"])).rejects.toThrow(/not a PDF, PNG or JPEG/);
    const gif = new TextEncoder().encode("GIF89a.....");
    await expect(assemblePacket(files([["gif", gif]]), ["gif"])).rejects.toThrow(/not a PDF, PNG or JPEG/);
  });

  it("rejects malformed PDFs and images", async () => {
    const badPdf = new TextEncoder().encode("%PDF-1.7\nthis is not really a pdf");
    await expect(assemblePacket(files([["Broken", badPdf]]), ["Broken"])).rejects.toThrow(PacketError);
    const badPng = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 1, 2, 3]);
    await expect(assemblePacket(files([["Broken PNG", badPng]]), ["Broken PNG"])).rejects.toThrow(/could not be read as an image/);
  });

  it("enforces the page limit, counting blank backs, before building", async () => {
    const f = files([["big", await pdfWithPages(5)]]);
    await expect(assemblePacket(f, repeat("big", 8), { maxPages: 40 })).resolves.toMatchObject({ pageCount: 40 });
    await expect(assemblePacket(f, repeat("big", 8), { maxPages: 40, duplex: true })).rejects.toThrow(/48 pages, over the 40-page limit/);
  });
});

describe("packetFilename", () => {
  it("builds a descriptive filename", () => {
    expect(packetFilename("Set the Table")).toBe("Little_Chewz_Set_the_Table_Print_Pack.pdf");
    expect(packetFilename("Secret Ingredients")).toBe("Little_Chewz_Secret_Ingredients_Print_Pack.pdf");
    expect(packetFilename("Café: Part 2!")).toBe("Little_Chewz_Cafe_Part_2_Print_Pack.pdf");
  });
});
