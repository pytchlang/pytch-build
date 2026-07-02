import pygit2
import click
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

    with (new_directory / "metadata.json").open("wt") as f_out:
        f_out.write('{"difficulty": "medium"}\n')

    with (new_directory / "credits.md").open("wt") as f_out:
        # No real credit bullets yet: a bullet naming an asset which does
        # not exist would fail the build's credits validation.  The example
        # is inside a fenced code block, which the parser ignores.
        f_out.write(
            f"# Credits for {tutorial_name}\n"
            "\n"
            "Credit every asset (image or sound) used by this tutorial,\n"
            "whether it lives under `project-assets/` or `tutorial-assets/`.\n"
            "Each asset is credited by a bullet-list item whose first content\n"
            "is the asset's backtick-quoted basename; a single bullet may name\n"
            "several assets which share one credit.  For example:\n"
            "\n"
            "```\n"
            "- `alien.png` — Drawn by A. Author, licensed CC-BY 4.0.\n"
            "- `beep.mp3`, `boop.mp3` — Made by us; public domain.\n"
            "```\n"
            "\n"
            "TODO: Add a credit bullet for each asset used by this tutorial.\n"
        )

    sig = create_signature(repo)

    commit_files(
        repo,
        [
            f"{tutorial_slug}/tutorial.md",
            f"{tutorial_slug}/summary.md",
            f"{tutorial_slug}/metadata.json",
        ],
        sig,
        "Add tutorial, summary, metadata placeholders",
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


@click.command()
@click.option(
    "--tutorial-name",
    required=True,
    help="human-readable short name of tutorial"
)
@click.option(
    "--tutorial-branch",
    required=True,
    help="name of branch to create"
)
@click.option(
    "--tutorial-slug",
    required=True,
    help="name of directory (folder) to create"
)
@click.option(
    "--repository-path",
    default=pygit2.discover_repository("."),
    envvar="GIT_DIR",
    metavar="PATH",
    help="path to root of git repository",
)
def main(repository_path, tutorial_name, tutorial_branch, tutorial_slug):
    """
    Create the branch, directories, and files for a new tutorial

    Also create an entry in the index.yaml file to include the new
    tutorial.
    """
    repo = pygit2.Repository(repository_path)

    add_new_tutorial_to_index_yaml(
        repo,
        tutorial_name,
        tutorial_branch,
    )

    create_new_tutorial_branch_and_structure(
        repo,
        tutorial_name,
        tutorial_branch,
        tutorial_slug
    )

    print(f"""
Assuming no errors were reported, files for the new tutorial are now
in the directory

    {tutorial_slug}/

and your repo is checked out on the branch

    {tutorial_branch}

to start work on this tutorial.

You can use an interactive-rebase to amend the {{base}} commit if the
default starting code is not appropriate for this tutorial.

The tutorial.md and summary.md files have been created and committed,
each containing a "TODO" marker.

The metadata.json file has been created; you should edit this to label
your tutorial with the appropriate difficulty level.

You should now be able to go to the top-level directory of the
pytch-releases checkout, and launch the development server with

    export PYTCH_IN_PROGRESS_TUTORIAL={tutorial_slug}
    ./pytch-build/makesite/local-server/dev-server.sh
""")
