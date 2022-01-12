# Author: James C Morrison
# Date: 1/1//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Encode and decode a message using the BBC algorithm as described by 
# Bahn, Baird, and Carlisle. The BBC algorithm is an unkeyed approach
# to jamming resistance. Without the use of keys, omnidirectional
# communication may be achieved with relatively low power and high
# speed. In BBC, codewords are binary strings with length 2^len(message+2)
# assuming 2 checksum bits concatenated to the end of the message.
# Since the mark (1 in codeword) density is low, the transmit power 
# requirement is low. 

# TODO: add doxygen headers
# TODO: answer decoding questions

from glowworm import gw_hash
from math import log


def encode_BBC(message, hash:function=gw_hash):
    """
    encode_BBC uses the BBC algorithm to place marks in a codeword.

    :param message:  message to be encoded
    :param hash:  hash function to determine mark positions for substrings
    :return:  the encoded message AKA codeword
    """
    # add checksum bits and calculate the message length
    message.extend(0,0)
    length = len(message)
    # initialize the codeword to all 0's
    mark_array = [0 for m in range(2 ** (length))]
    # place marks (1's) at each subset hash location
    for i in range(length):
        mark_array[hash(message[0:i])] = 1
    # return the codeword
    return mark_array


def decode_BBC(codeword:list, hash:function=gw_hash):
    """
    decode_BBC uses the BBC algorithm to decode a list of marks (codewords).

        :param codeword:  list of marks to be decoded
        :param hash:  hash function to determine mark positions
        :return:  list of identified messages (without checksum bits)
    """
    # initialize the current assumed message and array of valid messages
    message = []
    messages = []
    # make the first recursive call to decode
    _decode_BBC_recursive(codeword, log(len(codeword,2)), hash, 0, message, messages)
    return messages

# - is this depth first recusion?
# - is the L term from the paper the same as the message length or the
#   codeword length? This assumes codeword length
# - would best practice have these parameters named differently than the
#   caller function?
# - would it be faster to store the length instead of using a logarithm?
# - does python evaluate a result of 1 as true for a mathematical expression or do I need
#   <expression> == 1
# - typo in paper as marked in .pdf? The following code assumes yes
def _decode_BBC_recursive(codeword:list, length:int, hash:function, index, message, message_list:list):
    """
    _decode_BBC_recursive is the recursive functionality to decode a BBC code

        :param codeword:  message to be decoded
        :param length:  potential maximum length of message
        :param hash:  hash function to determine mark positions
        :param index:  current bit index !! NEEDS TO BE REMOVED REMAP TO len(msg)
        :param message: current message tree
        :param message_list:  array of valid messages contained in the codeword
    """
    # base case, we've reached the end of the message tree with a valid message, add the message and remove checksum
    if index == (length-1):
        message_list.append(message[:-2])
    # test both possible next message values
    else:
        # assuming the next message bit is a 0, check for a mark in the codeword
        if codeword[hash(message.append(0))]:
            _decode_BBC_recursive(codeword, length, hash, index+1, message.append(0), message_list)
        if codeword[hash(message.append(1))]:
            _decode_BBC_recursive(codeword, length, hash, index+1, message.append(1), message_list)
