import { PDFDocument } from "pdf-lib";
import { describe, expect, it } from "vitest";
import { PacketError, type SourceFile, assemblePacket } from "../src/lib/assemble.ts";
import { packetFilename } from "../src/lib/packet.ts";
import { fixture, pdfWithPages } from "./helpers.ts";

const files = (entries: [string, Uint8Array][]) =>
  new Map<string, SourceFile>(entries.map(([id, bytes]) => [id, { title: id, bytes }]));
const student = (...ids: string[]) => ({ packets: [ids], shared: [] });
const repeat = (id: string, n: number) => Array<string>(n).fill(id);
const sizes = async (bytes: Uint8Array) =>
  (await PDFDocument.load(bytes)).getPages().map((p) => [Math.round(p.getWidth()), Math.round(p.getHeight())]);
const blanks = async (bytes: Uint8Array) => (await PDFDocument.load(bytes))
  .getPages().map((p) => p.node.Contents() ? "page" : "blank");

describe("assemblePacket", () => {
  it("preserves every page of a multi-page worksheet in every student copy", async () => {
    const src = await PDFDocument.create();
    src.addPage([612, 792]).drawText("first");
    src.addPage([300, 400]).drawText("second");
    const out = await assemblePacket(files([["two", await src.save()]]), {
      packets: [["two"], ["two"], ["two"]], shared: [],
    });
    expect(out).toMatchObject({ pageCount: 6, sheetCount: 6, blankPages: 0 });
    expect(await sizes(out.bytes)).toEqual([[612, 792], [300, 400], [612, 792], [300, 400], [612, 792], [300, 400]]);
  });

  it("allows different odd-page worksheets on the front and back of a student's sheet", async () => {
    const f = files([["a", await pdfWithPages(1)], ["b", await pdfWithPages(1)]]);
    const out = await assemblePacket(f, { packets: [["a", "b"], ["a", "b"]], shared: [] }, { duplex: true });
    expect(out).toMatchObject({ pageCount: 4, blankPages: 0, sheetCount: 2 });
    expect(await blanks(out.bytes)).toEqual(["page", "page", "page", "page"]);
  });

  it("pads only the boundary of an odd-sized packet, not individual worksheets", async () => {
    const f = files([["one", await pdfWithPages(1)], ["two", await pdfWithPages(2)], ["three", await pdfWithPages(3, [595, 842])]]);
    const out = await assemblePacket(f, {
      packets: [["one", "two"], ["three", "one"]], shared: [],
    }, { duplex: true });
    expect(out).toMatchObject({ pageCount: 8, blankPages: 1, sheetCount: 4 });
    expect(await blanks(out.bytes)).toEqual(["page", "page", "page", "blank", "page", "page", "page", "page"]);
    expect((await sizes(out.bytes))[3]).toEqual([612, 792]);
  });

  it("puts group materials after packets with their own duplex reverses", async () => {
    const f = files([["student", await pdfWithPages(3)], ["shared", await pdfWithPages(1)], ["two", await pdfWithPages(2)]]);
    const out = await assemblePacket(f, {
      packets: [["student"]], shared: [
        { resourceId: "shared", frontOnly: false },
        { resourceId: "shared", frontOnly: false },
        { resourceId: "two", frontOnly: false },
      ],
    }, { duplex: true });
    expect(out).toMatchObject({ pageCount: 10, blankPages: 3 });
    expect(await blanks(out.bytes)).toEqual([
      "page", "page", "page", "blank", "page", "blank", "page", "blank", "page", "page",
    ]);
  });

  it("makes every cutout page front-only, even for a multi-page card source", async () => {
    const f = files([["cards", await pdfWithPages(2)]]);
    const out = await assemblePacket(f, {
      packets: [], shared: repeat("cards", 2).map((resourceId) => ({ resourceId, frontOnly: true })),
    }, { duplex: true });
    expect(out).toMatchObject({ pageCount: 8, blankPages: 4, sheetCount: 4 });
    expect(await blanks(out.bytes)).toEqual(["page", "blank", "page", "blank", "page", "blank", "page", "blank"]);
  });

  it("does not add blanks when single-sided, including shared cards", async () => {
    const f = files([["one", await pdfWithPages(1)], ["cards", await pdfWithPages(2)]]);
    const out = await assemblePacket(f, {
      packets: [["one"], ["one"]], shared: [{ resourceId: "cards", frontOnly: true }],
    }, { duplex: false });
    expect(out).toMatchObject({ pageCount: 4, blankPages: 0, sheetCount: 4 });
  });

  it("fits portrait PNG and landscape JPEG without changing PDF page sizes", async () => {
    const f = files([["png", fixture("station-poster.png")], ["jpg", fixture("photo-prompt.jpg")], ["pdf", fixture("exit-ticket.pdf")]]);
    const out = await assemblePacket(f, student("png", "jpg", "pdf"));
    expect(await sizes(out.bytes)).toEqual([[612, 792], [792, 612], [595, 842]]);
  });

  it("shares image and PDF content across many copies", async () => {
    const jpg = fixture("photo-prompt.jpg");
    const one = await assemblePacket(files([["jpg", jpg]]), student("jpg"));
    const many = await assemblePacket(files([["jpg", jpg]]), { packets: repeat("jpg", 30).map((id) => [id]), shared: [] });
    expect(many.bytes.length).toBeLessThan(one.bytes.length + 30 * 10000);
    const pdfOne = await assemblePacket(files([["pdf", one.bytes]]), student("pdf"));
    const pdfMany = await assemblePacket(files([["pdf", one.bytes]]), { packets: repeat("pdf", 30).map((id) => [id]), shared: [] });
    expect(pdfMany.bytes.length).toBeLessThan(pdfOne.bytes.length + 30 * 10000);
  });

  it("rejects an empty pack, missing files, and unsupported input", async () => {
    await expect(assemblePacket(files([]), { packets: [], shared: [] })).rejects.toThrow(/nothing to print/);
    await expect(assemblePacket(files([]), student("ghost"))).rejects.toThrow(/missing/);
    const html = new TextEncoder().encode("<html>login</html>");
    await expect(assemblePacket(files([["bad", html]]), student("bad"))).rejects.toThrow(PacketError);
    await expect(assemblePacket(files([["bad", html]]), student("bad"))).rejects.toThrow(/not a PDF, PNG or JPEG/);
  });

  it("rejects malformed PDFs and images", async () => {
    const badPdf = new TextEncoder().encode("%PDF-1.7\nthis is not really a pdf");
    await expect(assemblePacket(files([["Broken", badPdf]]), student("Broken"))).rejects.toThrow(PacketError);
    const badPng = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 1, 2, 3]);
    await expect(assemblePacket(files([["Broken PNG", badPng]]), student("Broken PNG"))).rejects.toThrow(/could not be read as an image/);
  });

  it("counts only necessary blank pages when enforcing the size limit", async () => {
    const f = files([["big", await pdfWithPages(5)]]);
    await expect(assemblePacket(f, student(...repeat("big", 8)), { maxPages: 40, duplex: true }))
      .resolves.toMatchObject({ pageCount: 40, blankPages: 0 });
    const packets = repeat("big", 8).map((id) => [id]);
    await expect(assemblePacket(f, { packets, shared: [] }, { maxPages: 40, duplex: true }))
      .rejects.toThrow(/47 pages, over the 40-page limit/);
  });
});

describe("packetFilename", () => {
  it("builds a descriptive filename", () => {
    expect(packetFilename("Set the Table")).toBe("Little_Chewz_Set_the_Table_Print_Pack.pdf");
    expect(packetFilename("Café: Part 2!")).toBe("Little_Chewz_Cafe_Part_2_Print_Pack.pdf");
  });
});
