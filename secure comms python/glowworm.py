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
    t  = (t|(t>>1)) ^ (t<<1)                
    t ^= (t>>4) ^ (t>>8) ^ (t>>16) ^ (t>>32)
    n +=1                                     
    s[n % 32] ^= t  
    return s[n % 32]                         


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
    n = 0

