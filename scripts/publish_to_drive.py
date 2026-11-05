#!/usr/bin/env python3
"""Agent-invoked explicit-ID replacement of an established generated PDF.

The registry entry in catalog/resources.json names the Drive destination
(`published_url`) and the generated PDF details (`pdf`):

    "pdf": {"renderer": "welcome", "source": "content/.../welcome.json"}
    "pdf": {"renderer": "teacher_guide", "output": "00-activate-teacher-guide.pdf"}   # select_builds target

Only an explicit human publish instruction authorizes running this helper.
It has no GitHub Action trigger and is not a publication audit.
Publishing replaces the file's contents through the Drive API, so the file
ID, link, name, folder, and sharing stay the same and Drive keeps the old
version in its history. After Drive reports the same MD5 as the local PDF,
the approved checksum is updated atomically after verified Drive read-back.

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
from datetime import datetime, timezone
from pathlib import Path
from publication_state import publication_status

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "catalog" / "resources.json"
OUT = ROOT / "exports" / "publish"
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
    if not entry.get("published_url"):
        raise PublishError(f"{resource_id} has no established official destination; initial publication is agent-managed")
    pdf = entry.get("pdf")
    if not isinstance(pdf, dict) or pdf.get("renderer") not in {"teacher_guide", "teacher_companion", "welcome"}:
        raise PublishError(f"{resource_id} is external or lacks PDF generation metadata")
    if not (pdf.get("source") or pdf.get("output")):
        raise PublishError(f"{resource_id} has no PDF build source/output")
    return drive_file_id(entry["published_url"]), pdf


def output_name(resource_id: str, build: dict) -> str:
    """Registry-built documents preview as <resource-id>.pdf; others name a select_builds output."""
    if build.get("output"):
        return build["output"]
    if build.get("source"):
        return f"{resource_id}.pdf"
    raise PublishError(f"Unsupported build instructions for {resource_id}: {build}")


def build_pdf(resource_id: str, build: dict) -> Path:
    """Build through scripts/build_selected.py, the same path as GitHub previews."""
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{resource_id}.pdf"
    name = output_name(resource_id, build)
    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps({"outputs": [name]}))
    subprocess.run([sys.executable, str(ROOT / "scripts/build_selected.py"),
                    "--manifest", str(manifest), "--release"], check=True)
    (ROOT / "exports" / name).replace(target)
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


def current_revision() -> str:
    """The accepted code revision, not the later status-metadata commit."""
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PublishError("Cannot identify the accepted Git revision") from exc
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise PublishError(f"Invalid accepted revision: {revision!r}")
    return revision


def assert_revision(expected: str | None) -> str:
    actual = current_revision()
    if expected is not None and expected != actual:
        raise PublishError(f"Accepted main revision changed: expected {expected}, found {actual}")
    return actual


def publish(resource_id: str, dry_run: bool = False, service=None,
            builder=build_pdf, expected_revision: str | None = None) -> dict:
    registry = load_registry()
    entry = registry.get(resource_id)
    file_id, build = check_entry(resource_id, entry)
    revision = assert_revision(expected_revision)
    # Every generated document uses the same explicit output mapping as previews.
    if builder is build_pdf:
        from select_builds import targets
        name = output_name(resource_id, build)
        if name not in targets():
            raise PublishError(f"{resource_id}: unregistered generated PDF output {name}")
    from select_builds import targets
    from publication_checks import unpublished_dependencies
    blocked = unpublished_dependencies(resource_id, registry, targets())
    if blocked:
        raise PublishError(f"{resource_id}: unpublished linked resources: {', '.join(blocked)}")
    pdf = builder(resource_id, build)
    assert_revision(revision)
    local_md5 = md5(pdf)
    service = service or drive_service()
    before = check_destination(service, file_id)

    report = {"resource_id": resource_id, "file_id": file_id, "name": before.get("name"),
              "local_md5": local_md5, "previous_md5": before.get("md5Checksum"),
              "previous_version": before.get("version"), "bytes": pdf.stat().st_size,
              "dry_run": dry_run, "status_before": publication_status(entry, local_md5),
              "release_revision": revision}
    if dry_run:
        report["result"] = "dry run: built and checked access; Drive not changed"
        return report
    assert_revision(revision)
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
    # Read back actual Drive metadata. A successful update request alone is not
    # evidence that the teacher-facing destination contains the expected bytes.
    confirmed = check_destination(service, file_id)
    if confirmed.get("id") != file_id or confirmed.get("md5Checksum") != local_md5:
        raise PublishError(f"Drive read-back checksum or file ID mismatch for {resource_id}")
    assert_revision(revision)
    details = entry["pdf"]
    if details.get("revision") == revision and details.get("approved_md5") == local_md5:
        report["status_after"] = "published"
        report["pdf"] = details
        return report
    details["approved_md5"] = local_md5
    details["revision"] = revision
    save_registry(registry)
    report["status_after"] = "published"
    report["confirmed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report["drive_version"] = str(confirmed["version"]) if confirmed.get("version") is not None else None
    report["pdf"] = details
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("resource_id", help="registry ID, for example ccc-q01-welcome")
    parser.add_argument("--dry-run", action="store_true", help="build and check access without uploading")
    parser.add_argument("--expected-revision", help="Reject a stale or unexpected main HEAD")
    parser.add_argument("--result-json", type=Path, help="Write verified publication report as JSON")
    args = parser.parse_args()
    try:
        report = publish(args.resource_id, dry_run=args.dry_run,
                         expected_revision=args.expected_revision)
        if args.result_json:
            args.result_json.parent.mkdir(parents=True, exist_ok=True)
            args.result_json.write_text(json.dumps(report, indent=2) + "\n")
    except subprocess.CalledProcessError as exc:
        print(f"PUBLISH FAILED: build step exited with {exc.returncode}; see the error above", file=sys.stderr)
        sys.exit(1)
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
