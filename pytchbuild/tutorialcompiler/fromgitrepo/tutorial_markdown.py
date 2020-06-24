import re
import xml.etree.ElementTree as etree
import markdown
from bs4 import BeautifulSoup


class ShortcodeProcessor(markdown.blockprocessors.BlockProcessor):
    RE_SHORTCODE = re.compile(r"^\s*\{\{< (\w+) (.*) >\}\}\s*$")

    def test(self, parent, block):
        m = self.RE_SHORTCODE.match(block)
        # TODO: More extensible shortcode mechanism.
        return (m is not None) and m.group(1) == "commit"

    def run(self, parent, blocks):
        block = blocks.pop(0)
        re_match = self.RE_SHORTCODE.match(block)

        # Ignore value; goal is side-effect of attaching to parent:
        etree.SubElement(parent, "div",
                         {"class": "patch-hunks",
                          "data-slug": re_match.group(2)})


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
