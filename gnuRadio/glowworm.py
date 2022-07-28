# Author: James C Morrison
# Date: 1/1//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# The Glow Worm Hash and supporting functions to be used with for
# mark placement in the BBC codec.

# To install a package: from cmd "python -m pip install name"
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
