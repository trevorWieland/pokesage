from abc import ABC, abstractmethod
from typing import Optional
from tqdm.asyncio import tqdm
from aiohttp import ClientSession

from ..battle.choices import ForceSwitchChoice, MoveDecisionChoice, TeamOrderChoice
from ..battle.state import BattleState
from ..connectors import ConnectionTermination, ConnectionTerminationCode, Connector
from ..processors import ProgressState


class AbstractSage(ABC):
    """
    Abstract Sage class for other player classes to implement with their decision functions.

    Each subclass should implement 3 main functions:
    - team_choice:
        - This function will be called when the player is asked which team order they should use.
        - For example, a teampreview message from showdown might trigger this function
        - In formats where less than a full team is used, this should submit the correct sample
    - move_choice:
        - This function will be called when the player is asked for a standard decision in the match
        - For example, every turn the player will recieve a call to this function
        - The player could choose to use moves, items, switch pokemon, or of course, resign
    - forceswitch_choice:
        - This function will be called when the player is forcibly asked to switch one or more pokemon
        - For example, when a pokemon faints they must be switched out before the next move_choice will be triggered
        - The player will have to choose which switches to make, or of course, resign
    """

    def __init__(
        self, name: str, connector: Connector, session: Optional[ClientSession] = None, use_tqdm: bool = False
    ) -> None:
        """ """

        self.name = name
        self.connector = connector
        self.session = session
        self.use_tqdm = use_tqdm

    async def launch(self) -> None:
        """
        Launches the associated connector object, as well as the aiohttp client session if needed
        """

        if self.use_tqdm:
            pbar = tqdm(total=self.connector.total_battles)
        else:
            pbar = None

        if self.session is not None:
            await self.play(session=self.session, pbar=pbar)
        else:
            async with ClientSession() as session:
                await self.play(session=session, pbar=pbar)

        if self.use_tqdm:
            pbar.close()

    async def play(self, session: ClientSession, pbar: Optional[tqdm]) -> None:
        """
        Communicates with the game using the connector.launch_connection generator
        """

        connection = self.connector.launch_connection(session)
        action = None

        while True:
            progress_state, data = await connection.asend(action)

            if progress_state == ProgressState.TEAM_ORDER:
                battle_state: BattleState = data
                action = await self.team_choice(session=session, battle_state=battle_state)
            elif progress_state == ProgressState.MOVE:
                battle_state: BattleState = data
                action = await self.move_choice(session=session, battle_state=battle_state)
                battle_state: BattleState = data
            elif progress_state == ProgressState.SWITCH:
                action = await self.forceswitch_choice(session=session, battle_state=battle_state)
            elif progress_state == ProgressState.GAME_END:
                # Not particularly helpful in this use case, but if built as a gymnasium env, this would provide `terminated`
                # Note: This means that the individual game has ended, *NOT* that the connection is closed.
                action = None

                if pbar is not None:
                    pbar.update(1)
            elif progress_state == ProgressState.FULL_END:
                # This tells us that the connection itself has been ended
                action = None

                print(data.model_dump_json(indent=2))

                break
            else:
                # This means a NO_ACTION state was returned.
                # since no action is needed, we can just continue
                action = None

            # print(progress_state)
            if action is not None:
                # print(f"Sending: {type(action)}")
                # print(action.model_dump_json(indent=2))
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
