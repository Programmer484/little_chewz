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
SECTION_GAP = 26.0                            # space above every group label after a block
CHECK_GAP = 9.0                               # whitespace between checklist rows
MARK_W = 12.0                                 # marker column: checklist text aligns with 2-digit numbers
TERM_W = 128.0                                # `pairs` term column; text starts TERM_GAP after it
TERM_GAP = 14.0
TAG_SIZE = 6.8                                # grey tracked-caps tag after a step title
PROMPT_RULE = 1.6                             # accent rule beside teacher prompts
PROMPT_INSET = 11.0                           # prompt text inset from its rule
CALLOUT_PAD = 14.0                            # callout inner padding


def fonts():
    for weight in ("Regular", "Bold", "Heavy", "Italic"):
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
    if data.get("option"):
        label += f"  ·  OPTION {str(data['option']).upper()}"
    school = quest["school"].upper().replace(" SCHOOL", "")
    quest_line = f"{school}  ·  QUEST {quest['quest_number']:02d}"
    return label, quest_line, HexColor(SECTION_COLOR_HEX[key])


def tint(color, amount):
    """Mix a colour into the page paper; amount 0 is paper, 1 is the colour."""
    mix = lambda a, b: a + (b - a) * amount
    return HexColor("#%02X%02X%02X" % tuple(round(255 * mix(getattr(PAPER, ch), getattr(color, ch)))
                                            for ch in ("red", "green", "blue")))


class NumberedRow(Flowable):
    """Number (or checklist marker) on the margin, text 12 pt after the widest number.

    `separator` is drawn above the row ('rule', 'space' or 'tight') and dropped when the
    row starts a page, so no divider or gap is ever stranded at a page edge.
    Timed steps add `mins` (right-aligned on the title line), a grey `tag` after the
    title, and teacher `prompts` set in italics beside a thin accent rule.
    """

    GAPS = {"rule": 2 * RULE_GAP, "space": STEP_GAP, "tight": CHECK_GAP}

    def __init__(self, number, text, accent, title=None, number_width=0, separator=None,
                 marker=None, mins=None, tag=None, prompts=()):
        super().__init__()
        self.number, self.text, self.title, self.accent = number, text, title, accent
        self.marker, self.mins, self.tag, self.prompts = marker, mins, tag, list(prompts)
        self.text_x = number_width + NUM_GAP
        self.separator = separator
        self.lines = []

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        at_top = getattr(getattr(self, "_frame", None), "_atTop", False)
        self.lead_in = 0 if (at_top or not self.separator) else self.GAPS[self.separator]
        text_w = avail_w - self.text_x
        mins_w = pdfmetrics.stringWidth(self.mins, "LC-Bold", SIZE) + 16 if self.mins else 0
        if self.title:
            title_w = pdfmetrics.stringWidth(self.title, "LC-Bold", SIZE)
            tag_w = (pdfmetrics.stringWidth(self.tag.upper(), "LC-Heavy", TAG_SIZE)
                     + 0.9 * (len(self.tag) - 1) + 10) if self.tag else 0
            if title_w + tag_w + mins_w > text_w:
                raise ValueError(f"Step title, tag and time do not fit one line: {self.title}")
        self.lines = simpleSplit(self.text, "LC-Regular", SIZE,
                                 text_w - (0 if self.title else mins_w))
        self.prompt_lines = [simpleSplit(p, "LC-Italic", SIZE, text_w - PROMPT_INSET)
                             for p in self.prompts]
        rows = len(self.lines) + (1 if self.title else 0)
        prompt_rows = sum(len(p) for p in self.prompt_lines)
        # Body runs from cap-top of the first line to the descender of the last.
        self.body = CAP + (rows + prompt_rows - 1) * LEAD + DESC + (6 + 2 * (len(self.prompts) - 1) if self.prompts else 0)
        self.height = self.lead_in + self.body
        return avail_w, self.height

    def draw_marker(self, c, base):
        c.setStrokeColor(self.accent); c.setFillColor(self.accent)
        if self.marker == "box":
            c.setLineWidth(0.9)
            c.rect(0.5, base - 0.6, CAP + 1.4, CAP + 1.4, stroke=1, fill=0)
        elif self.marker == "check":
            c.setLineWidth(1.5); c.setLineCap(1); c.setLineJoin(1)
            p = c.beginPath()
            p.moveTo(0.6, base + CAP * 0.48); p.lineTo(3.6, base + 0.4); p.lineTo(9.0, base + CAP + 0.6)
            c.drawPath(p, stroke=1, fill=0)
        else:
            c.setFont("LC-Bold", SIZE); c.drawString(0, base, self.number)

    def draw(self, c=None):
        c = self.canv
        if self.lead_in and self.separator == "rule":
            c.setStrokeColor(HAIR); c.setLineWidth(0.6)
            c.line(0, self.body + RULE_GAP, self.width_avail, self.body + RULE_GAP)
        base = self.body - CAP
        self.draw_marker(c, base)
        if self.mins:
            c.setFont("LC-Bold", SIZE); c.setFillColor(MID)
            c.drawRightString(self.width_avail, base, self.mins)
        if self.title:
            c.setFont("LC-Bold", SIZE); c.setFillColor(INK)
            c.drawString(self.text_x, base, self.title)
            if self.tag:
                x = self.text_x + pdfmetrics.stringWidth(self.title, "LC-Bold", SIZE) + 10
                tracked(c, x, base + 0.6, self.tag.upper(), "LC-Heavy", TAG_SIZE, MID, 0.9)
            base -= LEAD
        c.setFont("LC-Regular", SIZE); c.setFillColor(INK)
        for line in self.lines:
            c.drawString(self.text_x, base, line)
            base -= LEAD
        if self.prompts:
            base -= 6
            for lines in self.prompt_lines:
                top = base + CAP + 2
                c.setFont("LC-Italic", SIZE); c.setFillColor(INK)
                for line in lines:
                    c.drawString(self.text_x + PROMPT_INSET, base, line)
                    base -= LEAD
                c.setStrokeColor(self.accent); c.setLineWidth(PROMPT_RULE)
                c.line(self.text_x + PROMPT_RULE / 2, top, self.text_x + PROMPT_RULE / 2, base + LEAD - DESC - 1)
                base -= 2


