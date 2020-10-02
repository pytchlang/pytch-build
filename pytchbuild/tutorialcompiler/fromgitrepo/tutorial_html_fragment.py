"""Create an *HTML soup* of the tutorial

TODO: Add syntax highlighting to the code in the table rows?  Might be useful.

TODO: Do something clearer with multiple hunks in the one patch, rather than
just stacking two tables?
"""

import re
import bs4
import colorlog

from .tutorial_markdown import (
    soup_from_markdown_text,
)

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


def tutorial_div_from_project_history(project_history):
    soup = soup_from_markdown_text(project_history.tutorial_text)

    chapters = []
    current_chapter = []
    front_matter = []

    past_front_matter = False
    chapter_idx = 0
    maybe_wip_chapter_idx = None

    for elt in filter(node_is_relevant, soup.children):
        if not isinstance(elt, bs4.element.Tag):
            raise ValueError(f"child {elt} not a tag")

        if elt.name == "hr":
            past_front_matter = True
        elif not past_front_matter:
            front_matter.append(elt)
        elif node_is_work_in_progress_marker(elt):
            if not past_front_matter:
                raise ValueError("unexpected WiP marker in front matter")
            # Although we increment chapter_idx as soon as we see the <h2>, and
            # so the first real chapter gets index 1, this is correct because
            # the front-matter is treated as "chapter 0".
            maybe_wip_chapter_idx = chapter_idx
        else:
            if node_is_patch(elt):
                augment_patch_elt(soup, elt, project_history)
            elif elt.name == "h2":
                chapters.append(current_chapter)
                current_chapter = []
                chapter_idx += 1

            current_chapter.append(elt)

    chapters.append(current_chapter)

    tutorial_div = soup.new_tag("div", attrs={
        "class": "tutorial-bundle",
        "data-tip-sha1": project_history.tip_oid_string,
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

    # Give all paragraphs holding images (which there should probably only be
    # one of, being the screenshot) an identifiable class.  The front-end is
    # going to have to patch the SRC to be within the tutorials/whatever
    # directory anyway, so it also may as well be the front-end's job to make it
    # relative to "tutorial-assets".

    for img in soup.findAll("img"):
        img.parent.attrs["class"] = "image-container"

    summary_div = soup.new_tag("div", attrs={"class": "tutorial-summary"})
    for elt in soup:
        summary_div.append(elt)

    return summary_div
