#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:
Marcus Voß (m.voss@laposte.net)

Description:
POC websocket server that prints every message it receives.
"""

import asyncio
import json
import websockets
import logging
logging.basicConfig(level=logging.INFO)


CLIENTS = set()
WEBSOCKET_IP = "127.0.0.1"  # "10.0.20.227"
WEBSOCKET_PORT = 5678
USERNAME = "MVO"
PASSWORD = "e5W7Avnr6NgUiZ"


async def authenticate(username, password):
    reason = "unknown reason"
    if username == USERNAME:
        if password == PASSWORD:
            return True
        else:
            reason = f"wrong password ({password})"
    else:
        reason = f"wrong username ({username})"
    logging.info(f"client refused: {reason}")
    return False


async def register(websocket):
    logging.info("client connected {websocket}")
    CLIENTS.add(websocket)


async def unregister(websocket):
    logging.info("client disconnected {websocket}")
    CLIENTS.remove(websocket)


async def server(websocket, path):
    logging.debug("websocket: {websocket}")
    logging.debug("path: {path}")
    await register(websocket)
    try:
        async for message in websocket:
            msg = json.loads(message)
            uuid = websocket.request_headers["uuid"] or "unknown"
            msgID = msg.get("msgID")
            logging.info(f"{uuid}> {msgID}")
            await websocket.send(f"OK {msgID}")
    finally:
        await unregister(websocket)
logging.info("waiting for clients...")
start_server = websockets.serve(server, WEBSOCKET_IP, WEBSOCKET_PORT, create_protocol=websockets.basic_auth_protocol_factory(
    realm="TUB", check_credentials=authenticate)
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
