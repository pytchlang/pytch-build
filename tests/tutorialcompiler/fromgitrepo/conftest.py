import pytest

import pygit2


@pytest.fixture(scope="session")
def this_raw_repo():
    return pygit2.Repository(".")
