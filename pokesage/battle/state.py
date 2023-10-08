from typing import List, Optional

from poketypes.dex import DexWeather
from pydantic import BaseModel, Field

from .choices import BattleChoice
from .pokemon import BattlePokemon


class BattleState(BaseModel):
    """
    Representing the current state of the field in a given pokemon battle.

    Built to support singles, doubles, or triples gametypes
    """

    turn: int = Field(
        ...,
        description="The turn number of this battle state. Note: We might have multiple states per turn due to force-switches!",
    )

    player_team: List[BattlePokemon] = Field(
        [],
        description="A list containing Pokemon on the player's team. The order should match the order given in the request!",
    )
    opponent_team: List[BattlePokemon] = Field(
        [],
        description="A list containing Pokemon on the opponent's team.",
    )

    weather: Optional[DexWeather.ValueType] = Field(None, description="The current weather in the field")

    battle_choice: Optional[BattleChoice] = Field(
        None, description="The choices the player can make in response to this battle state"
    )
