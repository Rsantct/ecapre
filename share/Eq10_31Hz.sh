#!/bin/bash

gain=$1
ecanetpath="${HOME}"/ecapre/share/ecanet.py

## Eq10 at 2th cop position
# L
$ecanetpath c-select L && $ecanetpath cop-select 2 && $ecanetpath copp-select 1 && \
$ecanetpath copp-set $gain

# R
$ecanetpath c-select R && $ecanetpath cop-select 2 && $ecanetpath copp-select 1 && \
$ecanetpath copp-set $gain

## Eq10 at 3th cop position
# L
$ecanetpath c-select L && $ecanetpath cop-select 3 && $ecanetpath copp-select 1 && \
$ecanetpath copp-set $gain

# R
$ecanetpath c-select R && $ecanetpath cop-select 3 && $ecanetpath copp-select 1 && \
$ecanetpath copp-set $gain
