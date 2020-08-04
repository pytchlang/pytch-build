from dataclasses import dataclass
from typing import List
from pathlib import Path
import bs4

from .tutorial_history import ProjectAsset
from .tutorial_html_fragment import div_from_project_history


@dataclass
class TutorialBundle:
    top_level_directory_name: Path
    html_fragment: bs4.element.Tag
    assets: List[ProjectAsset]

    @classmethod
    def from_project_history(cls, project_history):
        return cls(
            Path(project_history.top_level_directory_name),
            div_from_project_history(project_history),
            project_history.all_project_assets
        )
