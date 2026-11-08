#!/usr/bin/env python3
"""Render a Celebrate Teacher Guide (template: "celebrate").

An end-of-quest guide that reads as an invitation but runs like a lesson. It
shares the Teacher Guide design system (Lato, cream page, coral accent, the
44 / 82 / 129 / 551 pt flow grid, action labels and linked resource lines) and
adds four Celebrate elements:

  confetti band   the six stage colours across the top of every page
  invitation      a Lobster headline and dashed "ticket" card on At a Glance
  party sizes     an S / M / L menu page; matching chips on each step
  finale          "Mission complete" page with the quest badge and last steps

Pages: optional cover, At a Glance, Choose your size + Preparation, Teaching
Flow (whole steps, as many pages as needed), optional finale.

Before editing: read templates/celebrate/README.md (fields) and
system/EDITORIAL_GUIDE.md (writing and the Teaching Flow grid). Artwork comes
from separate image files, never a pre-rendered page (CONTENT_CONTRACT.md).
Layout values mirror scripts/renderers/teacher_guide.py; keep them in step.

Usage (from the repository root):
    python scripts/renderers/celebrate.py <lesson.json> --output <guide.pdf> [--release]
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resource_links import resolved_registry  # noqa: E402
from notices import CLASSROOM_NOTICE  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
LATO = REPO / 'templates' / 'fonts'
LOBSTER = REPO / 'templates' / 'welcome' / 'assets' / 'fonts' / 'Lobster-Regular.ttf'
STAMP = REPO / 'templates' / 'celebrate' / 'assets' / 'celebrate-stamp.png'
LOGO = REPO / 'templates' / 'welcome' / 'assets' / 'little-chewz-logo.png'
ACTIONS = REPO / 'system' / 'action_labels.json'

W, H = 595.28, 841.89
L, R = 44., 551.
PAGE_W = R - L
GUTTER = 40.
COL_W = (PAGE_W - GUTTER) / 2
COL2_X = L + COL_W + GUTTER


def rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


BG = (.988, .981, .971); BLACK = (.118, .122, .126); MID = (.39, .40, .405); SOFT = (.77, .77, .77)
ACCENT = rgb('#E66654'); TINT = rgb('#FAECE7'); TINT_TEXT = rgb('#712B13')
# Stage order and colours from teacher_guide.py SECTION_COLOR_HEX (activate, p1–p5).
STAGES = [rgb(x) for x in ('#E66654', '#C6548F', '#8C5EBD', '#B0851F', '#59874C', '#478FB0')]
BAND_H = 6.

CAP = .7165; BOX_MID = .387
COL_NUM, COL_ACT, COL_TXT = L, 82., 129.
GAP, OV_GAP = 24., 27.
HDR_EYEBROW, HDR_TITLE, HDR_RULE = 38., 70., 88.
SEC_SIZE, BAR_W = 13.4, 28.
BODY, BODY_LH = 11.2, 17.2
FLOW_BODY, FLOW_ASK, FLOW_LH = 10.9, 11.2, 16.
ROW_STEP, LABEL_SIZE = 25., 8.9
STEP_NUM, STEP_TITLE, STEP_TITLE_LH = 17.5, 15.5, 19.
TIME_SIZE = 9.2
CHIP_R, CHIP_STEP = 6.6, 16.5
FLOW_FIRST_CAP, FLOW_LIMIT, CUE_BASELINE, PAGE_LIMIT = HDR_RULE + 30., 772., 800., 806.
NOTICE_BASELINE = 821.


class LayoutError(ValueError):
    pass


def register_fonts():
    for key, name in {'regular': 'Regular', 'semibold': 'Semibold', 'bold': 'Bold',
                      'heavy': 'Heavy', 'italic': 'Italic'}.items():
        pdfmetrics.registerFont(TTFont('CLato-' + key, str(LATO / f'Lato-{name}.ttf')))
    pdfmetrics.registerFont(TTFont('CLobster', str(LOBSTER)))


def font(key):
    return 'CLobster' if key == 'lobster' else 'CLato-' + key


def tw(text, size, key='regular'):
    return pdfmetrics.stringWidth(str(text), font(key), size)


def cap_to_base(cap_top, size):
    return cap_top + size * CAP


def wrap(text, width, size, key='regular'):
    out, line = [], ''
    for word in str(text).split():
        if tw(word, size, key) > width:
            raise LayoutError(f'Unbreakable word exceeds width: {word!r}')
        trial = (line + ' ' + word).strip()
        if tw(trial, size, key) <= width:
            line = trial
        else:
            out.append(line); line = word
    if line:
        out.append(line)
    return out or ['']


class Page:
    """Drawing surface measured from the top; dry pages only measure."""

    def __init__(self, c=None):
        self.c = c

    def text(self, s, x, baseline, size, key='regular', color=BLACK, right=R):
        s = str(s)
        if x + tw(s, size, key) > right + .2:
            raise LayoutError(f'Text exceeds right bound: {s!r}')
        if baseline > PAGE_LIMIT + 10:
            raise LayoutError(f'Text exceeds bottom margin: {s[:60]!r}')
        if self.c:
            self.c.setFillColorRGB(*color); self.c.setFont(font(key), size)
            self.c.drawString(x, H - baseline, s)
        return baseline

    def centred(self, s, baseline, size, key='regular', color=BLACK):
        return self.text(s, (W - tw(s, size, key)) / 2, baseline, size, key, color)

    def lines(self, s, x, baseline, width, size, lh, key='regular', color=BLACK):
        for i, value in enumerate(wrap(s, width, size, key)):
            if i:
                baseline += lh
            self.text(value, x, baseline, size, key, color, x + width)
        return baseline

    def rule(self, y, x=L, x2=R, color=SOFT, thick=.6):
        if self.c:
            self.c.setStrokeColorRGB(*color); self.c.setLineWidth(thick); self.c.line(x, H - y, x2, H - y)

    def vrule(self, x, y1, y2, color=SOFT, thick=.6):
        if self.c:
            self.c.setStrokeColorRGB(*color); self.c.setLineWidth(thick); self.c.line(x, H - y1, x, H - y2)

    def link(self, url, x1, top, x2, bottom):
        if self.c and url:
            self.c.linkURL(url, (x1, H - bottom, x2, H - top), relative=0, thickness=0)

    def chip(self, letter, cx, cy_top, r=CHIP_R, size=8.2):
        if self.c:
            cy = H - cy_top
            self.c.setFillColorRGB(*ACCENT); self.c.circle(cx, cy, r, stroke=0, fill=1)
            self.c.setFillColorRGB(1, 1, 1); self.c.setFont(font('heavy'), size)
            self.c.drawCentredString(cx, cy - size * CAP / 2, letter)

    def image(self, path, x, top, width=None, height=None):
        with Image.open(path) as im:
            iw, ih = im.size
        if width and not height:
            height = width * ih / iw
        if height and not width:
            width = height * iw / ih
        if self.c:
            self.c.drawImage(ImageReader(str(path)), x, H - top - height, width, height, mask='auto')
        return width, height


class Guide:
    def __init__(self, path: Path, registry: dict):
        self.path = path
        self.d = json.loads(path.read_text(encoding='utf-8'))
        self.registry = registry
        self.allowed = set(json.loads(ACTIONS.read_text())['teacher_guide_actions'])
        self.check()
        self.stage = self.d['title'].split(' / ')[0].strip().upper()
        self.labels = [s['label'] for s in self.d['sizes']]
        finale = self.d.get('finale') or {}
        count = int(finale.get('step_count', 0)) if finale else 0
        steps = self.d['steps']
        self.flow_steps, self.finale_steps = steps[:len(steps) - count], steps[len(steps) - count:]

    # -- source checks -----------------------------------------------------
    def check(self):
        d = self.d
        if d.get('template') != 'celebrate':
            raise ValueError(f'{self.path}: expected "template": "celebrate"')
        for field in ('title', 'grade', 'duration', 'print_note', 'invitation', 'goal', 'outcomes',
                      'focus', 'curriculum', 'sizes', 'core', 'steps'):
            if not d.get(field):
                raise ValueError(f'{self.path}: missing {field}')
        labels = [s.get('label') for s in d['sizes']]
        if len(labels) != len(set(labels)) or not all(isinstance(x, str) and len(x) == 1 for x in labels):
            raise ValueError(f'{self.path}: party sizes need unique one-letter labels')
        if [s.get('id') for s in d['steps']] != list(range(1, len(d['steps']) + 1)):
            raise ValueError(f'{self.path}: step IDs must be consecutive from 1')
        for step in d['steps']:
            unknown = set(step.get('sizes', [])) - set(labels)
            if unknown:
                raise ValueError(f'{self.path}: step {step["id"]} names undefined sizes {sorted(unknown)}')
            for row in step.get('rows', []):
                if row.get('kind', '').upper() not in self.allowed:
                    raise ValueError(f'{self.path}: unsupported action label {row.get("kind")!r}')
        finale = d.get('finale')
        if finale:
            count = finale.get('step_count', 0)
            if not isinstance(count, int) or isinstance(count, bool) or not 0 <= count < len(d['steps']):
                raise ValueError(f'{self.path}: finale step_count must leave at least one Teaching Flow step')

    def resolve(self, item):
        ref = item['ref']
        if ref not in self.registry:
            raise ValueError(f'{self.path}: unknown resource {ref}')
        rec = self.registry[ref]
        if not rec.get('title'):
            raise ValueError(f'{self.path}: resource {ref} has no title')
        return rec['title'], rec.get('url')

    def asset(self, value):
        path = (self.path.parent / value).resolve()
        if not path.is_file():
            raise FileNotFoundError(f'{self.path}: missing image {value}')
        return path

    # -- shared pieces -----------------------------------------------------
    def frame(self, p, number, total, eyebrow=None, title=None):
        if p.c:
            p.c.setFillColorRGB(*BG); p.c.rect(0, 0, W, H, stroke=0, fill=1)
            seg = W / len(STAGES)
            for i, colour in enumerate(STAGES):
                p.c.setFillColorRGB(*colour); p.c.rect(i * seg, H - BAND_H, seg + .5, BAND_H, stroke=0, fill=1)
        counter = f'{number:02d} / {total:02d}'
        p.text(counter, R - tw(counter, 9.1, 'semibold'), HDR_EYEBROW, 9.1, 'semibold', MID)
        if p.c:  # copyright line below PAGE_LIMIT, outside the content area
            p.c.setFillColorRGB(*MID); p.c.setFont(font('regular'), 7.4)
            p.c.drawString(L, H - NOTICE_BASELINE, CLASSROOM_NOTICE)
        if title:
            p.text(eyebrow, L, HDR_EYEBROW, 9.1, 'heavy', MID, R - 60)
            size = min(24., PAGE_W / tw(title, 24., 'heavy') * 24.)
            if size < 16:
                raise LayoutError(f'Header is too long: {title}')
            p.text(title, L, HDR_TITLE, size, 'heavy')
            p.rule(HDR_RULE, color=ACCENT, thick=1.3)

    def section(self, p, title, x, cap_top):
        b = p.text(title, x, cap_to_base(cap_top, SEC_SIZE), SEC_SIZE, 'bold')
        p.rule(b + 7.5, x, x + BAR_W, ACCENT, 2.)
        return b + 7.5 + 15.

    def prose(self, p, title, text, cap_top):
        top = self.section(p, title, L, cap_top)
        return p.lines(text, L, cap_to_base(top, BODY), PAGE_W, BODY, BODY_LH)

    def resource_line(self, p, item, x, b, width, size, desc_size=None):
        name, url = self.resolve(item)
        desc_size = desc_size or size
        name_w = tw(name, size, 'semibold')
        if name_w > width:
            raise LayoutError(f'Resource title too long: {name}')
        p.text(name, x, b, size, 'semibold', BLACK, x + width)
        p.rule(b + 2.2, x, x + name_w, BLACK, .5)
        p.link(url, x, b - size, x + name_w, b + 4)
        desc = item.get('description')
        if not desc:
            return b
        suffix = ' — ' + desc
        if name_w + tw(suffix, desc_size) <= width:
            p.text(suffix, x + name_w, b, desc_size, 'regular', MID, x + width)
            return b
        return p.lines('— ' + desc, x, b + FLOW_LH, width, desc_size, FLOW_LH, color=MID)

    # -- At a Glance -------------------------------------------------------
    def overview(self, p, number, total):
        d = self.d
        self.frame(p, number, total, 'TEACHER GUIDE', f'{self.stage} / AT A GLANCE')
        meta_b = cap_to_base(HDR_RULE + 17, 9.3); x = L
        for i, item in enumerate([f"GRADES {d['grade']}", d['duration'].upper(), d['print_note'].upper()]):
            if i:
                p.vrule(x + 12, meta_b - 9.3 * CAP, meta_b + .6, SOFT, .8); x += 24
            p.text(item, x, meta_b, 9.3, 'bold', MID); x += tw(item, 9.3, 'bold')
        rule = meta_b + 17; p.rule(rule)

        inv = d['invitation']
        head_size = 32.
        hb = p.text(inv['headline'], L, rule + 27 + head_size * .72, head_size, 'lobster', ACCENT)
        top = hb + 16
        card_w = PAGE_W - 120; key_x = L + 16; value_x = L + 86; value_w = L + card_w - 12 - value_x
        b = top + 13 + 10.4 * CAP + 4
        rows = inv.get('rows', [])
        for i, (key, value) in enumerate(rows):
            if i:
                b += 22
            p.text(key, key_x, b, 10.4, 'bold')
            b = p.lines(value, value_x, b, value_w, 10.4, 15.)
        card_h = b - top + 14
        if p.c:
            p.c.setStrokeColorRGB(*ACCENT); p.c.setLineWidth(1.3); p.c.setDash(4, 3)
            p.c.roundRect(L, H - top - card_h, card_w, card_h, 9, stroke=1, fill=0); p.c.setDash()
        stamp = self.asset(inv['stamp']) if inv.get('stamp') else STAMP
        side = min(100., card_h + 28)
        p.image(stamp, R - side, top + card_h / 2 - side / 2, width=side)

        rule = top + card_h + OV_GAP; p.rule(rule)
        b = self.prose(p, 'Learning goal', d['goal'], rule + OV_GAP)
        rule = b + OV_GAP; p.rule(rule)
        top = self.section(p, 'Learning outcomes', L, rule + OV_GAP)
        b = cap_to_base(top, BODY) - FLOW_LH - 9
        for i, value in enumerate(d['outcomes'], 1):
            b += FLOW_LH + 9
            p.text(f'{i:02d}', L, b, 10.4, 'bold', ACCENT)
            b = p.lines(value, L + 26, b, PAGE_W - 26, 10.9, FLOW_LH)
        rule = b + OV_GAP; p.rule(rule)
        b = self.prose(p, 'Teaching focus', d['focus'], rule + OV_GAP)
        rule = b + OV_GAP; p.rule(rule)
        b = self.prose(p, 'Curriculum connections', ' · '.join(d['curriculum']), rule + OV_GAP)
        if b > PAGE_LIMIT:
            raise LayoutError(f'At a Glance exceeds the page at baseline {b:.1f}')

    # -- Choose your size + Preparation -------------------------------------
    def sizes(self, p, number, total):
        d = self.d
        self.frame(p, number, total, 'TEACHER GUIDE', f'{self.stage} / CHOOSE YOUR SIZE')
        b = HDR_RULE
        if d.get('size_intro'):
            b = p.lines(d['size_intro'], L, cap_to_base(HDR_RULE + OV_GAP, BODY), PAGE_W, BODY, BODY_LH)
        else:
            b = HDR_RULE - 22 + 5
        for size in d['sizes']:
            rule = b + 22
            if b > HDR_RULE:
                p.rule(rule)
            tb = cap_to_base(rule + 22, 14.)
            cy = tb - 14 * BOX_MID + 1.4
            p.chip(size['label'], L + 13, cy, r=13, size=13)
            time = size.get('time', '')
            p.text(size['title'], COL_ACT, tb, 14., 'bold', BLACK, R - tw(time, TIME_SIZE, 'bold') - 12)
            if time:
                p.text(time, R - tw(time, TIME_SIZE, 'bold'), tb, TIME_SIZE, 'bold', MID)
            steps = size.get('steps', '')
            steps_w = tw(steps, 10.4) + 16 if steps else 0
            b = p.lines(size.get('text', ''), COL_ACT, tb + 19, R - COL_ACT - steps_w, 10.9, FLOW_LH)
            if steps:
                p.text(steps, R - tw(steps, 10.4), tb + 19, 10.4, 'regular', MID)
        if d.get('size_tip'):
            tip_top = b + 22
            lines = wrap(d['size_tip'], PAGE_W - 28, 10.6, 'semibold')
            tip_h = 16 + 15 * len(lines)
            if p.c:
                p.c.setFillColorRGB(*TINT); p.c.roundRect(L, H - tip_top - tip_h, PAGE_W, tip_h, 7, stroke=0, fill=1)
            tb = tip_top + 8 + 10.6 * CAP + 2
            p.lines(d['size_tip'], L + 14, tb, PAGE_W - 28, 10.6, 15., 'semibold', TINT_TEXT)
            b = tip_top + tip_h - 22 + 5

        rule = b + 22 + OV_GAP - 5; p.rule(rule)
        top = self.section(p, 'Preparation', L, rule + OV_GAP)
        bottoms = []
        columns = [(L, 'CORE RESOURCES', d['core'])]
        if d.get('optional_prep'):
            columns.append((COL2_X, d.get('prep_heading') or 'PREPARE YOUR CHOICES', d['optional_prep']))
        for x, heading, items in columns:
            rb = p.text(heading, x, cap_to_base(top, LABEL_SIZE), LABEL_SIZE, 'heavy', MID)
            for item in items:
                rb = self.resource_line(p, item, x, rb + 19, COL_W, 10.4, 9.6)
            bottoms.append(rb)
        bottom = max(bottoms) + OV_GAP
        if len(columns) == 2:
            p.vrule(L + COL_W + GUTTER / 2, top - 4, bottom - 6)
        p.rule(bottom)

        art = d.get('spot_art') or {}
        images = [self.asset(x) for x in art.get('images', [])]
        if images:
            height, gap = float(art.get('height', 92)), 18.
            widths = []
            for path in images:
                with Image.open(path) as im:
                    widths.append(im.size[0] * height / im.size[1])
            total_w = sum(widths) + gap * (len(images) - 1)
            scale = min(1., (PAGE_W - 40) / total_w)
            top = bottom + 30; x = L + (PAGE_W - total_w * scale) / 2
            for path, width in zip(images, widths):
                p.image(path, x, top, width * scale, height * scale); x += (width + gap) * scale
            bottom = top + height * scale
            if art.get('caption'):
                bottom = p.centred(art['caption'], bottom + 20, 9.6, 'italic', MID)
        if bottom > PAGE_LIMIT:
            raise LayoutError(f'Choose your size exceeds the page at {bottom:.1f}')

    # -- Teaching Flow -----------------------------------------------------
    def draw_row(self, p, row, b):
        kind = row['kind'].upper()
        p.text(kind, COL_ACT, b, LABEL_SIZE, 'heavy', ACCENT)
        width = R - COL_TXT
        if row.get('links') is not None:
            for i, item in enumerate(row['links']):
                if i:
                    b += FLOW_LH + 5
                b = self.resource_line(p, item, COL_TXT, b, width, FLOW_BODY)
            return b
        if row.get('ref'):
            return self.resource_line(p, row, COL_TXT, b, width, FLOW_BODY)
        ask = kind == 'ASK'
        return p.lines(row.get('text', ''), COL_TXT, b, width, FLOW_ASK if ask else FLOW_BODY,
                       FLOW_LH, 'semibold' if ask else 'regular')

    def draw_step(self, p, step, cap_top):
        value = str(step['mins']); time = value if value.upper() == 'OPTIONAL' else value + ' MIN'
        time_w = tw(time, TIME_SIZE, 'bold')
        b = cap_to_base(cap_top, STEP_TITLE)
        p.text(f"{step['id']:02d}", COL_NUM, b + (STEP_NUM - STEP_TITLE) * BOX_MID, STEP_NUM, 'heavy', ACCENT)
        p.text(time, R - time_w, b, TIME_SIZE, 'bold', MID)
        x = R - time_w - 14 - CHIP_R
        cy = b - STEP_TITLE * BOX_MID + 1.2
        for letter in reversed(self.labels):
            if letter in step.get('sizes', []):
                p.chip(letter, x, cy)
            x -= CHIP_STEP
        title_x = COL_NUM + max(tw(f'{i:02d}', STEP_NUM, 'heavy') for i in range(100)) + 7.5
        title_w = R - time_w - 14 - CHIP_STEP * len(self.labels) - 6 - title_x
        for i, value in enumerate(wrap(step['title'], title_w, STEP_TITLE, 'bold')):
            p.text(value, title_x, b + i * STEP_TITLE_LH, STEP_TITLE, 'bold', BLACK, title_x + title_w)
        b += i * STEP_TITLE_LH
        for n, row in enumerate(step.get('rows', [])):
            b = self.draw_row(p, row, b + (28 if n == 0 else ROW_STEP))
        return b

    def paginate(self):
        pages, current, used = [], [], None
        for step in self.flow_steps:
            height = self.draw_step(Page(), step, 0)
            if FLOW_FIRST_CAP + height > FLOW_LIMIT:
                raise LayoutError(f'Step {step["id"]} is too long for one page')
            need = FLOW_FIRST_CAP + height if used is None else used + 2 * GAP + 2 + height
            if used is not None and need > FLOW_LIMIT:
                pages.append(current); current, need = [], FLOW_FIRST_CAP + height
            current.append(step); used = need
        pages.append(current)
        return pages

    def flow(self, p, steps, number, total, more):
        self.frame(p, number, total, self.stage, 'Teaching Flow')
        last = None
        for step in steps:
            if last is None:
                cap = FLOW_FIRST_CAP
            else:
                rule = last + GAP + 2; p.rule(rule); cap = rule + GAP
            last = self.draw_step(p, step, cap)
        if more:
            cue = 'CONTINUED ON NEXT PAGE  →'
            p.text(cue, R - tw(cue, 9., 'semibold'), CUE_BASELINE, 9., 'semibold', MID)

    # -- Finale ------------------------------------------------------------
    def finale(self, p, number, total):
        f = self.d['finale']
        self.frame(p, number, total)
        b = p.centred(f.get('headline', 'Mission complete'), 118, 44, 'lobster', ACCENT)
        if f.get('kicker'):
            b = p.centred(f['kicker'].upper(), b + 28, 9.3, 'bold', MID)
        if f.get('badge'):
            size = float(f.get('badge_size', 158))
            p.image(self.asset(f['badge']), (W - size) / 2, b + 22, width=size)
            b += 22 + size + 11
        if f.get('line'):
            b += 23
            for value in wrap(f['line'], 330, 12.5, 'italic'):
                p.centred(value, b, 12.5, 'italic'); b += 19
            b -= 19
        last = b + 6
        for step in self.finale_steps:
            rule = last + GAP + 2; p.rule(rule)
            last = self.draw_step(p, step, rule + GAP)
        with Image.open(LOGO) as im:
            lw, lh = im.size
        logo_h, logo_top = 46., 762.
        if last + 20 > logo_top:
            raise LayoutError(f'Finale content reaches the logo at {last:.1f}; move a step back to Teaching Flow')
        p.image(LOGO, (W - lw * logo_h / lh) / 2, logo_top, height=logo_h)

    # -- document ----------------------------------------------------------
    def render(self, output: Path):
        register_fonts()
        flow_pages = self.paginate()
        cover = self.d.get('cover')
        first = 2 if cover else 1
        total = first - 1 + 2 + len(flow_pages) + (1 if self.d.get('finale') else 0)
        body = io.BytesIO()
        c = canvas.Canvas(body, pagesize=(W, H), invariant=1)
        c.setTitle('Little Chewz | ' + self.d['title']); c.setAuthor('Little Chewz')
        n = first
        self.overview(Page(c), n, total); c.showPage(); n += 1
        self.sizes(Page(c), n, total); c.showPage(); n += 1
        for i, steps in enumerate(flow_pages):
            self.flow(Page(c), steps, n, total, i < len(flow_pages) - 1); c.showPage(); n += 1
        if self.d.get('finale'):
            self.finale(Page(c), n, total); c.showPage()
        c.save()

        writer = PdfWriter()
        if cover:
            writer.append(PdfReader(str(self.asset(cover))), pages=(0, 1))
        writer.append(PdfReader(io.BytesIO(body.getvalue())))
        writer.add_metadata({'/Title': 'Little Chewz | ' + self.d['title'], '/Author': 'Little Chewz'})
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('wb') as fh:
            writer.write(fh)
        return output, total


def main():
    ap = argparse.ArgumentParser(description='Render a Celebrate Teacher Guide PDF.')
    ap.add_argument('document', type=Path, help='lesson JSON following templates/celebrate/TEMPLATE.json')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--root', type=Path, default=REPO)
    ap.add_argument('--release', action='store_true', help='Use published-only links')
    args = ap.parse_args()
    raw = json.loads((args.root / 'catalog/resources.json').read_text(encoding='utf-8'))
    registry = resolved_registry(raw, release=args.release)
    out, pages = Guide(args.document.resolve(), registry).render(args.output)
    print(out, pages, 'pages')


if __name__ == '__main__':
    main()
