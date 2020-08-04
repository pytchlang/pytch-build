"""Compile a tutorial from a git repo with a certain structure

TODO: Complete these docs.
"""

from .tutorial_history import ProjectHistory
from .tutorial_bundle import TutorialBundle


def compile(zipfile_out, git_repo_path, tip_revision):
    project_history = ProjectHistory(git_repo_path, tip_revision)
    bundle = TutorialBundle.from_project_history(project_history)
    bundle.write_zipfile(zipfile_out)
