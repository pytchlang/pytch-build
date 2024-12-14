import click
import pygit2
import json

from .tutorialcompiler.fromgitrepo.tutorial_history import ProjectHistory
from .tutorialcompiler.fromgitrepo.structured_diff import StructuredPytchDiff


class FlatMarkdownEmitter:
    @staticmethod
    def markdown_for_commit(commit):
        return f"""{{{{< commit {commit.identifier_slug} >}}}}\n\n"""


class PerMethodMarkdownEmitter:
    @staticmethod
    def markdown_for_commit(commit):
        slug = commit.identifier_slug
        codes = commit.old_and_new_code
        slug_label = f"{{#{slug}}}"
        diff = StructuredPytchDiff(slug_label, *codes)
        rich_commit_template = diff.detected_rich_commit_template()
        args_json = json.dumps(rich_commit_template.args)
        return f"""\
{{{{< learner-task >}}}}

{{{{< learner-task-help >}}}}

{{{{< jr-commit {slug} {rich_commit_template.kind} {args_json} >}}}}

{{{{< /learner-task >}}}}

"""


kEmitterFromKind = {
    "flat": FlatMarkdownEmitter,
    "per-method": PerMethodMarkdownEmitter,
}


@click.command()
@click.option(
    "--repository-path",
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
def main(repository_path, tip_revision):
    if repository_path is None:
        raise click.UsageError(
            "\nUnable to discover repository.  Please specify one\n"
            "either with the -r/--repository-path option or via\n"
            "the GIT_DIR environment variable.")

    project_history = ProjectHistory(repository_path, tip_revision)
    metadata = json.loads(project_history.metadata_text)
    program_kind = metadata.get("programKind", "flat")
    emitter_cls = kEmitterFromKind.get(program_kind)

    for slug in project_history.ordered_commit_slugs:
        commit = project_history.commit_from_slug[slug]
        print(emitter_cls.markdown_for_commit(commit))
