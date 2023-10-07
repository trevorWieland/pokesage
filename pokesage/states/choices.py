from pydantic import BaseModel, Field
from typing import Union, List


class TeamChoice(BaseModel):
    """
    Data Model representing a team order decision

    Contains information about move, target, and any extra move actions
    """


class MoveChoice(BaseModel):
    """
    Data Model representing a single move option for a pokemon.

    Contains information about move, target, and any extra move actions
    """


class SwitchChoice(BaseModel):
    """
    Data Model representing a switch-out option for a pokemon.

    Contains information about target switch slot number
    """


class ItemChoice(BaseModel):
    """
    Data Model representing a item-use option for a pokemon.

    Contains information about target and which item to use.

    Unused for showdown. Reserved for future emulator interaction
    """


class PassChoice(BaseModel):
    """
    Data Model representing that this slot doesn't need to do anything, and thus passes.

    Contains no extra information, and while we could design our system to not need this,
     it makes action shapes consistent to require it
    """


class ResignChoice(BaseModel):
    """
    Data Model representing the option to resign.

    Used for type-hinting consistency, and for connectors to gracefully terminate when a sage-class fails
    """


class DefaultChoice(BaseModel):
    """
    Data Model representing a single move option for a pokemon.

    Contains information about move, target, and any extra move actions
    """


AnyChoice = Union[
    List[Union[MoveChoice, SwitchChoice, ItemChoice, PassChoice]], TeamChoice, ResignChoice, DefaultChoice, None
]
TeamOrderChoice = Union[TeamChoice, ResignChoice, DefaultChoice]
MoveDecisionChoice = Union[List[Union[MoveChoice, SwitchChoice, ItemChoice, PassChoice]], ResignChoice, DefaultChoice]
ForceSwitchChoice = Union[List[Union[SwitchChoice, PassChoice]], ResignChoice, DefaultChoice]
