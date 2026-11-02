#!/usr/bin/env python3
"""Manual, read-only publication inspection; does not modify Drive or catalogue."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from publish_to_drive import (ROOT, PublishError, drive_file_id, drive_service,
                              load_registry, build_pdf, md5, output_name)


PUBLIC_READER_ROLES = {"reader", "commenter", "writer", "fileOrganizer", "organizer", "owner"}


def has_anyone_reader_permission(service, file_id: str) -> bool:
    """Inspect direct and inherited permissions; never infer public access from 'shared'."""
    page_token = None
    while True:
        params = {
            "fileId": file_id,
            "supportsAllDrives": True,
            "fields": "nextPageToken,permissions(type,role,permissionDetails(inherited))",
            "pageSize": 100,
        }
        if page_token:
            params["pageToken"] = page_token
        page = service.permissions().list(**params).execute()
        if not isinstance(page.get("permissions"), list):
            raise ValueError("Drive did not return permission details")
        if any(p.get("type") == "anyone" and p.get("role") in PUBLIC_READER_ROLES
               for p in page["permissions"]):
            return True
        page_token = page.get("nextPageToken")
        if not page_token:
            return False


def inspect_one(resource_id: str, item: dict, service=None, builder=build_pdf) -> dict:
    status = item.get("status", "unpublished")
    production = item.get("production_type")
    recorded = item.get("publication") or {}
    result = {"resource_id": resource_id, "status": status,
              "holding_present": bool(item.get("holding_url")),
              "production_type": production, "content_parity": "unverified",
              "trash_status": "not_checked", "sharing_status": "not_checked",
              "observations": []}
    if production not in {"generated_pdf", "external"}:
        result["result"] = "unknown"
        result["observations"].append("Missing production classification")
        return result
    published_url = item.get("published_url")
    if not published_url:
        result["result"] = "unpublished" if status == "unpublished" else "discrepancy"
        result["observations"].append("No registered published destination")
        return result
    if not re.search(r"(?:drive|docs)\.google\.com/", published_url):
        result["result"] = "unverified"
        result["observations"].append("External provider cannot be authenticated through Drive inspection")
        return result
    try:
        file_id = drive_file_id(published_url)
        if recorded.get("drive_file_id") and recorded["drive_file_id"] != file_id:
            raise PublishError("Recorded published file ID conflicts with resource URL")
        if service is None:
            service = drive_service()
        meta = service.files().get(
            fileId=file_id, supportsAllDrives=True,
            fields="id,name,mimeType,parents,md5Checksum,version,webViewLink,trashed").execute()
        if meta.get("id") != file_id:
            raise PublishError("Drive returned an unexpected file ID")

        if meta.get("trashed") is True:
            result["trash_status"] = "trashed"
            result["observations"].append("Published Drive destination is in Trash")
        elif meta.get("trashed") is False:
            result["trash_status"] = "not_trashed"
        else:
            result["trash_status"] = "unverified"
            result["observations"].append("Drive did not return Trash status")

        try:
            if has_anyone_reader_permission(service, file_id):
                result["sharing_status"] = "anyone_reader"
            else:
                result["sharing_status"] = "restricted"
                result["observations"].append(
                    "No anyone-with-link reader permission found; published teacher access may be restricted")
        except Exception as exc:
            result["sharing_status"] = "unverified"
            result["observations"].append(f"Could not verify sharing permissions: {exc}")

        if production == "generated_pdf":
            if meta.get("mimeType") != "application/pdf":
                raise PublishError("Generated PDF destination has unexpected MIME type")
            saved = recorded.get("artifact_md5")
            if (recorded.get("verification") != "verified" or not saved
                    or not re.fullmatch(r"[0-9a-f]{32}", saved)):
                result["result"] = "unverified"
                result["observations"].append("Published generated-PDF checksum was never verified")
            elif meta.get("md5Checksum") != saved:
                result["result"] = "discrepancy"
                result["observations"].append("Drive PDF checksum differs from recorded published bytes")
            else:
                build = item.get("build") or {}
                if not build:
                    raise PublishError("Missing current generated-PDF build mapping")
                # Checking current accepted bytes detects stale publication while
                # leaving the Drive file and catalogue unchanged.
                artifact = builder(resource_id, build)
                result["content_parity"] = ("verified" if md5(artifact) == saved else "mismatch")
                result["result"] = ("verified" if result["content_parity"] == "verified"
                                    else "discrepancy")
                if result["content_parity"] == "mismatch":
                    result["observations"].append("Current accepted renderer output differs from published bytes")
        else:
            if recorded.get("verification") != "verified":
                result["result"] = "unverified"
                result["observations"].append("External release has no agent-confirmed record")
            elif (recorded.get("drive_version") is not None
                  and str(meta.get("version")) != str(recorded["drive_version"])):
                result["result"] = "discrepancy"
                result["observations"].append("External Drive version changed after agent confirmation")
            else:
                result["result"] = "verified_metadata_only"
                result["observations"].append("Drive destination exists; external content parity remains unverified")
        # Preserve checksum/version discrepancies, and do not call absent permission
        # evidence a restricted file. The service account cannot test incognito access.
        if result["trash_status"] == "trashed" or result["sharing_status"] == "restricted":
            result["result"] = "discrepancy"
        elif (result["trash_status"] == "unverified"
              or result["sharing_status"] == "unverified"):
            if result["result"] in {"verified", "verified_metadata_only"}:
                result["result"] = "unverified"
        result["drive_file_id"] = file_id
        result["drive_version"] = meta.get("version")
    except Exception as exc:
        result["result"] = "unknown"
        result["observations"].append(f"Could not confirm Drive publication: {exc}")
    return result


def inspect(resource_id: str | None = None, service=None, builder=build_pdf) -> dict:
    registry = load_registry()
    ids = [resource_id] if resource_id else sorted(registry)
    if any(rid not in registry for rid in ids):
        raise PublishError("Unknown resource ID")
    return {"read_only": True,
            "resources": [inspect_one(rid, registry[rid], service=service, builder=builder)
                          for rid in ids]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--resource-id", help="Inspect one registry entry; default is all")
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    try:
        result = inspect(args.resource_id)
    except PublishError as exc:
        p.exit(1, f"INSPECTION FAILED: {exc}\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
