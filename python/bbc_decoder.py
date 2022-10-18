#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr
from math import ceil

DEFAULT_CHECKSUM = 0

class bbc_decoder(gr.interp_block):
    """
    docstring for block bbc_decoder
    """
    def __init__(self, message_length=2**7, codeword_length=2**17):
        gr.interp_block.__init__(self,
            name="bbc_decoder",
            in_sig=[(np.byte, codeword_length)],
            out_sig=[(np.byte, message_length)],
            interp = 1)
        
        self.set_relative_rate(1)
        
        self.myDecoder = Decoder(message_length*8, codeword_length*8, DEFAULT_CHECKSUM) # Bytes to bits


    # Use BBC to decode the incoming codeword vectors
    def work(self, input_items, output_items):
        print("work called")
        # Pull packet from the queue
        packet = input_items[0][:][0]
        
        # Check for a nonzero codeword
        #if sum(packet is not None):
            
        #print("\nDecoder heard codeword ", packet)
        result = self.myDecoder.decode(packet)
        interp = len(result)
            
        #Check for a decoded message
        if interp > 0:
                
            # Define the number of outputs
            self.set_relative_rate(interp)
                
            # Assign outputs iteratively
            for j in range(interp):
                try:
                    output_items[0][j][:] = result[j]
                    print("BBC decoder found and passed", result[j])
                except:
                        # Decrement the expected output size
                        #interp -= 1
                        print("\nDebug: Fix integer max in byte output of decoder. Failed to output:", result[j])
            #return len(output_items) #interp
        return len(output_items)

###############################################################################
class Decoder:
    def __init__(self, MSG_LEN, COD_LEN, CHK_LEN = 0):
        self.message_list = []
        self.num_checksum = DEFAULT_CHECKSUM
        self.shift_register = self.init_shift_register()
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN
        self.CHK_LEN = CHK_LEN #Is added to MSG_LEN, not subtracted from
        self.n = 0

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        init(shift_register)
        return (shift_register)

    #DECODE ITERATIVELY
    #Note that   D[n]   is the same as    memoryview(message)[int((self.n - self.n%8)/8)]
    def decode(self, packet):
        # Initialize variables
        self.message_list = []
        message = bytearray(ceil((self.MSG_LEN + self.CHK_LEN)/8))      #Bits to Bytes
        #memoryview(message)[int((self.n - self.n%8)/8)] = 1         # TODO: debug initialization for D[n]
        
        while True:
            # Check for mark corresponding to encoding D[n], beginning with a 0
            prop_bit = (memoryview(message)[int((self.n - self.n%8)/8)]>>(self.n%8)) & 0b1      # Find the proposed bit from previous execution, aka D[n]
            val = (add_bit(prop_bit, self.shift_register) % (self.COD_LEN))                  # Mark location from glowworm
            bit = (memoryview(packet)[int((val-val%8)/8)]>>(val%8)) & 0b1                       # Logical AND to determine if present in packet/codeword

            # If the mark is present... explore
            if bit==1:
                # message is complete, write to buffer
                if self.n == (self.MSG_LEN + self.CHK_LEN - 1):
                    #print(message)
                    valid_msg = bytearray(memoryview(message)[0:self.MSG_LEN - 1 - self.num_checksum])
                    self.message_list.append(bytes(message))
                    bit = 0
                    #TODO: Flow control statement?
                    
                # message is incomplete, continue assuming next bit is 0
                elif self.n < (self.MSG_LEN + self.CHK_LEN - 1):
                    self.n += 1
                    memoryview(message)[int((self.n - self.n%8)/8)] &= (0xff ^ (1<<self.n%8))
                    continue
                # In case something bad happens
                else:
                    raise Exception("107: Message completion led to over-indexing")


            # If the mark is not present... backtrace
            # Settle on an earlier 0 to change it to a 1 and pursue that tree
            if bit!=1:
                # delete checksum bits
                while self.n >= self.MSG_LEN: 
                    del_bit(0, self.shift_register)
                    self.n -= 1
                    
                # delete 1's until a 0 is encountered
                while self.n >=0 and (((memoryview(message)[int((self.n - self.n%8)/8)]>>(self.n%8)) & 0b1 )==1):
                    del_bit(1, self.shift_register)
                    memoryview(message)[int((self.n - self.n%8)/8)] &= (0xff ^ (1<<self.n%8))
                    self.n -= 1
                        
                if self.n < 0: #Packet is fully decoded
                    #print("BBC Decoder line 116: Packet is fully decoded. ")
                    break #proceed with next packet

                else: # Move over to the 1 branch of current search
                    del_bit(0, self.shift_register)
                    memoryview(message)[int((self.n - self.n%8)/8)] |= (1<<self.n%8)
        #for x in self.message_list:
        #    print("Non-iterative output: ",x)
        return self.message_list

###############################################################################
MAX_VAL = 0xffffffffffffffff
global n
n = 0       
def add_bit(b, s):
    global n
    t = (s[n % 32]^(0xffffffff if b else 0)) &MAX_VAL
    t = ((t|(t>>1)) ^ ((t<<1)&MAX_VAL))&MAX_VAL     # Have to enforce 64 bit condition on left shift     
    t = (t ^ (t>>4) ^ (t>>8) ^ (t>>16) ^ (t>>32)) & MAX_VAL
    n += 1                           
    s[n % 32] ^= (t&MAX_VAL)  #s[(n) % 32] ^= t, modified to reflect n change
    return s[n % 32]    #return s[(n) % 32], modified to reflect n change                      

def del_bit(b, s):
    global n
    n -= 1
    add_bit(b,s), 
    n -= 1
    return s[n % 32]
    
def init(s):
    global n
    n = 0
    h = 1
    for i in range(32):
        s[i]=0
    for i in range(4096):
        h=add_bit(h&1, s)
    n = 0    

###############################################################################