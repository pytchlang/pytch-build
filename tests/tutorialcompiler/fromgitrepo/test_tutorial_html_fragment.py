import pytest
from dataclasses import dataclass
from typing import List
from bs4 import BeautifulSoup

import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_html_fragment as THF


@dataclass
class MockHunkLine:
    old_lineno: int
    new_lineno: int
    content: str


@dataclass
class MockHunk:
    lines: List[MockHunkLine]


@dataclass
class MockPatch:
    hunks: List[MockHunk]


@pytest.fixture
def soup():
    return BeautifulSoup('', 'html.parser')


class TestHunkTable:
    @pytest.mark.parametrize(
        'old_lineno,new_lineno,exp_class',
        [
            (10, 12, 'diff-unch'),
            (-1, 8, 'diff-add'),
            (12, -1, 'diff-del')
        ])
    def test_line_classification(self, old_lineno, new_lineno, exp_class):
        mock_hunk_line = MockHunkLine(old_lineno, new_lineno, 'ignored')
        got_class = THF.line_classification(mock_hunk_line)
        assert got_class == exp_class

    @pytest.mark.parametrize(
        'lineno,exp_html',
        [
            (-1, '<td></td>'),
            (10, '<td>10</td>'),
        ])
    def test_table_data_from_line_number(self, soup, lineno, exp_html):
        got_html = THF.table_data_from_line_number(soup, lineno)
        assert str(got_html) == exp_html

    def test_table_row_from_line(self, soup):
        line = MockHunkLine(10, 12, 'foo()')
        got_html = THF.table_row_from_line(soup, line)
        assert str(got_html) == (
            '<tr>'
            '<td>10</td><td>12</td>'
            '<td><pre>foo()</pre></td></tr>'
        )

    def test_table_from_hunk(self, soup):
        hunk = MockHunk([
            MockHunkLine(10, 12, 'foo()'),
            MockHunkLine(11, -1, 'bar()'),
        ])
        got_html = THF.table_from_hunk(soup, hunk)
        assert str(got_html) == (
            '<table>'
            '<tbody class="diff-unch">'
            '<tr>'
            '<td>10</td><td>12</td>'
            '<td><pre>foo()</pre></td></tr>'
            '</tbody>'
            '<tbody class="diff-del">'
            '<tr>'
            '<td>11</td><td></td>'
            '<td><pre>bar()</pre></td></tr>'
            '</tbody>'
            '</table>'
        )

    def test_tables_div_from_patch(self, soup):
        patch = MockPatch([
            MockHunk([
                MockHunkLine(10, 12, 'foo()'),
                MockHunkLine(11, -1, 'bar()'),
            ]),
            MockHunk([
                MockHunkLine(-1, 22, 'baz()'),
                MockHunkLine(24, 24, 'qux()'),
            ]),
        ])
        got_html = THF.tables_div_from_patch(soup, patch)
        assert str(got_html) == (
            '<div class="patch">'
            '<table>'
            '<tbody class="diff-unch">'
            '<tr>'
            '<td>10</td><td>12</td>'
            '<td><pre>foo()</pre></td></tr>'
            '</tbody>'
            '<tbody class="diff-del">'
            '<tr>'
            '<td>11</td><td></td>'
            '<td><pre>bar()</pre></td></tr>'
            '</tbody>'
            '</table>'
            '<table>'
            '<tbody class="diff-add">'
            '<tr>'
            '<td></td><td>22</td>'
            '<td><pre>baz()</pre></td></tr>'
            '</tbody>'
            '<tbody class="diff-unch">'
            '<tr>'
            '<td>24</td><td>24</td>'
            '<td><pre>qux()</pre></td></tr>'
            '</tbody>'
            '</table>'
            '</div>'
        )


class TestHtmlFragment:
    @staticmethod
    def paragraph(soup, text):
        p = soup.new_tag("p")
        p.append(text)
        return p

    def test_div_from_chapter(self, soup):
        chapter = [
            self.paragraph(soup, "hello"),
            self.paragraph(soup, "world"),
        ]
        assert str(THF.div_from_chapter(soup, chapter)) == (
            '<div class="chapter-content">'
            '<p>hello</p>'
            '<p>world</p>'
            '</div>'
        )

    def test_div_from_front_matter(self, soup):
        front_matter = [
            self.paragraph(soup, "hello"),
            self.paragraph(soup, "world"),
        ]
        code = 'foo()'
        # It's possible this will fail one day if I'm making unwarranted
        # assumptions about the order in which attributes are represented
        # in the string form of an HTML fragment.
        assert str(THF.div_from_front_matter(soup, front_matter, code)) == (
            '<div class="front-matter" data-complete-code-text="foo()">'
            '<p>hello</p>'
            '<p>world</p>'
            '</div>'
        )


class TestPredicates:
    @pytest.mark.parametrize(
        'html,exp_is_relevant',
        [
            ('<p>Hello</p>', True),
            ('   Hello', True),
            ('Hello       ', True),
            ('    ', False),
            ('\n\nfoo\n', True),
        ])
    def test_node_is_relevant(self, html, exp_is_relevant):
        soup = BeautifulSoup(html, "html.parser")
        node = next(soup.children)
        assert THF.node_is_relevant(node) == exp_is_relevant

    @pytest.mark.parametrize(
        'html,exp_is_patch',
        [
            ('<p>Hello</p>', False),
            ('<div><p>Hello</p></div>', False),
            ('<div class="banana"><p>Hello</p></div>', False),
            ('<div class="patch-hunks"><p>Hello</p></div>', True),
            ('<div class="patch-hunks banana"><p>Hello</p></div>', True),
        ])
    def test_node_is_patch(self, html, exp_is_patch):
        soup = BeautifulSoup(html, "html.parser")
        node = next(soup.children)
        assert THF.node_is_patch(node) == exp_is_patch
