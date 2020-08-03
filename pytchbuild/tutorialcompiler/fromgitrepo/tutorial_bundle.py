from dataclasses import dataclass
from typing import List
import bs4

from .tutorial_history import ProjectAsset


@dataclass
class TutorialBundle:
    html_fragment: bs4.element.Tag
    assets: List[ProjectAsset]
