import re
import pygit2
from dataclasses import dataclass
from cached_property import cached_property


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
