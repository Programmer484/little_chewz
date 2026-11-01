#!/usr/bin/env bash
# Append each run's PDF previews to the shared history branch without overwriting earlier runs.
set -euo pipefail
# This step switches to the history branch. Restore the original commit on exit so
# later post steps (for example the shared .github/actions/pdf-setup) still find their files.
original_head="$(git rev-parse HEAD)"
trap 'git checkout --quiet --force "$original_head"' EXIT
# A single branch avoids branch proliferation; every run has its own immutable folder.
# Existing pdf-preview-run-* branches and URLs are deliberately left untouched.
preview_branch="pdf-preview-history"
run_folder="previews/${RUN_ID}"

temp_dir="$(mktemp -d)"
cp exports/*.pdf "$temp_dir/"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# PR and main jobs can complete concurrently. Retry an append if the
# shared history branch advances between fetch and push.
for attempt in 1 2 3 4 5 6 7 8; do
  if git ls-remote --exit-code --heads origin "$preview_branch" >/dev/null; then
    git fetch --no-tags origin "$preview_branch"
    git checkout -B "$preview_branch" FETCH_HEAD
  else
    git checkout --orphan "${preview_branch}-init-${RUN_ID}-${attempt}"
    git rm -rf --quiet .
  fi

  if [[ -e "$run_folder" ]]; then
    echo "::error::Preview folder for this run already exists: $run_folder"
    exit 1
  fi
  mkdir -p "$run_folder"
  cp "$temp_dir"/*.pdf "$run_folder/"
  git add -f "$run_folder"/*.pdf
  git commit -m "PDF previews for Actions run ${RUN_ID}"

  if git push origin "HEAD:refs/heads/$preview_branch"; then
    break
  fi
  if [[ "$attempt" -eq 8 ]]; then
    echo "::error::Failed to append PDFs to history after retries"
    exit 1
  fi
  sleep "$attempt"
done

{
  echo "### PDF review links"
  echo "| PDF | Preview | Download |"
  echo "| --- | --- | --- |"
  for pdf in "$run_folder"/*.pdf; do
    name="${pdf##*/}"
    echo "| ${name} | [Preview](https://github.com/${REPO}/blob/${preview_branch}/${pdf}) | [Download PDF](https://github.com/${REPO}/raw/refs/heads/${preview_branch}/${pdf}) |"
  done
} >> "$GITHUB_STEP_SUMMARY"
