#!/usr/bin/env python3
"""
    usage:

    eca_fil_ctrl.py                         -->  dump running parameters
    eca_fil_ctrl.py  path/to/somePEQ.yml    -->  load parameters from a YAML file
    eca_fil_ctrl.py  on | off | toggle      -->  bypass

"""

import yaml
import sys
from os.path import expanduser

UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )

from ecanet import ecanet

def get_cop_idx(chain, cop_name):
    """ retrieves the list index of a cop (chain operator) full name,
        inside a chain
    """
    ecanet( f'c-select {chain}' )
    tmp = ecanet('cop-list').split('\r\n')
    # i.e: ['256 37 S', 'Amplify (dB),4-band parametric filter', '', '']
    tmp = tmp[1].split(',')
    try:
        return tmp.index(cop_name) + 1 # ecasound counts from 1 on
    except:
        return None

def get_copp_idx(chain, cop_name, copp_name):
    """ retrieves the index of a cop parameter
    """
    ecanet( f'c-select   {chain}' )
    ecanet( f'cop-select { get_cop_idx(chain, cop_name) }' )
    tmp = ecanet('copp-list').split('\r\n')
    tmp = tmp[1].split(',')
    try:
        return tmp.index(copp_name) + 1 # ecasound counts from 1 on
    except:
        return None

def get_cop(chain, cop_name):
    """ returns a dict of a cop parameters settings
    """
    result = {}
    cop_idx = get_cop_idx(chain, cop_name)

    # select our chain
    ecanet( f'c-select {chain}' )
    # select our cop
    ecanet( f'cop-select {cop_idx}' )
    # queries the list of parameters of the cop
    param_list = ecanet( 'copp-list' ).split('\r\n')[1].split(',')
    for i in range( len(param_list) ):
        ecanet( f'copp-select {i+1}' )
        value =  ecanet( f'copp-get' ).split('\r\n')[1]
        result[param_list[i]] = value
    return result

def set_cop(chain, cop_name, params):
    """ configure cop parameters at runtime
    """
    cop_idx = get_cop_idx(chain, cop_name)
    # select our chain
    ecanet( f'c-select {chain}' )
    # select the cop
    ecanet( f'cop-select {cop_idx}' )

    for p in params:
        # print('setting:', p, '-->', params[p])
        ecanet( f'copp-select {get_copp_idx(chain, cop_name, p)}' )
        ecanet( f'copp-set {str(params[p])}' )

def set_cop_bypass(chain, cop_name, mode='toggle'):
    cop_idx = get_cop_idx(chain, cop_name)
    # select our chain
    ecanet( f'c-select {chain}' )
    # select the cop
    ecanet( f'cop-select {cop_idx}' )
    # bypass
    ecanet( f'cop-bypass {mode}' )

def get_cop_bypass(chain, cop_name):
    cop_idx = get_cop_idx(chain, cop_name)
    # select our chain
    ecanet( f'c-select {chain}' )
    # select the cop
    ecanet( f'cop-select {cop_idx}' )
    # get bypass
    return ecanet( f'cop-is-bypassed' )

def print_fil(params):

    for k in 'Filter', 'Gain':
        print( f'{k}:'.ljust(8) + str(round(float(params[k]),2)) )

    line2 = ' '*15
    for n in ['1','2','3','4']:
        line2 += f'#{n}'.ljust(15)
    print(line2)



    for k in 'Section', 'Frequency', 'Bandwidth', 'Gain':
        line = f'{k}:'.ljust(15)
        for n in ['1','2','3','4']:
            value = round(float(params[f'{k} {n}']),2)
            line += str(value).ljust(15)
        print(line)

def read_fil_peq_yml_vertical(fname):
    # example
    #
    # L:
    #
    #     Filter      :   1
    #     Gain        :   0.0
    #
    #     Section 1   :   0
    #     Frequency 1 :   100
    #     Bandwidth 1 :   1.0
    #     Gain 1      :   0.0
    #
    #     Section 2   :   0
    #     Frequency 2 :   200
    #     Bandwidth 2 :   1.0
    #     Gain 2      :   0.0
    #
    #     Section 3   :   0
    #     Frequency 3 :   400
    #     Bandwidth 3 :   1.0
    #     Gain 3      :   0.0
    #
    #     Section 4   :   1
    #     Frequency 4 :   800
    #     Bandwidth 4 :   1.0
    #     Gain 4      :   9.1

    # ---> All parameters can be directly parsed

    with open(fname, 'r') as f:
        return yaml.load(f)

def read_fil_peq_yml_horizontal(fname):

    # example
    #
    # L:
    #
    #     Filter: 1.0
    #     Gain:   0.0
    #                     #N1            #N2            #N3            #N4
    #     Section N:      0.0            1.0            0.0            1.0
    #     Frequency N:    100.0          200.0          400.0          800.0
    #     Bandwidth N:    1.0            1.0            1.0            1.0
    #     Gain N:         0.0            1.5            0.0            -1.0

    # ---> It is necessary to map to an appropriate parameter dictionary

    # loading the YAML --> tmp
    with open(fname, 'r') as f:
        tmp =  yaml.load(f)

    params = {'L':{}, 'R':{}}

    # Mapping the tmp ---> params dict
    for ch in params.keys():
        for k in 'Filter', 'Gain':
            params[ch][k] = tmp[ch][k]
    for ch in params.keys():
        for k in 'Section N', 'Frequency N', 'Bandwidth N', 'Gain N':
            values = tmp[ch][k].split()
            for i in range(len(values)):
                params[ch][k.replace('N',str(i+1))] = values[i]
    return params

if __name__ == '__main__':


    if sys.argv[1:]:

        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

        elif sys.argv[1] in ['on', 'off', 'toggle']:
            for chain in ('L', 'R'):
                set_cop_bypass( chain,
                            '4-band parametric filter',
                            mode={ 'on':'off',
                                   'off':'on',
                                   'toggle':'toggle'}[ sys.argv[1] ]
                            )

        else:
            fil_peq_fname = sys.argv[1]
            for chain in ('L', 'R'):
                params = read_fil_peq_yml_horizontal(fil_peq_fname)[chain]
                set_cop(chain, '4-band parametric filter', params)

    else:
        for chain in ('L', 'R'):
            bypassed = ''
            tmp = get_cop_bypass(chain, '4-band parametric filter') \
                    .split('\r\n')[1]
            if int(tmp):
                bypassed = '(BYPASSED)'
            print(f'\n--- chain {chain}: {bypassed}')
            params = get_cop(chain, '4-band parametric filter')
            print_fil(params)

