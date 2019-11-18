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
import itertools
#import datetime
import time
import json
#import sys
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)

from collections import deque
from ubxReceiver.ubx_receiver import UBX_receiver, UBX_message, NMEA_message

DATA = deque()
SERVER = None

SERIAL_PORT = "COM3"
BAUDRATE = 115200
USERNAME = "MVO"
PASSWORD = "e5W7Avnr6NgUiZ"
WEBSOCKET_PORT = "5678"
WEBSOCKET_SERVER ="10.0.20.237"
WEBSOCKET_ADDRESS = f"ws://{USERNAME}:{PASSWORD}@{WEBSOCKET_SERVER}:{WEBSOCKET_PORT}"

msgID = itertools.count()

def handle_msg(msg):
    """prints out the received message"""
    print(f"> {msg}")


async def gather_data():
    while True:
        global msgID
        logging.info("Attempting serial connection to UBX-GNSS receiver")
        try:
            receiver = UBX_receiver(SERIAL_PORT, BAUDRATE)
        except Exception as err: 
            logging.error(f"serial connection not successfull! {err}")
            await asyncio.sleep(5)
            continue
            
        try:
            logging.info("Starting to listen for UBX packets")
            receiver.ubx_config_disable_all()
            receiver.ubx_config_enable("GGA_UART1", "RAWX_UART1", "SFRBX_UART1")
            while True:
                try:
                    msg = receiver.parse()
                except Exception as err:
                    logging.error(f"Serial connection Error: {err}")
                    break
                try:
                    if (isinstance(msg, str)):
                        logging.error(f"received error: {msg}")
                    elif (isinstance(msg, UBX_message)):
                        constructed_message = {
                            "msgID": next(msgID),
                            "type": "GNSS",
                            "protocol": "UBX",
                            "timestamp": time.time(),
                            "class": msg.cl,
                            "id": msg.id,
                            "payload": list(msg.payload),
                            "raw": list(msg.raw_data)
                        }
                        DATA.append(constructed_message)
                    elif (isinstance(msg, NMEA_message)):
                        constructed_message = {
                            "msgID": next(msgID),
                            "type": "GNSS",
                            "protocol": "NMEA",
                            "timestamp": time.time(),
                            "talker": msg.talker_id+msg.msg_type,
                            "data": msg.data,
                            "raw": msg.raw_data
                        }
                        DATA.append(constructed_message)
                except (ValueError, IOError) as err:
                    logging.error(err)
                await asyncio.sleep(0.01)

        finally:
            del receiver  # clean up serial connection


async def gather_placeholder_data():
    counter = 0
    logging.debug("starting task: gather_data")
    while True:
        counter += 1
        now = str(counter)
        DATA.append(now)
       
        await asyncio.sleep(1)

async def report_queque_length():
    last_len = 0
    while True:
        queque_length = len(DATA)
        if queque_length != last_len:
            logging.info(f"queque length: {queque_length}")
            last_len = queque_length
        else:
            await asyncio.sleep(1)

async def listen_forever():
    """
    Basic Loop that listens for incoming websocket messages and reconnects in case of an error.
    General design based on https://github.com/aaugustin/websockets/issues/414
    """
    global SERVER
    logging.debug("starting task: listen_forever")
    while True:
        # outer loop restarted every time the connection fails
        SERVER = None
        logging.info("Connecting to websocket server...")
        connection = websockets.connect(WEBSOCKET_ADDRESS)
        try:
            SERVER = await asyncio.wait_for(connection, 5)
        except (OSError, websockets.exceptions.InvalidMessage) as err:
            logging.error(f"websocket connection unsuccessful: {err}")
            await asyncio.sleep(5)
            continue
        except websockets.exceptions.InvalidStatusCode as err:
            logging.error(f"websocket connection refused: {err}")
            await asyncio.sleep(5)
            continue
        except asyncio.TimeoutError as err:
            logging.error(f"websocket connection timeout: {err}")
            await asyncio.sleep(5)
            continue
        except Exception as err:
            logging.error(f"websocket connection failed for unknown reason: {err}")
            await asyncio.sleep(5)
            continue
        logging.info("websocket connected!")
        while True:
            # listener loop
            if len(DATA) > 0 and SERVER != None:
                try:
                    msg = json.dumps(DATA[0])  # get leftmost item
                    logging.debug(f"> {msg}")
                    await SERVER.send(msg)
                    answ = await SERVER.recv()
                    logging.info(f"< {answ}")
                    DATA.popleft()
                except websockets.exceptions.ConnectionClosed:
                    logging.error("websocket connection lost")
                    await asyncio.sleep(1)
                    break  # inner loop
            else:
                await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.get_event_loop().create_task(gather_data())
    asyncio.get_event_loop().create_task(report_queque_length())
    asyncio.get_event_loop().create_task(listen_forever())
    asyncio.get_event_loop().run_forever()
