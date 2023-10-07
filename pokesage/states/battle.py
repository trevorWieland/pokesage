from pydantic import BaseModel, Field
from typing import List, Union
from .battlestate import BattleState
from .choices import MoveChoice, SwitchChoice, ItemChoice


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
        [], description="The ordered list of battle states as they were before a decision by the player"
    )
    battle_actions: List[Union[MoveChoice, SwitchChoice, ItemChoice]] = Field(
        [], description="The list of decisions the player made at each corresponding BattleState in battle_states"
    )
