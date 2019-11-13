#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:
Marcus Voß (m.voss@laposte.net)

Description:
POC script to communicate with an ublox F9P GNSS receiver.
"""

#import serial
#import numpy as np
import time
import json 


from ubx_receiver import UBX_receiver, UBX_message, NMEA_message

def serial_gnss(port, baud):
    try:
        receiver = UBX_receiver(port, baud)
    except OSError as err:
        print(f"Error while opening serial port: {err}")
        return
    print("Starting to listen for UBX packets")
    receiver.ubx_config_disable_all()
    # receiver.ubx_config_enable("RAWX_UART1","SFRBX_UART1")
    receiver.ubx_config_enable("GGA_UART1", "RAWX_UART1")
    try:
        while True:
            try:
                msg = receiver.parse()
                if (isinstance(msg, str)):
                    print(f"error: {msg}")
                elif (isinstance(msg, UBX_message)):
                    print(msg)
                elif (isinstance(msg, NMEA_message)):
                    print(msg)
            except (ValueError, IOError) as err:
                print(err)
            time.sleep(0.01)

    finally:
        del receiver #clean up serial connection

if __name__ == "__main__":
    port = "COM6"
    baud = 115200
    serial_gnss(port,baud)