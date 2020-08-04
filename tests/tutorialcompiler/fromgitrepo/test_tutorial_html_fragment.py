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
            '<tr class="diff-unch">'
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
            '<tr class="diff-unch">'
            '<td>10</td><td>12</td>'
            '<td><pre>foo()</pre></td></tr>'
            '<tr class="diff-del">'
            '<td>11</td><td></td>'
            '<td><pre>bar()</pre></td></tr>'
            '</table>'
        )
