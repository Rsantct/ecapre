#!/bin/bash

CFILE="$HOME"/ecapre/ecapre.config

# This is for custom installed LADSPA plugins
export LADSPA_PATH=$LADSPA_PATH:"${HOME}"/ecapre/lib/ladspa
echo "(i) LADSPA_PATH=""$LADSPA_PATH"

# killing the IR receiver
pkill -KILL -f 'ir.py'

# killing the WEB PAGE server
pkill -KILL -f 'node ecapre'

# killing the CONTROL and AUX TCP servers
pkill -f 'server.py ecapre_control'
pkill -f 'server.py ecapre_aux'

# killing any ecasound an jack stuff
killall -KILL jalv
killall -KILL ecasound
killall -KILL JackBridge
killall -KILL jackdmp
#killall -KILL qjackctl
sleep 1

# Exit if just want to stop
if [[ $1 == 'stop' ]]; then
    # Setting JackBridge as the default system's sound device
    # https://github.com/deweller/switchaudio-osx
    SwitchAudioSource -s 'Built-in Output'
    osascript -e "set Volume 3.5"
    # Close any safari tab
    "${HOME}"/ecapre/share/scripts/ecapre_web.command stop
    clear
    echo "Stopped: Ecasound, JackBridge, Jack."
    echo
    echo "                                      "
    echo "     --  ---  --   --   --   -- ---   "
    echo "    |__   |  |  | |__| |__| |   |  |  "
    echo "       \  |  |  | |    |    |-- |  |  "
    echo "    ___|  |  |__| |    |    |__ |__/  "
    echo "                                      "
    sleep 3
    exit 0
fi

# Jack
FS=$(grep ^FS: $CFILE | cut -d":" -f2)
PERIOD_SIZE=$(grep ^PERIOD_SIZE: $CFILE | cut -d":" -f2)
PBK_PORTS=$(grep ^PBK_PORTS: $CFILE | cut -d":" -f2)
CAP_PORTS=$(grep ^CAP_PORTS: $CFILE | cut -d":" -f2)
PBK_DEVICE=$(grep ^PBK_DEVICE: $CFILE | cut -d":" -f2-)
CAP_DEVICE=$(grep ^CAP_DEVICE: $CFILE | cut -d":" -f2-)
JACK_OPT=" -R -d coreaudio"
JACK_OPT+=" --rate ""$FS"" --period ""$PERIOD_SIZE"
JACK_OPT+=" -P ""$PBK_DEVICE"" -o ""$PBK_PORTS"
if [[ "$CAP_PORTS" -ge 2 ]]; then
    JACK_OPT+=" -C ""$CAP_DEVICE"" -i ""$CAP_PORTS"
fi
/usr/local/bin/jackdmp $JACK_OPT &
sleep 2.0

# Qjackctl (optional just to check if things runs well)
#/Applications/Jack/qjackctl.app/Contents/MacOS/qjackctl &

# JackBridge (formerly JackRouter)
"${HOME}"/bin/JackBridge &
sleep .5

# Setting JackBridge as the default system's sound device
# https://github.com/deweller/switchaudio-osx
SwitchAudioSource -s 'JackBridge'

# Setting the Integrated Output level to max so that
# ecapre will assume the volume control
osascript -e "set Volume 10"

# jalv (a LV2 host for jack)
jalv -i -n convoLV2 -l "${HOME}"/ecapre/share/eq/drc.preset.lv2/drc.ttl \
http://gareus.org/oss/lv2/convoLV2#Stereo &

# Ecasound
ecasound  --server  -s:"${HOME}"/ecapre/share/ecapre.ecs  1>/dev/null 2>&1 &
sleep 3

# Eq10 needs some tuning at 31Hz band
"${HOME}"/ecapre/share/Eq10_31Hz.py 2.0

# Loading Eq4p plugin defaults (for Tones and Room gain)
tones_roomg_copID=1
"${HOME}"/ecapre/share/eca_Eq4p_ctrl.py \
          "${HOME}"/ecapre/share/eq/Eq4p_default.yml $tones_roomg_copID

# Trying to update the FIR drc_set from the convoLV2 plugin settings
"${HOME}"/ecapre/share/LV2drc2state.py

# Restoring Ecasound stages as per ecapre/.state.yml on disk
"${HOME}"/ecapre/share/services/ecapre_control.py restore

# Wiring:
jack_connect  'JackBridge #1:output_0'  'convoLV2:in_1'     1>/dev/null 2>&1
jack_connect  'JackBridge #1:output_1'  'convoLV2:in_2'     1>/dev/null 2>&1
jack_connect  'convoLV2:out_1'          'ecasound:in_1'     1>/dev/null 2>&1
jack_connect  'convoLV2:out_2'          'ecasound:in_2'     1>/dev/null 2>&1
jack_connect  'ecasound:out_1'          'system:playback_1' 1>/dev/null 2>&1
jack_connect  'ecasound:out_2'          'system:playback_2' 1>/dev/null 2>&1

# Launching the control TCP service
CONTROL_ADDR=$(grep control_addr $HOME/ecapre/ecapre.config | sed s/\ \ */\ /g | cut -d' ' -f2)
CONTROL_PORT=$(grep control_port $HOME/ecapre/ecapre.config | sed s/\ \ */\ /g | cut -d' ' -f2)
"${HOME}"/ecapre/share/server.py ecapre_control "$CONTROL_ADDR" "$CONTROL_PORT" 1>/dev/null 2>&1 &

# Launching the aux TCP service
AUX_ADDR=$(grep aux_addr $HOME/ecapre/ecapre.config | sed s/\ \ */\ /g | cut -d' ' -f2)
AUX_PORT=$(grep aux_port $HOME/ecapre/ecapre.config | sed s/\ \ */\ /g | cut -d' ' -f2)
"${HOME}"/ecapre/share/server.py ecapre_aux "$AUX_ADDR" "$AUX_PORT" 1>/dev/null 2>&1 &

# Launching the control WEB PAGE server
node "${HOME}"/ecapre/share/www/ecapre_node.js 1>/dev/null 2>&1 &

# Launching the control WEB page
"${HOME}"/ecapre/share/scripts/ecapre_web.command

# Launching the IR receiver
"${HOME}"/ecapre/share/scripts/ir.py 1>/dev/null 2>&1 &

clear
echo "                                      __      "
echo "     --   |  |  |  |  |  |  |  |  |  |        "
echo "    |  |  |  |  |\\ |  |\\ |  |  |\\ |  | _   "
echo "    |--   |  |  | \\|  | \\|  |  | \\|  |  \\ "
echo "    |  \\  |__|  |  |  |  |  |  |  |  |__|    "
echo ""
echo "--------------------------------------------------------------------------"
echo "(!) Remember to check that the current sample rate of 'JackBridge' under"
echo "    your 'Audio MIDI Configuration' settings matches to the one used"
echo "    by jackdmp, i.e. the FS: xxxxxx value inside the 'ecapre.config' file."
echo "--------------------------------------------------------------------------"

sleep 10
exit 0


