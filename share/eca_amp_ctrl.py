#!/usr/bin/env python3
"""
    Manage the raw level in dBFS at the Ecasound integrated preset effect 'eadb'
    -a:L    -eadb
    -a:R    -eadb

    Usage:     eca_amp_ctrl.py  [dBFS]

"""
import yaml
import sys
from os.path import expanduser
UHOME=expanduser('~')
sys.path.append( f'{UHOME}/ecapre/share' )
import ecanet as eca

with open(f'{UHOME}/ecapre/ecapre.config', 'r') as f:
    CFG = yaml.load(f)

def get_level(chain):
    """ This is for the -eadb preset as a chain operator.
        It works with dB values
    """
    level = None
    cmd = f'c-select {chain}'
    eca.ecanet(cmd)
    cmd = f'cop-get {CFG["AMP_COP_IDX"]},1'
    tmp = eca.ecanet(cmd).split('\r\n')
    level = float(tmp[1])
    return level

def set_level(chain, dBFS):
    """ This is for the -eadb preset as the first chain operator.
        It works with dB values
    """
    cmds = [ f'c-select {chain}', f'cop-set {CFG["AMP_COP_IDX"]},1,{str(dBFS)}' ]
    for cmd in cmds:
        eca.ecanet(cmd)

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

        elif isFloat(sys.argv[1]):
            for chain in ('L','R'):
                set_level(chain, sys.argv[1])

    else:
        for chain in ('L','R'):
            lev = get_level(chain)
            print( f'chain {chain}, cop# {CFG["AMP_COP_IDX"]}:  {lev} dBFS' )
