#!/usr/bin/env python3
""" Trying to update the FIR drc_set from the convoLV2 plugin settings
"""
import yaml
from os.path import expanduser
UHOME=expanduser('~')
STATE_FNAME      =  f'{UHOME}/ecapre/.state.yml'
LV2_PRESET_FNAME =  f'{UHOME}/ecapre/share/eq/drc.preset.lv2/drc.ttl'

def find_convoLV2_drc():
    with open(LV2_PRESET_FNAME, 'r') as f:
        lines = f.read().split('\n')
    drc_set =''
    for line in lines:
        if '.wav' in line:
            drc_set = line.split('.wav')[0].split('<')[-1].replace('drc_','')
    return drc_set


if __name__ == '__main__':

    with open(STATE_FNAME, 'r') as f:
        state = yaml.safe_load(f)

    drc_set = find_convoLV2_drc()
    if drc_set != '':
        state["drc_set"] = drc_set
        with open(STATE_FNAME, 'w') as f:
            yaml.dump( state, f, default_flow_style=False )
