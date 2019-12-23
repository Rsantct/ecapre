#!/usr/bin/env python3
"""
    ecapre's system control

    Usage:

        ecapre_control.py [command value] [add]

        commands:  values:
        ---------  -------

        level       xx (dB)
        balance     xx (dB)
        loudness    on | off |toggle
        bass        xx (dB)
        treble      xx (dB)
        target      room-house (dB-dB)

        Use 'add' for relative adjustment
"""

import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

from   share.ecanet        import ecanet
import share.eca_mbeq_ctrl as mbeq
import share.eca_Eq4p_ctrl as Eq4p

with open(f'{UHOME}/ecapre/ecapre.config', 'r') as f:
    CFG = yaml.load(f)

HEADROOM         =  CFG['headroom']
MIN_LOUD_COMPENS =  CFG['min_loud_compens']
MAX_LOUD_COMPENS =  CFG['max_loud_compens']
TONE_SPAN        =  CFG['tone_span']
REF_SPL_GAIN     =  CFG['ref_spl_gain']
STATE_FNAME      =  f'{UHOME}/ecapre/.state.yml'


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def set_level(chain, dB, balance):
    """ This is for the -eadb preset as the first chain operator.
        It works with dB values
    """
    ch_value = dB + REF_SPL_GAIN - HEADROOM + balance/2.0 * {'L':-1, 'R':1}[chain]
    cmds = [ f'c-select {chain}', f'cop-set 1,1,{str(ch_value)}' ]
    for cmd in cmds:
        ecanet(cmd)

def get_level(chain):
    """ This is for the -eadb preset as the first chain operator.
        It works with dB values
    """
    level = None
    cmd = f'c-select {chain}'
    ecanet(cmd)
    cmd = 'cop-get 1,1'
    tmp = ecanet(cmd).split('\r\n')
    level = float(tmp[1])
    return level + HEADROOM

def read_command_line():

    cmd, arg, relative = None, None, False

    opcs = sys.argv[1:]

    if 'add' in opcs:
        relative = True
        opcs.remove('add')

    try:
        cmd = opcs[0]
    except:
        raise

    try:
        arg = opcs[1]
    except:
        pass

    return cmd, arg, relative

def print_state():

    with open(STATE_FNAME, 'r') as f:
        state = yaml.load(f)

    line1 = 'Vol:  vvvv  Bal: bbbb  Loud: lll'
    line2 = 'Bass: ssss  Treb: tttt '

    line1 = line1.replace('vvvv', str(state['level']).ljust(5))
    line1 = line1.replace('bbbb', str(state['balance']).ljust(5))
    line1 = line1.replace('lll', {True:'on', False:'off'}[ state['loudness_track'] ] )
    line2 = line2.replace('ssss', str(state['bass']).ljust(5))
    line2 = line2.replace('tttt', str(state['treble']).ljust(5))

    print(line1)
    print(line2)

def restore():
    """ restore last settings from disk file .state.yml
    """
    for chain in ('L','R'):
        print( f'(ecapre_control) restoring [{chain}] from disk file .state.yml' )
        # Level
        set_level( chain, state['level'], state['balance'] )

        # Setting Loudness level compensation, by following
        # the attenuation dB below level=0dB (reference SPL)
        loud_level = max( min( -state['level'], MAX_LOUD_COMPENS), MIN_LOUD_COMPENS)
        mbeq.apply_loudness( loud_level )

        # Loudness_track
        mbeq.mbeq_bypass( {True:'off', False:'on'} [ state['loudness_track'] ] )

        # Tone
        Eq4p.set_tone('bass',   state['bass'] )
        Eq4p.set_tone('treble', state['treble'] )

if __name__ == '__main__':

    with open(STATE_FNAME, 'r') as f:
        state = yaml.load(f)

    if sys.argv[1:]:

        cmd, arg, relative = read_command_line()

        # Level adjustment
        if cmd == 'level' and isFloat(arg):

            if relative:
                level = state['level'] + float(arg)
            else:
                level = float(arg)

            for chain in 'L','R':
                set_level(chain, level, state['balance'])

            # Setting Loudness level compensation, by following
            # the attenuation dB below level=0dB (reference SPL)
            loud_level = max( min( -level, MAX_LOUD_COMPENS), MIN_LOUD_COMPENS)
            mbeq.apply_loudness( loud_level )
            state['level'] = level

        # Balance
        elif cmd in ('balance', 'bal'):
            bal = float(arg)
            for chain in 'L','R':
                set_level(chain, state['level'], bal)
            state['balance'] == bal

        # Loudness_track management
        elif cmd in ('loud', 'loudness'):
            if 'on' in arg:
                mbeq.mbeq_bypass('off')
                state['loudness_track'] = True
            if 'off' in arg:
                mbeq.mbeq_bypass('on')
                state['loudness_track'] = False

        # Loudness reference management
        # ** WIP **

        # Bass setting
        elif cmd == 'bass':
            dB = float(arg)
            # clamp
            dB = max(min(dB, TONE_SPAN), -TONE_SPAN)
            Eq4p.set_tone('bass', dB, relative )
            state['bass'] = dB

        # Treble setting
        elif cmd == 'treble':
            dB = float(arg)
            # clamp
            dB = max(min(dB, TONE_SPAN), -TONE_SPAN)
            Eq4p.set_tone('treble', dB, relative )
            state['treble'] = dB

        # Target EQ
        elif cmd == 'target':
            room  = float(arg.split('-')[0])
            house = float(arg.split('-')[1])
            Eq4p.set_target(room, house )
            state['target'] = f'{str(round(room,1))} {str(round(house,1))}'

        # Restore last settings from disk file .state.yml
        elif cmd == 'restore':
            restore()

        # Help
        elif '-h' in cmd:
            print(__doc__)

        # Saving the new settings
        with open(STATE_FNAME, 'w') as f:
            yaml.dump( state, f, default_flow_style=False )

    # If no arguments, print the current settings
    else:
        print_state()

