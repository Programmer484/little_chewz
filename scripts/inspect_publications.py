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
from publication_state import has_official_version

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


def diagnostic_line(resource_id: str, url: str, operation: str, exc: Exception) -> str:
    """Retain safe API identifiers, never raw exception bodies or credentials."""
    fields = [f"resource_id={resource_id}", f"operation={operation}",
              f"file_id={drive_id(url) or 'unknown'}",
              f"exception={type(exc).__name__}"]
    status = getattr(getattr(exc, "resp", None), "status", None)
    if isinstance(status, int):
        fields.append(f"http_status={status}")
    # Google HttpError may expose error_details, or a JSON response body.
    details = getattr(exc, "error_details", None)
    reason = None
    if isinstance(details, list) and details:
        reason = details[0].get("reason") if isinstance(details[0], dict) else None
    if not reason:
        body = getattr(exc, "content", b"")
        if isinstance(body, (str, bytes)) and len(body) < 8192:
            try:
                error = json.loads(body).get("error", {})
                reasons = error.get("errors", [])
                reason = (reasons[0].get("reason") if reasons else None) or error.get("status")
            except (ValueError, TypeError, AttributeError, IndexError):
                pass
    if isinstance(reason, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,96}", reason):
        fields.append(f"api_reason={reason}")
    return "\t".join(fields)


def inspect_link(url: str | None, resource: dict, service,
                 diagnostics: list[str] | None = None, resource_id: str = "") -> tuple[str, str]:
    if not url:
        return FAIL, "No published URL"
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return FAIL, "Invalid HTTPS URL"

    # Non-Drive links require explicit human approval of the exact current URL.
    # Every published Drive resource (including externally owned files and slides)
    # must pass live API checks; human review is not a bypass.
    if parsed.hostname not in DRIVE_HOSTS:
        return (PASS, "Human reviewed this URL") if resource.get("human_reviewed_url") == url else (
            REVIEW, "Human review required")

    file_id = drive_id(url)
    if not file_id:
        return FAIL, "Invalid Google Drive file URL"
    if service is None:
        return REVIEW, "Service account unavailable"
    try:
        metadata = service.files().get(
            fileId=file_id, supportsAllDrives=True, fields="id,trashed,md5Checksum").execute()
    except Exception as exc:
        # Drive's 404 can mean either missing or inaccessible to this service account.
        if diagnostics is not None:
            diagnostics.append(diagnostic_line(resource_id, url, "files.get", exc))
        return REVIEW, "Service account cannot access Drive file"
    if metadata.get("id") != file_id or metadata.get("trashed") is True:
        return FAIL, "Wrong Drive file or file in Trash"

    checksum_problem = None
    if resource.get("pdf"):
        approved = (resource["pdf"] or {}).get("approved_md5")
        actual = metadata.get("md5Checksum")
        if not approved:
            checksum_problem = (REVIEW, "Approved PDF checksum not recorded")
        elif not actual:
            checksum_problem = (REVIEW, "Drive did not return PDF checksum")
        elif approved.lower() != str(actual).lower():
            checksum_problem = (FAIL, "Published PDF checksum differs from approved version")
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
                if diagnostics is not None:
                    diagnostics.append(f"resource_id={resource_id}\toperation=permissions.list"
                                       f"\tfile_id={file_id}\tapi_reason=permissions_not_returned")
                return REVIEW, "Drive did not return permission information"
            if any(p.get("type") == "anyone" and p.get("role") in
                   {"reader", "commenter", "writer", "owner"} for p in permissions):
                return checksum_problem or (PASS, "Public sharing enabled")
            token = result.get("nextPageToken")
            if not token:
                return FAIL, "Anyone-with-the-link permission is missing"
    except Exception as exc:
        if diagnostics is not None:
            diagnostics.append(diagnostic_line(resource_id, url, "permissions.list", exc))
        return REVIEW, "Cannot read Drive sharing permissions"


def audit(registry: dict, folders=None, service=None, builder=None,
          source_targets=None, only: str | None = None) -> dict:
    if only and only not in registry:
        raise ValueError("Unknown resource: " + only)
    report = []
    diagnostics: list[str] = []
    credentials_checked = service is not None
    for rid, resource in registry.items():
        if not has_official_version(resource) or (only and rid != only):
            continue
        result = PASS
        issues = []
        for url in links(resource):
            if url and drive_id(url):
                if not credentials_checked:
                    credentials_checked = True
                    try:
                        service = drive_service()
                    except Exception as exc:
                        service = None
                        diagnostics.append(f"resource_id={rid}\toperation=drive_service"
                                           f"\texception={type(exc).__name__}")
            state, reason = inspect_link(url, resource, service, diagnostics, rid)
            if state != PASS:
                issues.append({"status": state, "url": url, "reason": reason})
                result = state
                if state == FAIL:
                    break  # Fail fast for this resource; still report the other resources.
        report.append({"resource_id": rid, "result": result, "issues": issues})
    overall = FAIL if any(r["result"] == FAIL for r in report) else (
        REVIEW if any(r["result"] == REVIEW for r in report) else PASS)
    return {"read_only": True, "result": overall, "resources": report,
            "diagnostics": diagnostics}


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
    # Keep detailed diagnostics in an artifact, not in the console or summary.
    diagnostic_path = args.report.with_suffix(".txt")
    diagnostic_path.write_text(
        "Publication inspection diagnostics (safe API codes only)\n"
        + ("\n".join(result["diagnostics"]) if result["diagnostics"]
           else "No API exceptions recorded.")
        + "\n", encoding="utf-8")
    summary = summary_table(result)
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as out:
            out.write(summary)
    sys.exit(1 if result["result"] == FAIL else 0)


if __name__ == "__main__":
    main()
