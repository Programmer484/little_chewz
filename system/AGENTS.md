# Editing instructions

The files here own the repository's rules; each states what it owns in its opening lines, and [START_HERE.md](../START_HERE.md#where-things-belong) maps every rule to its owner. Follow [AGENTS.md: maintaining instructions](../AGENTS.md#maintaining-instructions): change a rule only in its owner, replace superseded wording, and link instead of copying.

After editing any instruction file, run `python scripts/build_ai_brief.py` to refresh `AI_BRIEF.md`; `scripts/validate.py` fails while it is stale. `action_labels.json` is data read by the validator.
