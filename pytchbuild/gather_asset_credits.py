import pygit2
import click

from .tutorialcompiler.gather_tutorials import TutorialCollection


@click.command()
@click.option(
    "-o", "--output-file",
    type=click.File(mode="wt"),
    required=True,
    help="where to write the ReST giving asset credits",
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
def main(output_file, repository_path, index_source):
    index_source = getattr(TutorialCollection.IndexSource, index_source)
    tutorials = TutorialCollection.from_repo_path(repository_path, index_source)
    tutorials.write_asset_credits(output_file)
