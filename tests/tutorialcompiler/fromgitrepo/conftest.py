import pytest

import pygit2
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH


@pytest.fixture(scope="session")
def this_raw_repo():
    return pygit2.Repository(".")


@pytest.fixture(scope="session")
def cloned_repo(tmpdir_factory):
    clone_path = tmpdir_factory.mktemp("tutorials-")
    repo = pygit2.clone_repository(".",
                                   clone_path,
                                   checkout_branch="unit-tests-commits")

    tutorial_path = clone_path / "boing/tutorial.md"

    with open(tutorial_path, "wt") as f_tutorial:
        f_tutorial.write("Working copy of tutorial\n")

    summary_path = clone_path / "boing/summary.md"

    with open(summary_path, "wt") as f_summary:
        f_summary.write("# Working summary for Boing\n")

    return repo


@pytest.fixture(
    scope="session",
    params=list(TH.ProjectHistory.TutorialTextSource),
)
def project_history(cloned_repo, request):
    return TH.ProjectHistory(cloned_repo.workdir,
                             "unit-tests-commits",
                             request.param)


@pytest.fixture(scope="session")
def tutorial_md_text(project_history):
    return project_history.tutorial_text
