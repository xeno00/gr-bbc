"""
OOK Decoder
"""

import numpy as np
from gnuradio import gr

class blk(gr.interp_block):

    def __init__(self, sps=768,clen =2**17, dbug=0): 
        gr.sync_block.__init__(
            self,
            name='OOK Decoder',
            in_sig=[np.float32],
            out_sig=[np.byte]
        )
        # Set the default Interpolation Rate, i.e. sync case
        self.set_relative_rate(1)
        self.sps = sps
        self.dbug = dbug
        self.clen = clen # to bits from bytes
        self.zcount = 0  # Number of samples of zeros
        self.ocount = 0  # Number of samples of ones
        self.prev_samp =  0
        self.current_byte = '' # will be  string representing bits received
        self.output_bytes = bytearray() # will be the output bytes
        self.spstol = (np.ceil(0.75*self.sps))
        
    def work(self, input_items, output_items):
        
        # Initialize output queue
        output_queue = []
        
        # Use samples to get bitstream
        self.read_samples(input_items[0])
        
        # Peel off bytes from the beginning of the queue
        while len(self.current_byte) >= 8:
            byte = bytes(chr(int(self.current_byte[0:8],2)),'utf-8')
            #print("Stripped off ", byte)
            output_queue.append(byte)
            self.current_byte = self.current_byte[8:]


        # Use interp block to output the items
        interp = len(output_queue)
        if interp > 0:
            
            # Definre the number of outputs
            self.set_relative_rate(interp)
            
            # Assign outputs iteratively
            for j in range(interp):
                try:
                    print("Sent ", output_queue[j])
                    output_items[0][j] = output_queue[j]
                except:
                    print("OOK line 58: Failed to asign output... ", output_queue[j], ". j=", j)
                
            # Again, return the number of outputs
            return len(output_items[0])
        # Otherwise, return nothing
        return 0
            
    
    
    def read_samples(self, packet):
        i = 0
        for samp in packet:
            i+=1
            # Detect a Change
            if samp != self.prev_samp:
                if (self.ocount >= self.spstol) or (self.zcount >= self.spstol):
                    if self.prev_samp == 1: # look for ones bits
                        [obits,omod] = np.divmod(self.ocount,self.sps) # the floor
                        if omod >= self.spstol: # if the modulus is more than required for a bit, add another bit
                            obits +=1
                        otemp = '1'*int(obits) #JAMES
                        self.current_byte = self.current_byte + otemp #JAMES
                    elif self.prev_samp == 0:
                        [zbits,zmod] = np.divmod(self.zcount,self.sps)
                        if zmod >= self.spstol:
                            zbits +=1
                        ztemp = '0'*int(zbits) #JAMES
                        self.current_byte = self.current_byte + ztemp #JAMES
                    self.ocount = 0 # reset the counters
                    self.zcount = 0
            
            # Increment respective sample counter
            if samp == 1:
                self.ocount +=1
            elif samp == 0:
                self.zcount +=1
            else:
                print("incorrect value for sample on index " + str(i))

            self.prev_samp = samp # store the previous sample
