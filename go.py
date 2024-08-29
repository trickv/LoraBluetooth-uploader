#!/usr/bin/env python3

import sondehub
import serial
import re
import sys

port = serial.Serial('/dev/rfcomm0', 57600)
from sondehub.amateur import Uploader
uploader = Uploader("KD9PRC-go")

while True:
    line = port.readline().decode('latin1').strip()
    print(line)
    if line.startswith('Message='):
        vars = line.split('$$')[1].split(',')
        uploader.add_telemetry(
            vars[0], # Your payload callsign
            vars[2], # Time
            vars[3], # Latitude
            vars[4], # Longitude
            vars[5] # Altitude
        )
#sys.exit(0)
