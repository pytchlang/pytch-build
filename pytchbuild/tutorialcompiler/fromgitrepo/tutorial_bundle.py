from dataclasses import dataclass
from typing import List
from contextlib import closing
from pathlib import Path
import zipfile
import bs4

from .tutorial_history import Asset
from .tutorial_html_fragment import (
    tutorial_div_from_project_history,
    summary_div_from_project_history,
)


@dataclass
class TutorialBundle:
    top_level_directory_name: Path
    tutorial_html: bs4.element.Tag
    summary_html: bs4.element.Tag
    assets: List[Asset]

    @classmethod
    def from_project_history(cls, project_history):
        return cls(
            Path(project_history.top_level_directory_name),
            tutorial_div_from_project_history(project_history),
            summary_div_from_project_history(project_history),
            project_history.all_project_assets
        )

    def write_zipfile(self, out_file):
        bare_zfile = zipfile.ZipFile(out_file,
                                     mode="w",
                                     compression=zipfile.ZIP_DEFLATED)

        with closing(bare_zfile) as zfile:
            bundle_root_path = Path(self.top_level_directory_name)
            tutorial_html_path = bundle_root_path / "tutorial.html"
            tutorial_html_bytes = self.tutorial_html.encode("utf-8")
            zfile.writestr(str(tutorial_html_path), tutorial_html_bytes)

            for asset in self.assets:
                zfile.writestr(asset.path, asset.data)
