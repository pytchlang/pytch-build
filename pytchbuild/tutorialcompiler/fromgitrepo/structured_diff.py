from dataclasses import dataclass
from typing import Literal
from .structured_program import (
    make_of_kind,
    ActorIdentifier,
    ScriptPath,
    EventDescriptor,
)


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
