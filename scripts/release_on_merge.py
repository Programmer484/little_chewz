#!/usr/bin/env python3
"""Guarded release of explicitly accepted resource PRs; no background publication."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from select_builds import ROOT, select, targets
from publish_to_drive import PublishError, load_registry, save_registry, publish, output_name

SIGNAL_DIR = Path(".github/resource-releases")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ReleaseError(Exception):
    pass


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def release_request(pr: int, changed: set[str]) -> list[str]:
    """Only a newly merged, explicitly authorized marker can initiate a release."""
    marker = SIGNAL_DIR / f"{pr}.json"
    if marker.as_posix() not in changed:
        return []
    document = json.loads((ROOT / marker).read_text(encoding="utf-8"))
    if (document.get("signal") != "authorized-resource-merge"
            or document.get("pr_number") != pr):
        raise ReleaseError(f"{marker}: invalid /merge release authorization")
    ids = document.get("resource_ids")
    if (not isinstance(ids, list) or len(ids) != 1
            or any(not isinstance(i, str) or not ID_RE.fullmatch(i) for i in ids)
            or len(ids) != len(set(ids))):
        raise ReleaseError(f"{marker}: resource IDs must be unique stable IDs")
    return ids


def plan(pr: int, changed: set[str], merge_sha: str, base_sha: str,
         head_branch: str | None = None) -> dict:
    ids = release_request(pr, changed)
    if not ids:
        return {"pr": pr, "result": "no authorized resource release", "generated": [],
                "external": [], "blocked": []}
    if head_branch is not None and head_branch != f"edit/{ids[0]}":
        raise ReleaseError("Authorized /merge must come from the single matching generated-resource branch")
    registry = load_registry()
    registered = targets()
    affected = set(select(changed, base_ref=base_sha))
    head = git("rev-parse", "HEAD")
    if subprocess.run(["git", "merge-base", "--is-ancestor", merge_sha, head],
                      cwd=ROOT).returncode:
        raise ReleaseError("Accepted merge is not an ancestor of checked-out main")
    changed_after = set(git("diff", "--name-only", merge_sha, head).splitlines())
    superseded = set(select(changed_after, base_ref=merge_sha)) if changed_after else set()
    result = {"pr": pr, "merge_revision": merge_sha, "build_revision": head,
              "generated": [], "external": [], "blocked": []}
    for rid in ids:
        item = registry.get(rid)
        if item is None:
            result["blocked"].append({"resource_id": rid, "reason": "missing catalogue registration"})
            continue
        production_type = item.get("production_type")
        if production_type == "external":
            result["blocked"].append({"resource_id": rid, "reason": "External resources never use /merge or automated publishing"})
            continue
        if production_type != "generated_pdf":
            result["blocked"].append({"resource_id": rid, "reason": "missing or invalid production_type"})
            continue
        try:
            output = output_name(rid, item.get("build") or {})
        except PublishError as exc:
            result["blocked"].append({"resource_id": rid, "reason": str(exc)})
            continue
        if output not in registered:
            result["blocked"].append({"resource_id": rid, "reason": "generated output is not registered"})
        elif output not in affected:
            result["blocked"].append({"resource_id": rid, "reason": "no eligible generated source change in accepted PR"})
        elif output in superseded:
            result["blocked"].append({"resource_id": rid, "reason": "accepted source superseded by newer main"})
        elif not item.get("url") or item.get("status") == "unpublished":
            result["blocked"].append({"resource_id": rid, "reason": "initial upload/verification required"})
        else:
            result["generated"].append(rid)
    return result


def run_release(result: dict) -> dict:
    """A failed upload leaves pending_publish; external releases are never auto-uploaded."""
    for rid in result["generated"]:
        registry = load_registry()
        item = registry[rid]
        if item.get("status") == "published":
            item["status"] = "pending_publish"
            save_registry(registry)
        try:
            verified = publish(rid, expected_revision=result["build_revision"])
            result.setdefault("published", []).append({
                "resource_id": rid, "drive_file_id": verified["file_id"],
                "artifact_md5": verified["local_md5"], "publication": verified.get("publication")})
        except Exception as exc:
            # Keep partial outcomes explicit; do not advance any unverified item.
            result["blocked"].append({"resource_id": rid, "reason": str(exc)})
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pr", required=True, type=int)
    p.add_argument("--merge-sha", required=True)
    p.add_argument("--base-sha", required=True)
    p.add_argument("--changed-files", required=True, type=Path)
    p.add_argument("--head-branch", required=True)
    p.add_argument("--report", required=True, type=Path)
    args = p.parse_args()
    if args.pr < 1 or any(not re.fullmatch(r"[0-9a-f]{40}", sha)
                          for sha in (args.merge_sha, args.base_sha)):
        p.error("Expected PR number and full Git SHAs")
    try:
        changed = set(args.changed_files.read_text().splitlines())
        result = plan(args.pr, changed, args.merge_sha, args.base_sha, args.head_branch)
        result = run_release(result)
    except Exception as exc:
        result = {"pr": args.pr, "blocked": [{"reason": str(exc)}]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result.get("blocked"):
        sys.exit(1)


if __name__ == "__main__":
    main()
