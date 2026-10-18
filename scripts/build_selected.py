#!/usr/bin/env python3
"""Render and verify the exact PDFs selected by select_builds.py."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import fitz
from select_builds import ROOT, SOURCES, GUIDE

OUT = ROOT / "exports"


def render(manifest):
    names = manifest["outputs"]
    if set(names) - set(SOURCES):
        raise ValueError(f"Unknown outputs: {set(names) - set(SOURCES)}")
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.pdf"):
        old.unlink()  # Avoid stale PDFs appearing in review artifacts.
    for name in names:
        source = ROOT / SOURCES[name]
        output = OUT / name
        if name == GUIDE:
            cmd = [sys.executable, str(ROOT / "scripts/renderers/teacher_guide.py"),
                   "--root", str(ROOT), "--content", str(source),
                   "--output", str(output)]
        else:
            cmd = [sys.executable, str(ROOT / "scripts/renderers/teacher_companion.py"),
                   str(source), "-o", str(output), "--registry",
                   str(ROOT / "catalog/resources.json")]
        subprocess.run(cmd, check=True)
    actual = {p.name for p in OUT.glob("*.pdf")}
    if actual != set(names):
        raise ValueError(f"Expected {set(names)} PDF outputs; found {actual}")
    for name in names:
        file = OUT / name
        with fitz.open(file) as pdf:
            if not pdf.page_count:
                raise ValueError(f"Empty PDF: {name}")
            links = [link for page in pdf for link in page.get_links()]
            for link in links:
                if link["kind"] == fitz.LINK_URI and not link.get("uri", "").startswith("https://"):
                    raise ValueError(f"Invalid external link in {name}: {link}")
            if name == GUIDE and not any(link["kind"] == fitz.LINK_URI for link in links):
                raise ValueError(f"Guide lost resource hyperlinks: {name}")
            print(f"PASS {name}: {pdf.page_count} pages, {len(links)} links, {file.stat().st_size} bytes")
    if not names:
        print("No affected approved PDFs; validation completed without rendering.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    args = p.parse_args()
    render(json.loads(args.manifest.read_text()))
