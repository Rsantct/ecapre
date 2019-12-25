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
THIS_PLUGIN_COP_IDXS = eca.get_cop_idxs('L', THIS_PG_NAME)

### Eq10 settings for a target curve with room_gain:+6dB and house:-3dB
fname = f'{UHOME}/ecapre/share/eq/Eq10_target_6-3.yml'
with open(fname, 'r') as f:
    PARAMS_6_3 = yaml.load(f)

### Eq10 settings for Loudness curve with 13 dB compensation
fname = f'{UHOME}/ecapre/share/eq/Eq10_loud_compens_+13dB.yml'
with open(fname, 'r') as f:
    PARAMS_LOUD13 = yaml.load(f)

def print_Eq10(params):
    line1 = ''
    line2 = ''
    for k in [x for x in params if 'Hz' in x]:
        freq = k
        line1 += freq.ljust(7)
        line2 += str( round(float(params[k]),2) ).ljust(7)
    print(line1)
    print(line2)

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def bypass_all_Eq10(bpmode):
    for chain in ('L', 'R'):
        for cop_idx in eca.get_cop_idxs(chain, THIS_PG_NAME):
            eca.set_cop_bypass( chain, cop_idx, bpmode )

def apply_target( cop_idx, room_gain, house_atten ):

    # (i) This is a beta implementation.
    #    It is planned to math here the proper gains

    # Eq10 needs some tuning at 32Hz band to compensate
    # the low end roll off of this plugin
    adj_31Hz = 2.0

    #  31 Hz,63 Hz,125 Hz,250 Hz,500 Hz,1 kHz,2 kHz,4 kHz,8 kHz,16 kHz
    #  <-----  room gain  -----> <------------  house  -------------->


    # Getting PARAMS_6_3 as starting point:
    # a target curve with room_gain:+6dB and house:-3dB

    params = {}
    # lets scale :
    for k in PARAMS_6_3:

        ## Room gain section
        if k in ('31 Hz','63 Hz','125 Hz','250 Hz'):
            params[k] = room_gain / 6.0 * PARAMS_6_3[k]

        # House section
        else:
            params[k] = -house_atten / -2.81 * PARAMS_6_3[k]

    # Some fine tuning to compensate the Eq10 upper end rise
    params = upper_end_tuning(params)

    # Eq10 needs some tuning at 32Hz band
    params['31 Hz'] = params['31 Hz'] + adj_31Hz

    # and rendering:
    for chain in ('L', 'R'):
        eca.set_cop(chain, cop_idx, params)

def apply_loudness( cop_idx, loud_level ):
    params = {}

    # lets scale:
    for k in PARAMS_LOUD13:
        params[k] = loud_level / 13.0 * PARAMS_LOUD13[k]

    # Some fine tuning to compensate the Eq10 upper end rise
    params = upper_end_tuning(params)

    for chain in ('L', 'R'):
        eca.set_cop(chain, cop_idx, params)

def upper_end_tuning(params):
    # Some fine tuning to compensate the Eq10 upper end rise
    for k in ('1 kHz','2 kHz','4 kHz','8 kHz','16 kHz'):
        params[k] = params[k] + {   '1 kHz':    -0.10,
                                    '2 kHz':    -0.30,
                                    '4 kHz':    -0.65,
                                    '8 kHz':    -0.65,
                                    '16 kHz':   -0.25   }[ k ]
    return params

if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()


        elif isInt(sys.argv[1]):
            cop_idx = sys.argv[1]

            # Bypass management (notice: 'on' here means 'bypass-off')
            if sys.argv[2:] and sys.argv[2] in ('on','off','toggle'):
                for chain in ('L','R'):
                    eca.set_cop_bypass( chain, cop_idx,
                                        mode={ 'on':'off',
                                               'off':'on',
                                               'toggle':'toggle'}[ sys.argv[2] ]
                                       )

            # Printing out the running settigs for the selected cop index
            for chain in ('L', 'R'):
                bypassed = ''
                if eca.get_cop_bypass(chain, cop_idx):
                    bypassed = '(BYPASSED)'
                print(f'\n--- chain {chain}, cop# {cop_idx}: {bypassed}')
                params = eca.get_cop(chain, cop_idx)
                print_Eq10(params)

        # Loading an arbritary curve from a YAML file
        else:
            Eq10_fname = sys.argv[1]
            params = read_Eq10_yml(Eq10_fname)
            for chain in ('L', 'R'):
                #print(params) # debug
                eca.set_cop(chain, cop_idx, params)

    else:
        print(__doc__)
