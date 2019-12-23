# ecapre
hi-fi preamp based on ecasound


## Overview

This project is intended to work on a Mac OS, and of course under a Linux machine.

For Mac OS you need to use Homebrew and some tricks.

### Ecasound

On Mac OS install it from Homebrew

### JACK (Jack OSX)

https://jackaudio.org/downloads/

### JackBridge (formerly JackRouter)

JackRouter is the most important tool to enable Mac OS audio to be routed to the Jack audio server.

Unfortunatelly Jack OSX does not support anymore JackRouter.

Fortunatelly **madhatter68** has done a great work:

  **https://github.com/madhatter68/JackRouter**

### LADSPA plugins:

Under Linux simply use your package management tool

Under Mac OS you need to compile from source. We provide binaries here under `lib/ladspa`

  - shw
  - caps
  - fil-plugins

