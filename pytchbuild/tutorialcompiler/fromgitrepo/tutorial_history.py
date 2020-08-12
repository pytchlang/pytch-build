"""Representation of a tutorial within a Git repo

The files making up the tutorial should all live within a top-level directory
named for the tutorial.  Using "bunner" as an example tutorial name, the
structure should be::

   bunner/
      tutorial.md
      code.py
      project-assets/
         images/
            rabbit.png
            car.png
            ...etc...
         sounds/
            squish.mp3
            ...etc...

Internally, the relevant piece of Git history is represented by a
:py:class:`ProjectHistory` instance.  The commits within that history are
represented by :py:class:`ProjectCommit` instances, which should be of one of a
handful of particular forms.  The project's assets (images or sounds) are
represented by :py:class:`ProjectAsset` instances.
"""

import re
import pathlib
import pygit2
import itertools
import enum
from dataclasses import dataclass
from cached_property import cached_property


################################################################################

PROJECT_ASSET_DIRNAME = "project-assets"
CODE_FILE_BASENAME = "code.py"
TUTORIAL_TEXT_FILE_BASENAME = "tutorial.md"


################################################################################

@dataclass
class ProjectAsset:
    """An asset (graphics or sound) used in the tutorial's project
    """

    path: str
    data: bytes

    def __str__(self):
        return ('<ProjectAsset "{}": {} bytes>'
                .format(self.path, len(self.data)))

    @classmethod
    def from_delta(cls, repo, delta):
        """Construct a :py:class:`ProjectAsset` from a Git delta
        """
        if delta.status != pygit2.GIT_DELTA_ADDED:
            raise ValueError("delta is not of type ADDED")

        return cls(delta.new_file.path, repo[delta.new_file.id].data)


################################################################################

class ProjectCommit:
    """An individual commit within a tutorial's history

    Constructed from a ``pygit2.Repository`` and an ``oid``, which can be an
    SHA1 string.

    Should be one of the following types:

    Unique base commit
       The 'initial empty state' commit of the project.

    Update to project's Python code
       Modifies the project's ``code.py`` file.  Such a commit should have a
       *tag*, i.e., its commit subject should start with a string like
       ``{#check-for-winning}``.

    Update to tutorial text
       Modifies the tutorial text, held in the ``tutorial.md`` file.

    Addition of project asset or assets
       Adds one or more files within the ``project-assets`` directory.
    """

    def __init__(self, repo, oid):
        self.repo = repo
        self.commit = repo[oid]
        self.oid = self.commit.id

    def __str__(self):
        return f"<ProjectCommit: {self.short_oid} {self.summary_label}>"

    @cached_property
    def short_oid(self):
        return self.oid.hex[:12]

    @cached_property
    def summary_label(self):
        if self.has_identifier_slug:
            return f"#{self.identifier_slug}"
        if self.modifies_python_code:
            return "untagged-Python-change"
        if self.is_base:
            return "BASE"
        if self.adds_project_assets:
            asset_paths = ", ".join(f'"{a.path}"' for a in self.added_assets)
            return f"assets({asset_paths})"
        if self.modifies_tutorial_text:
            return "tutorial-text"
        return "?? unknown ??"

    @cached_property
    def tree(self):
        return self.commit.tree

    def text_file_contents(self, path):
        text_blob = self.tree / path
        return text_blob.data.decode("utf-8")

    @cached_property
    def message_subject(self):
        return self.commit.message.split('\n')[0]

    @cached_property
    def maybe_identifier_slug(self):
        m = re.match(r'\{\#([^ ]+)\}', self.message_subject)
        return m and m.group(1)

    @cached_property
    def has_identifier_slug(self):
        return self.maybe_identifier_slug is not None

    @cached_property
    def identifier_slug(self):
        if not self.has_identifier_slug:
            raise ValueError(f"commit {self.oid} has no identifier-slug")
        return self.maybe_identifier_slug

    @cached_property
    def is_base(self):
        return bool(re.match(r'\{base\}', self.message_subject))

    def modifies_single_file(self, target_basename):
        try:
            delta = self.sole_modify_against_parent
        except ValueError:
            return False

        path_of_modified_file = pathlib.Path(delta.old_file.path)
        return path_of_modified_file.name == target_basename

    @cached_property
    def diff_against_parent_or_empty(self):
        # If there is at least one parent, use the first one's tree as the
        # "tree" argument to pygit2.Tree.diff_to_tree().  If there is no parent,
        # we must be a root commit, in which case we want to compute the diff
        # against an empty tree, which is diff_to_tree()'s behaviour if no
        # "tree" arg given.
        parent_ids = self.commit.parent_ids
        diff_args = (
            (self.repo[parent_ids[0]].tree,)
            if parent_ids
            else ()
        )
        return self.commit.tree.diff_to_tree(*diff_args, swap=True)

    @cached_property
    def modifies_tutorial_text(self):
        return self.modifies_single_file(TUTORIAL_TEXT_FILE_BASENAME)

    @cached_property
    def modifies_python_code(self):
        return self.modifies_single_file(CODE_FILE_BASENAME)

    @staticmethod
    def path_is_a_project_asset(path_str):
        return pathlib.Path(path_str).parts[1] == PROJECT_ASSET_DIRNAME

    @cached_property
    def adds_project_assets(self):
        # Special-case the BASE commit, which can add a whole lot of files in
        # various places in the tree.  Treat it as not adding assets.
        #
        # TODO: Revisit this.  Maybe provide a helper script which sets up the
        # first commit or two in a canonical way?
        #
        if self.is_base:
            return False

        deltas_adding_assets = []
        other_deltas = []

        for delta in self.diff_against_parent_or_empty.deltas:
            if (delta.status == pygit2.GIT_DELTA_ADDED
                    and self.path_is_a_project_asset(delta.new_file.path)):
                deltas_adding_assets.append(delta)
            else:
                other_deltas.append(delta)

        if deltas_adding_assets and other_deltas:
            raise ValueError(f"commit {self.oid} adds project assets but also"
                             f" has other deltas")

        return bool(deltas_adding_assets)

    @cached_property
    def sole_modify_against_parent(self):
        diff = self.diff_against_parent_or_empty
        if len(diff) != 1:
            raise ValueError(f"commit {self.oid} does not have exactly one delta")
        delta = list(diff.deltas)[0]
        if delta.status != pygit2.GIT_DELTA_MODIFIED:
            raise ValueError(f"commit {self.oid}'s delta is not of type MODIFIED")
        return delta

    @cached_property
    def added_assets(self):
        if self.adds_project_assets:
            return [ProjectAsset.from_delta(self.repo, delta)
                    for delta in self.diff_against_parent_or_empty.deltas]
        else:
            return []

    @cached_property
    def code_patch_against_parent(self):
        if not self.modifies_python_code:
            raise ValueError(f"commit {self.oid} does not modify the Python code")

        delta = self.sole_modify_against_parent
        old_blob = self.repo[delta.old_file.id]
        new_blob = self.repo[delta.new_file.id]
        return old_blob.diff(new_blob)


