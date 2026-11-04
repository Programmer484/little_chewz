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
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether, PageTemplate,
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
    "overview": "OVERVIEW",
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
TABLE_NOTE_GAP = 3.0                          # `table` space between a row's cells and its note line
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


# `table` block: a calm comparison grid for choosing between lettered options.
# Columns size to their content and share the leftover width as gutters. Row data
# drives every mark, so nothing here is specific to one lesson:
#   "A · Name" first cell   -> accent letter badge and a larger bold name
#   Low / Medium / High     -> three-dot meter, explained once in a key under the table
#   "No" / "None"           -> muted, so the options that need something stand out
#   "encouraged": true      -> ENCOURAGED tag under the name
#   "food": true            -> safety mark after the Food cell, repeated on the callout
#   same "group" as the row above -> badges joined by a line; repeated cells muted
TABLE_LABEL = 7.4                             # column label size (tracked grey caps)
TABLE_HEAD_RULE = 11.0                        # header labels -> hairline -> first row
TABLE_NAME = 12.4                             # option name
TABLE_BADGE = 9.5                             # letter badge radius
TABLE_NAME_X = 2 * TABLE_BADGE + 8            # row name (and its tag) start after the badge
TABLE_NOTE, TABLE_NOTE_LEAD = 10.0, 14.6      # note type, one step below the cells
TABLE_NOTE_DROP = 19.0                        # cell baseline -> first note baseline
TABLE_ROW_GAP = 22.0                          # whitespace between rows; no dividers
TAG = "ENCOURAGED"
TAG_SIZE_T, TAG_TRACK = 6.6, 0.9
LEVELS = {"low": 1, "medium": 2, "high": 3}
MUTED = {"no", "none"}
DOT_R, DOT_STEP = 3.0, 8.6                    # meter dot radius and pitch
METER_W = 2 * DOT_R + 2 * DOT_STEP
MARK_R = 5.2                                  # safety mark radius
MARK_GAP = 6.0


def badge_parts(cell):
    """Split 'A · Design' into ('A', 'Design'); other first cells have no badge."""
    head, sep, rest = str(cell).partition("·")
    head = head.strip()
    return (head, rest.strip()) if sep and len(head) == 1 and rest.strip() else (None, str(cell))


def tag_width():
    return pdfmetrics.stringWidth(TAG, "LC-Heavy", TAG_SIZE_T) + TAG_TRACK * (len(TAG) - 1)


def food_column(columns):
    return next((i for i, c in enumerate(columns) if c.strip().lower() == "food"), None)


def cell_width(i, cell, row, food_col):
    if i == 0:
        letter, name = badge_parts(cell)
        indent = TABLE_NAME_X if letter else 0
        w = pdfmetrics.stringWidth(name, "LC-Bold", TABLE_NAME)
        return indent + max(w, tag_width() if row.get("encouraged") else 0)
    if str(cell).strip().lower() in LEVELS:
        return METER_W
    w = pdfmetrics.stringWidth(str(cell), "LC-Regular", SIZE)
    return w + (MARK_GAP + 2 * MARK_R if i == food_col and row.get("food") else 0)


def table_xs(columns, rows, avail_w):
    """Each column as wide as its widest label or cell; leftover width becomes equal gutters."""
    food_col = food_column(columns)
    widths = []
    for i, name in enumerate(columns):
        label_w = pdfmetrics.stringWidth(name.upper(), "LC-Bold", TABLE_LABEL) + 0.8 * (len(name) - 1)
        if i == 0 and any(badge_parts(r["cells"][0])[0] for r in rows):
            label_w += TABLE_NAME_X
        widths.append(max([label_w] + [cell_width(i, r["cells"][i], r, food_col) for r in rows]))
    gutter = (avail_w - sum(widths)) / max(1, len(widths) - 1)
    if gutter < 10:
        raise ValueError("Table is too wide: shorten its cells or drop a column")
    xs, x = [], 0.0
    for w in widths:
        xs.append(x); x += w + gutter
    return xs


def safety_mark(c, cx, cy, accent):
    """Small filled accent circle with '!': ties food rows to the safety callout."""
    c.setFillColor(accent); c.circle(cx, cy, MARK_R, stroke=0, fill=1)
    c.setFillColor(PAPER); c.setFont("LC-Heavy", 7.6)
    c.drawCentredString(cx, cy - 0.72 * 7.6 / 2, "!")


def meter(c, x, mid, level, accent, muted=False):
    for n in range(3):
        cx = x + DOT_R + n * DOT_STEP
        if n < level:
            c.setFillColor(tint(accent, 0.5) if muted else accent)
            c.circle(cx, mid, DOT_R, stroke=0, fill=1)
        else:
            c.setStrokeColor(tint(accent, 0.45)); c.setLineWidth(0.8)
            c.circle(cx, mid, DOT_R - 0.4, stroke=1, fill=0)


