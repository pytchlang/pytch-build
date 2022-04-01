import pytest

import pygit2
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH


@pytest.fixture(scope="session")
def discovered_repository_path():
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
    return pygit2.Repository(discovered_repository_path)


@pytest.fixture(scope="session")
def cloned_repo(tmpdir_factory, discovered_repository_path):
    clone_path = tmpdir_factory.mktemp("tutorials-")
    repo = pygit2.clone_repository(discovered_repository_path,
                                   clone_path,
                                   checkout_branch="unit-tests-commits")

    tutorial_path = clone_path / "boing/tutorial.md"

    with open(tutorial_path, "wt") as f_tutorial:
        f_tutorial.write("Working copy of tutorial\n"
                         "\n\n{{< commit import-pytch >}}\n"
                         "\n\n{{< commit add-Alien-skeleton >}}\n")

    summary_path = clone_path / "boing/summary.md"

    with open(summary_path, "wt") as f_summary:
        f_summary.write("# Working summary for Boing\n")

    return repo


@pytest.fixture(scope="function")
def clean_cloned_repo(tmpdir_factory, discovered_repository_path):
    clone_path = tmpdir_factory.mktemp("tutorials-")
    return pygit2.clone_repository(discovered_repository_path,
                                   clone_path,
                                   checkout_branch="unit-tests-commits")


@pytest.fixture(
    scope="session",
    params=list(TH.ProjectHistory.TutorialTextSource),
)
def project_history(cloned_repo, request):
    return TH.ProjectHistory(cloned_repo.workdir,
                             "unit-tests-commits",
                             request.param)


# To ensure we perform fresh computation of cached properties, and get
# expected warnings, allow a test to request a clean freshly-made instance
# of the history.
@pytest.fixture
def fresh_project_history(cloned_repo, request):
    return TH.ProjectHistory(cloned_repo.workdir,
                             "unit-tests-commits")


@pytest.fixture(scope="session")
def tutorial_md_text(project_history):
    return project_history.tutorial_text
