#!/usr/bin/env python3
"""
    Usagex:      start.py   start|stop
"""
import sys
import os
import subprocess as sp
from time import sleep
import yaml
import jack

UHOME = os.path.expanduser('~')
sys.path.append(f'{UHOME}/ecapre/share')


CFILE = f'{UHOME}/ecapre/ecapre.config'
with open(CFILE, 'r') as f:
    CONFIG = yaml.safe_load(f)


def jconnect(p1, p2, mode='connect'):
    JCLI = jack.Client('tmp', no_start_server=True)
    srcs    = JCLI.get_ports(p1, is_output=True)
    dests   = JCLI.get_ports(p2, is_input=True)
    result = True
    for s, d in zip(srcs, dests):
        try:
            if mode == 'connect':
                JCLI.connect(s, d)
            elif mode == 'disconnect':
                JCLI.disconnect(s, d)
        except:
            result = False
    JCLI.close()
    return result


def killbill():

    # killing the IR receiver
    sp.Popen( "pkill -KILL -f 'ir.py'", shell=True)
    # killing the WEB PAGE server
    sp.Popen( "pkill -KILL -f 'ecapre_node'", shell=True)
    # killing the CONTROL and AUX TCP servers
    sp.Popen( "pkill -KILL -f 'server.py ecapre_control'", shell=True)
    sp.Popen( "pkill -KILL -f 'server.py ecapre_aux'", shell=True)
    # killing any Ecasound an Jack stuff
    sp.Popen( "pkill -KILL -f 'jackd'", shell=True)
    sp.Popen( "pkill -KILL -f 'jalv'", shell=True)
    sp.Popen( "pkill -KILL -f 'ecasound'", shell=True)
    sp.Popen( "pkill -KILL -f 'JackBridge'", shell=True)
    sp.Popen( "pkill -KILL -f 'qjackctl'", shell=True)

    sleep(.2)

    # Close Safari tabs
    close_safari_tabs()

    # Restoring normal output
    sp.Popen( "SwitchAudioSource -s 'Built-in Output'", shell=True)
    sp.Popen( "osascript -e 'set Volume 3.5'", shell=True)

    print('''
    Stopped: Ecasound, JackBridge, Jack.


         --  ---  --   --   --   -- ---
        |__   |  |  | |__| |__| |   |  |
           \  |  |  | |    |    |-- |  |
        ___|  |  |__| |    |    |__ |__/
                                            ''')


# JACK
def run_jackd(qjackctl=False):

    # See doc/README.md for issues with Jack on MacOS

    def check_jack():
        n = 10
        while n:
            try:
                jc = jack.Client('tmp', no_start_server=True)
                jc.close()
                break
            except:
                sleep(.5)
                n -= 1
        if n:
            sleep(.2)
            return True
        else:
            return False


    jopts =  f'-R -L 2 -d coreaudio'
    jopts += f' --rate {CONFIG["FS"]} --period {CONFIG["PERIOD_SIZE"]}'
    jopts += f' -P {CONFIG["PBK_DEVICE"]} -o {CONFIG["PBK_PORTS"]}'
    if CONFIG["CAP_PORTS"]:
        jopts += f' -C {CONFIG["CAP_DEVICE"]} -i {CONFIG["CAP_PORTS"]}'
    sp.Popen(f'jackd {jopts}', shell=True)

    if not check_jack():
        raise ValueError('ERROR with JACK')
    else:
        print('(ecapre) JACK started :-)')

    # JackBridge (formerly JackRouter), the Coreaudio to JACK bridge
    if sp.run(f'{UHOME}/bin/JackBridge &', shell=True).returncode:
        raise ValueError('Cannot run JackBridge')
    sleep(.2)

    # Setting the Integrated Output level to max so that
    # ecapre will assume the volume control
    if sp.run(['osascript',  '-e' , '"set Volume 10"']).returncode:
        raise ValueError('Cannot set volume')

    # Setting JackBridge as the default system's sound device
    # https://github.com/deweller/switchaudio-osx
    if sp.run(['SwitchAudioSource',  '-s' , 'JackBridge']).returncode:
        raise ValueError('Cannot switch to JackBridge')

    if qjackctl:
        sp.Popen('/Applications/qjackctl.app/Contents/MacOS/qjackctl', shell=True)


# jalv (a LV2 host for Jack)
def run_jalv():
    """ jalv is a LV2 host for
    """
    fconfig = f'{UHOME}/ecapre/share/eq/drc.preset.lv2/drc.ttl'
    lv2url = 'http://gareus.org/oss/lv2/convoLV2' #Stereo
    sp.Popen(f'jalv -i -n convoLV2 -l "{fconfig}" {lv2url}', shell=True)
    sleep(.2)


