# ecapre
hi-fi preamp based on Ecasound and libzita-convolver (LV2 plugin implemented at https://github.com/x42/convoLV2)


## Overview

Features:

 - Calibrable volume control for reference SPL, with level dependant Loudness EQ compensation.
 - Bass, Treble, Balance
 - Adjustable 'Room gain' and 'House' curves, for subjective target 'in room' response.
 - Digital Room Correction: FIR convolution or IIR parametric eq filtering.

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

**libzita-convolver** is a well known partitioned convolution engine library, from Fons Adriaensen.

http://kokkinizita.linuxaudio.org/linuxaudio/index.html

F.A. provides also **`jconvolver`**, a Jack wrapper to run lib-zitaconvolver in a sophisticated configuration similar to Brutefir. Unfortunatley `jconvolver` does not compiles well on Mac OS.

So we have chosen to use [x42/convoLV2](https://github.com/x42/convoLV2), a well known LV2 plugin based on libzita-convolver.

This LV2 plugin needs a host. As per my Ecasound version is unable to load any LV2 plugis, we have chosen [jalv](https://github.com/drobilla/jalv) a minimalist LV2 host that runs on Jack.


## Wiring

<a href="url"><img src="https://github.com/Rsantct/ecapre/blob/master/doc/ecapre%20jack%20wiring.png" align="center" width="640" ></a>






