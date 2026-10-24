"""Minimal, one-page Little Chewz navigation PDF. Only links.json requires URL updates.

Usage: python templates/quest_navigation/render.py templates/quest_navigation/links.json output.pdf
"""
import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

SECTIONS = [
    ("Activate", "Before the quest", "activate"),
    ("Set the Table", "Part One", "set-the-table"),
    ("Secret Ingredients", "Part Two", "secret-ingredients"),
    ("The Showdown", "Part Three", "the-showdown"),
    ("Chew On This", "Part Four", "chew-on-this"),
    ("Plate It Forward", "Part Five", "plate-it-forward"),
    ("Celebrate", "After the quest", "celebrate"),
    ("Next Quest or Mission", "Continue the adventure", "next-steps"),
]

def render(data, output):
    width, height = 612, 792
    c = canvas.Canvas(output, pagesize=(width, height), pageCompression=1)
    c.setTitle("Little Chewz — Quest Resources")
    pdfmetrics.registerFont(TTFont("LC", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("LCBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    ink, muted = HexColor("#292725"), HexColor("#746A61")
    hair, accent, paper = HexColor("#E5DED6"), HexColor("#BD7159"), HexColor("#FBF7F2")
    c.setFillColor(paper)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(accent)
    c.setFont("LCBold", 10)
    c.drawCentredString(width/2, 746, "CHEWLANDIA ACADEMY")
    c.setFillColor(ink)
    c.setFont("LCBold", 25)
    c.drawCentredString(width/2, 704, "YOUR QUEST RESOURCES")
    c.setFillColor(muted)
    c.setFont("LC", 11)
    c.drawCentredString(width/2, 681, "Confetti Cake Cottage School  |  Quest One")
    left, right = 49, 563
    for index, (name, stage, key) in enumerate(SECTIONS):
        top = 623 - index*67
        if index == 0:
            c.setFillColor(HexColor("#F6E9E0"))
            c.roundRect(left, top-58, right-left, 60, 8, fill=1, stroke=0)
        c.setFont("LC", 9)
        c.setFillColor(accent if index == 0 else muted)
        c.drawString(left+16, top-18, stage.upper())
        c.setFont("LCBold", 14)
        c.setFillColor(ink)
        c.drawString(left+16, top-40, name)
        url = data.get("links", {}).get(key, "")
        if url:
            if not url.startswith("https://"):
                raise ValueError("Only HTTPS links are allowed: " + key)
            c.setFillColor(accent)
            c.setFont("LCBold", 10)
            c.drawRightString(right-16, top-33, "OPEN GUIDE  >")
            c.linkURL(url, (left, top-57, right, top+1), relative=0, thickness=0)
        else:
            c.setFillColor(muted)
            c.setFont("LC", 9)
            c.drawRightString(right-16, top-33, "COMING SOON")
        c.setStrokeColor(hair)
        c.setLineWidth(.7)
        c.line(left, top-64, right, top-64)
    c.showPage()
    c.save()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python render.py links.json navigation.pdf")
    with open(sys.argv[1], encoding="utf8") as source:
        render(json.load(source), sys.argv[2])
