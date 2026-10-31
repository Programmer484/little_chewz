# Agent command contract

This document **routes user intent**, not full procedures. `/create`, `/update`, and `/merge` are agent instructions, not executable programs; client-side slash aliases require separate configuration. Resolve the resource and stable ID from live GitHub records.

| User request | Owning instructions | Result |
| --- | --- | --- |
| `/create` | [CREATE.md](CREATE.md) | Draft in holding; **never publish**. |
| `/update` | [WORKFLOW.md](WORKFLOW.md) | Revise source or holding file; retain existing official release. |
| `/merge` for `generated_pdf` | [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md#generated-pdf-publication-after-authorized-merge) | After explicit human approval, initiate guarded release of a generated PDF. |
| “Publish” an `external` resource or first-ever `generated_pdf` | [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md) | Agent-managed official Drive placement and verification, then catalog update. |

Never use `/merge` to publish an external worksheet, poster, media file or slide deck. An ordinary PR merge or preview is not publication. There is no configured `/publish` slash command; natural-language publication instructions follow [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md). [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) owns all status and URL definitions.
