from dataclasses import dataclass
from typing import Dict
import yaml
import bs4
from pathlib import Path

from .fromgitrepo import git_repository
from .fromgitrepo.tutorial_history import ProjectHistory


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
