from beartype.typing import Dict, Optional

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

    player_team: Dict[str, BattlePokemon] = Field(
        {},
        description="A list containing Pokemon on the player's team. The keys must be unique to this pokemon",
    )
    opponent_team: Dict[str, BattlePokemon] = Field(
        {},
        description="A list containing Pokemon on the opponent's team.",
    )

    player_slots: Dict[int, Optional[str]] = Field(
        {}, description="Maps the player'ss battle slots to either None or the string id of the pokemon in that slot"
    )
    opponent_slots: Dict[int, Optional[str]] = Field(
        {}, description="Maps the opponent's battle slots to either None or the string id of the pokemon in that slot"
    )

    weather: Optional[DexWeather.ValueType] = Field(None, description="The current weather in the field")

    battle_choice: Optional[BattleChoice] = Field(
        None, description="The choices the player can make in response to this battle state"
    )
