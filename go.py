#!/usr/bin/env python3

"""
When receiving a packet we get this:
FreqErr=3.9
PacketRSSI=-90
PacketSNR=6
Message=$$KD9PRC-2,2618,05:07:47,41.87812,-88.07533,00240,3,179,8,29.9*3C93
['KD9PRC-2', '2618', '05:07:47', '41.87812', '-88.07533', '00240', '3', '179', '8', '29.9*3C93']

When idle we're also getting spammed with these at a 1s interval ish:
GPS=05:06:18,41.87812,-88.07533,230,0,0,6
CurrentRSSI=-90


"""

import sondehub
import serial
import re
import sys

port = serial.Serial('/dev/rfcomm0', 57600, timeout=5)
from sondehub.amateur import Uploader
uploader = Uploader("KD9PRC-go")

rssi = None
snr = None

while True:
    line = port.readline().decode('latin1').strip()
    if line.startswith('CurrentRSSI') or line.startswith('GPS'):
        continue
    print(line)
    if line.startswith('PacketRSSI='):
        rssi = line.split('=')[1]
    if line.startswith('Message='):
        vars = line.split('$$')[1].split('*')[0].split(',')
        print(vars)
        uploader.add_telemetry(
            vars[0], # Your payload callsign
            vars[2], # Time
            vars[3], # Latitude
            vars[4], # Longitude
            vars[5], # Altitude
            rssi=rssi,
            snr=snr,
            modulation="LoRa",
            frame=vars[1],
            sats=vars[8],
            temp=vars[9]
        )
        print()
#sys.exit(0)
