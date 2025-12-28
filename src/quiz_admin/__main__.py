import sys
import asyncio
from typing import Any
import aioconsole
from websockets import connect, ClientConnection
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from quiz_common.models import Quiz
import json


async def send_receive_messages(uri: str, quiz_data: dict[str, Any]):
    async with connect(uri) as ws:
        await ws.send(json.dumps(quiz_data))  # Inital sending the whole quiz data to the server

        await asyncio.gather(
            asyncio.create_task(send_messages(ws)),
            asyncio.create_task(receive_messages(ws)),
        )


async def send_messages(ws: ClientConnection):
    while True:
        user_input = await aioconsole.ainput("Send 'y' for the next question\n")
        if user_input:
            await ws.send(user_input)


async def receive_messages(ws: ClientConnection):
    while True:
        response = await ws.recv()
        print(response)


def main():
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} <url> <quiz file>")

    server_url = f"ws://{sys.argv[1]}/admin"

    try:
        quiz_file = sys.argv[2]

        with open(quiz_file, encoding="utf-8") as file:
            quiz_data = YAML(typ="safe").load(file)

        Quiz(**quiz_data)  # Load to validate a structure

    except (OSError, YAMLError) as e:
        sys.exit(str(e))
    except TypeError as e:
        sys.exit(f"TODO: better error handling\n{str(e)}")

    try:
        asyncio.get_event_loop().run_until_complete(
            send_receive_messages(server_url, quiz_data)
        )
    except OSError:
        sys.exit("Admin: cannot reach server")
    except ConnectionClosedOK as e:
        print(e.reason)
    except ConnectionClosedError:
        print("Admin: server disconected")
    except KeyboardInterrupt:
        print("\nAdmin: exit")
        sys.exit()
