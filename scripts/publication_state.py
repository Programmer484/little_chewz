"""Derive each resource's publication state from its publication evidence.

Only generated PDFs use source/approved MD5 comparisons. Every other resource
uses its current official and genuinely distinct holding destinations.
Missing checksums are not evidence of equality: auditing reports them separately.
"""
from __future__ import annotations

from urllib.parse import urlsplit


def identity(url: str | None) -> str | None:
    if not url:
        return None
    p = urlsplit(url)
    if p.hostname in {"drive.google.com", "docs.google.com"}:
        parts = p.path.split("/")
        for marker in ("d", "folders"):
            if marker in parts:
                i = parts.index(marker) + 1
                if i < len(parts) and parts[i]:
                    return "drive:" + parts[i]
    # For external sites a changed query can actually identify a new media file.
    return (p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), p.query)


def has_official_version(resource: dict | None) -> bool:
    return bool(resource and resource.get("published_url"))


def publication_status(resource: dict | None, current_md5: str | None = None) -> str:
    if not has_official_version(resource):
        return "unpublished"
    holding = identity(resource.get("holding_url"))
    published = identity(resource.get("published_url"))
    if holding is not None and holding != published:
        return "pending_publish"
    if resource.get("pdf"):
        approved = (resource.get("pdf") or {}).get("approved_md5")
        if approved and current_md5 and current_md5 != approved:
            return "pending_publish"
    return "published"



def status_report(registry: dict, *, only: str | None = None, builder=None) -> list[dict]:
    """Build generated PDFs on demand to calculate current source-vs-approved parity.

    Never writes to the catalogue or Drive. An unavailable checksum is a
    verification limitation, not proof of a pending change.
    """
    from hashlib import md5
    from pathlib import Path
    if only and only not in registry:
        raise ValueError("Unknown resource: " + only)
    result = []
    for rid, resource in registry.items():
        if only and rid != only:
            continue
        status = publication_status(resource)
        item = {"resource_id": rid, "status": status}
        if resource.get("pdf") and has_official_version(resource):
            approved = (resource.get("pdf") or {}).get("approved_md5")
            if not approved:
                item["verification"] = "unknown"
                item["checksum_evidence"] = "NEEDS REVIEW: approved MD5 unavailable"
            else:
                try:
                    if builder is None:
                        from publish_to_drive import build_pdf
                        source = build_pdf(rid, resource["pdf"])
                    else:
                        source = builder(rid, resource["pdf"])
                    actual = md5(Path(source).read_bytes()).hexdigest()
                    item["status"] = publication_status(resource, actual)
                    item["verification"] = "match" if actual == approved else "changed"
                    item["checksum_evidence"] = item["verification"]
                except Exception as exc:
                    item["verification"] = "unknown"
                    item["checksum_evidence"] = "NEEDS REVIEW: " + str(exc)
        result.append(item)
    return result



def lesson_status_report(registry: dict, quest_index: dict, read_quest, builder=None) -> list[dict]:
    """Derive each lesson's state from its registered Teacher Guide resource.

    A lesson needs no publication fields in quest.json. Guide pdf.output is the
    existing explicit mapping; checksum comparison uses status_report unchanged.
    """
    guides = {}
    for rid, resource in registry.items():
        build = resource.get("pdf") or {}
        output = build.get("output") if build.get("renderer") == "teacher_guide" else None
        if output:
            if output in guides:
                raise ValueError(f"Duplicate generated PDF output: {output}")
            guides[output] = rid

    result = []
    for school in quest_index["school_index"]:
        quest = read_quest(school["quest_manifest"])
        for lesson in quest["learning_sequence"]:
            output = f"{lesson['folder']}-teacher-guide.pdf"
            rid = guides.get(output)
            state = status_report(registry, only=rid, builder=builder)[0] if rid else {
                "status": "unpublished"}
            result.append({
                "quest_id": quest["id"],
                "lesson_folder": lesson["folder"],
                "lesson_title": lesson["title"],
                "guide_resource_id": rid,
                "status": state["status"],
                **({"checksum_evidence": state["checksum_evidence"]}
                   if "checksum_evidence" in state else {}),
            })
    return result


if __name__ == "__main__":
    import argparse
    import json
    from publish_to_drive import load_registry

    parser = argparse.ArgumentParser(description="Derived publication status; read-only")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--resource-id")
    group.add_argument("--lessons", action="store_true",
                       help="Report each lesson's state from its Teacher Guide resource")
    args = parser.parse_args()
    registry = load_registry()
    if args.lessons:
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        quest_index = json.loads((root / "catalog/quests.json").read_text())
        read_quest = lambda name: json.loads((root / name).read_text())
        report = lesson_status_report(registry, quest_index, read_quest)
    else:
        report = status_report(registry, only=args.resource_id)
    print(json.dumps(report, indent=2))
