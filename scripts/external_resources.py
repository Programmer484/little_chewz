#!/usr/bin/env python3
"""Agent-operated staging and Drive publication of external resources.

Never treats staging as publication; slideshow PDF/PPTX pairing stays in the
separate human-approved slide procedure.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from publish_to_drive import ROOT, drive_service, drive_file_id, load_registry, save_registry, PublishError

FOLDER_CONFIG = ROOT / "catalog/drive_folders.json"
META = "id,name,mimeType,parents,version,size,webViewLink,capabilities(canEdit,canAddChildren)"
FOLDER_MIME = "application/vnd.google-apps.folder"


def folder_metadata(service, folder_id: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{15,}", folder_id or ""):
        raise PublishError("Missing or invalid configured Drive folder ID")
    meta = service.files().get(fileId=folder_id, fields=META, supportsAllDrives=True).execute()
    if meta.get("id") != folder_id or meta.get("mimeType") != FOLDER_MIME:
        raise PublishError("Destination/staging folder was not verified")
    if not meta.get("capabilities", {}).get("canAddChildren"):
        raise PublishError("Service account lacks upload permission in folder")
    return meta


def source_media(path: Path, mime: str):
    if not path.is_file() or not path.stat().st_size or not mime or "/" not in mime:
        raise PublishError("External original and explicit MIME type are required")
    from googleapiclient.http import MediaFileUpload
    return MediaFileUpload(str(path), mimetype=mime, resumable=True)


def verify_file(service, file_id: str, mime: str, folder_id: str | None = None) -> dict:
    meta = service.files().get(fileId=file_id, fields=META, supportsAllDrives=True).execute()
    if meta.get("id") != file_id or meta.get("mimeType") != mime:
        raise PublishError("Drive read-back ID/MIME mismatch; publication not confirmed")
    if folder_id and folder_id not in meta.get("parents", []):
        raise PublishError("Drive read-back destination folder mismatch")
    return meta


def check_no_duplicate(service, folder_id: str, name: str) -> None:
    escaped = name.replace("\\", "\\\\").replace("'", "\\'")
    query = f"'{folder_id}' in parents and name = '{escaped}' and trashed = false"
    found = service.files().list(q=query, fields="nextPageToken,files(id,name)", pageSize=100,
                                 supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    if found.get("files"):
        raise PublishError("A teacher-facing file with this name already exists; reconcile ID, do not duplicate")


def stage_file(path: Path, mime: str, service=None) -> dict:
    if not FOLDER_CONFIG.is_file():
        raise PublishError("General external staging folder configuration is missing")
    config = json.loads(FOLDER_CONFIG.read_text())
    folder_id = ((config.get("staging") or {}).get("external") or {}).get("folder_id")
    service = service or drive_service()
    folder_metadata(service, folder_id)
    media = source_media(path, mime)
    uploaded = service.files().create(
        body={"name": path.name, "parents": [folder_id]}, media_body=media,
        fields=META, supportsAllDrives=True).execute()
    file_id = uploaded.get("id")
    confirmed = verify_file(service, file_id, mime, folder_id)
    return {"result": "staged for review, NOT published", "file_id": file_id,
            "staging_folder_id": folder_id, "mime_type": mime,
            "link": confirmed.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"}


def confirm_accepted_revision(revision: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", revision or ""):
        raise PublishError("Accepted release revision must be a full Git SHA")
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if current != revision:
        raise PublishError("Checkout does not match accepted release revision")


def publish_file(resource_id: str, path: Path, mime: str, revision: str,
                 destination_folder_id: str | None = None, service=None) -> dict:
    confirm_accepted_revision(revision)
    registry = load_registry()
    item = registry.get(resource_id)
    if not item or item.get("production_type") != "external":
        raise PublishError("Only registered external resources can use this publication path")
    if item.get("type") == "slide_deck":
        raise PublishError("Slide PDF/PPTX pairing needs separate human-reviewed slide workflow")
    service = service or drive_service()
    media = source_media(path, mime)
    original_url = item.get("url")
    if original_url:
        file_id = drive_file_id(original_url)
        existing = verify_file(service, file_id, mime)
        if not existing.get("capabilities", {}).get("canEdit"):
            raise PublishError("Service account cannot replace existing file in place")
        if destination_folder_id and destination_folder_id not in existing.get("parents", []):
            raise PublishError("Requested destination differs from existing published folder")
        parent = (existing.get("parents") or [None])[0]
        updated = service.files().update(fileId=file_id, media_body=media, fields=META,
                                         supportsAllDrives=True).execute()
        if updated.get("id") != file_id:
            raise PublishError("In-place replacement changed file ID")
        action = "replaced in place"
    else:
        if item.get("status", "unpublished") != "unpublished":
            raise PublishError("No published destination despite live status")
        folder_metadata(service, destination_folder_id)
        check_no_duplicate(service, destination_folder_id, path.name)
        created = service.files().create(
            body={"name": path.name, "parents": [destination_folder_id]},
            media_body=media, fields=META, supportsAllDrives=True).execute()
        file_id = created.get("id")
        parent = destination_folder_id
        action = "first teacher-facing upload"
    confirmed = verify_file(service, file_id, mime, parent)
    confirm_accepted_revision(revision)
    # Agent verifies Drive metadata; content parity is explicitly not inferred.
    record = {"verification": "verified", "method": "external_agent",
              "drive_file_id": file_id, "release_revision": revision,
              "confirmed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "content_parity": "unverified",
              "drive_version": str(confirmed["version"]) if confirmed.get("version") is not None else None}
    item["status"] = "published"
    item["url"] = original_url or confirmed.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
    item["publication"] = record
    save_registry(registry)
    return {"result": action, "resource_id": resource_id, "file_id": file_id,
            "destination_folder_id": parent, "publication": record}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    stage = sub.add_parser("stage", help="Upload a review original to the configured holding folder")
    stage.add_argument("--file", type=Path, required=True)
    stage.add_argument("--mime", required=True)
    publish = sub.add_parser("publish", help="Agent-confirmed external publication after /merge")
    publish.add_argument("--resource-id", required=True)
    publish.add_argument("--file", type=Path, required=True)
    publish.add_argument("--mime", required=True)
    publish.add_argument("--revision", required=True)
    publish.add_argument("--destination-folder-id")
    args = parser.parse_args()
    try:
        result = (stage_file(args.file, args.mime) if args.command == "stage"
                  else publish_file(args.resource_id, args.file, args.mime, args.revision,
                                    args.destination_folder_id))
    except PublishError as exc:
        parser.exit(1, f"EXTERNAL PUBLISH FAILED: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
