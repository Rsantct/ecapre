#!/usr/bin/env python3
"""
    ecapre's system control

    Usage:

        ecapre_control.py [command value] [add]

        commands:  values:
        ---------  -------

        loudness    on | off |toggle
        target      room-house (dB-dB)

        level       xx (dB)
        balance     xx (dB)
        bass        xx (dB)
        treble      xx (dB)

            use 'add' for relative xx adjustment
"""

import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

import share.ecanet        as eca
import share.eca_Eq4p_ctrl as Eq4p
import share.eca_Eq10_ctrl as Eq10

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
    cmds = [ f'c-select {chain}', f'cop-set {CFG["AMP_COP_IDX"]},1,{str(ch_value)}' ]
    for cmd in cmds:
        eca.ecanet(cmd)

def read_command_phrase(command_phrase):

    cmd, arg, relative = None, None, False

    opcs = command_phrase.split(' ')

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

    line1 = 'Vol:   vvvv  Bal:   bbbb  Loud: lll'
    line2 = 'Bass:  ssss  Treb:  tttt'
    line3 = 'RoomG: rrrr  House: hhhh'

    line1 = line1.replace('vvvv', str(state['level'])).rjust(4)
    line1 = line1.replace('bbbb', str(state['balance'])).rjust(4)
    line1 = line1.replace('lll', {True:'on', False:'off'}[ state['loudness_track'] ] )
    line2 = line2.replace('ssss', str(state['bass'])).rjust(4)
    line2 = line2.replace('tttt', str(state['bass'])).rjust(4)
    line3 = line3.replace('rrrr', str(state['room_gain'])).rjust(4)
    line3 = line3.replace('hhhh', str(state['house_curve'])).rjust(4)

    print(line1)
    print(line2)
    print(line3)

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
        Eq10.apply_loudness( CFG['LOUD_COP_IDX'], loud_level )

        # Loudness_track
        if not state['loudness_track']:
            Eq10.apply_loudness( CFG['LOUD_COP_IDX'], 0.0 )

        # Tone
        Eq4p.set_tone(cop_idx=CFG['TONE_COP_IDX'], band='bass',
                                                   gain=state['bass'] )
        Eq4p.set_tone(cop_idx=CFG['TONE_COP_IDX'], band='treble',
                                                   gain=state['treble'] )

        # Target: room_gain and house curves
        Eq4p.apply_room_gain( cop_idx = CFG['ROOMG_COP_IDX'],
                              room_gain = state['room_gain'] )
        Eq10.apply_target(    cop_idx = CFG['HOUSE_COP_IDX'],
                              room_gain = 0.0,
                              house_atten = -state['house_curve'] )

# Interface function to plug this on server.py
def do( command_phrase ):
    cmd, arg, relative = read_command_phrase( command_phrase )
    state = process( cmd, arg, relative )
    return state.encode()

# Main function for command processing
def process( cmd, arg, relative ):
    """ input:  a tuple (command, arg, relative)
        output: the ecapre state dictionary
    """

    # Load current status
    with open(STATE_FNAME, 'r') as f:
        state = yaml.load(f)

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
        Eq10.apply_loudness( CFG['LOUD_COP_IDX'], loud_level )
        state['level'] = level

    # Balance
    elif cmd in ('balance', 'bal'):
        bal = float(arg)
        for chain in 'L','R':
            set_level(chain, state['level'], bal)
        state['balance'] == bal

    # Loudness_track management
    elif cmd in ('loud', 'loudness'):
        mode = arg
        for chain in ('L','R'):
            if mode == 'on':
                loud_level = max( min( -state['level'], MAX_LOUD_COMPENS),
                                  MIN_LOUD_COMPENS)
                Eq10.apply_loudness( CFG['LOUD_COP_IDX'], loud_level )
            else:
                Eq10.apply_loudness( CFG['LOUD_COP_IDX'], 0.0 )
        state['loudness_track'] = {'on':True, 'off':False}[arg]

    # Loudness reference management
    # ** WIP **

    # Bass setting
    elif cmd == 'bass':
        dB = float(arg)
        # clamp
        dB = max(min(dB, TONE_SPAN), -TONE_SPAN)
        Eq4p.set_tone(CFG['TONE_COP_IDX'], 'bass', dB, relative )
        state['bass'] = dB

    # Treble setting
    elif cmd == 'treble':
        dB = float(arg)
        # clamp
        dB = max(min(dB, TONE_SPAN), -TONE_SPAN)
        Eq4p.set_tone(CFG['TONE_COP_IDX'], 'treble', dB, relative )
        state['treble'] = dB

    # Target EQ (room_gain and house curves)
    elif cmd == 'target':
        roomg = float(arg.split('-')[0])
        house = float(arg.split('-')[1])
        Eq4p.apply_room_gain( CFG['ROOMG_COP_IDX'], roomg )
        Eq10.apply_target(    CFG['HOUSE_COP_IDX'], room_gain=0.0,
                                                    house_atten=house )
        state['room_gain']   =  round(roomg,1)
        state['house_curve'] = -round(house,1)

    # Restore last settings from disk file .state.yml
    elif cmd == 'restore':
        restore()

    # Help
    elif '-h' in cmd:
        print(__doc__)

    # Saving the new settings
    with open(STATE_FNAME, 'w') as f:
        yaml.dump( state, f, default_flow_style=False )

    return state

# command line use
if __name__ == '__main__':

    if sys.argv[1:]:

        command_phrase = ' '.join (sys.argv[1:] )
        cmd, arg, relative = read_command_phrase( command_phrase )
        dummy = process( cmd, arg, relative )

    # If no arguments, print the current settings
    else:
        print_state()

