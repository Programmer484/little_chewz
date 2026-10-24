#!/usr/bin/env python3
"""Build one approved document and replace its Drive file in place.

The registry entry in catalog/resources.json names the Drive destination
(`url`) and how to build the PDF (`build`):

    "build": {"renderer": "claude", "source": "content/.../welcome.json"}
    "build": {"output": "00-activate-teacher-guide.pdf"}   # select_builds target

Publishing replaces the file's contents through the Drive API, so the file
ID, link, name, folder, and sharing stay the same and Drive keeps the old
version in its history. After Drive reports the same MD5 as the local PDF,
an `approved` entry is marked `published`.

Credentials: a Google service account key (JSON) in the environment
variable GOOGLE_SERVICE_ACCOUNT_JSON. Share the target file or folder with
the service account's email as an Editor.

Usage:
    python scripts/publish_to_drive.py ccc-q01-welcome --dry-run
    python scripts/publish_to_drive.py ccc-q01-welcome
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "catalog" / "resources.json"
OUT = ROOT / "exports" / "publish"
PUBLISHABLE = {"approved", "published"}
SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_ID = re.compile(r"/d/([A-Za-z0-9_-]{20,})")


class PublishError(Exception):
    pass


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def save_registry(registry: dict) -> None:
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def drive_file_id(url: str) -> str:
    match = DRIVE_ID.search(url or "")
    if not match:
        raise PublishError(f"Not a Drive file URL: {url!r}")
    return match.group(1)


def check_entry(resource_id: str, entry: dict | None) -> tuple[str, dict]:
    if entry is None:
        raise PublishError(f"Unknown resource ID: {resource_id}")
    status = entry.get("status", "unapproved")
    if status not in PUBLISHABLE:
        raise PublishError(f"{resource_id} is {status}; only approved or published entries can be published")
    build = entry.get("build")
    if not isinstance(build, dict) or not (build.get("source") or build.get("output")):
        raise PublishError(f"{resource_id} has no 'build' instructions in the registry")
    return drive_file_id(entry.get("url", "")), build


def build_pdf(resource_id: str, build: dict) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{resource_id}.pdf"
    if build.get("renderer") == "claude":
        source = ROOT / build["source"]
        subprocess.run([sys.executable, str(ROOT / "templates/claude/render.py"), str(source),
                        "--output", str(target)], check=True)
    elif build.get("output"):
        manifest = OUT / "manifest.json"
        manifest.write_text(json.dumps({"outputs": [build["output"]]}))
        subprocess.run([sys.executable, str(ROOT / "scripts/build_selected.py"),
                        "--manifest", str(manifest)], check=True)
        (ROOT / "exports" / build["output"]).replace(target)
    else:
        raise PublishError(f"Unsupported build instructions for {resource_id}: {build}")
    if not target.is_file() or target.stat().st_size == 0:
        raise PublishError(f"Build produced no PDF for {resource_id}")
    if not target.read_bytes().startswith(b"%PDF"):
        raise PublishError(f"Build output is not a PDF: {target}")
    return target


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def drive_service():
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise PublishError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build as discovery_build

    creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    return discovery_build("drive", "v3", credentials=creds, cache_discovery=False)


META_FIELDS = "id,name,mimeType,md5Checksum,version,modifiedTime,webViewLink,capabilities(canEdit)"


def check_destination(service, file_id: str) -> dict:
    meta = service.files().get(fileId=file_id, fields=META_FIELDS, supportsAllDrives=True).execute()
    if meta.get("mimeType") != "application/pdf":
        raise PublishError(f"Drive file {file_id} is {meta.get('mimeType')}, not a PDF")
    if not meta.get("capabilities", {}).get("canEdit"):
        raise PublishError(f"Service account cannot edit {meta.get('name')} ({file_id}); share it as Editor")
    return meta


def upload(service, file_id: str, pdf: Path) -> dict:
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(pdf), mimetype="application/pdf", resumable=True)
    return service.files().update(fileId=file_id, media_body=media, fields=META_FIELDS,
                                  supportsAllDrives=True).execute()


def publish(resource_id: str, dry_run: bool = False, service=None, builder=build_pdf) -> dict:
    registry = load_registry()
    entry = registry.get(resource_id)
    file_id, build = check_entry(resource_id, entry)
    pdf = builder(resource_id, build)
    local_md5 = md5(pdf)
    service = service or drive_service()
    before = check_destination(service, file_id)
    report = {"resource_id": resource_id, "file_id": file_id, "name": before.get("name"),
              "local_md5": local_md5, "previous_md5": before.get("md5Checksum"),
              "previous_version": before.get("version"), "bytes": pdf.stat().st_size,
              "dry_run": dry_run, "status_before": entry.get("status")}
    if dry_run:
        report["result"] = "dry run: built and checked access; Drive not changed"
        return report
    if before.get("md5Checksum") == local_md5:
        report["result"] = "unchanged: Drive already has these exact bytes"
    else:
        after = upload(service, file_id, pdf)
        if after.get("id") != file_id:
            raise PublishError(f"Drive returned a different file ID: {after.get('id')}")
        if after.get("md5Checksum") != local_md5:
            raise PublishError(f"MD5 mismatch after upload: Drive {after.get('md5Checksum')}, local {local_md5}")
        report.update(result="replaced in place", new_version=after.get("version"),
                      modified=after.get("modifiedTime"), link=after.get("webViewLink"))
    if entry.get("status") == "approved":
        entry["status"] = "published"
        save_registry(registry)
        report["status_after"] = "published"
    else:
        report["status_after"] = entry.get("status")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("resource_id", help="registry ID, for example ccc-q01-welcome")
    parser.add_argument("--dry-run", action="store_true", help="build and check access without uploading")
    args = parser.parse_args()
    try:
        report = publish(args.resource_id, dry_run=args.dry_run)
    except PublishError as exc:
        print(f"PUBLISH FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(report, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"### Drive publish: `{report['resource_id']}`\n\n")
            for key, value in report.items():
                fh.write(f"- **{key}**: {value}\n")


if __name__ == "__main__":
    main()
