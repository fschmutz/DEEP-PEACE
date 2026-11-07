#!/usr/bin/env bash
#
# Regenerate this template's own screenshots in docs/screenshots/.
#
#   scripts/screenshots/capture.sh NODE_MODULES_DIR [OWNER/REPO]
#
# NODE_MODULES_DIR  any local node_modules that has `playwright` with its
#                   Chromium installed (`npx playwright install chromium`).
#                   The template ships no Node dependencies; borrow one from
#                   any project that has Playwright installed.
# OWNER/REPO        the context for GitHub's Markdown renderer
#                   (default: ScaleMeNow/GITHUB-TEMPLATE).
#
# What it captures, at 1280 px wide:
#   readme.png                 README.md as GitHub renders a repository file
#   pull-request-template.png  .github/PULL_REQUEST_TEMPLATE.md as a PR body
#   issue-form-bug.png         .github/ISSUE_TEMPLATE/bug.yml, as an HTML mock
#                              of the issue form (labelled as a rendering)
#
# How: `gh api markdown` turns the Markdown into GitHub's own HTML (the only
# network call that needs `gh auth`), scripts/screenshots/render.py wraps it,
# and capture.mjs photographs it with Playwright. No browser login, no
# github.com page is opened.
#
# Stylesheet: github-markdown-css is FETCHED at capture time from cdnjs, pinned
# to a version and verified against a SHA-256 below — not vendored, so the
# template carries no third-party CSS. Bump both lines together.
#
# Needs: bash, curl, sha256sum (or shasum), gh (authenticated), python3 with
# PyYAML, node. Every PNG must stay within 600 KB; scripts/check-screenshots.sh
# runs at the end and fails the capture if one does not.
#
set -euo pipefail

readonly CSS_VERSION="5.9.0"
readonly CSS_SHA256="305a3a0fce18b39309d608292d9fcb2e53bf58765930ce2e721884477326513f"
readonly CSS_URL="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/${CSS_VERSION}/github-markdown-light.min.css"
readonly MAX_HEIGHT=1600

if [ $# -lt 1 ] || [ ! -d "$1" ]; then
  sed -n '3,31p' "$0" | sed 's/^# \{0,1\}//' >&2
  exit 2
fi
node_modules="$(cd "$1" && pwd)"
context="${2:-ScaleMeNow/GITHUB-TEMPLATE}"

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "${here}/../.." && pwd)"
out="${root}/docs/screenshots"

for tool in curl gh python3 node; do
  command -v "${tool}" >/dev/null 2>&1 || { echo "capture: ${tool} is required" >&2; exit 1; }
done
if [ ! -d "${node_modules}/playwright" ]; then
  echo "capture: ${node_modules} has no playwright package" >&2
  exit 1
fi

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT

curl -sSfL --retry 2 -o "${work}/github-markdown.css" "${CSS_URL}"
if command -v sha256sum >/dev/null 2>&1; then
  actual="$(sha256sum "${work}/github-markdown.css" | cut -d' ' -f1)"
else
  actual="$(shasum -a 256 "${work}/github-markdown.css" | cut -d' ' -f1)"
fi
if [ "${actual}" != "${CSS_SHA256}" ]; then
  echo "capture: github-markdown-css ${CSS_VERSION} hash mismatch (got ${actual})" >&2
  exit 1
fi

python3 "${here}/render.py" "${root}" "${work}/github-markdown.css" "${work}" "${context}"

mkdir -p "${out}"
# README last, and twice: its Screenshots section embeds readme.png itself, so
# the second pass shows the README as it now is rather than the previous run.
node "${here}/capture.mjs" "${node_modules}" "${MAX_HEIGHT}" \
  "${work}/issue-form-bug.html=${out}/issue-form-bug.png" \
  "${work}/pull-request-template.html=${out}/pull-request-template.png" \
  "${work}/readme.html=${out}/readme.png" \
  "${work}/readme.html=${out}/readme.png"

for png in "${out}"/*.png; do
  echo "$(wc -c < "${png}" | tr -d ' ') bytes  ${png#"${root}"/}"
done

"${root}/scripts/check-screenshots.sh" "${root}"
