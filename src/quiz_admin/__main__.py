"""
Main entry point for the quiz admin client.

This module allows an admin to send a quiz to the server and interactively
control the quiz session via a websocket connection.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import aioconsole
from quiz_common.models import Quiz
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from websockets import ClientConnection, connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


async def send_receive_messages(uri: str, quiz_data: dict[str, Any]) -> None:
    """
    Establish a websocket connection to the server.

    Send the quiz data and concurrently handle sending and receiving messages.
    """
    async with connect(uri) as ws:
        # Initial sending the whole quiz data to the server
        await ws.send(json.dumps(quiz_data))
        await asyncio.gather(send_messages(ws), receive_messages(ws))


async def send_messages(ws: ClientConnection) -> None:
    """Prompt the user for input and send messages to the server over the websocket."""
    while True:
        user_input = await aioconsole.ainput("Send 'y' for the next question\n")
        if user_input:
            await ws.send(user_input)


async def receive_messages(ws: ClientConnection) -> None:
    """Receive messages from the server and print them to the console."""
    while True:
        response = await ws.recv()
        print(response)


def main() -> None:
    """
    Script entry point.

    Parse arguments, load the quiz YAML file, validate it, and start the websocket
    communication with the server.
    """
    if len(sys.argv) != 3:  # noqa: PLR2004
        sys.exit(f"Usage: {sys.argv[0]} <url> <quiz file>")

    server_url = f"ws://{sys.argv[1]}/admin"

    try:
        quiz_file = sys.argv[2]

        with Path(quiz_file).open(encoding="utf-8") as file:
            quiz_data = YAML(typ="safe").load(file)

        Quiz(**quiz_data)  # Load to validate a structure

    except (OSError, YAMLError) as e:
        sys.exit(str(e))
    except TypeError as e:
        sys.exit(f"TODO: better error handling\n{e}")

    try:
        asyncio.run(send_receive_messages(server_url, quiz_data))
    except OSError as e:
        sys.exit(f"Admin: cannot reach server\n{e}")
    except ConnectionClosedOK as e:
        print(e.reason)
    except ConnectionClosedError as e:
        sys.exit(f"Admin: server disconected\n{e}")
    except KeyboardInterrupt:
        sys.exit("\nAdmin: exit")
