#!/usr/bin/env python3
"""Little Chewz teacher-resource PDF generator (shared masthead, tight-column lists).

Usage from the repository root (replace resource.json with the source path):
    python scripts/renderers/teacher_companion.py resource.json -o exports/resource.pdf --registry catalog/resources.json

Requires: pip install reportlab. Uses the bundled Lato in templates/fonts/ and the
school crest in templates/welcome/assets/crest.png.
Before editing: read system/RESOURCE_GUIDELINES.md (presentation rules).
"""
import argparse
import html
import json
from pathlib import Path

from resource_links import resolved_registry
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, PageTemplate,
                                Paragraph, Spacer)

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "templates" / "fonts"
CREST = ROOT / "templates" / "welcome" / "assets" / "crest.png"

# Page and grid: A4 with the Teacher Guide's 44 / 551 pt margins.
PAGE_W, PAGE_H = 595.28, 841.89
L, R = 44.0, 551.0
TEXT_W = R - L
TOP_FIRST, TOP_LATER, BOTTOM = 176.0, 78.0, 64.0   # frame insets from page edges

PAPER = HexColor("#FCFAF7")
INK = HexColor("#1E1F20")
MID = HexColor("#646768")
HAIR = HexColor("#E2DED8")

# One section palette, matching scripts/renderers/teacher_guide.py SECTION_COLOR_HEX.
SECTION_COLOR_HEX = {
    "activate": "#E66654", "p1": "#C6548F", "p2": "#8C5EBD", "p3": "#B0851F",
    "p4": "#59874C", "p5": "#478FB0", "celebrate": "#E66654",
}
STAGE_KEYS = {"00": "activate", "01": "p1", "02": "p2", "03": "p3", "04": "p4", "05": "p5", "06": "celebrate"}

# Resource-type tag shown in the masthead pill. `kind` in the source JSON picks one.
RESOURCE_TAGS = {
    "questions": "QUESTIONS",
    "extension": "EXTENSION",
    "answer_key": "ANSWER KEY",
    "instructions": "INSTRUCTIONS",
    "reference": "REFERENCE",
}

# Tight-column list metrics (spacing study variant A, approved 2026-10-31).
SIZE, LEAD = 10.6, 15.6                       # body type
CAP, DESC = 0.72 * SIZE, 0.22 * SIZE          # Lato cap height and descender
NUM_GAP = 12.0                                # widest number to text column
RULE_GAP = 11.0                               # equal optical space above and below a divider
STEP_GAP = 20.0                               # whitespace between undivided step rows
LABEL_TO_ROW = 18.0                           # group label baseline to first row cap-top


def fonts():
    for weight in ("Regular", "Bold", "Heavy"):
        pdfmetrics.registerFont(TTFont(f"LC-{weight}", str(FONT_DIR / f"Lato-{weight}.ttf")))
    pdfmetrics.registerFontFamily("LC-Regular", normal="LC-Regular", bold="LC-Bold")


def safe(text):
    return html.escape(str(text), quote=False).replace("\n", "<br/>")


def tracked(c, x, y, text, font, size, color, track=1.0, right=False):
    width = pdfmetrics.stringWidth(text, font, size) + track * (len(text) - 1)
    if right:
        x -= width
    c.saveState()
    t = c.beginText(x, y)
    t.setFont(font, size); t.setCharSpace(track); t.setFillColor(color); t.textOut(text)
    c.drawText(t)
    c.restoreState()
    return width


def find_quest(base):
    for folder in [base, *base.parents]:
        candidate = folder / "quest.json"
        if candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"No quest.json above {base}")


def section_info(data):
    """Section label and accent from the companion's `stage`, using quest.json titles."""
    stage = data.get("stage") or ""
    key = STAGE_KEYS.get(stage[:2])
    if not key:
        raise ValueError(f"Companion needs a valid stage (e.g. 01-set-the-table), got {stage!r}")
    quest = find_quest(Path(data.get("_base", ".")))
    lesson = next((l for l in quest["learning_sequence"] if l["folder"] == stage), None)
    if lesson is None:
        raise ValueError(f"Stage {stage} is not in quest.json")
    title = lesson["title"].upper()
    label = title if key in ("activate", "celebrate") else f"PART {int(stage[:2])}  ·  {title}"
    school = quest["school"].upper().replace(" SCHOOL", "")
    quest_line = f"{school}  ·  QUEST {quest['quest_number']:02d}"
    return label, quest_line, HexColor(SECTION_COLOR_HEX[key])


