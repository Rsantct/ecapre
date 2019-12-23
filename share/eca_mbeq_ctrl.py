#!/usr/bin/env python3
""" 15 band EQ, first and last are shelf kind of, bands are:
    50 100 156 220 311 440 622 880 1250 1750 2500 3500 5000 10000 20000
"""

from math import log10
import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

import ecanet as eca

THIS_PG_NAME = 'Multiband EQ'

def print_mbeq(params):
    line1 = ''
    line2 = ''
    for k in [x for x in params if 'Hz' in x]:
        freq = k.split('Hz')[0]
        line1 += freq.ljust(6)
        line2 += str( round(float(params[k]),2) ).ljust(6)
    print(line1)
    print(line2)

def read_mbeq_yml(fname):

    # 50    :  6.00
    # 100   :  4.05
    # 156   :  3.12
    # 220   :  2.40
    # 311   :  1.68
    # 440   :  1.00
    # 622   :  0.35
    # 880   :  0.07
    # 1250  : -0.22
    # 1750  : -0.39
    # 2500  : -0.40
    # 3500  : -0.42
    # 5000  : -0.45
    # 10000 :  0.95
    # 20000 :  5.7


    # loading the YAML --> tmp
    with open(fname, 'r') as f:
        tmp =  yaml.load(f)

    params = {}

    # The plugin params needs to be renamed 'XXHz gain', also the 50Hz one
    # needs to be renamed '50Hz (low shelving)'
    for k in tmp:
        pname = f'{k}Hz gain'
        if pname[:4] == '50Hz':
            pname += ' (low shelving)'
        params[pname] = tmp[k]

    return params

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def apply_loudness( loud_level ):
    params = {}
    # lets scale:
    for k in PARAMS13dB:
        params[k] = loud_level / 13.0 * PARAMS13dB[k]
    for chain in ('L', 'R'):
        eca.set_cop(chain, THIS_PG_NAME, params)

def mbeq_bypass(mode):
    for chain in ('L', 'R'):
        eca.set_cop_bypass( chain, THIS_PG_NAME, mode)


### MBEQ CURVE FOR +13dB LOUDNESS COMPENSATION
PARAMS13dB = read_mbeq_yml( f'{UHOME}/ecapre/share/eq/mbeq_loud_compens_+13dB.yml' )

if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

        # Bypass management (notice: 'on' here means 'bypass-off')
        elif sys.argv[1] in ['on', 'off', 'toggle']:
            mode = {'on':'off', 'off':'on', 'toggle':'toggle'}[ sys.argv[1] ]
            mbeq_bypass(mode)

        # Applying loudness compensation
        elif isFloat(sys.argv[1]):
            apply_loudness( loud_level = float(sys.argv[1]) )

        # Loading an arbritary curve from a YAML file
        else:
            mbeq_fname = sys.argv[1]
            params = read_mbeq_yml(mbeq_fname)
            for chain in ('L', 'R'):
                # print(params) # debug
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
            print_mbeq(params)

