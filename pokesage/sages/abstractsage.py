from abc import ABC, abstractmethod
from ..connectors import Connector, ConnectionTerminationCode, ConnectionTermination, ProgressState
from ..states.choices import TeamOrderChoice, MoveDecisionChoice, ForceSwitchChoice
from ..states.battlestate import BattleState
from typing import Optional
from aiohttp import ClientSession


class AbstractSage(ABC):
    """ """

    def __init__(self, name: str, connector: Connector, session: Optional[ClientSession] = None) -> None:
        """ """

        self.name = name
        self.connector = connector
        self.session = session

    async def launch(self) -> None:
        """
        Launches the associated connector object, as well as the aiohttp client session if needed
        """

        action = None

        if self.session is not None:
            await self.play(session=self.session)
        else:
            async with ClientSession() as session:
                await self.play(session=session)

    async def play(self, session: ClientSession) -> None:
        """
        Communicates with the game using the connector-launch generator
        """

        connection = await self.connector.launch_connection(session)

        while True:
            try:
                progress_state, battle_state = connection.send(action)

                if progress_state == ProgressState.TEAM_ORDER:
                    action = await self.team_choice(session=session, battle_state=battle_state)
                elif progress_state == ProgressState.MOVE:
                    action = await self.move_choice(session=session, battle_state=battle_state)
                elif progress_state == ProgressState.SWITCH:
                    action = await self.forceswitch_choice(session=session, battle_state=battle_state)
                elif progress_state == ProgressState.END:
                    # Not particularly helpful in this use case, but if built as a gymnasium env, this would provide `terminated`
                    # Note: This means that the individual game has ended, *NOT* that the connection is closed.
                    action = None

            except StopIteration as ex:
                term: ConnectionTermination = ex[0]

                if term.code == ConnectionTerminationCode.OBJECTIVE_COMPLETE:
                    # In this case the objective has completed
                    # For example, we could have laddered for the set number of matches, or challenged all the opponents, etc
                    pass
                else:
                    # This is the error state (Something has gone wrong)
                    pass

    @abstractmethod
    async def team_choice(self, session: ClientSession, battle_state: BattleState) -> TeamOrderChoice:
        """
        This function should return a teamorder decision based on the battle_processor given.

        The function may optionally use the session object given to make any http requests as needed.

        This function should be instantiated by the sage class, not the connection handler
        """

    @abstractmethod
    async def move_choice(self, session: ClientSession, battle_state: BattleState) -> MoveDecisionChoice:
        """
        This function should return a move decision based on the battle_processor given.

        The function may optionally use the session object given to make any http requests as needed.

        This function should be instantiated by the sage class, not the connection handler
        """

    @abstractmethod
    async def forceswitch_choice(self, session: ClientSession, battle_state: BattleState) -> ForceSwitchChoice:
        """
        This function should return a forced-switch decision based on the battle_processor given.

        The function may optionally use the session object given to make any http requests as needed.

        This function should be instantiated by the sage class, not the connection handler
        """
