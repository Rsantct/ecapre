#!/usr/bin/env python3
"""
    'C* Eq10 - 10-band equaliser'
    from caps ladspa plugins package
    http://quitte.de/dsp/caps.html#Eq10

    31 Hz,63 Hz,125 Hz,250 Hz,500 Hz,1 kHz,2 kHz,4 kHz,8 kHz,16 kHz
"""

import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

import ecanet as eca

THIS_PG_NAME = 'C* Eq10 - 10-band equaliser'

def print_Eq10(params):
    line1 = ''
    line2 = ''
    for k in [x for x in params if 'Hz' in x]:
        freq = k
        line1 += freq.ljust(7)
        line2 += str( round(float(params[k]),2) ).ljust(7)
    print(line1)
    print(line2)

def read_Eq10_yml(fname):

    # loading the YAML --> tmp
    with open(fname, 'r') as f:
        return  yaml.load(f)

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def apply_target( room_gain, house ):

    #  31 Hz,63 Hz,125 Hz,250 Hz,500 Hz,1 kHz,2 kHz,4 kHz,8 kHz,16 kHz
    #  <-----  room gain  -----> <------------  house  -------------->

    # Getting PARAMS_6_3 as starting point:
    # a target curve with room_gain:+6dB and house:-3dB

    params = {}
    # lets scale :
    for k in PARAMS_6_3:
        # Room gain section
        if k in ('31 Hz','63 Hz','125 Hz','250 Hz'):
            params[k] = room_gain /  6.0 * PARAMS_6_3[k]
        # House section
        else:
            params[k] = -house    / -3.0 * PARAMS_6_3[k]

    # and rendering:
    for chain in ('L', 'R'):
        eca.set_cop(chain, THIS_PG_NAME, params)

def Eq10_bypass(mode):
    for chain in ('L', 'R'):
        eca.set_cop_bypass( chain, THIS_PG_NAME, mode)

### Eq10 settings for target curve with room_gain:+6dB and house:-3dB
PARAMS_6_3 = read_Eq10_yml( f'{UHOME}/ecapre/share/eq/Eq10_target_6-3.yml' )

if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

        # Bypass management (notice: 'on' here means 'bypass-off')
        elif sys.argv[1] in ['on', 'off', 'toggle']:
            mode = {'on':'off', 'off':'on', 'toggle':'toggle'}[ sys.argv[1] ]
            Eq10_bypass(mode)

        # Loading an arbritary curve from a YAML file
        else:
            Eq10_fname = sys.argv[1]
            params = read_Eq10_yml(Eq10_fname)
            for chain in ('L', 'R'):
                #print(params) # debug
                eca.set_cop(chain, THIS_PG_NAME, params)


    # Printing out the running settigs
    else:
        for chain in ('L', 'R'):
            bypassed = ''
            tmp = eca.get_cop_bypass(chain, THIS_PG_NAME).split('\r\n')[1]
            if int(tmp):
                bypassed = '(BYPASSED)'
            print(f'\n--- chain {chain}: {bypassed}')
            params = eca.get_cop(chain, THIS_PG_NAME)
            print_Eq10(params)

