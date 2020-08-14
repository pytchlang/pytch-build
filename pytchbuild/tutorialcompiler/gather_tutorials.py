from dataclasses import dataclass
from typing import Dict
import yaml
import bs4
from pathlib import Path
import copy

from .fromgitrepo import git_repository
from .fromgitrepo.tutorial_history import ProjectHistory
from .fromgitrepo.tutorial_bundle import TutorialBundle


@dataclass
class TutorialSummary:
    name: str  # Currently just for human readers
    div: bs4.element.Tag


@dataclass
class TutorialCollection:
    tutorials: Dict[str, ProjectHistory]

    @classmethod
    def from_repo_path(cls, repo_path):
        with git_repository(repo_path) as repo:
            index_path = Path(repo.workdir) / "index.yaml"
            with index_path.open("rt") as yaml_file:
                tutorial_dicts = yaml.load(yaml_file, yaml.Loader)

        tutorials = {d["name"]: ProjectHistory(repo_path, d["tip-commit"])
                     for d in tutorial_dicts}
        return cls(tutorials)

    def write_to_zipfile(self, zfile):
        bundles = [TutorialBundle.from_project_history(project_history)
                   for project_history in self.tutorials.values()]

        for bundle in bundles:
            bundle.write_to_zipfile(zfile)

        index_soup = bs4.BeautifulSoup('<div class="tutorial-index"></div>',
                                       "html.parser")
        index_div = index_soup.find("div")
        for bundle in bundles:
            summary_div = copy.deepcopy(bundle.summary_html)
            summary_div["data-tutorial-name"] = bundle.top_level_directory_name
            index_div.append(summary_div)

        zfile.writestr("tutorial-index.html", index_soup.encode("utf-8"))
