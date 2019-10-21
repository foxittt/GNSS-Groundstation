#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:
Marcus Voß (m.voss@laposte.net)

Description:
POC script to communicate with an ublox F9P GNSS receiver.
"""

import serial
import time
import numpy as np


from ubx_helper import ubx_config_helper, ubx_parser
SERIAL_PORT = "COM6"
BAUDRATE = 115200


ubx = ubx_config_helper()
parser = ubx_parser()

port = serial.Serial(SERIAL_PORT, BAUDRATE)  # open serial port
time.sleep(1)

# Turn off all NMEA messages but the GGA message
print("sending disable msg")
msg_disable = ubx.ubx_config_disable(
    "GLL_UART1", "GSV_UART1", "GGA_UART1", "RMC_UART1", "GSA_UART1", "VTG_UART1")
print(list(msg_disable))
port.write(msg_disable)

print("sending enable msg")
msg_enable = ubx.ubx_config_enable("RAWX_UART1")
print(list(msg_enable))
port.write(msg_enable)

# ser.write(ubx.ubx_config_disable_all())

print("Starting to listen for UBX packets")

try:
    while True:
        try:
           parser.add_byte(port.read())
        except (ValueError, IOError) as err:
            print(err)

finally:
    port.close()
