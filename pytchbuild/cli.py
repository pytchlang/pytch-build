"""Console script for pytchbuild
"""

import sys
import click
import colorlog

import pygit2

from .tutorialcompiler.fromgitrepo import (
    compile as compile_fromgitrepo,
    compile_html_only as compile_html_only_fromgitrepo,
)
from .tutorialcompiler.fromgitrepo.tutorial_history import ProjectHistory
from .tutorialcompiler.fromgitrepo.errors import TutorialStructureError


log_handler = colorlog.StreamHandler()
log_handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s : %(message)s"))

logger = colorlog.getLogger()  # Root logger
logger.addHandler(log_handler)


@click.command()
@click.option(
    "-o", "--output-file",
    type=click.File(mode="wb"),
    required=True,
    help=("where to write the zipfile containing the tutorial content"
          " (or, under \"--html-only\", the HTML fragment)"),
)
@click.option(
    "-r", "--repository-path",
    default=pygit2.discover_repository("."),
    envvar="GIT_DIR",
    metavar="PATH",
    help="path to root of git repository",
)
@click.option(
    "-b", "--tip-revision",
    default="HEAD",
    metavar="REVISION",
    help="revision (e.g., branch name) at tip of tutorial",
)
@click.option(
    "-t", "--tutorial-text-source",
    type=click.Choice([x.name for x in ProjectHistory.TutorialTextSource],
                      case_sensitive=False),
    default=ProjectHistory.TutorialTextSource.TIP_REVISION.name,
    help="what source to use for the tutorial text",
)
@click.option(
    "-f", "--output-format",
    type=click.Choice(["bundle-zipfile", "html-only"]),
    default="bundle-zipfile",
    help="what to write: the full bundle zipfile, or just the HTML fragment",
)
def main(output_file, repository_path, tip_revision, tutorial_text_source, output_format):
    if repository_path is None:
        raise click.UsageError(
            "\nUnable to discover repository.  Please specify one\n"
            "either with the -r/--repository-path option or via\n"
            "the GIT_DIR environment variable.")

    # Convert string to enumerator:
    tutorial_text_source = getattr(ProjectHistory.TutorialTextSource,
                                   tutorial_text_source)

    try:
        if output_format == "bundle-zipfile":
            compile_fun = compile_fromgitrepo
        elif output_format == "html-only":
            compile_fun = compile_html_only_fromgitrepo
        else:
            # (Shouldn't happen, because Click should enforce valid choice.)
            raise click.UsageError(f"unknown output_format \"{output_format}\"")

        compile_fun(output_file,
                    repository_path,
                    tip_revision,
                    tutorial_text_source)
    except TutorialStructureError as err:
        colorlog.error(str(err))
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
