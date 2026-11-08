# Release markers

A file named `<PR-number>.json` added in a PR publishes the listed generated PDFs when that PR merges into `main`:

```json
{"resource_ids": ["ccc-q01-welcome", "ccc-q01-activate-teacher-guide"]}
```

List dependencies before the resources that link to them. The **Publish** workflow runs `scripts/publish_to_drive.py --marker` on the merge commit. Rules: [system/PUBLISH.md](../../system/PUBLISH.md).