class NumberedRow(Flowable):
    """Number on the margin, text 12 pt after the widest number, shared baseline.

    `separator` is drawn above the row ('rule' or 'space') and dropped when the
    row starts a page, so no divider or gap is ever stranded at a page edge.
    """

    def __init__(self, number, text, accent, title=None, number_width=0, separator=None):
        super().__init__()
        self.number, self.text, self.title, self.accent = number, text, title, accent
        self.text_x = number_width + NUM_GAP
        self.separator = separator
        self.lines = []

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        at_top = getattr(getattr(self, "_frame", None), "_atTop", False)
        self.lead_in = 0 if (at_top or not self.separator) else (2 * RULE_GAP if self.separator == "rule" else STEP_GAP)
        self.lines = simpleSplit(self.text, "LC-Regular", SIZE, avail_w - self.text_x)
        rows = len(self.lines) + (1 if self.title else 0)
        # Body runs from cap-top of the first line to the descender of the last.
        self.body = CAP + (rows - 1) * LEAD + DESC
        self.height = self.lead_in + self.body
        return avail_w, self.height

    def draw(self, c=None):
        c = self.canv
        if self.lead_in and self.separator == "rule":
            c.setStrokeColor(HAIR); c.setLineWidth(0.6)
            c.line(0, self.body + RULE_GAP, self.width_avail, self.body + RULE_GAP)
        base = self.body - CAP
        c.setFont("LC-Bold", SIZE); c.setFillColor(self.accent)
        c.drawString(0, base, self.number)
        if self.title:
            c.setFont("LC-Bold", SIZE); c.setFillColor(INK)
            c.drawString(self.text_x, base, self.title)
            base -= LEAD
        c.setFont("LC-Regular", SIZE); c.setFillColor(INK)
        for line in self.lines:
            c.drawString(self.text_x, base, line)
            base -= LEAD


class GroupLabel(Flowable):
    """Tracked accent caps label, e.g. CORE · CLUE TRACKER PAGE 1."""

    def __init__(self, text, accent):
        super().__init__()
        self.text, self.accent = text.upper().replace(" · ", "  ·  "), accent

    def wrap(self, avail_w, avail_h):
        return avail_w, LABEL_TO_ROW

    def draw(self):
        tracked(self.canv, 0, LABEL_TO_ROW - 0.72 * 8.4, self.text, "LC-Heavy", 8.4, self.accent)


