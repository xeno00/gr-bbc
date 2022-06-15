"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
DEFAULT_CHECKSUM = 0

class blk(gr.sync_block):

    def __init__(self, msg_len=2**6, cod_len=2**12):
        #GR Interpretable variables, names and ports
        gr.sync_block.__init__(self,
            name='BBC Encoder',
            in_sig=[(np.byte, msg_len)],
            out_sig=[(np.byte, cod_len)]
        )
        #self.cod_len = cod_len
        self.myEncoder = Encoder(msg_len, cod_len)
    
    # Use BBC to encode the incoming vectors
    def work(self, input_items, output_items):
        output_items[0][:][:] = self.myEncoder.encode(input_items[0][:][:])
        return len(output_items[0])
    
###############################################################################
class Encoder:
    def __init__(self, msg_len, cod_len):
        self.shift_register = self.init_shift_register()
        self.msg_len = msg_len
        self.cod_len = cod_len

    def init_shift_register(self):
        shift_register = [0 for i in range(32)]
        init(shift_register)
        return (shift_register)

    def parse_input(self, my_input):
        #print("parsing", my_input)
        #if(type(my_input)==type("string")):
        #    my_input = my_input.encode(encoding="ASCII")
        message = bytearray(my_input.tobytes())#bytearray(MSG_LEN)
        #print("message = ", message)
        #memoryview(message)[0:(len(input))] = input
        return message

    def encode(self, input):
        #print("parsing ", input)
        message = self.parse_input(input)
        #print("message ", message)
        codeword = bytearray(self.cod_len)
        for i in range(self.msg_len):
            element = memoryview(message)[int((i-i%8)/8)]
            bit = ((element) >> (i%8)) & 0b1
            mark_loc = add_bit(bit, self.shift_register) % self.cod_len
            memoryview(codeword)[int((mark_loc-mark_loc%8)/8)] |= (1<<(mark_loc%8))
            # Was error for adding 10000000, so changed to | instead of +
        #print(codeword==0)
        return(codeword)
        
 ##############################################################################
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
