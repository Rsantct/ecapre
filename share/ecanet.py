#!/usr/bin/env python3
""" A simple module to talk to the standard Ecasound TCP server
    https://manpages.debian.org/stable/ecasound/ecasound-iam.1.en.html
"""
import sys
import socket

def ecanet(command):
    """Sends commands to ecasound and accept results"""

    # note:   - ecasound needs CRLF
    #         - socket send and receive bytes (not strings),
    #           hence .encode() and .decode()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect( ('localhost', 2868) )
    s.send( (command + '\r\n').encode() )
    data = s.recv(8192).decode()
    s.close()
    return data

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

# To command line usage
if __name__ == '__main__':

    cmd = ' '.join( sys.argv[1:] )

    #print( 'command:', cmd ) # debug
    ans = ecanet(cmd)
    print( ans )