def counted_canvas(header):
    """Canvas class that knows the total page count for the 'n / N' footer."""

    class Counted(rl_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for state in self._pages:
                self.__dict__.update(state)
                header(self, self._pageNumber, total)
                super().showPage()
            super().save()

    return Counted


def generator(data, output, registry=None):
    fonts()
    registry = registry or {}
    label, quest_line, accent = section_info(data)
    kind = data.get("kind")
    if kind not in RESOURCE_TAGS:
        raise ValueError(f"Companion `kind` must be one of {sorted(RESOURCE_TAGS)}, got {kind!r}")
    tag = RESOURCE_TAGS[kind]
    title = data["title"]
    meta = "  ·  ".join(data.get("meta", []))
    if pdfmetrics.stringWidth(title, "LC-Heavy", 26) > TEXT_W:
        raise ValueError(f"Title too long for one line: {title}")

    def paint(c, page, total):
        if page == 1:
            top = PAGE_H - 40
            c.drawImage(str(CREST), L, top - 30, 30, 30, mask="auto")
            tracked(c, L + 40, top - 11, quest_line, "LC-Bold", 7.4, MID, 1.1)
            tracked(c, L + 40, top - 25, label, "LC-Heavy", 8.6, accent, 1.0)
            tag_w = pdfmetrics.stringWidth(tag, "LC-Heavy", 7.6) + 1.0 * (len(tag) - 1)
            c.setStrokeColor(accent); c.setLineWidth(0.9)
            c.roundRect(R - tag_w - 18, top - 27, tag_w + 18, 17, 8.5, stroke=1, fill=0)
            tracked(c, R - 9, top - 21.6, tag, "LC-Heavy", 7.6, accent, 1.0, right=True)
            c.setFont("LC-Heavy", 26); c.setFillColor(INK); c.drawString(L, top - 72, title)
            if meta:
                c.setFont("LC-Regular", 10.2); c.setFillColor(MID); c.drawString(L, top - 92, meta)
            c.setStrokeColor(accent); c.setLineWidth(1.3)
            c.line(L, top - 108, R, top - 108)
        else:
            tracked(c, L, PAGE_H - 40, f"{label}  ·  {title.upper()}", "LC-Heavy", 7.6, accent, 1.0)
            c.setStrokeColor(HAIR); c.setLineWidth(0.6); c.line(L, PAGE_H - 50, R, PAGE_H - 50)
        c.setStrokeColor(HAIR); c.setLineWidth(0.5); c.line(L, 40, R, 40)
        tracked(c, L, 27, "LITTLE CHEWZ  ·  CHEWLANDIA ACADEMY", "LC-Bold", 6.8, MID, 1.0)
        tracked(c, R, 27, f"{page} / {total}", "LC-Bold", 6.8, MID, 1.0, right=True)

    def background(c, doc):
        c.saveState(); c.setFillColor(PAPER); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1); c.restoreState()

    styles = {
        "intro": ParagraphStyle("intro", fontName="LC-Regular", fontSize=11, leading=17, textColor=INK, spaceAfter=18),
        "body": ParagraphStyle("body", fontName="LC-Regular", fontSize=SIZE, leading=LEAD, textColor=INK, spaceAfter=10),
        "note": ParagraphStyle("note", fontName="LC-Regular", fontSize=9.8, leading=14.5, textColor=MID, spaceAfter=10),
    }
    story = []
    if data.get("intro"):
        story.append(Paragraph(safe(data["intro"]), styles["intro"]))

    number = 0

    def numbered(items, divided, start=None):
        nonlocal number
        if start is not None:
            number = int(start) - 1
        last = number + len(items)
        width = pdfmetrics.stringWidth("0" * len(f"{last:02d}"), "LC-Bold", SIZE)
        for i, item in enumerate(items):
            number += 1
            separator = None if i == 0 else ("rule" if divided else "space")
            text, title = (item, None) if isinstance(item, str) else (item.get("text", ""), item.get("title"))
            story.append(NumberedRow(f"{number:02d}", text, accent, title=title,
                                     number_width=width, separator=separator))
        story.append(Spacer(1, 26))

    for block in data.get("blocks", []):
        typ = block.get("type", "paragraph")
        if typ == "heading":
            story.append(GroupLabel(block["text"], accent))
        elif typ == "paragraph":
            story.append(Paragraph(safe(block["text"]), styles["body"]))
        elif typ in ("questions", "answers"):
            numbered(block.get("items", []), divided=True, start=block.get("start"))
        elif typ == "steps":
            numbered(block.get("items", []), divided=False, start=block.get("start"))
        elif typ == "bullets":
            for item in block.get("items", []):
                story.append(Paragraph("•  " + safe(item), styles["body"]))
        elif typ == "note":
            story.append(Paragraph(safe(block["text"]), styles["note"]))
        elif typ == "spacer":
            story.append(Spacer(1, min(40, max(0, float(block.get("points", 8))))))
        elif typ == "image":
            path = Path(block["path"])
            if not path.is_absolute():
                path = Path(data.get("_base", ".")) / path
            if not path.exists():
                raise FileNotFoundError(path)
            w, h = ImageReader(str(path)).getSize()
            scale = min(1, float(block.get("max_width", TEXT_W)) / w, float(block.get("max_height", 350)) / h)
            story.append(Image(str(path), width=w * scale, height=h * scale, hAlign="LEFT"))
            if block.get("caption"):
                story.append(Paragraph(safe(block["caption"]), styles["note"]))
            story.append(Spacer(1, 8))
        elif typ == "links":
            for item in block.get("items", []):
                entry = registry.get(item.get("ref", ""), {})
                url = entry.get("url") if item.get("ref") in registry else item.get("url")
                name = item.get("title") or entry.get("title")
                if not url or not name:
                    raise ValueError(f"Missing link URL/title: {item}")
                if not url.startswith("https://"):
                    raise ValueError("Links must be approved HTTPS URLs")
                text = (f'<link href="{html.escape(url, quote=True)}"><u><font name="LC-Bold">'
                        f'{safe(name)}</font></u></link>')
                if item.get("description"):
                    text += f'<font color="{MID.hexval()}">  — {safe(item["description"])}</font>'
                story.append(Paragraph(text, styles["body"]))
        else:
            raise ValueError(f"Unsupported block type: {typ}")
    while story and isinstance(story[-1], Spacer):
        story.pop()

    doc = BaseDocTemplate(str(output), pagesize=(PAGE_W, PAGE_H), title=title,
                          author="Little Chewz", subject=f"{label} · {tag}")
    first = Frame(L, BOTTOM, TEXT_W, PAGE_H - TOP_FIRST - BOTTOM, id="first",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    later = Frame(L, BOTTOM, TEXT_W, PAGE_H - TOP_LATER - BOTTOM, id="later",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate("first", [first], onPage=background, autoNextPageTemplate="later"),
                          PageTemplate("later", [later], onPage=background)])
    doc.build(story, canvasmaker=counted_canvas(paint))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("content", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--registry", type=Path, help="Optional approved resources.json")
    parser.add_argument("--release", action="store_true", help="Use published-only Drive links")
    args = parser.parse_args()
    data = json.loads(args.content.read_text(encoding="utf-8"))
    data["_base"] = str(args.content.resolve().parent)
    registry = (resolved_registry(json.loads(args.registry.read_text()), release=args.release)
                if args.registry else {})
    output = args.output or args.content.with_suffix(".pdf")
    generator(data, output, registry)
    print(output)


if __name__ == "__main__":
    main()
