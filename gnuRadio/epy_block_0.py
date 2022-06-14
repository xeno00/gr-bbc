"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
DEFAULT_CHECKSUM = 0
global first
first = True

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, msg_len=2**10, cod_len=2**20):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='BBC Decoder',   # will show up in GRC
            in_sig=[(np.byte, cod_len)],
            out_sig=[(np.byte, msg_len)]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.myDecoder = Decoder(msg_len, cod_len)

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        output_items[0][:][:] = self.myDecoder.decode(input_items[0][:][:])
        return len(output_items[0])

#################################################################################################
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
            print(codeword)
            first = False
            self.message_list = []
            message = bytearray(self.msg_len)
            self._decode_BBC_recursive(message, codeword, 0) # make the first recursive call to decode
            #return self.message_list
            print(self.message_list)
    
    def _decode_BBC_recursive(self, message, codeword, index):
        if index == (self.msg_len-1):
                self.message_list.append(bytes(memoryview(message)[0:self.msg_len-1-self.num_checksum]).decode(encoding='ascii'))
        else:
            # assuming the next message bit is a 0, check for a mark in the codeword
            val = (add_bit(0, self.shift_register) % (self.cod_len))
            bit = ((memoryview(codeword)[int((val-val%8)/8)])>>(val%8))& 0b1
            if bit == 1: #TODO
                self._decode_BBC_recursive(message, codeword, index+1)
            del_bit(0, self.shift_register)

            # assuming the next message bit is a 1, check for a mark in the codeword
            val = (add_bit(1, self.shift_register) % (self.cod_len))
            bit =  (memoryview(codeword)[int((val-val%8)/8)]>>(val%8))& 0b1
            if bit == 1: #(1<<val) == (codeword & (1<<val)):
                memoryview(message)[int((index-index%8)/8)] += (1<<index%8)
                self._decode_BBC_recursive(message, codeword, index+1)
            del_bit(1, self.shift_register)

#################################################################################################
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
