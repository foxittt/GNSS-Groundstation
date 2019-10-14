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
SERIAL_PORT = "COM6"
BAUDRATE = 115200


class ubx_helper:
    config = {
        # ubx-config for UART1
        "GLL": b'\xCA\x00\x91\x20',
        "GSV": b'\xC5\x00\x91\x20',
        "GSA": b'\xC0\x00\x91\x20',
        "RMC": b'\xAC\x00\x91\x20',
        "VTG": b'\xB1\x00\x91\x20'
    }

    def compute_checksum(self, msg):
        '''8-Bit Fletcher Algorithm modelled after ublox documentation. Returns checksum'''
        CK_A = CK_B = 0
        # start at class (byte 2)
        for i in range(2, len(msg)):
            CK_A += msg[i]
            CK_B += CK_A
        # mask to 8bit uint
        CK_A &= 0xFF
        CK_B &= 0xFF
        # convert to bytes
        CK_A = bytes([CK_A])
        CK_B = bytes([CK_B])
        # print("CK_A",CK_A)
        # print("CK_B",CK_B)
        return CK_A+CK_B

    def ubx_msg(self, c, id, payload):
        '''generate a valid ubx message with checksum'''
        sync = b'\xB5\x62'
        print("payload", list(payload))
        length = bytes([len(payload)])
        if (len(length) < 2):
            length += b'\x00'
        msg = sync+c+id+length+payload
        checksum = self.compute_checksum(msg)
        msg += checksum
        return msg

    def ubx_set_val(self, *args):
        '''set ubx config values'''
        if (len(args) % 2 != 0):
            raise ValueError("Number of arguments must be even!")
        c = b'\x06'
        id = b'\x8A'
        payload = b'\x00\x01\x00\x00'
        for arg in args:
            if (type(arg) != bytes):
                arg = bytes([arg])
            payload += arg

        msg = self.ubx_msg(c, id, payload)
        return msg

    def ubx_config_disable(self, *args):
        '''disable ubx messages (multiple strings as argument)'''
        vals = []
        for arg in args:
            vals.append(self.config[arg])
            vals.append(b'\x00')
        return self.ubx_set_val(*vals)

    def ubx_config_enable(self, *args):
        '''enable ubx messages (multiple strings as argument)'''
        vals = []
        for arg in args:
            vals.append(self.config[arg])
            vals.append(b'\x01')
        return self.ubx_set_val(*vals)


ubx = ubx_helper()
ser = serial.Serial(SERIAL_PORT, BAUDRATE)  # open serial port
time.sleep(1)

# Turn off all NMEA messages but the GGA message
print("sending disable msg")
msg_disable_gll = ubx.ubx_config_disable("GLL", "GSV", "RMC", "GSA", "VTG")
print(list(msg_disable_gll))
ser.write(msg_disable_gll)


def gga_decode(msg):
    pass


while True:
    sentence = ser.readline()
    # if sentence.startswith(b"$GNGGA") or True:
    gga_decode(sentence)
    print(sentence)
