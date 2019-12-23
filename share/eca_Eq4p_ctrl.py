#!/usr/bin/env python3
"""
    'C* Eq4p - 4-band parametric shelving equaliser' from caps
    http://quitte.de/dsp/caps.html#Eq4p

    Default settigs from Ecasound's ecapre.ecs file:

        a: mode=0(lowshelve) Q=.25   102.87  Hz
        b: mode=1(band)      Q=.5    529.15  Hz
        c: mode=1(band)      Q=.25   529.15  Hz
        d: mode=2(hishelve)  Q=.25  2721.78  Hz

"""
import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

import ecanet as eca

COP_NAME = 'C* Eq4p - 4-band parametric shelving equaliser'

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def print_Eq4p(params):
    COLW = 12
    # print(params); return # debug
    line0 = ' '.ljust(COLW)+'[a]'.ljust(COLW)+'[b]'.ljust(COLW)+'[c]'.ljust(COLW)+'[d]'.ljust(COLW)
    lmode = 'mode:'.ljust(COLW)
    lfreq = 'freq:'.ljust(COLW)
    lQ    = 'Q:'.ljust(COLW)
    lgain = 'gain:'.ljust(COLW)
    for x in ('a', 'b', 'c', 'd'):
        # translating the mode numeric value to his descripting name:
        mode = {0.0:'lowshelve', 1.0:'band', 2.0:'hishelve'} \
                    [ float(params[f'{x}.mode']) ]
        freq = params[f'{x}.f (Hz)']
        Q    = params[f'{x}.Q']
        gain = params[f'{x}.gain (dB)']
        lmode += mode.ljust(COLW)
        lfreq += str( round(float(freq),2) ).ljust(COLW)
        lQ    += str( round(float(Q   ),2) ).ljust(COLW)
        lgain += str( round(float(gain),2) ).ljust(COLW)
    print(line0)
    print(lmode)
    print(lfreq)
    print(lQ)
    print(lgain)

def read_Eq4p_yml(fname):
    # loading the YAML --> tmp
    with open(fname, 'r') as f:
        tmp =  yaml.load(f)
    # translating mode description to numeric values
    params = {}
    for k in tmp:
        if 'mode' in k:
            params[k] = {'lowshelve':0, 'band':1, 'hishelve':2}[ tmp[k] ]
        else:
            params[k] = tmp[k]
    return params

def bypass_Eq4p(mode):
    for chain in ('L', 'R'):
        eca.set_cop_bypass( chain, cop_name=COP_NAME,
                            mode={ 'on':'off',
                                   'off':'on',
                                   'toggle':'toggle'}[ mode ] )

def set_tone(band='bass', gain=0.0, add=False):
    stage = {'bass':'a', 'treble':'d'}[band]
    for chain in ('L','R'):
        params = eca.get_cop( chain, COP_NAME )
        # relative:
        if add:
            curr = float(params[f'{stage}.gain (dB)'])
            params[f'{stage}.gain (dB)'] = curr + gain
        # absolute:
        else:
            params[f'{stage}.gain (dB)'] = gain
        eca.set_cop(chain, COP_NAME, params)

def set_target(room=4.0, house=2.0):
    """ applies a {room} gain curve and a negative {house} curve
    """
    room_stage  = 'b'
    house_stage = 'c'
    for chain in ('L','R'):
        # get current Eq4p paramenters
        params = eca.get_cop( chain, COP_NAME )
        # applies target curves through by 'b' and 'c' stages
        params[f'{room_stage}.gain (dB)'] = room
        params[f'{house_stage}.gain (dB)'] = house * -1
        eca.set_cop(chain, COP_NAME, params)


if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

        # Bypass management
        elif sys.argv[1] in ['on', 'off', 'toggle']:
            bypass_Eq4p(mode=sys.argv[1])

        # Loading an arbritary curve from a YAML file
        else:
            Eq4p_fname = sys.argv[1]
            params = read_Eq4p_yml(Eq4p_fname)
            for chain in ('L', 'R'):
                #print(params) # debug
                eca.set_cop(chain, COP_NAME, params)


    # Printing out the running settigs
    else:
        for chain in ('L', 'R'):
            bypassed = ''
            tmp = eca.get_cop_bypass(chain, COP_NAME).split('\r\n')[1]
            if int(tmp):
                bypassed = '(BYPASSED)'
            print(f'\n--- chain {chain}: {bypassed}')
            params = eca.get_cop(chain, COP_NAME)
            print_Eq4p(params)

