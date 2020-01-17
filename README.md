# ecapre

hi-fi preamp based on Ecasound and optionally libzita-convolver.

## Overview

Features:

 - Calibrable volume control for reference SPL, with level dependant Loudness EQ compensation.
 - Bass, Treble, Balance
 - Adjustable 'Room gain' and 'House' curves, for subjective target 'in room' response.
 - Digital Room Correction: FIR convolution or IIR parametric eq filtering.
 - Black-box design, all runs as a background process.
 - Command line or web page for the preamp control.

This project is intended to work on a Mac OS, and of course under a Linux machine.

For a more precise, flexible and powerfull audio system, including FIR filtering, active loudspeaker xover, and more features, you can go to [pe.audio.sys](https://github.com/Rsantct/pe.audio.sys) (currently only under Linux).

## Mac OS

On Mac OS you need to use Homebrew and some tricks:

### Ecasound

Install it from Homebrew


### JACK (Jack OSX)

https://jackaudio.org/downloads/


### JackBridge (formerly JackRouter)

JackRouter is the key tool to able your Mac OS audio to be routed to the Jack audio server.

JACK OS works well, but you still need to route your Mac OS application's sound (coreaudio domain) to *ecapre* through by Jack. 

Unfortunatelly JackRouter is not mantained on Jack OSX anymore, but fortunatelly **madhatter68** has done a great work:

  **https://github.com/madhatter68/JackRouter**


### LADSPA plugins:

  - **caps.so**: the **CAPS** package (the **C*** **Audio Plugin Suite**)
  - **filters.so**: the FIL plugin from **Fons Adriaensen**

Under Linux simply use your package management tool

Under Mac OS you need to compile from source. We provide binaries here under `lib/ladspa`


### libzita-convolver (a FIR convolver)

If desired, we can use a FIR convolver for DRC (digital room correction) purposes.

**`libzita-convolver`** is a well known partitioned convolution engine library, from Fons Adriaensen.

http://kokkinizita.linuxaudio.org/linuxaudio/index.html

F.A. provides also **`jconvolver`**, a Jack wrapper to run lib-zitaconvolver in a sophisticated configuration similar to Brutefir. Unfortunatley `jconvolver` does not compiles well on Mac OS.

So we have chosen to use [x42/convoLV2](https://github.com/x42/convoLV2), a well known LV2 plugin based on libzita-convolver.

This LV2 plugin needs a host. As per my Ecasound version is unable to load any LV2 plugis, we have chosen [jalv](https://github.com/drobilla/jalv) a minimalist LV2 host that runs on Jack.


## Wiring

<a href="url"><img src="https://github.com/Rsantct/ecapre/blob/master/doc/ecapre%20jack%20wiring.png" align="center" width="640" ></a>

## Preamp control

The preamp can be controlled via command line, or through by a web page:

<a href="url"><img src="https://github.com/Rsantct/ecapre/blob/master/doc/ecapre%20control%20web.png" align="center" width="640" ></a>


    ~$ ./ecapre/share/services/ecapre_control.py help

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


    ~$ ./ecapre/share/services/ecapre_control.py state
    {'balance': 0.0, 'bass': 0.0, 'drc_set': 'drc1', 'house_curve': -2.0, 'input': 'desktopApps', 
    'level': -12.0, 'loudness_ref': 0.0, 'loudness_track': True, 'mono': False, 'muted': False, 
    'room_gain': 4.0, 'treble': 0.0}
    

