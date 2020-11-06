import pygit2
import click

from .tutorialcompiler.fromgitrepo import git_repository
from .tutorialcompiler.gather_tutorials import TutorialCollection, commit_to_releases


@click.command()
@click.option(
    "-o", "--output-file",
    type=click.File(mode="wb"),
    required=True,
    help=("where to write the zipfile containing the tutorial collection"),
)
@click.option(
    "-r", "--repository-path",
    default=pygit2.discover_repository("."),
    envvar="GIT_DIR",
    metavar="PATH",
    help="path to root of git repository",
)
@click.option(
    "--index-source",
    type=click.Choice([x.name for x in TutorialCollection.IndexSource],
                      case_sensitive=False),
    default=TutorialCollection.IndexSource.WORKING_DIRECTORY.name,
    help='what source to use for the "index.yaml" file of tutorials',
)
@click.option(
    "--make-release/--no-make-release",
    default=False,
    help="make a commit to the 'releases' branch",
)
def main(output_file, repository_path, index_source, make_release):
    # Convert string to enumerator:
    index_source = getattr(TutorialCollection.IndexSource, index_source)

    tutorials = TutorialCollection.from_repo_path(repository_path, index_source)

    releases_commit_oid = None

    if make_release:
        with git_repository(repository_path) as repo:
            releases_commit_oid = commit_to_releases(repo, tutorials)

    tutorials.write_new_zipfile(releases_commit_oid, output_file)
