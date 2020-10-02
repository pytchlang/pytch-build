import re
import xml.etree.ElementTree as etree
import markdown
from bs4 import BeautifulSoup


class ShortcodeProcessor(markdown.blockprocessors.BlockProcessor):
    RE_SHORTCODE = re.compile(r"^\s*\{\{< ([-\w]+)( (.*))? >\}\}\s*$")

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
        elif kind == "run-finished-project":
            etree.SubElement(parent, "div",
                             {"class": "run-finished-project"})
        elif kind == "work-in-progress":
            etree.SubElement(parent, "div",
                             {"class": "work-in-progress"})
        else:
            raise ValueError(f'unknown shortcode kind "{kind}"')


class ShortcodeExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        # Not sure what priority is appropriate; 20 seems to work.
        md.parser.blockprocessors.register(
            ShortcodeProcessor(md.parser),
            'shortcode',
            20
        )


def soup_from_markdown_text(markdown_text):
    html = markdown.markdown(markdown_text, extensions=[ShortcodeExtension()])
    soup = BeautifulSoup(html, "html.parser")
    return soup


def ordered_commit_slugs_in_soup(soup):
    return [elt.attrs["data-slug"]
            for elt in soup.find_all("div",
                                     attrs={"class": "patch-container"})]
