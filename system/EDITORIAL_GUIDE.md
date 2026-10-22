# Little Chewz — Canonical Teacher Guide / LLM Instructions

**Scope:** These instructions apply to every AI or editor drafting or revising Little Chewz teacher-guide content and to any AI working on the teacher-guide generator. Use **Full Guide Revised.pdf** as the editorial and visual benchmark; use the **latest approved** lesson sequence and slideshow for content. This file governs *writing*, while generator code governs *rendering*.


File locations and source authority are defined in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). Edit the current lesson source under `content/`; layout implementation lives in `scripts/renderers/teacher_guide.py`. Validation, review, and delivery follow [WORKFLOW.md](WORKFLOW.md).

## 1. Primary editorial rule

**Tell teachers only what they need to do next.** Write concise, practical instructions in the tone of the Revised Full Guide. Eliminate the obvious, redundant reminders, repeated slide content, lengthy explanations, and instructions that don't change what the teacher does.

Keep the existing section structure and terminology unless instructed otherwise: At a Glance, Learning goal, Learning outcomes, Preparation, Teaching focus, Teaching Flow, and purposeful optional extensions. **Assessment is optional** and, when used, appears as a standalone section below Teaching focus. Never add an assessment task that is missing from the Teaching Flow.

## 2. Learning design: goal, outcomes, focus and assessment

**Learning goal**
- One concise sentence identifying the central educational purpose.
- Describe the learning, not a list of activities.

**Learning outcomes**
- Normally **three** short, observable, student-centred statements, roughly the length of the original guide.
- Begin with a useful action verb such as **ask, identify, describe, explain, compare, apply, reflect**.
- Avoid vague outcomes such as “understand” or “explore” without visible evidence of what students can do.
- Do not write “By the end of Activate…” or any equivalent introductory preamble.
- Fit the evidence and demands of the actual lesson; do not introduce assessment tasks or predictions students have not yet been equipped to make.

**Teaching focus**
- **One short sentence; one instructional priority.** Write in the direct, practical tone of the original guide.
- Avoid multiple “listen for / check / prompt” demands, and avoid assessment boilerplate.

**Assessment — optional**
- Include an Assessment section **only when it adds specific guidance beyond Teaching focus**, such as explaining what to look for in selected worksheets, activity products, or performance tasks. Omit it entirely for Activate, celebrations, or any lesson where Teaching focus already supplies sufficient guidance.
- **Assessment is not an additional activity**. Do not ask teachers to administer extra exit slips, worksheets, discussion questions, checks, or marking steps that do not already appear in the Teaching Flow.
- Tie evidence to the materials and choices **already listed in the Teaching Flow**. For choice-based lessons, give short resource-specific indicators so the teacher uses only the lines for activities selected (e.g., `Clue Tracker: identifies relevant evidence and a reasonable inference`).
- Describe **observable student thinking or work**, not vague participation; never assume every learner demonstrated understanding because a few students answered aloud.
- Do not duplicate Learning outcomes or Teaching focus; give practical evidence cues that a teacher can recognize from existing student responses, notes, discussion, or work.
- Brief, formative wording only. No formal grading or new rubric unless the chosen activity already requires one.
- In lesson JSON, **omit `assessment`**, set it to `null` or `""`, or use `[]` to hide the section. To include it, use a short string or an array of concise material-specific bullet strings. The PDF generator will include the section only when there is content.

**Approved Activate model**

Learning goal: Spark curiosity about Confetti Cake Cottage School and introduce the Zenix approach to solving mysteries through careful observation, thoughtful questions, and understanding different perspectives.

Learning outcomes:
1. Ask thoughtful questions about the school and its mysteries.
2. Identify an unusual detail about Callie Cupcake.
3. Explain why Zenix gather information and consider different perspectives before judging.

Teaching focus: Encourage students to seek understanding before making judgments.

Assessment: Omitted — Teaching focus is sufficient for Activate.

## 3. Resource labels, descriptions, and links

**Presentation pattern:** **Linked Resource Title** `—` concise, light-grey description. In generated PDFs the linked title is **bold and underlined**; the em dash and description are **light grey**. A title may appear alone when no description adds value.

