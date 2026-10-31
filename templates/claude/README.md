# `claude` template: clean page style and quest navigation

A left-aligned A4 page style for Little Chewz documents, matching the Confetti Cake Cottage School look: cream page, crest or Little Chewz logo, brush headline, coral numbers and labels, hairline dividers. It includes a quest navigation page that links each stage to its Teacher Guide.

- `TEMPLATE.json`: skeleton document showing every block type (`lede`, `paragraphs`, `list`, `callout`, `nav`).
- Renderer: [`scripts/renderers/claude.py`](../../scripts/renderers/claude.py), with ReportLab and pypdf. Each page's spacing stretches to fill the page; a page that overflows fails loudly.
- `assets/`: school crest and Little Chewz logo (extracted from the Welcome PDF) and open-licensed fonts. New artwork goes here as separate files, never as a pre-rendered full page ([asset rule](../../system/CONTENT_CONTRACT.md#resources-slides-and-assets)).

```bash
python scripts/renderers/claude.py \
  content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json \
  --output exports/01-welcome.pdf
```

## Navigation links

`nav` rows name a stable resource ID from `catalog/resources.json`. A row shows **Open Guide** and becomes clickable only when that entry is `pending_publish` or `published` with an HTTPS URL; otherwise it shows **Coming Soon**. Never put Drive URLs in the document JSON.

## Fonts

The Canva originals (Better Faster, Glacial Indifference) are only partially embedded in the source PDF and Better Faster is commercial, so they cannot be reused. This template uses SIL OFL stand-ins: Lobster for headlines and Outfit for body text. Licences are in `assets/fonts/`.

## Status and builds

A document using this style is registered in `catalog/resources.json` with `"build": {"renderer": "claude", "source": "<path to its JSON>"}`. That makes it a PR preview target named `<resource-id>.pdf`, rebuilt when its JSON, anything in its folder, these assets, or the renderer changes. The same build feeds **Publish to Drive** ([PUBLISH.md](../../system/PUBLISH.md)). Rendering does not publish anything.

Current consumer: the Quest One Welcome PDF (`ccc-q01-welcome`).
