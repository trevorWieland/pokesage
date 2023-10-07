from abc import ABC, abstractmethod

from ..processors import Processor
from ..states.battlestate import BattleState
from aiohttp import ClientSession


class Connector(ABC):
    """
    An abstract class defining function headers mandatory for connector objects

    Inheritance Order:
    Connector -> SpecificConnector -> Sage
    """

    @abstractmethod
    async def launch(self) -> None:
        """
        This function should be the main entry point for the player launching.

        In this function you should instantiate any async pools/connectors/tqdm/etc

        This function should be instantiated by the connection handling subclass, not the sage
        """

    @abstractmethod
    async def team_choice(self, session: ClientSession, battle_state: BattleState) -> str:
        """
        This function should return a teamorder decision based on the battle_processor given.

        The function may optionally use the session object given to make any http requests as needed.

        This function should be instantiated by the sage class, not the connection handler
        """

    @abstractmethod
    async def move_choice(self, session: ClientSession, battle_state: BattleState) -> str:
        """
        This function should return a move decision based on the battle_processor given.

        The function may optionally use the session object given to make any http requests as needed.

        This function should be instantiated by the sage class, not the connection handler
        """

    @abstractmethod
    async def forceswitch_choice(self, session: ClientSession, battle_state: BattleState) -> str:
        """
        This function should return a forced-switch decision based on the battle_processor given.

        The function may optionally use the session object given to make any http requests as needed.

        This function should be instantiated by the sage class, not the connection handler
        """