# Ecasound
def run_ecasound():

    ecacmd = f'ecasound --server -s:{UHOME}/ecapre/share/ecapre.ecs'

    # We need to provide custom LADSPA path to the ecasound shell:
    envladspa = 'export LADSPA_PATH=$LADSPA_PATH:"${HOME}"/ecapre/lib/ladspa'
    envlv2    = 'export LV2_PATH="$LV2_PATH":"$HOME"/Library/Audio/Plug-Ins/LV2:/Library/Audio/Plug-Ins/LV2:/usr/local/lib/lv2:/usr/lib/lv2'

    # ecasound stdout will not be displayed, only stderr
    cmd = f'{envladspa} && {envlv2} && {ecacmd} 1>/dev/null'
    sp.Popen( cmd, shell=True)

    # wait 5 sec for ecasound to be ready
    n = 10
    while n:
        if not sp.run( 'echo engine-status | nc -c localhost 2868',
                        shell=True).returncode:
            break
        sleep(.5)
    if not n:
        raise ValueError('(!) ERROR running ecasoud')

    # Importing custom ecasound modules
    import eca_Eq10_ctrl as eq10
    import eca_Eq4p_ctrl as eq4p

    # compensates the Eq10 low end roll-off at 31 Hz band, for all Eq10 stages
    eq10.low_end_tuning(cop='all')

    # Loading Eq4p plugin defaults (for Tones and Room gain)
    eq4p.load_curve( CONFIG["TONE_COP_IDX"],
                     f'{UHOME}/ecapre/share/eq/Eq4p_default.yml' )


# Launching the control and aux TCP services
def run_servers():

    addr = CONFIG["control_addr"]
    port = CONFIG["control_port"]
    sp.Popen( f'{UHOME}/ecapre/share/server.py ecapre_control {addr} {port}', shell=True)
    addr = CONFIG["aux_addr"]
    port = CONFIG["aux_port"]
    sp.Popen( f'{UHOME}/ecapre/share/server.py ecapre_aux {addr} {port}', shell=True)


# Launching the control WEB PAGE server
def run_web():

    # Node web server
    sp.Popen( f'node {UHOME}/ecapre/share/www/ecapre_node.js', shell=True)
    # Open control web on Safari
    sp.Popen( f'{UHOME}/ecapre/share/scripts/ecapre_web.command', shell=True)


# Launching the IR receiver
def ir_receiver():
    sp.Popen(f'{UHOME}/ecapre/share/scripts/ir.py', shell=True)


def show_msg():

    print("""
                                      __
     --   |  |  |  |  |  |  |  |  |  |
    |  |  |  |  |\\ |  |\\ |  |  |\\ |  | _
    |--   |  |  | \\|  | \\|  |  | \\|  |  \\
    |  \\  |__|  |  |  |  |  |  |  |  |__|

    --------------------------------------------------------------------------
    (!) Remember to check that the current sample rate of 'JackBridge' under
        your 'Audio MIDI Configuration' settings matches to the one used
        by jackdmp, i.e. the FS: xxxxxx value inside the 'ecapre.config' file.
    --------------------------------------------------------------------------
    """)


def close_safari_tabs():
    cmd =   'osascript -e'
    cmd +=  ' \'tell application "Safari" to delete (every tab of every window'
    cmd +=  ' where its name contains "ecapre")\''
    sp.Popen(cmd, shell=True)


def run_audio():

    # JACK
    run_jackd(qjackctl=True)

    # JALV
    run_jalv()

    # ECASOUND
    run_ecasound()

    # Trying to update the FIR drc_set from the convoLV2 plugin settings
    sp.run( f'{UHOME}/ecapre/share/LV2drc2state.py', shell=True)

    # Restore last state from disk to Ecasound:
    sp.run( f'{UHOME}/ecapre/share/services/ecapre_control.py restore'.split() )

    # Wiring (loopback is the preamp entry point, ecasound is the output)
    jconnect('JackBridge',  'loopback')
    jconnect('loopback',    'convoLV2')
    jconnect('convoLV2',    'ecasound')
    jconnect('ecasound',    'system')


if __name__ == '__main__':

    if not sys.argv[1:]:
        print(__doc__)
        sys.exit()

    elif sys.argv[1] == 'stop':
        killbill()
        sys.exit()

    elif sys.argv[1] == 'start':
        killbill()
        run_audio()
        run_servers()
        run_web()
        #ir_receiver()
        show_msg()

    else:
        print(__doc__)
