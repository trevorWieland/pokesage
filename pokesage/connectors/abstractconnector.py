"""Abstract Connector class for using any backend."""

from abc import ABC, abstractmethod
from enum import Enum, unique
from beartype.typing import AsyncGenerator, Optional, Tuple, Union

from aiohttp import ClientSession
from pydantic import BaseModel, Field

from ..battle.choices import AnyChoice
from ..battle.state import BattleState
from ..processors import ProgressState


@unique
class ConnectionTerminationCode(Enum):
    """Enum for the possible termination codes for a connection."""

    OBJECTIVE_COMPLETE = 0
    INVALID_CHOICE = 1
    SETUP_ERROR = 2
    CONNECTION_ERROR = 3
    PROCESSOR_ERROR = 4
    OTHER_ERROR = 5


class ConnectionTermination(BaseModel):
    """BaseModel for a connection termination.

    Attributes:
        code: The status code for this termination
        message: An optional extra string message about this termination
    """

    code: ConnectionTerminationCode = Field(..., description="The status code for this termination")
    message: Optional[str] = Field(None, description="An optional extra string message about this termination")


class Connector(ABC):
    """Abstract Connector class for using any backend.

    Since the entrypoint for the user is the sage class, the sage class should create the aiohttp session,
    so that all downstream connections use the same async connection pool
    """

    @abstractmethod
    async def launch_connection(
        self, session: ClientSession
    ) -> AsyncGenerator[Tuple[ProgressState, Union[BattleState, ConnectionTermination, None]], AnyChoice]:
        """Launch the connector as an async generator.

        Tip:
            This function should be an async generator that:
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
