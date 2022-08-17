"""
D E C O D E R
"""
#import sys    #sys.setrecursionlimit((msg_len+1)*8)    after gr.sync_block.__init__()
import numpy as np
from gnuradio import gr
from gnuradio import grc
from math import ceil
import inspect
DEFAULT_CHECKSUM = 0
#TODO: REMOVE FIRST HANDLING TO MAKE VERSATILE
global first
first = True

class blk(gr.sync_block):

    def __init__(self): #If there is an error, change default here:
        msg_len = get_top_variable("MESSAGE_LENGTH", default=2**7)
        cod_len = get_top_variable("CODEWORD_LENGTH", default=2**17)
        
        gr.sync_block.__init__(self,
            name='BBC Decoder',
            in_sig=[(np.byte,  cod_len if isinstance(cod_len, int) else int(cod_len))],
            out_sig=[(np.byte, msg_len if isinstance(msg_len, int) else int(msg_len))]
        )
        # Convert from Bytes to bits
        self.myDecoder = Decoder(msg_len*8, cod_len*8, DEFAULT_CHECKSUM) # Bytes to bits
        #sys.setrecursionlimit((msg_len+1)*8)

    # Use BBC to decode the incoming codeword vectors
    def work(self, input_items, output_items):
        result = self.myDecoder.decode(input_items[0][:][:][0])
        #TODO: add function to iteratively push results out
        try:
            for x in result:
                output_items[0][:][:] = bytearray(x)
            return len(output_items[0])
        except:
            print("DEBUG decoder line 33: output typing failed.\n")
            print("Type of decoder result: ", type(bytearray(result)))
            print("Type of stream: ", type(self.out_sig))

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
        
        global first
        while first and True:
            # Check for mark corresponding to encoding D[n], beginning with a 0
            prop_bit = (memoryview(message)[int((self.n - self.n%8)/8)]>>(self.n%8)) & 0b1      # Find the proposed bit from previous execution, aka D[n]
            val = (add_bit(prop_bit, self.shift_register) % (self.COD_LEN))                  # Mark location from glowworm
            bit = (memoryview(packet)[int((val-val%8)/8)]>>(val%8)) & 0b1                       # Logical AND to determine if present in packet/codeword

            # If the mark is present... explore
            if bit==1:
                # message is complete, write to buffer
                if self.n == (self.MSG_LEN + self.CHK_LEN - 1):
                    #print(message)
                    self.message_list.append(bytes(memoryview(message)[0:self.MSG_LEN - 1 - self.num_checksum]))
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
                    print("Packet is fully decoded. Still need to mplement multiple messages in GRC (decoder)")
                    break #proceed with next packet

                else: # Move over to the 1 branch of current search
                    del_bit(0, self.shift_register)
                    memoryview(message)[int((self.n - self.n%8)/8)] |= (1<<self.n%8)
        first = False
        for x in self.message_list:
            print(x)
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
            print(result)
            #print(f"[Block Debug 2] While modifying the flowgraph, I found top variable \'{variable_name}\': type={type(result)}, value={result}")
            #return result
        
    finally:
        del top

    print("returining default vaule")
    return default