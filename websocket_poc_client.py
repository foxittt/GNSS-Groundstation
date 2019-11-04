#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: 
Marcus Voß (m.voss@laposte.net)

Description:
POC websocket client that automatically reconnects and should prevent message loss.
"""


import asyncio
import websockets
import datetime
import json
import sys

from collections import deque
from ubx_receiver import UBX_receiver, UBX_message, NMEA_message

DATA = deque()
SERVER = None

SERIAL_PORT = "COM5"
BAUDRATE = 115200
WEBSOCKET_ADDRESS = "ws://localhost:5678"


def handle_msg(msg):
    """prints out the received message"""
    print(f"> {msg}")


async def gather_data():
    receiver = UBX_receiver(SERIAL_PORT, BAUDRATE)
    try:
        print("Starting to listen for UBX packets")
        receiver.ubx_config_disable_all()
        # receiver.ubx_config_enable("RAWX_UART1","SFRBX_UART1")
        receiver.ubx_config_enable("GGA_UART1")
        while True:
            try:
                msg = receiver.parse()
                if (isinstance(msg, str)):
                    print(f"error: {msg}")
                elif (isinstance(msg, UBX_message)):
                    print(msg)
                    DATA.append(str(msg))
                elif (isinstance(msg, NMEA_message)):
                    print(msg)
                    DATA.append(str(msg))
            except (ValueError, IOError) as err:
                print(err)
            await asyncio.sleep(0)

    finally:
        del receiver #clean up serial connection


async def gather_placeholder_data():
    counter = 0
    print("starting task: gather_data")
    while True:
        counter += 1
        now = str(counter)
        DATA.append(now)
        print(f"length: {len(DATA)}")
        print(f"size: {sys.getsizeof(DATA)}")
        await asyncio.sleep(1)


async def send_data():
    global SERVER
    print("starting task: send_data")
    while True:
        if len(DATA) > 0 and SERVER != None:
            msg = DATA[0]  # get leftmost item
            try:
                print(f"< {msg}")
                await SERVER.send(msg)
                print("send")
                answ = await SERVER.recv()
                print(f"> {answ}")
                DATA.popleft()
            except:
                print("message failed!")
                SERVER = None
        await asyncio.sleep(0)


async def listen_forever():
    """
    Basic Loop that listens for incoming websocket messages and reconnects in case of an error.
    General design based on https://github.com/aaugustin/websockets/issues/414
    """
    global SERVER
    print("starting task: listen_forever")
    while True:
        # outer loop restarted every time the connection fails
        SERVER = None
        print("Connecting to websocket server...")
        connection = websockets.connect(WEBSOCKET_ADDRESS)
        try:
            SERVER = await asyncio.wait_for(connection, 5)
        except (OSError, websockets.exceptions.InvalidMessage) as e:
            print("Connection unsuccessful:", e)
            await asyncio.sleep(5)
            continue
        except:
            print("Connection timeout:")
            await asyncio.sleep(5)
            continue

        print("Connected!")
        while True:
            # listener loop
            if len(DATA) > 0 and SERVER != None:
                try:
                    msg = DATA[0]  # get leftmost item
                    print(f"< {msg}")
                    await SERVER.send(msg)
                    answ = await SERVER.recv()
                    print(f"> {answ}")
                    DATA.popleft()
                except websockets.exceptions.ConnectionClosed:
                    print("Connection lost")
                    await asyncio.sleep(1)
                    break  # inner loop
            else:
                await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.get_event_loop().create_task(gather_data())
    # asyncio.get_event_loop().create_task(send_data())
    asyncio.get_event_loop().create_task(listen_forever())
    asyncio.get_event_loop().run_forever()
