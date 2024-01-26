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
      tutorial-assets/
         screenshot.png
         some-diagram.png

Internally, the relevant piece of Git history is represented by a
:py:class:`ProjectHistory` instance.  The commits within that history are
represented by :py:class:`ProjectCommit` instances, which should be of one of a
handful of particular forms.  The project's assets (images or sounds) are
represented by :py:class:`Asset` instances.  Likewise any assets required for
the tutorial itself, such as screenshots or diagrams.
"""

import re
import pathlib
import pygit2
from collections import Counter
import itertools
import enum
import colorlog
import json
from pathlib import Path
from dataclasses import dataclass
from .cached_property import cached_property
from .errors import InternalError, TutorialStructureError
from ..medialib import (
    MediaLibraryItem as MLItem,
    MediaLibraryEntry as MLEntry,
    MediaLibraryData,
)

logger = colorlog.getLogger(__name__)


################################################################################

PROJECT_ASSET_DIRNAME = "project-assets"
TUTORIAL_ASSET_DIRNAME = "tutorial-assets"
ASSET_SOURCE_DIRNAME = "asset-src"
CODE_FILE_BASENAME = "code.py"
TUTORIAL_TEXT_FILE_BASENAME = "tutorial.md"
SUMMARY_TEXT_FILE_BASENAME = "summary.md"
METADATA_FILE_BASENAME = "metadata.json"


################################################################################

@dataclass
class Asset:
    """An asset (graphics or sound) used in the tutorial's project
    """

    path: str
    data: bytes

    def __str__(self):
        return ('<Asset "{}": {} bytes>'
                .format(self.path, len(self.data)))

    @classmethod
    def from_delta(cls, repo, delta):
        """Construct a :py:class:`Asset` from a Git delta
        """
        if delta.status not in [
            pygit2.GIT_DELTA_ADDED,
            pygit2.GIT_DELTA_MODIFIED,
        ]:
            raise InternalError("delta is not of type ADDED or MODIFIED")

        return cls(delta.new_file.path, repo[delta.new_file.id].data)

    @cached_property
    def is_project_asset(self):
        return Path(self.path).parts[1] == 'project-assets'

    @cached_property
    def path_suffix(self):
        return Path(self.path).suffix

    @cached_property
    def project_asset_local_path(self):
        if not self.is_project_asset:
            return None

        # The parts are, e.g.,
        #
        #     ["bunner", "project-assets", "images", "splash-3.png"]
        #     ["ticket-vending-machine", "project-assets", "coin-1.png"]
        #
        # and we want the part past the tutorial slug part and the
        # "project-assets" part.
        #
        return "/".join(Path(self.path).parts[2:])


################################################################################

@dataclass
class AssetsCreditsEntry:
    """A credit which applies to some of the assets in a tutorial
    """

    asset_basenames: [str]
    asset_usage: str
    credit_markdown: str


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
        if self.adds_project_assets or self.adds_tutorial_assets:
            asset_paths = ", ".join(f'"{a.path}"' for a in self.added_assets)
            return f"add-assets({asset_paths})"
        if self.modifies_project_assets:
            asset_paths = ", ".join(f'"{a.path}"' for a in self.modified_assets)
            return f"modify-assets({asset_paths})"
        if self.adds_asset_source:
            return "asset-source"
        if self.modifies_tutorial_text:
            return "tutorial-text"
        return "?? unknown ??"

    @cached_property
    def tree(self):
        return self.commit.tree

    def text_file_contents(self, path):
        try:
            text_blob = self.tree / path
        except KeyError:
            raise TutorialStructureError(
                f"file \"{path}\" not found in tree of {self.oid}"
            )
        else:
            return text_blob.data.decode("utf-8")

    @cached_property
    def message_subject(self):
        return self.commit.message.split('\n')[0]

    @cached_property
    def message_body(self):
        lines = self.commit.message.split('\n')
        if lines[1] != "":
            raise TutorialStructureError(
                f"commit {self.oid} has malformed commit message"
            )
        return "\n".join(lines[2:] + [""])

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
            raise InternalError(f"commit {self.oid} has no identifier-slug")
        return self.maybe_identifier_slug

    @cached_property
    def is_base(self):
        return bool(re.match(r'\{base\}', self.message_subject))

    def modifies_single_file(self, target_basename):
        try:
            delta = self.sole_modify_against_parent
        except TutorialStructureError:
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

    @staticmethod
    def path_is_a_tutorial_asset(path_str):
        return pathlib.Path(path_str).parts[1] == TUTORIAL_ASSET_DIRNAME

    @staticmethod
    def path_is_an_asset_source(path_str):
        return pathlib.Path(path_str).parts[1] == ASSET_SOURCE_DIRNAME

    def adds_assets(self, is_asset_fun, asset_kind_name):
        # Special-case the BASE commit, which can add a whole lot of files in
        # various places in the tree.  Treat it as not adding assets.
        #
        # TODO: Revisit this.  Maybe provide a helper script which sets up the
        # first commit or two in a canonical way?
        #
        if self.is_base:
            return False

        any_deltas_adding_assets = False
        any_other_deltas = False

        for delta in self.diff_against_parent_or_empty.deltas:
            if (delta.status == pygit2.GIT_DELTA_ADDED
                    and is_asset_fun(delta.new_file.path)):
                any_deltas_adding_assets = True
            else:
                any_other_deltas = True

        if any_deltas_adding_assets and any_other_deltas:
            raise TutorialStructureError(
                f"commit {self.oid} adds {asset_kind_name} assets"
                " but also has other deltas"
            )

        return any_deltas_adding_assets

    def modifies_assets(self, is_asset_fun, asset_kind_name):
        any_deltas_modifying_assets = False
        any_other_deltas = False

        for delta in self.diff_against_parent_or_empty.deltas:
            if (delta.status == pygit2.GIT_DELTA_MODIFIED
                    and is_asset_fun(delta.new_file.path)):
                any_deltas_modifying_assets = True
            else:
                any_other_deltas = True

        if any_deltas_modifying_assets and any_other_deltas:
            raise TutorialStructureError(
                f"commit {self.oid} modifies {asset_kind_name} assets"
                " but also has other deltas"
            )

        return any_deltas_modifying_assets

    @cached_property
    def adds_project_assets(self):
        return self.adds_assets(self.path_is_a_project_asset, "project")

    @cached_property
    def modifies_project_assets(self):
        return self.modifies_assets(self.path_is_a_project_asset, "project")

    @cached_property
    def adds_tutorial_assets(self):
        return self.adds_assets(self.path_is_a_tutorial_asset, "tutorial")

    @cached_property
    def adds_asset_source(self):
        return self.adds_assets(self.path_is_an_asset_source, "asset-source")

    @cached_property
    def sole_modify_against_parent(self):
        diff = self.diff_against_parent_or_empty
        if len(diff) != 1:
            raise TutorialStructureError(
                f"commit {self.oid} does not have exactly one delta"
            )
        delta = list(diff.deltas)[0]
        if delta.status != pygit2.GIT_DELTA_MODIFIED:
            raise TutorialStructureError(
                f"commit {self.oid}'s delta is not of type MODIFIED"
            )
        return delta

    @cached_property
    def added_assets(self):
        if self.adds_project_assets or self.adds_tutorial_assets:
            return [Asset.from_delta(self.repo, delta)
                    for delta in self.diff_against_parent_or_empty.deltas]
        else:
            return []

    @cached_property
    def modified_assets(self):
        if self.modifies_project_assets:
            return [Asset.from_delta(self.repo, delta)
                    for delta in self.diff_against_parent_or_empty.deltas]
        else:
            return []

    @cached_property
    def assets_credits(self):
        should_have_credits = (
            self.adds_project_assets
            or self.modifies_project_assets
            or self.adds_tutorial_assets
        )

        if should_have_credits:
            credit_markdown = self.message_body
            if re.match(r"^\s*$", credit_markdown):
                logger.warning(f"commit {self.oid} adds assets but has no"
                               " body containing Markdown for credits/licence")
                return []

            usage = ("the tutorial text/summary" if self.adds_tutorial_assets
                     else "the project")

            return [
                AssetsCreditsEntry(
                    [Path(asset.path).name for asset in self.added_assets],
                    usage,
                    credit_markdown
                )
            ]
        else:
            return []

    def assert_modifies_python_code(self):
        if not self.modifies_python_code:
            raise TutorialStructureError(
                f"commit {self.oid} does not modify the Python code"
            )

    @cached_property
    def code_patch_against_parent(self):
        self.assert_modifies_python_code()
        delta = self.sole_modify_against_parent
        old_blob = self.repo[delta.old_file.id]
        new_blob = self.repo[delta.new_file.id]
        return old_blob.diff(new_blob)


################################################################################

class MediaEntryProcessor:
    def __init__(self, name, paths):
        self.name = name
        # Initially, every element of self.items is a string, being
        # the path of an asset we expect to be provided in due course.
        # Each time accept_item() is called, one element of self.items
        # might get replaced with a MediaLibraryItem for that asset.
        # By the time all tutorial assets have been provided to us via
        # accept_item(), all elements of self.items should be
        # MediaLibraryItem instances.
        self.items = paths

    def accept_item(self, path, item):
        try:
            idx = self.items.index(path)
            self.items[idx] = item
            return True
        except ValueError:
            return False

    def assert_awaiting_nothing(self):
        missing_paths = [
            item for item in self.items
            if isinstance(item, str)
        ]
        if len(missing_paths) > 0:
            raise TutorialStructureError(
                f'media-entry "{self.name}":'
                f" paths {missing_paths} not found"
            )


class MediaEntriesProcessor:
    def __init__(self, entry_dicts):
        self.processors = [
            MediaEntryProcessor(entry["name"], entry["assets"])
            for entry in entry_dicts
        ]

    def accept_item(self, path, item):
        n_did_accept = 0
        for processor in self.processors:
            n_did_accept += int(processor.accept_item(path, item))

        if n_did_accept > 1:
            raise TutorialStructureError(
                f'asset "{path}":'
                f" part of {n_did_accept} entries"
            )

        return n_did_accept == 1

    def assert_awaiting_nothing(self):
        for processor in self.processors:
            processor.assert_awaiting_nothing()

    def as_entries(self, tags, id_iter):
        return [
            MLEntry(next(id_iter), processor.name, processor.items, tags)
            for processor in self.processors
        ]


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

        self.validate_structure()

    def validate_structure(self):
        self.validate_slug_uniqueness()

    def validate_slug_uniqueness(self):
        occurrences_of_slug = Counter(self.ordered_commit_slugs)
        repeated_slugs = [
            slug
            for slug, n_occurrences in occurrences_of_slug.items()
            if n_occurrences > 1
        ]
        if repeated_slugs:
            raise TutorialStructureError(
                f"duplicate commit-identifier slug/s {repeated_slugs}"
            )

    def commit_linear_ancestors(self, tip_oid):
        project_commits = [ProjectCommit(self.repo, tip_oid)]
        while not project_commits[-1].is_base:
            # TODO: Handle merges (more than one parent).
            parent_ids = project_commits[-1].commit.parent_ids
            if not parent_ids:
                raise TutorialStructureError(
                    f"did not find {{base}} commit in ancestors of {tip_oid}"
                )
            oid = parent_ids[0]
            project_commits.append(ProjectCommit(self.repo, oid))
        return project_commits

    @cached_property
    def tip_oid_string(self):
        return str(self.project_commits[0].oid)

    @cached_property
    def all_assets(self):
        """List of all assets added or updated during the history of the project

        If an asset is added and then modified, the most recent
        content of that asset is used.  Assets are given in no
        particular order.
        """
        asset_from_path = {}
        for commit in self.project_commits:
            for asset in itertools.chain(
                commit.added_assets,
                commit.modified_assets
            ):
                # We go through commits from newest to oldest, so
                # ignore any older modifies/adds of an asset we
                # already know about.
                if asset.path not in asset_from_path:
                    asset_from_path[asset.path] = asset
        return list(asset_from_path.values())

    def medialib_contribution(self, tag, id_iter):
        metadata = json.loads(self.metadata_text)

        entry_dicts = metadata.get("groupedProjectAssets", [])
        media_processor = MediaEntriesProcessor(entry_dicts)

        data_from_content_id = {}
        singleton_entries = []
        for asset in self.all_assets:
            if (local_path := asset.project_asset_local_path) is None:
                continue
            if asset.path_suffix not in [".jpg", ".png"]:
                continue
            item = MLItem.from_project_asset(asset)
            if not media_processor.accept_item(local_path, item):
                entry = MLEntry(next(id_iter), item.name, [item], [tag])
                singleton_entries.append(entry)
            data_from_content_id[item.relativeUrl] = asset.data

        media_processor.assert_awaiting_nothing()

        entries = (
            media_processor.as_entries([tag], id_iter)
            + singleton_entries
        )

        return MediaLibraryData(entries, data_from_content_id)

    @cached_property
    def all_project_assets(self):
        return [a for a in self.all_assets if a.is_project_asset]

    @cached_property
    def all_asset_credits(self):
        """List of all AssetsCreditsEntry objects
        """
        commits_credits = (c.assets_credits for c in self.project_commits)

        # Provide the credits entries such that the earliest one in the list
        # is for the earliest (nearest the root) commit in the history.
        all_credits = list(itertools.chain.from_iterable(commits_credits))
        return list(reversed(all_credits))

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
            raise TutorialStructureError(
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
    def summary_text_path(self):
        dirname = self.top_level_directory_name
        return f"{dirname}/{SUMMARY_TEXT_FILE_BASENAME}"

    @cached_property
    def metadata_text_path(self):
        dirname = self.top_level_directory_name
        return f"{dirname}/{METADATA_FILE_BASENAME}"

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
            raise InternalError("unknown tutorial_text_source")

    @cached_property
    def summary_text(self):
        if self.tutorial_text_source == self.TutorialTextSource.TIP_REVISION:
            tip_commit = self.project_commits[0]
            return tip_commit.text_file_contents(self.summary_text_path)
        elif self.tutorial_text_source == self.TutorialTextSource.WORKING_DIRECTORY:
            full_path = self.workdir_path / self.summary_text_path
            with full_path.open("rt") as f_in:
                return f_in.read()
        else:
            raise InternalError("unknown tutorial_text_source")

    @cached_property
    def metadata_text(self):
        if self.tutorial_text_source == self.TutorialTextSource.TIP_REVISION:
            tip_commit = self.project_commits[0]
            return tip_commit.text_file_contents(self.metadata_text_path)
        elif self.tutorial_text_source == self.TutorialTextSource.WORKING_DIRECTORY:
            full_path = self.workdir_path / self.metadata_text_path
            with full_path.open("rt") as f_in:
                return f_in.read()
        else:
            raise InternalError("unknown tutorial_text_source")

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

    @cached_property
    def ordered_commit_slugs(self):
        """All slugs, in order as if playing FORWARDS through history
        """
        # Our 'project_commits' list goes backwards from HEAD to the '{base}'
        # commit, so use reversed() to get forwards ordering.
        return [
            pc.identifier_slug
            for pc in reversed(self.project_commits)
            if pc.has_identifier_slug
        ]

    def slug_is_known(self, slug):
        """Return whether the given *slug* is a valid commit slug
        """
        return slug in self.commit_from_slug

    def code_text_from_slug(self, slug):
        """The contents of ``code.py`` as of the commit tagged with the given *slug*
        """
        commit = self.commit_from_slug[slug]
        return commit.text_file_contents(self.python_code_path)

    def code_patch_against_parent(self, slug):
        commit = self.commit_from_slug[slug]
        return commit.code_patch_against_parent
