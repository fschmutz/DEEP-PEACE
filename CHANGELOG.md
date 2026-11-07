# Changelog

All notable changes to this repository are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this repository adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Repositories created from this template should keep this file and start their own
history — replace the entry below rather than inheriting it.

## [Unreleased]

### Added

- `scripts/check-doc-surface.sh` accepts declared exceptions in
  `.github/doc-surface-exceptions.txt` (`docs/path: reason`, a trailing `/`
  covers a directory) for generated files consumed at a `docs/` path. A declared
  path passes, and so does a wiki link to it; an entry with no reason, outside
  `docs/`, or matching no tracked file fails. Nine new cases in
  `scripts/tests/check-doc-surface-test.sh`.
- `scripts/check-repo-settings.sh`: checks the live repository against
  Getting Started steps 2, 6 and 7 (About description and topics, wikis and the
  wiki repository, issues, projects and discussions off, squash merge only,
  delete head branches, secret scanning, push protection, vulnerability
  reporting on public repositories, an active ruleset). `--apply` sets the About
  box and the feature and merge settings. A requirement that cannot hold is
  declared in `.github/repo-settings-exceptions.txt`. Step 2 now names the About
  box as mandatory; step 8 runs the script.
- **Multi-branch variant** for BAM pipeline repositories (`dev`, `preprod`,
  `prod` at one SHA, the owner pushes direct, a push deploys through
  CodeBuild), so they keep template files byte-identical instead of patching
  them:
  - `.github/rulesets/multi-branch.example.json`: the main example's rules and
    admin bypass, targeting the three deploy branches; a repository appends its
    build jobs to `required_status_checks`. `scripts/apply-ruleset.sh -f` applies
    it, and its plan now prints the target branches. In the `template structure`
    PATHS list; the JSON step parses every `.github/rulesets/*.json`.
  - `ci.yml` documents the multi-branch `push.branches` form above `on:`; it is
    the one trigger such a repository edits.
  - `AGENTS.md`, `CONTRIBUTING.md`, `CLAUDE.md` and the Copilot pointer say
    that `main` means every deploy branch, kept at one SHA.
  - `wiki/Getting-Started.md` gains a *Multi-branch repositories* section and a
    placeholders row for the `ci.yml` trigger; `wiki/Bundles.md` and the README
    point at it.
- `scripts/check-doc-surface.sh`: one implementation of the one-doc-surface rule
  (nothing tracked under `docs/` but `docs/screenshots/`, no wiki link into
  `docs/`), called by the `ci.yml` step and a pre-commit hook. It replaces the
  inline `find` in CI, which missed wiki links into the old doc tree. Repos copy
  it byte for byte.

### Changed

- `wiki.yml` and `label-sync.yml` publish from the default branch, whatever it
  is called: the trigger takes every branch and a job-level
  `if: github.ref_name == github.event.repository.default_branch` keeps only the
  default one. Their concurrency groups carry the ref, so a skipped run on
  another branch cannot replace a pending default-branch run.
- `.pre-commit-config.yaml`: `check-yaml` runs with `--unsafe` (syntax only),
  so CloudFormation short tags (`!Ref`, `!Sub`) pass without a per-repository
  exclude; `check-json` skips JSONC configs by name (`.oxlintrc.json`,
  `tsconfig*.json`, `jsconfig.json`, `devcontainer.json`, `.vscode/*.json`).
- Template-owned markdown (`AGENTS`, `CLAUDE`, `CONTRIBUTING`, `SECURITY`,
  `SUPPORT`, the Copilot pointer, the bundle READMEs, `wiki/Bundles`,
  `wiki/Architecture-Decisions`, `wiki/ADR/`) is prettier 3-formatted, so a
  repository that runs prettier no longer has to prettier-ignore it.

### Fixed

- `scripts/wiki-sync.sh` runs from a laptop again: `WIKI_URL` defaults to the
  origin remote with `.wiki.git`, and outside CI the push goes through a
  `push-confirm` alias when the machine defines one, so a guarded `git push` no
  longer refuses it. `wiki.yml` grants `contents: write` to the publish job only,
  with `permissions: {}` at the top level.
- `scripts/check-doc-surface.sh` skips YAML frontmatter at the top of a wiki
  page: a `path: docs/...` value there names a file in another repository, not a
  link. Four new cases in the test.
- Shipped files no longer name internal repositories or the incident behind
  the bundles; they describe the case instead, since public repositories copy
  them too. A `Shipped files name no internal repository` step in
  `template structure` keeps it that way (`CHANGELOG.md` excepted). It runs only
  in the template repository (`is_template`), since a repository made from it
  may carry an internal name of its own.
- `ci.yml` requires the executable bit only on scripts with a shebang; a sourced
  library (`scripts/lib/*.sh`) is only parsed. It used to fail every repository
  with a shell library. Scripts are found at any depth under `scripts/`.
