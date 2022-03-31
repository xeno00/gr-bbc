import BBCCodecNum as bbc
import glowworm as gw
#import ctypes
#gw = ctypes.CDLL("secure comms python/glowworm.so")

#print(type(gw))
#cw = bbc.encode_BBC(message="hello world", num_checksum=2)
#print(bin(cw))
#print(gw.add1())
#print(windll.kernel32.add1) 

#gw[1] refrences the first real function in the c file, in this case, add1
#print(gw[1]())

s = [0 for i in range(32)]
gw.init(s)

print(gw.add_bit(0,s)%64)
print(gw.add_bit(1,s)%64)
print(gw.add_bit(0,s)%64)
print(gw.add_bit(1,s)%64)
print(gw.add_bit(0,s)%64)
print(gw.add_bit(1,s)%64)

# a 1024 bit message
message = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
length = 152
mes = 2126878914293937816159096234051292569148680520 # from "Hi! my name is ____""
message = "Hi! my name is ____"
codeword = bbc.encode(message)
print("our codeword is ", codeword)
decoded  = bbc.decode(codeword, 152, 0)
print("our decoded messages include ", decoded)


