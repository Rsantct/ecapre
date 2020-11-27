## Python3

Modules needed:

    pip3 install   pyaml JACK-Client


## Ecasound

### MacOs

Get it from Homebrew

    brew install ecasound


## Jack

https://jackaudio.org/downloads/

### MacOS

2020-nov. Homebrew provides Jack1 with Ecasound, but it does not work in Mojave, so uninstall it:
    
    brew uninstall jack (force to ignore dependencies)
    
then install JackOSX.0.92_b3.pkg from

    https://ccrma.stanford.edu/software/jacktrip/osx/index.html


## MacOS: Jack to Coreaudio bridge

You need your main sound card to be released as your **Coreaudio** system default, leaving the card to be used by **JACK**.

Then you need to load a virtual device **JackRouter**: is the key tool to able your MacOS audio to be routed to JACK.

Unfortunatelly JackRouter is not mantained on Jack OSX package anymore, but fortunatelly **madhatter68** has done a great work:

  **https://github.com/madhatter68/JackRouter**


### LADSPA plugins:

  - **caps.so**: the **CAPS** package (the **C*** **Audio Plugin Suite**)
  - **filters.so**: the FIL plugin from **Fons Adriaensen**


#### Linux

simply use your package management tool

#### Mac OS

you need to compile from source. We provide binaries here under `lib/ladspa`


### FIR convolver

If desired, we can use a FIR convolver for DRC (digital room correction) purposes.

We choose **libzita-convolver**, a well known partitioned convolution engine library, by Fons Adriaensen.

http://kokkinizita.linuxaudio.org/linuxaudio/index.html


#### Linux

**jconvolver** is a Jack wrapper to run lib-zitaconvolver in a sophisticated configuration similar to Brutefir.

(Unfortunatley `jconvolver` does not compiles well on Mac OS)

#### MacOS

A well known LV2 plugin based on libzita-convolver: [x42/convoLV2](https://github.com/x42/convoLV2)

This LV2 plugin needs a host. As per my Ecasound version is unable to load any LV2 plugins, we have chosen [drobilla/jalv](https://github.com/drobilla/jalv) a minimalist LV2 host that runs on Jack.


## Wiring

<a href="url"><img src="https://github.com/Rsantct/ecapre/blob/master/doc/ecapre%20jack%20wiring.png" align="center" width="640" ></a>


