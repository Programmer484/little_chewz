#!/usr/bin/env python3
"""Read-only audit of published resources: Exists, Accessible, Correct."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from publish_to_drive import ROOT, build_pdf, drive_service, load_registry, output_name
from select_builds import resource_refs, targets

PASS = "PASS"
FAIL = "FAIL"
REVIEW = "NEEDS REVIEW"
DRIVE_HOSTS = {"drive.google.com", "docs.google.com"}
FILE_ID = re.compile(r"/(?:d|folders)/([A-Za-z0-9_-]{20,})")
MD5 = re.compile(r"[0-9a-f]{32}")


def check(state: str, reason: str) -> dict:
    return {"result": state, "reason": reason}


def worst(*states: str) -> str:
    if FAIL in states:
        return FAIL
    if REVIEW in states:
        return REVIEW
    return PASS


def drive_id(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if parsed.hostname not in DRIVE_HOSTS:
        return None
    match = FILE_ID.search(parsed.path)
    return match.group(1) if match else None


def url_key(url: str) -> str:
    file_id = drive_id(url)
    if file_id:
        return "drive:" + file_id
    # Preserve web path and query: different routes can point to different resources.
    parts = urlsplit(url)
    return (parts.scheme.lower() + "://" + (parts.netloc or "").lower()
            + parts.path + ("?" + parts.query if parts.query else ""))


def published_parts(resource: dict) -> dict[str, str]:
    url = resource.get("published_url")
    if not url:
        return {}
    result = {"main": url}
    if resource.get("type") == "slide_deck" and resource.get("pdf_url"):
        result["pdf"] = resource["pdf_url"]
    return result


def expected_folder(folders: dict, resource_id: str, part: str) -> str | None:
    entry = (folders.get("published") or {}).get("by_resource_id", {}).get(resource_id)
    return entry if isinstance(entry, str) and part == "main" else (
        entry.get(part) if isinstance(entry, dict) else None)


def approved_checksum(resource: dict, part: str) -> str | None:
    approved = resource.get("publication") or {}
    if part == "pdf":
        return approved.get("pdf_md5")
    return approved.get("artifact_md5") or approved.get("approved_md5")


def expected_mime(resource: dict, part: str) -> set[str] | None:
    if part == "pdf" or resource.get("production_type") == "generated_pdf":
        return {"application/pdf"}
    if resource.get("type") == "slide_deck":
        return {"application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/vnd.google-apps.presentation"}
    return None


def public_reader(service, file_id: str) -> bool:
    token = None
    while True:
        params = {"fileId": file_id, "supportsAllDrives": True,
                  "fields": "nextPageToken,permissions(type,role)",
                  "pageSize": 100}
        if token:
            params["pageToken"] = token
        page = service.permissions().list(**params).execute()
        perms = page.get("permissions")
        if not isinstance(perms, list):
            raise ValueError("Drive did not return sharing permissions")
        if any(p.get("type") == "anyone" and p.get("role")
               in {"reader", "commenter", "writer"} for p in perms):
            return True
        token = page.get("nextPageToken")
        if not token:
            return False


def audit_drive(resource_id: str, resource: dict, part: str, url: str,
                service, folders: dict, builder=build_pdf) -> dict:
    file_id = drive_id(url)
    if not file_id:
        return {"exists": check(FAIL, "Not a valid Drive file or folder link"),
                "accessible": check(REVIEW, "No file to check"),
                "correct": check(REVIEW, "No file to check")}
    try:
        meta = service.files().get(
            fileId=file_id, supportsAllDrives=True,
            fields="id,name,mimeType,parents,md5Checksum,trashed").execute()
        if meta.get("id") != file_id:
            raise ValueError("Drive returned another file")
    except Exception as exc:
        return {"exists": check(FAIL, "Missing or not visible to inspector: " + str(exc)),
                "accessible": check(REVIEW, "File cannot be inspected"),
                "correct": check(REVIEW, "File cannot be inspected")}

    if meta.get("trashed") is True:
        existence = check(FAIL, "File is in Trash")
    elif meta.get("trashed") is not False:
        existence = check(REVIEW, "Drive did not confirm Trash status")
    else:
        approved_folder = expected_folder(folders, resource_id, part)
        parents = meta.get("parents")
        if not approved_folder:
            existence = check(REVIEW, "Approved folder not recorded yet")
        elif not isinstance(parents, list):
            existence = check(REVIEW, "Drive did not confirm folder")
        elif approved_folder not in parents:
            existence = check(FAIL, "File is not in its approved folder")
        else:
            existence = check(PASS, "Exists in approved folder")

    try:
        accessible = (check(PASS, "Anyone with the link can view")
                      if public_reader(service, file_id)
                      else check(FAIL, "Public viewing is disabled"))
    except Exception as exc:
        accessible = check(REVIEW, "Cannot confirm public viewing: " + str(exc))

    allowed = expected_mime(resource, part)
    if allowed and meta.get("mimeType") not in allowed:
        correctness = check(FAIL, "Wrong file format")
    else:
        recorded_id = (resource.get("publication") or {}).get("drive_file_id")
        if part == "main" and recorded_id and recorded_id != file_id:
            correctness = check(FAIL, "Link points to the wrong file ID")
        else:
            expected = approved_checksum(resource, part)
            actual = meta.get("md5Checksum")
            if not expected or not MD5.fullmatch(expected):
                correctness = check(REVIEW, "Approved checksum not recorded yet")
            elif not actual:
                correctness = check(REVIEW, "Drive did not provide a file checksum")
            elif actual != expected:
                correctness = check(FAIL, "Checksum differs from approved version")
            elif resource.get("production_type") == "generated_pdf" and part == "main":
                try:
                    built = builder(resource_id, resource["build"])
                    current = hashlib.md5(built.read_bytes()).hexdigest()
                    correctness = (check(PASS, "Drive and current approved source match")
                                   if current == expected else
                                   check(FAIL, "Current GitHub source differs from published PDF"))
                except Exception as exc:
                    correctness = check(REVIEW, "Cannot rebuild source PDF: " + str(exc))
            else:
                correctness = check(PASS, "Checksum matches approved version")
    return {"exists": existence, "accessible": accessible, "correct": correctness}


def audit_website(url: str) -> dict:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return {"exists": check(FAIL, "Invalid public HTTPS link"),
                "accessible": check(FAIL, "Not a public HTTPS link"),
                "correct": check(REVIEW, "No approved checksum")}
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "LittleChewzPublicationAudit/1.0"})
        with urllib.request.urlopen(request, timeout=12) as response:
            destination = urlsplit(response.geturl())
            if destination.hostname in {"accounts.google.com", "login.microsoftonline.com"}:
                return {"exists": check(PASS, "Link resolves"),
                        "accessible": check(FAIL, "Redirected to sign-in"),
                        "correct": check(REVIEW, "No approved checksum")}
            if response.status >= 400:
                raise ValueError("HTTP " + str(response.status))
        return {"exists": check(PASS, "Link responds"),
                "accessible": check(PASS, "Opens without signing in"),
                "correct": check(REVIEW, "No approved downloadable checksum")}
    except urllib.error.HTTPError as exc:
        state = FAIL if exc.code in {401, 403, 404, 410} else REVIEW
        return {"exists": check(state, "HTTP " + str(exc.code)),
                "accessible": check(state, "HTTP " + str(exc.code)),
                "correct": check(REVIEW, "Content not checked")}
    except Exception as exc:
        return {"exists": check(REVIEW, "Cannot open site: " + str(exc)),
                "accessible": check(REVIEW, "Cannot verify anonymous access"),
                "correct": check(REVIEW, "Content not checked")}


def guide_links(service, resource_id: str, resource: dict, registry: dict,
                resource_reports: dict, source_targets: dict) -> dict:
    """Read hyperlinks in the *published PDF*, not only references in source JSON."""
    file_id = drive_id(resource["published_url"])
    if not file_id:
        return check(REVIEW, "Guide is not a downloadable Drive PDF")
    try:
        import fitz
        raw = service.files().get_media(fileId=file_id, supportsAllDrives=True).execute()
        if not isinstance(raw, bytes):
            raise ValueError("Drive did not return PDF bytes")
        with fitz.open(stream=raw, filetype="pdf") as pdf:
            urls = [link["uri"] for page in pdf for link in page.get_links()
                    if link.get("kind") == fitz.LINK_URI and link.get("uri")]
    except Exception as exc:
        return check(REVIEW, "Could not read published guide links: " + str(exc))

    by_link = {}
    for rid, item in registry.items():
        for url in published_parts(item).values():
            by_link.setdefault(url_key(url), set()).add(rid)
        # Recognize draft/holding links so a published Guide cannot silently use them.
        for key in ("url", "holding_url"):
            if item.get(key):
                by_link.setdefault(url_key(item[key]), set()).add(rid)

    issues = []
    review = []
    seen = set()
    for url in urls:
        key = url_key(url)
        matched = by_link.get(key, set())
        if not matched:
            review.append("Unregistered link: " + url)
            continue
        seen.update(matched)
        for rid in matched:
            record = registry[rid]
            if record.get("status") != "published":
                issues.append("Links to unpublished resource: " + rid)
            elif rid in resource_reports:
                linked = resource_reports[rid]["result"]
                if linked == FAIL:
                    issues.append("Linked resource fails: " + rid)
                elif linked == REVIEW:
                    review.append("Linked resource needs review: " + rid)

    guide_target = next((t for t in source_targets.values()
                         if t.get("resource_id") == resource_id and t.get("kind") == "teacher_guide"), None)
    if guide_target is None:
        review.append("No registered lesson source to compare with guide")
    else:
        for rid in resource_refs(guide_target["data"]):
            if rid not in registry or registry[rid].get("status") != "published":
                issues.append("Guide requires unpublished resource: " + rid)
            elif rid not in seen:
                issues.append("Published guide is missing expected link: " + rid)

    if issues:
        return check(FAIL, "; ".join(sorted(set(issues))[:15]))
    if review:
        return check(REVIEW, "; ".join(sorted(set(review))[:15]))
    return check(PASS, str(len(urls)) + " published hyperlinks checked")


def audit(registry: dict, folders: dict, service=None, builder=build_pdf,
          source_targets: dict | None = None, only: str | None = None) -> dict:
    if only and only not in registry:
        raise ValueError("Unknown resource: " + only)
    selected = {rid: resource for rid, resource in registry.items()
                if resource.get("status") == "published"}
    if only:
        selected = {rid: resource for rid, resource in selected.items() if rid == only}
    report = {}
    for rid, resource in selected.items():
        pieces = published_parts(resource)
        if not pieces:
            parts = {"main": {"exists": check(FAIL, "No published link"),
                              "accessible": check(REVIEW, "No link"),
                              "correct": check(REVIEW, "No link")}}
        else:
            parts = {}
            for part, url in pieces.items():
                if drive_id(url):
                    if service is None:
                        service = drive_service()
                    parts[part] = audit_drive(rid, resource, part, url, service, folders, builder)
                elif urlsplit(url).hostname in DRIVE_HOSTS:
                    parts[part] = {"exists": check(FAIL, "Invalid Drive destination"),
                                   "accessible": check(REVIEW, "No file to inspect"),
                                   "correct": check(FAIL, "Invalid or placeholder Drive link")}
                else:
                    parts[part] = audit_website(url)

        checks = {}
        for category in ("exists", "accessible", "correct"):
            states = [p[category]["result"] for p in parts.values()]
            checks[category] = {"result": worst(*states),
                                "details": {part: p[category]["reason"] for part, p in parts.items()}}
        report[rid] = {"resource_id": rid, "checks": checks}

    # Compute linked resource results before checking hyperlink targets.
    for value in report.values():
        value["result"] = worst(*(x["result"] for x in value["checks"].values()))

    # A published teacher guide must have every real hyperlink checked too.
    if source_targets is None:
        source_targets = targets()
    for rid, resource in selected.items():
        build = resource.get("build") or {}
        if not (resource.get("production_type") == "generated_pdf"
                and str(build.get("output", "")).endswith("-teacher-guide.pdf")):
            continue
        link_result = guide_links(service, rid, resource, registry, report, source_targets)
        c = report[rid]["checks"]["correct"]
        c["result"] = worst(c["result"], link_result["result"])
        c["details"]["guide_links"] = link_result["reason"]

    for value in report.values():
        value["result"] = worst(*(c["result"] for c in value["checks"].values()))
    overall = worst(*(r["result"] for r in report.values())) if report else REVIEW
    return {"read_only": True, "result": overall, "resources": list(report.values())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-id", help="Inspect one published resource")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    registry = load_registry()
    folders = json.loads((ROOT / "catalog/drive_folders.json").read_text())
    result = audit(registry, folders, only=args.resource_id)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    summary = ["### Publication audit: " + result["result"], "",
               "Published resources: " + str(len(result["resources"])),
               "Unpublished resources: skipped", ""]
    for item in result["resources"]:
        summary.append("- " + item["resource_id"] + ": " + item["result"]
                       + " (" + ", ".join(k + ": " + v["result"]
                                        for k, v in item["checks"].items()) + ")")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("\n".join(summary) + "\n")
    sys.exit(0 if result["result"] == PASS else 1)


if __name__ == "__main__":
    main()
