#!/usr/bin/env python3
"""
    You need an FTDI FT23xx USB UART with a 3 pin IR receiver at 38 KHz,
    e.g. TSOP31238 or TSOP38238.

    Usage:

        ir.py  [-t logfilename]

        -t  Learning mode. Prints out the received bytes so you can
            map "key_bytes: actions" inside the file 'ir.config'

"""

import serial
import sys
import yaml
import socket
from time import time
import os

def send_cmd(cmd):
    if cmd[:4] == 'aux ':
        host, port = AUX_HOST, AUX_PORT
        cmd = cmd[4:]
        svcName = 'aux'
    else:
        host, port = CTL_HOST, CTL_PORT
        svcName = 'control'
    print('sending:', cmd, f'to {host}:{port}')
    with socket.socket() as s:
        try:
            s.connect( (host, port) )
            s.send( cmd.encode() )
            s.close()
        except:
            pass
            print (f'(ir.py) ecapre service \'{svcName}\' socket error port {port}')
    return

def irpacket2cmd(p, keymap):
    try:
        return keymap[ str(p) ]
    except:
        return ''

def serial_params(d):
    """ read a remote dict config then returns serial params """
    # defaults
    baudrate    = 9600
    bytesize    = 8
    parity      = 'N'
    stopbits    = 1
    if 'baudrate' in d:
        baudrate = d['baudrate']
    if bytesize in d and d['bytesize'] in (5, 6, 7, 8):
        bytesize = d['bytesize']
    if 'parity' in d and d['parity'] in ('N', 'E', 'O', 'M', 'S'):
        parity = d['parity']
    if 'stopbits' in d and d['stopbits'] in (1, 1.5, 2):
        stopbits = d['stopbits']
    return baudrate, bytesize, parity, stopbits

def main_EOP():
    # LOOPING: reading byte by byte as received
    lastTimeStamp = time() # helper to avoid bouncing
    irpacket = b''
    while True:
        rx  = s.read( 1 )
        # Detecting EndOfPacket byte with some tolerance,
        # or fixed length packets depending on remote:
        if  abs( int.from_bytes(rx, "big") -
                 int.from_bytes(endOfPacket, "big") ) <= 5:
            #print(irpacket)
            cmd = irpacket2cmd(irpacket, keymap)
            if cmd:
                if time() - lastTimeStamp >= antibound:
                    send_cmd(cmd)
                    lastTimeStamp = time()
            irpacket = b''
        else:
            irpacket += rx

def main_PL():
    # LOOPING: reading packetLength bytes
    lastTimeStamp = time() # helper to avoid bouncing
    while True:
        irpacket  = s.read( packetLength )
        cmd = irpacket2cmd(irpacket, keymap)
        if cmd:
            if time() - lastTimeStamp >= antibound:
                send_cmd(cmd)
                lastTimeStamp = time()

def main_TM():
    # Test mode will save the received bytes to a file so you can analyze them.
    irpacket = b''
    while True:
        rx  = s.read( 1 )
        print(rx)
        flog.write(rx)

if __name__ == "__main__":

    UHOME = os.path.expanduser("~")
    THISPATH = os.path.dirname(os.path.abspath(__file__))

    if '-h' in sys.argv:
        print(__doc__)
        exit()

    # ecapre services addressing
    try:
        with open(f'{UHOME}/ecapre/ecapre.config', 'r') as f:
            eca = yaml.load(f)
            CTL_HOST, CTL_PORT = eca['control_addr'], eca['control_port']
            AUX_HOST, AUX_PORT = eca['aux_addr'], eca['aux_port']
    except:
        print('ERROR with \'ecapre.config\'')
        exit()

    # IR config file
    try:
        with open(f'{THISPATH}/ir.config', 'r') as f:
            CFG = yaml.load(f)
            antibound   = CFG['antibound']
            REMCFG      = CFG['remotes'][ CFG['remote'] ]
            keymap      = REMCFG['keymap']
            baudrate, bytesize, parity, stopbits = serial_params(REMCFG)
            packetLength = REMCFG['packetLength']
            try:
                endOfPacket = bytes.fromhex(REMCFG['endOfPacket'])
            except:
                endOfPacket = None

    except:
        print(f'ERROR with \'{THISPATH}/ir.config\'')
        exit()

    # testing mode to learn new keys
    test_mode = sys.argv[1:] and sys.argv[1] == '-t'
    if test_mode:
        if sys.argv[2:]:
            logfname = f'{sys.argv[2]}'
            flog = open(logfname, 'wb')
            print(f'(i) saving to \'{logfname}\'')
        else:
            print('-t  missing the log filename')
            exit()

    # Open the IR usb device
    s = serial.Serial( port=CFG['ir_dev'], baudrate=baudrate, bytesize=bytesize,
                       parity=parity, stopbits=stopbits, timeout=None)
    print('Serial open:', s.name, baudrate, bytesize, parity, stopbits)


    # Go LOOPING
    if test_mode:
        main_TM()
    elif endOfPacket and packetLength:
        print( 'ERROR: choose endOfPacket OR packetLength on your remote config' )
    elif endOfPacket:
        main_EOP()
    elif packetLength:
        main_PL()

