#!/usr/bin/env python3
"""Local, dependency-free structural validation; not editorial signoff."""
from pathlib import Path
import sys

from validation.runner import run


def main():
    try:
        ctx, lesson_count, companion_count = run(Path(__file__).resolve().parents[1])
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Validated {len(ctx.registry)} registry links; {lesson_count} editable lesson; "
          f"{companion_count} companion sources")
    for message in ctx.warnings:
        print("WARN:", message)
    for message in ctx.errors:
        print("ERROR:", message)
    print("PASS" if not ctx.errors else "FAILED")
    return bool(ctx.errors)


if __name__ == "__main__":
    sys.exit(main())
