#!/usr/bin/env python3
"""
    ecapre's system control

    Usage:

        ecapre_control.py [command value] [add]

        (use 'add' for relative adjustment)

        commands:       values:
        ---------       -------

        state
        get_inputs
        input           inputName
        mute            on | off |toggle
        mono            on | off |toggle

        loudness        on | off |toggle
        loudness_ref    xx (dB)
        target          room-house (dB-dB)

        level           xx (dB)
        balance         xx (dB)
        bass            xx (dB)
        treble          xx (dB)

        help

"""

import json
import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

import ecanet        as eca
import eca_Eq4p_ctrl as Eq4p
import eca_Eq10_ctrl as Eq10

with open(f'{UHOME}/ecapre/ecapre.config', 'r') as f:
    CFG = yaml.load(f)

HEADROOM         =  CFG['headroom']
MIN_LOUD_COMPENS =  CFG['min_loud_compens']
MAX_LOUD_COMPENS =  CFG['max_loud_compens']
TONE_SPAN        =  CFG['tone_span']
BALANCE_SPAN     =  CFG['balance_span']
REF_SPL_GAIN     =  CFG['ref_spl_gain']
STATE_FNAME      =  f'{UHOME}/ecapre/.state.yml'

def isFloat(s):
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

def cross_chains(mode):
    if mode == 'on':
        eca.ecanet( 'jack-connect ecasound:out_1 system:playback_2' )
        eca.ecanet( 'jack-connect ecasound:out_2 system:playback_1' )
    else:
        eca.ecanet( 'jack-disconnect ecasound:out_1 system:playback_2' )
        eca.ecanet( 'jack-disconnect ecasound:out_2 system:playback_1' )

def select_input(input_name):
    if input_name == 'none':
        eca.ecanet( 'jack-disconnect  system:capture_1          convoLV2:in_1' )
        eca.ecanet( 'jack-disconnect  system:capture_2          convoLV2:in_2' )
        eca.ecanet( 'jack-disconnect  JackBridge\ #1:output_0   convoLV2:in_1' )
        eca.ecanet( 'jack-disconnect  JackBridge\ #1:output_1   convoLV2:in_2' )
    elif input_name == 'analog':
        eca.ecanet( 'jack-connect     system:capture_1          convoLV2:in_1' )
        eca.ecanet( 'jack-connect     system:capture_2          convoLV2:in_2' )
        eca.ecanet( 'jack-disconnect  JackBridge\ #1:output_0   convoLV2:in_1' )
        eca.ecanet( 'jack-disconnect  JackBridge\ #1:output_1   convoLV2:in_2' )
    else:
        eca.ecanet( 'jack-disconnect  system:capture_1          convoLV2:in_1' )
        eca.ecanet( 'jack-disconnect  system:capture_2          convoLV2:in_2' )
        eca.ecanet( 'jack-connect     JackBridge\ #1:output_0   convoLV2:in_1' )
        eca.ecanet( 'jack-connect     JackBridge\ #1:output_1   convoLV2:in_2' )

def set_level(chain, dB, balance):
    """ This is for the -eadb preset as the first chain operator.
        It works with dB values
    """
    ch_value = dB + REF_SPL_GAIN - HEADROOM + balance/2.0 * {'L':-1, 'R':1}[chain]
    cmds = [ f'c-select {chain}', f'cop-set {CFG["AMP_COP_IDX"]},1,{str(ch_value)}' ]
    for cmd in cmds:
        eca.ecanet(cmd)

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
    # Load current status
    with open(STATE_FNAME, 'r') as f:
        state = yaml.load(f)

    # Mono
    cross_chains( {True:'on', False:'off'}[ state["mono"] ] )

    for chain in ('L','R'):
        print( f'(ecapre_control) restoring [{chain}] from disk file .state.yml' )

        # Level
        set_level(chain, state['level'] - 3.0 * state['mono'], state['balance'])

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

def read_command_phrase(command_phrase):
    cmd, arg, relative = '', '', False
    # avoid crash if an empy string is received.
    if not command_phrase.strip():
        return cmd, arg, relative
    # This is to avoid empty values when there are more
    # than on space as delimiter inside the command_phrase:
    opcs = [x for x in command_phrase.split(' ') if x]
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

# Interface function to plug this on server.py
def do( command_phrase ):
    cmd, arg, relative = read_command_phrase( command_phrase
                                              .replace('\n','').replace('\r','') )
    state = process( cmd, arg, relative )
    return json.dumps(state).encode()

