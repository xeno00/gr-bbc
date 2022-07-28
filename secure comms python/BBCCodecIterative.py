# Author: James C Morrison
# Date: 7/27//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Implement the BBC codec with object oriented programming and bytearrays
# Use an iterative decoder

# CURRENT MODEL
#from math import ceil
import glowworm as gw
from math import ceil
#MSG_LEN = 2**3  # bits  # now a class property
#COD_LEN = 2**6  # bits  # now a class property
DEFAULT_CHECKSUM = 0

#global COD_LEN

class Codec:
    # The codec is comprised of an encoder and decoder, with an associated message/codeword pair
    def __init__(self, MSG_LEN, COD_LEN, CHK_LEN):
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN
        self.CHK_LEN = CHK_LEN
        self.encoder = Encoder(self.MSG_LEN, self.COD_LEN, self.CHK_LEN)
        self.decoder = Decoder(self.MSG_LEN, self.COD_LEN, self.CHK_LEN)

    # Resulting functionality should be "mycodec.encode("My password is xwing")"
    def bbc_encode(self, message):
        self.encoder = Encoder(self.MSG_LEN, self.COD_LEN, self.CHK_LEN)
        return self.encoder.encode(message)

    # Resulting functionality should be "mycodec.decode(bytearray1)"
    def bbc_decode(self, codeword):
        self.decoder = Decoder(self.MSG_LEN, self.COD_LEN, self.CHK_LEN)
        return self.decoder.decode(codeword)


class Encoder:
    def __init__(self, MSG_LEN, COD_LEN, CHK_LEN):
        self.shift_register = self.init_shift_register()
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN
        self.CHK_LEN = CHK_LEN

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
            element = memoryview(message)[int((i-i%8)/8)]                   # ASCII byte to be encoded
            bit = ((element) >> (i%8)) & 0b1                                # Extract bit from Byte
            mark_loc = gw.add_bit(bit, self.shift_register) % self.COD_LEN  # Mark location from glowworm
            memoryview(codeword)[int((mark_loc-mark_loc%8)/8)] |= 1<<(mark_loc%8)
        # TODO: ADD CHECKSUM ENCODING
        return(codeword)


class Decoder:
    def __init__(self, MSG_LEN, COD_LEN, CHK_LEN):
        self.message_list = []
        self.num_checksum = DEFAULT_CHECKSUM
        self.shift_register = self.init_shift_register()
        self.MSG_LEN = MSG_LEN
        self.COD_LEN = COD_LEN
        self.CHK_LEN = CHK_LEN #Is added to MSG_LEN, not subtracted from
        self.n = 0

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        gw.init(shift_register)
        return (shift_register)

    #DECODE ITERATIVELY
    #Note that   D[n]   is the same as    memoryview(message)[int((self.n - self.n%8)/8)]
    def decode(self, packet):
        # Initialize variables
        self.message_list = []
        message = bytearray(ceil((self.MSG_LEN + self.CHK_LEN)/8))
        #memoryview(message)[int((self.n - self.n%8)/8)] = 1         # TODO: debug initialization for D[n]

        while True:
            # Check for mark corresponding to encoding D[n], beginning with a 0
            prop_bit = (memoryview(message)[int((self.n - self.n%8)/8)]>>(self.n%8)) & 0b1      # Find the proposed bit from previous execution, aka D[n]
            val = (gw.add_bit(prop_bit, self.shift_register) % (self.COD_LEN))                  # Mark location from glowworm
            bit = (memoryview(packet)[int((val-val%8)/8)]>>(val%8)) & 0b1                       # Logical AND to determine if present in packet/codeword

            # If the mark is present... explore
            if bit==1:
                # message is complete, write to buffer
                if self.n == (self.MSG_LEN + self.CHK_LEN - 1):
                    print(message)
                    self.message_list.append(bytes(memoryview(message)[0:self.MSG_LEN - 1 - self.num_checksum]))
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
            else:
                # delete checksum bits
                while self.n >= self.MSG_LEN: 
                    gw.del_bit(0, self.shift_register)
                    self.n -= 1
                    
                # delete 1's until a 0 is encountered
                while self.n >=0 and (((memoryview(message)[int((self.n - self.n%8)/8)]>>(self.n%8)) & 0b1 )==1):
                    gw.del_bit(1, self.shift_register)
                    memoryview(message)[int((self.n - self.n%8)/8)] &= (0xff ^ (1<<self.n%8))
                    self.n -= 1
                        
                if self.n < 0: #Packet is fully decoded
                    print("Packet is fully decoded")
                    break #proceed with next packet

                else: # Move over to the 1 branch of current search
                    gw.del_bit(0, self.shift_register)
                    memoryview(message)[int((self.n - self.n%8)/8)] |= (1<<self.n%8)

        return self.message_list