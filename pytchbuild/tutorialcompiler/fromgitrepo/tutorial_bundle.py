from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from contextlib import closing
from pathlib import Path
import zipfile
import bs4
import json

from .tutorial_history import Asset
from .tutorial_html_fragment import (
    tutorial_div_from_project_history,
    summary_div_from_project_history,
)
from .structured_program import StructuredPytchProgram


@dataclass
class TutorialBundle:
    top_level_directory_name: Path
    tutorial_html: bs4.element.Tag
    summary_html: bs4.element.Tag
    assets: List[Asset]
    final_code_text: str
    metadata: Dict[str, Any]

    @classmethod
    def from_project_history(cls, project_history):
        return cls(
            Path(project_history.top_level_directory_name),
            tutorial_div_from_project_history(project_history),
            summary_div_from_project_history(project_history),
            project_history.all_assets,
            project_history.final_code_text,
            json.loads(project_history.metadata_text),
        )

    def maybe_write_structured_json(self, out_zipfile):
        program_kind = self.metadata.get("programKind", "flat")
        if program_kind != "per-method":
            return

        program = (
            StructuredPytchProgram(self.final_code_text)
            .as_NoIdsStructuredProject()
        )
        program_json = json.dumps(asdict(program))

        bundle_root_path = Path(self.top_level_directory_name)
        path = bundle_root_path / "skeleton-structured-program.json"

        out_zipfile.writestr(
            str(path),
            program_json.encode("utf-8")
        )

    def write_to_zipfile(self, out_zipfile):
        bundle_root_path = Path(self.top_level_directory_name)

        tutorial_html_path = bundle_root_path / "tutorial.html"
        tutorial_html_bytes = self.tutorial_html.encode("utf-8")
        out_zipfile.writestr(str(tutorial_html_path), tutorial_html_bytes)

        summary_html_path = bundle_root_path / "summary.html"
        summary_html_bytes = self.summary_html.encode("utf-8")
        out_zipfile.writestr(str(summary_html_path), summary_html_bytes)

        project_asset_paths = [a.path for a in self.assets if a.is_project_asset]
        assets_manifest_path = bundle_root_path / "project-assets.json"
        assets_manifest_bytes = json.dumps(project_asset_paths).encode("utf-8")
        out_zipfile.writestr(str(assets_manifest_path), assets_manifest_bytes)

        for asset in self.assets:
            out_zipfile.writestr(asset.path, asset.data)

    def write_new_zipfile(self, out_file):
        bare_zfile = zipfile.ZipFile(out_file,
                                     mode="w",
                                     compression=zipfile.ZIP_DEFLATED)

        with closing(bare_zfile) as zfile:
            self.write_to_zipfile(zfile)