# Main function for command processing
def process( cmd, arg, relative ):
    """ input:  a tuple (command, arg, relative)
        output: the ecapre state dictionary after processing the input
    """

    result = 'ACK'  # a default result for any processed cmd

    # Load current status
    with open(STATE_FNAME, 'r') as f:
        state = yaml.load(f)

    # Get state
    if cmd in ('state','get_state','status'):
        result = state

    # Select input
    elif cmd == 'input':
        select_input( arg )
        state["input"] = arg

    # Get inputs
    elif cmd == 'get_inputs':
        result = CFG["inputs"]

    # Mute
    elif cmd == 'mute' and arg in ('on','off','toggle'):
        # arg can be 'on'|'off'|'toggle'
        # state options are boolean
        for chain in 'L','R':
            eca.ecanet( f'c-select {chain}' )
            eca.ecanet( f'c-mute {arg}' )
        muted = {   'on':      True,
                    'off':     False,
                    'toggle':  {True:False, False:True}[state['muted']]
                }[arg]
        state["muted"] = muted

    # Mono management
    elif cmd == 'mono':

        # arg can be 'on'|'off'|'toggle'
        # state options are boolean
        mono_act = { 'on':      True,
                     'off':     False,
                     'toggle':  {True:False, False:True}[state['mono']]
                  }[arg]

        if mono_act:
            cross_chains('on')
            for chain in 'L','R':
                set_level(chain, state['level'] - 3.0 , state['balance'])
        else:
            cross_chains('off')
            for chain in 'L','R':
                set_level(chain, state['level'] + 3.0 , state['balance'])

        state['mono'] = mono_act

    # Level adjustment
    elif cmd == 'level' and isFloat(arg):
        if relative:
            level = state['level'] + float(arg)
        else:
            level = float(arg)

        for chain in 'L','R':
            set_level(chain, level - 3.0 * state['mono'], state['balance'])

        # Setting Loudness level compensation, by following
        # the attenuation dB below level=0dB (reference SPL)
        loud_level = max( min( -level, MAX_LOUD_COMPENS), MIN_LOUD_COMPENS)
        Eq10.apply_loudness( CFG['LOUD_COP_IDX'], loud_level )
        state['level'] = level

    # Balance
    elif cmd in ('balance', 'bal') and isFloat(arg):
        bal = float(arg)
        if relative:
            bal = state["balance"] + bal
        # clamp
        bal = max(min(bal, BALANCE_SPAN), -BALANCE_SPAN)
        for chain in 'L','R':
            set_level( chain, state['level'] - 3.0 * state['mono'], bal )
        state["balance"] = bal

    # Loudness_track management
    elif cmd in ('loud', 'loudness', 'loudness_track'):

        # arg can be 'on'|'off'|'toggle'
        # state options are boolean
        ld_act = { 'on':      True,
                   'off':     False,
                   'toggle':  {True:False, False:True}[state['loudness_track']]
                  }[arg]

        if ld_act:
            loud_level = max( min( -state['level'], MAX_LOUD_COMPENS),
                              MIN_LOUD_COMPENS)
            Eq10.apply_loudness( CFG['LOUD_COP_IDX'], loud_level )
        else:
            Eq10.apply_loudness( CFG['LOUD_COP_IDX'], 0.0 )

        state['loudness_track'] = ld_act

    # Loudness reference management
    elif cmd == 'loudness_ref' and isFloat(arg):
        # !!!! WIP !!!!
        result = 'WIP'

    # Bass & Treble setting
    elif cmd in ('bass','treble') and isFloat(arg):
        dB = float(arg)
        if relative:
            dB = state[cmd] + dB
        # clamp
        dB = max(min(dB, TONE_SPAN), -TONE_SPAN)
        Eq4p.set_tone(CFG['TONE_COP_IDX'], cmd, dB)
        state[cmd] = dB

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
    elif cmd in ('-h','--help','help'):
        result = __doc__

    # Something not processed
    else:
        result = 'NACK'

    # Saving the new settings
    with open(STATE_FNAME, 'w') as f:
        yaml.dump( state, f, default_flow_style=False )

    return result

# command line use
if __name__ == '__main__':

    if sys.argv[1:]:

        command_phrase = ' '.join (sys.argv[1:] )
        cmd, arg, relative = read_command_phrase( command_phrase )
        if not cmd:
            print_state()
        print( process( cmd, arg, relative ) )

