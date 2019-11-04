#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: 
Marcus Voß (m.voss@laposte.net)

Description:
POC websocket server that prints every message it receives.
"""

import asyncio
import websockets

CLIENTS = set()
WEBSOCKET_IP = "localhost"#"10.0.20.227"
WEBSOCKET_PORT = 5678


async def register(websocket):
    print("client connected", websocket)
    CLIENTS.add(websocket)


async def unregister(websocket):
    print("client disconnected", websocket)
    CLIENTS.remove(websocket)


async def server(websocket, path):
    print("websocket:", websocket)
    print("path:", path)
    await register(websocket)
    try:
        async for message in websocket:
            print(f">{message}")
            await websocket.send("OK")
    finally:
        await unregister(websocket)

start_server = websockets.serve(server, WEBSOCKET_IP, WEBSOCKET_PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
