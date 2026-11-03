# Companion resource guidelines (Draft)

Companions (question banks, extensions, answer keys and other teacher pages) support the Teacher Guide without repeating its Teaching Flow. Each must make sense when opened alone. These guidelines retain their draft status; this cleanup does not approve content.

## Writing

- Give each document one clear purpose and an activity-specific title, such as **Songwriting Extension**.
- Start with what the teacher needs to do. Include only necessary steps, prompts, materials, and examples; avoid long lesson-plan sections.
- State additional time when applicable, separately from core lesson time.
- Preserve approved content and terminology. Never invent activities to fill a template.
- Keep optional questions optional. Omit generic prompts or learning-focus sections unless they add practical value.
- Do not add a “Back to Teaching Flow” link; the resource opens in a new tab.

## Presentation

Every companion uses the shared resource masthead and footer, rendered by `scripts/renderers/teacher_companion.py`; do not restyle individual documents.

- **Masthead (page 1):** school crest, `CONFETTI CAKE COTTAGE · QUEST 01`, the section label in its accent colour (`PART 2 · SECRET INGREDIENTS`), a resource-type tag at the top right, the title, one grey meta line, then a full-width accent rule. Later pages carry a one-line running header. A guide for one lettered lesson option sets `option` (`"A"`), which adds `· OPTION A` to the section label.
- **Section and colour** come from the companion's `stage` and `quest.json`, using the Teacher Guide's section palette. Never set them by hand; colour always appears with the section name.
- **Resource-type tag** comes from `kind`: `questions`, `extension`, `answer_key`, `instructions` or `reference`. Add a new kind to `RESOURCE_TAGS` in the renderer only when a real resource needs it.
- **Title:** short and matching the resource's catalogue title, so the Teacher Guide link and the document agree. No section names or dashes in the title.
- **Meta line:** two or three short facts in `meta`: whether it is optional, added time, and when or with what to use it (`Optional · Adds about 15–25 minutes · Follows Small Bite 1: School Song`).
- **Footer:** `LITTLE CHEWZ · CHEWLANDIA ACADEMY` and `page / total` on every page.
- **Numbered lists (tight column, approved 2026-10-31):** numbers on the margin in the section colour, same size and baseline as their text; text 12 pt after the widest number. `questions` and `answers` rows are separated by hairline dividers with equal 11 pt optical space above and below; `steps` show a bold title line and are separated by whitespace only. Dividers and gaps never strand at a page edge.
- **Group labels:** `heading` blocks render as small tracked caps in the section colour, for groups such as `Core · Clue Tracker page 1`.
- No other decorative headers, badges or boxes. Use illustrations or setup photos only when they aid comprehension.
- For multiple resource variants, link the Teacher Guide to one instruction/chooser PDF that links to the separate versions.

## Activity guides

A Teacher Guide that offers lettered activity options (such as the Showdown's A–D) links one short activity guide per option (`kind: instructions`, `option` set to its letter). It is a teacher's summary with light notes on the trickiest parts to run, not a lesson plan. Start from `templates/teacher_companion/ACTIVITY_TEMPLATE.json`, which fixes the section names and order, and keep every activity guide in that shape so a teacher who has used one can scan the next:

- **Sections, in this order, each only when needed:** `Before class` (materials and setup that need lead time) → `How it runs` (timed `steps` for the guide steps it expands, each `tag` naming that step) → `Look for` (two or three `check` items from the activity's success criteria). An option-specific choice, such as a list of twists, may sit before `Look for`.
- **Write from what goes wrong.** Walk the activity step by step and note what is easiest to miss or most likely to fail: timing, supplies, logistics, safety. Put the preparation it needs in `Before class` and the fix in the step itself. Leave out generic classroom management, such as dominant voices or frustration; teachers already handle it.
- **Tips are optional and rare.** Add a short `If …` section only for a situation specific to this activity whose fix is not obvious, in one or two lines. Most guides need none; generic classroom management never qualifies.
- **Repeat nothing** from the Teacher Guide (launch, clean-up, debrief, printing, student-resource links, option totals) or from the student materials (missions on cards, recipe quantities). The meta line names the guide steps it expands and their time.
- **One page by default.** Only activities with safety risks, such as food or ovens, go longer, and then to cover everything the teacher must check so they don't have to think of it themselves. Only these use a `callout`.
- Apply the test from the Teacher Guide's Preparation rule to every line: would a teacher get this wrong, or have to improvise, without it?

## Source and generation

Companions use JSON with required `title`, `kind`, `stage` and `meta`, and optional `option` and `intro`. Start from `templates/teacher_companion/TEMPLATE.json`, which shows every block; delete the ones you do not use. Blocks mix in any order, with no minimum count, one-page requirement or decorative filler.

| Block | Use for | Renders as |
| --- | --- | --- |
| `heading` | Group label (`Before class`, `Core · Clue Tracker page 1`) | Small tracked caps in the section colour |
| `callout` | Safety warnings only: allergies, food rules, ovens, hot equipment (`title`, `text`) | Tinted panel with an accent rule; omit it when nothing can hurt anyone |
| `checklist` | `style: "box"` for prep and materials; `style: "check"` for success criteria or look-fors | Unnumbered rows with a box or tick in the number column |
| `steps` | Ordered teacher actions; items take `title`, `text`, and optionally `mins`, `tag`, `prompts` | Numbered rows; `mins` right-aligned, `tag` in grey caps after the title (e.g. `Guide step 3`), `prompts` as italic teacher lines beside an accent rule, without quotation marks |
| `questions`, `answers` | Question banks and answer keys | Numbered rows with hairline dividers |
| `pairs` | Short term–explanation tables: look-fors, troubleshooting, roles (`term`, `text`) | Bold term column with the explanation beside it, hairline dividers |
| `bullets`, `paragraph`, `note` | Plain lists, body text, small grey notes | Body or grey text |
| `links` | Registry resources by `ref`, with a short `description` | Bold underlined title and grey description |
| `image`, `spacer` | A comprehension-aiding illustration; a rare extra gap. Sections space themselves, so never use `spacer` for layout | |

Numbered blocks (`steps`, `questions`, `answers`) number continuously across a document; set `start` on a block to restart. A step's `tag` may point to the Teacher Guide step it expands; keep the guide's step structure rather than repeating its Teaching Flow. Add a new block type to `scripts/renderers/teacher_companion.py` only when real content needs it.

Use the ownership and approved-link rules in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). Layout implementation lives in `scripts/renderers/teacher_companion.py`; follow [WORKFLOW.md](WORKFLOW.md) for checking, previews, and publication. See [START_HERE.md](../START_HERE.md#local-checks-and-approved-previews) for current commands.
