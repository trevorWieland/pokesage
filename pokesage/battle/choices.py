from beartype.typing import List, Optional, Union

from pydantic import BaseModel, Field


class TeamChoice(BaseModel):
    """
    Data Model representing a team order decision

    Contains information about move, target, and any extra move actions
    """

    team_order: List[int] = Field(
        ...,
        description="A list of integer pokemon slots in the order you want them.",
    )

    def to_showdown(self) -> str:
        """
        Converts the choice to a showdown-formatted decision
        """

        if len(self.team_order) >= 10:
            return "team " + ",".join([str(s) for s in self.team_order])
        else:
            return "team " + "".join([str(s) for s in self.team_order])


class MoveChoice(BaseModel):
    """
    Data Model representing a single move option for a pokemon.

    Contains information about move, target, and any extra move actions
    """

    move_number: int = Field(..., description="The 1-indexed position of the move")

    target_number: Optional[int] = Field(None, description="The 1-indexed target of the move, if needed.")

    tera: bool = Field(False, description="Whether this choice involves teratyping first")
    mega: bool = Field(False, description="Whether this choice involves mega-evolving first")
    dyna: bool = Field(False, description="Whether this choice involves dynamaxing first")
    zmove: bool = Field(False, description="Whether this choice is using the zmove form of the move")

    def to_showdown(self) -> str:
        """
        Converts the choice to a showdown-formatted decision
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
    """
    Data Model representing a switch-out option for a pokemon.

    Contains information about target switch slot number
    """

    slot: int = Field(..., description="The slot to switch to")

    def to_showdown(self) -> str:
        """
        Converts the choice to a showdown-formatted decision
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
        """
        Converts the choice to a showdown-formatted decision
        """

        raise NotImplementedError


class PassChoice(BaseModel):
    """
    Data Model representing that this slot doesn't need to do anything, and thus passes.

    Contains no extra information, and while we could design our system to not need this,
     it makes action shapes consistent to require it
    """


class ResignChoice(BaseModel):
    """
    Data Model representing the option to resign.

    Used for type-hinting consistency, and for connectors to gracefully terminate when a sage-class fails for just one battle
    """


class QuitChoice(BaseModel):
    """
    Data Model representing the option to resign all games and close connection.

    Used for type-hinting consistency, and for connectors to gracefully terminate when a sage-class fails irrecoverably
    """


class DefaultChoice(BaseModel):
    """
    Data Model representing a single move option for a pokemon.

    Contains information about move, target, and any extra move actions
    """

    def to_showdown(self) -> str:
        """
        Converts the choice to a showdown-formatted decision
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
MoveDecisionChoice = Union[
    List[Union[MoveChoice, SwitchChoice, ItemChoice, PassChoice]],
    ResignChoice,
    DefaultChoice,
    QuitChoice,
]
ForceSwitchChoice = Union[List[Union[SwitchChoice, PassChoice]], ResignChoice, DefaultChoice, QuitChoice]
