# Author: James C Morrison
# Date: 3/26//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Implement the BBC codec with object oriented programming and bytearrays
# CURRENT MODEL
#from math import ceil
import glowworm as gw
#MSG_LEN = 2**3  # bits  # now a class property
#COD_LEN = 2**6  # bits  # now a class property
DEFAULT_CHECKSUM = 0

#global COD_LEN

class Codec:
    # The codec is comprised of an encoder and decoder, with an associated message/codeword pair
    def __init__(self, MSG_LEN, COD_LEN):
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN
        self.encoder = Encoder(self.MSG_LEN, self.COD_LEN)
        self.decoder = Decoder(self.MSG_LEN, self.COD_LEN)

    # Resulting functionality should be "mycodec.encode("My password is xwing")"
    def bbc_encode(self, message):
        self.encoder = Encoder(self.MSG_LEN, self.COD_LEN)
        return self.encoder.encode(message)

    # Resulting functionality should be "mycodec.decode(bytearray1)"
    def bbc_decode(self, codeword):
        self.decoder = Decoder(self.MSG_LEN, self.COD_LEN)
        return self.decoder.decode(codeword)


class Encoder:
    def __init__(self, MSG_LEN, COD_LEN):
        self.shift_register = self.init_shift_register()
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)

    def parse_input(self, input):
        input = input.encode(encoding="ASCII")
        message = bytearray(int(self.MSG_LEN/8))
        memoryview(message)[0:(len(input))] = input
        return message

    def encode(self, input):
        message = self.parse_input(input)
        codeword = bytearray(int(self.COD_LEN/8))
        for i in range(self.MSG_LEN):
            element = memoryview(message)[int((i-i%8)/8)]
            bit = ((element) >> (i%8)) & 0b1
            mark_loc = gw.add_bit(bit, self.shift_register) % self.COD_LEN
            memoryview(codeword)[int((mark_loc-mark_loc%8)/8)] |= 1<<(mark_loc%8)
        return(codeword)


class Decoder:
    def __init__(self, MSG_LEN, COD_LEN):
        self.message_list = []
        self.num_checksum = DEFAULT_CHECKSUM
        self.shift_register = self.init_shift_register()
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)
    
    def decode(self, codeword):
        self.message_list = []
        message = bytearray(int(self.MSG_LEN/8)) # bits to bytes
        self._decode_BBC_recursive(message, codeword, 0) # make the first recursive call to decode
        return self.message_list
    
    def _decode_BBC_recursive(self, message, codeword, index):

        if index == (self.MSG_LEN-1):
                #self.message_list.append(bytes(memoryview(message)[0:self.MSG_LEN-1-self.num_checksum]).decode(encoding='ascii'))
                self.message_list.append(bytes(memoryview(message)[0:self.MSG_LEN - 1 - self.num_checksum])) # the output will now be a bytearray, can attempt to decode later
        else:
            # assuming the next message bit is a 0, check for a mark in the codeword
            val = (gw.add_bit(0, self.shift_register) % (self.COD_LEN))
            bit = ((memoryview(codeword)[int((val-val%8)/8)])>>(val%8))& 0b1
            if bit == 1:
                self._decode_BBC_recursive(message, codeword, index+1)
            gw.del_bit(0, self.shift_register)

            # assuming the next message bit is a 1, check for a mark in the codeword
            val = (gw.add_bit(1, self.shift_register) % (self.COD_LEN))
            bit =  (memoryview(codeword)[int((val-val%8)/8)]>>(val%8))& 0b1
            if bit == 1: #(1<<val) == (codeword & (1<<val)):
                memoryview(message)[int((index-index%8)/8)] |= (1<<index%8)
                self._decode_BBC_recursive(message, codeword, index+1)
            gw.del_bit(1, self.shift_register)
            memoryview(message)[int((index-index%8)/8)] = 0