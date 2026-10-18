#!/usr/bin/env python3
"""Lightweight, flexible Little Chewz teacher-resource PDF generator.

Usage:
    python resource_generator.py songwriting_extension.json
    python resource_generator.py mission_video_questions.json -o MyResource.pdf
    python resource_generator.py resource.json --registry /path/to/Template/resources.json

Requires: pip install reportlab. Uses locally installed Lato fonts when available.
This is a standalone companion generator; it does NOT modify the Teacher Guide.
"""
import argparse
import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether, HRFlowable, Image)

ACCENTS = {
    "activate": "#D96E58",
    "set the table": "#E35C73",
    "secret ingredients": "#9671B4",
    "the showdown": "#D49C20",
    "chew on this": "#70A34E",
    "plate it forward": "#319CBB",
    "celebrate": "#D96E58",
}
PAPER = colors.HexColor("#FEFCFA")
INK = colors.HexColor("#292728")
MUTED = colors.HexColor("#777173")


def fonts():
    root = Path("/usr/share/fonts/truetype/lato")
    if (root / "Lato-Regular.ttf").exists():
        pdfmetrics.registerFont(TTFont("LittleLato", str(root / "Lato-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("LittleLatoBold", str(root / "Lato-Bold.ttf")))
        pdfmetrics.registerFontFamily("LittleLato", normal="LittleLato", bold="LittleLatoBold")
        return "LittleLato", "LittleLatoBold"
    return "Helvetica", "Helvetica-Bold"


def safe(text):
    return html.escape(str(text), quote=False).replace("\n", "<br/>")


def generator(data, output, registry=None):
    reg = fonts()
    normal, bold = reg
    accent = colors.HexColor(data.get("accent") or ACCENTS.get(data.get("section", "").strip().lower(), "#E35C73"))
    styles = {
        "eyebrow": ParagraphStyle("eyebrow", fontName=bold, fontSize=9, leading=13, textColor=accent, spaceAfter=12),
        "title": ParagraphStyle("title", fontName=bold, fontSize=25, leading=30, textColor=INK, spaceAfter=8),
        "time": ParagraphStyle("time", fontName=normal, fontSize=10.3, leading=15, textColor=MUTED, spaceAfter=13),
        "intro": ParagraphStyle("intro", fontName=normal, fontSize=11, leading=17, textColor=INK, spaceAfter=12),
        "body": ParagraphStyle("body", fontName=normal, fontSize=10.5, leading=16.5, textColor=INK, spaceAfter=9),
        "heading": ParagraphStyle("heading", fontName=bold, fontSize=12, leading=16, textColor=INK, spaceBefore=16, spaceAfter=8),
        "stepnum": ParagraphStyle("stepnum", fontName=bold, fontSize=12, leading=18, textColor=accent),
        "step": ParagraphStyle("step", fontName=normal, fontSize=10.5, leading=16.5, textColor=INK),
        "question": ParagraphStyle("question", fontName=normal, fontSize=10.5, leading=16.5, textColor=INK),
        "note": ParagraphStyle("note", fontName=normal, fontSize=10, leading=15, textColor=MUTED),
    }
    story = []
    eyebrow = " · ".join(x.upper() for x in (data.get("section"), data.get("eyebrow")) if x)
    story.append(Paragraph(safe(data["title"]), styles["title"]))
    if eyebrow: story.append(Paragraph(safe(eyebrow), styles["eyebrow"]))
    if data.get("time"):story.append(Paragraph(safe(data["time"]), styles["time"]))
    story.append(HRFlowable(width=46, thickness=2.2, color=accent, hAlign="LEFT", spaceBefore=9, spaceAfter=23))
    if data.get("intro"):
        story.append(Paragraph(safe(data["intro"]), styles["intro"]))
        story.append(Spacer(1,9))

    def numbered(items, kind):
        for n, item in enumerate(items, 1):
            marker = Paragraph(f"{n:02d}", styles["stepnum"])
            if isinstance(item, str):content = Paragraph(safe(item), styles["question"])
            else:
                text = safe(item.get("text", ""))
                title = safe(item.get("title", ""))
                content = Paragraph((f"<font name='{bold}'>{title}:</font>  " if title else "") + text, styles["step"])
            table = Table([[marker,content]], colWidths=[35, 460], hAlign="LEFT")
            table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                       ("LEFTPADDING",(0,0),(-1,-1),0),
                                       ("RIGHTPADDING",(0,0),(-1,-1),10),
                                       ("TOPPADDING",(0,0),(-1,-1),2),
                                       ("BOTTOMPADDING",(0,0),(-1,-1),8)]))
            story.append(KeepTogether([table,Spacer(1,10 if kind=="steps" else 6)]))

    for block in data.get("blocks", []):
        typ = block.get("type", "paragraph")
        if typ == "heading": story.append(Paragraph(safe(block["text"]), styles["heading"]))
        elif typ == "paragraph": story.append(Paragraph(safe(block["text"]), styles["body"]))
        elif typ in ("steps", "questions"): numbered(block.get("items", []), typ)
        elif typ == "bullets":
            for item in block.get("items", []):
                story.append(Paragraph("•  " + safe(item), styles["body"]))
        elif typ == "note": story.append(Paragraph(safe(block["text"]), styles["note"]))
        elif typ == "spacer": story.append(Spacer(1, min(40,max(0,float(block.get("points",8))))))
        elif typ == "image":
            path = Path(block["path"])
            if not path.is_absolute():path = Path(data.get("_base", ".")) / path
            if not path.exists():raise FileNotFoundError(path)
            w,h = ImageReader(str(path)).getSize()
            scale = min(1, float(block.get("max_width", 495))/w, float(block.get("max_height",350))/h)
            story.append(Image(str(path), width=w*scale, height=h*scale, hAlign="LEFT"))
            if block.get("caption"):story.append(Paragraph(safe(block["caption"]), styles["note"]))
            story.append(Spacer(1,8))
        elif typ == "links":
            for item in block.get("items", []):
                entry = registry.get(item.get("ref", ""), {}) if registry else {}
                url = item.get("url") or entry.get("url")
                label = item.get("title") or entry.get("title")
                if not url or not label:raise ValueError(f"Missing link URL/title: {item}")
                if not url.startswith("https://"):raise ValueError("Links must be approved HTTPS URLs")
                text = f'<link href="{html.escape(url,quote=True)}" color="{accent.hexval()}"><u>{safe(label)}</u></link>'
                if item.get("description"):text += "  — " + safe(item["description"])
                story.append(Paragraph(text,styles["body"]))
        else: raise ValueError(f"Unsupported block type: {typ}")

    def page_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PAPER)
        canvas.rect(0,0,A4[0],A4[1],stroke=0,fill=1)
        canvas.restoreState()

    doc=SimpleDocTemplate(str(output),pagesize=A4,leftMargin=50,rightMargin=50,
                          topMargin=51,bottomMargin=50,allowSplitting=True,
                          title=data["title"],author="Little Chewz — Draft Resource Generator")
    doc.build(story,onFirstPage=page_background,onLaterPages=page_background)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("content",type=Path)
    parser.add_argument("-o","--output",type=Path)
    parser.add_argument("--registry",type=Path,help="Optional approved resources.json")
    args=parser.parse_args()
    data=json.loads(args.content.read_text(encoding="utf-8"))
    data["_base"]=str(args.content.resolve().parent)
    registry=json.loads(args.registry.read_text()) if args.registry else {}
    output=args.output or args.content.with_suffix(".pdf")
    generator(data,output,registry)
    print(output)

if __name__=="__main__": main()
