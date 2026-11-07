# Getting Started

From `Use this template` to a green CI and a published wiki.

> Edit this page at `wiki/Getting-Started.md` in the repository. Changes made in
> the GitHub wiki UI are overwritten by the next sync.

## 1. Create the repository

On [the template repository](https://github.com/ScaleMeNow/GITHUB-TEMPLATE),
choose **Use this template → Create a new repository**.

- **Owner**: the ScaleMeNow organisation, unless the repository belongs to another
  house entity.
- **Visibility**: private. The bundled `LICENSE` is proprietary; publishing the
  repository means replacing it first.
- **Include all branches**: no. Only `main` matters.

## 2. Turn on the features the pack expects

The repository page → **About** (the gear beside it) is mandatory, and a copy of
the template starts with it empty:

| Field | Value |
|---|---|
| Description | one line saying what the repository is |
| Topics | at least one: the domain, the stack, the owner entity |
| Website | the site it serves or documents, when there is one |

Settings → General → Features:

| Setting | Value | Why |
|---|---|---|
| Wikis | on | `.github/workflows/wiki.yml` pushes to the wiki repository |
| Issues | on | the issue forms are useless without it |
| Projects / Discussions | off | turn on when there is someone to run them |

Settings → General → Pull Requests: allow **squash merge** only, and enable
*Automatically delete head branches*.

Settings → Advanced Security: enable **secret scanning** and **push protection**,
and, on a **public** repository only, **private vulnerability reporting**.

Secret scanning and push protection are already on organisation-wide for
ScaleMeNow, so confirm rather than configure — and do not add a scanning
workflow to duplicate them. Private vulnerability reporting exists only on
public repositories: on a private one GitHub has no such setting and the API
answers 404, so `SECURITY.md` sends reporters to the email channel. On a public
repository it is off by default; enable it, or the *Report a vulnerability*
button `SECURITY.md` mentions does not exist.

## 3. Replace the placeholders

The template ships with this repository's own name in a few places. Find them:

```bash
grep -rn "GITHUB-TEMPLATE" . --exclude-dir=.git
```

That one pattern covers every link, badge, and the raw screenshot URLs in
`wiki/Home.md` (`https://github.com/ScaleMeNow/GITHUB-TEMPLATE/raw/main/docs/screenshots/...`).
Then work through them:

| File | What to change |
|---|---|
| `README.md` | title, purpose line, badge URLs (`OWNER/REPO`) |
| `.github/CODEOWNERS` | owners for `*` and for the paths this repo actually has |
| `.github/attribution-allow.txt` | the addresses that may author or commit in this repository |
| `.github/ISSUE_TEMPLATE/config.yml` | the four contact link URLs |
| `.github/ISSUE_TEMPLATE/bug.yml` | the security policy link |
| `SUPPORT.md` | the wiki and Getting Started links |
| `wiki/Bundles.md` | the links to the bundle READMEs |
| `scripts/screenshots/capture.sh` | the default `OWNER/REPO` render context, if you keep the tool |
| `SECURITY.md` | the scope paragraph and the reporting contact |
| `CHANGELOG.md` | drop the template's `1.0.0` entry and start your own |
| `wiki/Home.md` | the repository name and what it does |
| `.github/workflows/ci.yml` | multi-branch repos: list every deploy branch in `on.push.branches` — see [Multi-branch repositories](#multi-branch-repositories) |
| `LICENSE` | keep it, or replace it before the repository goes public |
| `docs/screenshots/*.png` | delete the template's three images and add your own — screenshots are mandatory |
| `README.md` `## Screenshots` | link your own images, with alt text saying what each one shows |
| `wiki/Home.md` `## Screenshots` | point the image URLs at your `OWNER/REPO`, or drop the section |
| `scripts/screenshots/` | the template's own capture tooling — delete it, or adapt it to your UI |

Leaving a badge URL pointing at the template is the mistake to watch for: the
README will show the template's CI status, green, forever. The screenshots are
the other one: the template's images pass the check in your repository too, and
show the template instead of your product until you replace them.

A repository with genuinely nothing to show — a pure library, a data-only
repository — declares it instead: create `.github/screenshots-exempt` with one
line giving the reason, and delete `docs/screenshots/` and both `## Screenshots`
sections. `scripts/check-screenshots.sh` prints the reason and passes; an empty
or comment-only file fails. The reasoning is
[ADR-0002](ADR/0002-Screenshots-Are-Mandatory).

## 4. Install the hooks

```bash
pipx install pre-commit
pre-commit install
pre-commit run --all-files
```

Three gates matter. `gitleaks` blocks secrets, `actionlint` blocks workflow
files that would only fail once pushed, and `screenshots` blocks a repository
that does not show what it looks like. The first two are pinned in
`.pre-commit-config.yaml`, and Dependabot keeps the pins moving; the third is
`scripts/check-screenshots.sh`, run as a local hook.

A fourth gate has no local equivalent. `attribution guard` needs a pull request
to read, so it runs in CI only, and it reads the addresses it trusts from
`.github/attribution-allow.txt`. Replace the address in that file before the
first pull request, or every pull request fails on its own author.

## 5. Enable Dependabot

`.github/dependabot.yml` watches `github-actions` and `pre-commit` weekly. Blocks
for `npm`, `pip`, and `docker` are commented out — uncomment the one this
repository actually uses.

Enabling a block for an ecosystem with no manifest produces a recurring Dependabot
error on the repository, so uncomment deliberately.

## 6. Apply a ruleset

`.github/rulesets/main.example.json` is **documentation, not enforcement**. Nothing
protects `main` until you create the ruleset, and nothing in this template does
it for you — a template that applied branch protection on every clone would lock
a repository before anyone had decided who owns it.

The example keeps the repository admin role as a bypass actor: in BAM
repositories the owner pushes directly to `main`, and everyone else goes through
a pull request and the required checks. Remove the bypass only if the owner
should use pull requests too.

`scripts/apply-ruleset.sh` is the deliberate step. It plans by default:

```bash
./scripts/apply-ruleset.sh                # what it would do, and nothing else
./scripts/apply-ruleset.sh --apply        # create it, or update it in place
```

The plan checks each `required_status_checks` context against the job names this
repository actually produces — the template ships `workflow syntax`,
`template structure`, `screenshots`, and `attribution guard`. Fix anything it
prints as `UNKNOWN` first. Requiring a
check that never reports blocks every pull request, permanently, and the only
way out is an admin bypass.

**Multi-branch repositories** apply `.github/rulesets/multi-branch.example.json`
instead: the same rules and the same admin bypass, targeting
`refs/heads/dev`, `refs/heads/preprod` and `refs/heads/prod`. Append the
repository's own build jobs (the `name:` of each job, exactly as it reports) to
its `required_status_checks`; the plan flags any name no workflow produces.

```bash
./scripts/apply-ruleset.sh -f .github/rulesets/multi-branch.example.json
```

**Private repositories on GitHub Free** cannot have rulesets, nor classic
branch protection: the API answers 403 *Upgrade to GitHub Pro or make this
repository public*, and `apply-ruleset.sh` stops with exit 3 instead of planning
a ruleset that can never exist. Pick one: upgrade the account, make the
repository public, or record the exception in the repository's `wiki/Home.md`
(no ruleset, the owner is the only writer). CI still runs every gate; nothing
makes it required.

Two checks the template ships do **not** belong in that list:
`dependency review` and `label by path` are path-filtered and do not report on
every pull request. See [Bundles](Bundles).

The raw API call works too, if you would rather see it:

```bash
gh api -X POST repos/OWNER/REPO/rulesets \
  --input .github/rulesets/main.example.json
```

Verify:

```bash
gh api repos/OWNER/REPO/rulesets --jq '.[] | {name, enforcement}'
```

## 7. Publish the wiki

Three steps, in order. None of them happens by itself, and skipping either of the
first two makes the third fail in a way that reads like a bug.

**a. Enable Wikis** — Settings → Features → Wikis. Step 2 above.

**b. Create one page through the Wiki tab.** Any title, any content; the sync
overwrites it. This is the part that surprises people: enabling Wikis does *not*
create the `<repo>.wiki.git` remote, and a push cannot create it either. Until a
page exists, every sync fails with `Repository not found` even though
`has_wiki` is `true`.

Save that page **before** the first push to the default branch that touches
`wiki/`. Adopting the pack into an existing repository is such a push: its sync
runs at once and fails with the *create one page* error. Nothing is lost; save
the page, then do step c.

**c. Run the workflow by hand** — Actions → `wiki` → *Run workflow* → the
default branch (`main`, or `prod` in a multi-branch repository; on any other
branch the job is skipped). The workflow filters on `paths: ["wiki/**", ...]`,
and a paths filter needs a before/after comparison to match anything. The push that creates a repository
from a template has no before, and neither does a force push that rewrites
history, so the first sync is silently skipped. That is what `workflow_dispatch`
is for.

After that it is automatic: edit a file in `wiki/`, open a pull request, and the
merge publishes it. Commits on the published wiki are attributed to the author of
the source commit, not to the CI identity.

If a later run fails with a 403 while pushing, Wikis have been turned off again,
or the job lost `permissions: contents: write`.

## 8. Confirm the pack is live

```bash
./scripts/check-repo-settings.sh          # About, features, merge, security, ruleset
gh run list --limit 5
```

`check-repo-settings.sh` reads the live repository and prints `ok`, `FAIL` or
`DECLARED` for every setting in steps 2, 6 and 7. With `--apply` it sets the
About box and the features and merge settings in one call:

```bash
./scripts/check-repo-settings.sh --apply \
  --description "What this repository is, in one line" --topics "bam,aws,python"
```

A setting that does not hold here on purpose (a ruleset or secret scanning on a
private repository on GitHub Free, rebase merging chosen over squash) is
declared with its reason in `.github/repo-settings-exceptions.txt`, one
`key: reason` line each; it then prints as `DECLARED` instead of `FAIL`, and
`--apply` leaves that setting alone.

Green CI and every setting `ok` or `DECLARED`. That is the whole checklist.

## Multi-branch repositories

BAM pipeline repositories (the Engine, the Launcher, Init, the Console API) do
not have one `main`. They have three deploy branches, `dev`, `preprod` and
`prod`, kept at one SHA; the owner pushes to all three directly, and a push to
any of them deploys through CodeBuild. The default branch is usually `prod`.

The template covers that shape without forking its files. What changes:

| What | Single-branch (shipped) | Multi-branch |
|---|---|---|
| "`main`" in `AGENTS.md`, `CONTRIBUTING.md`, `CLAUDE.md` | the default branch | every deploy branch, kept at one SHA — the files say so, keep them as shipped |
| `ci.yml` `on.push.branches` | `[main]` | `[dev, preprod, prod]` — the one edit; the comment above `on:` shows it |
| `wiki.yml`, `label-sync.yml` | publish from the default branch | unchanged: the job-level `if:` follows the default branch, whatever it is called |
| `.pre-commit-config.yaml` | `check-yaml --unsafe`, `check-json` skips JSONC configs by name | unchanged: CloudFormation short tags (`!Ref`, `!Sub`) and `.oxlintrc.json` / `tsconfig*.json` already pass |
| Ruleset | `.github/rulesets/main.example.json` | `.github/rulesets/multi-branch.example.json`, plus the repository's build checks — see [step 6](#6-apply-a-ruleset) |

A deploy branch that `ci.yml` does not list is a branch whose pushes deploy
without the gate ever running.

## Where to go next

- [Home](Home) — how this wiki is generated and the page conventions
- `CONTRIBUTING.md` — branch, commit, and pull request conventions
- `SECURITY.md` — reporting a vulnerability, and where secrets belong
