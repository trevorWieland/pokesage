from abc import ABC, abstractmethod
from typing import Type
from enum import Enum, unique
from aiohttp import ClientSession

from ..battle.battle import Battle
from ..battle.state import BattleState


@unique
class ProgressState(Enum):
    NO_ACTION = 0
    TEAM_ORDER = 1
    MOVE = 2
    SWITCH = 3
    GAME_END = 4
    FULL_END = 5


class Processor(ABC):
    """
    Processes incoming `messages` and updates the BattleState accordingly.

    A Processor should be implemented to handle a specific format of messages (Showdown, GBA emulator, etc.)
    The Battle/BattleState that gets updated SHOULD NOT contain anything directly tied to the formatting.
    """

    BATTLE_CLASS: Type[Battle] = Battle
    BATTLE_STATE_CLASS: Type[BattleState] = BattleState

    def __init__(self, battle_id: str, session: ClientSession) -> None:
        """
        Initialize the Processor with a battle_id, as well as the session to use for any http requests
        """

        self.battle_id = battle_id
        self.session = session

        self.battle: Battle = self.BATTLE_CLASS(battle_actions=[], battle_states=[])

        self.log = []

    @abstractmethod
    async def process_message(self, message_str: str) -> ProgressState:
        """
        This function shouild process the given message and return a ProgressState accordingly.

        Remember, everything that you want to keep should be stored in self.battle / a state inside self.battle.battle_states!
        self.log should only be used for troubleshooting measures, or other logging purposes
        """
