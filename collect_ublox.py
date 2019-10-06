#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 20:14:45 2019

@authors: Maarten Uijt de Haag and Eric Maaz 

Function: data collection software for the flight test

- setup receiver to acquire NMEA and raw measurements
- write measurements to a file that has the data in the name
- print the position to a file

Copyright (c) - TU Berlin - FacV - ILR - F3

"""

import serial
import time
#import sys
import numpy as np
#import matplotlib.pyplot as plt
#import cv2

from datetime import datetime
     
# Open the serial port
#ser = serial.Serial('/dev/ttyACM0', 460800)  # open serial port
ser = serial.Serial('COM8', 9600)  # open serial port
	
# Get a datetime object containing current date and time
now = datetime.now()

# Make the output filename
filename = now.strftime("finow_flight_laser_%d_%m_%Y_%H_%M_%S.dat")
print("Filename generated:", "filename")

# Open the output file
fd = open(filename, 'w+')


def compute_checksum(msg, n):
    
    ck_a = np.zeros((1,1),dtype='uint8')
    ck_b = np.zeros((1,1),dtype='uint8')
    
    # Convert buffer of bytes to a numpy array
    val = np.frombuffer(msg,dtype='uint8')
    
    # Compute checksum
    for ii in range(2,n):
        ck_a[0] = ck_a[0] + val[ii]
        ck_b[0] = ck_b[0] + ck_a[0]
        
    return msg+ck_a.tobytes()+ck_b.tobytes()
        

print ('Initializing U-blox F9P receiver - please wait ....')

#a = '\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xA7\x02\x91\x20\x00'

# Turn off all NMEA messages but the GGA message
msg_disable_gll = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xCC\x00\x91\x20\x00'
msg_disable_gll = compute_checksum(msg_disable_gll,len(msg_disable_gll)) 
ser.write(msg_disable_gll)
time.sleep(1)

msg_disable_gsv = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xC7\x00\x91\x20\x00'
msg_disable_gsv = compute_checksum(msg_disable_gsv,len(msg_disable_gsv)) 
ser.write(msg_disable_gsv)
time.sleep(1)

msg_disable_gsa = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xC2\x00\x91\x20\x00'
msg_disable_gsa = compute_checksum(msg_disable_gsa,len(msg_disable_gsa)) 
ser.write(msg_disable_gsa)
time.sleep(1)

msg_disable_rmc = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xAE\x00\x91\x20\x00'
msg_disable_rmc = compute_checksum(msg_disable_rmc,len(msg_disable_rmc)) 
ser.write(msg_disable_rmc)
time.sleep(1)

#msg_disable_vtg = '\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xB3\x00\x91\x20\x00'
#msg_disable_vtg = compute_checksum(msg_disable_vtg,len(msg_disable_vtg)) 
#ser.write(msg_disable_vtg)
#time.sleep(1)

# Turn on the raw messages

# Measurements
msg_enable_rawx = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xA7\x02\x91\x20\x01'
msg_enable_rawx = compute_checksum(msg_enable_rawx,len(msg_enable_rawx)) 
ser.write(msg_enable_rawx)
time.sleep(1)

# Measurements
msg_enable_sfrbx = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\x34\x02\x91\x20\x01'
msg_enable_sfrbx = compute_checksum(msg_enable_sfrbx,len(msg_enable_sfrbx)) 
ser.write(msg_enable_sfrbx)
time.sleep(1)

# At this point the receiver outputs: GNGGA, GNVTG, RAWX, SFRBX

print ('Start collecting data')

utc_prv = 0.0

try:
    while 1 :
        
        # Read a "line" of data from the U-Blox receiver    
        data = ser.readline()
        
        # Check how long the data string is: too big is not good
        #print len(data)
        #print data
        
        # Write trhis data to the file immediately
        fd.write(data)
     
        # Find the GGA input string
        a = data.find('GNGGA') 
        
        # If data string found print to the screen
        if a > 0 :
           print(data)
#            b = data[a:].split(",")
#            utc = float(b[1])
#            lat = float(b[2][0:2]) + float(b[2][2:])/60.0 
#            lon = float(b[4][0:3]) + float(b[4][3:])/60.0
#            numsvs = int(b[7])
#            alt = float(b[11])
#            print("-> t: %8.2f, lat: %8.5f, lon: %8.5f, alt: %7.3f, numsvs: %3d" % (utc, lat, lon, alt, numsvs) )

       
        # Maybe figure out what SVSs are there
        
except:    
    fd.close()
    print('Closed output file: ', filename) 



