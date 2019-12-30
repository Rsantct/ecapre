#!/usr/bin/env python3
"""
    compensates the Eq10 low end roll-off at 31 Hz band

    usage:    Eq10_31Hz.py gain_dB  (default 2.0 dB)
"""

import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )
import ecanet as eca

with open(f'{UHOME}/ecapre/ecapre.config', 'r') as f:
    CFG = yaml.load(f)

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

if __name__ == '__main__':

    gain31 = 2.0

    if sys.argv[1:]:

        if isFloat(sys.argv[1]):
            gain31 = sys.argv[1]

        elif '-h' in sys.argv[1]:
            print(__doc__)
            exit()

    cops = CFG["HOUSE_COP_IDX"], CFG["LOUD_COP_IDX"]

    for cop in cops:
        print( f'(Eq10_31Hz) setting {gain31} dB at 31 Hz band on Eq10 plugin #{cop}' )
        for chain in 'L', 'R':
            # copp 1 --> 31 Hz band
            cmds = [f'c-select {chain}',
                    f'cop-select {cop}',
                    f'copp-select 1',
                    f'copp-set {gain31}']
            for cmd in cmds:
                eca.ecanet( cmd )

