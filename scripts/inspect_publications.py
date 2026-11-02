#!/usr/bin/env python3
"""Inspect published links without second-guessing source-owned PDF content."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from publish_to_drive import drive_service, load_registry

PASS = "PASS"
FAIL = "FAIL"
REVIEW = "NEEDS REVIEW"
DRIVE_HOSTS = {"drive.google.com", "docs.google.com"}
FILE_ID = re.compile(r"/(?:d|folders)/([A-Za-z0-9_-]{20,})")


def drive_id(url: str) -> str | None:
    parsed = urlsplit(url)
    if parsed.hostname not in DRIVE_HOSTS:
        return None
    match = FILE_ID.search(parsed.path)
    return match.group(1) if match else None


def links(resource: dict) -> list[str]:
    return [resource.get("published_url")]


def inspect_link(url: str | None, resource: dict, service) -> tuple[str, str]:
    if not url:
        return FAIL, "No published URL"
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return FAIL, "Invalid HTTPS URL"

    # Human approval is URL-bound; ordinary Drive links still require public sharing.
    review = (resource.get("human_review") or {}).get(url)
    if resource.get("review_mode") == "human" or parsed.hostname not in DRIVE_HOSTS:
        return (PASS, "Human reviewed this URL") if review == "reviewed" else (
            REVIEW, "Human review required")

    file_id = drive_id(url)
    if not file_id:
        return FAIL, "Invalid Google Drive file URL"
    if service is None:
        return REVIEW, "Service account unavailable"
    try:
        metadata = service.files().get(
            fileId=file_id, supportsAllDrives=True, fields="id,trashed").execute()
    except Exception as exc:
        # Drive's 404 can mean either missing or inaccessible to this service account.
        return REVIEW, "Service account cannot access Drive file"
    if metadata.get("id") != file_id or metadata.get("trashed") is True:
        return FAIL, "Wrong Drive file or file in Trash"

    try:
        token = None
        while True:
            params = {"fileId": file_id, "supportsAllDrives": True,
                      "fields": "nextPageToken,permissions(type,role)", "pageSize": 100}
            if token:
                params["pageToken"] = token
            result = service.permissions().list(**params).execute()
            permissions = result.get("permissions")
            if not isinstance(permissions, list):
                return REVIEW, "Drive did not return permission information"
            if any(p.get("type") == "anyone" and p.get("role") in
                   {"reader", "commenter", "writer", "owner"} for p in permissions):
                return PASS, "Public sharing enabled"
            token = result.get("nextPageToken")
            if not token:
                return FAIL, "Anyone-with-the-link permission is missing"
    except Exception as exc:
        return REVIEW, "Cannot read Drive sharing permissions"


def audit(registry: dict, folders=None, service=None, builder=None,
          source_targets=None, only: str | None = None) -> dict:
    if only and only not in registry:
        raise ValueError("Unknown resource: " + only)
    report = []
    credentials_checked = service is not None
    for rid, resource in registry.items():
        if resource.get("status") != "published" or (only and rid != only):
            continue
        # Classroom slide PPTX files are human approved; linked PDFs remain holding copies.
        if resource.get("type") == "slide_deck":
            continue
        result = PASS
        issues = []
        for url in links(resource):
            if url and drive_id(url) and resource.get("review_mode") != "human":
                if not credentials_checked:
                    credentials_checked = True
                    try:
                        service = drive_service()
                    except Exception:
                        service = None
            state, reason = inspect_link(url, resource, service)
            if state != PASS:
                issues.append({"status": state, "url": url, "reason": reason})
                result = state
                if state == FAIL:
                    break  # Fail fast for this resource; still report the other resources.
        report.append({"resource_id": rid, "result": result, "issues": issues})
    overall = FAIL if any(r["result"] == FAIL for r in report) else (
        REVIEW if any(r["result"] == REVIEW for r in report) else PASS)
    return {"read_only": True, "result": overall, "resources": report}


def summary_table(report: dict) -> str:
    rows = ["| Status | Resource | Link | Reason |", "|---|---|---|---|"]
    for item in report["resources"]:
        for issue in item["issues"]:
            url = issue["url"] or ""
            link = f"[Open resource]({url})" if url.startswith("https://") else "—"
            reason = issue["reason"].replace("|", "\\|").replace("\n", " ")
            rows.append(f"| {issue['status']} | `{item['resource_id']}` | {link} | {reason} |")
    if len(rows) == 2:
        rows.append("| PASS | All published resources | — | No action needed |")
    return "### Publication inspection\n\n" + "\n".join(rows) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-id")
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    result = audit(load_registry(), only=args.resource_id)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    summary = summary_table(result)
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as out:
            out.write(summary)
    sys.exit(1 if result["result"] == FAIL else 0)


if __name__ == "__main__":
    main()