- **All resource-registry items must have working approved links.** Do not allow unlinked resource names as a fallback; missing destinations are errors to resolve before release.
- **Underline means hyperlink** and nothing else. Do not underline ordinary text for emphasis.
- Keep descriptions brief and functional: e.g. `Mrs. Tongsley's Letter — Opening read-aloud`, `Chapter One — Full chapter`, `Teacher Answer Key — Teacher reference`.
- Never invent link targets or replace a missing approved resource with a guessed URL.
- Keep extra questions, full stories, student-facing material, worksheets, answer keys, and supporting resources in their **separate linked files**.
- Each lesson has **its own slide set/deck**. Link only that lesson's approved slideshow in Preparation. In Teaching Flow, `SHOW`/`KEEP` slide numbers are local to the lesson and must be verified against its current approved slides. Historical quest-wide slide numbers are not current lesson numbers.
- A command such as `SHOW Slides 1–3 — Introduce the school.` is slide navigation, **not** a separately linked resource entry. `KEEP Slide 3 — Display during the welcome letter.` is likewise slide navigation.

**Preparation should be a resource list, not an instruction paragraph.** Its purpose is to show what the teacher needs ready before class.

- Under **CORE RESOURCES**, list the lesson slideshow and materials used by every student or class, with one linked resource title per line.
- When activities offer alternatives, use **PREPARE YOUR CHOICES** for choice-dependent materials. Reserve **OPTIONAL PREPARATION** for extras that are not tied to an activity choice.
- Give each resource a short `—` description only when useful, such as which choice uses it or how many copies to prepare (`One per student`, `One per group of 3–4`). Keep activity directions in Teaching Flow.
- Omit activities that require no separate resources or printing and routine classroom supplies. Do not compress resource lists into an italic `prep_note` paragraph or repeat listed materials in prose; use a note only for essential setup information that cannot fit on a resource line.

## 4. Approved Teaching Flow action labels

Prefer this deliberately small vocabulary; use the label only when the action genuinely adds information.

| Label | Meaning |
| --- | --- |
| **SHOW** | Display or advance to specified slide(s); play media embedded on a slide. |
| **KEEP** | Remain on a named slide during the following action or passage. |
| **READ** | Read an approved short passage aloud or open a linked reading. |
| **ASK** | Ask the strongest, most relevant discussion question. |
| **DO** | Give a short, concrete classroom direction. |
| **GIVE** | Distribute or direct students to a linked student resource. |
| **MORE** | Link supplementary teacher resources or additional prompts. |

Avoid `NOTE`, `WATCH`, `CHECK`, `TIME`, `USE`, `OR`, and `CHOICE` as action labels. Do not create near-synonyms. For genuine alternatives, use `DO` to direct the teacher to select one, and identify the options (A/B/C/D) in the instruction text rather than as separate action labels. The choices must reflect real alternatives available to the teacher. Use `SHOW` for media on a slide, or `DO` with a linked resource for standalone audio.

**For engineering:** [action_labels.json](action_labels.json) owns the allowed labels and internal row types; the table explains usage. The validator and renderer must consult that file when checking validity. Rendering branches for specialized content are still appropriate.

## 5. How to write a Teaching Flow step

- Use the established **number, title, duration**, then brief labelled action rows.
- Start with the **action**. Prefer compact imperatives over explanations: `DO Pair-share for two minutes.`
- Give **one meaningful instruction per row**; avoid long paragraphs unless the paragraph itself is an approved READ excerpt.
- Follow the classroom sequence. Do not introduce the task twice (once in the title and again in the first row).
- Use the minimum number of rows needed; do not pad steps with SHOW/ASK/DO by habit.
- Give **one strong ASK question**. Put optional extra questions under MORE as linked resources.
- Say what teachers need to *do*, not why each step is pedagogically important.
- Do not repeat the wording on the slide or narrate what the video already says.
- Use exact slide numbers/ranges from the **current approved lesson slide set**, not from a historical quest-wide deck.
- Avoid navigation-only rows. Mention a transition only when it changes what the teacher needs to do.
- Follow the concise writing of **Full Guide Revised.pdf**, not the wordier Activate Teacher Guide phrasing.

**Example of preferred brevity**

```text
SHOW   Slide 5 — Play Mrs. Tongsley's video.
ASK    What are you wondering about after her message?
MORE   Mrs. Tongsley's Video — Direct video preview. [linked resource]
```

**Slide continuity**

```text
SHOW   Slides 1–3 — Introduce the school.
KEEP   Slide 3 — Display during the welcome letter.
READ   Mrs. Tongsley's Letter — Opening read-aloud. [linked resource]
```

Use KEEP only when staying on the slide is a meaningful instruction, not on every row that happens to leave a slide visible.

