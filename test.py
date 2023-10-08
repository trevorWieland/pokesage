import asyncio

from pokesage.connectors import WebsocketConnector
from pokesage.sages import DefaultSage

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

conn = WebsocketConnector("colress-gpt-test1", "sYTANfm=xNn&2e]", "gen9randombattle", "singles", "ladder")
sage = DefaultSage("colressgpt-test-1", conn)

asyncio.run(sage.launch())
