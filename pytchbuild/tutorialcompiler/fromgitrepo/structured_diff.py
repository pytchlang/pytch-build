from dataclasses import dataclass
from typing import Literal
from .cached_property import cached_property
from .structured_program import (
    ActorIdentifier,
    ScriptPath,
    EventDescriptor,
    StructuredPytchProgram,
)
from .utils import make_of_kind
from .errors import TutorialStructureError


#########################################################################
#
# Mirror the TypeScript classes used to represent different kinds of
# commits to "per-method" programs.


@dataclass
class JrCommitAddSprite:
    kind: Literal["add-sprite"]
    name: str
    make = make_of_kind("add-sprite")


@dataclass
class JrCommitAddMedialibAppearancesEntry:
    kind: Literal["add-medialib-appearances-entry"]
    actor: ActorIdentifier
    displayIdentifier: str
    nItems: int
    make = make_of_kind("add-medialib-appearances-entry")


@dataclass
class JrCommitDeleteAppearance:
    kind: Literal["delete-appearance"]
    actor: ActorIdentifier
    appearanceFilename: str
    make = make_of_kind("delete-appearance")


@dataclass
class JrCommitAddScript:
    kind: Literal["add-script"]
    path: ScriptPath
    event: EventDescriptor
    codeText: str
    make = make_of_kind("add-script")


@dataclass
class JrCommitEditScript:
    kind: Literal["edit-script"]
    path: ScriptPath
    event: EventDescriptor
    oldCodeText: str
    newCodeText: str
    make = make_of_kind("edit-script")


@dataclass
class JrCommitChangeHatBlock:
    kind: Literal["change-hat-block"]
    path: ScriptPath
    codeText: str
    oldEvent: EventDescriptor
    newEvent: EventDescriptor
    make = make_of_kind("change-hat-block")


########################################################################


