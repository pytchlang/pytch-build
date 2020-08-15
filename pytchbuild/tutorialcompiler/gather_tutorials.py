from dataclasses import dataclass
from typing import Dict
import yaml
import bs4
from pathlib import Path
import zipfile
import copy
import pygit2
import time
from contextlib import closing

from .fromgitrepo import git_repository
from .fromgitrepo.tutorial_history import ProjectHistory
from .fromgitrepo.tutorial_bundle import TutorialBundle


RELEASES_BRANCH_NAME = "releases"
RELEASE_RECIPES_BRANCH_NAME = "release-recipes"


@dataclass
class TutorialSummary:
    name: str  # Currently just for human readers
    div: bs4.element.Tag


@dataclass
class TutorialCollection:
    tutorials: Dict[str, ProjectHistory]

    @classmethod
    def from_repo_path(cls, repo_path):
        with git_repository(repo_path) as repo:
            index_path = Path(repo.workdir) / "index.yaml"
            with index_path.open("rt") as yaml_file:
                tutorial_dicts = yaml.load(yaml_file, yaml.Loader)

        tutorials = {d["name"]: ProjectHistory(repo_path, d["tip-commit"])
                     for d in tutorial_dicts}
        return cls(tutorials)

    def write_to_zipfile(self, zfile):
        bundles = [TutorialBundle.from_project_history(project_history)
                   for project_history in self.tutorials.values()]

        for bundle in bundles:
            bundle.write_to_zipfile(zfile)

        index_soup = bs4.BeautifulSoup('<div class="tutorial-index"></div>',
                                       "html.parser")
        index_div = index_soup.find("div")
        for bundle in bundles:
            summary_div = copy.deepcopy(bundle.summary_html)
            summary_div["data-tutorial-name"] = bundle.top_level_directory_name
            index_div.append(summary_div)

        zfile.writestr("tutorial-index.html", index_soup.encode("utf-8"))

    def write_new_zipfile(self, out_file):
        bare_zfile = zipfile.ZipFile(out_file,
                                     mode="w",
                                     compression=zipfile.ZIP_DEFLATED)

        with closing(bare_zfile) as zfile:
            self.write_to_zipfile(zfile)

    @property
    def gathered_tip_oids(self):
        return [t.tip_oid_string for t in self.tutorials.values()]


def create_signature(repo):
    return pygit2.Signature(repo.config['user.name'],
                            repo.config['user.email'],
                            time=int(time.time()))


def sole_tree_entry(commit):
    entries = list(commit.tree)
    if len(entries) != 1:
        raise ValueError(f"expecting just one entry in tree for {commit.oid}")
    return entries[0]


def verify_entry_type(idx, entry):
    """Verify type of entry is as expected given its index

    Special-purpose for the list of contributing commits used to create a
    release.  The first one is the recipe branch, which should have just the
    "index.yaml" file.  The rest should be tutorial branches, which should have
    just one top-level subdirectory for the tutorial code and data.
    """
    if idx == 0 and entry.filemode != pygit2.GIT_FILEMODE_BLOB:
        raise ValueError(f"expecting tree-entry to be BLOB for {entry.id}")
    if idx > 0 and entry.filemode != pygit2.GIT_FILEMODE_TREE:
        raise ValueError(f"expecting tree-entry to be TREE for {entry.id}")


def verify_index_yaml_clean(repo):
    working_path = Path(repo.workdir) / "index.yaml"
    working_data = working_path.open("rb").read()
    recipes_tip_commit = repo.revparse_single(RELEASE_RECIPES_BRANCH_NAME)
    recipes_tip_tree = recipes_tip_commit.tree
    recipes_tip_entry = recipes_tip_tree["index.yaml"]
    recipes_tip_data = recipes_tip_entry.data

    if not working_data == recipes_tip_data:
        raise ValueError('file "index.yaml" in working directory'
                         ' does not match version at tip of branch'
                         f' "{RELEASE_RECIPES_BRANCH_NAME}"')


def create_union_tree(repo, commit_oid_strs):
    """Create and write the union of the trees of the given commits as a new tree

    Return the OID of the resulting new tree.
    """
    tree_builder = repo.TreeBuilder()
    names_already_added = set()
    for idx, oid in enumerate(commit_oid_strs):
        entry = sole_tree_entry(repo[oid])
        verify_entry_type(idx, entry)
        if entry.name in names_already_added:
            raise ValueError(f'duplicate name "{entry.name}"')
        tree_builder.insert(entry.name, entry.id, entry.filemode)
        names_already_added.add(entry.name)
    return tree_builder.write()


def commit_to_releases(repo, tutorial_tip_oid_strs):
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

    release_recipes_tip = str(repo.revparse_single(RELEASE_RECIPES_BRANCH_NAME).oid)
    contributing_commit_oids = [release_recipes_tip] + tutorial_tip_oid_strs
    tree_oid = create_union_tree(repo, contributing_commit_oids)

    releases_tip = str(repo.revparse_single(RELEASES_BRANCH_NAME).oid)
    parent_oids = [releases_tip] + contributing_commit_oids

    new_oid = repo.create_commit(f"refs/heads/{RELEASES_BRANCH_NAME}",
                                 sig, sig,
                                 "Release new versions of tutorials\n",
                                 tree_oid,
                                 parent_oids)
    return new_oid
