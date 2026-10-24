"""Render the "claude" table-of-contents template.

A minimalist one-page A4 contents page styled to match the Welcome PDF
(Confetti Cake Cottage School): cream page, brush headline, Glacial
body text, coral accents, and the school crest. Fonts are open-licensed
(SIL OFL) stand-ins for the Canva originals: Sedgwick Ave Display for
Better Faster, Outfit for Glacial Indifference.

Usage (from the repository root):
    python templates/claude/render.py
    python templates/claude/render.py --data path/to/toc.json --output /tmp/toc.pdf
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

# Page matches the Welcome PDF exactly (Canva A4).
PAGE_W, PAGE_H = 595.5, 842.25
MARGIN = 56
FOOTER_TOP = 130  # entries stay above this line


def rgb(r: int, g: int, b: int) -> Color:
    return Color(r / 255, g / 255, b / 255)


# Palette sampled from the Welcome PDF.
CREAM = rgb(250, 245, 239)
INK = rgb(28, 24, 22)
BROWN = rgb(112, 82, 52)
MUTED = rgb(110, 96, 84)
CORAL = rgb(238, 128, 96)
HAIRLINE = rgb(226, 214, 200)
CREST_RING = rgb(0, 59, 49)

HEADLINE = "SedgwickAveDisplay"
BODY = "Outfit"
BODY_BOLD = "Outfit-Bold"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(HEADLINE, str(FONTS / "SedgwickAveDisplay-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BODY, str(FONTS / "Outfit-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BODY_BOLD, str(FONTS / "Outfit-Bold.ttf")))


def spaced_text(c: canvas.Canvas, x: float, y: float, text: str, font: str, size: float,
                spacing: float, color: Color, align: str = "left") -> None:
    width = pdfmetrics.stringWidth(text, font, size) + spacing * (len(text) - 1)
    if align == "center":
        x -= width / 2
    elif align == "right":
        x -= width
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(spacing)
    t.setFillColor(color)
    t.textOut(text)
    t.setCharSpace(0)  # do not leak spacing into later drawString calls
    c.drawText(t)


def wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if pdfmetrics.stringWidth(trial, font, size) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_header(c: canvas.Canvas, data: dict) -> float:
    crest_size = 84
    cx, cy = MARGIN - 6, PAGE_H - 48 - crest_size
    c.drawImage(ImageReader(str(ASSETS / "crest.png")), cx, cy, crest_size, crest_size, mask="auto")
    c.setStrokeColor(CREST_RING)
    c.setLineWidth(2.2)
    c.circle(cx + crest_size / 2, cy + crest_size / 2, crest_size / 2 - 0.6, stroke=1, fill=0)

    text_x = cx + crest_size + 22
    spaced_text(c, text_x, cy + 56, data.get("eyebrow", "").upper(), BODY_BOLD, 9.5, 1.6, CORAL)
    c.setFillColor(INK)
    c.setFont(HEADLINE, 34)
    c.drawString(text_x, cy + 18, data.get("title", "Table of Contents").upper())

    rule_y = cy - 26
    c.setStrokeColor(BROWN)
    c.setLineWidth(0.8)
    c.line(MARGIN, rule_y, PAGE_W - MARGIN, rule_y)
    return rule_y


def draw_entry(c: canvas.Canvas, index: int, entry: dict, top: float, gap: float = 30) -> float:
    num_x, title_x, right_x = MARGIN, MARGIN + 34, PAGE_W - MARGIN
    baseline = top - gap

    c.setFillColor(CORAL)
    c.setFont(BODY_BOLD, 14)
    c.drawString(num_x, baseline, f"{index:02d}")

    title = entry["title"]
    c.setFillColor(INK)
    c.setFont(BODY_BOLD, 14)
    c.drawString(title_x, baseline, title)

    page = entry.get("page")
    if page is not None:
        page_text = str(page)
        c.drawRightString(right_x, baseline, page_text)
        # Dotted leader between title and page number.
        start = title_x + pdfmetrics.stringWidth(title, BODY_BOLD, 14) + 10
        end = right_x - pdfmetrics.stringWidth(page_text, BODY_BOLD, 14) - 10
        if end > start:
            c.setStrokeColor(HAIRLINE)
            c.setLineWidth(1.1)
            c.setLineCap(1)
            c.setDash(0.1, 4.2)
            c.line(start, baseline + 2, end, baseline + 2)
            c.setDash()

    y = baseline - 18
    c.setFillColor(MUTED)
    c.setFont(BODY, 11)
    for line in wrap(entry.get("summary", ""), BODY, 11, right_x - title_x - 16):
        c.drawString(title_x, y, line)
        y -= 15

    parts = entry.get("parts") or []
    if parts:
        y -= 4
        col_w = (right_x - title_x) / 2
        rows = (len(parts) + 1) // 2
        for i, part in enumerate(parts):
            col, row = divmod(i, rows)
            px, py = title_x + col * col_w, y - row * 17
            c.setFillColor(CORAL)
            c.circle(px + 2.5, py + 3.2, 2.1, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont(BODY, 10.5)
            c.drawString(px + 12, py, part)
        y -= rows * 17 - 2

    return y + 15


def draw_footer(c: canvas.Canvas, data: dict) -> None:
    logo = 46
    c.drawImage(ImageReader(str(ASSETS / "little-chewz-logo.png")),
                PAGE_W / 2 - logo / 2, 58, logo, logo, mask="auto")
    spaced_text(c, PAGE_W / 2, 38, data.get("footer", ""), BODY, 9, 1.2, BROWN, align="center")


def render(data: dict, output: Path) -> Path:
    register_fonts()
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=(PAGE_W, PAGE_H))
    c.setTitle(data.get("title", "Table of Contents"))
    c.setAuthor("Little Chewz")

    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    top = draw_header(c, data)
    entries = data.get("entries", [])

    # Measure the entries on a scratch canvas, then spread them evenly
    # between the header rule and the footer.
    scratch = canvas.Canvas(io.BytesIO(), pagesize=(PAGE_W, PAGE_H))
    used = 0.0
    for i, entry in enumerate(entries, start=1):
        used += 1000 - draw_entry(scratch, i, entry, 1000, gap=0)
    first_gap = 34.0
    free = (top - first_gap) - FOOTER_TOP - used
    gap = max(26.0, min(84.0, free / max(len(entries) - 1, 1)))
    leftover = max(0.0, free - gap * (len(entries) - 1))
    first_gap += leftover * 0.4  # sit the block slightly above centre

    y = top - first_gap
    for i, entry in enumerate(entries, start=1):
        y = draw_entry(c, i, entry, y, gap=0)
        if i < len(entries):
            sep = y - gap / 2 + 4
            c.setStrokeColor(HAIRLINE)
            c.setLineWidth(0.6)
            c.line(MARGIN, sep, PAGE_W - MARGIN, sep)
            y -= gap

    draw_footer(c, data)
    c.showPage()
    c.save()
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=HERE / "TEMPLATE.json")
    parser.add_argument("--output", type=Path, default=Path("exports/claude-table-of-contents.pdf"))
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    print(render(data, args.output))


if __name__ == "__main__":
    main()
