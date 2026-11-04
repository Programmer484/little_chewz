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


def unknown_sharing(resource: dict, url: str, checksum_problem) -> tuple[str, str]:
    """Existence is verified; permission visibility is unknown, not private.

    Human approval is tied to the exact official URL and cannot suppress a
    detected checksum problem. Confirmed private results never reach here.
    """
    if checksum_problem:
        return checksum_problem
    if resource.get("human_reviewed_url") == url:
        return PASS, "Sharing manually approved for this exact Drive link"
    return REVIEW, "Sharing could not be checked automatically; review the link and approve its exact URL"


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
            fileId=file_id, supportsAllDrives=True, fields="id,trashed,md5Checksum,permissions(type,role)").execute()
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
    # files.get may expose public permissions even when permissions.list is
    # forbidden for an externally owned file. This requires no extra request.
    inline_permissions = metadata.get("permissions")
    if isinstance(inline_permissions, list) and any(
        p.get("type") == "anyone" and p.get("role") in
        {"reader", "commenter", "writer", "owner"} for p in inline_permissions
    ):
        return checksum_problem or (PASS, "Public sharing verified")

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
                    diagnostics.append(f"resource_id={resource_id}\\toperation=permissions.list"
                                       f"\\tfile_id={file_id}\\tapi_reason=permissions_not_returned")
                return unknown_sharing(resource, url, checksum_problem)
            if any(p.get("type") == "anyone" and p.get("role") in
                   {"reader", "commenter", "writer", "owner"} for p in permissions):
                return checksum_problem or (PASS, "Public sharing verified")
            token = result.get("nextPageToken")
            if not token:
                return FAIL, "File is not shared with anyone who has the link"
    except Exception as exc:
        if diagnostics is not None:
            diagnostics.append(diagnostic_line(resource_id, url, "permissions.list", exc))
        return unknown_sharing(resource, url, checksum_problem)


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
        report.append({"resource_id": rid, "title": resource.get("title", rid), "result": result, "issues": issues})
    overall = FAIL if any(r["result"] == FAIL for r in report) else (
        REVIEW if any(r["result"] == REVIEW for r in report) else PASS)
    return {"read_only": True, "result": overall, "resources": report,
            "diagnostics": diagnostics}


def friendly_reason(reason: str) -> str:
    """Plain-language explanation and next step for the Actions summary."""
    replacements = {
        "No published URL": "No live link is recorded. Add the verified official link.",
        "Invalid HTTPS URL": "The link is invalid. Check and correct the saved URL.",
        "Invalid Google Drive file URL": "The Drive file ID could not be read. Correct the link.",
        "Service account unavailable": "Drive verification is unavailable. Check the publisher account.",
        "Service account cannot access Drive file":
            "The publisher cannot open the file. Check its access; existence is not confirmed.",
        "Wrong Drive file or file in Trash": "The linked file is missing, mismatched, or in Trash.",
        "Approved PDF checksum not recorded":
            "No approved PDF checksum is on record. Verify the existing PDF before recording a baseline.",
        "Drive did not return PDF checksum":
            "Drive did not provide a checksum. Confirm the file type and retry.",
        "Published PDF checksum differs from approved version":
            "The live PDF differs from the approved version. Review the change before publishing.",
        "Human review required": "Review this external website and approve the exact URL.",
        "Sharing could not be checked automatically; review the link and approve its exact URL":
            "Drive confirmed the file exists, but could not confirm public sharing. Open it as a viewer, then record approval for this exact URL.",
        "File is not shared with anyone who has the link":
            "Public link access is not enabled. Update sharing or replace the link.",
    }
    return replacements.get(reason, reason)


def summary_table(report: dict) -> str:
    total = len(report["resources"])
    problems = sum(bool(x["issues"]) for x in report["resources"])
    rows = ["| Status | Resource | What happened / next step | Link |",
            "|---|---|---|---|"]
    for item in report["resources"]:
        for issue in item["issues"]:
            url = issue["url"] or ""
            link = f"[Open]({url})" if url.startswith("https://") else "—"
            title = item.get("title") or item["resource_id"]
            reason = friendly_reason(issue["reason"]).replace("|", "\\|").replace("\\n", " ")
            rows.append(f"| {issue['status']} | {title} | {reason} | {link} |")
    if problems == 0:
        rows.append("| PASS | All checked resources | No action needed | — |")
    header = f"### Publication inspection — {problems} need attention out of {total} checked\\n\\n"
    footer = ("\\n**Technical details:** Download `inspection-report.txt` and "
              "`inspection-report.json` from the workflow artifacts. "
              "NEEDS REVIEW is not proof that the link is broken.\\n")
    return header.replace("\\n", "\n") + "\n".join(rows) + "\n" + footer.replace("\\n", "\n")


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
