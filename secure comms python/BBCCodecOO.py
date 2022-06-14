# Author: James C Morrison
# Date: 3/26//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Implement the BBC codec with object oriented programming and bytearrays
# CURRENT MODEL
#from math import ceil
import glowworm as gw
MSG_LEN = 2**10
COD_LEN = 2**20
DEFAULT_CHECKSUM = 0

class Codec:
    # The codec is comprised of an encoder and decoder, with an associated message/codeword pair
    def __init__(self):
        self.encoder = Encoder()
        self.decoder = Decoder()

    # Resulting functionality should be "mycodec.encode("My password is xwing")"
    def bbc_encode(self, message):
        self.encoder = Encoder()
        return self.encoder.encode(message)

    # Resulting functionality should be "mycodec.decode(bytearray1)"
    def bbc_decode(self, codeword):
        self.decoder = Decoder()
        return self.decoder.decode(codeword)


class Encoder:
    def __init__(self):
        self.shift_register = self.init_shift_register()

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)

    def parse_input(self, input):
        input = input.encode(encoding="ASCII")
        message = bytearray(MSG_LEN)
        memoryview(message)[0:(len(input))] = input
        return message

    def encode(self, input):
        message = self.parse_input(input)
        codeword = bytearray(COD_LEN)
        for i in range(MSG_LEN):
            element = memoryview(message)[int((i-i%8)/8)]
            bit = ((element) >> (i%8)) & 0b1
            mark_loc = gw.add_bit(bit, self.shift_register) % COD_LEN
            memoryview(codeword)[int((mark_loc-mark_loc%8)/8)] += 1<<(mark_loc%8)
        return(codeword)


class Decoder:
    def __init__(self):
        self.message_list = []
        self.num_checksum = DEFAULT_CHECKSUM
        self.shift_register = self.init_shift_register()

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)
    
    def decode(self, codeword):
        self.message_list = []
        message = bytearray(MSG_LEN)
        self._decode_BBC_recursive(message, codeword, 0) # make the first recursive call to decode
        return self.message_list
    
    def _decode_BBC_recursive(self, message, codeword, index):
        if index == (MSG_LEN-1):
                self.message_list.append(bytes(memoryview(message)[0:MSG_LEN-1-self.num_checksum]).decode(encoding='ascii'))
        else:
            # assuming the next message bit is a 0, check for a mark in the codeword
            val = (gw.add_bit(0, self.shift_register) % (COD_LEN))
            bit = ((memoryview(codeword)[int((val-val%8)/8)])>>(val%8))& 0b1
            if bit == 1: #TODO
                self._decode_BBC_recursive(message, codeword, index+1)
            gw.del_bit(0, self.shift_register)

            # assuming the next message bit is a 1, check for a mark in the codeword
            val = (gw.add_bit(1, self.shift_register) % (COD_LEN))
            bit =  (memoryview(codeword)[int((val-val%8)/8)]>>(val%8))& 0b1
            if bit == 1: #(1<<val) == (codeword & (1<<val)):
                memoryview(message)[int((index-index%8)/8)] += (1<<index%8)
                self._decode_BBC_recursive(message, codeword, index+1)
            gw.del_bit(1, self.shift_register)
        

        
#class InfoPair:
#    def __init__(self):
#        self.message = bytearray(ceil(MSG_LEN/8))
#        self.codeword = bytearray(ceil(COD_LEN/8))
#        self.num_checksum = DEFAULT_CHECKSUM

#    def set_message(self, message):
#        self.message = bytearray(message)

#    def set_codeword(self, codeword):
#        self.codeword = bytearray(codeword)

#    def read_file(self, type:int=1, location:str="data.txt"):
#        try:
#            with open(location, "rb") as source:
#                if(type):
#                    source.readinto(self.message)
#                else:
#                    source.readinto(self.codeword)
#        except:
#            print("The file could not be read.") 