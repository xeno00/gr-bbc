"""
E N C O D E R
"""

import numpy as np
from gnuradio import gr
DEFAULT_CHECKSUM = 0

class blk(gr.sync_block):
    
    def __init__(self, msg_len=2**3, cod_len=2**12):
        gr.sync_block.__init__(self,
            name='BBC Encoder',
            in_sig=[(np.byte, msg_len)],
            out_sig=[(np.byte, cod_len)]
        )
        # Convert from bits to Bytes
        self.myEncoder = Encoder(msg_len*8, cod_len*8)
    
    # Use BBC to encode the incoming message vectors
    def work(self, input_items, output_items):
        result = self.myEncoder.encode(input_items[0][:][:])
        try:
            output_items[0][:][:] = result
            return len(output_items[0])
        except:
            print("DEBUG encoder line 31: output typing failed.\n")
            print("Type of encoder result: ", type(result))
            print("Type of stream: ", type(self.out_sig))
    
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
        message = bytearray(my_input.tobytes())
        #TODO: add error exception for wrong sized input vector
        return message

    def encode(self, input):
        message = self.parse_input(input)
        codeword = bytearray(int(self.cod_len/8))
        
        for i in range(self.msg_len):
            element = memoryview(message)[int((i-i%8)/8)]
            bit = ((element) >> (i%8)) & 0b1
            mark_loc = add_bit(bit, self.shift_register) % self.cod_len
            memoryview(codeword)[int((mark_loc-mark_loc%8)/8)] |= (1<<(mark_loc%8))
            # TODO: add + vs | change to python library
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
    return s[n % 32]        #return s[(n) % 32], modified to reflect n change                      

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
