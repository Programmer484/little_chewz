#!/usr/bin/env python3
"""Select only existing approved PDF outputs affected by a change.

No slide or worksheet build assumptions. Unknown changes to build infrastructure
fall back to all approved PDFs; unrelated content creates no PDF preview.
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEST = "content/confetti-cake-cottage/quest-01-bake-off-betrayal"
LESSON = f"{QUEST}/lessons/00-activate/lesson.json"
COVER = f"{QUEST}/lessons/00-activate/cover.png"
MISSION = f"{QUEST}/resources/teacher_companion/mission-video-questions.json"
CONFETTI = f"{QUEST}/resources/teacher_companion/confetti-file-questions.json"
SOURCES = {
    "00-activate-teacher-guide.pdf": LESSON,
    "mission-video-questions.pdf": MISSION,
    "confetti-file-questions.pdf": CONFETTI,
}
ALL = set(SOURCES)
GUIDE = "00-activate-teacher-guide.pdf"
COMPANIONS = ALL - {GUIDE}
IGNORED_PREFIX = ("content/", "templates/", "system/")
IGNORED = {".gitignore", "README.md", "START_HERE.md", "MIGRATION_REPORT.md", "SYSTEM_IMPROVEMENTS.md"}


def resource_refs(value):
    if isinstance(value, dict):
        found = {value["ref"]} if isinstance(value.get("ref"), str) else set()
        for entry in value.values():
            found.update(resource_refs(entry))
        return found
    if isinstance(value, list):
        found = set()
        for entry in value:
            found.update(resource_refs(entry))
        return found
    return set()


def changed_registry_ids(base_ref):
    path = "catalog/resources.json"
    try:
        previous = json.loads(subprocess.check_output(
            ["git", "show", f"{base_ref}:{path}"], cwd=ROOT, text=True))
        current = json.loads((ROOT / path).read_text())
    except (OSError, ValueError, subprocess.CalledProcessError):
        return None  # Conservative rebuild if diff cannot be determined.
    return {key for key in set(previous) | set(current)
            if previous.get(key) != current.get(key)}


def select(changed, base_ref=None):
    changed = {p.replace("\\", "/").removeprefix("./") for p in changed}
    selected = set()
    for path in changed:
        if path in (LESSON, COVER):
            selected.add(GUIDE)
        elif path == MISSION:
            selected.add("mission-video-questions.pdf")
        elif path == CONFETTI:
            selected.add("confetti-file-questions.pdf")
        elif path == f"{QUEST}/resources/teacher_companion/songwriting-extension.json":
            continue  # Unapproved draft; never render automatically.
        elif path == "catalog/resources.json":
            ids = changed_registry_ids(base_ref) if base_ref else None
            if ids is None:
                selected.update(ALL)
            else:
                for name, source in SOURCES.items():
                    try:
                        refs = resource_refs(json.loads((ROOT / source).read_text()))
                    except (OSError, ValueError):
                        selected.add(name)  # Validation will catch broken sources.
                        continue
                    if ids & refs:
                        selected.add(name)
        elif path == "scripts/renderers/teacher_guide.py":
            selected.add(GUIDE)
        elif path == "scripts/renderers/teacher_companion.py":
            selected.update(COMPANIONS)
        elif path.startswith("scripts/") or path in ("requirements.txt", ".github/workflows/build-resources.yml"):
            selected.update(ALL)
        elif path == "system/action_labels.json":
            selected.add(GUIDE)
        elif path in IGNORED or path.startswith(IGNORED_PREFIX):
            continue
        else:
            # Unknown file: avoid silently dropping a new build dependency.
            selected.update(ALL)
    return sorted(selected)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--changed", nargs="*", default=[])
    p.add_argument("--base-ref", help="Base Git revision to compare registry entries")
    p.add_argument("--all", action="store_true", help="Rebuild all approved PDFs")
    p.add_argument("--output", type=Path, help="Write JSON selection manifest")
    a = p.parse_args()
    outputs = sorted(ALL) if a.all else select(a.changed, a.base_ref)
    result = {"outputs": outputs, "source_paths": [SOURCES[name] for name in outputs]}
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
