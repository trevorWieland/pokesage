"""Contains the Processor class for abstracting the processing of battle messages.

This class is intentionally vague about message formatting, and supports any string input message, so long as in your
implementation, you can create a valid BattleState from it.
"""

from abc import ABC, abstractmethod
from typing import Type
from enum import Enum, unique
from aiohttp import ClientSession

from ..battle.battle import Battle
from ..battle.state import BattleState
from ..battle.choices import AnyChoice


@unique
class ProgressState(Enum):
    """Enum for representing the state of the battle after processing a message."""

    NO_ACTION = 0
    TEAM_ORDER = 1
    MOVE = 2
    SWITCH = 3
    GAME_END = 4
    FULL_END = 5


class Processor(ABC):
    """Processes incoming `messages` and updates the BattleState accordingly.

    A Processor should be implemented to handle a specific format of messages (Showdown, GBA emulator, etc.)
    The Battle/BattleState that gets updated SHOULD NOT contain anything directly tied to the formatting.

    Attributes:
        BATTLE_CLASS (Type[Battle]): The Battle class to use for this processor.
        BATTLE_STATE_CLASS (Type[BattleState]): The BattleState class to use for this processor.
        battle_id (str): The id of the battle to process messages for.
        session (ClientSession): The aiohttp session to use for any http requests.
        battle (Battle): The Battle object to update with each message.
        log (list): A list of messages that have been processed, for logging purposes.

    Args:
        session (ClientSession): The aiohttp session to use for any http requests.
        battle_id (str): The id of the battle to process messages for.
        player_name (str): The name of the player to use for this battle.
    """

    BATTLE_CLASS: Type[Battle] = Battle
    BATTLE_STATE_CLASS: Type[BattleState] = BattleState

    def __init__(self, session: ClientSession, battle_id: str, player_name: str) -> None:
        self.battle_id = battle_id
        self.session = session

        self.battle: Battle = self.BATTLE_CLASS(battle_actions=[], battle_states=[], player_name=player_name)
        self.log = []

    @abstractmethod
    async def process_message(self, message_str: str) -> ProgressState:
        """Process the given message and return a ProgressState accordingly.

        Remember, everything that you want to keep should be stored in self.battle / a state inside of
        `self.battle.battle_states`!
        self.log should only be used for troubleshooting measures, or other logging purposes

        Args:
            message_str (str): The message to process.

        Returns:
            ProgressState: The state of the battle after processing the message.
        """

    @abstractmethod
    async def process_action(self, action: AnyChoice, action_str: str) -> None:
        """Take an action given by the sage and process it.

        This shouldn't *submit* the action to the game, but instead log the action as part of the state

        Args:
            action (AnyChoice): The action to process.
            action_str (str): The string representation of the action.
        """
