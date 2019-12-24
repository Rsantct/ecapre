# ecapre
hi-fi preamp based on ecasound


## Overview

Features:

 - Calibrable volume control for reference SPL, with level dependant Loudness EQ compensation.
 - Bass, Treble, Balance
 - Adjustable 'Room gain' and 'House' curves, for subjective target 'in room' response.
 - Parametric EQ stage for Digital Room Correction purposes (room modes EQ).

This project is intended to work on a Mac OS, and of course under a Linux machine.

A more precise, flexible and powerfull audio system, including FIR filtering, active loudspeaker xover, and more you can go to [pe.audio.sys](https://github.com/Rsantct/pe.audio.sys) (currently under Linux only).

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
  - **mbeq_1197.so**: from **Steve Harris**'s swh plugins package

Under Linux simply use your package management tool

Under Mac OS you need to compile from source. We provide binaries here under `lib/ladspa`