class TableHeader(Flowable):
    """Column labels for a `table` block: tracked grey caps over one hairline."""

    def __init__(self, columns, xs, indent):
        super().__init__()
        self.columns, self.xs, self.indent = columns, xs, indent

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        self.height = 0.72 * TABLE_LABEL + TABLE_HEAD_RULE + 18
        return avail_w, self.height

    def draw(self):
        c = self.canv
        base = self.height - 0.72 * TABLE_LABEL
        for i, (x, name) in enumerate(zip(self.xs, self.columns)):
            x += self.indent if i == 0 else 0
            tracked(c, x, base, name.upper(), "LC-Bold", TABLE_LABEL, MID, 0.8)
        c.setStrokeColor(HAIR); c.setLineWidth(0.6)
        c.line(0, base - TABLE_HEAD_RULE, self.width_avail, base - TABLE_HEAD_RULE)


class TableRow(Flowable):
    """One `table` row: badge and name, comparable cells on the grid, then an optional note."""

    def __init__(self, row, xs, accent, food_col=None, previous=None, following=None, separator=None):
        super().__init__()
        self.row, self.xs, self.accent, self.food_col, self.separator = row, xs, accent, food_col, separator
        group = row.get("group")
        self.join_prev = bool(group and previous and previous.get("group") == group)
        self.join_next = bool(group and following and following.get("group") == group)
        self.prev_cells = previous["cells"] if self.join_prev else None

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        at_top = getattr(getattr(self, "_frame", None), "_atTop", False)
        self.lead_in = 0 if (at_top or not self.separator) else TABLE_ROW_GAP
        self.letter, self.name = badge_parts(self.row["cells"][0])
        note = self.row.get("note")
        self.note_lines = simpleSplit(note, "LC-Regular", TABLE_NOTE, avail_w - self.xs[1]) if note else []
        tag_drop = TABLE_NOTE_DROP if self.row.get("encouraged") else 0
        note_drop = TABLE_NOTE_DROP + (len(self.note_lines) - 1) * TABLE_NOTE_LEAD if self.note_lines else 0
        self.body = 0.72 * TABLE_NAME + max(tag_drop, note_drop, TABLE_BADGE - 0.36 * TABLE_NAME) + DESC
        self.height = self.lead_in + self.body
        return avail_w, self.height

    def draw(self):
        c = self.canv
        cells = self.row["cells"]
        base = self.body - 0.72 * TABLE_NAME
        mid = base + 0.36 * TABLE_NAME
        if self.letter:
            line = tint(self.accent, 0.45)
            c.setStrokeColor(line); c.setLineWidth(1.4)
            if self.join_prev:
                c.line(TABLE_BADGE, mid + TABLE_BADGE, TABLE_BADGE, self.height)
            if self.join_next:
                c.line(TABLE_BADGE, mid - TABLE_BADGE, TABLE_BADGE, 0)
            c.setFillColor(self.accent)
            c.circle(TABLE_BADGE, mid, TABLE_BADGE, stroke=0, fill=1)
            c.setFillColor(PAPER); c.setFont("LC-Heavy", 10)
            c.drawCentredString(TABLE_BADGE, mid - 0.72 * 10 / 2, self.letter)
        name_x = TABLE_NAME_X if self.letter else 0
        c.setFont("LC-Bold", TABLE_NAME); c.setFillColor(INK)
        c.drawString(name_x, base, self.name)
        if self.row.get("encouraged"):
            tracked(c, name_x, base - TABLE_NOTE_DROP, TAG, "LC-Heavy", TAG_SIZE_T, self.accent, TAG_TRACK)
        for i, (x, cell) in enumerate(zip(self.xs[1:], cells[1:]), 1):
            value = str(cell).strip()
            repeated = self.prev_cells is not None and str(self.prev_cells[i]).strip() == value
            level = LEVELS.get(value.lower())
            if level:
                meter(c, x, mid, level, self.accent, muted=repeated)
                continue
            muted = repeated or value.lower() in MUTED
            c.setFont("LC-Regular", SIZE); c.setFillColor(MID if muted else INK)
            c.drawString(x, base, value)
            if i == self.food_col and self.row.get("food"):
                cx = x + pdfmetrics.stringWidth(value, "LC-Regular", SIZE) + MARK_GAP + MARK_R
                safety_mark(c, cx, base + 0.72 * SIZE / 2, self.accent)
        note_base = base - TABLE_NOTE_DROP
        c.setFont("LC-Regular", TABLE_NOTE); c.setFillColor(MID)
        for line in self.note_lines:
            c.drawString(self.xs[1], note_base, line)
            note_base -= TABLE_NOTE_LEAD


