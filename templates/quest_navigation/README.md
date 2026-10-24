# Quest navigation PDF template

A standalone, minimalist one-page navigation type for the Welcome PDF. Unlike the five-part Learning Cycle, this covers the full teaching sequence: Activate, five parts, Celebrate, and Next Quest or Mission.

## Rebuild
```bash
python templates/quest_navigation/render.py templates/quest_navigation/links.json /tmp/quest-navigation.pdf
```
Requires `reportlab` and DejaVu Sans installed at `/usr/share/fonts/truetype/dejavu/`.

## Updating links
Edit **only** `links.json` as teacher resources are approved/published. Existing resource IDs and canonical destinations remain owned by `catalog/resources.json`; copy the approved/current URL to the corresponding navigation key. Empty strings display **COMING SOON** with no click target. Do not fabricate or link unapproved resources.

## Inclusion
The generated page is intended to be appended as page 6 of `01_Welcome.pdf` after the Quest Kit Contents page. This template does **not** automatically modify the published Welcome PDF or publish new links. Inspect the PDF visually and check click areas before publication. It is a standalone template, not the Teacher Guide template and not a registered automatic CI build target.

## Legacy source
The sequence and Next Quest/Mission section follow `Full Guide.pdf` (v0); the revised guide and quest manifest confirm the five parts. The two populated destinations are from the GitHub resource catalog.
