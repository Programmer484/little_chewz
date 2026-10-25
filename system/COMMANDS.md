# Command contract

The only user-facing commands are **`/create`**, **`/update`**, and **`/merge`**. Natural-language instructions after a command apply. Infer the resource from conversation and confirm its ID against current GitHub records. These files define agent behavior; slash-command aliases require separate client configuration.

## `/create [instructions]`

The user has already prototyped the resource in chat. Follow [CREATE.md](CREATE.md): establish identity, create/reuse `edit/<stable-resource-id>`, commit editable sources/assets to GitHub, register intent as `unpublished`, validate and share the PR preview. **Do not upload to Drive yet.**

## `/update [instructions]`

Find/reuse the resource's branch (or branch from current `main` if missing), fetch its latest remote head, edit only the requested scope, validate, commit and push without force. Multiple agents across chats use the same resource branch. On concurrent updates reconcile rather than overwrite.

## `/merge [instructions]`

This is permission to accept the resource change and initiate publication. Reconcile the latest `main`, verify and merge, show the **combined `main`** output, and delete the branch after checking that all intended commits were merged. Replace the existing Drive destination in place, or create the first file in its proper Drive folder and update the catalogue. Verify exact deliverables and set `published` only after confirmation. On failure retain `pending_publish` (older live Drive version) or `unpublished` (none) and report the blocker.

**No `/publish` command.** Publication is part of `/merge`. Today the merge-trigger orchestration is not built; the manual GitHub Action is an internal temporary fallback. Never claim the automatic step executed if it did not.