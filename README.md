# Little Chewz — AI-first editable source

Start with **[START_HERE.md](START_HERE.md)**, then read **[AGENTS.md](AGENTS.md)**.

This repository separates lesson data, reusable templates, rendering scripts, and published exports. It contains approved Activate JSON, three companion resource sources, and explicitly unapproved skeletons for six later stages. **No published Drive files are replaced by this repository.**

**Workflow:** `content/` = actual lesson/resource wording; `templates/` = structures; `scripts/` = actions; `exports/` = generated PDFs. Future slide generation is **per lesson**, with an independent slide set for each stage and no default full-quest deck regeneration. The current seven-slide Activate asset remains published; the historical 44-slide deck is only a reference. No new slide generator has been implemented.

See [migration report](MIGRATION_REPORT.md) and run `python scripts/validate.py`. Build instructions are in START_HERE.

System tooling improvements (including GitHub Actions validation and PDF previews) are tracked in **[SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md)**. These are proposed/planned tasks, not enabled features.
