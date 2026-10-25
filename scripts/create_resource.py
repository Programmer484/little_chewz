#!/usr/bin/env python3
"""Create or update a prototyped resource on its one shared edit/<id> branch.

Never publishes. Uses a fresh remote head, a GitHub PR, and non-force push.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "catalog/resources.json"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PRODUCTION_TYPES = {"generated_pdf", "external"}


class ResourceError(Exception):
    pass


def cmd(*args: str, check: bool = True) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode:
        raise ResourceError(f"{' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def valid_repo_path(value: str) -> Path:
    candidate = Path(value)
    if (candidate.is_absolute() or not candidate.parts or ".." in candidate.parts
            or candidate.parts[0] not in {"content", "templates"}):
        raise ResourceError("Source and asset destinations must stay inside content/ or templates/")
    resolved = (ROOT / candidate).resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise ResourceError("Resource path escapes repository")
    return resolved


def resource_id(quest_id: str, slug: str) -> str:
    if not ID_RE.fullmatch(quest_id) or not ID_RE.fullmatch(slug):
        raise ResourceError("Quest ID and slug must be stable lowercase kebab-case")
    return f"{quest_id}-{slug}"


def registration(rid: str, title: str, kind: str, production: str,
                 source_path: str | None, build_output: str | None = None,
                 build_renderer: str | None = None) -> dict:
    if not ID_RE.fullmatch(rid):
        raise ResourceError("Resource ID must use lowercase kebab-case")
    if production not in PRODUCTION_TYPES or not title.strip() or not kind.strip():
        raise ResourceError("Title, type, and production_type are required")
    if source_path is not None:
        valid_repo_path(source_path)
    result = {"title": title, "type": kind, "production_type": production,
              "audience": "teacher", "tags": [], "status": "unpublished"}
    if source_path:
        result["source"] = {"kind": "github", "path": source_path}
    else:
        result["source"] = {"kind": "external_original", "location": "unrecorded"}
    if production == "generated_pdf":
        if not source_path:
            raise ResourceError("Generated PDFs require editable GitHub source")
        if bool(build_output) == bool(build_renderer):
            raise ResourceError("Supply exactly one --build-output or --renderer for generated PDF")
        if build_output:
            if "/" in build_output or not build_output.endswith(".pdf"):
                raise ResourceError("Registered build output must be a PDF filename")
            result["build"] = {"output": build_output}
        else:
            result["build"] = {"renderer": build_renderer, "source": source_path}
    elif build_output or build_renderer:
        raise ResourceError("External materials never declare Python PDF builds")
    return result


def reconcile(registry: dict, rid: str, new: dict) -> tuple[dict, bool]:
    existing = registry.get(rid)
    if existing is not None:
        if existing.get("type") != new["type"]:
            raise ResourceError("Existing stable resource ID has a different type")
        if existing.get("production_type", new["production_type"]) != new["production_type"]:
            raise ResourceError("Existing resource ID has a different production classification")
        if existing.get("title") != new["title"]:
            raise ResourceError("Resource title differs; use /update instead of creating a duplicate")
        return registry, False
    for other_id, item in registry.items():
        if item.get("title", "").casefold() == new["title"].casefold():
            raise ResourceError(f"Similar resource already registered as {other_id}; reconcile identity")
    registry[rid] = new
    return registry, True


def prepare_source(rid: str, prototype: Path | None, destination: str | None,
                   production: str, kind: str) -> list[str]:
    if not destination:
        if production == "generated_pdf":
            raise ResourceError("Generated PDF must have a repository source path")
        return []
    dest = valid_repo_path(destination)
    if prototype is None:
        if not dest.is_file():
            raise ResourceError("Resource prototype is required; no file exists at source path")
        return [dest.relative_to(ROOT).as_posix()]
    if not prototype.is_file():
        raise ResourceError(f"Prototype not found: {prototype}")
    if dest.is_file():
        if dest.read_bytes() != prototype.read_bytes():
            raise ResourceError("Destination already contains different content; use /update")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(prototype, dest)
    if kind == "teacher_companion" and dest.suffix == ".json":
        data = json.loads(dest.read_text())
        if data.get("resource_id") != rid:
            raise ResourceError("Companion prototype must contain matching resource_id")
    return [dest.relative_to(ROOT).as_posix()]


def switch_to_resource_branch(rid: str) -> tuple[str, str]:
    if cmd("git", "status", "--porcelain"):
        raise ResourceError("Working tree is not clean; save or reconcile it before switching")
    cmd("git", "fetch", "--no-tags", "origin", "main")
    branch = f"edit/{rid}"
    remote = cmd("git", "ls-remote", "--heads", "origin", branch)
    if remote:
        remote_sha = remote.split()[0]
        cmd("git", "fetch", "--no-tags", "origin", branch)
        local = cmd("git", "branch", "--list", branch)
        if local:
            cmd("git", "switch", branch)
            # Non-fast-forward local work must be reconciled, not discarded.
            cmd("git", "merge", "--ff-only", "FETCH_HEAD")
        else:
            cmd("git", "switch", "-c", branch, "FETCH_HEAD")
        if cmd("git", "rev-parse", "HEAD") != remote_sha:
            raise ResourceError("Resource branch moved during checkout")
    else:
        cmd("git", "switch", "-c", branch, "refs/remotes/origin/main")
        remote_sha = ""
    return branch, remote_sha


def create(args) -> dict:
    rid = args.resource_id or resource_id(args.quest_id, args.slug)
    new = registration(rid, args.title, args.type, args.production_type,
                       args.source_path, args.build_output, args.renderer)
    branch, remote_start = switch_to_resource_branch(rid)
    # Catalogue is loaded only AFTER fetching and switching to the current branch.
    catalogue = json.loads(REGISTRY.read_text(encoding="utf-8"))
    catalogue, added = reconcile(catalogue, rid, new)
    paths = prepare_source(rid, args.prototype, args.source_path,
                           args.production_type, args.type)
    if added:
        REGISTRY.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        paths.append("catalog/resources.json")
    if not paths and not added:
        return {"resource_id": rid, "branch": branch, "result": "reused existing resource"}
    cmd(sys.executable, "scripts/validate.py")
    cmd("git", "add", "--", *paths)
    if not cmd("git", "diff", "--cached", "--name-only"):
        return {"resource_id": rid, "branch": branch, "result": "no changes"}
    cmd("git", "commit", "-m", f"Create resource {rid}")
    # git push is fast-forward-only; stale parallel edits cause a safe failure.
    cmd("git", "push", "origin", f"HEAD:refs/heads/{branch}")
    # A failed PR creation doesn't discard the pushed source.
    existing = cmd("gh", "pr", "list", "--head", branch, "--state", "open",
                   "--json", "url", "--jq", ".[0].url // empty")
    if existing:
        url = existing
    else:
        url = cmd("gh", "pr", "create", "--draft", "--base", "main", "--head", branch,
                  "--title", f"Resource: {args.title}", "--body",
                  f"Create and preview {rid}. No publication authorized.")
    return {"resource_id": rid, "branch": branch, "previous_remote_sha": remote_start,
            "pr": url, "result": "pushed for preview; unpublished"}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--resource-id")
    p.add_argument("--quest-id", default="ccc-q01")
    p.add_argument("--slug")
    p.add_argument("--title", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--production-type", required=True, choices=sorted(PRODUCTION_TYPES))
    p.add_argument("--prototype", type=Path, help="Already prototyped source or original")
    p.add_argument("--source-path", help="Repository destination for editable source")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--build-output", help="Existing selector output for generated PDFs")
    group.add_argument("--renderer", help="Registry-built PDF renderer")
    args = p.parse_args()
    if not args.resource_id and not args.slug:
        p.error("Provide --resource-id or --slug")
    try:
        print(json.dumps(create(args), indent=2))
    except ResourceError as exc:
        p.exit(1, f"RESOURCE CREATE FAILED: {exc}\n")


if __name__ == "__main__":
    main()
