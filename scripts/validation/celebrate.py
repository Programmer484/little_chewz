"""Only the extra contract for Celebrate teacher guides."""


def validate(ctx, source, doc):
    labels = [size.get("label") for size in doc.get("sizes", [])]
    if (not labels or len(labels) != len(set(labels))
            or not all(isinstance(label, str) and len(label) == 1 for label in labels)):
        ctx.error(source, "celebrate guide needs party sizes with unique one-letter labels")
    if not (doc.get("invitation") or {}).get("headline"):
        ctx.error(source, "celebrate guide needs an invitation headline")
    for step in doc.get("steps", []):
        unknown = set(step.get("sizes", [])) - set(labels)
        if unknown:
            ctx.error(source, f'celebrate step {step.get("id")} names undefined sizes {sorted(unknown)}')
    count = (doc.get("finale") or {}).get("step_count", 0)
    if (not isinstance(count, int) or isinstance(count, bool)
            or not 0 <= count < len(doc.get("steps", []))):
        ctx.error(source, "celebrate finale step_count must leave at least one Teaching Flow step")
    note = (doc.get("finale") or {}).get("teacher_note")
    if note is not None:
        if not (isinstance(note, dict)
                and all(note.get(key) for key in ("label", "headline", "text", "ref"))):
            ctx.error(source, "celebrate finale teacher_note needs label, headline, text and ref")
        # Reference existence is checked in the shared recursive reference pass.
