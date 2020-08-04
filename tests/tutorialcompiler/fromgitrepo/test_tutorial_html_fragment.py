import pytest
from dataclasses import dataclass

import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_html_fragment as THF


@dataclass
class MockHunkLine:
    old_lineno: int
    new_lineno: int
    content: str
