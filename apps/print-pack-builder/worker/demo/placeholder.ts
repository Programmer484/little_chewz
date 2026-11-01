import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

/** Characters the standard Helvetica (WinAnsi) font can draw. */
const safe = (text: string) => text.replace(/[^\x20-\x7e¡-ÿ–—‘’“”•…]/g, "?");

/**
 * A clearly labelled stand-in page for a real allowlisted worksheet, used in
 * demo mode so the whole flow works without Google credentials.
 */
export async function placeholderPdf(title: string, pages: number): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  doc.setTitle(`Demo placeholder: ${safe(title)}`);
  const bold = await doc.embedFont(StandardFonts.HelveticaBold);
  const regular = await doc.embedFont(StandardFonts.Helvetica);
  for (let n = 1; n <= pages; n++) {
    const page = doc.addPage([612, 792]);
    page.drawRectangle({ x: 36, y: 36, width: 540, height: 720, borderColor: rgb(0.93, 0.42, 0.36), borderWidth: 3 });
    page.drawText("DEMO PLACEHOLDER", { x: 60, y: 700, size: 30, font: bold, color: rgb(0.93, 0.42, 0.36) });
    page.drawText(safe(title), { x: 60, y: 660, size: 20, font: bold, color: rgb(0.2, 0.2, 0.25), maxWidth: 490 });
    page.drawText(`Page ${n} of ${pages}. The real worksheet prints here when Drive access is configured.`, {
      x: 60,
      y: 620,
      size: 11,
      font: regular,
      color: rgb(0.3, 0.3, 0.35),
      maxWidth: 490,
    });
  }
  return doc.save();
}
