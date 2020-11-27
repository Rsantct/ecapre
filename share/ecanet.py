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

def get_cop_idxs(chain, cop_name):
    """ retrieves the list indexes used by a full named chain operator (aka cop),
        inside the given chain
    """
    ecanet( f'c-select {chain}' )
    tmp = ecanet('cop-list').split('\r\n')
    # i.e: ['256 37 S', 'copName1,copName2,copName3', '', '']
    cops = tmp[1].split(',')
    try:
        idxs = [i for i in range(len(cops)) if cops[i] == cop_name]
        # ecasound counts from 1 on
        idxs = [str(x+1) for x in idxs]
        return idxs
    except:
        return None

def get_copp_idx(chain, cop_idx, copp_name):
    """ retrieves the index of a cop parameter (aka copp)
    """
    ecanet( f'c-select   {chain}' )
    ecanet( f'cop-select {cop_idx}' )
    tmp = ecanet('copp-list').split('\r\n')
    tmp = tmp[1].split(',')
    try:
        return tmp.index(copp_name) + 1 # ecasound counts from 1 on
    except:
        return None

def get_cop(chain, cop_idx):
    """ returns a dict of a cop parameters settings
    """
    result = {}

    # select the chain
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

def set_cop(chain, cop_idx, params):
    """ configure cop parameters at runtime
    """
    # select the chain
    ecanet( f'c-select {chain}' )
    # select the cop
    ecanet( f'cop-select {cop_idx}' )

    for p in params:
        # print('setting:', p, '-->', params[p])
        ecanet( f'copp-select {get_copp_idx(chain, cop_idx, p)}' )
        ecanet( f'copp-set {str(params[p])}' )

def set_cop_bypass(chain, cop_idx, mode='toggle'):
    # select our chain
    ecanet( f'c-select {chain}' )
    # select the cop
    ecanet( f'cop-select {cop_idx}' )
    # bypass
    ecanet( f'cop-bypass {mode}' )

def get_cop_bypass(chain, cop_idx):
    # select the chain
    ecanet( f'c-select {chain}' )
    # select the cop
    ecanet( f'cop-select {cop_idx}' )
    # get bypass
    return {'0':False, '1':True}[ ecanet( f'cop-is-bypassed' ).split('\r\n')[1] ]

# To command line usage
if __name__ == '__main__':

    cmd = ' '.join( sys.argv[1:] )

    #print( 'command:', cmd ) # debug
    ans = ecanet(cmd)
    print( ans )
