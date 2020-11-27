# ecapre

An hi-fi preamp based on Ecasound and optionally libzita-convolver.


## Overview

Features:

 - Calibrable volume control for reference SPL, with level dependant Loudness EQ compensation.
 - Bass, Treble, Balance
 - Adjustable 'Room gain' and 'House' curves, for subjective target 'in room' response.
 - Digital Room Correction: FIR convolution or IIR parametric eq filtering.
 - Black-box design, all runs as a background process.
 - Command line or web page for the preamp control.

This project is intended to work on a Mac OS, and of course under a Linux machine.

For a more precise, flexible and powerfull audio system, including FIR filtering, active loudspeaker xover, and more features, you can take a look into **[pe.audio.sys](https://github.com/Rsantct/pe.audio.sys)** (currently only under Linux).


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
    {'balance': 0.0, 'bass': 0.0, 'drc_set': 'nearfield', 'house_curve': -2.0, 'input': 'desktopApps', 
    'level': -12.0, 'loudness_ref': 0.0, 'loudness_track': True, 'mono': False, 'muted': False, 
    'room_gain': 4.0, 'treble': 0.0}
    

