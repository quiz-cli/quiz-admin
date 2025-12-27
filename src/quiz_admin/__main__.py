import sys
import asyncio
import aioconsole
from websockets import connect, ClientConnection
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


async def send_receive_messages(uri: str):
    async with connect(uri) as ws:
        await asyncio.gather(
            asyncio.create_task(send_messages(ws)),
            asyncio.create_task(receive_messages(ws)),
        )


async def send_messages(ws: ClientConnection):
    while True:
        user_input = await aioconsole.ainput()
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
        asyncio.get_event_loop().run_until_complete(
            send_receive_messages(server_url)
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
