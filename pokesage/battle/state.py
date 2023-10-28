"""Pydantic BaseModels for the main BattleState class.

This module contains the BattleState class, which is a full representation of a pokemon battle state as a serializable
pydantic object. You may find the need to subclass this class to add additional information to the battle state,
such as additional information about the pokemon, or additional information about the state itself. You may also
extend the class to add/edit serialization functions for use in training a model.

Tip:
    Remember that the BattleState class, unlike the BattleClass, is for storing *state* information about each step
    in the battle. This means that things like weather, field conditions, teams, etc should be stored here, while
    things like player names, victory information, administrative data should be stored in the Battle class.
"""

from beartype.typing import Dict, Optional

from poketypes.dex import DexWeather
from pydantic import BaseModel, Field

from .choices import BattleChoice
from .pokemon import BattlePokemon


class BattleState(BaseModel):
    """A full representation of a pokemon battle state as a serializable object.

    Built to support singles, doubles, or triples gametypes

    Attributes:
        turn: The turn number of this battle state. Note: We might have multiple states per turn due to force-switches!
        player_team: A list containing Pokemon on the player's team.
        opponent_team: A list containing Pokemon on the opponent's team.
        player_slots: Maps the player'ss battle slots to either None or the string id of the pokemon in that slot
        opponent_slots: Maps the opponent's battle slots to either None or the string id of the pokemon in that slot
        weather: The current weather in the field
        battle_choice: The choices the player can make in response to this battle state
    """

    turn: int = Field(
        ...,
        description="The turn number of this battle state.",
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

    player_has_megad: bool = Field(False, description="Whether the player has mega evolved a pokemon")
    opponent_has_megad: bool = Field(False, description="Whether the opponent has mega evolved a pokemon")

    player_has_zmoved: bool = Field(False, description="Whether the player has used a zmove")
    opponent_has_zmoved: bool = Field(False, description="Whether the opponent has used a zmove")

    player_has_dynamaxed: bool = Field(False, description="Whether the player has dynamaxed a pokemon")
    opponent_has_dynamaxed: bool = Field(False, description="Whether the opponent has dynamaxed a pokemon")

    player_has_teratyped: bool = Field(False, description="Whether the player has teratyped a pokemon")
    opponent_has_teratyped: bool = Field(False, description="Whether the opponent has teratyped a pokemon")

    weather: Optional[DexWeather.ValueType] = Field(None, description="The current weather in the field")

    battle_choice: Optional[BattleChoice] = Field(
        None, description="The choices the player can make in response to this battle state"
    )
