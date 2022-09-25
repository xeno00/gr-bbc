"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, sps=768,clen =2**17, dbug=0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='OOK Decoder',   # will show up in GRC
            in_sig=[np.float32],
            out_sig=[np.float32, (np.byte,int(8))]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.sps = sps
        self.dbug = dbug
        self.clen = clen  # to bits from bytes
        self.zcount = 0
        self.ocount = 0
        self.prev_samp =  0
        self.current_byte = '' # will be  string representing bits received
        self.output_bytes = bytearray() # will be the output bytes
        self.spstol = (np.ceil(0.75*self.sps))
        self.msgportname = "Message"
        self.message_port_register_out(pmt.intern(self.msgportname))

    def work(self, input_items, output_items):
        data = input_items[0]
        i = 0 # loop counter

         #main loop
        for samp in data:
            i+=1
            if samp != self.prev_samp: # if the sample value has changed
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

            if samp == 1:
                self.ocount +=1
            elif samp == 0:
                self.zcount +=1
            else:
                print("incorrect value for sample on index " + str(i))

            self.prev_samp = samp # store the previous sample

            while len(self.current_byte) >= 8:
                # import pdb
                # pdb.set_trace()
                if self.dbug == 1:
                    print('got a byte')
                    print(self.current_byte[0:8]) # only get the first 8 bits
                self.output_bytes = self.output_bytes + bytearray(chr(int(self.current_byte[0:8],2)),'utf-8')
                #print("len of output_bytes is " + str(len(self.output_bytes)))
                self.message_port_pub(pmt.intern(self.msgportname), pmt.intern(self.current_byte[0:8]))
                #self.output_bytes = self.output_bytes + self.current_byte[0:8]
                self.current_byte = self.current_byte[8:]

        # check to see if the
        #a = self.output_bytes.find(self.sep)
        #if a != -1:
        # import pdb
        # pdb.set_trace()
        if len(self.output_bytes) == self.clen:
            print("Found a codeword")
            print("current_byte is " + str(self.current_byte))

        #     #print("Message found is " + self.output_bytes[len(self.sep)-1:a])
            self.message_port_pub(pmt.intern(self.msgportname), pmt.intern(str(self.output_bytes)))
        #     if a == len(self.output_bytes)-1:
        #         self.output_bytes = ""
        #     else:
        #         self.output_bytes = self.output_bytes[a+len(self.sep):]
            output_items[1][:] =  self.output_bytes
        else:
            print("No codeword yet")
            #output_items[1][:] = bytearray()
        if self.dbug == 1:
            #print("Bytes found are: " + self.output_bytes)
            print("Current byte is: " + self.current_byte)
#           print("Leftover Ocount is: " + str(self.ocount))
#           print("Leftover Zcount is: " + str(self.zcount))


        # just output what we got in
        output_items[0][:] = input_items[0]
        return len(output_items[0])
