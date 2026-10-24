"""Render a document in the "claude" page style.

Clean, left-aligned A4 pages styled to match the Confetti Cake Cottage
School Welcome PDF: cream page, crest or Little Chewz logo in the header,
brush headline, coral numbers and labels, hairline dividers. Fonts are
open-licensed (SIL OFL) stand-ins for the Canva originals: Sedgwick Ave
Display for Better Faster, Outfit for Glacial Indifference.

The document is a JSON file with an optional cover PDF and a list of
pages; each page has a header (mark, eyebrow, title) and blocks:
  lede        larger intro sentence
  paragraphs  optional coral label plus paragraphs
  list        numbered rows: title, text, optional note {label, text}
  callout     coral bar with a short statement and optional subtext
  nav         quest navigation rows; each row links to a registry
              resource (catalog/resources.json) when it is approved or
              published, otherwise shows the pending label

Usage (from the repository root):
    python templates/claude/render.py \
        content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json \
        --output exports/01-welcome.pdf
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
FONTS = ASSETS / "fonts"
REPO = HERE.parent.parent
REGISTRY = REPO / "catalog" / "resources.json"
LINKABLE = {"approved", "published"}

# Page matches the Welcome PDF exactly (Canva A4).
PAGE_W, PAGE_H = 595.5, 842.25
MARGIN = 56
CONTENT_W = PAGE_W - 2 * MARGIN
BOTTOM = 84  # content stays above this; footer sits below


def rgb(r: int, g: int, b: int) -> Color:
    return Color(r / 255, g / 255, b / 255)


# Palette sampled from the Welcome PDF.
CREAM = rgb(250, 245, 239)
INK = rgb(28, 24, 22)
BODY_INK = rgb(58, 50, 44)
MUTED = rgb(110, 96, 84)
BROWN = rgb(112, 82, 52)
CORAL = rgb(238, 128, 96)
TINT = rgb(245, 231, 221)
HAIRLINE = rgb(226, 214, 200)
CREST_RING = rgb(0, 59, 49)

HEADLINE = "SedgwickAveDisplay"
BODY = "Outfit"
BOLD = "Outfit-Bold"

# Indent for text that sits beside a number column.
NUM_COL = 34


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(HEADLINE, str(FONTS / "SedgwickAveDisplay-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BODY, str(FONTS / "Outfit-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD, str(FONTS / "Outfit-Bold.ttf")))


# ---------------------------------------------------------------- helpers

def width(text: str, font: str, size: float, spacing: float = 0) -> float:
    return pdfmetrics.stringWidth(text, font, size) + spacing * max(len(text) - 1, 0)


def spaced(c, x, y, text, font, size, spacing, color, align="left"):
    w = width(text, font, size, spacing)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(spacing)
    t.setFillColor(color)
    t.textOut(text)
    t.setCharSpace(0)  # do not leak spacing into later drawString calls
    c.drawText(t)
    return w


def wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if width(trial, font, size) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_block(c, x, y, text, font, size, leading, max_width, color) -> float:
    """Draw wrapped text with its first baseline at y; return the last baseline."""
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap(text, font, size, max_width)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return y - (len(lines) - 1) * leading


def label(c, x, y, text, color=CORAL):
    spaced(c, x, y, text.upper(), BOLD, 9, 1.5, color)


def hairline(c, y, x0=MARGIN, x1=PAGE_W - MARGIN):
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.6)
    c.line(x0, y, x1, y)


# ----------------------------------------------------------------- blocks
# Each block draws from a cursor y (top of the block) and returns the new
# cursor (bottom of the block). `flex` adds space to internal gaps so a
# page can be spread out to fill its height.

def block_lede(c, b, y, flex):
    last = text_block(c, MARGIN, y - 15, b["text"], BODY, 15, 21, CONTENT_W, INK)
    return last - 6


def block_paragraphs(c, b, y, flex):
    if b.get("label"):
        label(c, MARGIN, y - 9, b["label"])
        y -= 9 + 12 + flex * 0.3
    for i, para in enumerate(b["paragraphs"]):
        if i:
            y -= 9 + flex * 0.3
        last = text_block(c, MARGIN, y - 12, para, BODY, 11.5, 16.5, CONTENT_W, BODY_INK)
        y = last - 4
    return y


def block_list(c, b, y, flex):
    compact = b.get("compact", False)
    gap = (11 if compact else 15) + flex
    size, lead = (10.5, 14.5) if compact else (11, 15.5)
    text_x = MARGIN + NUM_COL
    text_w = PAGE_W - MARGIN - text_x
    if b.get("label"):
        label(c, MARGIN, y - 9, b["label"])
        y -= 9 + 10
    for i, item in enumerate(b["items"]):
        if i:
            hairline(c, y - gap / 2)
            y -= gap
        base = y - 14
        if item.get("number"):
            c.setFillColor(CORAL)
            c.setFont(BOLD, 13)
            c.drawString(MARGIN, base, item["number"])
        c.setFillColor(INK)
        c.setFont(BOLD, 13.5)
        c.drawString(text_x, base, item["title"])
        last = text_block(c, text_x, base - lead - 1, item["text"], BODY, size, lead, text_w, MUTED)
        note = item.get("note")
        if note:
            ny = last - lead
            lw = spaced(c, text_x, ny, note["label"].upper(), BOLD, 8.5, 1.3, CORAL)
            c.setFont(BODY, size)
            c.setFillColor(BODY_INK)
            c.drawString(text_x + lw + 7, ny, note["text"])
            last = ny
        y = last - 5
    return y


def block_callout(c, b, y, flex):
    x = MARGIN + 16
    first = y - 15
    last = text_block(c, x, first, b["text"], BODY, 14, 20, CONTENT_W - 16, INK)
    if b.get("subtext"):
        last -= 18
        spaced(c, x, last, b["subtext"].upper(), BOLD, 8.5, 1.4, CORAL)
    c.setFillColor(CORAL)
    c.rect(MARGIN, last - 5, 3, first + 13 - (last - 5), stroke=0, fill=1)
    return last - 7


def block_nav(c, b, y, flex, registry):
    row_h = 46 + flex
    text_x = MARGIN + NUM_COL
    right = PAGE_W - MARGIN
    action = b.get("action_label", "Open Guide").upper()
    pending = b.get("pending_label", "Coming Soon").upper()
    hairline(c, y)
    for item in b["items"]:
        top, bottom = y, y - row_h
        mid = (top + bottom) / 2
        url = resolve(registry, item.get("resource"))
        if url:
            c.setFillColor(TINT)
            c.roundRect(MARGIN - 8, bottom + 3, CONTENT_W + 16, row_h - 6, 6, stroke=0, fill=1)
        if item.get("number"):
            c.setFillColor(CORAL)
            c.setFont(BOLD, 13)
            c.drawString(MARGIN, mid - 9, item["number"])
        spaced(c, text_x, mid + 5, item["label"].upper(), BOLD, 8, 1.3, MUTED)
        c.setFillColor(INK)
        c.setFont(BOLD, 13.5)
        c.drawString(text_x, mid - 9, item["title"])
        if url:
            spaced(c, right - 14, mid - 4, action, BOLD, 9, 1.3, CORAL, align="right")
            c.setStrokeColor(CORAL)
            c.setLineWidth(1.4)
            c.setLineCap(1)
            c.setLineJoin(1)
            c.lines([(right - 6, mid + 0.5, right - 2.5, mid - 3), (right - 2.5, mid - 3, right - 6, mid - 6.5)])
            c.linkURL(url, (MARGIN - 8, bottom + 3, right + 8, top - 3), relative=0, thickness=0)
        else:
            spaced(c, right, mid - 4, pending, BODY, 8.5, 1.3, MUTED, align="right")
        hairline(c, bottom)
        y = bottom
    return y - 2


BLOCKS = {
    "lede": block_lede,
    "paragraphs": block_paragraphs,
    "list": block_list,
    "callout": block_callout,
}


def resolve(registry: dict, resource_id: str | None) -> str | None:
    if not resource_id:
        return None
    entry = registry.get(resource_id)
    if not entry:
        raise SystemExit(f"Unknown resource ID in navigation: {resource_id}")
    url = entry.get("url") or entry.get("destination") or ""
    if entry.get("status") in LINKABLE and url.startswith("https://"):
        return url
    return None


# ---------------------------------------------------------------- page

def draw_header(c, page) -> float:
    size = 84
    x, y = MARGIN - 6, PAGE_H - 48 - size
    if page.get("mark", "crest") == "logo":
        c.drawImage(ImageReader(str(ASSETS / "little-chewz-logo.png")), x, y, size, size, mask="auto")
    else:
        c.drawImage(ImageReader(str(ASSETS / "crest.png")), x, y, size, size, mask="auto")
        c.setStrokeColor(CREST_RING)
        c.setLineWidth(2.2)
        c.circle(x + size / 2, y + size / 2, size / 2 - 0.6, stroke=1, fill=0)

    tx = x + size + 22
    avail = PAGE_W - MARGIN - tx
    spaced(c, tx, y + 56, page.get("eyebrow", "").upper(), BOLD, 9.5, 1.6, CORAL)
    title = page["title"].upper()
    fs = 34.0
    while width(title, HEADLINE, fs) > avail and fs > 20:
        fs -= 1
    c.setFillColor(INK)
    c.setFont(HEADLINE, fs)
    c.drawString(tx, y + 18, title)

    rule = y - 26
    c.setStrokeColor(BROWN)
    c.setLineWidth(0.8)
    c.line(MARGIN, rule, PAGE_W - MARGIN, rule)
    return rule


def draw_footer(c, doc, number: int) -> None:
    hairline(c, 54)
    spaced(c, MARGIN, 38, doc.get("footer", ""), BODY, 8.5, 1.2, BROWN)
    spaced(c, PAGE_W - MARGIN, 38, str(number), BOLD, 9, 0, BROWN, align="right")


def draw_blocks(c, page, top, flex, registry) -> float:
    y = top - 26 - flex
    for i, b in enumerate(page["blocks"]):
        if i:
            y -= 22 + flex
        if b["type"] == "nav":
            y = block_nav(c, b, y, flex, registry)
        elif b["type"] in BLOCKS:
            y = BLOCKS[b["type"]](c, b, y, flex)
        else:
            raise SystemExit(f"Unknown block type: {b['type']}")
    return y


def fit_flex(page, top, registry) -> float:
    """Pick the extra gap that spreads the blocks down to BOTTOM (capped)."""
    def bottom_at(flex):
        scratch = canvas.Canvas(io.BytesIO(), pagesize=(PAGE_W, PAGE_H))
        return draw_blocks(scratch, page, top, flex, registry)

    b0, b1 = bottom_at(0), bottom_at(1)
    if b0 < BOTTOM:
        raise SystemExit(f"Page '{page['title']}' overflows by {BOTTOM - b0:.0f}pt")
    per_unit = b0 - b1
    return min((b0 - BOTTOM) / per_unit, page.get("max_flex", 24)) if per_unit > 0 else 0


def render(doc_path: Path, output: Path) -> Path:
    from pypdf import PdfReader, PdfWriter

    register_fonts()
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    body = io.BytesIO()
    c = canvas.Canvas(body, pagesize=(PAGE_W, PAGE_H))
    first_number = 2 if doc.get("cover") else 1
    for n, page in enumerate(doc["pages"], start=first_number):
        c.setFillColor(CREAM)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        top = draw_header(c, page)
        draw_blocks(c, page, top, fit_flex(page, top, registry), registry)
        draw_footer(c, doc, n)
        c.showPage()
    c.save()

    writer = PdfWriter()
    if doc.get("cover"):
        writer.append(PdfReader(str(doc_path.parent / doc["cover"])))
    writer.append(PdfReader(io.BytesIO(body.getvalue())))
    writer.add_metadata({"/Title": doc.get("title", ""), "/Author": "Little Chewz"})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as fh:
        writer.write(fh)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a claude-style Little Chewz PDF.")
    parser.add_argument("document", type=Path, help="document JSON (see TEMPLATE.json)")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    out = args.output or Path("exports") / f"{args.document.stem}.pdf"
    print(render(args.document, out))


if __name__ == "__main__":
    main()
