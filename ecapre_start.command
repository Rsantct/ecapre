#!/bin/bash

echo "(!) REMEMBER TO USE THE CURRENT SAMPLE RATE WHEN STARTING JACKD"
FS=44100

# 'Built-in Microphone', 'Built-in Output'
CAP_DEV='AppleHDAEngineInput:1B,0,1,0:1'
PBK_DEV='AppleHDAEngineOutput:1B,0,1,1:0'

### 'USB Audio CODEC ' (Behringer UCA-202)
##CAP_DEV='AppleUSBAudioEngine:Burr-Brown from TI              :USB Audio CODEC :14100000:2'
##PBK_DEV='AppleUSBAudioEngine:Burr-Brown from TI              :USB Audio CODEC :14100000:1'

# This is for custom installed LADSPA plugins
export LADSPA_PATH=$LADSPA_PATH:"${HOME}"/ecapre/lib/ladspa

echo "(i) LADSPA_PATH=""$LADSPA_PATH"

# killing the control TCP server
pkill -f 'server.py ecapre_control'

# killing any ecasound an jack stuff
killall -KILL ecasound
killall -KILL JackBridge
killall -KILL jackdmp
#killall -KILL qjackctl

# Exit if just want to stop
if [[ $1 == 'stop' ]]; then
    echo "Stopped: Ecasound, JackBridge, Jack."
    exit 0
fi

# Jack
/usr/local/bin/./jackdmp \
    -R -d coreaudio -r "$FS" -p 128 -o 2 -i 2 \
    -C  "$CAP_DEV" \
    -P  "$PBK_DEV" &
sleep 2.0

# Qjackctl (optional just to check if things runs well)
#/Applications/Jack/qjackctl.app/Contents/MacOS/qjackctl &

# JackBridge (formerly JackRouter)
"${HOME}"/bin/JackBridge &
sleep .5

# Setting JackBridge as the default system's sound device
# https://github.com/deweller/switchaudio-osx
SwitchAudioSource -s 'JackBridge'

# Ecasound
ecasound  --server  -s:"${HOME}"/ecapre/share/ecapre.ecs  1>/dev/null 2>&1 &
sleep 3

# Eq10 needs some tuning at 31Hz band
"${HOME}"/ecapre/share/Eq10_31Hz.py 2.0

# Loading Eq4p plugin defaults (for Tones and Room gain)
tones_roomg_copID=1
"${HOME}"/ecapre/share/eca_Eq4p_ctrl.py \
          "${HOME}"/ecapre/share/eq/Eq4p_default.yml $tones_roomg_copID

# Restoring ecapre status
"${HOME}"/ecapre/ecapre_control.py restore

# Wiring:

#jack_connect  'system:capture_1'  'ecasound:in_1'  1>/dev/null 2>&1
#jack_connect  'system:capture_2'  'ecasound:in_2'  1>/dev/null 2>&1

jack_connect  'ecasound:out_1'  'system:playback_1'  1>/dev/null 2>&1
jack_connect  'ecasound:out_2'  'system:playback_2'  1>/dev/null 2>&1

jack_connect  'JackBridge #1:output_0'  'ecasound:in_1'  1>/dev/null 2>&1
jack_connect  'JackBridge #1:output_1'  'ecasound:in_2'  1>/dev/null 2>&1

# Launching the control TCP service
CONTROL_ADDR=$(grep control_addr $HOME/ecapre/ecapre.config | sed s/\ \ */\ /g | cut -d' ' -f2)
CONTROL_PORT=$(grep control_port $HOME/ecapre/ecapre.config | sed s/\ \ */\ /g | cut -d' ' -f2)
"${HOME}"/ecapre/share/server.py ecapre_control "$CONTROL_ADDR" "$CONTROL_PORT" &

