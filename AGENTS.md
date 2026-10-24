# Little Chewz — AI instructions

This is an editable educational source repository. PDFs are outputs; legacy PDFs are inputs only while awaiting conversion.

**No repository access?** [AI_BRIEF.md](AI_BRIEF.md) is every instruction file in one generated document, made to paste into a chat. Ask the user for the exact current file before changing it; never reconstruct a file from memory.

## Read for the task

1. Read [START_HERE.md](START_HERE.md) for navigation and current capabilities, and [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) for ownership, status, assets, and version authority.
2. Open the file you will change. Its `$instructions` key (stories: `instructions:` frontmatter) names the guides to read first. Each folder's `AGENTS.md` routes everything in it:

   | Changing | Folder guide | Main rules |
   | --- | --- | --- |
   | Lessons, companions, stories, quest status, Welcome | [content/AGENTS.md](content/AGENTS.md) | [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md), [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) |
   | Resource names, links, status, publishing | [catalog/AGENTS.md](catalog/AGENTS.md) | [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) |
   | Lesson slide PDFs and PPTX | | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |
   | Templates and their artwork | [templates/AGENTS.md](templates/AGENTS.md) | Asset rules in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#resources-slides-and-assets) |
   | Renderers, build selection, validation, publishing scripts | [scripts/AGENTS.md](scripts/AGENTS.md) | [WORKFLOW.md](system/WORKFLOW.md#pdf-build-selection) |
   | The instructions themselves | [system/AGENTS.md](system/AGENTS.md) | [Maintaining instructions](#maintaining-instructions) |

3. For every edit, follow [WORKFLOW.md](system/WORKFLOW.md). For file creation or binary transfers through a connector, read [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).

## Non-negotiable boundaries

- Use approved facts, canon, names, dialogue, activities, and resource links. Flag missing or conflicting evidence; never invent a substitute.
- Keep lifecycle to `unapproved` → `approved` → `published`, with the one status owner defined in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Uploading, merging, rendering, or passing checks does not approve content or authorize publication.
- Edit the owning source; do not duplicate resources inside Teacher Guides. Keep required PDF images versioned in GitHub, as separate asset files rather than pre-rendered pages.
- Keep content, visual changes, and publishing actions distinct. Preserve the published seven-slide Activate asset; historical quest-wide slide numbers are not current lesson numbers.
- Save edits through a pushed PR, reconcile simultaneous AI changes against the latest `main`, and merge when authorized. Verify the merged result and preserve unrelated work.
- For PDF previews, give the verified **GitHub Actions run URL first**, preferably the post-merge `main` run. Follow [WORKFLOW.md](system/WORKFLOW.md#preview-links-and-retention); do not use a preview-branch or PR Files link as the primary review link.

## Maintaining instructions

- Treat “from now on” and equivalent requests as lasting rules; keep one-time requests within the task. Record lesson-specific decisions in that lesson's existing source/status metadata.
- Find the rule's owner in `START_HERE.md`. Update it there; replace superseded wording and link from other documents instead of copying the rule.
- State the scope, required behavior, and any necessary exception. Use direct instructions and keep examples only when they clarify a decision.
- Search for conflicts and stale references. Update affected templates or behavior within the authorized scope; record remaining work explicitly.
- Keep agents routed: a new source type gets a `$instructions` pointer (defined in `scripts/validate.py`) and a template carrying it; a new folder of editable files gets an `AGENTS.md` and a row in the table above.
- After editing any instruction file, run `python scripts/build_ai_brief.py`; `scripts/validate.py` fails while `AI_BRIEF.md` is stale. Never edit `AI_BRIEF.md` directly.
- Keep editorial judgment in prose, shared values in their existing data files, and objective checks in `scripts/validate.py`. Do not add unused enforcement files or speculative tooling.
- Apply explicit user decisions within their scope. If conflicting instructions would change approval, publication, or content meaning and intent is unclear, flag the conflict and continue independent work.
- Report where the rule was saved, what now enforces it, and any existing materials still needing updates. Do not silently rewrite or publish the whole collection.
