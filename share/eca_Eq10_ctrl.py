#!/usr/bin/env python3
"""
    A module to manage the LADSPA plugin 'C* Eq10 - 10-band equaliser'
    from the 'caps' package (http://quitte.de/dsp/caps.html#Eq10),
    on Ecasound.

    Eq10 bands:

        31 Hz, 63 Hz, 125 Hz, 250 Hz, 500 Hz, 1 kHz, 2 kHz, 4 kHz, 8 kHz, 16 kHz

    Command line usage:

        eca_Eq10_ctrl.py cop=N [ load=file ] [ bypass=off|on|toggle ]

"""

import yaml
import sys
from os.path import expanduser
UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )
import ecanet as eca

THIS_PG_NAME = 'C* Eq10 - 10-band equaliser'
CHAINS = eca.ecanet('c-list').split('\r\n')[1].split(',')
EQ10COPS = {}
for chain in CHAINS:
    EQ10COPS[chain] = eca.get_cop_idxs(chain, THIS_PG_NAME)

### Eq10 settings for a target curve with room_gain:+6dB and house:-3dB
fname = f'{UHOME}/ecapre/share/eq/Eq10_target_6-3.yml'
PARAMS_RG6_HC3 = yaml.safe_load( open(fname, 'r') )

### Eq10 settings for Loudness curve with 13 dB compensation
fname = f'{UHOME}/ecapre/share/eq/Eq10_loud_compens_+13dB.yml'
PARAMS_LOUD13 = yaml.safe_load( open(fname, 'r') )


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
    for chain in CHAINS:
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


    # Getting PARAMS_RG6_HC3 as starting point:
    # a target curve with room_gain:+6dB and house:-3dB

    params = {}
    # lets scale :
    for k in PARAMS_RG6_HC3:

        ## Room gain section
        if k in ('31 Hz','63 Hz','125 Hz','250 Hz'):
            params[k] = room_gain / 6.0 * PARAMS_RG6_HC3[k]

        # House section
        else:
            params[k] = -house_atten / -2.81 * PARAMS_RG6_HC3[k]

    # Some fine tuning to compensate the Eq10 upper end rise
    params = upper_end_tuning(params)

    # Eq10 needs some tuning at 32Hz band
    params['31 Hz'] = params['31 Hz'] + adj_31Hz

    # and rendering:
    for chain in CHAINS:
        eca.set_cop(chain, cop_idx, params)


def apply_loudness( cop_idx, loud_level ):
    params = {}

    # lets scale:
    for k in PARAMS_LOUD13:
        params[k] = loud_level / 13.0 * PARAMS_LOUD13[k]

    # Some fine tuning to compensate the Eq10 upper end rise
    params = upper_end_tuning(params)

    for chain in CHAINS:
        eca.set_cop(chain, cop_idx, params)


def upper_end_tuning(params):
    # Some fine tuning to compensate the Eq10 upper end rise.
    # Adjust 'totEq10' as per your Eq10 plugins in series.

    # Get the number of Eq10 plugins in the first channel (chain 'L')
    totEq10 = len( EQ10COPS['L'] )

    for k in ('1 kHz','2 kHz','4 kHz','8 kHz','16 kHz'):
        params[k] = params[k] + {   '1 kHz':  -0.05 * totEq10,
                                    '2 kHz':  -0.15 * totEq10,
                                    '4 kHz':  -0.32 * totEq10,
                                    '8 kHz':  -0.32 * totEq10,
                                    '16 kHz': -0.12 * totEq10   }[ k ]
    return params


def low_end_tuning(cop='all', gain31Hz=2.0):
    """ compensates the Eq10 low end roll-off at 31 Hz band
    """

    # iterate sover the Eq10 plugings for all channels (chains)
    for chain in CHAINS:

        if cop == 'all':
            cops = EQ10COPS[chain]
        else:
            cops = [cop]

        for cop in cops:
            print( f'(eca_Eq10_ctrl) setting {gain31Hz} dB at 31 Hz band'
                   f' on chain:{chain}, Eq10 plugin #{cop} ' )
            # copp 1 --> 31 Hz band
            cmds = [f'c-select {chain}',
                    f'cop-select {cop}',
                    f'copp-select 1',
                    f'copp-set {gain31Hz}']
            for cmd in cmds:
                eca.ecanet( cmd )


def load_curve(cop_idx, fname):
    params = yaml.safe_load(open(fname, 'r'))
    for chain in CHAINS:
        eca.set_cop(chain, cop_idx, params)


def check_cop_idx(cop):
    for chain in CHAINS:
        if cop not in EQ10COPS[chain]:
            return False
    return True


if __name__ == '__main__':


    bypass_mode = cop_idx = Eq10_fname = ''

    for opc in sys.argv[1:]:

        if '-h' in opc:
            print(__doc__)
            sys.exit()

        elif 'cop=' in opc:
            tmp = opc.split('=')[-1]
            if tmp.isdigit():
                cop_idx = tmp

        elif 'bypass=' in opc:
            tmp = opc.split('=')[-1]
            if tmp in ('on','off','toggle'):
                bypass_mode = tmp

        elif 'load=' in opc:
            Eq10_fname = opc.split('=')[-1]

        else:
            print(__doc__)
            sys.exit()


    if cop_idx:

        if not check_cop_idx(cop_idx):
            print(f'(!) Bad cop index {cop_idx} is NOT an Eq10 kind of')
            sys.exit()

        # Loading an arbritary curve from a YAML file
        if Eq10_fname:
            load_curve(Eq10_fname)

        # Setting bypass mode
        if bypass_mode:
            for chain in CHAINS:
                eca.set_cop_bypass( chain, cop_idx, bypass_mode )

        # selecting ONE cop_idx
        cops = [cop_idx]

    else:
        #selectign ALL cops loaded in chains
        cops = EQ10COPS[chain]


    # Printing out Eq10 running settings
    for chain in CHAINS:
        for cop_idx in cops:
            bypassed = ''
            if eca.get_cop_bypass(chain, cop_idx):
                bypassed = '(BYPASSED)'
            print(f'\n--- chain: {chain}, cop: {cop_idx} {bypassed}')
            params = eca.get_cop(chain, cop_idx)
            print_Eq10(params)
            print()

