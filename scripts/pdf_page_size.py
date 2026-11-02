#!/usr/bin/env python3
"""Require US Letter page dimensions for printable PDFs (slides are exempt)."""
from __future__ import annotations

import argparse
from pathlib import Path

import fitz

LETTER = (612.0, 792.0)  # 8.5 x 11 inches at 72 points/inch
TOLERANCE = 1.0  # PDF rounding differences, not scaling to another paper size


def check_letter(data: bytes | Path) -> None:
    """Raise ValueError unless every page is US Letter, portrait or landscape."""
    try:
        if isinstance(data, Path):
            pdf = fitz.open(data)
        else:
            pdf = fitz.open(stream=data, filetype="pdf")
        with pdf:
            if pdf.page_count == 0:
                raise ValueError("PDF has no pages")
            for i, page in enumerate(pdf):
                size = (float(page.mediabox.width), float(page.mediabox.height))
                if not any(all(abs(got - wanted) <= TOLERANCE
                               for got, wanted in zip(size, expected))
                           for expected in (LETTER, LETTER[::-1])):
                    raise ValueError(
                        f"Page {i + 1} is {size[0]:.1f} x {size[1]:.1f} pt; "
                        "expected US Letter (612 x 792 pt, portrait or landscape)")
    except (fitz.FileDataError, fitz.EmptyFileError) as exc:
        raise ValueError("Not a readable PDF") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="+", type=Path, help="PDF(s) to validate before upload")
    args = parser.parse_args()
    for path in args.pdf:
        try:
            check_letter(path)
        except ValueError as exc:
            parser.exit(1, f"FAIL {path}: {exc}\n")
        print(f"PASS {path}: all pages are US Letter")


if __name__ == "__main__":
    main()
