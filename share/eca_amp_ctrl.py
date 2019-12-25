#!/usr/bin/env python3
"""
    An Ecasound integrated preset effect to adjust the preamp level in dB
    As the wanted 12 dB of HEADROOM, and the wanted -20dB initial level:
    -a:L    -eadb:-32.0
    -a:R    -eadb:-32.0

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
    """ This is for the -eadb preset as chain operator.
        It works with dB values
    """
    level = None
    cmd = f'c-select {chain}'
    eca.ecanet(cmd)
    cmd = f'cop-get {CFG["AMP_COP_IDX"]},1'
    tmp = eca.ecanet(cmd).split('\r\n')
    level = float(tmp[1])
    return level

if __name__ == '__main__':

    if sys.argv[1:]:

        # -h ---> help
        if '-h' in sys.argv[1][0:]:
            print(__doc__)
            exit()

    else:
        for chain in ('L','R'):
            lev = get_level(chain)
            print( f'{chain}, cop# {CFG["AMP_COP_IDX"]}: {lev}' )
