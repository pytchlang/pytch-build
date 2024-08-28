from dataclasses import dataclass
from typing import Dict
import yaml
import bs4
from pathlib import Path
import enum
import zipfile
import copy
import pygit2
import itertools
import re
import subprocess
import shutil
from contextlib import closing

from .medialib import MediaLibraryData

from .fromgitrepo import git_repository
from .fromgitrepo.tutorial_history import ProjectHistory
from .fromgitrepo.tutorial_bundle import TutorialBundle
from .fromgitrepo.errors import InternalError, TutorialStructureError
from .fromgitrepo.config import (
    RELEASES_BRANCH_NAME,
    RELEASE_RECIPES_BRANCH_NAME,
)
from .fromgitrepo.repo_functions import (
    create_signature,
    file_contents_at_revision,
)


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

        revision_from_branch_name = {
            d["branch_name"]: d["commit_id"] for d in build_info
        }

        for descriptor in index_wrt_branches:
            tip = descriptor["tip-commit"]
            if tip not in revision_from_branch_name:
                name = descriptor["name"]
                raise RuntimeError(f'no tip-commit found for "{name}" (tip "{tip}")')

        tutorials = {
            d["name"]: TutorialInfo(
                d["name"],
                d["tip-commit"],
                ProjectHistory(repo_path, revision_from_branch_name[d["tip-commit"]]),
            )
            for d in index_wrt_branches
        }

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

    def write_asset_credits(self, out_file):
        pandoc = shutil.which("pandoc")
        if pandoc is None:
            raise RuntimeError("could not find pandoc executable")

        pandoc_process = subprocess.Popen(
            [
                pandoc,
                "--from=markdown",
                "--to=rst",
                "--output=-",
                "-",
            ],
            stdin=subprocess.PIPE,
            stdout=out_file,
            encoding="utf-8",
        )
        pandoc_input = pandoc_process.stdin

        pandoc_input.write("# Assets contributed by tutorials\n\n")

        for n, t in self.tutorials.items():
            # This computation of 'safe_name' is incomplete.  It
            # handles "Q*Bert".
            #
            # TODO: Might need generalising.
            #
            safe_name = re.sub(r'\*', r'\*', t.name)

            pandoc_input.write(f"## Tutorial _{safe_name}_\n\n")
            for credit in t.project_history.all_asset_credits:
                n_files = len(credit.asset_basenames)
                files_noun = "File" if n_files == 1 else "Files"
                basenames_list = ", ".join(
                    f'`"{name}"`' for name in credit.asset_basenames
                )
                pandoc_input.write(f"\n{files_noun} {basenames_list}: ")
                pandoc_input.write(credit.credit_markdown)

        pandoc_input.close()
        pandoc_process.wait()

    def all_asset_media(self):
        id_iter = itertools.count(64000)
        library_data = MediaLibraryData.new_empty()
        for n, t in self.tutorials.items():
            tag = f'Tutorial "{n}"'
            tutorial_data = t.project_history.medialib_contribution(tag, id_iter)
            library_data.accumulate(tutorial_data)

        return library_data.with_entries_unified()

    def write_asset_media(self, out_dir):
        self.all_asset_media().write_files(out_dir)

    @property
    def gathered_tip_oids(self):
        return [info.project_history.tip_oid_string
                for info in self.tutorials.values()]

    @property
    def build_sources_dicts(self):
        return [info.summary_dict for info in self.tutorials.values()]


def sole_tree_entry(commit):
    entries = list(commit.tree)
    if len(entries) != 1:
        raise TutorialStructureError(
            f"expecting just one entry in tree for {commit.id}"
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

    release_recipes_tip = str(repo.revparse_single(RELEASE_RECIPES_BRANCH_NAME).id)
    contributing_commit_oids = [release_recipes_tip] + tutorials.gathered_tip_oids
    tree_oid = create_union_tree(repo, contributing_commit_oids, extra_files)

    releases_tip = str(repo.revparse_single(RELEASES_BRANCH_NAME).id)
    parent_oids = [releases_tip] + contributing_commit_oids

    new_oid = repo.create_commit(f"refs/heads/{RELEASES_BRANCH_NAME}",
                                 sig, sig,
                                 "Release new versions of tutorials\n",
                                 tree_oid,
                                 parent_oids)
    return new_oid
