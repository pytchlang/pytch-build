"""Compile a tutorial from a git repo with a certain structure

TODO: Complete these docs.
"""

from contextlib import contextmanager
import pygit2


from .tutorial_history import ProjectHistory
from .tutorial_bundle import TutorialBundle
from .tutorial_html_fragment import tutorial_div_from_project_history


def compile(zipfile_out, git_repo_path, tip_revision, tutorial_text_source):
    project_history = ProjectHistory(git_repo_path,
                                     tip_revision,
                                     tutorial_text_source)

    bundle = TutorialBundle.from_project_history(project_history)
    bundle.write_new_zipfile(zipfile_out)


def compile_html_only(
        html_fragment_out,
        git_repo_path,
        tip_revision,
        tutorial_text_source,
):
    project_history = ProjectHistory(git_repo_path,
                                     tip_revision,
                                     tutorial_text_source)
    tutorial_html = tutorial_div_from_project_history(project_history)

    # We have this file as binary; explicitly encode.
    html_fragment_out.write(tutorial_html.encode("utf-8"))


@contextmanager
def git_repository(path):
    """Context manager which calls .free() on exiting context"""
    repo = pygit2.Repository(path)
    yield repo
    repo.free()
