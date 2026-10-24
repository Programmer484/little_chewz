# `claude` template: clean page style and quest navigation

A left-aligned A4 page style for Little Chewz documents, matching the Confetti Cake Cottage School look: cream page, crest or Little Chewz logo, brush headline, coral numbers and labels, hairline dividers. It includes a quest navigation page that links each stage to its Teacher Guide.

- `TEMPLATE.json`: skeleton document showing every block type (`lede`, `paragraphs`, `list`, `callout`, `nav`).
- `render.py`: builds the PDF with ReportLab and pypdf. Each page's spacing stretches to fill the page; a page that overflows fails loudly.
- `assets/`: school crest and Little Chewz logo (extracted from the Welcome PDF) and open-licensed fonts.

Current consumer: the Quest One Welcome PDF, `content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json` (cover kept as the original artwork in `cover.pdf`).

```bash
python templates/claude/render.py \
  content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json \
  --output exports/01-welcome.pdf
```

## Navigation links

`nav` rows name a stable resource ID from `catalog/resources.json`. A row shows **Open Guide** and becomes clickable only when that entry is `approved` or `published` with an HTTPS URL; otherwise it shows **Coming Soon**. Never put Drive URLs in the document JSON.

## Fonts

The Canva originals (Better Faster, Glacial Indifference) are only partially embedded in the source PDF and Better Faster is commercial, so they cannot be reused. This template uses SIL OFL stand-ins: Sedgwick Ave Display for headlines and Outfit for body text. Licences are in `assets/fonts/`.

## Status

Rendering does not approve or publish anything. The Welcome document has no registry entry yet; add one (with its Drive destination) to track its lifecycle status. This template is not registered with the automated PDF build.
