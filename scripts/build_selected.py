#!/usr/bin/env python3
"""Render and verify the exact PDFs selected by select_builds.py."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import fitz
from select_builds import ROOT, targets

OUT = ROOT / "exports"


def render(manifest, release=False):
    names = manifest["outputs"]
    registered = targets()
    if set(names) - set(registered):
        raise ValueError(f"Unknown outputs: {set(names) - set(registered)}")
    if release:
        from publication_checks import unpublished_dependencies
        registry = json.loads((ROOT / "catalog/resources.json").read_text())
        for name in names:
            rid = registered[name]["resource_id"]
            blocked = unpublished_dependencies(rid, registry, registered)
            if blocked:
                raise ValueError(f"{rid}: unpublished release dependencies: {', '.join(blocked)}")
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.pdf"):
        old.unlink()  # Avoid stale PDFs appearing in review artifacts.
    for name in names:
        source = ROOT / registered[name]["source"]
        output = OUT / name
        if registered[name]["kind"] == "teacher_guide":
            cmd = [sys.executable, str(ROOT / "scripts/renderers/teacher_guide.py"),
                   "--root", str(ROOT), "--content", str(source),
                   "--output", str(output)]
            if release:
                cmd.append("--release")
        elif registered[name]["kind"] == "celebrate":
            cmd = [sys.executable, str(ROOT / "scripts/renderers/celebrate.py"),
                   str(source), "--root", str(ROOT), "--output", str(output)]
            if release:
                cmd.append("--release")
        elif registered[name]["kind"] == "teacher_companion":
            cmd = [sys.executable, str(ROOT / "scripts/renderers/teacher_companion.py"),
                   str(source), "-o", str(output), "--registry",
                   str(ROOT / "catalog/resources.json")]
            if release:
                cmd.append("--release")
        else:  # Registry-built document; renderer named by its `build.renderer`.
            cmd = [sys.executable, str(ROOT / f"scripts/renderers/{registered[name]['kind']}.py"),
                   str(source), "--output", str(output)]
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
            if registered[name]["kind"] in ("teacher_guide", "celebrate") and not any(link["kind"] == fitz.LINK_URI for link in links):
                raise ValueError(f"Guide lost resource hyperlinks: {name}")
            print(f"PASS {name}: {pdf.page_count} pages, {len(links)} links, {file.stat().st_size} bytes")
    if not names:
        print("No affected eligible PDFs; validation completed without rendering.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--release", action="store_true", help="Use only verified published resource links")
    args = p.parse_args()
    render(json.loads(args.manifest.read_text()), release=args.release)
