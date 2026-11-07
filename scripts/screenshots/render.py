#!/usr/bin/env python3
"""Build the HTML pages that scripts/screenshots/capture.sh photographs.

    render.py REPO_ROOT CSS_FILE OUT_DIR OWNER/REPO

Writes three self-contained pages into OUT_DIR:

  readme.html                 README.md through GitHub's own Markdown renderer
                              (`gh api markdown`, mode=markdown — the mode GitHub
                              uses for repository files, so soft line breaks stay
                              soft), styled with github-markdown-css. One
                              substitution: the GitHub Actions status badge of a
                              private repository only loads with a GitHub login,
                              so it is drawn as a static shields-style "CI" label
                              (CI_BADGE below). Nothing else is altered, and the
                              README caption under the gallery says so.
  pull-request-template.html  .github/PULL_REQUEST_TEMPLATE.md through the same
                              renderer in mode=gfm — the mode GitHub uses for a
                              pull request body, which is where it appears.
  issue-form-bug.html         .github/ISSUE_TEMPLATE/bug.yml drawn as an HTML
                              mock of GitHub's issue form. GitHub has no API that
                              renders an issue form, so every field is built from
                              the YAML and the page says, on its face, that it is
                              a rendering. Markdown blocks still go through
                              `gh api markdown`.

Needs: python3 with PyYAML, and `gh` authenticated (the Markdown API call).
"""

from __future__ import annotations

import base64
import html
import re
import subprocess
import sys
from pathlib import Path

import yaml

# A workflow status badge: https://github.com/OWNER/REPO/actions/workflows/<f>/badge.svg
WORKFLOW_BADGE = re.compile(
    r'src="https://github\.com/[^"/]+/[^"/]+/actions/workflows/[^"]+/badge\.svg[^"]*"'
)

# Static "CI" label in shields.io's flat style (20 px, 3 px radius, Verdana 11,
# grey #555 with the flat gloss and text shadow), so it sits in the badge row
# like the real one. It states no status: it is a label, not a result.
CI_BADGE = """<svg xmlns="http://www.w3.org/2000/svg" width="25" height="20" role="img" aria-label="CI">
<title>CI</title>
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<clipPath id="r"><rect width="25" height="20" rx="3" fill="#fff"/></clipPath>
<g clip-path="url(#r)"><rect width="25" height="20" fill="#555"/><rect width="25" height="20" fill="url(#s)"/></g>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
<text aria-hidden="true" x="125" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">CI</text>
<text x="125" y="140" transform="scale(.1)" fill="#fff">CI</text>
</g></svg>"""


def static_ci_badge(rendered: str) -> str:
    """Swap the private workflow badge for the static CI label, and nothing else."""
    uri = "data:image/svg+xml;base64," + base64.b64encode(CI_BADGE.encode()).decode()
    return WORKFLOW_BADGE.sub(f'src="{uri}"', rendered)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<base href="{base}">