class TableKey(Flowable):
    """One quiet line under a table explaining its dot meters and safety mark."""

    def __init__(self, accent, levels, safety):
        super().__init__()
        self.accent, self.levels, self.safety = accent, levels, safety

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        self.height = 20 + 0.72 * 8.4
        return avail_w, self.height

    def draw(self):
        c = self.canv
        size, base = 8.4, 0
        mid = base + 0.72 * size / 2
        parts = []
        if self.levels:
            parts += [("meter", n, word) for n, word in ((1, "Low"), (2, "Medium"), (3, "High"))]
        if self.safety:
            parts.append(("mark", 0, "Involves food: see below"))
        widths = [(METER_W if kind == "meter" else 2 * MARK_R) + 5 + pdfmetrics.stringWidth(word, "LC-Regular", size)
                  for kind, _, word in parts]
        x = self.width_avail - sum(widths) - 16 * (len(parts) - 1)
        for (kind, level, word), w in zip(parts, widths):
            if kind == "meter":
                meter(c, x, mid, level, self.accent); x += METER_W + 5
            else:
                safety_mark(c, x + MARK_R, mid, self.accent); x += 2 * MARK_R + 5
            c.setFont("LC-Regular", size); c.setFillColor(MID); c.drawString(x, base, word)
            x += pdfmetrics.stringWidth(word, "LC-Regular", size) + 16


class Callout(Flowable):
    """Tinted panel with an accent rule on its left: optional bold title, then text."""

    def __init__(self, title, text, accent, marked=False):
        super().__init__()
        self.title, self.text, self.accent, self.marked = title, text, accent, marked

    def wrap(self, avail_w, avail_h):
        self.width_avail = avail_w
        inner = avail_w - 2 * CALLOUT_PAD - 3
        title_w = inner - (2 * MARK_R + 7 if self.marked else 0)
        self.title_lines = simpleSplit(self.title, "LC-Heavy", 14, title_w) if self.title else []
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
        for n, line in enumerate(self.title_lines):
            lx = x
            if self.marked and n == 0:
                safety_mark(c, x + MARK_R, base + 0.72 * 14 / 2, self.accent); lx += 2 * MARK_R + 7
                c.setFillColor(INK)
            c.setFont("LC-Heavy", 14); c.drawString(lx, base, line); base -= 19
        if self.title_lines:
            base += 19 - 17
        for line in self.lines:
            c.setFont("LC-Regular", 11); c.drawString(x, base, line); base -= 16.5


class GroupLabel(Flowable):
    """Tracked accent caps label, e.g. CORE · CLUE TRACKER PAGE 1."""

    def __init__(self, text, accent):
        super().__init__()
        self.text, self.accent = text.upper().replace(" · ", "  ·  "), accent
        self.trim = 0.0  # set when a text paragraph follows, whose first baseline sits lower than a row's

    def wrap(self, avail_w, avail_h):
        return avail_w, LABEL_TO_ROW - self.trim

    def draw(self):
        tracked(self.canv, 0, LABEL_TO_ROW - self.trim - 0.72 * 8.4, self.text, "LC-Heavy", 8.4, self.accent)


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
    table_food = False  # a callout after a table with food rows carries the same safety mark

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
            if story and isinstance(story[-1], GroupLabel):
                story[-1].trim = 0.28 * styles["body"].fontSize  # Paragraph baseline: fontSize below top; rows: cap height
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
            rows = [PairRow(item["term"], item["text"], separator=None if i == 0 else "rule")
                    for i, item in enumerate(block.get("items", []))]
            heading = [story.pop()] if story and isinstance(story[-1], GroupLabel) else []
            # A short table moves to the next page whole, with its heading, rather than splitting.
            if len(rows) <= 6:
                story.append(KeepTogether(heading + rows))
            else:
                story.extend(heading + rows)
            story.append(Gap(1, 26))
        elif typ == "table":
            columns = block.get("columns", [])
            if len(columns) < 2:
                raise ValueError("A table needs at least two columns")
            rows = block.get("rows", [])
            for row in rows:
                if len(row.get("cells", [])) != len(columns):
                    raise ValueError(f"Table row needs {len(columns)} cells: {row}")
            xs = table_xs(columns, rows, TEXT_W)
            food_col = food_column(columns)
            indent = TABLE_NAME_X if any(badge_parts(r["cells"][0])[0] for r in rows) else 0
            heading = [story.pop()] if story and isinstance(story[-1], GroupLabel) else []
            parts = heading + [TableHeader(columns, xs, indent)]
            for i, row in enumerate(rows):
                parts.append(TableRow(row, xs, accent, food_col,
                                      previous=rows[i - 1] if i else None,
                                      following=rows[i + 1] if i + 1 < len(rows) else None,
                                      separator=None if i == 0 else "space"))
            has_levels = any(str(c).strip().lower() in LEVELS for r in rows for c in r["cells"][1:])
            has_food = food_col is not None and any(r.get("food") for r in rows)
            table_food = table_food or has_food
            if has_levels or has_food:
                parts.append(TableKey(accent, has_levels, has_food))
            story.append(KeepTogether(parts))
            story.append(Gap(1, 34))
        elif typ == "callout":
            story.append(Callout(block.get("title"), block.get("text"), accent, marked=table_food))
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
