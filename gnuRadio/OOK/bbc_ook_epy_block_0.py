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

    def __init__(self, sps=768, clen=2 ** 17, dbug=0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='OOK Decoder',  # will show up in GRC
            in_sig=[np.float32],
            out_sig=[np.float32]#, (np.byte, int(8))] # save bytes output for later
            #out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.sps = sps
        self.dbug = dbug
        self.clen = clen * 8  # to bits from bytes, if using the string method
        self.zcount = 0
        self.ocount = 0
        self.prev_samp = 0
        self.current_byte = ''  # will be  string representing bits received
        self.output_bytes = bytearray()  # will be the output bytes
        self.output_bytes_string = ''
        self.spstol = (np.ceil(0.75 * self.sps))
        self.msgportname = "Message"
        self.message_port_register_out(pmt.intern(self.msgportname))
        self.cwb = 0

    def work(self, input_items, output_items):
        data = input_items[0]
        if self.dbug == 1:
            print("Received Data of size " + str(len(data)))
        i = 0  # loop counter
        # main loop
        for samp in data:
            i += 1
            if samp != self.prev_samp:  # if the sample value has changed
                if (self.ocount >= self.spstol) or (self.zcount >= self.spstol):
                    self.declarebit(int(self.prev_samp))  # will update self.current_byte
                    self.ocount = 0  # reset the counters
                    self.zcount = 0

            if samp == 1:
                self.ocount += 1
            elif samp == 0:
                self.zcount += 1
            else:
                print("incorrect value for sample on index " + str(i))

            self.prev_samp = samp  # store the previous sample

            while len(self.current_byte) >= 8:
                self.cwb += 1
                ## for some reason, this one doesn't work...
                # self.output_bytes = self.output_bytes + bytearray(chr(int(self.current_byte[0:8],2)),'utf-8') # output_bytes are bytes
                self.output_bytes_string = self.output_bytes_string + self.current_byte[0:8]  # output_bytes is a string
                self.current_byte = self.current_byte[8:]
                # self.message_port_pub(pmt.intern(self.msgportname), pmt.intern(self.current_byte[0:8])) # debugging
                if self.dbug == 1:
                    print("Found " + str(self.cwb) + " bytes so far.")
                    # print(self.current_byte[0:8]) # only get the first 8 bits
                    print("len of output_bytes is " + str(len(self.output_bytes_string)))

        ## if we're at the end and have bits in current_byte, then, add them to output_byte_string
        if (self.ocount >= self.spstol) and (len(self.current_byte) == 7) and (len(self.output_bytes_string) <= self.clen):
            # this might just be a dirty hack for now, need to figure out a better way to check if there's a partial
            ## byte and ocount is high enough
            self.declarebit(int(1)) # will update self.current_byte
            self.output_bytes_string = self.output_bytes_string + self.current_byte[0:8]  # output_bytes is a string
            self.current_byte = ''
            self.ocount = 0

        # now we can see if we have a codeword to output
        if len(self.output_bytes_string) >= self.clen:
            if self.dbug == 1:
                print("Found a codeword")
                print("current_byte is " + str(self.current_byte))
                print("Bytes found are: " + str(self.output_bytes_string))
            # import pdb
            # pdb.set_trace()
            # output the codeword
            # need to break up the codeword into byte-sized chunks and transmit them
            #for k in range(1,int((self.clen/8) + 1)):
            for k in range(0, int((self.clen / 8) )):
                bytes_to_send = self.output_bytes_string[self.clen-(k*8):self.clen-((k-1)*8)]
                bytes_to_send = self.output_bytes_string[k*8:(k+1)*8]
                self.message_port_pub(pmt.intern(self.msgportname), pmt.intern(bytes_to_send))

            ## what a one-liner, converts to bytearray: https://stackoverflow.com/questions/32675679/convert-binary-string-to-bytearray-in-python-3
            ## save the bytes output for later
            #self.output_bytes = bytearray(int(self.output_bytes_string[:int(self.clen/8)], 2).to_bytes(int((self.clen/8) + 7) // 8, 'big'))
            #output_items[1][:] =  bytearray(self.output_bytes[:int(self.clen/8)]) # only output 1 codeword at a time
            #self.message_port_pub(pmt.intern(self.msgportname), pmt.intern(str(self.output_bytes[:int(self.clen / 8)]))) #send bytearray as pmt
            #self.message_port_pub(pmt.intern(self.msgportname), pmt.intern(self.output_bytes_string[:int(self.clen)])) # send the bytes as a s
            self.output_bytes_string = self.output_bytes_string[self.clen:]  # pare the string
        else:
            if self.dbug == 1:
                print("No codeword yet")
        if self.dbug == 1:
            print("Current byte is: " + self.current_byte)
            print("Leftover Ocount is: " + str(self.ocount))
            print("Leftover Zcount is: " + str(self.zcount))

        ## just output what we got in
        output_items[0][:] = input_items[0]
        return len(output_items[0])

    def declarebit(self, bitval: int):
        if bitval == 1:
            cnt = self.ocount
        else:
            cnt = self.zcount
        [bits, bmod] = np.divmod(cnt, self.sps)  # the floor
        if bmod >= self.spstol:  # if the modulus is more than required for a bit, add another bit
            bits += 1  # see if we have enough samples left over to declare a bit
        self.current_byte = self.current_byte + (str(bitval) * int(bits))  # JAMES
