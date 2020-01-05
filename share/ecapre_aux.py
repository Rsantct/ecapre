#!/usr/bin/env python3
"""
    ecapre's auxiliary functions control

    Usage:

        ecapre_aux.py [command argument]

        commands:   values:
        ---------   -------
        ampli       on | off

"""

import json
import yaml
import sys
import os
from subprocess import Popen, check_output

UHOME = os.path.expanduser('~')


with open(f'{UHOME}/ecapre/ecapre.config', 'r') as f:
    CFG = yaml.load(f)

def isFloat(s):
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

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
        arg = opcs[1]
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

    # Inputs list:
    if cmd == 'get_inputs':
        inputs = CFG["inputs"]
        return inputs

    # Amplifier switching
    if cmd == 'amp_switch':
        if arg in ('on','off'):
            print( f'(ecapre_aux) ampli.sh {arg}' )
            Popen( f'ampli.sh {arg}'.split(), shell=False )
        elif arg == 'state':
            try:
                return check_output( ['ampli.sh'], shell=False ).decode()
            except:
                return 'off'

    # List of macros under macros/ folder
    if cmd == 'get_macros':
        macro_files = []
        with os.scandir( f'{UHOME}/ecapre/macros' ) as entries:
            for entrie in entries:
                fname = entrie.name
                if ( fname[0] in [str(x) for x in range(1,10)] ) and fname[1]=='_':
                    macro_files.append(fname)
        result = ','.join(macro_files)

    # Run a macro
    if cmd == 'run_macro':
        print( f'(ecapre_aux) running macro: {arg}' )
        Popen( f'{UHOME}/ecapre/macros/{arg}', shell=True)

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


