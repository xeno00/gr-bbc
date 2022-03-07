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



message = 0b101010
message1 = "Hi"
message2 = 42
codeword = bbc.encode(message2)
print("our codeword is ", codeword)
decoded  = bbc.decode(codeword, 6, 0)
print("our decoded messages include ", decoded)


