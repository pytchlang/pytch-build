import pygit2
import click
import pathlib

from .tutorialcompiler.gather_tutorials import TutorialCollection


existing_writable_directory = click.Path(
    exists=True,
    file_okay=False,
    dir_okay=True,
    writable=True,
    path_type=pathlib.Path
)


@click.command()
@click.option(
    "-o", "--output-directory",
    type=existing_writable_directory,
    required=True,
    help="where to write the documentation fragment giving asset credits",
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
    default="WORKING_DIRECTORY",
    help='what source to use for the "index.yaml" file of tutorials',
)
def main(output_directory, repository_path, index_source):
    index_source = getattr(TutorialCollection.IndexSource, index_source)
    tutorials = TutorialCollection.from_repo_path(repository_path, index_source)
    tutorials.write_asset_media(output_directory)
