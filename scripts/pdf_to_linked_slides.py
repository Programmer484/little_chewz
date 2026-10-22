#!/usr/bin/env python3
"""Convert a reviewed PDF into an image-based PPTX, preserving PDF link hotspots.

Requires PyMuPDF, Pillow, python-pptx. Human approval is required separately
before replacing existing Google Drive PDF/PPTX files.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

import fitz
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.action import PP_ACTION_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches


def convert(
    src: Path,
    dst: Path,
    *,
    scale: float = 1.5,
    quality: int = 92,
    allow_unsupported_links: bool = False,
) -> dict:
    """Build a linked PPTX and verify images, link count, and destinations."""
    started = time.perf_counter()
    if scale <= 0 or not 1 <= quality <= 100:
        raise ValueError("Scale must be positive and JPEG quality must be 1..100")
    pdf = fitz.open(src)
    try:
        if not len(pdf):
            raise ValueError("Source PDF has no pages")
        if pdf.needs_pass:
            raise ValueError("Unlock the reviewed PDF before conversion")
        sizes = [page.rect for page in pdf]
        ratio = sizes[0].width / sizes[0].height
        if any(abs(rect.width / rect.height - ratio) > 0.001 for rect in sizes):
            raise ValueError("Mixed-aspect PDF: normalize pages before conversion")

        pptx = Presentation()
        pptx.slide_width = Inches(13.333333)
        pptx.slide_height = round(pptx.slide_width / ratio)
        layout = pptx.slide_layouts[6]
        records = []
        pending_internal = []
        warnings = []
        page_info = []

        for index, page in enumerate(pdf):
            pix = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                colorspace=fitz.csRGB,
                alpha=False,
            )
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=False)
            jpeg = output.getvalue()
            slide = pptx.slides.add_slide(layout)
            slide.shapes.add_picture(
                io.BytesIO(jpeg), 0, 0,
                width=pptx.slide_width, height=pptx.slide_height
            ).name = f"PDF page {index + 1}: image"

            for item_number, link in enumerate(page.get_links(), 1):
                box = link.get("from")
                if box is None:
                    warnings.append(f"Page {index+1}, link {item_number}: no rectangle")
                    continue
                x = max(0.0, box.x0 / page.rect.width)
                y = max(0.0, box.y0 / page.rect.height)
                w = min(box.width / page.rect.width, 1.0 - x)
                h = min(box.height / page.rect.height, 1.0 - y)
                if w <= 0 or h <= 0:
                    warnings.append(f"Page {index+1}, link {item_number}: off-slide rectangle")
                    continue

                kind = link.get("kind")
                uri = link.get("uri")
                target = link.get("page")
                supported_uri = kind == fitz.LINK_URI and bool(uri)
                supported_goto = (
                    kind == fitz.LINK_GOTO
                    and isinstance(target, int)
                    and 0 <= target < len(pdf)
                )
                if not (supported_uri or supported_goto):
                    warnings.append(
                        f"Page {index+1}, link {item_number}: unsupported action {kind}"
                    )
                    continue

                hotspot = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE,
                    int(pptx.slide_width * x),
                    int(pptx.slide_height * y),
                    int(pptx.slide_width * w),
                    int(pptx.slide_height * h),
                )
                hotspot.name = f"PDF link p{index+1} #{item_number}"
                hotspot.fill.solid()
                hotspot.fill.fore_color.rgb = RGBColor(255, 255, 255)
                alpha = OxmlElement("a:alpha")
                alpha.set("val", "0")
                hotspot._element.spPr.solidFill.srgbClr.append(alpha)
                hotspot.line.fill.background()

                if supported_uri:
                    hotspot.click_action.hyperlink.address = uri
                    records.append({"slide": index+1, "type": "URI", "url": uri})
                else:
                    pending_internal.append((hotspot, target))
                    records.append({"slide": index+1, "type": "GOTO", "target": target+1})
            page_info.append({
                "slide": index+1, "pixel_width": pix.width,
                "pixel_height": pix.height, "image_bytes": len(jpeg),
            })

        if warnings and not allow_unsupported_links:
            raise ValueError("Links could not be preserved: " + "; ".join(warnings))
        for hotspot, target in pending_internal:
            hotspot.click_action.target_slide = pptx.slides[target]
        dst.parent.mkdir(parents=True, exist_ok=True)
        pptx.save(dst)
    finally:
        pdf.close()

    # Reopen the saved artifact. Count duplicate URL annotations individually.
    reopened = Presentation(dst)
    if len(reopened.slides) != len(page_info):
        raise RuntimeError("PPTX slide count changed")
    for slide in reopened.slides:
        if sum(shape.shape_type == 13 for shape in slide.shapes) != 1:
            raise RuntimeError("Expected exactly one full-slide image per slide")
    expected_uris = sorted(
        (entry["slide"], entry["url"]) for entry in records
        if entry["type"] == "URI"
    )
    actual_uris = sorted(
        (number, shape.click_action.hyperlink.address)
        for number, slide in enumerate(reopened.slides, 1)
        for shape in slide.shapes
        if shape.click_action.action == PP_ACTION_TYPE.HYPERLINK
    )
    if expected_uris != actual_uris:
        raise RuntimeError("PPTX URI links do not match the PDF")
    loaded_slides = list(reopened.slides)
    expected_gotos = sorted(
        (entry["slide"], entry["target"]) for entry in records
        if entry["type"] == "GOTO"
    )
    actual_gotos = sorted(
        (number, loaded_slides.index(shape.click_action.target_slide) + 1)
        for number, slide in enumerate(reopened.slides, 1)
        for shape in slide.shapes
        if shape.click_action.action == PP_ACTION_TYPE.NAMED_SLIDE
    )
    if expected_gotos != actual_gotos:
        raise RuntimeError("PPTX page links do not match the PDF")
    return {
        "pdf": str(src),
        "pptx": str(dst),
        "slides": len(page_info),
        "links": records,
        "link_count": len(records),
        "warnings": warnings,
        "file_bytes": dst.stat().st_size,
        "verified": True,
        "scale": scale,
        "quality": quality,
        "total_seconds": round(time.perf_counter() - started, 3),
        "pages": page_info,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--scale", type=float, default=1.5)
    parser.add_argument("--quality", type=int, default=92)
    parser.add_argument("--json", type=Path, help="Save a conversion verification report")
    parser.add_argument(
        "--allow-unsupported-links", action="store_true",
        help="Permits dropped links; NEVER use when publishing",
    )
    args = parser.parse_args()
    output = args.output or args.pdf.with_suffix(".pptx")
    result = convert(
        args.pdf, output, scale=args.scale, quality=args.quality,
        allow_unsupported_links=args.allow_unsupported_links,
    )
    if args.json:
        args.json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["warnings"]:
        print("WARNING: links were dropped", file=sys.stderr)


if __name__ == "__main__":
    main()
