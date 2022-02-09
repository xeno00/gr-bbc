# Author: James C Morrison
# Date: 1/1//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Implement the BBC codec with integer values rather than arrays
# PRIORITIZES SPEED OVER CLARITY
# WORKING MODEL

# TODO: add docstring headers
# TODO: figure out correct interfacing between py and c vars
# TODO: implement an iterative model rather than recursive
# TODO: Check encode_BBC implmentation
# TODO: Configure the glowwormDelBit calls
# TODO: write separate init() for pulling c file in? Move glow worm inits there with global memory for s,n,t,i,h?
# TODO: optomize complete substring deletion in encode - use the current state and add to it
# TODO: QUESTIONS
        # 1) should s, n, t, i, h be implemented in the caller functions rather than global memory? If we have local memory dont need delBit in encode
        # 2) does best practice have different variable names between caller and recursor
        # 3) how to prune the recursive tree for unnecessary calls?
        # 4) when should we deal with passing parameters vs implicit calculation of values?
        # 5) why do we need n to initialize the hash? Do we need to re-initialize for each size substring    ******
        #    or can we always initialize with 0?
        # 6) 


#uint64 s[32]; //buffer
#static uint64 n; //current string length
#uint64 t, i, h; //temporary
#const uint64 CHECKVALUE = 0xCCA4220FC78D45E0;

from math import log
import glowworm as gw
#import ctypes
#gw = ctypes.CDLL("secure comms python/glowworm.so")
DEFAULT_LENGTH = 5

def encode_BBC(message, num_checksum:int=0):
    # Configure message and length
    length = DEFAULT_LENGTH
    if(type(message)==str):
        length = len(message)*8 + num_checksum # get length (number of bits of message) while still string, assuming ACII so each letter is a byte
        message = int.from_bytes(message.encode(encoding='ascii'), byteorder='little') # convert to bytes
    message = message << num_checksum # add checksum bits and calculate the message length

    # Configure hash function and shift register
    shift_register = [0 for i in range(32)] # same as s in paper. needs 32 64b words.
    codeword = 0b0          # initialize the codeword to all 0's
    gw.init(shift_register) # initialize the hash # FLAG: check question 5 above

    # Set marks using array indexing with hash's output
    for i in range(length): # Set bounds (n) for each substring
        bit = message&(1<<i)
        mark_loc = gw.add_bit(bit, shift_register) % (2^(length+2))
        codeword |= (1<<mark_loc)
    
    # End state assums new shift register memory allocated inside of the decode function, since no delBit here.
    return codeword


def decode_BBC(codeword:int, length:int, num_checksum:int=0):
    # initialize the current assumed message and array of valid messages
    message = 0b0
    messages = []
    shift_register = [0 for i in range(32)]  # same as s in paper. needs 32 64b words.
    codeword = 0b0          # initialize the codeword to all 0's
    gw.init(shift_register) # initialize the hash # FLAG: check question 5 above
    # make the first recursive call to decode
    _decode_BBC_recursive(codeword, length, 0, message, messages, num_checksum, shift_register, t)
    return messages


def _decode_BBC_recursive(codeword:int, length:int, index, message:int, message_list:list, num_checksum:int, s, t):

    # base case, we've reached the end of the message tree with a valid message, add the message and remove checksum
    if index == (length-1):
        message_list.append((message>>num_checksum).to_bytes(length, byteorder='little').decode(encoding='ascii'))

    # test both possible next message values
    else:
        # assuming the next message bit is a 0, check for a mark in the codeword
        if codeword & (1<<gw.add_bit(0, s) ):
            _decode_BBC_recursive(codeword, length, hash, index+1, message, message_list)
        gw.del_bit(0, s, index+2, t)

        # assuming the next message bit is a 1, check for a mark in the codeword
        if codeword & (1<<gw.add_bit(1, s) ):
            _decode_BBC_recursive(codeword, length, hash, index+1, message+2**index, message_list)
        gw.del_bit(1, s, index+2, t)

# 0 1 0 1.... 7 bits with % 128