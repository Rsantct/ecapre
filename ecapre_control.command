#!/bin/bash

THIS_PATH="`dirname \"$0\"`"                # relative
THIS_PATH="`( cd \"$THIS_PATH\" && pwd )`"  # absolutized and normalized
"$THIS_PATH"/share/services/ecapre_control.py $1

