#!/bin/bash

echo "(!) REMEMBER TO USE THE CURRENT SAMPLE RATE WHEN STARTING JACKD"
FS=44100


# This is for custom installed LADSPA plugins
export LADSPA_PATH=$LADSPA_PATH:"${HOME}"/ecapre/lib/ladspa

echo "(i) LADSPA_PATH=""$LADSPA_PATH"

# killing any ecasound an jack
killall -KILL ecasound
killall -KILL JackBridge
killall -KILL jackdmp

# Exit if just want to stop
if [[ $1 == 'stop' ]]; then
    echo "Stopped: Ecasound, JackBridge, Jack."
    exit 0
fi
sleep 3

# Jack
/usr/local/bin/./jackdmp -R -d coreaudio -r "$FS" -p 128 -o 2 -i 2 \
-C AppleHDAEngineInput:1B,0,1,0:1 -P AppleHDAEngineOutput:1B,0,1,1:0 &
sleep 3

# JackRouter
"${HOME}"/bin/JackBridge &
sleep .5

# Ecasound
ecasound  --server  -s:"${HOME}"/ecapre/share/eq/ecapre.ecs  1>/dev/null 2>&1 &
sleep 3


# Loading Eq4p plugin defaults (tones and target bands)
"${HOME}"/ecapre/share/eca_Eq4p_ctrl.py \
          "${HOME}"/ecapre/share/eq/Eq4p_default.yml


# Restoring ecapre status
"${HOME}"/ecapre/ecapre_control.py restore

# Wiring:

#jack_connect  'system:capture_1'  'ecasound:in_1'  1>/dev/null 2>&1
#jack_connect  'system:capture_2'  'ecasound:in_2'  1>/dev/null 2>&1

jack_connect  'ecasound:out_1'  'system:playback_1'  1>/dev/null 2>&1
jack_connect  'ecasound:out_2'  'system:playback_2'  1>/dev/null 2>&1

jack_connect  'JackBridge #1:output_0'  'ecasound:in_1'  1>/dev/null 2>&1
jack_connect  'JackBridge #1:output_1'  'ecasound:in_2'  1>/dev/null 2>&1
