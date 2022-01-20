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
        # 1) should s, n, t, i, h be implemented in the caller functions rather than global memory?
        # 2) does best practice have different variable names between caller and recursor
        # 3) how to prune the recursive tree for unnecessary calls?
        # 4) when should we deal with passing parameters vs implicit calculation of values?
        # 5) why do we need n to initialize the hash? Do we need to re-initialize for each size substring
        #    or can we always initialize with 0?
        # 6) 


#uint64 s[32]; //buffer
#static uint64 n; //current string length
#uint64 t, i, h; //temporary
#const uint64 CHECKVALUE = 0xCCA4220FC78D45E0;

import glowworm.c
from math import log


def encode_BBC(message:int, num_checksum:int):
    # add checksum bits and calculate the message length
    message = message << num_checksum
    length = len(message)
    t, i, h, n = 0          # temporary for hash
    shift_register = 0b0    # same as s in paper. needs 32b.
    codeword = 0b0          # initialize the codeword to all 0's
    glowwormInit(shift_register, n,t,i,h) # initialize the hash # FLAG: check question 5 above

    # Set marks using xor
    for n in range(length): # Set bounds (n) for each substring
        n += 1 # need this to not cut substrings too short, first substring length is 1, not 0
        # Build out the hash for each substring
        for j in range(n):
            glowwormAddBit(message&(1<<j), shift_register, n, t) # message&(1<<j) same as b in paper,
        codeword ^= shift_register
        # Delete progress in register before moving to different substring  #FLAG: This needs to go for additive faster approach
        for j in range(n):
            glowwormDelBit(message&(1<<(n-j)), shift_register, n, t) # work in reverse order
        
    return codeword


def decode_BBC(codeword:list):
    # initialize the current assumed message and array of valid messages
    message = []
    messages = []
    leng = log(len(codeword,2))
    t, i, h, n = 0          # temporary for hash
    shift_register = 0b0    # same as s in paper. needs 32b.
    codeword = 0b0          # initialize the codeword to all 0's
    glowwormInit(shift_register, n,t,i,h) # initialize the hash # FLAG: check question 5 above
    # make the first recursive call to decode
    _decode_BBC_recursive(codeword, leng, 0, message, messages)
    return messages


def _decode_BBC_recursive(codeword:list, length:int, index, message:int, message_list:list):

    # base case, we've reached the end of the message tree with a valid message, add the message and remove checksum
    if index == (length-1):
        message_list.append(message[:-2])

    # test both possible next message values
    else:
        # assuming the next message bit is a 0, check for a mark in the codeword
        if codeword[hash(message.append(0))]:
            _decode_BBC_recursive(codeword, length, hash, index+1, message.append(0), message_list)
        if codeword[hash(message.append(1))]:
            _decode_BBC_recursive(codeword, length, hash, index+1, message.append(1), message_list)
    # Change shift regeister state for other branch
    glowwormDelBit()
