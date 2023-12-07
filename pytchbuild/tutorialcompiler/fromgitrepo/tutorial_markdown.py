import re
import xml.etree.ElementTree as etree
import markdown
import markdown.extensions.fenced_code
from bs4 import BeautifulSoup
import copy
import json

from .errors import TutorialStructureError


class ShortcodeProcessor(markdown.blockprocessors.BlockProcessor):
    RE_SHORTCODE = re.compile(r"^\s*\{\{< ([-/\w]+)( (.*))? >\}\}\s*$")

    simple_shortcode_kinds = [
        "run-finished-project", "work-in-progress", "asset-credits",
        "learner-task", "/learner-task", "learner-task-help",
    ]

    def test(self, parent, block):
        m = self.RE_SHORTCODE.match(block)
        return (m is not None)

    def run(self, parent, blocks):
        block = blocks.pop(0)
        re_match = self.RE_SHORTCODE.match(block)
        kind = re_match.group(1)
        args_str = re_match.group(3)

        if kind == "commit":
            # Ignore value; goal is side-effect of attaching to parent:
            etree.SubElement(parent, "div",
                             {"class": "patch-container",
                              "data-slug": args_str})
        elif kind == "jr-commit":
            [slug, commit_kind, *commit_args] = args_str.split(" ")
            etree.SubElement(parent, "div",
                             {"class": "jr-commit",
                              "data-slug": slug,
                              "data-jr-commit-kind": commit_kind,
                              "data-jr-commit-args": json.dumps(commit_args)})
        elif kind in self.simple_shortcode_kinds:
            etree.SubElement(parent, "div", {"class": kind})
        else:
            raise TutorialStructureError(f'unknown shortcode kind "{kind}"')


class ShortcodeExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        # Not sure what priority is appropriate; 20 seems to work.
        md.parser.blockprocessors.register(
            ShortcodeProcessor(md.parser),
            'shortcode',
            20
        )


def node_is_from_shortcode(node, target_shortcode):
    if node.name != "div":
        return False
    node_classes = node.attrs.get("class", [])
    return target_shortcode in node_classes


def new_div(soup, div_class):
    div = soup.new_tag("div")
    div.attrs["class"] = div_class
    return div


def gather_learner_task_divs(flat_soup):
    """Create a new soup with structured learner tasks.

    The input `flat_soup` should have sequential DIVs for the start-
    and end-markers of each learner task.  Between them (still at the
    same nesting level in the input soup) should be learner-task-help
    DIVs which mark the start of each help section.

    Gather all the DIVs for one learner task into a single DIV
    containing inner DIVs for:

    The introduction, which is everything up to (but excluding) the
    first learner-task-help DIV, and is turned into a
    learner-task-intro DIV.

    Zero or more help sections, each of which is turned into a
    learner-task-help DIV.
    """
    soup = BeautifulSoup("", features="html.parser")
    empty_chunk_error = TutorialStructureError(
        "empty learner chunk (intro/help)"
    )

    elts = flat_soup.children
    for elt in elts:
        if node_is_from_shortcode(elt, "learner-task"):
            task_div = new_div(soup, "learner-task")
            chunk_div = new_div(soup, "learner-task-intro")
            for elt in elts:
                if node_is_from_shortcode(elt, "/learner-task"):
                    break
                if node_is_from_shortcode(elt, "learner-task-help"):
                    if len(chunk_div.contents) == 0:
                        raise empty_chunk_error
                    task_div.append(chunk_div)
                    chunk_div = new_div(soup, "learner-task-help")
                else:
                    chunk_div.append(copy.copy(elt))
            task_div.append(chunk_div)
            soup.append(task_div)
        else:
            soup.append(copy.copy(elt))

    return soup


def soup_from_markdown_text(markdown_text):
    html = markdown.markdown(
        markdown_text,
        extensions=[ShortcodeExtension(), "fenced_code"]
    )
    flat_soup = BeautifulSoup(html, "html.parser")
    soup = gather_learner_task_divs(flat_soup)
    return soup


def slugs_for_class(soup, cls):
    """List of "data-slug" attrs for elements of given `cls`."""
    return [
        elt.attrs["data-slug"]
        for elt in soup.find_all("div", attrs={"class": cls})
    ]


def ordered_commit_slugs_in_soup(soup):
    patch_slugs = slugs_for_class(soup, "patch-container")
    jr_slugs = slugs_for_class(soup, "jr-commit")

    have_patch_slugs = len(patch_slugs) > 0
    have_jr_slugs = len(jr_slugs) > 0

    if have_patch_slugs and have_jr_slugs:
        raise TutorialStructureError("mixture of patch and jr-commit slugs")

    return patch_slugs if have_patch_slugs else jr_slugs
