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
import sys
import time
import crcmod

from sondehub.amateur import Uploader
uploader = Uploader("KD9PRC-go")

crc16f = crcmod.predefined.mkCrcFun('crc-ccitt-false')

rssi = None
snr = None
port = None

while True:
    try:
        if port is None:
            port = serial.Serial('/dev/rfcomm0', 57600, timeout=5)
        line = port.readline()
    except serial.serialutil.SerialException as e:
        print("SerialException: {}, retrying...".format(e))
        time.sleep(0.1)
        port.close()
        time.sleep(1)
        port.open()
        time.sleep(0.1)
        continue
    line = line.decode('latin1').strip()
    if line.startswith('CurrentRSSI') or line.startswith('GPS'):
        continue
    print(line, end=' ')
    if line.startswith('PacketRSSI='):
        rssi = line.split('=')[1]
    if line.startswith('Message='):
        ukhas_line_parts = line.lstrip("Message=$$").split("*")
        expected_crc = "{0:04X}".format(crc16f(ukhas_line_parts[0].encode('ascii')))
        if expected_crc != ukhas_line_parts[1]:
            print("CRC error: {} mismatches expected {}".format(expected_crc, ukhas_line_parts[1]))
            print()
            continue
        else:
            print("(CRC OK)")
        vars = line.split('$$')[1].split('*')[0].split(',')
        print(vars)
        out = uploader.add_telemetry(
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
        print(out)
    print()
    time.sleep(0.05)
#sys.exit(0)
