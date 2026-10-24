# `claude` template: table of contents

A minimalist one-page A4 contents page styled to match the Confetti Cake Cottage School Welcome PDF (`01_Welcome_updated.pdf`).

- `TEMPLATE.json`: page title, eyebrow, footer, and entries (`title`, `summary`, optional `page`, optional `parts` list).
- `render.py`: builds the PDF with ReportLab. Entries are spaced automatically to fill the page.
- `assets/`: the school crest and Little Chewz logo (extracted from the Welcome PDF) and open-licensed fonts.

```bash
python templates/claude/render.py                      # writes exports/claude-table-of-contents.pdf
python templates/claude/render.py --data my-toc.json --output /tmp/toc.pdf
```

Fonts: the Welcome PDF uses Better Faster (commercial) and Glacial Indifference, which cannot be redistributed in full from the PDF. This template uses SIL OFL stand-ins, Sedgwick Ave Display for headlines and Outfit for body text; licences are in `assets/fonts/`.

Page numbers in `TEMPLATE.json` assume the contents page is inserted as page 2 of the Welcome PDF. Entry wording is drawn from that PDF and is `unapproved` until a human reviews it. This template is not registered with the automated PDF build.
