# `welcome` template: clean page style and quest navigation

A left-aligned A4 page style for Little Chewz documents, matching the Confetti Cake Cottage School look: cream page, crest or Little Chewz logo, brush headline, coral numbers and labels, hairline dividers. It includes a quest navigation page that links each stage to its Teacher Guide.

- `TEMPLATE.json`: skeleton document showing every block type (`lede`, `paragraphs`, `list`, `callout`, `founder`, `nav`).
- Renderer: [`scripts/renderers/welcome.py`](../../scripts/renderers/welcome.py), with ReportLab and pypdf. Each page's spacing stretches to fill the page; a page that overflows fails loudly.
- `assets/`: school crest, Little Chewz logo and founder portrait (`lisa-trout.jpg`, used by the `founder` block's `photo`), extracted from the original Welcome PDF, and open-licensed fonts. New artwork goes here as separate files, never as a pre-rendered full page ([asset rule](../../system/CONTENT_CONTRACT.md#resources-slides-and-assets)).

```bash
python scripts/renderers/welcome.py \
  content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json \
  --output exports/01-welcome.pdf
```

## Navigation links

`nav` rows name a stable resource ID from `catalog/resources.json`. A row shows **Open Guide** and becomes clickable only when that entry has an official HTTPS `published_url`; otherwise it shows **Coming Soon**. Never put Drive URLs in the document JSON.

## Fonts

The Canva originals (Better Faster, Glacial Indifference) are only partially embedded in the source PDF and Better Faster is commercial, so they cannot be reused. This template uses SIL OFL stand-ins: Lobster for headlines and Outfit for body text. Licences are in `assets/fonts/`.

## Status and builds

A document using this style is registered in `catalog/resources.json` with `"pdf": {"renderer": "welcome", "source": "<path to its JSON>"}`; its editable JSON declares `"template": "welcome"`. The preview output is `<resource-id>.pdf`. The selector finds local file references in the JSON automatically, rebuilds for renderer/shared-asset changes, and safely rebuilds when an input cannot be attributed. The same renderer feeds **Actions → Publish** ([PUBLISH.md](../../system/PUBLISH.md)); rendering alone never publishes.

Current consumer: the Quest One Welcome PDF (`ccc-q01-welcome`).