- `.github/bundles/security/README.md` linked the ADR page one level short. A new
  `Relative markdown links resolve` step fails on any relative link outside
  `wiki/` that points at no file; links that climb out of the repository
  (GitHub routes such as `../../issues/new`) are left alone.
- `scripts/check-repo-settings.sh --apply` checks the PATCH response instead of
  a fresh read, which could still return the old values and print a FAIL that
  was not there; topics are written first so the response carries them.
- `scripts/check-repo-settings.sh --apply` leaves a declared setting alone; it
  used to reset it to the template default on every run (a repository that
  chose rebase merging lost it). With `-R`, the declarations are read from that
  repository's default branch instead of the current checkout's file.
- `ci.yml` installs actionlint from the release tarball checked against a
  pinned sha256, instead of piping `download-actionlint.bash` from a mutable tag
  into `bash`. The `actionlint` and `structure` jobs check out with
  `persist-credentials: false`, like `screenshots`; so do `wiki.yml`,
  `label-sync.yml` and `dependency-review.yml`, which pass their token explicitly.
- `.pre-commit-config.yaml` freezes every `rev:` to a commit SHA with a
  `# frozen: vX` comment; Dependabot's pre-commit ecosystem keeps them moving.
- Private vulnerability reporting is scoped to public repositories in
  `SECURITY.md`, `wiki/Getting-Started.md` and the issue chooser. GitHub does not
  offer it on private repositories (the API returns 404), so the email channel is
  the reporting path for every private house repository.
- `scripts/attribution-guard.sh` skipped the title and body re-read without a
  word when `--refresh-text` (or an `edited` event) came with no repository or
  pull request number, and checked the stale text instead. That is now an
  error, like a re-read the API refuses.
- `scripts/apply-ruleset.sh` no longer reads a failed rulesets query as an empty
  list. A private repository on GitHub Free (403 *Upgrade to GitHub Pro*) exits 3
  with what to do, any other error exits 1; it used to plan a CREATE that could
  never happen. `wiki/Getting-Started.md` step 6 lists the three ways out.
- `wiki/Getting-Started.md` step 7: save the first wiki page before the first
  push to the default branch that touches `wiki/`, or that sync fails once.
- `.gitignore` ignores the AWS CLI state (`.aws/credentials`, `config`,
  `sso/`, `cli/`) instead of all of `.aws/`, which hid the tracked
  `.aws/run.sh` entry point of pipeline repositories after a copy.
- `scripts/check-doc-surface.sh` filters `docs/screenshots/` per link, not per
  line: a wiki line linking a screenshot and another `docs/` path now fails.
  `scripts/tests/check-doc-surface-test.sh` holds the cases and runs in CI.

### Added

- **Bundle model.** Every researched enhancement now ships with the template,
  grouped into named bundles A–I with a declared default. Bundles that are off
  live under `.github/bundles/` as `.disabled` or `.example` files, which GitHub
  reads as neither workflows nor community files. The map is in the README and
  in full on the `Bundles` wiki page; the reasoning is `wiki/ADR/0001`.
- **Bundle B — Agent** (on): `AGENTS.md` as the single house contract for AI
  assistants, with `CLAUDE.md` and `.github/copilot-instructions.md` as pointers
  to it.
- **Bundle C — Supply chain** (on): `.github/workflows/dependency-review.yml`,
  paths-filtered and preflighted so it never sits red on a repository without
  dependencies or without Advanced Security.
- **Bundle D — Triage** (on): `.github/labels.yml` with a `yq` + `gh` sync
  workflow, `.github/labeler.yml` with a path-based labeller, a third issue form
  for documentation problems, and `SUPPORT.md`.
- **Bundle E — Governance** (files on, enforcement opt-in):
  `scripts/apply-ruleset.sh`, which plans by default and validates required
  status check names against the jobs the workflows really produce; ADRs under
  `wiki/ADR/` with a template and an index page.
- **Bundles F, G, H** (off): release-please and SBOM stubs, the
  public-repository community files, a stale bot, and OpenSSF Scorecard —
  all inert, each carrying the cost of running it in its header.
- **Bundle I** (documentation only): a README section on a future
  `ScaleMeNow/smn-actions` repository of reusable workflows, and why it does not
  exist yet.
- CI checks that every `uses:` is pinned to a full commit SHA, that the
  off-by-default bundles have not lost their suffix, and that the disabled
  bundle workflows still parse.
- **Screenshots are mandatory** (Bundle A, `wiki/ADR/0002`).
  `scripts/check-screenshots.sh` requires a README `## Screenshots` section
  linking alt-texted images under `docs/screenshots/` (no orphans, no dangling
  paths, at most 600 KB each), or a reason declared in
  `.github/screenshots-exempt`. It runs as the `screenshots` job in `ci.yml`,
  required by the ruleset example, and as a pre-commit hook.
