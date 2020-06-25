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
    def __init__(self, repo_directory, tip_revision):
        self.repo = pygit2.Repository(repo_directory)
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
    def top_level_directory_name(self):
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
    def python_code_path(self):
        dirname = self.top_level_directory_name
        return f"{dirname}/{CODE_FILE_BASENAME}"
