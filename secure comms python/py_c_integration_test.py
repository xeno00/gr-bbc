import BBCCodecNum as bbc
import ctypes
#gw = ctypes.CDLL("secure comms python/glowworm.so")

#print(type(gw))
#cw = bbc.encode_BBC(message="hello world", num_checksum=2)
#print(bin(cw))
#print(gw.add1())
#print(windll.kernel32.add1) 

#gw[1] refrences the first real function in the c file, in this case, add1
#print(gw[1]())


import glowworm as gw
s = [0 for i in range(32)] # same as s in paper. needs 32 64b words.
gw.init(s)
print(0xaf0a5f77bc7293a8%128)
print(gw.n, gw.add_bit(0, s) %32)
print(gw.n, gw.add_bit(1, s) %32)
print(gw.n, gw.add_bit(1, s) %32)
print(gw.n, gw.add_bit(1, s) %32)

