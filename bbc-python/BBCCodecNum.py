# Author: James C Morrison
# Date: 1/1//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Implement the BBC codec with integer values rather than arrays

# TODO: add docstring headers
# TODO: implement an iterative model rather than recursive
# TODO: Check encode_BBC implmentation
# TODO: Configure the glowwormDelBit calls
# TODO: write separate init() for pulling c file in? Move glow worm inits there with global memory for s,n,t,i,h?
# TODO: optomize complete substring deletion in encode - use the current state and add to it
# TODO: QUESTIONS
        # 1) should s, n, t, i, h be implemented in the caller functions rather than global memory? If we have local memory dont need delBit in encode
        # 2) does best practice have different variable names between caller and recursor
        # 3) how to prune the recursive tree for unnecessary calls?


from math import log
import glowworm as gw

DEFAULT_LENGTH = 6     # Eventually want to set to 1024 bits, so that codeword length is 2^1024
DEFAULT_CHECKSUM = 0   # set default number of additional bits to be used for checksum
string_flag = 0

# Convert input to a number, or series of numbers
def scrub_input(message, num_checksum):
    """
    srub_input converts different data to an integer and interpolates message length

    :param message:  message to be encoded, as diverse types
    :param num_checksum:  the number of checksum bits (i.e. left shifts)
    :return:  the encoded message AKA codeword, as an integer
    """

    if  (type(message)==int):
        length = 64 + num_checksum
    elif(type(message)==bytes):
        length = len(message)*8 + num_checksum
        message = int.from_bytes(message, byteorder='little') # convert to byte
    elif(type(message)==str):
        global string_flag
        string_flag = 1
        length = len(message)*8 + num_checksum # get length (number of bits of message) while still string, assuming ASCII so each letter is a byte
        message = int.from_bytes(message.encode(encoding='ascii'), byteorder='little')
    else:
        length=0 # error case
        print("scrub_input exception: this data type is not recognized")
    message = message << num_checksum # add checksum bits and calculate the message length
     
    return (message, length)
    
# Initialize a new glow worm shift register and the unknown codeword or message
def init_shift_register():
    # Configure hash function and shift register
    shift_register = [0 for i in range(32)]     # same as paper's "s" variable. Each of the 32 entries is a 64b word.
    unknown = 0b0                               # initialize the codeword or message to all 0's, so that we can place marks as needed
    gw.init(shift_register)
    return (shift_register, unknown)

# Encode a message into a codeword
def encode(message, num_checksum:int=DEFAULT_CHECKSUM):

    message, length = scrub_input(message, num_checksum)
    shift_register, codeword = init_shift_register()

    # Set marks using array indexing with hash's output (LSB first)
    for i in range(length): # Set bounds (n) for each substring
        bit = message & (1<<i)
        mark_loc = gw.add_bit(bit, shift_register) % (length)
        codeword |= (1<<mark_loc)
    
    # End state assums new shift register memory allocated inside of the decode function, since no delBit here.
    return codeword

# Decode a codeword into a list of possible messages
def decode(codeword:int, length:int, num_checksum:int=0):
    # initialize the current assumed message and array of valid messages
    messages = []
    shift_register, message = init_shift_register()
    _decode_BBC_recursive(codeword, length, 0, message, messages, num_checksum, shift_register) # make the first recursive call to decode

    return messages

# Handle the recursive call for the decoder
def _decode_BBC_recursive(codeword:int, length:int, index, message, message_list:list, num_checksum:int, s):

    # base case, we've reached the end of the message tree with a valid message, add the message and remove checksum
    if index == (length):
        if(string_flag):                            #2**length?
            print((message>>num_checksum).to_bytes(int((length)/8)+20, byteorder='little').decode(encoding='ascii'))
            message_list.append()#(message>>num_checksum).to_bytes((2**length)/8, byteorder='little').decode(encoding='ascii'))
        else:
            message_list.append(message)

    # test both possible next message values
    else:
        # assuming the next message bit is a 0, check for a mark in the codeword
        val = (gw.add_bit(0, s) % (length))
        if (codeword & (1<<val)) != 0:
            _decode_BBC_recursive(codeword, length, index+1, message, message_list, num_checksum, s)
        gw.del_bit(0, s)

        # assuming the next message bit is a 1, check for a mark in the codeword
        val = (gw.add_bit(1, s) % (length))
        if (codeword & (1<<val)) != 0: #(1<<val) == (codeword & (1<<val)):
            _decode_BBC_recursive(codeword, length, index+1, message+2**index, message_list, num_checksum, s)
        gw.del_bit(1, s)