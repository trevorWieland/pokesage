"""Pydantic BaseModels for choices the player can make in a battle.

In addition to the BaseModels, this module also contains type aliases for the various types of choices that can be made.
Be careful when using these type aliases, as the standard isinstance() function will not work on them. Instead, use
beartypes or some other type-checking library to ensure that the choice you are given is the one you expect.
"""

from beartype.typing import List, Optional, Union

from pydantic import BaseModel, Field

from poketypes.dex import DexMoveTarget


class TeamChoice(BaseModel):
    """Base Model representing a team order decision.

    When initialized, team_order will be in sorted order. As a response to this Choice, the player should sort the
    team_order list in the order they want their pokemon to be in.

    Attributes:
        team_order: A list of integer pokemon slots in the order you want them.
    """

    team_order: List[int] = Field(
        ...,
        description="A list of integer pokemon slots in the order you want them.",
    )

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        if len(self.team_order) >= 10:
            return "team " + ",".join([str(s) for s in self.team_order])
        else:
            return "team " + "".join([str(s) for s in self.team_order])


class MoveChoice(BaseModel):
    """Base Model representing a single move option for a pokemon.

    Contains information about move, target, and any extra move actions.

    Attributes:
        move_number: The 1-indexed position of the move
        target_number: The 1-indexed target of the move, if needed.
        target_type: The target type of the move. Can be None if you can't target anything. (Locked into Outrage, etc)
        tera: Whether this choice involves teratyping first
        mega: Whether this choice involves mega-evolving first
        dyna: Whether this choice involves dynamaxing first
        zmove: Whether this choice is using the zmove form of the move
    """

    move_number: int = Field(..., description="The 1-indexed position of the move")

    target_type: Optional[DexMoveTarget.ValueType] = Field(
        ...,
        description="The target type of the move. Can be None if you can't target anything. (Locked into Outrage, etc)",
    )

    target_number: Optional[int] = Field(None, description="The 1-indexed target of the move, if needed.")

    tera: bool = Field(False, description="Whether this choice involves teratyping first")
    mega: bool = Field(False, description="Whether this choice involves mega-evolving first")
    dyna: bool = Field(False, description="Whether this choice involves dynamaxing first")
    zmove: bool = Field(False, description="Whether this choice is using the zmove form of the move")

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        choice = f"move {self.move_number}"

        if self.target_number is not None:
            choice += f" {self.target_number}"
        if self.tera:
            choice += " terastallize"
        if self.mega:
            choice += " mega"
        if self.dyna:
            choice += " dynamax"
        if self.zmove:
            choice += " zmove"

        return choice.strip()


class SwitchChoice(BaseModel):
    """Base Model representing a switch-out option for a pokemon.

    Contains information about target switch slot number

    Attributes:
        slot: The slot to switch to
    """

    slot: int = Field(..., description="The slot to switch to")

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        choice = f"switch {self.slot}"

        return choice.strip()


class ItemChoice(BaseModel):
    """
    Data Model representing a item-use option for a pokemon.

    Contains information about target and which item to use.

    Unused for showdown. Reserved for future emulator interaction
    """

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision

        Raises:
            NotImplementedError: This choice is not supported in showdown
        """
        raise NotImplementedError


class PassChoice(BaseModel):
    """Base Model representing that this slot doesn't need to do anything, and thus passes.

    Contains no extra information, and while we could design our system to not need this,
    it makes action shapes consistent to require it
    """

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        return "pass"


class ResignChoice(BaseModel):
    """Base Model representing the option to resign.

    Used for type-hinting consistency, and for connectors to gracefully terminate when a sage-class fails for this
    individual battle, but not irrecoverably for all battles.
    """

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        return "forfeit"


class QuitChoice(BaseModel):
    """Base Model representing the option to resign all games and close connection.

    Used for type-hinting consistency, and for connectors to gracefully terminate when a sage-class fails irrecoverably.
    """

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        return "forfeit"


class DefaultChoice(BaseModel):
    """Base Model representing picking the first legal option.

    Used for type-hinting consistency, since the default option is always the first legal option.
    """

    def to_showdown(self) -> str:
        """Convert the choice to a showdown-formatted decision.

        Returns:
            str: The showdown-formatted decision
        """
        return "default"


AnyChoice = Union[
    List[Union[MoveChoice, SwitchChoice, ItemChoice, PassChoice]],
    TeamChoice,
    ResignChoice,
    DefaultChoice,
    QuitChoice,
    None,
]
BattleChoice = Union[
    List[
        Union[
            List[Union[MoveChoice, SwitchChoice, ItemChoice],],
            PassChoice,
        ]
    ],
    TeamChoice,
]

TeamOrderChoice = Union[TeamChoice, ResignChoice, DefaultChoice, QuitChoice]
SlotChoice = Union[MoveChoice, SwitchChoice, ItemChoice, PassChoice]
MoveDecisionChoice = Union[
    List[SlotChoice],
    ResignChoice,
    DefaultChoice,
    QuitChoice,
]
ForceSwitchChoice = Union[List[Union[SwitchChoice, PassChoice]], ResignChoice, DefaultChoice, QuitChoice]
