from dataclasses import dataclass
from typing import Literal
from .cached_property import cached_property
from .structured_program import (
    make_of_kind,
    ActorIdentifier,
    ScriptPath,
    EventDescriptor,
    StructuredPytchProgram,
)
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
class JrCommitAddMedialibAppearance:
    kind: Literal["add-medialib-appearance"]
    actor: ActorIdentifier
    displayIdentifier: str
    appearanceFilename: str
    make = make_of_kind("add-medialib-appearance")


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
    old_code: str
    new_code: str

    @cached_property
    def old_program(self):
        return StructuredPytchProgram(self.old_code)

    @cached_property
    def new_program(self):
        return StructuredPytchProgram(self.new_code)

    def sole_added(self, old_objs, new_objs, name):
        old_set = set(old_objs)
        new_set = set(new_objs)

        removed_objs = old_set - new_set
        if len(removed_objs) > 0:
            raise TutorialStructureError(
                f"expecting every {name} from old code to still exist"
                f" in new code, but found {removed_objs!r} removed"
            )

        added_objs = new_set - old_set
        if len(added_objs) != 1:
            raise TutorialStructureError(
                f"expecting exactly one new {name} to exist in new code"
                f" compared to old code, but found {added_objs!r} added"
            )

        return added_objs.pop()

    def assert_lists_unchanged(self, old_objs, new_objs, name_plural):
        if new_objs != old_objs:
            raise TutorialStructureError(
                f"expecting the collection of {name_plural}"
                " to be unchanged, but found"
                f" old list {old_objs} to differ"
                f" from new list {new_objs}"
            )
