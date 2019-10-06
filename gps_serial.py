import serial
import time

SERIAL_PORT ="COM8"
BAUDRATE = 9600



ser = serial.Serial(SERIAL_PORT, BAUDRATE)  # open serial port

def gga_decode(msg):
    pass

while True:
    sentence = list(ser.readline())
    #if sentence.startswith(b"$GNGGA") or True:
    gga_decode(sentence)
    print(sentence)

    