@dataclass
class StructuredPytchDiff:
    label: str
    old_code: str
    new_code: str

    @cached_property
    def old_program(self):
        return StructuredPytchProgram(self.old_code)

    @cached_property
    def new_program(self):
        return StructuredPytchProgram(self.new_code)

    def structure_error(self, msg):
        return TutorialStructureError(f"{self.label}: {msg}")

    def sole_added(self, old_objs, new_objs, name):
        old_set = set(old_objs)
        new_set = set(new_objs)

        removed_objs = old_set - new_set
        if len(removed_objs) > 0:
            raise self.structure_error(
                f"expecting every {name} from old code to still exist"
                f" in new code, but found {removed_objs!r} removed"
            )

        added_objs = new_set - old_set
        if len(added_objs) != 1:
            raise self.structure_error(
                f"expecting exactly one new {name} to exist in new code"
                f" compared to old code, but found {added_objs!r} added"
            )

        return added_objs.pop()

    def sole_removed(self, old_objs, new_objs, name):
        old_set = set(old_objs)
        new_set = set(new_objs)

        added_objs = new_set - old_set
        if len(added_objs) > 0:
            raise self.structure_error(
                f"expecting every {name} in new code to have existed"
                f" in old code, but found {added_objs!r} added"
            )

        removed_objs = old_set - new_set
        if len(removed_objs) != 1:
            raise self.structure_error(
                f"expecting exactly one {name} to be removed in new code"
                f" compared to old code, but found {removed_objs!r} removed"
            )

        return removed_objs.pop()

    def assert_lists_unchanged(self, old_objs, new_objs, name_plural):
        if new_objs != old_objs:
            raise self.structure_error(
                f"expecting the collection of {name_plural}"
                " to be unchanged, but found"
                f" old list {old_objs} to differ"
                f" from new list {new_objs}"
            )

    def add_sprite_commit(self):
        added_class_name = self.sole_added(
            self.old_program.all_actor_names,
            self.new_program.all_actor_names,
            "class",
        )
        return JrCommitAddSprite.make(added_class_name)

    def add_medialib_appearance_commit(self, display_identifier):
        added_appearance = self.sole_added(
            set(self.old_program.all_appearances),
            set(self.new_program.all_appearances),
            "appearance",
        )
        return JrCommitAddMedialibAppearancesEntry.make(
            added_appearance.actor_identifier,
            display_identifier,
            1,
        )

    def add_medialib_appearances_entry_commit(self, entry_name):
        old_appearances = set(self.old_program.all_appearances)
        new_appearances = set(self.new_program.all_appearances)
        if len(old_appearances - new_appearances) > 0:
            raise self.structure_error(
                "expecting no appearances to be removed"
            )

        added_appearances = new_appearances - old_appearances
        if len(added_appearances) <= 1:
            raise self.structure_error(
                "expecting more than one appearance to be added"
            )

        actors_adding_appearances = set(
            appearance.actor_identifier
            for appearance in added_appearances
        )
        if len(actors_adding_appearances) != 1:
            raise self.structure_error(
                "expecting appearances to be added to exactly"
                " one actor"
            )

        actor = actors_adding_appearances.pop()

        return JrCommitAddMedialibAppearancesEntry.make(
            actor,
            entry_name,
            len(added_appearances),
        )

    def delete_appearance_commit(self):
        deleted_appearance = self.sole_removed(
            set(self.old_program.all_appearances),
            set(self.new_program.all_appearances),
            "appearance",
        )
        return JrCommitDeleteAppearance.make(
            deleted_appearance.actor_identifier,
            deleted_appearance.appearance_name,
        )

    def add_script_commit(self):
        added_path = self.sole_added(
            set(self.old_program.all_script_paths),
            set(self.new_program.all_script_paths),
            "script",
        )
        added_script = self.new_program.handler_from_path(added_path)
        return JrCommitAddScript.make(
            added_path,
            added_script.summary.event,
            added_script.summary.code_text,
        )

    def assert_event_unchanged(self, old_script, new_script):
        assert new_script.path == old_script.path
        old_event = old_script.script.event
        new_event = new_script.script.event
        if new_event != old_event:
            raise self.structure_error(
                f"expecting event for script at {old_script.path}"
                f" to be unchanged, but found {old_event} for old"
                f" vs {new_event} for new"
            )

    def assert_code_unchanged(self, old_script, new_script):
        assert new_script.path == old_script.path
        old_code_lines = old_script.script.body_lines
        new_code_lines = new_script.script.body_lines
        if new_code_lines != old_code_lines:
            raise self.structure_error(
                f"expecting code for script at {old_script.path}"
                f" to be unchanged, but found {old_code_lines} for old"
                f" vs {new_code_lines} for new"
            )

    def sole_edit_script_commit(self, commits):
        n_commits = len(commits)
        if n_commits != 1:
            paths = [commit.path for commit in commits]
            raise self.structure_error(
                "expecting exactly one script to have different"
                f" code but found {n_commits}, at {paths}"
            )
        return commits[0]

    def edit_script_commit(self):
        self.assert_lists_unchanged(
            self.old_program.all_script_paths,
            self.new_program.all_script_paths,
            "script paths",
        )

        commits = []
        for old_script, new_script in zip(
            self.old_program.all_scripts,
            self.new_program.all_scripts,
        ):
            self.assert_event_unchanged(old_script, new_script)
            old_code = old_script.script.body_suite_text
            new_code = new_script.script.body_suite_text
            if new_code != old_code:
                commits.append(
                    JrCommitEditScript.make(
                        old_script.path,
                        old_script.script.event,
                        old_code,
                        new_code,
                    )
                )

        return self.sole_edit_script_commit(commits)

    def sole_change_hat_block_commit(self, commits):
        n_commits = len(commits)
        if n_commits != 1:
            paths = [commit.path for commit in commits]
            raise self.structure_error(
                "expecting exactly one script to have a different"
                f" hat-block but found {n_commits}, at {paths}"
            )
        return commits[0]

    def change_hat_block_commit(self):
        self.assert_lists_unchanged(
            self.old_program.all_script_paths,
            self.new_program.all_script_paths,
            "script paths",
        )

        commits = []
        for old_script, new_script in zip(
            self.old_program.all_scripts,
            self.new_program.all_scripts,
        ):
            self.assert_code_unchanged(old_script, new_script)
            old_event = old_script.script.event
            new_event = new_script.script.event
            if new_event != old_event:
                commits.append(
                    JrCommitChangeHatBlock.make(
                        old_script.path,
                        old_script.script.body_suite_text,
                        old_script.script.event,
                        new_script.script.event,
                    )
                )

        return self.sole_change_hat_block_commit(commits)

    def rich_commit(self, kind, *args):
        match kind:
            case "add-sprite":
                return self.add_sprite_commit(*args)
            case "add-medialib-appearance":
                return self.add_medialib_appearance_commit(*args)
            case "add-medialib-appearances-entry":
                return self.add_medialib_appearances_entry_commit(*args)
            case "delete-appearance":
                return self.delete_appearance_commit(*args)
            case "add-script":
                return self.add_script_commit(*args)
            case "edit-script":
                return self.edit_script_commit(*args)
            case "change-hat-block":
                return self.change_hat_block_commit(*args)

        raise ValueError(f'{self.label}: unknown commit-kind "{kind}"')
