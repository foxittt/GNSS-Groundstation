

import asyncio
import websockets
import datetime
import sys

from collections import deque

DATA = deque()
SERVER = None


def handle_msg(msg):
    """prints out the received message"""
    print(f"< {msg}")


async def gather_data():
    while True:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        DATA.append(now)
        #print(f"length: {len(DATA)}")
        #print(f"size: {sys.getsizeof(DATA)}")
        await asyncio.sleep(1)


async def send_data():
    while True:
        if len(DATA) > 0 and SERVER != None:
            SERVER.send(DATA.pop())
            print(f"length: {len(DATA)}")


async def listen_forever():
    """
    Basic Loop that listens for incoming websocket messages and reconnects in case of an error.
    General design based on https://github.com/aaugustin/websockets/issues/414
    """
    while True:
        # outer loop restarted every time the connection fails
        print("Connecting to websocket server...")
        try:
            async with websockets.connect("ws://localhost:5678") as ws:
                SERVER = ws
                print("Connected!")
                while True:
                    # listener loop
                    try:
                        handle_msg(await ws.recv())
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection lost")
                        SERVER = None
                        await asyncio.sleep(1)
                        break  # inner loop
        except OSError as e:
            print("Connection unsuccessful:", e)
            await asyncio.sleep(5)
        except Exception as e:
            print("Connection Error", e.__class__, e)
            continue


if __name__ == "__main__":
    asyncio.get_event_loop().create_task(gather_data())
    asyncio.get_event_loop().create_task(send_data())
    asyncio.get_event_loop().create_task(listen_forever())
    asyncio.get_event_loop().run_forever()
