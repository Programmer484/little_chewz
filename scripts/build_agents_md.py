#!/usr/bin/env python3
"""Build the root AGENTS.md: every instruction file in one document.

Coding agents load AGENTS.md automatically (CLAUDE.md imports it), and the same file can
be pasted into an AI chat. The source files stay the single owners of each rule; this
only concatenates them in reading order, demotes their headings one level, and rewrites
relative links to repository-root paths. scripts/validate.py fails while it is stale.

Usage:
    python scripts/build_agents_md.py           # rewrite AGENTS.md
    python scripts/build_agents_md.py --check   # exit 1 if AGENTS.md is stale
"""
from __future__ import annotations

import argparse
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "AGENTS.md"

# Reading order: entry point, ownership, routine, writing guides, specialised procedures.
SOURCES = [
    "system/AI_RULES.md",
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

HEADER = """# Little Chewz: agent instructions

> **Generated file. Do not edit.** Built by `python scripts/build_agents_md.py` from the instruction files below; change a rule in its owning file, then regenerate.
> Repository: https://github.com/Programmer484/little_chewz

You are helping edit the Little Chewz teaching-material repository. This file is the complete, current set of rules, in the order to read them, and can be pasted into any AI chat. Each part is headed by the file that owns it. Paths are relative to the repository root.

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
        return f"[{label}]({resolved}{'#' + anchor if anchor else ''})"

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
    parser.add_argument("--check", action="store_true", help="fail if AGENTS.md is stale")
    args = parser.parse_args()
    expected = render()
    if args.check:
        current = BRIEF.read_text(encoding="utf-8") if BRIEF.is_file() else ""
        if current != expected:
            print("AGENTS.md is stale; run python scripts/build_agents_md.py", file=sys.stderr)
            sys.exit(1)
        print("AGENTS.md is current")
        return
    BRIEF.write_text(expected, encoding="utf-8")
    print(f"Wrote {BRIEF.relative_to(ROOT)} ({len(expected.encode())} bytes)")


if __name__ == "__main__":
    main()
