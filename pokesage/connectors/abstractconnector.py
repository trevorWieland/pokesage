from abc import ABC, abstractmethod

from ..processors import Processor
from ..states.battlestate import BattleState
from ..states.choices import AnyChoice

from aiohttp import ClientSession
from enum import Enum, unique
from typing import AsyncGenerator, Union, List, Optional, Tuple
from pydantic import BaseModel, Field


@unique
class ConnectionTerminationCode(Enum):
    OBJECTIVE_COMPLETE = 0
    INVALID_CHOICE = 1
    SETUP_ERROR = 2
    CONNECTION_ERROR = 3
    PROCESSOR_ERROR = 4
    OTHER_ERROR = 5


@unique
class ProgressState(Enum):
    NO_ACTION = 0
    TEAM_ORDER = 1
    MOVE = 2
    SWITCH = 3
    GAME_END = 4
    FULL_END = 5


class ConnectionTermination(BaseModel):
    """
    A returned object by the Connector's launch_connection function.
    """

    code: ConnectionTerminationCode = Field(..., description="The status code for this termination")
    message: Optional[str] = Field(None, description="An optional extra string message about this termination")


class Connector(ABC):
    """
    An abstract class defining function headers mandatory for connector objects

    Since the entrypoint for the user is the sage class, the sage class should create the aiohttp session,
    so that all downstream connections use the same async connection pool
    """

    @abstractmethod
    async def launch_connection(
        self, session: ClientSession
    ) -> AsyncGenerator[Tuple[ProgressState, Union[BattleState, ConnectionTermination, None]], AnyChoice]:
        """
        This function should be a generator that:
        - yields BattleState
        - accepts Choice as send (See Choice type alias for options)
        - returns a ConnectionTermination (Used when objective complete, or on error state)

        This function should be instantiated by the connection handling subclass, not the sage
        """
