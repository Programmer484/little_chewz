"""Describe which inputs can change each rendered PDF.

Nested blocks use path conventions (`path`, `asset`, `assets`, `icon`, etc.),
rather than a list of block types. Local Python imports are discovered, so a
new renderer helper automatically belongs to that renderer's dependency graph.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

# Any block may reference assets using these conventional fields. A novel
# block type needs no selector change; unusual assets can use `dependencies`.
ASSET_KEYS = frozenset({
    "cover", "icon", "path", "asset", "assets", "image", "images",
    "file", "files", "font", "fonts", "dependencies",
})
# Files used implicitly by a renderer, independent of authored JSON blocks.
RENDERER_ASSETS = {
    "teacher_guide": ("templates/fonts/",),
    "teacher_companion": ("templates/fonts/", "templates/welcome/assets/crest.png"),
    "welcome": ("templates/welcome/assets/",),
}
# Real build inputs shared by every output; the workflow and validation code
# are deliberately not on this list.
SHARED_BUILD_INPUTS = frozenset({"scripts/build_selected.py", "requirements.txt"})


@dataclass(frozen=True)
class Inputs:
    files: frozenset[str]
    folders: frozenset[str]

    def affected_by(self, changes: set[str]) -> bool:
        return not self.files.isdisjoint(changes) or any(
            path.startswith(folder) for path in changes for folder in self.folders
        )


def local_path(value: str, base: Path) -> str | None:
    """Resolve an authored relative file path without leaving the repository."""
    if not value or urlsplit(value).scheme or value.startswith("//"):
        return None
    path = Path(value)
    if path.is_absolute():
        return None
    try:
        return (ROOT / base / path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None


def source_assets(data: object, source: str) -> Inputs:
    """Collect asset file paths from nested content, regardless of block type."""
    files, folders = set(), set()
    base = Path(source).parent

    def collect(value):
        if not isinstance(value, str):
            return
        rel = local_path(value, base)
        if not rel:
            return
        if value.endswith("/") or (ROOT / rel).is_dir():
            folders.add(rel.rstrip("/") + "/")
        else:
            files.add(rel)

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in ASSET_KEYS:
                    if isinstance(child, str):
                        collect(child)
                    elif isinstance(child, list):
                        for item in child:
                            collect(item)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    return Inputs(frozenset(files), frozenset(folders))


@lru_cache(maxsize=None)
def python_imports(entry: str) -> frozenset[str]:
    """Follow local Python imports so helper changes select their consumers."""
    files, pending = set(), [entry]
    while pending:
        path = pending.pop()
        if path in files:
            continue
        files.add(path)
        src = ROOT / path
        if not src.is_file():
            continue
        tree = ast.parse(src.read_text(encoding="utf-8"), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = ([node.module] if node.module else [])
                if node.module:
                    modules += [node.module + "." + alias.name for alias in node.names]
                if node.level:
                    base = src.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    modules += [
                        base.relative_to(ROOT).as_posix().replace("/", ".") + "." + name
                        for name in modules
                    ]
            else:
                continue
            for module in modules:
                stem = Path(*module.split("."))
                for candidate in (
                    src.parent / stem,
                    ROOT / "scripts/renderers" / stem,
                    ROOT / "scripts" / stem,
                    ROOT / stem,
                ):
                    file = candidate.with_suffix(".py")
                    if file.is_file():
                        rel = file.relative_to(ROOT).as_posix()
                        if rel not in files:
                            pending.append(rel)
                        break
    return frozenset(files)


def inputs_for(target: dict) -> Inputs:
    """Exact dependencies for a registered PDF, including its active template."""
    source, kind = target["source"], target["kind"]
    assets = source_assets(target["data"], source)
    files = set(SHARED_BUILD_INPUTS) | {source} | set(assets.files)
    folders = set(assets.folders)
    files.update(python_imports(f"scripts/renderers/{kind}.py"))
    for path in RENDERER_ASSETS.get(kind, ()):
        if path.endswith("/"):
            folders.add(path)
        else:
            files.add(path)
    # Template-specific assets apply to that template's consumers only.
    template = target["data"].get("template", kind)
    folders.add(f"templates/{template}/assets/")
    # Companion mastheads derive the stage/quest wording from quest.json.
    if kind == "teacher_companion":
        for parent in (ROOT / source).parents:
            if parent == ROOT.parent:
                break
            quest = parent / "quest.json"
            if quest.is_file():
                files.add(quest.relative_to(ROOT).as_posix())
                break
    return Inputs(frozenset(files), frozenset(folders))
