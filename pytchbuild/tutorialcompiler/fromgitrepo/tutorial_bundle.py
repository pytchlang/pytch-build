from dataclasses import dataclass
from typing import List
import bs4

from .tutorial_history import ProjectAsset
from .tutorial_html_fragment import div_from_project_history


@dataclass
class TutorialBundle:
    html_fragment: bs4.element.Tag
    assets: List[ProjectAsset]

    @classmethod
    def from_project_history(cls, project_history):
        return cls(
            div_from_project_history(project_history),
            project_history.all_project_assets
        )
