"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.basic_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, threshold = 0.03, triggered = False):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.basic_block.__init__(
            self,
            name='Wait for Trigger',   # will show up in GRC
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.threshold = threshold
        #self.itemsconsumed = 0
        self.triggered = triggered

    def forecast(self, noutput_items, ninput_items_required):
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items
        #if self.debug:
        #    print("Forecasting " + str(self.itemsconsumed) + " items")
        #ninput_items_required[0] = self.itemsconsumed

    def general_work(self, input_items, output_items):
        """example: multiply with constant"""
        in0 = input_items[0][:len(output_items[0])]
        out = output_items[0]
        if self.triggered: # pass through
            out[:] = in0
            #print("Triggered steady")
            self.consume(0,len(in0))
            return len(out)
        else:
            fval = np.argmax(in0 > self.threshold)
            if fval != 0:
                self.triggered = True
                #print("Triggered")
                out = in0[fval:-1]
                self.consume(0,len(in0))
                return len(out)
            else:
                if in0[0] > self.threshold:
                    out[:] = in0
                    #print("Triggered")
                    self.consume(0,len(in0))
                    return len(out)
                out = np.array([])
                self.consume(0,len(in0))
                #print("No output")
                return 0
