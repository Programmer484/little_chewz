# Editing instructions

The files here own the repository's rules; each states what it owns in its opening lines, and [START_HERE.md](../START_HERE.md#where-things-belong) maps every rule to its owner. Follow [AI_RULES.md: maintaining instructions](AI_RULES.md#maintaining-instructions): change a rule only in its owner, replace superseded wording, and link instead of copying.

After editing any instruction file, run `python scripts/build_agents_md.py` to regenerate the root `AGENTS.md`; `scripts/validate.py` fails while it is stale. Never edit the root `AGENTS.md` itself. `action_labels.json` is data read by the validator.
