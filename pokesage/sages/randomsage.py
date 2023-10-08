from aiohttp import ClientSession

from ..battle.choices import DefaultChoice, ForceSwitchChoice, MoveDecisionChoice, TeamOrderChoice
from ..battle.state import BattleState
from .abstractsage import AbstractSage


class RandomSage(AbstractSage):
    """
    Picks the first legal option every time.

    Best used for testing connections, as this is even less sophisticated than random choices.
    """

    async def team_choice(self, session: ClientSession, battle_state: BattleState) -> TeamOrderChoice:
        """
        Simply returns default choice, which will signify picking the first legal option.

        This is the equivalent to picking /choose default on showdown or running out of time in VGC
        """

        # TODO: Implement random team ordering

        return DefaultChoice()

    async def move_choice(self, session: ClientSession, battle_state: BattleState) -> MoveDecisionChoice:
        """
        Simply returns default choice, which will signify picking the first legal option.

        This is the equivalent to picking /choose default on showdown or running out of time in VGC
        """

        # TODO: Implement random move sampling

        return DefaultChoice()

    async def forceswitch_choice(self, session: ClientSession, battle_state: BattleState) -> ForceSwitchChoice:
        """
        Simply returns default choice, which will signify picking the first legal option.

        This is the equivalent to picking /choose default on showdown or running out of time in VGC
        """

        # TODO: Implement random move sampling

        return DefaultChoice()


class Bronius(RandomSage):
    """
    Sage-named version of the RandomSage class.

    Cool kids use this instead of RandomSage
    """