class PairRow(Flowable):
    """Bold term in a fixed left column, explanation beside it; hairline between rows."""

    def __init__(self, term, text, separator=None):
        super().__init__()
        self.term, self.text, self.separator = term, text, separator

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        at_top = getattr(getattr(self, "_frame", None), "_atTop", False)
        self.lead_in = 0 if (at_top or not self.separator) else 2 * RULE_GAP
        self.term_lines = simpleSplit(self.term, "LC-Bold", SIZE, TERM_W)
        self.lines = simpleSplit(self.text, "LC-Regular", SIZE, avail_w - TERM_W - TERM_GAP)
        rows = max(len(self.term_lines), len(self.lines))
        self.body = CAP + (rows - 1) * LEAD + DESC
        self.height = self.lead_in + self.body
        return avail_w, self.height

    def draw(self):
        c = self.canv
        if self.lead_in:
            c.setStrokeColor(HAIR); c.setLineWidth(0.6)
            c.line(0, self.body + RULE_GAP, self.width_avail, self.body + RULE_GAP)
        for x, font, lines in ((0, "LC-Bold", self.term_lines),
                               (TERM_W + TERM_GAP, "LC-Regular", self.lines)):
            base = self.body - CAP
            c.setFont(font, SIZE); c.setFillColor(INK)
            for line in lines:
                c.drawString(x, base, line)
                base -= LEAD