**A/B alternatives:** Preserve the original four-page Set the Table teaching-flow style. For a lesson with choices, set `flow_style: "compact"` and put each alternative under `step.options` with `label` (A/B), `title`, and its own `rows`. Do not flatten alternatives into ordinary rows prefixed `A —` or `B —`. Every Teaching Flow, with or without options, uses one shared grid (44 / 82 / 129 / 551 pt): step numbers at 44; options mirror the step heading one level down (a heavy accent letter about 13% larger than its bold option title, right-aligned just before it, the same ratio as step number to step title). Step numbers and option letters are vertically centred on their title (text-box middles aligned); step titles set tight beside the number (just past the widest two-digit number) so options read as indented subsets of the step; option titles and action labels at 82 in every step; instruction text at 129; times and page counters right-aligned at 551. Labels share a baseline with their text, option rows use the same type as ordinary rows, options are separated by a 0.5 pt warm-grey rule from 82 pt, and every divider has equal optical space above and below. Spacing values live as named constants at the top of the layout section in `scripts/renderers/teacher_guide.py`. Longer or revised activities may move later sections down without changing the option typography and spacing.

## 6. READ passages and excerpts

- For an approved, short passage, use the existing **indented READ passage with a coloured vertical rule**, preserving paragraph breaks and selective bold emphasis. **Do not add literal quotation marks.**
- Include excerpts only for short passages **under approximately 250 words**; this is authorial guidance, **not a programmed word-count check**.
- For longer readings, link to the **full resource** and ask the teacher to open/read it. Do not paste full student-facing stories or lengthy teacher resources into the Teacher Guide.
- Preserve the approved wording of any passage. Do not silently rewrite dialogue, lore, named characters, or the Zenix rule.
- The presence of an excerpt does not make it an unlinked resource-registry item; an explicit resource reference still requires a link.

## 7. Generator engineering boundaries

- Preserve existing PDF-native style, Lato typography, section-colour configuration, page margins and other deliberate design choices unless a change is requested.
- Handle typesetting, mixed emphasis, hyperlinks, measurable fitting/wrapping, whole-step pagination, continuation cues and destination integrity **in code**.
- Handle tone, step concision, vocabulary, passage length, exact educational priority and pedagogy **in these LLM instructions**, not in brittle heuristic validators.
- **Keep missing-resource links as errors.** Do not weaken existing strict link behaviour.
- Do **not** introduce a code-enforced 250-word limit, a banned-`NOTE` special case, or hard-coded length checks for Learning outcomes/Teaching focus.
- Prefer minimal, localized changes and data-driven configuration. Keep content and layout responsibilities separate; do not duplicate source text inside rendering functions.
- Follow the workflow for rendered-output review. Report layout discrepancies rather than silently changing approved text to fit.

## 8. Editorial review

- Are the goal, outcomes and Teaching focus **short** and tightly aligned to the actual activities?
- If Assessment is included, does it identify evidence within the selected existing materials, without adding a task or duplicating Teaching focus?
- If Assessment adds no distinct value, has it been omitted rather than padded with boilerplate?
- Does Teaching focus convey **one** idea?
- Could a teacher scan every step and act without rereading it?
- Have explanatory filler and redundant rows been removed?
- Does `KEEP Slide N` clearly cover each important continuity instruction?
- Are all resource references linked, bold and underlined, with concise grey `— descriptions` where useful?
- Are slide numbers verified against the corresponding lesson-specific slideshow?
- Are passages short, properly indented, and faithful to approved source text?
- Are links, resource names, page breaks, accents and wording checked before publishing?

## 9. MORE resources and alternatives

- Use **MORE**, not **EXTEND**, as the standard Teaching Flow label for optional linked resources. The generator already supports multiple resource lines under a single MORE label.
- Present each resource as **bold, underlined linked title** followed by a short light-grey `— description`, such as `Mission Video Questions — Additional questions`.
- In Teaching Flow, the linked resource title and description (including **MORE** rows) use the same standard body font size as **DO** instructions. Do not shrink linked descriptions to fit; shorten the wording or adjust the shared layout instead.
- Put supplementary discussion questions in separate linked PDFs, not in the core teacher-guide flow.
- When a video has a written alternative, keep the video in SHOW and link the readable source under MORE, e.g. `Bakery Log (1958) — Read-aloud alternative to video`.
- Do not create a new mandatory teaching step for an optional extension or fallback.

## Illustrated teacher instructions vs optional question banks

- Keep the Teacher Guide itself concise and scannable. Do not put full supporting resources or redundant artwork in the core flow.
- Use an illustrated standalone teacher-resource page where a visual genuinely demonstrates setup, printing, assembly, or student use (for example, the School Pass).
- Keep additional question banks minimally designed: clear title, readable questions, and necessary context. Do not decorate at the expense of scanning speed.
- For a resource with multiple format variants, link the Teacher Guide to a single teacher-facing instruction or chooser PDF, then link from that PDF to each separately hosted version.
- Preserve stable file links and use approved HTTPS destinations from the central resource registry; avoid embedding large materials in the Teacher Guide.
