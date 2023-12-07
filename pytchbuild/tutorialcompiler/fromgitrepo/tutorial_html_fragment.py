"""Create an *HTML soup* of the tutorial

TODO: Add syntax highlighting to the code in the table rows?  Might be useful.

TODO: Do something clearer with multiple hunks in the one patch, rather than
just stacking two tables?
"""

import re
import json
import copy
import bs4
import difflib
import colorlog

from .tutorial_markdown import (
    soup_from_markdown_text,
    ordered_commit_slugs_in_soup,
)

from .errors import InternalError, TutorialStructureError

logger = colorlog.getLogger(__name__)


def line_classification(hunk_line):
    return ("diff-add" if hunk_line.old_lineno == -1
            else "diff-del" if hunk_line.new_lineno == -1
            else "diff-unch")


def table_data_from_line_number(soup, lineno):
    cell = soup.new_tag("td", attrs={"class": "linenum"})
    if lineno != -1:
        lineno_pre = soup.new_tag("pre")
        lineno_pre.append(str(lineno))
        cell.append(lineno_pre)
    return cell


def table_row_from_line(soup, line):
    row = soup.new_tag("tr")
    content_cell = soup.new_tag("td")
    content_pre = soup.new_tag("pre")

    row.append(table_data_from_line_number(soup, line.old_lineno))
    row.append(table_data_from_line_number(soup, line.new_lineno))

    content_pre.append(line.content.rstrip("\n"))
    content_cell.append(content_pre)
    row.append(content_cell)

    return row


def table_from_hunk(soup, hunk):
    prev_class = None
    running_tbody = None
    tbody_elts = []

    for line in hunk.lines:
        line_class = line_classification(line)
        if line_class != prev_class:
            tbody_elts.append(running_tbody)
            running_tbody = soup.new_tag("tbody", attrs={"class": line_class})
            if line_class == "diff-add":
                running_tbody["data-added-text"] = ""

        prev_class = line_class

        running_tbody.append(table_row_from_line(soup, line))
        if line_class == "diff-add":
            running_tbody["data-added-text"] += line.content

    table = soup.new_tag("table")
    for tbody in tbody_elts[1:] + [running_tbody]:
        table.append(tbody)

    return table


def tables_div_from_patch(soup, patch):
    div = soup.new_tag("div", attrs={"class": "patch"})
    for hunk in patch.hunks:
        div.append(table_from_hunk(soup, hunk))
    return div


def div_from_elements(soup, div_class, elements):
    div = soup.new_tag("div", attrs={"class": div_class})
    for elt in elements:
        div.append(elt)
    return div


def div_from_chapter(soup, chapter):
    return div_from_elements(soup, "chapter-content", chapter)


def div_from_front_matter(
        soup,
        front_matter,
        maybe_seek_to_chapter,
        initial_code_text,
        final_code_text
):
    div = div_from_elements(soup, "front-matter", front_matter)
    div["data-initial-code-text"] = initial_code_text
    div["data-complete-code-text"] = final_code_text

    if maybe_seek_to_chapter is not None:
        div["data-seek-to-chapter"] = str(maybe_seek_to_chapter)

    return div


RE_WHITESPACE = re.compile(r"\s*\Z")


def node_is_relevant(soup_node):
    node_is_whitespace_string = (
        isinstance(soup_node, bs4.element.NavigableString)
        and RE_WHITESPACE.match(soup_node)
    )
    return not node_is_whitespace_string


def node_is_patch(elt):
    return (elt.name == "div"
            and elt.has_attr("class")
            and "patch-container" in elt.attrs["class"])


def node_is_work_in_progress_marker(elt):
    return (elt.name == "div"
            and elt.has_attr("class")
            and "work-in-progress" in elt.attrs["class"])


def node_is_asset_credits_marker(elt):
    return (elt.name == "div"
            and elt.has_attr("class")
            and "asset-credits" in elt.attrs["class"])


def augment_patch_elt(soup, elt, project_history):
    target_slug = elt.attrs["data-slug"]
    if project_history.slug_is_known(target_slug):
        code_text = project_history.code_text_from_slug(target_slug)
        elt.attrs["data-code-as-of-commit"] = code_text
        patch = project_history.code_patch_against_parent(target_slug)
        elt.append(tables_div_from_patch(soup, patch))
    else:
        logger.warning(f'slug "{target_slug}" not found; noting in output')
        warning_p = soup.new_tag(
            "p",
            attrs={"class": "tutorial-compiler-warning unknown-slug"})
        warning_p.append(f'Slug "{target_slug}" was not found.')
        elt.append(warning_p)


