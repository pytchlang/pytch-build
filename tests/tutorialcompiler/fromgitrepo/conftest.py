import pytest

import pygit2
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH


@pytest.fixture(scope="session")
def this_raw_repo():
    return pygit2.Repository(".")


@pytest.fixture(scope="session")
def project_history():
    return TH.ProjectHistory(".", "unit-tests-commits")
