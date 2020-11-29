from dataclasses import dataclass
from typing import Dict
import yaml
import bs4
from pathlib import Path
import enum
import zipfile
import copy
import pygit2
import time
from contextlib import closing

from .fromgitrepo import git_repository
from .fromgitrepo.tutorial_history import ProjectHistory
from .fromgitrepo.tutorial_bundle import TutorialBundle
from .fromgitrepo.errors import InternalError, TutorialStructureError


RELEASES_BRANCH_NAME = "releases"
RELEASE_RECIPES_BRANCH_NAME = "release-recipes"


def yaml_load(yaml_content):
    return yaml.load(yaml_content, yaml.Loader)


@dataclass
class TutorialSummary:
    name: str  # Currently just for human readers
    div: bs4.element.Tag


@dataclass
class TutorialInfo:
    name: str
    branch_name: str
    project_history: ProjectHistory

    @property
    def summary_dict(self):
        history = self.project_history
        return {
            "name": self.name,
            "branch_name": self.branch_name,
            "dir_name": history.top_level_directory_name,
            "commit_id": history.tip_oid_string,
        }


@dataclass
class TutorialCollection:
    tutorials: Dict[str, TutorialInfo]

    class IndexSource(enum.Enum):
        RECIPES_TIP = enum.auto()
        WORKING_DIRECTORY = enum.auto()

    @staticmethod
    def index_yaml_content(repo, source):
        Source = TutorialCollection.IndexSource
        if source == Source.WORKING_DIRECTORY:
            index_path = Path(repo.workdir) / "index.yaml"
            with index_path.open("rt") as yaml_file:
                return yaml_file.read()
        elif source == Source.RECIPES_TIP:
            return index_data_at_recipes_tip(repo).decode("utf-8")
        else:
            raise InternalError("unknown source")

    @classmethod
    def from_repo_path(cls, repo_path, index_source):
        with git_repository(repo_path) as repo:
            content = cls.index_yaml_content(repo, index_source)
            tutorial_dicts = yaml_load(content)

        tutorials = {d["name"]: TutorialInfo(d["name"],
                                             d["tip-commit"],
                                             ProjectHistory(repo_path,
                                                            d["tip-commit"]))
                     for d in tutorial_dicts}
        return cls(tutorials)

    @classmethod
    def from_releases_commit(cls, repo_path, revision):
        missing_files = []
        with git_repository(repo_path) as repo:
            try:
                index_wrt_branches = yaml_load(
                    file_contents_at_revision(repo, revision, "index.yaml")
                )
            except KeyError:
                missing_files.append("index.yaml")

            try:
                build_info = yaml_load(
                    file_contents_at_revision(repo, revision, "build-sources.yaml")
                )
            except KeyError:
                missing_files.append("build-sources.yaml")

        if missing_files:
            raise RuntimeError(f'could not find {missing_files} in "{revision}"')

        # TODO: Compute tutorials

        return cls(tutorials)

    def write_to_zipfile(self, maybe_collection_oid, zfile):
        bundles = [TutorialBundle.from_project_history(info.project_history)
                   for info in self.tutorials.values()]

        for bundle in bundles:
            bundle.write_to_zipfile(zfile)

        index_soup = bs4.BeautifulSoup('<div class="tutorial-index"></div>',
                                       "html.parser")
        index_div = index_soup.find("div")

        if maybe_collection_oid is not None:
            index_div.attrs["data-collection-sha1"] = str(maybe_collection_oid)

        for bundle in bundles:
            summary_div = copy.deepcopy(bundle.summary_html)
            summary_div["data-tutorial-name"] = bundle.top_level_directory_name
            index_div.append(summary_div)

        zfile.writestr("tutorial-index.html", index_soup.encode("utf-8"))

    def write_new_zipfile(self, maybe_collection_oid, out_file):
        bare_zfile = zipfile.ZipFile(out_file,
                                     mode="w",
                                     compression=zipfile.ZIP_DEFLATED)

        with closing(bare_zfile) as zfile:
            self.write_to_zipfile(maybe_collection_oid, zfile)

    @property
    def gathered_tip_oids(self):
        return [info.project_history.tip_oid_string
                for info in self.tutorials.values()]

    @property
    def build_sources_dicts(self):
        return [info.summary_dict for info in self.tutorials.values()]


def create_signature(repo):
    return pygit2.Signature(repo.config['user.name'],
                            repo.config['user.email'],
                            time=int(time.time()))


