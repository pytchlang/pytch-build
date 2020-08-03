import re
import pathlib
import pygit2
from dataclasses import dataclass
from cached_property import cached_property


################################################################################

PROJECT_ASSET_DIRNAME = "project-assets"
CODE_FILE_BASENAME = "code.py"
TUTORIAL_TEXT_FILE_BASENAME = "tutorial.md"


################################################################################

@dataclass
class ProjectAsset:
    path: str
    data: bytes

    def __str__(self):
        return ('<ProjectAsset "{}": {} bytes>'
                .format(self.path, len(self.data)))

    @classmethod
    def from_delta(cls, repo, delta):
        if delta.status != pygit2.GIT_DELTA_ADDED:
            raise ValueError("delta is not of type ADDED")

        return cls(delta.new_file.path, repo[delta.new_file.id].data)


################################################################################

class ProjectCommit:
    def __init__(self, repo, oid):
        self.repo = repo
        self.commit = repo[oid]
        self.oid = self.commit.id

    @cached_property
    def short_oid(self):
        return self.oid.hex[:12]

    @cached_property
    def tree(self):
        return self.commit.tree

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
        try:
            delta = self.sole_modify_against_parent
        except ValueError:
            return False

        path_of_modified_file = pathlib.Path(delta.old_file.path)
        return path_of_modified_file.name == TUTORIAL_TEXT_FILE_BASENAME

    @cached_property
    def modifies_python_code(self):
        try:
            delta = self.sole_modify_against_parent
        except ValueError:
            return False

        path_of_modified_file = pathlib.Path(delta.old_file.path)
        return path_of_modified_file.name == CODE_FILE_BASENAME

    @staticmethod
    def path_is_a_project_asset(path_str):
        return pathlib.Path(path_str).parts[1] == PROJECT_ASSET_DIRNAME

    @cached_property
    def adds_project_assets(self):
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
