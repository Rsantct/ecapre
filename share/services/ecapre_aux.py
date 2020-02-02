#!/usr/bin/env python3
"""
    ecapre's auxiliary functions control

    Usage:

        ecapre_aux.py [command argument]

        commands:   values:
        ---------   -------
        amp_switch  on | off

"""

import json
import yaml
import sys
import os
from subprocess import Popen, check_output

UHOME = os.path.expanduser('~')

MAIN_FOLDER = f'{UHOME}/ecapre'
MACROS_FOLDER = f'{MAIN_FOLDER}/macros'
LOUD_MON_CTRL = f'{MAIN_FOLDER}/.loudness_control'
LOUD_MON_VAL  = f'{MAIN_FOLDER}/.loudness_monitor'

with open( f'{MAIN_FOLDER}/ecapre.config' , 'r' ) as f:
    CFG = yaml.load( f )
try:
    AMP_MANAGER =  CFG['aux']['amp_manager']
except:
    # This will be printed out to the terminal to advice the user:
    AMP_MANAGER =  'echo For amp switching please configure config.yml'

def player(action):
    # BETA version only works with Spotify under Mac OS
    try:
        if action == 'prev':
            Popen( f'osascript -e \'tell application \"Spotify\" to previous track\'', shell=True )
        elif action == 'next':
            Popen( f'osascript -e \'tell application \"Spotify\" to next track\'', shell=True )
        elif action == 'play_pause':
            Popen( f'osascript -e \'tell application \"Spotify\" to playpause\'', shell=True )
        elif action == 'stop':
            Popen( f'osascript -e \'tell application \"Spotify\" to playpause\'', shell=True )
    except:
        return

def read_command_phrase(command_phrase):
    cmd, arg = None, None
    # This is to avoid empty values when there are more
    # than on space as delimiter inside the command_phrase:
    opcs = [x for x in command_phrase.split(' ') if x]
    try:
        cmd = opcs[0]
    except:
        raise
    try:
        # allows spaces inside the arg part, e.g. 'run_macro 2_Radio Clasica'
        arg = ' '.join( opcs[1:] )
    except:
        pass
    return cmd, arg

# Interface function to plug this on server.py
def do( command_phrase ):
    cmd, arg = read_command_phrase( command_phrase
                                              .replace('\n','').replace('\r','') )
    result = process( cmd, arg )
    return json.dumps(result).encode()

# Main function for command processing
def process( cmd, arg ):
    """ input:  a tuple (command, arg)
        output: a result string
    """
    result = ''

    # Get the system name
    if cmd == 'system_name':
        result = CFG['system_name']

    # Amplifier switching
    elif cmd == 'amp_switch':
        if arg in ('on','off'):
            print( f'(aux) {AMP_MANAGER.split("/")[-1]} {arg}' )
            Popen( f'{AMP_MANAGER} {arg}'.split(), shell=False )
        elif arg == 'state':
            try:
                with open( f'{UHOME}/.amplifier', 'r') as f:
                    result =  f.read().strip()
            except:
                result = '--'

    # List of macros under macros/ folder
    elif cmd == 'get_macros':
        macro_files = []
        with os.scandir( f'{MACROS_FOLDER}' ) as entries:
            for entrie in entries:
                fname = entrie.name
                if ( fname[0] in [str(x) for x in range(1,10)] ) and fname[1]=='_':
                    macro_files.append(fname)
        result = macro_files

    # Run a macro
    elif cmd == 'run_macro':
        print( f'(aux) running macro: {arg}' )
        Popen( f'"{MACROS_FOLDER}/{arg}"', shell=True)
        result = 'tried'

    # Send reset to the loudness monitor daemon through by its control file
    elif cmd == 'loudness_monitor_reset':
        try:
            with open(LOUD_MON_CTRL, 'w') as f:
                f.write('reset')
            result = 'done'
        except:
            result = 'error'

    # Get the loudness monitor value from the loudness monitor daemon's output file
    elif cmd == 'get_loudness_monitor':
        try:
            with open(LOUD_MON_VAL, 'r') as f:
                result = round( float(f.read().strip()), 1)
        except:
            result = ''

    # Playback control
    elif cmd == 'player':
        player(arg)

    # Help
    elif '-h' in cmd:
        print(__doc__)

    return result

# command line use
if __name__ == '__main__':

    if sys.argv[1:]:

        command_phrase = ' '.join (sys.argv[1:] )
        cmd, arg = read_command_phrase( command_phrase )
        result = process( cmd, arg )
        print( result )


