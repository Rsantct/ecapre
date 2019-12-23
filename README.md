# ecapre
hi-fi preamp based on ecasound


## Overview

Features:

 - Calibrable volume control for reference SPL, with Loudness compensation
 - Bass, Treble, Balance
 - Room gain and House curves
 - Parametric EQ stage for Digital Room Correction purposes

This project is intended to work on a Mac OS, and of course under a Linux machine.

For Mac OS you need to use Homebrew and some tricks:

### Ecasound

On Mac OS install it from Homebrew


### JACK (Jack OSX)

https://jackaudio.org/downloads/


### JackBridge (formerly JackRouter)

JackRouter is the most important tool to able your Mac OS audio to be routed to the Jack audio server.

JACK OS works well, but you need to route your Mac OS application's sound (coreaudio domain) to *ecapre* through by Jack. 
Unfortunatelly Jack OSX does not support anymore JackRouter.

Fortunatelly **madhatter68** has done a great work:

  **https://github.com/madhatter68/JackRouter**


### LADSPA plugins:

  - shw
  - caps
  - fil-plugins

Under Linux simply use your package management tool

Under Mac OS you need to compile from source. We provide binaries here under `lib/ladspa`


