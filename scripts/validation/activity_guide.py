"""Only the extra layout/section contract for activity guides."""
SECTIONS = ("Before class", "Choose one", "How it runs", "Tips")


def validate(ctx, source, doc):
    if doc.get("kind") != "instructions" or not doc.get("option"):
        ctx.error(source, 'activity guide needs kind "instructions" and an option letter')
    ranks = []
    seen_heading = False
    for block in doc.get("blocks", []):
        typ = block.get("type")
        if typ == "spacer":
            ctx.error(source, "activity guide must not use spacer blocks; sections space themselves")
        if typ == "callout" and seen_heading:
            ctx.error(source, "activity guide callout (Safety first) must come before the first section")
        if typ != "heading":
            continue
        seen_heading = True
        title = block.get("text", "")
        rank = next((i for i, name in enumerate(SECTIONS)
                     if title == name or (name == "Choose one" and title.startswith(name))), None)
        if rank is None:
            ctx.error(source, f"activity guide section {title!r} is not one of Before class, Choose one …, How it runs, Tips")
        else:
            ranks.append(rank)
    if ranks != sorted(ranks) or len(ranks) != len(set(ranks)):
        ctx.error(source, "activity guide sections must appear once each, in template order")
    if 2 not in ranks:
        ctx.error(source, "activity guide needs a 'How it runs' section")
