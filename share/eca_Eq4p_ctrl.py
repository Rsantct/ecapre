#!/usr/bin/env python3
"""
    'C* Eq4p - 4-band parametric shelving equaliser'
    from caps ladspa plugins package
    http://quitte.de/dsp/caps.html#Eq4p


    a.mode,a.f (Hz),a.Q,a.gain (dB),
    b.mode,b.f (Hz),b.Q,b.gain (dB),
    c.mode,c.f (Hz),c.Q,c.gain (dB),
    d.mode,d.f (Hz),d.Q,d.gain (dB),
    _latency

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

THIS_PG_NAME = 'C* Eq4p - 4-band parametric shelving equaliser'


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def print_Eq4p(params):
    COLW = 12
    #print(params); return # debug
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
        tmp =  yaml.safe_load(f)
    # translating mode description to numeric values
    params = {}
    for k in tmp:
        if 'mode' in k:
            params[k] = {'lowshelve':0, 'band':1, 'hishelve':2}[ tmp[k] ]
        else:
            params[k] = tmp[k]
    return params


def bypass_all_Eq4p(bpmode):
    for chain in ('L', 'R'):
        for cop_idx in eca.get_cop_idxs(chain, THIS_PG_NAME):
            eca.set_cop_bypass( chain, cop_idx, bpmode )


def set_tone(cop_idx, band='bass', gain=0.0):
    stage = {'bass':'a', 'treble':'d'}[band]
    for chain in ('L','R'):
        params = eca.get_cop( chain, cop_idx )
        params[f'{stage}.gain (dB)'] = gain
        eca.set_cop(chain, cop_idx, params)


def apply_room_gain( cop_idx, room_gain ):
    for chain in ('L','R'):
        params = eca.get_cop( chain, cop_idx )
        # Room gain applied at 'b' section
        params['b.gain (dB)'] = room_gain
        params['b.Q'] = '0.33'
        eca.set_cop(chain, cop_idx, params)


def load_curve(cop_idx, fname):
    params = read_Eq4p_yml(fname)
    # rendering
    for chain in ('L', 'R'):
        #print(params) # debug
        eca.set_cop(chain, cop_idx, params)


if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

        # Bypass management (notice: 'on' here means 'bypass-off')
        elif sys.argv[1] in ['on', 'off', 'toggle']:
            bypass_all_Eq4p( bpmode={ 'on':'off',
                                      'off':'on',
                                      'toggle':'toggle'}[ sys.argv[1] ] )

        # Loading an arbritary curve from a YAML file
        else:
            fname, cop_idx = sys.argv[1], sys.argv[2]
            load_curve(cop_idx, fname)

    # Printing out the running settigs
    else:
        for chain in ('L', 'R'):
            for cop_idx in eca.get_cop_idxs(chain, THIS_PG_NAME):
                bypassed = ''
                if eca.get_cop_bypass(chain, cop_idx):
                    bypassed = '(BYPASSED)'
                print(f'\n--- chain {chain}, cop# {cop_idx}: {bypassed}')
                params = eca.get_cop(chain, cop_idx)
                print_Eq4p(params)

