import pygit2
from pathlib import Path

from .tutorialcompiler.fromgitrepo.config import (
    RELEASE_RECIPES_BRANCH_NAME,
    NEW_BRANCH_STARTING_COMMIT,
)

from .tutorialcompiler.fromgitrepo.repo_functions import (
    ensure_status_clean,
    create_signature,
    commit_files,
)


def create_new_tutorial_branch_and_structure(
    repo, tutorial_name, branch_name, tutorial_slug
):
    """
    Create the directory structure as well as the branch itself
    """
    ensure_status_clean(repo)

    branch_start_commit = repo.revparse_single(NEW_BRANCH_STARTING_COMMIT)
    repo.create_branch(branch_name, branch_start_commit)
    repo.checkout(f"refs/heads/{branch_name}")
    new_directory = Path(repo.workdir) / tutorial_slug
    new_directory.mkdir()
    (new_directory / "project-assets").mkdir()
    (new_directory / "tutorial-assets").mkdir()

    # TODO: Worth moving to, e.g., Jinja for these?

    with (new_directory / "tutorial.md").open("wt") as f_out:
        f_out.write(f"# {tutorial_name}\n\nTODO: Write tutorial\n")

    with (new_directory / "summary.md").open("wt") as f_out:
        f_out.write(f"# {tutorial_name}\n\nTODO: Write summary\n")

    sig = create_signature(repo)

    commit_files(
        repo,
        [f"{tutorial_slug}/tutorial.md", f"{tutorial_slug}/summary.md"],
        sig,
        "Add tutorial and summary placeholders",
    )

    with (new_directory / "code.py").open("wt") as f_out:
        f_out.write("import pytch\n")

    commit_files(
        repo,
        [f"{tutorial_slug}/code.py"],
        sig,
        "{base} Add starting point of code",
    )


def add_new_tutorial_to_index_yaml(repo, name, branch):
    ensure_status_clean(repo)

    repo.checkout(f"refs/heads/{RELEASE_RECIPES_BRANCH_NAME}")
    index_yaml_path = Path(repo.workdir) / "index.yaml"

    if not index_yaml_path.is_file():
        raise RuntimeError("file index.yaml not found")

    with index_yaml_path.open("at") as f_out:
        f_out.write(f"- name: {name}\n  tip-commit: {branch}\n")

    sig = create_signature(repo)

    commit_files(repo, ["index.yaml"], sig, f'Add tutorial "{name}"')
