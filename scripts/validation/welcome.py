"""Welcome source checks; deliberately independent from Teaching Flow rules."""
from select_builds import nav_refs


def validate(ctx, source, doc):
    for ref in sorted(nav_refs(doc)):
        if ref not in ctx.registry:
            ctx.error(source, f"navigation names unknown resource {ref}")
