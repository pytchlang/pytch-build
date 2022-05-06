import pytest

import pygit2
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH
from pathlib import Path


@pytest.fixture(scope="session")
def discovered_repository_path():
    """
    The path for this repo.  As a side-effect, ensures all branches
    needed for unit tests exist.
    """
    path = pygit2.discover_repository(".")
    if path is None:
        raise ValueError("containing git repository not found")

    # Ensure we have all branches required for tests.  Any branch which
    # already exists is left alone.

    repo = pygit2.Repository(path)

    for branch_name in [
            "unit-tests-commits",
            "unit-tests-bad-commits",
            "unit-tests-commit-0",
            "unit-tests-dupd-slugs-1",
            "unit-tests-dupd-slugs-2",
    ]:
        if repo.lookup_branch(branch_name) is None:
            remote_branch_name = f"refs/remotes/origin/{branch_name}"
            try:
                target_oid = repo.lookup_reference(remote_branch_name).target
            except KeyError:
                raise ValueError(f"remote branch {branch_name} not found")
            repo.create_branch(branch_name, repo.get(target_oid))

    repo.free()

    return path


@pytest.fixture(scope="session")
def this_raw_repo(discovered_repository_path):
    """
    PyGit2 Repository object for this repo.
    """
    return pygit2.Repository(discovered_repository_path)


def _repo_clone(tmpdir_factory, path):
    clone_path = tmpdir_factory.mktemp("tutorials-")
    repo = pygit2.clone_repository(
        path,
        clone_path,
        checkout_branch="unit-tests-commits"
    )
    repo.config["user.name"] = "Random Coder"
    repo.config["user.email"] = "random.coder@example.com"
    return repo


@pytest.fixture(scope="session")
def cloned_repo(tmpdir_factory, discovered_repository_path):
    """
    This repo cloned into a tmpdir, checked out at the branch
    "unit-tests-commits", with changes made to the working copies of
    ``boing/tutorial.md`` and ``boing/summary.md``.  Tests using this
    fixture should not modify the repo, as the fixture is
    session-scoped.
    """
    repo = _repo_clone(tmpdir_factory, discovered_repository_path)
    clone_path = Path(repo.workdir)

    tutorial_path = clone_path / "boing/tutorial.md"

    with open(tutorial_path, "wt") as f_tutorial:
        f_tutorial.write("Working copy of tutorial\n"
                         "\n\n{{< commit import-pytch >}}\n"
                         "\n\n{{< commit add-Alien-skeleton >}}\n")

    summary_path = clone_path / "boing/summary.md"

    with open(summary_path, "wt") as f_summary:
        f_summary.write("# Working summary for Boing\n")

    metadata_path = clone_path / "boing/metadata.json"

    with open(metadata_path, "wt") as f_metadata:
        f_metadata.write('{"difficulty": "easy"}')

    return repo


@pytest.fixture(scope="function")
def clean_cloned_repo(tmpdir_factory, discovered_repository_path):
    """
    This repo cloned into a tmpdir, checked out at the branch
    "unit-tests-commits", ensuring the repo's user name and email
    address are configured.  Scoped to "function".
    """
    return _repo_clone(tmpdir_factory, discovered_repository_path)


@pytest.fixture(
    scope="session",
    params=list(TH.ProjectHistory.TutorialTextSource),
)
def project_history(cloned_repo, request):
    """
    A ProjectHistory constructed from a clone of this repo, using the
    "unit-tests-commits" branch.  Parametrised with the two choices
    for tutorial-text-source.
    """
    return TH.ProjectHistory(cloned_repo.workdir,
                             "unit-tests-commits",
                             request.param)


@pytest.fixture
def fresh_project_history(cloned_repo, request):
    """
    A ProjectHistory constructed from a clone of this repo, using the
    "unit-tests-commits" branch.  This fixture is function-scoped so
    a test using it gets a fresh ProjectHistory instance, ensuring all
    cached-properties are computed.
    """
    return TH.ProjectHistory(cloned_repo.workdir,
                             "unit-tests-commits")


@pytest.fixture(scope="session")
def tutorial_md_text(project_history):
    return project_history.tutorial_text