def augment_asset_credits_elt(soup, elt, project_history):
    for credit in project_history.all_asset_credits:
        credit_intro_elt = soup.new_tag("p", attrs={"class": "credit-intro"})
        credit_intro_elt.append("For ")
        first_name = True
        for name in credit.asset_basenames:
            if not first_name:
                credit_intro_elt.append(", ")
            first_name = False
            name_elt = soup.new_tag("code", attrs={"class": "asset-filename"})
            name_elt.append(name)
            credit_intro_elt.append(name_elt)
        credit_intro_elt.append(f" (used in {credit.asset_usage}):")

        elt.append(credit_intro_elt)

        credit_body_elt = soup.new_tag("div", attrs={"class": "credits"})

        credits_soup = soup_from_markdown_text(credit.credit_markdown)
        for credit_elt in credits_soup.children:
            credit_body_elt.append(credit_elt)

        elt.append(credit_body_elt)


def warn_if_slug_usage_mismatch(project_history, soup):
    """Check all tagged commits are used, in order, in the tutorial

    Emit a warning to the logger if not.
    """
    in_history = project_history.ordered_commit_slugs
    in_tutorial = ordered_commit_slugs_in_soup(soup)
    diff = list(difflib.unified_diff(
        in_history,
        in_tutorial,
        fromfile="slugs-present-in-history",
        tofile="slugs-used-in-tutorial",
        lineterm=""))
    if diff:
        logger.warning("mismatch between commit-slugs present in history"
                       " and commit-slugs used in tutorial; diff follows")
        for diff_item in diff:
            logger.warning("    " + diff_item)


def tutorial_div_from_project_history(project_history):
    soup = soup_from_markdown_text(project_history.tutorial_text)
    warn_if_slug_usage_mismatch(project_history, soup)

    chapters = []
    current_chapter = []
    front_matter = []

    past_front_matter = False
    chapter_idx = 0
    maybe_wip_chapter_idx = None

    for elt in filter(node_is_relevant, soup.children):
        if not isinstance(elt, bs4.element.Tag):
            raise InternalError(f"child {elt} not a tag")

        if elt.name == "hr":
            if past_front_matter:
                logger.warning(
                    "multiple horizontal rules (thematic breaks) found"
                )
            past_front_matter = True
        elif not past_front_matter:
            if node_is_asset_credits_marker(elt):
                augment_asset_credits_elt(soup, elt, project_history)
            if node_is_patch(elt):
                slug = elt.attrs["data-slug"]
                logger.warning(
                    f"commit \"{slug}\" found in front matter; ignoring"
                )
            front_matter.append(elt)
        elif node_is_work_in_progress_marker(elt):
            if not past_front_matter:
                raise TutorialStructureError(
                    "unexpected WiP marker in front matter"
                )
            # Although we increment chapter_idx as soon as we see the <h2>, and
            # so the first real chapter gets index 1, this is correct because
            # the front-matter is treated as "chapter 0".
            maybe_wip_chapter_idx = chapter_idx
        else:
            if node_is_patch(elt):
                augment_patch_elt(soup, elt, project_history)
            elif node_is_asset_credits_marker(elt):
                augment_asset_credits_elt(soup, elt, project_history)
            elif elt.name == "h2":
                chapters.append(current_chapter)
                current_chapter = []
                chapter_idx += 1

            current_chapter.append(elt)

    chapters.append(current_chapter)

    # Round-trip to get compact representation:
    metadata_json = json.dumps(json.loads(project_history.metadata_text))

    tutorial_div = soup.new_tag("div", attrs={
        "class": "tutorial-bundle",
        "data-tip-sha1": project_history.tip_oid_string,
        "data-metadata-json": metadata_json,
    })

    tutorial_div.append(div_from_front_matter(
        soup,
        front_matter,
        maybe_wip_chapter_idx,
        project_history.initial_code_text,
        project_history.final_code_text
    ))

    # Skip the first 'chapter'; it should be empty because the main content
    # should start with a <H2>.  TODO: Check this.
    for chapter in chapters[1:]:
        tutorial_div.append(div_from_chapter(soup, chapter))

    return tutorial_div


def summary_div_from_project_history(project_history):
    soup = soup_from_markdown_text(project_history.summary_text)
    metadata_string = project_history.metadata_text

    # Give all paragraphs holding images (which there should probably only be
    # one of, being the screenshot) an identifiable class.  The front-end is
    # going to have to patch the SRC to be within the tutorials/whatever
    # directory anyway, so it also may as well be the front-end's job to make it
    # relative to "tutorial-assets".

    for img in soup.findAll("img"):
        img.parent.attrs["class"] = "image-container"

    summary_div = soup.new_tag(
        "div",
        attrs={
            "class": "tutorial-summary",
            "data-metadata-json": metadata_string
        }
    )

    for elt in soup:
        # In other situations, trying to append the original elt
        # instance led to hard-to-track-down bugs.
        summary_div.append(copy.copy(elt))

    return summary_div