class Callout(Flowable):
    """Tinted panel with an accent rule on its left: optional bold title, then text."""

    def __init__(self, title, text, accent):
        super().__init__()
        self.title, self.text, self.accent = title, text, accent

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        inner = avail_w - 2 * CALLOUT_PAD - 3
        self.title_lines = simpleSplit(self.title, "LC-Heavy", 14, inner) if self.title else []
        self.lines = simpleSplit(self.text, "LC-Regular", 11, inner) if self.text else []
        h = len(self.title_lines) * 19 + len(self.lines) * 16.5
        self.height = 2 * CALLOUT_PAD + h - 6
        return avail_w, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(tint(self.accent, 0.10))
        c.rect(0, 0, self.width_avail, self.height, stroke=0, fill=1)
        c.setFillColor(self.accent)
        c.rect(0, 0, 3, self.height, stroke=0, fill=1)
        x, base = 3 + CALLOUT_PAD, self.height - CALLOUT_PAD - 0.72 * 14
        c.setFillColor(INK)
        for line in self.title_lines:
            c.setFont("LC-Heavy", 14); c.drawString(x, base, line); base -= 19
        if self.title_lines:
            base += 19 - 17
        for line in self.lines:
            c.setFont("LC-Regular", 11); c.drawString(x, base, line); base -= 16.5


class GroupLabel(Flowable):
    """Tracked accent caps label, e.g. CORE · CLUE TRACKER PAGE 1."""

    def __init__(self, text, accent):
        super().__init__()
        self.text, self.accent = text.upper().replace(" · ", "  ·  "), accent

    def wrap(self, avail_w, avail_h):
        return avail_w, LABEL_TO_ROW

    def draw(self):
        tracked(self.canv, 0, LABEL_TO_ROW - 0.72 * 8.4, self.text, "LC-Heavy", 8.4, self.accent)


class Gap(Spacer):
    """Vertical gap that collapses at the top of a frame, so no page starts with blank space."""

    def wrap(self, avail_w, avail_h):
        at_top = getattr(getattr(self, "_frame", None), "_atTop", False)
        return (avail_w, 0) if at_top else super().wrap(avail_w, avail_h)


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
            if isinstance(item, str):
                item = {"text": item}
            story.append(NumberedRow(f"{number:02d}", item.get("text", ""), accent, title=item.get("title"),
                                     number_width=width, separator=separator, mins=item.get("mins"),
                                     tag=item.get("tag"), prompts=item.get("prompts", [])))
        story.append(Gap(1, 26))

    for block in data.get("blocks", []):
        typ = block.get("type", "paragraph")
        if typ == "heading":
            if story and not isinstance(story[-1], Spacer):
                story.append(Gap(1, SECTION_GAP - 10))  # text blocks end with 10 pt; sections sit 26 pt apart
            story.append(GroupLabel(block["text"], accent))
        elif typ == "paragraph":
            story.append(Paragraph(safe(block["text"]), styles["body"]))
        elif typ in ("questions", "answers"):
            numbered(block.get("items", []), divided=True, start=block.get("start"))
        elif typ == "steps":
            numbered(block.get("items", []), divided=False, start=block.get("start"))
        elif typ == "checklist":
            style = block.get("style", "box")
            if style not in ("box", "check"):
                raise ValueError(f"Checklist style must be box or check, got {style!r}")
            for i, item in enumerate(block.get("items", [])):
                story.append(NumberedRow("", item, accent, number_width=MARK_W, marker=style,
                                         separator=None if i == 0 else "tight"))
            story.append(Gap(1, 26))
        elif typ == "pairs":
            for i, item in enumerate(block.get("items", [])):
                story.append(PairRow(item["term"], item["text"], separator=None if i == 0 else "rule"))
            story.append(Gap(1, 26))
        elif typ == "callout":
            story.append(Callout(block.get("title"), block.get("text"), accent))
            story.append(Gap(1, 24))
        elif typ == "bullets":
            for item in block.get("items", []):
                story.append(Paragraph("•  " + safe(item), styles["body"]))
        elif typ == "note":
            story.append(Paragraph(safe(block["text"]), styles["note"]))
        elif typ == "spacer":
            story.append(Gap(1, min(40, max(0, float(block.get("points", 8))))))
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
            story.append(Gap(1, 8))
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
