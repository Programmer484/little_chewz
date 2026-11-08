# Edit — prepare an exact approved candidate

Editing and merges without a release marker **never publish**. Reuse the catalogue resource ID and the shared lesson review branch, reconcile remote changes, and keep currently published Drive files untouched.

**Drive-managed files:** iterate on authoritative source, check content and presentation, then **link last**. Draft previews prefer a registered Holding URL over the previous public version of a staged dependency. Human review checks that each link opens the *right* resource, not merely that it resolves. Run `python scripts/validate.py` and relevant tests. Finish by replacing the Holding file **in place**, preserving its Drive ID, with the final artifact; record its current version/checksum and exact approval scope.

**Generated PDFs:** at the first edit, create the matching source from `templates/<type>/TEMPLATE.json`, retain the `template` key and add the catalogue `pdf.renderer` and `pdf.output` or `pdf.source` mapping. Iterate editable JSON and GitHub Actions previews, not PDF exports; **the preview is the review copy, so no Holding copy is required**. Never overwrite the live file during edits. On release, build from accepted source with public dependency links only. Never record approved MD5/revision before confirming exact published Drive bytes.

**Other Drive-managed files:** iterate worksheets, slides, artwork, letters and media through chat or the native authoring tool and stage the approved candidate in Holding. Externally hosted videos/web apps are reviewed at their actual URL instead; no Drive Holding copy is required. For revisions, hold a separate copy; do not move it over the established public file. Student-material PDFs require US Letter pages (`scripts/pdf_page_size.py`); slide PDF/PPTX pairs follow [Slide conversion](SLIDE_CONVERSION.md).

Report GitHub source/preview, staged ID and version, checks and remaining blockers. Only [Publish](PUBLISH.md), on an explicit human instruction (including a PR release marker), changes live resources.
