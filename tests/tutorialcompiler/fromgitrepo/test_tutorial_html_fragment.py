import pytest
from dataclasses import dataclass
from bs4 import BeautifulSoup

import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_html_fragment as THF


@dataclass
class MockHunkLine:
    old_lineno: int
    new_lineno: int
    content: str


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