- **Attribution is checked** (Bundle A). `scripts/attribution-guard.sh` fails a
  pull request whose commits were authored or committed by an address that is
  not in `.github/attribution-allow.txt`, whose author or committer *name*
  reads as a tool (`Cursor Agent`, `Claude`, `Copilot`, `AI assistant`) even
  when the address is allow-listed, whose messages carry a `Co-authored-by:`
  trailer naming anybody else or an assistant footer, or whose title or body
  carries agent body markers, an agent run link, an "Open in …" footer image,
  or a "Generated with …" line. The title and the body are re-read from the
  API on the `edited` action. The allow-list understands `committer:` entries
  for a GitHub web merge, `bot:` entries for `dependabot[bot]`,
  `github-actions[bot]` and `renovate[bot]`, and `name:` entries for a person
  whose name collides with a tool's; `$ATTRIBUTION_ALLOW` and
  `$ATTRIBUTION_ALLOW_FILE` override it without a commit. A missing,
  unreadable, or empty allow file warns and falls back to the address built
  into the script rather than trusting everybody. It runs as the
  `attribution guard` job of `.github/workflows/attribution-guard.yml`, which
  is its own workflow because the check needs the `pull_request` `edited`
  trigger that `ci.yml` does not have, and the ruleset example requires it.
  `scripts/tests/attribution-guard-test.sh` runs the guard against recorded
  API payloads in the same job, before the live check — one fixture per
  overlapping footer rule, so deleting a rule turns a case red.
- The template's own screenshots — README, bug issue form, pull request
  template — and `scripts/screenshots/capture.sh`, which regenerates them
  locally with `gh api markdown`, github-markdown-css, and Playwright. The
  private repository's CI status badge is the one substitution: it is drawn as
  a static shields-style "CI" label, and the README gallery caption says so.

### Changed

- Every action in `.github/workflows/` is pinned to a full commit SHA with the
  version as a trailing comment, replacing mutable tags.
- `SECURITY.md` records that secret scanning and push protection are already on
  organisation-wide, and that private vulnerability reporting is off by default
  and has to be enabled per repository.
- `ci.yml` covers the new files, and the executable check applies to every
  script in `scripts/` rather than only the wiki sync.
- `docs/` may exist, but only as `docs/screenshots/`; the one-documentation-
  surface check fails on anything else under it. Prose stays in `wiki/`.
- The pull request template asks whether the screenshots were updated.
- Every link, badge, and issue-form URL now names the repository by its real
  name, `ScaleMeNow/GITHUB-TEMPLATE`, instead of the pre-rename slug. The
  placeholder sanity grep searches for `GITHUB-TEMPLATE`, which also catches
  the raw screenshot URLs in `wiki/Home.md`.
- The owner pushes directly to `main`, which is the norm in BAM repositories;
  contributors other than the owner, and anyone when a ruleset without the
  admin bypass protects `main`, use a branch and a pull request. `AGENTS.md`,
  `CLAUDE.md`, the Copilot instructions, `CONTRIBUTING.md`, the README, and the
  wiki say so, and the ruleset docs explain the admin bypass actor that keeps it
  possible.

### Fixed

- `scripts/attribution-guard.sh` split its commit records on a tab, which is
  IFS whitespace, so an absent author login (an email GitHub cannot map to an
  account) shifted every later field one slot left and a tool-named author
  skipped the name check. Records now use the unit separator. A failed re-read
  of the title and body on `edited` is an error instead of a pass on the stale
  payload.
- `scripts/tests/attribution-guard-test.sh` let the runner's own
  `GITHUB_EVENT_PATH` and `GITHUB_REPOSITORY` reach every case, so inside the
  `edited` workflow each fixture tried to re-read a pull request that does not
  exist and exited 2. Each case now runs without the runner context, and a case
  proves it.

## [1.0.0] - 2026-10-01

### Added

- Initial ScaleMeNow house GitHub configuration pack: README hero, `CHANGELOG`,
  `SECURITY`, `CONTRIBUTING`, proprietary `LICENSE`, `.gitignore`, and
  `.pre-commit-config.yaml` with `gitleaks` and `actionlint`.
- Wiki-as-code surface: `wiki/` as the source of truth plus
  `scripts/wiki-sync.sh` and `.github/workflows/wiki.yml`.
- GitHub configuration: `CODEOWNERS`, weekly Dependabot for `github-actions` and
  `pre-commit`, pull request template, bug and feature issue forms with blank
  issues disabled, and a lean `ci.yml`.
- `.github/rulesets/main.example.json` as a documented branch-protection shape,
  applied out of band.
