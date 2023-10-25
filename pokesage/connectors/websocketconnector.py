"""Connector class for using the Showdown Websocket Simulator as a backend."""

import json
import os
from beartype.typing import AsyncGenerator, Dict, List, Literal, Optional, Tuple, Type, Union
from urllib.parse import quote

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType
from poketypes.showdown.showdownmessage import (
    Message,
    Message_challstr,
    MType,
    Message_updatesearch,
)
from yarl import URL
from beartype.door import is_bearable

from ..battle.battle import Battle
from ..battle.choices import AnyChoice, ForceSwitchChoice, MoveDecisionChoice, QuitChoice, ResignChoice, TeamOrderChoice
from ..battle.state import BattleState
from ..processors import ShowdownProcessor
from .abstractconnector import ConnectionTermination, ConnectionTerminationCode, Connector, ProgressState


class WebsocketConnector(Connector):
    """Connector class for using the Showdown Websocket Simulator as a backend.

    Tip:
        Since the entrypoint for the user is the sage class, the sage class should create the aiohttp session,
        so that all downstream connections use the same async connection pool.

    Args:
        showdown_username (str): The username to use for logging in to showdown
        showdown_password (str): The password to use for logging in to showdown
        target_format (str): The format to use for this connection
        gametype (Literal["singles", "doubles", "triples"]): The gametype to use for this connection
        objective (Literal["accept", "challenge", "ladder"]): The objective to use for this connection
        whitelist_users (Optional[List[str]], optional): A list of users to challenge if the objective is challenge.
            Defaults to [].
        max_concurrent_battles (int, optional): The maximum number of concurrent battles to have at once.
            Defaults to 1.
        total_battles (int, optional): The total number of battles to play. Defaults to 1.
        processor_class (Type[ShowdownProcessor], optional): The processor class to use for this connection.
            Defaults to ShowdownProcessor.
        showdown_uri (str, optional): The uri to use for connecting to showdown.
            Defaults to "ws://localhost:8000/showdown/websocket".
        save_logs (bool, optional): Whether to save logs for each battle. Defaults to False.
        save_json (bool, optional): Whether to save json dumps for each battle. Defaults to False.

    Attributes:
        showdown_username: The username to use for logging in to showdown
        showdown_password: The password to use for logging in to showdown
        target_format: The format to use for this connection
        gametype: The gametype to use for this connection
        objective: The objective to use for this connection
        whitelist_users: A list of users to challenge if the objective is challenge.
        max_concurrent_battles: The maximum number of concurrent battles to have at once.
        total_battles: The total number of battles to play.
        processor_class: The processor class to use for this connection.
        showdown_uri: The uri to use for connecting to showdown.
        save_logs: Whether to save logs for each battle.
        save_json: Whether to save json dumps for each battle.
        logged_in: Whether we have logged in to showdown yet.
        last_search: The last updatesearch message we received.
        valid_formats: The list of valid formats for this connection.
        pending_challenges: A dictionary of pending challenges we have sent, mapping the target user to the format.
        battle_processors: A dictionary of battle processors we have created, mapping the battle id to the processor.
        completed_battles: A dictionary of completed battles we have finished, mapping the battle id to the battle.
        pending_battle_amt: The number of battles we have pending.
        active_battle_amt: The number of battles we have active.

    Raises:
        RuntimeError: If the objective is set to challenge but no users are in the whitelist.
    """

    def __init__(
        self,
        showdown_username: str,
        showdown_password: str,
        target_format: str,
        gametype: Literal["singles", "doubles", "triples"],
        objective: Literal["accept", "challenge", "ladder"],
        whitelist_users: Optional[List[str]] = None,
        max_concurrent_battles: int = 1,
        total_battles: int = 1,
        processor_class: Type[ShowdownProcessor] = ShowdownProcessor,
        showdown_uri: str = "ws://localhost:8000/showdown/websocket",
        save_logs: bool = False,
        save_json: bool = False,
    ) -> None:
        self.showdown_username = showdown_username
        self.showdown_password = showdown_password
        self.target_format = target_format
        self.gametype = gametype
        self.objective = objective

        if self.objective == "challenge" and len(whitelist_users) == 0:
            raise RuntimeError("Objective was set to challenge but no users were in the whitelist!")

        self.whitelist_users = whitelist_users if whitelist_users is not None else []
        self.max_concurrent_battles = max_concurrent_battles
        self.total_battles = total_battles
        self.processor_class = processor_class
        self.showdown_uri = showdown_uri
        self.save_logs = save_logs
        self.save_json = save_json

        # Parameter initialization
        self.logged_in: bool = False
        self.last_search: Optional[Message_updatesearch] = None
        self.valid_formats: List[str] = []

        self.pending_challenges: Dict[str, str] = {}
        self.battle_processors: Dict[str, ShowdownProcessor] = {}
        self.completed_battles: Dict[str, Battle] = {}

        self.pending_battle_amt: int = 0
        self.active_battle_amt: int = 0

    async def launch_connection(
        self, session: ClientSession
    ) -> AsyncGenerator[Tuple[ProgressState, Union[BattleState, ConnectionTermination, None]], AnyChoice]:
        """Launch the connector as an async generator.

        Tip:
            This function is an async generator that:
            * yields BattleState
            * accepts AnyChoice as asend (See AnyChoice type alias for options)

            You should use this generator by calling `asend` on it, and then passing the action you want to take. If
            no action is needed at the time, this would mean sending None.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.

        Yields:
            Tuple[ProgressState, Union[BattleState, ConnectionTermination, None]]:
                * ProgressState: The current progress state of the connection
                * Union[BattleState, ConnectionTermination, None]: The current data for this progress state
        """
        conn_term = None

        async with session.ws_connect(self.showdown_uri) as ws:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    message: str = msg.data

                    if message[0] == ">" and "battle" in message:
                        # In this case this is a battle message block
                        battle_id = message.strip().split("\n")[0][1:]

                        for m in message.strip().split("\n")[1:]:
                            progress_state, data = await self.handle_battle_message(session, ws, battle_id, m)

                            if data is None:
                                continue

                            action = yield progress_state, data
                            conn_term = await self.process_action(ws, progress_state, action, battle_id)
                            if conn_term is not None:
                                break
                    elif message[0] == "|":
                        # In this case this is a standard message block
                        for m in message.strip().split("\n"):
                            (
                                progress_state,
                                conn_term,
                            ) = await self.handle_general_message(session, ws, m)
                            if conn_term is not None:
                                break

                            action = yield progress_state, None
                            conn_term = await self.process_action(ws, progress_state, action)
                            if conn_term is not None:
                                break
                    elif message[0] != ">":
                        # In this case this is a global message block
                        progress_state, conn_term = await self.handle_general_message(session, ws, f"||{message}")
                        if conn_term is not None:
                            break

                        action = yield progress_state, None
                        conn_term = await self.process_action(ws, progress_state, action)
                        if conn_term is not None:
                            break
                    else:
                        continue

                    if conn_term is not None:
                        yield ProgressState.FULL_END, conn_term
                        break
                else:
                    # We should never see a websocket error from showdown
                    # If we do see one, we should end and return the error information
                    yield ProgressState.FULL_END, ConnectionTermination(
                        code=ConnectionTerminationCode.CONNECTION_ERROR,
                        message=msg.data,
                    )
                    break

    async def handle_general_message(
        self, session: ClientSession, ws: ClientWebSocketResponse, message: str
    ) -> Tuple[ProgressState, Optional[ConnectionTermination]]:
        """Handle a general message given by the showdown server.

        This ranges from login strings to battle requests. This is where our administrative tasks should be done.
        Battle-specific tasks (other than original creation) should be handled as part of `handle_battle_message`

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            ws (ClientWebSocketResponse): The websocket connection to showdown.
            message (str): The message to handle.

        Returns:
            Tuple[ProgressState, Optional[ConnectionTermination]]:
                * ProgressState: The current progress state of the connection
                * Optional[ConnectionTermination]: Any connection termination information, if needed
        """
        msg = Message.from_message(message)

        if msg.MTYPE == MType.updateuser:
            self.logged_in = msg.NAMED

            if self.logged_in and self.last_search is not None:
                conn_term = await self.handle_updatesearch(session, ws, self.last_search)
                if conn_term is not None:
                    return ProgressState.FULL_END, conn_term
        elif msg.MTYPE == MType.updatesearch:
            if self.objective == "ladder":
                self.pending_battle_amt = len(msg.SEARCHING)
            self.active_battle_amt = 0 if msg.GAMES is None else len(msg.GAMES)

            if self.logged_in:
                conn_term = await self.handle_updatesearch(session, ws, msg)
                if conn_term is not None:
                    return ProgressState.FULL_END, conn_term
            else:
                self.last_search = msg
        elif msg.MTYPE == MType.formats:
            self.valid_formats = [f.lower().replace("[", "").replace("]", "").replace(" ", "") for f in msg.FORMATS]
        elif msg.MTYPE == MType.challstr:
            try:
                await self.send_login(session, ws, msg)
            except Exception as ex:
                return ProgressState.FULL_END, ConnectionTermination(
                    code=ConnectionTerminationCode.SETUP_ERROR, message=str(ex)
                )
        elif msg.MTYPE == MType.pm:
            # For whatever reason showdown seems to use pms for challenge requests, so we
            # need to check this for any pending challenges we've sent/received
            pass
        else:
            # This is unlikely to be a bug since we only care about battle-related things in this class
            # However, for debugging purposes it might be nice to log unexpected messages, or to expand the
            # elif chain to include more types and manually pass so that it is clear they are unneeded
            pass

        return ProgressState.NO_ACTION, None

    async def handle_updatesearch(
        self, session: ClientSession, ws: ClientWebSocketResponse, message: Message_updatesearch
    ) -> Optional[ConnectionTermination]:
        """Handle the updatesearch message.

        This is one of the main objective-processing points, the other being `pm`.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            ws (ClientWebSocketResponse): The websocket connection to showdown.
            message (Message_updatesearch): The updatesearch message to handle.

        Returns:
            Optional[ConnectionTermination]: Any connection termination information, if needed
        """
        if len(self.completed_battles.keys()) >= self.total_battles and message.GAMES is None:
            # In this case we've completed the needed amount and all games are over
            return ConnectionTermination(
                code=ConnectionTerminationCode.OBJECTIVE_COMPLETE, message="REQUIRED NUMBER OF GAMES COMPLETED"
            )
        elif len(self.completed_battles.keys()) >= self.total_battles:
            # In this case we've somehow completed the necessary amt of battles but not all games are over?
            return None
        elif self.pending_battle_amt + self.active_battle_amt >= self.max_concurrent_battles:
            # In this case we already have too many concurrent games, so we skip creating any new ones
            return None

        if self.objective == "accept":
            # if we're just trying to accept challenges, we don't want to initiate anything ourselves
            pass
        elif self.objective == "challenge":
            # TODO: Add support for multiple formats
            for u in self.whitelist_users:
                if u not in self.pending_challenges.keys():
                    await ws.send_str(f"|/challenge {u}, {self.target_format}")
                    self.pending_challenges[u] = self.target_format
                    self.pending_battle_amt += 1
                    break
        elif self.objective == "ladder":
            # We can ladder as long as we don't already have an ongoing or searching match for this format
            # We can also ladder once per format simulatneously, though for now we stick to just one format
            # TODO: Add support for multi-format searching instead of only one format

            if self.target_format not in message.SEARCHING and (
                message.GAMES is None or all([self.target_format not in g for g in message.GAMES])
            ):
                # in this case we aren't already searching for a match in this format, so we can submit a ladder request
                await ws.send_str(f"|/search, {self.target_format}")
                self.pending_battle_amt += 1

        return None

    async def send_login(
        self,
        session: ClientSession,
        ws: ClientWebSocketResponse,
        message: Message_challstr,
    ) -> None:
        """Handle the challengestr login flow.

        Sends a request to showdown's official login site with the user/pass/challstr to get a login token first
        Then sends that login token to the target showdown websocket to validate username selection

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            ws (ClientWebSocketResponse): The websocket connection to showdown.
            message (Message_challstr): The challengestr message to handle.

        Raises:
            RuntimeError: If the login fails
        """
        # TODO: Do some better char escaping for the user/pass
        params = {
            "name": quote(self.showdown_username).replace("-", "%2D"),
            "pass": quote(self.showdown_password),
            "challstr": message.CHALLSTR.strip(),
        }

        uri_str = (
            "https://play.pokemonshowdown.com/api/login?"
            f"name={params['name']}&pass={params['pass']}&challstr={params['challstr']}"
        )

        url = URL(
            uri_str,
            encoded=True,
        )

        async with session.post(url) as resp:
            r = await resp.text()
            r = json.loads(r[1:])

            if "assertion" not in r.keys():
                raise RuntimeError(f"Failed to log in: {r}")

            token = r["assertion"]

        await ws.send_str(f"|/trn {self.showdown_username},0,{token.strip()}")

    async def handle_battle_message(
        self,
        session: ClientSession,
        ws: ClientWebSocketResponse,
        battle_id: str,
        message: str,
    ) -> Tuple[ProgressState, Optional[BattleState]]:
        """Handle battle-specific messages.

        Mostly serves to pass messages to the corresponding processor for the battle.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            ws (ClientWebSocketResponse): The websocket connection to showdown.
            battle_id (str): The id of the battle to handle.
            message (str): The message to handle.

        Returns:
            Tuple[ProgressState, Optional[BattleState]]: The resulting progress state and battle state, if any.
                If the battle has already concluded with a win/loss, the battle state will be None.
        """
        if battle_id in self.completed_battles.keys():
            return ProgressState.NO_ACTION, None

        bp = self.battle_processors.get(
            battle_id,
            self.processor_class(session, self.showdown_username, self.showdown_username),
        )

        progress_state = await bp.process_message(message_str=message)

        self.battle_processors[battle_id] = bp

        return progress_state, bp.battle.battle_states[-1]

    async def process_action(
        self,
        ws: ClientWebSocketResponse,
        progress_state: ProgressState,
        action: AnyChoice,
        battle_id: Optional[str] = None,
    ) -> Optional[ConnectionTermination]:
        """Process the action based on the current progress state, closing any connections as needed.

        All action verification is handled later in `submit_action`, this just looks at progress_state and determines
        what to do.

        Args:
            ws (ClientWebSocketResponse): The websocket connection to showdown.
            progress_state (ProgressState): The current progress state of the connection
            action (AnyChoice): The action to submit.
            battle_id (Optional[str], optional): The id of the battle to submit the action to, if any.

        Returns:
            Optional[ConnectionTermination]:
        """
        if progress_state == ProgressState.FULL_END:
            # Process any final logging / closing operations needed if any (e.g. resign from all ongoing battles)
            # TODO

            return ConnectionTermination(code=ConnectionTerminationCode.OBJECTIVE_COMPLETE)
        elif progress_state == ProgressState.GAME_END:
            # Process game end movement
            if self.save_logs:
                os.makedirs(f"logs/{self.target_format}/", exist_ok=True)
                with open(f"logs/{self.target_format}/{battle_id}.log", "w", encoding="utf8") as f:
                    f.writelines([f"{line}\n" for line in self.battle_processors[battle_id].log])

            if self.save_json:
                os.makedirs(f"logs/{self.target_format}/", exist_ok=True)
                with open(f"logs/{self.target_format}/{battle_id}.json", "w", encoding="utf8") as f:
                    json.dump(self.battle_processors[battle_id].battle.model_dump(mode="json"), f)

            self.completed_battles[battle_id] = self.battle_processors.pop(battle_id).battle
            return None
        else:
            # Verify/Submit the action to pokemon showdown
            try:
                return await self.submit_action(ws, progress_state, action, battle_id=battle_id)
            except AssertionError as ex:
                return ConnectionTermination(code=ConnectionTerminationCode.INVALID_CHOICE, message=f"{type(ex)}: {ex}")
            except NotImplementedError as ex:
                return ConnectionTermination(code=ConnectionTerminationCode.INVALID_CHOICE, message=f"{type(ex)}: {ex}")
            except Exception as ex:
                return ConnectionTermination(code=ConnectionTerminationCode.OTHER_ERROR, message=f"{type(ex)}: {ex}")

    async def submit_action(
        self,
        ws: ClientWebSocketResponse,
        progress_state: ProgressState,
        action: AnyChoice,
        battle_id: Optional[str] = None,
    ) -> Optional[ConnectionTermination]:
        """Submit an action to the showdown server.

        Note:
            This function will:
            * Verify that the action(s) returned the by the user is valid to submit at this time
            * Submit it to showdown

            This will not check if a given move is a legal move, because that step should be done by the processor
            at choice-build time. This will only check if the action is a valid action-type to submit at this time.

        Args:
            ws (ClientWebSocketResponse): The websocket connection to showdown.
            progress_state (ProgressState): The current progress state of the connection
            action (AnyChoice): The action to submit.
            battle_id (Optional[str], optional): The id of the battle to submit the action to, if any.

        Returns:
            Optional[ConnectionTermination]: Any connection termination information, if needed
        """
        # Handle quit and resign options first since they are the simple cases
        if is_bearable(action, QuitChoice):
            # Process all-resignation decision
            # TODO: Resign from all active games / close anything else as needed

            return ConnectionTermination(
                code=ConnectionTerminationCode.OTHER_ERROR,
                message="USER REQUESTED SHUTDOWN",
            )
        if is_bearable(action, ResignChoice):
            # Process resignation decision
            # TODO: Resign from just this game, don't return ConnectionTermination
            assert (
                battle_id is not None
            ), "battle_id was None but you sent a resignation! When not in a battle, send QuitChoice instead!"
            return

        assert is_bearable(action, AnyChoice)

        action_str = f"{battle_id}|/choose "

        if progress_state == ProgressState.TEAM_ORDER:
            # Check valid formatting for team order submission:
            assert is_bearable(action, TeamOrderChoice), f"action was not a valid TeamOrderChoice!\n{action}"
            assert (
                battle_id is not None
            ), "battle_id was None! This likely means a bug in websocketconnector, not your code!"

            # TeamOrderChoice can either be a TeamChoice or a DefaultChoice, easy
            action_str += action.to_showdown()
        elif progress_state == ProgressState.SWITCH:
            # Check valid formatting for force-switch submission:
            assert is_bearable(action, ForceSwitchChoice), f"action was not a valid ForceSwitchChoice!\n{action}"
            assert (
                battle_id is not None
            ), "battle_id was None! This likely means a bug in websocketconnector, not your code!"

            # ForceSwitchChoice can either be a List of either Switch/Pass choices, or a single DefaultChoice
            if is_bearable(action, list):
                assert (
                    (self.gametype == "singles" and len(action) == 1)
                    or (self.gametype == "doubles" and len(action) == 2)
                    or (self.gametype == "triples" and len(action) == 3)
                ), f"gametype is {self.gametype}, but you sent {len(action)} commands!"
                action_str += ",".join([sub_action.to_showdown() for sub_action in action])
            else:
                action_str += action.to_showdown()
        elif progress_state == ProgressState.MOVE:
            # Check valid formatting for move submission:
            assert is_bearable(action, MoveDecisionChoice), f"action was not a valid MoveDecisionChoice!\n{action}"
            assert (
                battle_id is not None
            ), "battle_id was None! This likely means a bug in websocketconnector, not your code!"

            # ForceSwitchChoice can either be a List of Move/Switch/Pass choices, or a single DefaultChoice
            if is_bearable(action, list):
                assert (
                    (self.gametype == "singles" and len(action) == 1)
                    or (self.gametype == "doubles" and len(action) == 2)
                    or (self.gametype == "triples" and len(action) == 3)
                ), f"gametype is {self.gametype}, but you sent {len(action)} commands!"
                action_str += ",".join([sub_action.to_showdown() for sub_action in action])
            else:
                action_str += action.to_showdown()
        else:
            assert action is None
            return

        await self.battle_processors[battle_id].process_action(action, action_str)
        await ws.send_str(action_str)
