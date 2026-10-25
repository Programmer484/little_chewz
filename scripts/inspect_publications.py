#!/usr/bin/env python3
"""Manual, read-only publication inspection; does not modify Drive or catalogue."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from publish_to_drive import (ROOT, PublishError, drive_file_id, drive_service,
                              load_registry, build_pdf, md5, output_name)


def inspect_one(resource_id: str, item: dict, service=None, builder=build_pdf) -> dict:
    status = item.get("status", "unpublished")
    production = item.get("production_type")
    recorded = item.get("publication") or {}
    result = {"resource_id": resource_id, "status": status,
              "holding_present": bool(item.get("holding_url")),
              "production_type": production, "content_parity": "unverified",
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
            fields="id,name,mimeType,parents,md5Checksum,version,webViewLink").execute()
        if meta.get("id") != file_id:
            raise PublishError("Drive returned an unexpected file ID")
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
