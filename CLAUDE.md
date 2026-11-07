# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Follow [`AGENTS.md`](AGENTS.md).** It is the house contract for every assistant
working in this repository, and it is the file to read first and in full. This
page adds only the Claude-specific notes; it does not restate or override it.

The short version, so nothing is a surprise: fetch `origin/main` before you read
or branch, the owner pushes to `main` directly (you commit, the owner pushes)
while other contributors use pull requests, no secrets in the tree,
respect `.github/CODEOWNERS`, write everything in English, and no
`Co-Authored-By` or assistant attribution in commits. In multi-branch
repositories (`dev`, `preprod`, `prod`, where a push deploys), `main` means
every deploy branch, kept at one SHA.

## Claude-specific notes

- **Plan mode on anything that touches `/.github/`.** Workflows, `CODEOWNERS`,
  rulesets, and the gitleaks config change the rules everyone else works under.
  Show the plan before the diff.
- **Prefer reading to guessing.** This tree is small enough to read end to end.
  A grep across it costs less than a wrong assumption about what is in it.
- **Do not use `Bash` for file work.** Read, edit, and search with the file
  tools. Reserve the shell for `git`, `pre-commit`, and `gh`.
- **Never run `git commit --amend`, `git push --force`, `git rebase` on a pushed
  branch, or `gh pr merge`** unless the instruction to do so was explicit.
- **Do not add "generated with" footers** to commits, pull request bodies, issue
  comments, or files. `AGENTS.md` §7 is not negotiable, and the
  `attribution guard` job fails the pull request on the footer, on a
  `Co-authored-by:` trailer naming anyone outside
  `.github/attribution-allow.txt`, and on an author or committer address that
  is not on that list.
- **Subagents inherit this contract.** If you delegate, restate the constraints;
  a subagent that has not read `AGENTS.md` will happily invent a `docs/`
  directory.
- **One documentation surface.** `wiki/` is it. The only thing allowed under
  `docs/` is `docs/screenshots/` (images, ADR-0002); CI fails on anything else
  there — that is deliberate, not a bug to work around.
- **Screenshots are mandatory** (`AGENTS.md` §10). After a visible change,
  regenerate the screenshot and Read the PNG before committing it: you can see
  the image, `gitleaks` cannot, so a customer name in it is yours to catch.
- **Bundles are opt-in by design.** Files under `.github/bundles/` end in
  `.disabled` or `.example` on purpose. Do not "fix" them by activating them;
  see [`wiki/Bundles.md`](wiki/Bundles.md) for how enabling is meant to work.

## How the pieces fit

There is no build and no language toolchain: the product is the files
themselves. Four things tie them together, and each spans several files.

- **`ci.yml` is the gate**, beside `attribution-guard.yml`, which exists only
  because it needs the `edited` trigger. Its `template structure` job holds a literal
  list of every file the template promises (the `PATHS` heredoc). Adding,
  renaming or removing a template file means editing that list in the same
  commit, or CI fails. The same job requires every `scripts/**/*.sh` with a
  shebang to be executable (`git update-index --chmod=+x <script>`; a sourced
  library without one is only parsed), every `uses:` pinned to a 40-char SHA
  with a `# vX` comment, nothing under `docs/` except `docs/screenshots/`,
  relative markdown links outside `wiki/` resolving to a file,
  and every file under `.github/bundles/` to end in `.disabled`/`.example`
  (or be a `README.md`). It also actionlints the disabled bundle workflows.
- **`scripts/check-screenshots.sh` is the single implementation** of ADR-0002;
  the `screenshots` CI job and the pre-commit hook only call it. Other
  repositories copy it byte for byte: change it here, never fork it elsewhere.
- **`wiki/` is mirrored, not merged.** `scripts/wiki-sync.sh` (via `wiki.yml` on
  push to `main`) makes the GitHub wiki match `wiki/` exactly, overwriting UI
  edits and deleting pages removed here.

`scripts/apply-ruleset.sh` defaults to a plan; `--apply` changes live branch
protection and is the owner's step, never CI's and never yours unprompted.

Anything that names `ScaleMeNow/GITHUB-TEMPLATE` is a placeholder a clone must
swap. A new file carrying it gets a row in the README's _Replace the
placeholders_ table.

## Checks you can run

```bash
pre-commit run --all-files                  # gitleaks, actionlint, hygiene, screenshots
pre-commit run <hook-id> --all-files        # one hook: gitleaks, actionlint, check-screenshots, ...
scripts/check-screenshots.sh                # the screenshot rule on its own
scripts/check-doc-surface.sh                # the one-doc-surface rule on its own
scripts/check-repo-settings.sh              # the live GitHub settings: About, features, merge, ruleset
scripts/tests/attribution-guard-test.sh     # the attribution guard, against its fixtures
scripts/tests/check-doc-surface-test.sh     # the doc-surface check, per link not per line

# Template-owned markdown stays prettier-clean, so repos that run prettier keep it as shipped
npx --yes prettier@3 --check AGENTS.md CLAUDE.md CONTRIBUTING.md SECURITY.md SUPPORT.md \
  .github/copilot-instructions.md .github/PULL_REQUEST_TEMPLATE.md '.github/bundles/**/README.md' \
  wiki/Bundles.md wiki/Architecture-Decisions.md 'wiki/ADR/*.md'

# CI-only checks, reproduced locally
for f in .github/bundles/*/*.yml.disabled; do actionlint - < "$f"; done
grep -rnE '^\s*(-\s+)?uses:' .github/workflows/ | grep -vE '@[0-9a-f]{40}'   # must print nothing

# Regenerate docs/screenshots/ (needs gh auth, python3 + PyYAML, node,
# and any node_modules with playwright + chromium)
scripts/screenshots/capture.sh /path/to/node_modules

gh run list --limit 5                       # what CI thought of the last pushes
```