def sole_tree_entry(commit):
    entries = list(commit.tree)
    if len(entries) != 1:
        raise TutorialStructureError(
            f"expecting just one entry in tree for {commit.oid}"
        )
    return entries[0]


def verify_entry_type(idx, entry):
    """Verify type of entry is as expected given its index

    Special-purpose for the list of contributing commits used to create a
    release.  The first one is the recipe branch, which should have just the
    "index.yaml" file.  The rest should be tutorial branches, which should have
    just one top-level subdirectory for the tutorial code and data.
    """
    if idx == 0 and entry.filemode != pygit2.GIT_FILEMODE_BLOB:
        raise TutorialStructureError(
            f"expecting tree-entry to be BLOB for {entry.id}"
        )
    if idx > 0 and entry.filemode != pygit2.GIT_FILEMODE_TREE:
        raise TutorialStructureError(
            f"expecting tree-entry to be TREE for {entry.id}"
        )


def file_contents_at_revision(repo, revision, file_path):
    commit = repo.revparse_single(revision)
    return commit.tree[file_path].data


def index_data_at_recipes_tip(repo):
    return file_contents_at_revision(repo, RELEASE_RECIPES_BRANCH_NAME, "index.yaml")


def verify_index_yaml_clean(repo):
    working_path = Path(repo.workdir) / "index.yaml"

    if not working_path.exists():
        # If we have got this far, we must be working from the "recipes tip"
        # version of the index file, in which case it's OK for it to not exist
        # in the working directory.
        return

    working_data = working_path.open("rb").read()
    recipes_tip_data = index_data_at_recipes_tip(repo)

    if not working_data == recipes_tip_data:
        raise TutorialStructureError(
            'file "index.yaml" in working directory'
            ' does not match version at tip of branch'
            f' "{RELEASE_RECIPES_BRANCH_NAME}"'
        )


def create_union_tree(repo, commit_oid_strs, extra_files):
    """Create and write the union of the trees of the given commits as a new tree

    The ``extra_files`` dictionary gives additional top-level files which should
    be included in the tree.  The keys should be strings (containing no
    path-separator characters), and the values should be ``bytes`` objects.

    Return the OID of the resulting new tree.
    """
    tree_builder = repo.TreeBuilder()
    names_already_added = set()
    for idx, oid in enumerate(commit_oid_strs):
        entry = sole_tree_entry(repo[oid])
        verify_entry_type(idx, entry)
        if entry.name in names_already_added:
            raise TutorialStructureError(f'duplicate name "{entry.name}"')
        tree_builder.insert(entry.name, entry.id, entry.filemode)
        names_already_added.add(entry.name)

    for filename, filebytes in extra_files.items():
        # TODO: Check for no "/" chars in filename.
        if filename in names_already_added:
            raise TutorialStructureError(
                f'duplicate name "{entry.name}" from extra_files'
            )
        blob_id = repo.create_blob(filebytes)
        tree_builder.insert(filename, blob_id, pygit2.GIT_FILEMODE_BLOB)
        names_already_added.add(filename)

    return tree_builder.write()


def commit_to_releases(repo, tutorials):
    """First commit_oid_strs should have just 'index.yaml' in its tree.

    Others are tutorial tips, which should each have just one
    top-level tree entry, which should be a directory

    Can undo a release like this by doing

        git branch -f releases 'releases^'

    but this is a history-altering change so don't do this if you've
    already pushed.
    """
    verify_index_yaml_clean(repo)

    sig = create_signature(repo)

    build_sources = tutorials.build_sources_dicts
    build_sources_yaml = yaml.dump(build_sources, sort_keys=False).encode()

    extra_files = {
        "build-sources.yaml": build_sources_yaml,
    }

    release_recipes_tip = str(repo.revparse_single(RELEASE_RECIPES_BRANCH_NAME).oid)
    contributing_commit_oids = [release_recipes_tip] + tutorials.gathered_tip_oids
    tree_oid = create_union_tree(repo, contributing_commit_oids, extra_files)

    releases_tip = str(repo.revparse_single(RELEASES_BRANCH_NAME).oid)
    parent_oids = [releases_tip] + contributing_commit_oids

    new_oid = repo.create_commit(f"refs/heads/{RELEASES_BRANCH_NAME}",
                                 sig, sig,
                                 "Release new versions of tutorials\n",
                                 tree_oid,
                                 parent_oids)
    return new_oid
