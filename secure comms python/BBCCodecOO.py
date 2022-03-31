# Author: James C Morrison
# Date: 3/26//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Implement the BBC codec with object oriented programming and bytearrays
# CURRENT MODEL
from math import ceil
import glowworm as gw
MSG_LEN = 1024
DEFAULT_CHECKSUM = 0

class Codec:
    # The codec is comprised of an encoder and decoder, with an associated message/codeword pair
    def __init__(self):
        self.secret  = InfoPair()
        self.encoder = Encoder(self.secret)
        self.decoder = Decoder(self.secret)

    # Resulting functionality should be "mycodec.encode("My password is xwing")"
    def encode_message(self, message):
        self.secret.set_message(message)
        self.encoder = Encoder(self.secret)
        return self.encoder.encode()

    # Resulting functionality should be "mycodec.decode(bytearray1)"
    def decode_message(self, codeword):
        self.secret.set_codeword(codeword)
        self.decoder = Decoder(self.secret)
        return self.decoder.decode()


class InfoPair:
    def __init__(self):
        self.message = bytearray(ceil(MSG_LEN/8))
        self.codeword = bytearray(ceil(2**MSG_LEN/8))
        self.num_checksum = DEFAULT_CHECKSUM

    def set_message(self, message):
        self.message = bytearray(message)

    def set_codeword(self, codeword):
        self.codeword = bytearray(codeword)

    def read_file(self, type:int=1, location:str="data.txt"):
        try:
            with open(location, "rb") as source:
                if(type):
                    source.readinto(self.message)
                else:
                    source.readinto(self.codeword)
        except:
            print("The file could not be read.") 


class Encoder:
    def __init__(self, secret:InfoPair):
        self.message =  secret.message
        self.codeword = 0
        self.shift_register = self.init_shift_register()

    def init_shift_register():
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)

    def encode(self):
        for i in range(MSG_LEN):
            bit = ((memoryview(self.message)[int((i-i%8)/8)]) >> (i%8)) & 0b1
            mark_loc = gw.add_bit(bit, self.shift_register) % 1024
            memoryview(self.codeword)[int((mark_loc-mark_loc%8)/8)] += 1<<(mark_loc%8)
        return(self.codeword)


class Decoder:
    def __init__(self, secret:InfoPair):
        self.messages = []
        self.message = 0
        self.codeword = secret.codeword
        self.num_checksum = secret.num_checksum
        self.shift_register = self.init_shift_register()

    def init_shift_register():
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)
    
    def decode(self):
        self._decode_BBC_recursive(0) # make the first recursive call to decode
        return self.messages
    
    def _decode_BBC_recursive(self, index):
        if index == (MSG_LEN):
                self.message_list.append(bytes(memoryview(self.message)[0:MSG_LEN-1-self.num_checksum]).decode(encoding='ascii'))
                self.message = 0

        else:
            # assuming the next message bit is a 0, check for a mark in the codeword
            val = (gw.add_bit(0, self.shift_register) % (MSG_LEN))
            if (self.codeword & (1<<val)) != 0:
                self._decode_BBC_recursive(index+1)
            gw.del_bit(0, self.shift_register)

            # assuming the next message bit is a 1, check for a mark in the codeword
            val = (gw.add_bit(1, self.shift_register) % (MSG_LEN))
            if (self.codeword & (1<<val)) != 0: #(1<<val) == (codeword & (1<<val)):
                self.message += 2**index
                self._decode_BBC_recursive(index+1)
            gw.del_bit(1, self.shift_register)
        

        
