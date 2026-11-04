#!/usr/bin/env python3
"""Human-readable GitHub Actions summary for a resource release report."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

FRIENDLY = {
    "Approved PDF checksum not recorded":
        "The linked PDF has no verified baseline. Review the existing file and record its exact Drive checksum.",
    "Cannot read Drive sharing permissions":
        "The publisher can open the file but cannot inspect sharing. Verify viewer access and approve the exact URL.",
    "Published PDF checksum differs from approved version":
        "The live PDF no longer matches its approved version. Review the replacement.",
    "Service account cannot access Drive file":
        "The publisher cannot confirm that this file exists. Check access for the publisher account.",
}

def blocked_rows(resource_id: str, reason: str) -> list[tuple[str, str, str]]:
    """Split dependency failures into independent, actionable table rows."""
    if "pre-publication inspection blocked:" in reason:
        issues = reason.split("pre-publication inspection blocked:", 1)[1].strip()
        rows = []
        for issue in issues.split("; "):
            name, separator, detail = issue.partition(": ")
            if not separator:
                rows.append(("Blocked", resource_id, issue))
                continue
            status, marker, message = detail.partition(" (")
            if not marker:
                rows.append((status, name, detail))
                continue
            message = message.removesuffix(")")
            rows.append((status, name, FRIENDLY.get(message, message)))
        return rows
    return [("Blocked", resource_id, reason)]

def format_report(report: dict) -> str:
    blocked = report.get("blocked", [])
    published = report.get("published", [])
    status = "Blocked" if blocked else "Published" if published else "No publication recorded"
    lines = [f"### Resource release #{report.get('pr', 'unknown')} — {status}", "",
             "| Status | Resource | What happened / next step |",
             "|---|---|---|"]
    for row in published:
        lines.append(f"| Published | {row['resource_id']} | Drive file replaced and verified |")
    for row in blocked:
        reason = explanation(row.get("reason", "Unknown error")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| Blocked | {row.get('resource_id', 'Release')} | {reason} |")
    if not blocked and not published:
        lines.append("| No change | — | No resources were published |")
    lines.extend(["", "**Technical details:** See `release-report.json` in the downloadable workflow artifact.",
                  "A merge alone does not prove Drive publication.", ""])
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    message = format_report(json.loads(args.report.read_text(encoding="utf-8")))
    if args.output:
        args.output.write_text(message, encoding="utf-8")
    print(message)

if __name__ == "__main__":
    main()
