import re
import xml.etree.ElementTree as etree
import markdown
import markdown.extensions.fenced_code
from bs4 import BeautifulSoup
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


def soup_from_markdown_text(markdown_text):
    html = markdown.markdown(
        markdown_text,
        extensions=[ShortcodeExtension(), "fenced_code"]
    )
    soup = BeautifulSoup(html, "html.parser")
    return soup


def ordered_commit_slugs_in_soup(soup):
    return [elt.attrs["data-slug"]
            for elt in soup.find_all("div",
                                     attrs={"class": "patch-container"})]
