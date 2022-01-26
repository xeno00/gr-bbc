# Author: James C Morrison
# Date: 1/1//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# The Glow Worm Hash and supporting functions to be used with for
# mark placement in the BBC codec.

#TODO: write some code
# To install a package: from cmd "python -m pip install name"

def add_bit(b, s, n, t):
    t = s[n % 32]^(0xffffffff if b else 0)
    t = (t|(t>>1)) ^ ((t<<1) & 0xffffffffffffffff)       # Have to enforce 64 bit condition on left shift     
    t ^= (t>>4) ^ (t>>8) ^ (t>>16) ^ (t>>32)
    #n = n + 1        removed since cant modify global variable                             
    s[(n+1) % 32] ^= t  #s[(n) % 32] ^= t, modified to reflect n change
    return s[(n+1) % 32]    #return s[(n) % 32], modified to reflect n change                      


def del_bit(b, s, n, t):
    n -= 1
    add_bit(b,s,n,t), 
    n -= 1
    return s[n % 32]
    

def init(s, n, t, i, h):
    h = 1
    n = 0
    for i in range(32):
        s[i]=0
    for i in range(4096):
        h=add_bit(h&1, s, n, t)
        n+=1 # moved out 1 level from original hash since function cannot modify n in global scope
    n = 0
