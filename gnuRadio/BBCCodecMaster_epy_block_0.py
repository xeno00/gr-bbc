"""
D E C O D E R
"""
import sys    #sys.setrecursionlimit((msg_len+1)*8)    after gr.sync_block.__init__()
import numpy as np
from gnuradio import gr
from gnuradio import grc
import inspect
DEFAULT_CHECKSUM = 0
#TODO: REMOVE FIRST HANDLING TO MAKE VERSATILE
global first
first = True

class blk(gr.sync_block):

    def __init__(self): #If there is an error, change default here:
        msg_len = get_top_variable("MESSAGE_LENGTH", default=2**7)
        cod_len = get_top_variable("CODEWORD_LENGTH", default=512)
        
        gr.sync_block.__init__(self,
            name='BBC Decoder',
            in_sig=[(np.byte,  cod_len if isinstance(cod_len, int) else int(cod_len))],
            out_sig=[(np.byte, msg_len if isinstance(msg_len, int) else int(msg_len))]
        )
        # Convert from Bytes to bits
        self.myDecoder = Decoder(msg_len*8, cod_len*8)
        sys.setrecursionlimit((msg_len+1)*8)

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
            print("Message list- decoder--\n", str(self.message_list))
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
                    print("Line 68. Recursion max length reached. current message: ", str(message), "Length at error = ", str(index)) #DEBUG
            del_bit(0, self.shift_register)

            # assuming the next message bit is a 1, check for a mark in the codeword
            val = (add_bit(1, self.shift_register) % (self.cod_len))
            bit =  (memoryview(codeword)[int((val-val%8)/8)]>>(val%8))& 0b1
            if bit == 1: #(1<<val) == (codeword & (1<<val)):
                memoryview(message)[int((index-index%8)/8)] |= (1<<index%8)
                try:
                    self._decode_BBC_recursive(message, codeword, index+1)
                    memoryview(message)[int((index-index%8)/8)] &= (0xff ^ (1<<index%8)) #set one bit low
                except:
                    print("Line 79. Recursion max length reached. current message: ", str(message), "Length at error = ", str(index)) #DEBUG
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

###############################################################################
    
def get_top_variable(variable_name="", default=None):
    '''
    Returns the value of a variable from the flow graph.
    '''
    ## Run Condition: GNURadio is starting the flowgraph, resulting output comes from here when working
    top = inspect.currentframe().f_back.f_back.f_locals
    try:
        # Check if top has the variable name we're looking for
        if top.__contains__(variable_name):
            #print(f"[Block Debug 1] While starting, I found top variable \'{variable_name}\': type={type(top[variable_name])}, value={top[variable_name]}")
            return top[variable_name]
    finally:
        del top
        
    ## Run Condition: Saving the flowgraph, necessary when default case isnt correct. Removed return to fix error
    top = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_locals
    try:
        # Make sure top has 'self'
        if top.__contains__("self") and \
                (isinstance(top['self'], grc.gui.canvas.flowgraph.FlowGraph)) and \
                (hasattr(top['self'], 'blocks')):

            # Get a list of all blocks
            block_names = [block.name for block in top['self'].blocks]

            # Find the index to the variable we need
            block_index = block_names.index(variable_name)
            
            # Return result
            result = top["self"].blocks[block_index].params['value'].value
            #print(f"[Block Debug 2] While modifying the flowgraph, I found top variable \'{variable_name}\': type={type(result)}, value={result}")
            #return result
        
    finally:
        del top

    print("returining default vaule")
    return default