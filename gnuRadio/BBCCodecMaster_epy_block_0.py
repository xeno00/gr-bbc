"""
D E C O D E R
"""

import numpy as np
from gnuradio import gr
DEFAULT_CHECKSUM = 0
global first
#TODO: REMOVE FIRST HANDLING TO MAKE VERSATILE
first = True

class blk(gr.sync_block):

    def __init__(self, msg_len=2**3, cod_len=2**12):
        gr.sync_block.__init__(
            self,
            name='BBC Decoder',   # will show up in GRC
            in_sig=[(np.byte, cod_len)],
            out_sig=[(np.byte, msg_len)]
        )
        # Convert from bits to Bytes
        self.myDecoder = Decoder(msg_len*8, cod_len*8)

    # Use BBC to decode the incoming codeword vectors
    def work(self, input_items, output_items):
        result = self.myDecoder.decode(input_items[0][:][:])
        #TODO: add function to iteratively push results out
        try:
            output_items[0][:][:] = bytearray(result[0].encode())
            return len(output_items[0])
        except:
            print("DEBUG decoder line 33: output typing failed.\n")
            print("Type of decoder result: ", type(bytearray(result[0].encode())))
            print("Type of stream: ", type(self.out_sig))

###############################################################################
class Decoder:
    def __init__(self, msg_len, cod_len):
        self.message_list = []
        self.num_checksum = DEFAULT_CHECKSUM
        self.shift_register = self.init_shift_register()
        self.msg_len = msg_len
        self.cod_len = cod_len

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        init(shift_register)
        return (shift_register)
    
    def decode(self, codeword):
        codeword = bytearray(codeword.tobytes()) #added for GRC implementation
        global first
        if(first):
            first = False
            self.message_list = []
            message = bytearray(int(self.msg_len/8))
            self._decode_BBC_recursive(message, codeword, 0) # make the first recursive call to decode
            print("Message list- decoder--\n", self.message_list)
            return self.message_list
    
    def _decode_BBC_recursive(self, message, codeword, index):
        # BASE CASE
        if index == (self.msg_len-1):
            self.message_list.append(bytes(memoryview(message)[0:self.msg_len-1-self.num_checksum]).decode(encoding='ascii'))
            
        # assuming the next message bit is a 0, check for a mark in the codeword
        else:
            val = (add_bit(0, self.shift_register) % (self.cod_len))
            bit = ((memoryview(codeword)[int((val-val%8)/8)])>>(val%8))& 0b1
            if bit == 1: #TODO
                try:
                    self._decode_BBC_recursive(message, codeword, index+1)
                except:
                    print("Line 68. Recursion max length reached. current message: ", message, "Length at error = ", index) #DEBUG
            del_bit(0, self.shift_register)

            # assuming the next message bit is a 1, check for a mark in the codeword
            val = (add_bit(1, self.shift_register) % (self.cod_len))
            bit =  (memoryview(codeword)[int((val-val%8)/8)]>>(val%8))& 0b1
            if bit == 1: #(1<<val) == (codeword & (1<<val)):
                memoryview(message)[int((index-index%8)/8)] |= (1<<index%8)
                try:
                    self._decode_BBC_recursive(message, codeword, index+1)
                except:
                    print("Line 79. Recursion max length reached. current message: ", message, "Length at error = ", index) #DEBUG
            del_bit(1, self.shift_register)

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
