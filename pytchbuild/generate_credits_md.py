"""One-off tool to bootstrap a ``credits.md`` for a tutorial branch.

Given a branch, this walks its git history, reuses the *legacy*
commit-message credit extraction (``ProjectCommit.assets_credits``, surfaced
as ``ProjectHistory.commit_message_asset_credits``), and writes a first-draft
``credits.md`` to stdout.

The output is a **draft** for a human to review: any tip-tree asset for which
no commit-message credit can be recovered is emitted with a ``TODO``
placeholder, and a warning (on stderr) lists those assets.  Because the
build's new validator guarantees completeness before any branch can build,
the known bugs in the old extractor do not matter here.
"""

from collections import OrderedDict

import pygit2
import click

from .tutorialcompiler.fromgitrepo.tutorial_history import (
    ProjectHistory,
    PROJECT_ASSET_DIRNAME,
    TUTORIAL_ASSET_DIRNAME,
)


TODO_PLACEHOLDER = "TODO: credit needed."


def collapse_whitespace(text):
    """Collapse runs of whitespace (incl. newlines) to single spaces.

    The legacy credit body is the multi-line commit message body; for a
    single bullet in the first-draft ``credits.md`` we flatten it.  A human
    reviews and reformats afterwards.
    """
    return " ".join(text.split())


def credit_body_from_basename(project_history):
    """Map each asset basename to its (flattened) legacy credit body.

    Where a basename is credited by more than one commit (e.g. an add and a
    later modify), the earliest — i.e. the adding commit — wins, matching
    "the credit ... in the commit that added it".
    """
    body_from_basename = {}
    # commit_message_asset_credits is earliest-first, so the first credit
    # seen for a basename is the one from its adding commit.
    for entry in project_history.commit_message_asset_credits:
        body = collapse_whitespace(entry.credit_markdown)
        for basename in entry.asset_basenames:
            body_from_basename.setdefault(basename, body)
    return body_from_basename


def bullet_line(basenames, body):
    quoted = ", ".join(f"`{name}`" for name in basenames)
    return f"- {quoted} — {body}\n"


def section_lines(heading, basenames, body_from_basename, todo_basenames):
    """Markdown lines for one asset-location section.

    Assets sharing an identical recovered credit body are grouped into one
    bullet; each asset with no recovered credit gets its own ``TODO`` bullet.
    """
    if not basenames:
        return []

    lines = [f"## {heading}\n", "\n"]

    # Group credited assets by identical body, preserving first-seen order.
    groups = OrderedDict()
    for basename in sorted(basenames):
        if basename in body_from_basename:
            groups.setdefault(body_from_basename[basename], []).append(basename)

    for body, group_basenames in groups.items():
        lines.append(bullet_line(group_basenames, body))

    # One clearly-marked placeholder bullet per uncovered asset.
    for basename in sorted(basenames):
        if basename not in body_from_basename:
            todo_basenames.append(basename)
            lines.append(bullet_line([basename], TODO_PLACEHOLDER))

    lines.append("\n")
    return lines


def credits_md_text(project_history):
    """The first-draft ``credits.md`` text, plus the list of TODO basenames."""
    project_basenames = project_history.tip_tree_asset_basenames(
        PROJECT_ASSET_DIRNAME
    )
    tutorial_basenames = project_history.tip_tree_asset_basenames(
        TUTORIAL_ASSET_DIRNAME
    )
    body_from_basename = credit_body_from_basename(project_history)

    name = project_history.top_level_directory_name
    lines = [f"# Credits for {name}\n", "\n"]

    todo_basenames = []
    lines += section_lines(
        "Project assets", project_basenames, body_from_basename, todo_basenames
    )
    lines += section_lines(
        "Tutorial assets", tutorial_basenames, body_from_basename, todo_basenames
    )

    return "".join(lines), todo_basenames


@click.command()
@click.argument("branch")
@click.option(
    "-r", "--repository-path",
    default=pygit2.discover_repository("."),
    envvar="GIT_DIR",
    metavar="PATH",
    help="path to root of git repository",
)
def main(branch, repository_path):
    """Write to stdout a first-draft credits.md for the tutorial on BRANCH."""
    project_history = ProjectHistory(
        repository_path, branch, should_validate_credits=False
    )
    text, todo_basenames = credits_md_text(project_history)

    click.echo(text, nl=False)

    if todo_basenames:
        click.echo(
            f"WARNING: {len(todo_basenames)} asset/s need a credit filled in:"
            f" {sorted(todo_basenames)}",
            err=True,
        )
