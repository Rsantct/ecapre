#!/usr/bin/env python3
"""
    Beta version. It works if the received data when a key is pressed has a
    fixed word length, like my Panasonic TV remote.
    TODO: new routine to decode variable length remote.

    You need an FTDI FT23xx USB UART with a 3 pin IR receiver at 38 KHz,
    e.g. TSOP31238 or TSOP38238.

    Usage:

        ir.py [-t]

        -t  prints out the received bytes so you can
            map keys <> actions into the file 'ir.config'

"""

import serial
import sys
import yaml
import socket
from time import time, sleep
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
            print (f'(ir.py) ecapre service \'{svcName}\' socket error port {port}')
    return

def rx2cmd(w, keymap):
    try:
        return keymap[ str(w) ]
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

if __name__ == "__main__":

    UHOME = os.path.expanduser("~")
    THISPATH = os.path.dirname(os.path.abspath(__file__))

    if '-h' in sys.argv:
        print(__doc__)
        exit()

    # testing mode to learn new keys
    test_mode = '-t' in sys.argv

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
            REMCGF      = CFG['remotes'][ CFG['remote'] ]
            keymap      = REMCGF['keymap']
            wlen        = REMCGF['wlength']
            baudrate, bytesize, parity, stopbits = serial_params(REMCGF)
    except:
        print(f'ERROR with \'{THISPATH}/ir.config\'')
        exit()

    # Open the IR usb device
    s = serial.Serial( port=CFG['ir_dev'], baudrate=baudrate, bytesize=bytesize,
                       parity=parity, stopbits=stopbits, timeout=None)
    print('Serial open:', s.name, baudrate, bytesize, parity, stopbits)

    # LOOP
    lastTimeStamp = time()
    while True:
        rx  = s.read( wlen )
        cmd = rx2cmd(rx, keymap)
        if test_mode:
            print(rx, cmd)
        if cmd:
            if time() - lastTimeStamp >= antibound:
                send_cmd(cmd)
                lastTimeStamp = time()
