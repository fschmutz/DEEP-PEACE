# Security

This repository is **private**. Access to it is access to everything in it —
grant it on that basis, and remember that revoking someone's access does not
undo what they already cloned.

> Repositories created from this template must replace the scope paragraph below
> and the reporting contact with their own.

## Scope

Describe here what this repository actually holds and what the sensitivity of it
is: infrastructure identifiers, operational runbooks, application source,
customer-facing configuration. A reader should be able to tell from this section
whether a given file is safe to paste elsewhere.

## Reporting a vulnerability

**Do not open a public issue, and do not open an issue in this repository.**
Issues here are readable by everyone who has access, which defeats the purpose of
reporting privately.

Use the channel that exists for this repository's visibility:

1. **Email Falco Schmutz** at <fschmutz@premaccess.com>. This is the channel for
   every **private** repository, which is every house repository by default.
   Include what you found, how to reproduce it, and how far the exposure reaches.
2. **GitHub private vulnerability reporting**, the Security tab → _Report a
   vulnerability_, on **public** repositories only. GitHub does not offer the
   feature on private repositories: the setting is absent and
   `PUT /repos/OWNER/REPO/private-vulnerability-reporting` returns 404 there.

   **Owner checklist, once per public repository:** Settings → Advanced
   Security → _Private vulnerability reporting_ → **Enable**. It is off by
   default and nothing in the tree can turn it on. Until it is enabled there is
   no _Report a vulnerability_ button, so a reporter who follows this line finds
   nothing; a private repository keeps the email channel above as its only one.

   ```bash
   gh api repos/OWNER/REPO --jq '.visibility, (.security_and_analysis // "not visible with this token")'
   ```

Expect an acknowledgement within two business days. If the finding is a live
exposure — a leaked credential, a public mirror of a private repo, an access
grant that should not exist — say so in the first line and email as well as
filing, so it is not waiting in a queue.

## Secrets

- Secrets belong in AWS Secrets Manager or SSM Parameter Store, referenced by
  name. They never belong in the tree, in a workflow file, or in an issue.
- `gitleaks` runs in `pre-commit` and blocks the commit. Do not weaken it to
  warn-only to land a change; fix the change.
- `.env` and equivalents are git-ignored. Keep it that way.
- Workflows read secrets through `secrets.*` only, and workflow `permissions:`
  start at `contents: read` and are widened per job, never at file scope by
  default.

### Scanning is already on at the organisation

Secret scanning and push protection are enabled organisation-wide for
ScaleMeNow, so a repository made from this template inherits them. **Do not add
a secret-scanning workflow** — a second scanner duplicates the finding, bills
runner minutes for it, and gives two places to silence an alert from.

What is left to the repository is the local gate: `gitleaks` in `pre-commit`,
which catches the secret before it becomes a commit rather than after it becomes
a push. Confirm the inherited settings once, in Settings → Advanced Security,
and then leave them alone.

## Supply chain

- Every action is pinned to a full commit SHA with the version in a trailing
  comment; the `template structure` CI job fails on anything looser. A tag is
  mutable, and a moved tag runs someone else's code with this repository's
  token.
- `.github/workflows/dependency-review.yml` blocks a pull request that
  introduces a high or critical advisory. It is paths-filtered to dependency
  manifests, and it needs the dependency graph — on a private repository, that
  means GitHub Advanced Security. Without it the job reports a notice and skips
  rather than failing.
- Dependabot keeps `github-actions` and `pre-commit` pins moving weekly. A
  Dependabot pull request is a dependency change and gets read like one.

## Rotation

If a credential in this repository may have been exposed, treat rotation as a
production change: it follows the normal approval path for the system that owns
the credential, and it happens before the incident is considered closed.
