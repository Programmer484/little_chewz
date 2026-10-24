#!/usr/bin/env python3
"""Build AI_BRIEF.md: every instruction file in one document to paste into an AI chat.

The source files stay the single owners of each rule; this only concatenates them in
reading order, demotes their headings one level, and turns relative links into GitHub
links so they still work outside the repository. scripts/validate.py fails while the
brief is stale.

Usage:
    python scripts/build_ai_brief.py           # rewrite AI_BRIEF.md
    python scripts/build_ai_brief.py --check   # exit 1 if AI_BRIEF.md is stale
"""
from __future__ import annotations

import argparse
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "AI_BRIEF.md"
REPO_URL = "https://github.com/Programmer484/little_chewz/blob/main/"

# Reading order: entry point, ownership, routine, writing guides, specialised procedures.
SOURCES = [
    "AGENTS.md",
    "START_HERE.md",
    "system/CONTENT_CONTRACT.md",
    "system/WORKFLOW.md",
    "system/EDITORIAL_GUIDE.md",
    "system/action_labels.json",
    "system/RESOURCE_GUIDELINES.md",
    "templates/claude/README.md",
    "system/SLIDE_CONVERSION.md",
    "system/DRIVE_PUBLISHING.md",
    "system/CHAT_FILE_CREATION.md",
    "SYSTEM_IMPROVEMENTS.md",
    "content/AGENTS.md",
    "catalog/AGENTS.md",
    "templates/AGENTS.md",
    "scripts/AGENTS.md",
    "system/AGENTS.md",
]

HEADER = """# Little Chewz: complete AI brief

> **Generated file. Do not edit.** Built by `scripts/build_ai_brief.py` from the repository's instruction files; edit those and regenerate.
> Repository: https://github.com/Programmer484/little_chewz

You are helping edit the Little Chewz teaching-material repository. Everything below is the full, current set of rules, in the order to read them. Each part is headed by the file that owns it; when you change a rule, change it in that file.

If you cannot read the repository directly, ask the user to paste the exact current file before proposing changes to it, and return complete replacement text for each changed file with its path. Never reconstruct file contents, URLs, statuses, or Drive IDs from memory.

## Contents

"""

LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")


def absolute_links(text: str, source: str) -> str:
    base = posixpath.dirname(source)

    def fix(match: re.Match) -> str:
        label, target = match.groups()
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            return match.group(0)
        path, _, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(base, path))
        return f"[{label}]({REPO_URL}{resolved}{'#' + anchor if anchor else ''})"

    return LINK.sub(fix, text)


def demote_headings(text: str) -> str:
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,5} ", line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def render() -> str:
    parts, contents = [], []
    for source in SOURCES:
        text = (ROOT / source).read_text(encoding="utf-8").strip()
        if source.endswith(".json"):
            text = f"Allowed Teacher Guide action labels and internal row types (data read by the validator):\n\n```json\n{text}\n```"
        else:
            text = demote_headings(absolute_links(text, source))
        contents.append(f"- `{source}`")
        parts.append(f"---\n\n# File: `{source}`\n\n{text}\n")
    return HEADER + "\n".join(contents) + "\n\n" + "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if AI_BRIEF.md is stale")
    args = parser.parse_args()
    expected = render()
    if args.check:
        current = BRIEF.read_text(encoding="utf-8") if BRIEF.is_file() else ""
        if current != expected:
            print("AI_BRIEF.md is stale; run python scripts/build_ai_brief.py", file=sys.stderr)
            sys.exit(1)
        print("AI_BRIEF.md is current")
        return
    BRIEF.write_text(expected, encoding="utf-8")
    print(f"Wrote {BRIEF.relative_to(ROOT)} ({len(expected.encode())} bytes)")


if __name__ == "__main__":
    main()
