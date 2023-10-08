from typing import List, Literal, Optional

from poketypes.dex import DexGen
from pydantic import BaseModel, Field

from .choices import AnyChoice, BattleChoice
from .state import BattleState


class Battle(BaseModel):
    """
    Representing a battle in its entirety.
    One Battle contains multiple BattleStates in an ordered list.
    Each BattleState should represent the battlefield itself at the point of a decision.

    This class should (other than the BattleState list) contain no state-specific details.

    Things like weather, field conditions, teams, etc should be stored *only* in the BattleState.
    Things like player names, victory information, administrative data should be stored here.

    Built to support singles, doubles, or triples gametypes
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
        """
        Helper function to quickly tell how many slots there are for this gametype
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
