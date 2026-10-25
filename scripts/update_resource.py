#!/usr/bin/env python3
"""Update an existing resource on its shared branch without overwriting stale work."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from create_resource import (ROOT, REGISTRY, ResourceError, cmd,
                             switch_to_resource_branch, valid_repo_path)


def update(resource_id: str, prototype: Path, source_path: str,
           expected_source_sha256: str) -> dict:
    if len(expected_source_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_source_sha256):
        raise ResourceError("Supply the exact 64-character SHA256 observed before editing")
    branch, remote_sha = switch_to_resource_branch(resource_id)
    if not remote_sha:
        raise ResourceError("No remote working branch; use /create for the first revision")
    registry = json.loads(REGISTRY.read_text())
    if resource_id not in registry:
        raise ResourceError("Resource is not registered")
    dest = valid_repo_path(source_path)
    if not dest.is_file() or not prototype.is_file():
        raise ResourceError("Current source and replacement prototype must both exist")
    current = hashlib.sha256(dest.read_bytes()).hexdigest()
    if current != expected_source_sha256:
        raise ResourceError("Resource source changed since it was read; reconcile new remote edits")
    if dest.read_bytes() == prototype.read_bytes():
        return {"resource_id": resource_id, "branch": branch, "result": "no content change"}
    shutil.copyfile(prototype, dest)
    cmd(sys.executable, "scripts/validate.py")
    rel = dest.relative_to(ROOT).as_posix()
    cmd("git", "add", "--", rel)
    cmd("git", "commit", "-m", f"Update resource {resource_id}")
    # A competing agent advancing the remote branch causes a safe push failure.
    cmd("git", "push", "origin", f"HEAD:refs/heads/{branch}")
    existing = cmd("gh", "pr", "list", "--head", branch, "--state", "open",
                   "--json", "url", "--jq", ".[0].url // empty")
    if not existing:
        existing = cmd("gh", "pr", "create", "--draft", "--base", "main", "--head", branch,
                       "--title", f"Update resource {resource_id}",
                       "--body", "Resource update for review; no publication authorized.")
    return {"resource_id": resource_id, "branch": branch, "pr": existing,
            "result": "updated shared branch; publication unchanged"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--resource-id", required=True)
    p.add_argument("--prototype", type=Path, required=True)
    p.add_argument("--source-path", required=True)
    p.add_argument("--expected-source-sha256", required=True)
    a = p.parse_args()
    try:
        print(json.dumps(update(a.resource_id, a.prototype, a.source_path,
                                a.expected_source_sha256), indent=2))
    except ResourceError as exc:
        p.exit(1, f"RESOURCE UPDATE FAILED: {exc}\n")


if __name__ == "__main__":
    main()
