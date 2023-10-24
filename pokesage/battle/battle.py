"""Pydantic BaseModels for the main Battle class.

This module contains the Battle class, which is a full representation of a pokemon battle as a serializable object.
You may find the need to subclass this class to add additional information to the battle, particularly if you are
adapting this for use in a format that isn't directly supported. Additionally, you might subclass this to add/edit
serialization functions for use in training a model.

Tip:
    Remember that the Battle class, and any subclasses therin should focus on storing *administrative* information about
    the battle, while the BattleState class, and any subclasses therin should focus on storing *state* information about
    each individual state in the battle.
"""

from typing import List, Literal, Optional

from poketypes.dex import DexGen
from pydantic import BaseModel, Field

from .choices import AnyChoice
from .state import BattleState


class Battle(BaseModel):
    """A full representation of a pokemon battle as a serializable object.

    One Battle contains multiple BattleStates in an ordered list.
    Each BattleState should represent the battlefield itself at the point of a decision.
    This class should (other than the BattleState list) contain no state-specific details.

    Things like weather, field conditions, teams, etc should be stored *only* in the BattleState.
    Things like player names, victory information, administrative data should be stored here.

    Built to support singles, doubles, or triples gametypes

    Attributes:
        battle_states: The ordered list of battle states as they were before each decision.
        battle_actions: The list of decisions the player made at each corresponding BattleState in battle_states
        player_name: The player's name
        player_rating: The rating of the player
        player_id: A unique identifier for the player
        opponent_name: The opponent's name
        opponent_rating: The rating of the opponent
        opponent_id: A unique identifier for the opponent
        rated: Whether this match is rated or not
        gametype: The gametype of this battle
        format: The format of this match
        gen: The generation this battle format corresponds to
        turn: The current / total number of turns in this battle
        player_victory: Whether this resulted in the player's victory
        player_team_size: The integer team size of the player
        opponent_team_size: The integer team size of the opponent
    """

    battle_states: List[BattleState] = Field(
        [],
        description="The ordered list of battle states as they were before a decision by the player",
    )
    battle_actions: Optional[AnyChoice] = Field(
        None,
        description="The list of decisions the player made at each corresponding BattleState in battle_states",
    )

    player_name: Optional[str] = Field(None, description="The player's name")
    player_rating: Optional[int] = Field(None, description="The rating of the player")
    player_id: Optional[str] = Field(None, description="A unique identifier for the player")

    opponent_name: Optional[str] = Field(None, description="The opponent's name")
    opponent_rating: Optional[int] = Field(None, description="The rating of the opponent")
    opponent_id: Optional[str] = Field(None, description="A unique identifier for the opponent")

    rated: bool = Field(False, description="Whether this match is rated or not")

    gametype: Optional[Literal["singles", "doubles", "triples"]] = Field(
        None, description="The gametype of this battle"
    )
    format: Optional[str] = Field(None, description="The format of this match")
    gen: Optional[DexGen.ValueType] = Field(None, description="The generation this battle format corresponds to")
    turn: int = Field(None, description="The current / total number of turns in this battle")

    player_victory: Optional[bool] = Field(None, description="Whether this resulted in the player's victory")

    player_team_size: Optional[int] = Field(None, description="The integer team size of the player")
    opponent_team_size: Optional[int] = Field(None, description="The integer team size of the opponent")

    def slot_length(self) -> int:
        """Identify the slot length based on the gametype.

        Raises:
            RuntimeError: If the gametype is not initialized, this function will fail.
            RuntimeError: If the gametype is somehow not one of the expected values, this function will fail.

        Returns:
            int: The integer number of slots for this gametype
        """
        if self.gametype is None:
            raise RuntimeError("slot_length was called but no gametype was set!")

        if self.gametype == "singles":
            return 1
        if self.gametype == "doubles":
            return 2
        if self.gametype == "triples":
            return 3

        raise RuntimeError(f"Unknown gametype: {self.gametype}")
