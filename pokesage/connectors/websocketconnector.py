from .abstractconnector import Connector, ProgressState, ConnectionTermination, ConnectionTerminationCode
from ..processors import ShowdownMinimumProcessor, ShowdownProcessor
from ..states.battlestate import BattleState
from ..states.choices import AnyChoice, TeamOrderChoice, MoveDecisionChoice, ForceSwitchChoice, ResignChoice

from aiohttp import ClientSession, WSMsgType, ClientWebSocketResponse
from enum import Enum, unique
from typing import AsyncGenerator, Union, List, Optional, Tuple, Literal, Type
from pydantic import BaseModel, Field
from poketypes.showdown.showdownmessage import Message, MType


class WebsocketConnector(Connector):
    """
    An abstract class defining function headers mandatory for connector objects

    Since the entrypoint for the user is the sage class, the sage class should create the aiohttp session,
    so that all downstream connections use the same async connection pool
    """

    def __init__(
        self,
        showdown_username: str,
        showdown_password: str,
        target_format: str,
        objective: Literal["accept", "challenge", "ladder"],
        whitelist_users: List[str] = [],
        max_concurrent_battles: int = 1,
        total_battles: int = 1,
        processor_class: Type[ShowdownProcessor] = ShowdownMinimumProcessor,
        showdown_uri: str = "ws://localhost:8000/showdown/websocket",
    ) -> None:
        """
        Save connection parameters so that the connection can be initialized later
        """

        self.showdown_username = showdown_username
        self.showdown_password = showdown_password
        self.target_format = target_format
        self.objective = objective

        if self.objective == "challenge" and len(whitelist_users) == 0:
            raise RuntimeError(
                "Objective was set to challenge but no users were in the whitelist! Please add at least one user to the list!"
            )

        self.whitelist_users = whitelist_users
        self.max_concurrent_battles = max_concurrent_battles
        self.total_battles = total_battles
        self.processor_class = processor_class
        self.showdown_uri = showdown_uri

    async def launch_connection(
        self, session: ClientSession
    ) -> AsyncGenerator[Tuple[ProgressState, Union[BattleState, ConnectionTermination, None]], AnyChoice]:
        """
        This function should be an async generator that:
        - yields BattleState
        - accepts Choice as send (See Choice type alias for options)

        This function should be instantiated by the connection handling subclass, not the sage
        """

        conn_term = None

        async with session.connect(self.showdown_uri) as ws:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    message: str = msg.data

                    if message[0] == ">" and "battle" in message:
                        # In this case this is a battle message block
                        battle_id = message.strip().split("\n")[0][1:]

                        for m in message.strip().split("\n"):
                            progress_state, data = await self.handle_battle_message(session, ws, battle_id, m)
                            action = yield progress_state, data

                            progress_state, conn_term = await self.process_action(ws, progress_state, action)

                            if conn_term is not None:
                                break
                    elif message[0] == "|":
                        # In this case this is a standard message block
                        for m in message.strip().split("\n"):
                            progress_state, data = await self.handle_general_message(session, ws, m)
                            action = yield progress_state, data
                    elif message[0] != ">":
                        # In this case this is a global message block
                        progress_state, data = await self.handle_general_message(session, ws, f"||{message}")
                        action = yield progress_state, data
                    else:
                        continue

                    if conn_term is not None:
                        yield ProgressState.FULL_END, conn_term
                        break
                else:
                    # We should never see a websocket error from showdown
                    # If we do see one, we should end and return the error information
                    yield ProgressState.FULL_END, ConnectionTermination(
                        code=ConnectionTerminationCode.CONNECTION_ERROR, message=msg.data
                    )
                    break

    async def handle_general_message(
        self, session: ClientSession, ws: ClientWebSocketResponse, message: str
    ) -> Tuple[ProgressState, None]:
        """ """

    async def handle_battle_message(
        self, session: ClientSession, ws: ClientWebSocketResponse, battle_id: str, message: str
    ) -> Tuple[ProgressState, BattleState]:
        """ """

    async def process_action(
        self, ws: ClientWebSocketResponse, progress_state: ProgressState, action: AnyChoice
    ) -> Tuple[ProgressState, Optional[ConnectionTermination]]:
        """"""

        if progress_state == ProgressState.FULL_END:
            # Process any final logging / closing operations needed if any
            # TODO

            return progress_state, ConnectionTermination(code=ConnectionTerminationCode.OBJECTIVE_COMPLETE)
        elif progress_state == ProgressState.GAME_END:
            # Process game end logging here
            # TODO
            return progress_state, None
        else:
            # Verify/Submit the action to pokemon showdown
            try:
                await self.submit_action(ws, progress_state, action)
            except Exception as e:
                return ProgressState.FULL_END, ConnectionTermination(
                    code=ConnectionTerminationCode.INVALID_CHOICE, message=str(e)
                )

    async def submit_action(
        self, ws: ClientWebSocketResponse, progress_state: ProgressState, action: AnyChoice
    ) -> None:
        """
        This function will:
        - Verify that the action(s) returned the by the user is valid to submit at this time
        - Submit it to showdown

        It will not check if a given move is a legal move, because that step should be done by the processor
        at choice-build time
        """

        # TODO: Fill out verification steps

        if isinstance(action, ResignChoice):
            # Process resignation decision
            pass

        if progress_state == ProgressState.TEAM_ORDER:
            # Check valid formatting for team order submission:
            assert isinstance(action, TeamOrderChoice)
        elif progress_state == ProgressState.SWITCH:
            # Check valid formatting for force-switch submission:
            assert isinstance(action, ForceSwitchChoice)
        elif progress_state == ProgressState.MOVE:
            # Check valid formatting for move submission:
            assert isinstance(action, MoveDecisionChoice)
        else:
            assert action is None

        if not isinstance(action, list):
            # Submit the action as a single item
            await ws.send_str(f"")
