"""Player Logic for making the first legal choice in a battle.

Contains both DefaultSage and Gorm, which are the same class but with different names.
This class will make the first legal choice, including moves, switches, and team orders.
"""

from aiohttp import ClientSession

from ..battle.choices import DefaultChoice, ForceSwitchChoice, MoveDecisionChoice, TeamOrderChoice
from ..battle.state import BattleState
from .abstractsage import AbstractSage


class DefaultSage(AbstractSage):
    """Picks the first legal option every time.

    Best used for testing connections, as this is even less sophisticated than random choices.
    """

    async def team_choice(self, session: ClientSession, battle_state: BattleState) -> TeamOrderChoice:
        """Generate a TeamOrderChoice decision, which will be used for selecting pokemon order.

        This class specifically will simply return the default choice, which is the original team order given.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            battle_state (BattleState): The current battle state to make a decision from.

        Returns:
            TeamOrderChoice: The default team order
        """
        return DefaultChoice()

    async def move_choice(self, session: ClientSession, battle_state: BattleState) -> MoveDecisionChoice:
        """Generate a MoveDecisionChoice decision, which will be used for typical move selection.

        This class specifically will pick the first legal option for each slot, in order from left to right.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            battle_state (BattleState): The current battle state to make a decision from.

        Returns:
            MoveDecisionChoice: The first legal move(s) to make in this turn.
        """
        return DefaultChoice()

    async def forceswitch_choice(self, session: ClientSession, battle_state: BattleState) -> ForceSwitchChoice:
        """Generate a ForceSwitchChoice decision, which will be used when needing to switch pokemon.

        This class specifically will pick the first legal option for each slot, in order from left to right.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            battle_state (BattleState): The current battle state to make a decision from.

        Returns:
            ForceSwitchChoice: The first legal switch(s) to make in this turn.
        """
        return DefaultChoice()


class Gorm(DefaultSage):
    """
    Sage-named version of the DefaultSage class.

    Cool kids use this instead of DefaultSage
    """
