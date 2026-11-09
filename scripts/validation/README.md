# Source validation architecture

Run `python scripts/validate.py` for repository-wide local checks. The command does not build, audit or publish anything.

`runner.py` dispatches each authored source using the `template` field **and its owner** (lesson, companion or standalone). The routing table names the only validator modules applied to that source:

| Template | Validator dependencies |
| --- | --- |
| `teacher_guide` | `teacher_guide.py` |
| `celebrate` | `teacher_guide.py` + `celebrate.py` |
| `teacher_companion` | `companion.py` |
| `activity_guide` | `companion.py` + `activity_guide.py` |
| `option_overview` | `companion.py` |
| `welcome` | `welcome.py` |

Validators are loaded only when needed. Owner mismatches cannot bypass the owner's baseline checks. The template-to-PDF-renderer mapping is kept in this same routing table rather than duplicated across validators.

- `common.py` checks nested catalogue `ref` values **once per source** and owns worksheet-print quantity rules.
- `catalog.py` owns registry entries, PDF metadata, and local Drive-folder *configuration* checks; no Google Drive API is contacted.
- `teacher_guide.py` owns Teaching Flow, cover, options, bonuses, and print quantities; Celebrate adds only its unique invitation/party/finale rules.
- `companion.py` checks companion identity and obsolete status fields; Activity Guide adds its section contract.
- `welcome.py` checks Welcome navigation IDs, not Teacher Guide teaching steps.
- `runner.py` checks quest manifests, story frontmatter, template registration, and PDF build mappings without rerunning source validators.

New source types should add one focused validator and one entry in `RULES`. Do not copy shared reference or Teacher Guide checks into specialized modules. Tests: `python -m unittest discover -s tests -v`.
