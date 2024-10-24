import pygit2
import click
import yaml
import sys
from pathlib import Path

from .tutorialcompiler.gather_tutorials import TutorialCollection


def commit_lut_from_branch_records(branch_records):
    return dict(
        (branch["branch_name"], branch["commit_id"])
        for branch in branch_records
    )


@click.command()
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
def main(repository_path, index_source):
    repo_root = Path(pygit2.Repository(repository_path).workdir)
    with (repo_root / "build-sources.yaml").open() as f_in:
        build_sources_data = yaml.load(f_in, yaml.Loader)
        build_sources_lut = commit_lut_from_branch_records(
            build_sources_data
        )

    tutorials = TutorialCollection.from_repo_path(
        repository_path,
        getattr(TutorialCollection.IndexSource, index_source)
    )
    index_data = tutorials.build_sources_dicts
    index_lut = commit_lut_from_branch_records(index_data)

    branch_names = set(build_sources_lut.keys()) | set(index_lut.keys())
    max_name_length = max(len(name) for name in branch_names)
    error_notes = []

    for branch_name in sorted(branch_names):
        in_build_sources = branch_name in build_sources_lut
        in_index = branch_name in index_lut

        note_prefix = f"{branch_name:<{max_name_length}}  "
        if in_build_sources and not in_index:
            error_notes.append(
                f"{note_prefix}in BUILD-SOURCES but not in INDEX"
            )
        elif in_index and not in_build_sources:
            error_notes.append(
                f"{note_prefix}in INDEX but not in BUILD-SOURCES"
            )
        else:
            build_sources_oid = build_sources_lut[branch_name]
            index_oid = index_lut[branch_name]
            if build_sources_oid != index_oid:
                error_notes.append(
                    f"{note_prefix}"
                    f"commits: BUILD-SOURCES {build_sources_oid}"
                    f"; INDEX {index_oid}"
                )

    if error_notes:
        print(
            "Tutorial branch heads are not consistent between"
            " build-sources.yaml file and index.yaml file:",
            file=sys.stderr
        )
    for error_note in error_notes:
        print(f"    {error_note}", file=sys.stderr)

    sys.exit(1 if error_notes else 0)
