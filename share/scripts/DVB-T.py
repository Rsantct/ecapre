#!/usr/bin/env python3

# Copyright (c) 2019 Rafael Sánchez
# This file is part of 'ecapre', a PC based personal audio system.
#
# 'ecapre' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'ecapre' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'ecapre'.  If not, see <https://www.gnu.org/licenses/>.


"""
    Starts and stops Mplayer for DVB-T playback.

    Also used to change on the fly the played stream.

    DVB-T tuned channels are ussually stored at
        ~/.mplayer/channels.conf

    User settings (presets, default) can be configured at
        ecapre/DVB-T.yml

    Usage: DVB-T.py   start   [ <preset_num> | <channel_name> ]
                      stop
                      prev    (load previous from recent presets)
                      preset  <preset_num>
                      name    <channel_name>
"""

import sys,os
from pathlib import Path
from time import sleep
import subprocess as sp
import yaml

UHOME = os.path.expanduser("~")

## USER SETTINGS: see inside DVB-T.yml

## Mplayer options:
tuner_file = f'{UHOME}/.mplayer/channels.conf'
options = '-quiet -nolirc -slave -idle'

# Input FIFO. Mplayer runs in server mode (-slave) and
# will read commands from a fifo:
input_fifo = f'{UHOME}/ecapre/.dvb_fifo'
f = Path( input_fifo )
if  not f.is_fifo():
    sp.Popen ( f'mkfifo {input_fifo}'.split() )
del(f)

# Mplayer output is redirected to a file, so it can be read what it is been playing:
redirection_path = f'{UHOME}/ecapre/.dvb_events'


def select_by_name(channel_name):
    """ loads a stream by its preset name """

    try:
        # check_output will fail if no command output
        sp.check_output( ['grep', channel_name, tuner_file] ).decode()
    except:
        print( f'(init/DVB) Channel NOT found: \'{channel_name}\'' )
        return False

    try:
        print( f'(init/DVB) trying to load \'{channel_name}\'' )
        # The whole address after 'loadfile' needs to be SINGLE quoted to load properly:
        command = ('loadfile \'dvb://' + channel_name + '\'\n' )
        f = open( input_fifo, 'w')
        f.write(command)
        f.close()
        return True
    except:
        print( f'(init/DVB) failed to load \'{channel_name}\'' )
        return False

def select_by_preset(preset_num):
    """ loads a stream by its preset number """
    try:
        channel_name = DVB_config['presets'][ preset_num ]
        select_by_name(channel_name)
        # Rotating and saving recent preset:
        last = DVB_config['recent_presets']['last']
        if preset_num != last:
            DVB_config['recent_presets']['prev'] = last
            DVB_config['recent_presets']['last'] = preset_num
            dump_yaml( DVB_config, DVB_config_fpath )
        return True

    except:
        print( f'(init/DVB) error in preset # {preset_num}' )
        return False

def start():
    cmd = f'mplayer {options} -profile dvb -input file={input_fifo}'
    with open(redirection_path, 'w') as redirfile:
        sp.Popen( cmd.split(), shell=False, stdout=redirfile, stderr=redirfile )

def stop():
    # Killing our mplayer instance
    sp.Popen( ['pkill', '-KILL', '-f', 'profile dvb'] )
    sleep(.5)

def load_yaml(fpath):
    try:
        with open(fpath, 'r') as f:
            d = yaml.safe_load(f)
        return d
    except:
        print ( '(init/DVB) YAML error loading ' + fpath )

def dump_yaml(d, fpath):
    try:
        with open(fpath, 'w') as f:
            yaml.dump( d, f, default_flow_style=False )
    except:
        print ( '(init/DVB) YAML error dumping ' + fpath )

if __name__ == '__main__':

    ### Reading the DVB-T config file
    fpath = f'{UHOME}/ecapre/DVB-T.yml'
    try:
        DVB_config = load_yaml(fpath)
    except:
        print ( '(DVB-T.py) ERROR reading \'ecapre/DVB-T.yml\'' )
        sys.exit()


    ### Reading the command line
    if sys.argv[1:]:

        opc = sys.argv[1]

        # STARTS the script and optionally load a preset/name
        if opc == 'start':
            start()
            if sys.argv[2:]:
                opc2 = sys.argv[2]
                if opc2.isdigit():
                    select_by_preset( int(opc2) )
                elif opc2.isalpha():
                    select_by_name(opc2)
            else:
                if DVB_config['default_preset'] != 0:
                    select_by_preset( DVB_config['default_preset'] )
                else:
                    select_by_preset( DVB_config['recent_presets']['last'] )

        # STOPS all this stuff
        elif opc == 'stop':
            stop()

        # ON THE FLY changing to a preset number or rotates recent
        elif opc == 'preset':
            select_by_preset( int(sys.argv[2]) )
        elif opc == 'prev':
            select_by_preset( DVB_config['recent_presets']['prev'] )

        # ON THE FLY changing to a preset name
        elif opc == 'name':
            select_by_name( sys.argv[2] )

        elif '-h' in opc:
            print(__doc__)
            sys.exit()

        else:
            print( '(init/DVB) Bad option' )

    else:
        print(__doc__)
