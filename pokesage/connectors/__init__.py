"""Connector classes for PokeSage.

Classes:
    Connector: Abstract Connector class for other connector classes to implement with their connection functions.
    WebsocketConnector: Connector class for connecting to a websocket server.
    ConnectionTerminationCode: Enum for the possible connection termination codes.
    ConnectionTermination: Class for storing a connection termination code and message.
"""

from .abstractconnector import ConnectionTermination, ConnectionTerminationCode, Connector
from .websocketconnector import WebsocketConnector