<title>{title}</title>
<link rel="stylesheet" href="{css}">
<style>
  body {{ margin: 0; background: #ffffff; font-family: -apple-system,
         BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial,
         sans-serif; color: #1f2328; }}
  .frame {{ max-width: 1012px; margin: 24px auto; border: 1px solid #d1d9e0;
           border-radius: 6px; overflow: hidden; }}
  .frame-head {{ display: flex; align-items: center; gap: 8px;
                padding: 10px 16px; background: #f6f8fa;
                border-bottom: 1px solid #d1d9e0; font-size: 14px;
                font-weight: 600; }}
  .frame-head .path {{ color: #59636e; font-weight: 400;
                      font-family: ui-monospace, SFMono-Regular, Menlo,
                      monospace; font-size: 12px; }}
  .markdown-body {{ box-sizing: border-box; padding: 32px 45px; }}
  {extra}
</style>
</head>
<body>
<div class="frame">
  <div class="frame-head">{heading} <span class="path">{path}</span></div>
  {body}
</div>
</body>
</html>
"""

FORM_CSS = """
  .notice { margin: 16px 45px 0; padding: 8px 12px; border: 1px dashed #9a6700;
            border-radius: 6px; background: #fff8c5; font-size: 12px;
            color: #6c4400; }
  .form { padding: 8px 45px 32px; }
  .field { margin-top: 24px; }
  .field > label, .field > .label { display: block; font-weight: 600;
            font-size: 14px; margin-bottom: 6px; }
  .req { color: #d1242f; margin-left: 2px; }
  .desc { color: #59636e; font-size: 12px; margin: -2px 0 8px; }
  .control { box-sizing: border-box; width: 100%; padding: 6px 12px;
             border: 1px solid #d1d9e0; border-radius: 6px; font-size: 14px;
             background: #f6f8fa; color: #1f2328; font-family: inherit; }
  .tall { min-height: 96px; white-space: pre-wrap; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .placeholder { color: #818b98; }
  .labels { margin-top: 8px; font-size: 12px; color: #59636e; }
  .chip { display: inline-block; padding: 0 7px; border-radius: 2em;
          background: #d73a4a; color: #fff; font-weight: 500; line-height: 18px; }
  .check { display: flex; gap: 8px; align-items: baseline; font-size: 14px;
           margin: 4px 0; }
  .submit { margin-top: 24px; display: inline-block; padding: 5px 16px;
            border-radius: 6px; background: #1f883d; color: #fff;
            font-weight: 500; font-size: 14px; }
  .md { border: 0; padding: 0; }
"""


def gh_markdown(text: str, mode: str, context: str) -> str:
    result = subprocess.run(
        ["gh", "api", "markdown", "-f", f"mode={mode}", "-f", f"context={context}",
         "-F", "text=@-"],
        input=text, capture_output=True, text=True, check=True,
    )
    return result.stdout


def page(*, base: str, css: str, title: str, heading: str, path: str,
         body: str, extra: str = "") -> str:
    return PAGE.format(base=html.escape(base), css=html.escape(css),
                       title=html.escape(title), heading=html.escape(heading),
                       path=html.escape(path), body=body, extra=extra)


def control_text(value: str | None, placeholder: str | None) -> str:
    if value:
        return html.escape(value)
    if placeholder:
        return f'<span class="placeholder">{html.escape(placeholder)}</span>'
    return ""


def field_head(attrs: dict, required: bool, tag: str = "label") -> str:
    out = f'<{tag} class="label">{html.escape(str(attrs.get("label", "")))}'
    if required:
        out += '<span class="req">*</span>'
    out += f"</{tag}>"
    if attrs.get("description"):
        out += f'<div class="desc">{html.escape(str(attrs["description"]))}</div>'
    return out


def render_form(form: dict, context: str) -> str:
    parts = [
        '<div class="notice">Rendering of <code>.github/ISSUE_TEMPLATE/bug.yml</code>'
        " — a local HTML mock built from the YAML, not a capture of github.com.</div>",
        '<div class="form">',
        f'<div class="field"><label class="label">{html.escape(form["name"])}</label>'
        f'<div class="desc">{html.escape(form.get("description", ""))}</div></div>',
        '<div class="field"><label class="label">Add a title<span class="req">*</span></label>'
        f'<div class="control">{html.escape(form.get("title", ""))}</div>',
    ]
    labels = form.get("labels") or []
    if labels:
        chips = " ".join(f'<span class="chip">{html.escape(x)}</span>' for x in labels)
        parts.append(f'<div class="labels">Labels applied on submit: {chips}</div>')
    parts.append("</div>")

    for item in form.get("body", []):
        kind = item["type"]
        attrs = item.get("attributes", {})
        required = bool(item.get("validations", {}).get("required"))
        if kind == "markdown":
            rendered = gh_markdown(attrs["value"], "gfm", context)
            parts.append(f'<div class="field markdown-body md">{rendered}</div>')
        elif kind == "textarea":
            mono = " mono" if attrs.get("render") else ""
            parts.append(
                f'<div class="field">{field_head(attrs, required)}'
                f'<div class="control tall{mono}">'
                f"{control_text(attrs.get('value'), attrs.get('placeholder'))}</div></div>"
            )
        elif kind == "input":
            parts.append(
                f'<div class="field">{field_head(attrs, required)}'
                f'<div class="control">{control_text(attrs.get("value"), attrs.get("placeholder"))}'
                "&nbsp;</div></div>"
            )
        elif kind == "dropdown":
            options = "".join(f"<option>{html.escape(str(o))}</option>"
                              for o in attrs.get("options", []))
            parts.append(
                f'<div class="field">{field_head(attrs, required)}'
                f'<select class="control"><option>Selections: None</option>{options}'
                "</select></div>"
            )
        elif kind == "checkboxes":
            star = '<span class="req">*</span>'
            boxes = "".join(
                '<div class="check"><input type="checkbox" disabled>'
                f"<span>{html.escape(str(o['label']))}"
                f"{star if o.get('required') else ''}</span></div>"
                for o in attrs.get("options", [])
            )
            parts.append(f'<div class="field">{field_head(attrs, False, "div")}{boxes}</div>')
        else:
            raise SystemExit(f"render.py: unsupported issue-form field type {kind!r}")

    parts.append('<div class="submit">Create</div></div>')
    return "\n".join(parts)


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    root = Path(sys.argv[1]).resolve()
    css = Path(sys.argv[2]).resolve().as_uri()
    out = Path(sys.argv[3]).resolve()
    context = sys.argv[4]
    base = root.as_uri() + "/"
    out.mkdir(parents=True, exist_ok=True)

    readme = static_ci_badge(
        gh_markdown((root / "README.md").read_text(encoding="utf-8"), "markdown", context)
    )
    (out / "readme.html").write_text(page(
        base=base, css=css, title="README", heading="README", path="README.md",
        body=f'<article class="markdown-body">{readme}</article>',
    ), encoding="utf-8")

    pr_path = ".github/PULL_REQUEST_TEMPLATE.md"
    pr = gh_markdown((root / pr_path).read_text(encoding="utf-8"), "gfm", context)
    (out / "pull-request-template.html").write_text(page(
        base=base, css=css, title="Pull request template",
        heading="Pull request description", path=pr_path,
        body=f'<article class="markdown-body">{pr}</article>',
    ), encoding="utf-8")

    form_path = ".github/ISSUE_TEMPLATE/bug.yml"
    form = yaml.safe_load((root / form_path).read_text(encoding="utf-8"))
    (out / "issue-form-bug.html").write_text(page(
        base=base, css=css, title="Bug report form", heading="New issue",
        path=form_path, body=render_form(form, context), extra=FORM_CSS,
    ), encoding="utf-8")


if __name__ == "__main__":
    main()
