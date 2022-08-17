import numpy as np
from gnuradio import gr
from gnuradio import grc
import inspect


class blk(gr.sync_block):

    def __init__(self):  # only default arguments here
        cod_len = get_top_variable("CODEWORD_LENGTH", default=2**17)
        
        gr.sync_block.__init__(self,
            name='OR Codeword',
            in_sig=[(np.ubyte,  cod_len if isinstance(cod_len, int) else int(cod_len)), 
                    (np.ubyte,  cod_len if isinstance(cod_len, int) else int(cod_len))],    #[np.complex64],
            out_sig=[(np.ubyte, cod_len if isinstance(cod_len, int) else int(cod_len))]
        )


    def work(self, input_items, output_items):
        #print(input_items[0][0]) gives list without extra binder
        #print(input_items[1])  gives list with extra binder
        result = self.combine_codewords([input_items[1][0], input_items[0][0]])
        #print(result)
        print("Assigning result")
        print(result[37])
        #output_items[0][:] = input_items[0]    WORKS. Same error if input_items[0][0]
        output_items[0][:] = list(result)
        print("final step")
        #return len(output_items[0])            WORKS
        return len(output_items[0])

    def combine_codewords(self, words):
        result = 0
        #print(type(words[0][0][0]))
        print("decoding 0")
        cw1 = int.from_bytes(words[0],"little")
        print("decoding 1")
        cw2 = int.from_bytes(words[1],"little")
        #for x in words:
        #    result |= int.from_bytes(x,"little")
        print("combining...")
        result = cw1 |cw2
        print("encoding...")
        result = cw1.to_bytes(len(words[0]),"little")#result.to_bytes(len(words[0]),"little")
        print("returning...")
        return result


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

    ## Run Condition: Saving the flowgraph, necessary when default case isnt correct
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
            result = top['self'].blocks[block_index].params['value'].value
            print(f"[Block Debug 2] While modifying the flowgraph, I found top variable \'{variable_name}\': type={type(result)}, value={result}")
            return result

    finally:
        del top

    print("returining default vaule")
    return default