################################################################################

class ProjectHistory:
    """Development history of a Pytch project within a tutorial context
    """

    class TutorialTextSource(enum.Enum):
        TIP_REVISION = enum.auto()
        WORKING_DIRECTORY = enum.auto()

    def __init__(
            self,
            repo_directory,
            tip_revision,
            tutorial_text_source=TutorialTextSource.TIP_REVISION,
    ):
        self.repo = pygit2.Repository(repo_directory)
        self.tutorial_text_source = tutorial_text_source
        tip_oid = self.repo.revparse_single(tip_revision).oid
        self.project_commits = self.commit_linear_ancestors(tip_oid)

    def commit_linear_ancestors(self, tip_oid):
        project_commits = [ProjectCommit(self.repo, tip_oid)]
        while not project_commits[-1].is_base:
            # TODO: Handle merges (more than one parent).
            oid = project_commits[-1].commit.parent_ids[0]
            project_commits.append(ProjectCommit(self.repo, oid))
        return project_commits

    @cached_property
    def all_project_assets(self):
        """List of all assets added during the history of the project
        """
        commits_assets = (c.added_assets for c in self.project_commits)
        return list(itertools.chain.from_iterable(commits_assets))

    @cached_property
    def top_level_directory_name(self):
        """The sole directory at top level of the repo

        In the example, ``bunner``.
        """
        # 'project_commits' has the tip as the first element:
        final_tree = self.project_commits[0].tree

        entries = list(final_tree)
        n_entries = len(entries)
        if n_entries != 1:
            raise ValueError(
                f"top-level tree has {n_entries} entries (expecting just one)"
            )
        only_entry = entries[0]

        return only_entry.name

    @cached_property
    def workdir_path(self):
        return pathlib.Path(self.repo.workdir)

    @cached_property
    def python_code_path(self):
        dirname = self.top_level_directory_name
        return f"{dirname}/{CODE_FILE_BASENAME}"

    @cached_property
    def tutorial_text_path(self):
        dirname = self.top_level_directory_name
        return f"{dirname}/{TUTORIAL_TEXT_FILE_BASENAME}"

    @cached_property
    def tutorial_text(self):
        """The final tutorial text, depending on ``tutorial_text_source``

        The value depends on the ``tutorial_text_source`` value this
        :py:class:`ProjectHistory` was constructed with:

        If ``TIP_REVISION``, the value is the contents of the ``tutorial.md``
        file as of the tip commit.

        If ``WORKING_DIRECTORY``, the value is the contents of the file in the
        working directory of the repository.  If there are uncommitted changes,
        this will differ from the ``TIP_REVISION`` value.

        In the example, the contents of the file ``bunner/tutorial.md``, either
        as of the tip commit from which the :py:class:`ProjectHistory` was
        constructed, or as currently in the repo's working directory.
        """
        if self.tutorial_text_source == self.TutorialTextSource.TIP_REVISION:
            tip_commit = self.project_commits[0]
            return tip_commit.text_file_contents(self.tutorial_text_path)
        elif self.tutorial_text_source == self.TutorialTextSource.WORKING_DIRECTORY:
            full_path = self.workdir_path / self.tutorial_text_path
            with full_path.open("rt") as f_in:
                return f_in.read()
        else:
            raise ValueError("unknown tutorial_text_source")

    @cached_property
    def initial_code_text(self):
        """The initial Python code

        In the example, the contents of the file ``bunner/code.py`` as of the
        special *base* commit in the ancestry of the tip commit from which the
        :py:class:`ProjectHistory` was constructed.
        """
        base_commit = self.project_commits[-1]
        return base_commit.text_file_contents(self.python_code_path)

    @cached_property
    def final_code_text(self):
        """The final Python code

        In the example, the contents of the file ``bunner/code.py`` as of the
        tip commit from which the :py:class:`ProjectHistory` was constructed.
        """
        tip_commit = self.project_commits[0]
        return tip_commit.text_file_contents(self.python_code_path)

    @cached_property
    def commit_from_slug(self):
        return {
            pc.identifier_slug: pc
            for pc in self.project_commits
            if pc.has_identifier_slug
        }

    def code_text_from_slug(self, slug):
        """The contents of ``code.py`` as of the commit tagged with the given *slug*
        """
        commit = self.commit_from_slug[slug]
        return commit.text_file_contents(self.python_code_path)

    def code_patch_against_parent(self, slug):
        commit = self.commit_from_slug[slug]
        return commit.code_patch_against_parent
